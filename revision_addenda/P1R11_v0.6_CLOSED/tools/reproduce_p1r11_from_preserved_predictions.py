#!/usr/bin/env python3
"""
P1R-11 closure reproduction harness.

PROVENANCE LABEL
----------------
This is a RECONSTRUCTED closure/reproduction script created from the documented
P1R-11 analysis specification and recovered historical execution records. It is
NOT represented as the byte-identical original ephemeral analysis script.

It performs no model training. It reads the preserved six test probability
matrices plus frozen cohort / RQ3 metadata and recomputes the revision-stage
post hoc diagnostics.
"""
from __future__ import annotations
import argparse, hashlib, json, math, os
from pathlib import Path
from itertools import combinations

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, f1_score, confusion_matrix

SEEDS = [42, 123, 2026]
LABELS = {0: "Negative", 1: "Neutral", 2: "Positive"}
LABEL_TO_ID = {v:k for k,v in LABELS.items()}
PAIR_SEEDS = [(42,123),(42,2026),(123,2026)]


def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def locate(root: Path, stem: str) -> Path:
    candidates = [root/stem, root/(stem+'.bin')]
    for p in candidates:
        if p.exists(): return p
    hits = list(root.rglob(stem)) + list(root.rglob(stem+'.bin'))
    if len(hits)==1: return hits[0]
    if not hits: raise FileNotFoundError(f'Cannot locate {stem} under {root}')
    raise RuntimeError(f'Ambiguous file for {stem}: {hits}')


NEEDED_COLUMNS = {
    'prediction':['row_id','p_negative','p_neutral','p_positive','pred_class_id'],
    'IGAR_RQ4_Final_Cohort_150k.parquet':['row_id','duplicate_group_id','split','rating_target','vader_target'],
    '05_RQ3_primary_final.parquet':['row_id','duplicate_group_id','duplicate_group_size'],
    '05_RQ3_singleton_sensitivity.parquet':['row_id'],
    'RQ4_Test_Paired_JSD_22_500.parquet':['row_id','mean_seed_jsd'],
}

def load_parquet(root: Path, stem: str) -> tuple[pd.DataFrame, Path]:
    p=locate(root, stem)
    cols=NEEDED_COLUMNS['prediction'] if stem.startswith('seed_') else NEEDED_COLUMNS.get(stem)
    try:
        return pd.read_parquet(p,columns=cols), p
    except ImportError:
        # Offline closure fallback: narrow reader for the exact archived Arrow-23/SNAPPY files.
        from mini_parquet_snappy import read_parquet
        return read_parquet(p,columns=cols), p


def prob_matrix(df: pd.DataFrame) -> np.ndarray:
    a=df[['p_negative','p_neutral','p_positive']].to_numpy(dtype=float)
    if not np.isfinite(a).all(): raise ValueError('Probability matrix contains non-finite values')
    return a


def jsd_rows(p: np.ndarray, q: np.ndarray) -> np.ndarray:
    # Natural-log Jensen-Shannon divergence (not square-root distance).
    p=np.asarray(p,dtype=np.float64); q=np.asarray(q,dtype=np.float64)
    m=0.5*(p+q)
    def xlogratio(a,b):
        out=np.zeros_like(a,dtype=np.float64)
        mask=a>0
        out[mask]=a[mask]*(np.log(a[mask])-np.log(b[mask]))
        return out
    return 0.5*np.sum(xlogratio(p,m),axis=1)+0.5*np.sum(xlogratio(q,m),axis=1)


def as_target(series: pd.Series) -> np.ndarray:
    if pd.api.types.is_numeric_dtype(series): return series.astype(int).to_numpy()
    vals=series.astype(str).str.strip().str.title().map(LABEL_TO_ID)
    if vals.isna().any():
        raise ValueError(f'Unmapped labels: {sorted(series[vals.isna()].astype(str).unique())[:10]}')
    return vals.astype(int).to_numpy()


def cluster_model(y, d, groups):
    X=sm.add_constant(np.asarray(d,dtype=float))
    fit=sm.OLS(np.asarray(y,dtype=float),X).fit(cov_type='cluster',cov_kwds={'groups':np.asarray(groups)},use_t=True)
    ci=fit.conf_int()[1]
    return {'beta':float(fit.params[1]),'se':float(fit.bse[1]),'ci95':[float(ci[0]),float(ci[1])],
            't':float(fit.tvalues[1]),'p':float(fit.pvalues[1])}


def entropy_2class(prob):
    x=prob[:,[0,2]].astype(np.float64)
    x=x/x.sum(axis=1,keepdims=True)
    return -np.sum(np.where(x>0,x*np.log(x),0.0),axis=1)


def mean_seed_entropy(preds, mask, binary=False):
    vals=[]
    for seed in SEEDS:
        p=preds[seed]
        if binary:
            e=entropy_2class(p)
        else:
            e=-np.sum(np.where(p>0,p*np.log(p),0.0),axis=1)
        vals.append(float(np.mean(e[mask])))
    return float(np.mean(vals)), vals


def mean_seed_accuracy(pred_dfs, target, mask, polarity_restricted=False):
    vals=[]
    for seed in SEEDS:
        df=pred_dfs[seed]
        if polarity_restricted:
            a=df[['p_negative','p_positive']].to_numpy(float)
            pred=np.where(np.argmax(a,axis=1)==0,0,2)
        else:
            pred=df['pred_class_id'].astype(int).to_numpy()
        vals.append(float(accuracy_score(target[mask],pred[mask])))
    return float(np.mean(vals)), vals


def summarize_metric_array(x):
    x=np.asarray(x,float)
    return {'mean':float(np.mean(x)),'median':float(np.median(x)),'sd':float(np.std(x,ddof=1)),
            'iqr':float(np.quantile(x,.75)-np.quantile(x,.25)),'n':int(len(x))}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--inputs-dir',required=True,type=Path,help='Directory containing preserved Parquet files; .bin suffix accepted.')
    ap.add_argument('--manifest',required=True,type=Path,help='P1R11_ADDENDUM_MANIFEST.json containing 33 canonical targets.')
    ap.add_argument('--out-dir',required=True,type=Path)
    args=ap.parse_args(); args.out_dir.mkdir(parents=True,exist_ok=True)

    pred_df={'R':{},'V':{}}; pred_prob={'R':{},'V':{}}; file_hashes={}
    for src in ['R','V']:
        for seed in SEEDS:
            stem=f'seed_{seed}_Model{src}_test_probabilities.parquet'
            df,p=load_parquet(args.inputs_dir,stem)
            if len(df)!=22500: raise AssertionError(f'{stem}: expected 22500 rows, got {len(df)}')
            pred_df[src][seed]=df.reset_index(drop=True); pred_prob[src][seed]=prob_matrix(df)
            file_hashes[stem]=sha256_file(p)

    # Canonical row order must be identical in all six matrices.
    row0=pred_df['R'][42]['row_id'].to_numpy()
    for src in ['R','V']:
        for seed in SEEDS:
            if not np.array_equal(row0,pred_df[src][seed]['row_id'].to_numpy()):
                raise AssertionError(f'row_id order mismatch: {src}{seed}')

    # Probability integrity.
    probability_integrity={}
    for src in ['R','V']:
        for seed in SEEDS:
            p=pred_prob[src][seed]
            rs=p.sum(axis=1)
            probability_integrity[f'{src}{seed}']={
                'finite':bool(np.isfinite(p).all()),'nan_count':int(np.isnan(p).sum()),'inf_count':int(np.isinf(p).sum()),
                'row_sum_min':float(rs.min()),'row_sum_max':float(rs.max()),'max_abs_row_sum_deviation':float(np.max(np.abs(rs-1.0)))
            }

    cohort, cohort_path=load_parquet(args.inputs_dir,'IGAR_RQ4_Final_Cohort_150k.parquet')
    rq3, rq3_path=load_parquet(args.inputs_dir,'05_RQ3_primary_final.parquet')
    rq3_single, rq3s_path=load_parquet(args.inputs_dir,'05_RQ3_singleton_sensitivity.parquet')
    paired_old, paired_path=load_parquet(args.inputs_dir,'RQ4_Test_Paired_JSD_22_500.parquet')
    file_hashes.update({cohort_path.name:sha256_file(cohort_path),rq3_path.name:sha256_file(rq3_path),rq3s_path.name:sha256_file(rq3s_path),paired_path.name:sha256_file(paired_path)})

    split=cohort['split'].astype(str).str.lower()
    test=cohort.loc[split.eq('test')].copy()
    if len(test)!=22500: raise AssertionError(f'Expected 22500 test rows in cohort; got {len(test)}')
    byid=test.set_index('row_id',drop=False)
    try: test=byid.loc[row0].reset_index(drop=True)
    except KeyError as e: raise AssertionError('Prediction row_id not fully represented in frozen cohort') from e

    rating=as_target(test['rating_target'] if 'rating_target' in test else test['rating_label'])
    vader=as_target(test['vader_target'] if 'vader_target' in test else test['vader_label'])
    D=(rating!=vader).astype(int)
    groups=test['duplicate_group_id'].astype(str).to_numpy()
    severity=np.abs(rating-vader)

    # Cross-source per-seed and three-seed mean.
    cross_seed={}; cross_arr=[]
    for seed in SEEDS:
        j=jsd_rows(pred_prob['R'][seed],pred_prob['V'][seed]); cross_seed[str(seed)]=j; cross_arr.append(j)
    cross=np.mean(np.vstack(cross_arr),axis=0)

    # Verify original paired-JSD table where available.
    paired_byid=paired_old.set_index('row_id')
    paired_aligned=paired_byid.loc[row0]
    if 'mean_seed_jsd' in paired_aligned:
        diff=float(np.max(np.abs(cross-paired_aligned['mean_seed_jsd'].to_numpy(float))))
    else: diff=None

    primary=cluster_model(cross,D,groups)
    primary.update({'D0':summarize_metric_array(cross[D==0]),'D1':summarize_metric_array(cross[D==1]),'n':len(cross),'agreement_n':int((D==0).sum()),'disagreement_n':int((D==1).sum()),'paired_jsd_max_abs_diff':diff})

    # Within-source pairwise seed JSD.
    within_pairs={'R':{},'V':{}}; within_review={}
    for src in ['R','V']:
        pair_arrays=[]
        for a,b in PAIR_SEEDS:
            j=jsd_rows(pred_prob[src][a],pred_prob[src][b]); pair_arrays.append(j)
            within_pairs[src][f'{a}_{b}']={'all':summarize_metric_array(j),'D0':summarize_metric_array(j[D==0]),'D1':summarize_metric_array(j[D==1])}
        within_review[src]=np.mean(np.vstack(pair_arrays),axis=0)
    within_combined=0.5*(within_review['R']+within_review['V'])
    ratio_full=float(np.mean(cross[D==1])/np.mean(within_combined[D==1]))

    # Polarity-only / Neutral-free.
    polarity=(rating!=1)&(vader!=1)
    pol=cluster_model(cross[polarity],D[polarity],groups[polarity])
    pol.update({'n':int(polarity.sum()),'D0':summarize_metric_array(cross[polarity & (D==0)]),'D1':summarize_metric_array(cross[polarity & (D==1)])})
    ratio_pol=float(np.mean(cross[polarity & (D==1)])/np.mean(within_combined[polarity & (D==1)]))

    # Full-source singleton membership from RQ3 primary; cross-check with singleton-sensitivity table.
    # Every frozen RQ4 test row must be represented in the authoritative RQ3 table.
    rq3_row_ids=set(rq3['row_id'].tolist())
    missing_rq3=[x for x in row0 if x not in rq3_row_ids]
    if missing_rq3:
        raise AssertionError(f'{len(missing_rq3)} test row_ids absent from RQ3 table')
    single_ids=set(rq3.loc[rq3['duplicate_group_size'].astype(int).eq(1),'row_id'].tolist())
    single_ids2=set(rq3_single['row_id'].tolist())
    # The singleton-sensitivity table should be the full-source singleton population; allow extra metadata filtering history but record relation.
    singleton=np.array([x in single_ids for x in row0],dtype=bool)
    sing=cluster_model(cross[singleton],D[singleton],groups[singleton])
    sing.update({'n':int(singleton.sum()),'D0':summarize_metric_array(cross[singleton & (D==0)]),'D1':summarize_metric_array(cross[singleton & (D==1)]),'singleton_id_set_agreement_with_secondary_table':len(single_ids.symmetric_difference(single_ids2))})
    ratio_sing=float(np.mean(cross[singleton & (D==1)])/np.mean(within_combined[singleton & (D==1)]))

    joint=singleton & polarity
    joint_fit=cluster_model(cross[joint],D[joint],groups[joint]); joint_fit.update({
        'n':int(joint.sum()),
        'D0':summarize_metric_array(cross[joint & (D==0)]),
        'D1':summarize_metric_array(cross[joint & (D==1)]),
        'variance_estimator_note':'Cluster-robust covariance with one observation per cluster; with the statsmodels small-sample correction this is algebraically equivalent to HC1 on this singleton subset.'
    })

    # Class-specific metrics per model/seed against its own weak target.
    learnability={}
    class_mean={}
    for src,target in [('R',rating),('V',vader)]:
        stage=[]
        for seed in SEEDS:
            pred=pred_df[src][seed]['pred_class_id'].astype(int).to_numpy()
            pr,rc,f1,sup=precision_recall_fscore_support(target,pred,labels=[0,1,2],zero_division=0)
            stage.append({'seed':seed,'accuracy':float(accuracy_score(target,pred)),'macro_f1':float(f1_score(target,pred,average='macro')),
                          'classes':{LABELS[i]:{'precision':float(pr[i]),'recall':float(rc[i]),'f1':float(f1[i]),'support':int(sup[i])} for i in range(3)},
                          'confusion_matrix':confusion_matrix(target,pred,labels=[0,1,2]).tolist()})
        learnability[src]=stage
        class_mean[src]={c:{metric:float(np.mean([x['classes'][c][metric] for x in stage])) for metric in ['precision','recall','f1']} for c in LABELS.values()}
        class_mean[src]['accuracy']=float(np.mean([x['accuracy'] for x in stage])); class_mean[src]['macro_f1']=float(np.mean([x['macro_f1'] for x in stage]))

    # Entropy / shared-label diagnostics.
    agree_pol=(rating==vader)&(rating!=1)
    entR,_=mean_seed_entropy(pred_prob['R'],agree_pol,False); entV,_=mean_seed_entropy(pred_prob['V'],agree_pol,False)
    entR2,_=mean_seed_entropy(pred_prob['R'],agree_pol,True); entV2,_=mean_seed_entropy(pred_prob['V'],agree_pol,True)
    shared_target=rating
    accR,_=mean_seed_accuracy(pred_df['R'],shared_target,agree_pol,False); accV,_=mean_seed_accuracy(pred_df['V'],shared_target,agree_pol,False)
    accR2,_=mean_seed_accuracy(pred_df['R'],shared_target,agree_pol,True); accV2,_=mean_seed_accuracy(pred_df['V'],shared_target,agree_pol,True)

    # Full uncertainty summaries for S13 Panel D: five reporting scopes, by source and seed.
    scopes={
        'full':np.ones(len(D),dtype=bool),
        'agreement':D==0,
        'disagreement':D==1,
        'polarity_all':polarity,
        'polarity_agreement':agree_pol,
    }
    uncertainty={}
    for scope_name,mask in scopes.items():
        uncertainty[scope_name]={}
        for src in ['R','V']:
            ent=[]; mc=[]
            for seed in SEEDS:
                p=pred_prob[src][seed]
                e=-np.sum(np.where(p>0,p*np.log(p),0.0),axis=1)
                ent.append(float(np.mean(e[mask])))
                mc.append(float(np.mean(np.max(p,axis=1)[mask])))
            uncertainty[scope_name][src]={
                'entropy':float(np.mean(ent)),
                'max_confidence':float(np.mean(mc)),
                'per_seed_entropy':ent,
                'per_seed_max_confidence':mc,
                'n':int(mask.sum()),
            }

    # Singleton x Neutral composition for S14 Panels B/C.
    neutral_involved=(rating==1)|(vader==1)
    crosstab_singleton_neutral={
        'marginal':{
            'singleton':{
                'neutral_involved':int((singleton & neutral_involved).sum()),
                'polarity_only':int((singleton & ~neutral_involved).sum()),
            },
            'non_singleton':{
                'neutral_involved':int((~singleton & neutral_involved).sum()),
                'polarity_only':int((~singleton & ~neutral_involved).sum()),
            },
        },
        'conditional_on_disagreement':{
            'singleton':{
                'neutral_involved':int((singleton & neutral_involved & (D==1)).sum()),
                'polarity_only':int((singleton & ~neutral_involved & (D==1)).sum()),
            },
            'non_singleton':{
                'neutral_involved':int((~singleton & neutral_involved & (D==1)).sum()),
                'polarity_only':int((~singleton & ~neutral_involved & (D==1)).sum()),
            },
        },
    }

    # Pairwise within-source seed JSD for S12 Panels B/C.
    within_pairs_subsets={}
    for sub_name,mask in [('polarity_only',polarity),('singleton',singleton)]:
        within_pairs_subsets[sub_name]={}
        for src in ['R','V']:
            within_pairs_subsets[sub_name][src]={}
            for a,b in PAIR_SEEDS:
                j=jsd_rows(pred_prob[src][a],pred_prob[src][b])
                within_pairs_subsets[sub_name][src][f'{a}_{b}']={
                    'all':summarize_metric_array(j[mask]),
                    'D0':summarize_metric_array(j[mask & (D==0)]),
                    'D1':summarize_metric_array(j[mask & (D==1)]),
                }

    # Directional composition / severity.
    def lab(i): return LABELS[int(i)]
    trans=np.array([f'{lab(a)}->{lab(b)}' for a,b in zip(rating,vader)],dtype=object)
    severity_stats={int(s):summarize_metric_array(cross[severity==s]) for s in sorted(np.unique(severity))}
    transition_stats={}
    for t in sorted(set(trans[D==1])):
        mask=(trans==t)&(D==1); transition_stats[t]=summarize_metric_array(cross[mask])
    s1=(severity==1)&(D==1)
    toward=s1 & (vader==1) & (rating!=1)
    from_neutral=s1 & (rating==1) & (vader!=1)
    s1_mass=100.0*float(cross[toward].sum()/cross[s1].sum())
    nn=(rating==1)&(vader==1)
    neutral_neutral_full=summarize_metric_array(cross[nn])

    # Largest 1/5/10 duplicate-text cluster sensitivity (original S6 definition).
    # IMPORTANT: clusters are ranked by their observed size *within the frozen test set*,
    # not by full-corpus duplicate_group_size. The historical S6 exclusions remove
    # exactly 1,106 / 2,793 / 3,362 test rows for k=1/5/10.
    group_sizes_test=pd.Series(groups).value_counts(sort=True)
    expected_removed={1:1106,5:2793,10:3362}
    beta0=primary['beta']; excl={}
    for k in [1,5,10]:
        top=set(group_sizes_test.head(k).index.astype(str))
        keep=np.array([g not in top for g in groups],dtype=bool)
        removed=int((~keep).sum())
        if removed != expected_removed[k]:
            raise AssertionError(f'S6 top-{k} test-set cluster exclusion removed {removed} rows; expected {expected_removed[k]}')
        beta=float(np.mean(cross[keep & (D==1)])-np.mean(cross[keep & (D==0)]))
        excl[str(k)]={'beta':beta,'percent_change_abs':100.0*abs(beta-beta0)/abs(beta0),'n':int(keep.sum()),'removed_n':removed}
    max_excl=max(x['percent_change_abs'] for x in excl.values())

    computed={
      'within_source_ratio_full_disagreement':ratio_full,
      'within_source_ratio_polarity_only_disagreement':ratio_pol,
      'within_source_ratio_singleton_disagreement':ratio_sing,
      'polarity_only_n':int(polarity.sum()),'polarity_only_beta':pol['beta'],'polarity_only_ci95':pol['ci95'],'polarity_only_retained_percent':100.0*pol['beta']/beta0,
      'singleton_n':int(singleton.sum()),'singleton_beta':sing['beta'],'singleton_ci95':sing['ci95'],'singleton_retained_percent':100.0*sing['beta']/beta0,
      'joint_n':int(joint.sum()),'joint_beta':joint_fit['beta'],'joint_ci95':joint_fit['ci95'],'joint_retained_percent':100.0*joint_fit['beta']/beta0,
      'model_r_neutral_f1':class_mean['R']['Neutral']['f1'],
      'shared_label_three_class_accuracy_difference_v_minus_r_pp':100.0*(accV-accR),
      'shared_label_binary_accuracy_model_r_percent':100.0*accR2,'shared_label_binary_accuracy_model_v_percent':100.0*accV2,
      'shared_label_binary_accuracy_difference_v_minus_r_pp':100.0*(accV2-accR2),
      'polarity_agreement_entropy_ratio_three_class_r_over_v':entR/entV,
      'polarity_agreement_entropy_ratio_binary_renormalized_r_over_v':entR2/entV2,
      's1_n':int(s1.sum()),'s1_polarity_to_vader_neutral_n':int(toward.sum()),'s1_polarity_to_vader_neutral_percent':100.0*toward.sum()/s1.sum(),
      's1_polarity_to_vader_neutral_weighted_mean_jsd':float(np.mean(cross[toward])),'s1_rating_neutral_to_polarity_weighted_mean_jsd':float(np.mean(cross[from_neutral])),
      's1_weighted_jsd_mass_toward_vader_neutral_percent':s1_mass,
      'neutral_neutral_n':int(nn.sum()),'neutral_neutral_mean_jsd':float(np.mean(cross[nn])),'neutral_neutral_median_jsd':float(np.median(cross[nn])),
      'largest_cluster_exclusion_max_beta_change_percent':float(max_excl),'all_repeated_text_exclusion_beta_attenuation_percent':100.0*(1.0-sing['beta']/beta0)
    }

    detailed={
      'provenance_label':'RECONSTRUCTED CLOSURE SCRIPT; NO MODEL RETRAINING',
      'input_file_hashes':file_hashes,'probability_integrity':probability_integrity,'primary':primary,
      'within_source_pairs':within_pairs,'polarity_only':pol,'singleton':sing,'joint':joint_fit,
      'learnability_per_seed':learnability,'learnability_mean':class_mean,
      'shared_label':{'three_class':{'R':accR,'V':accV},'polarity_restricted':{'R':accR2,'V':accV2}},
      'entropy':{'three_class_polarity_agreement':{'R':entR,'V':entV},'two_class_renormalized_polarity_agreement':{'R':entR2,'V':entV2}},
      'uncertainty_by_scope':uncertainty,
      'singleton_neutral_crosstab':crosstab_singleton_neutral,
      'neutral_neutral_full':neutral_neutral_full,
      'within_source_pairs_subsets':within_pairs_subsets,
      'severity':severity_stats,'transitions':transition_stats,'largest_cluster_exclusions':excl,'computed_33_targets':computed
    }

    (args.out_dir/'P1R11_REPRODUCED_RESULTS.json').write_text(json.dumps(detailed,indent=2),encoding='utf-8')

    # Validate against canonical targets with transparent tolerances reflecting reported rounding.
    manifest=json.loads(args.manifest.read_text())
    expected=manifest.get('revision_stage_reported_targets')
    if expected is None:
        expected=manifest.get('revision_stage_targets')
    if expected is None:
        raise KeyError('Manifest must contain revision_stage_reported_targets or revision_stage_targets')
    tol={
      'ratio':0.06,'beta':0.00015,'ci':0.0002,'percent':0.08,'f1':0.00015,'pp':0.02,'entropy':0.0008,'jsd':0.0012,'count':0
    }
    def tolerance(k):
        if k.endswith('_n'): return tol['count']
        if 'ci95' in k: return tol['ci']
        # Unit-bearing suffixes take precedence over embedded metric names.
        # Example: *_beta_change_percent must use percent tolerance, not beta tolerance.
        if k.endswith('_percent'): return tol['percent']
        if k.endswith('_pp'): return tol['pp']
        # Entropy targets are gate-sensitive and must use the tighter entropy tolerance
        # before the generic ratio rule is considered.
        if 'entropy' in k: return tol['entropy']
        if 'ratio' in k or 'within_source_ratio' in k: return tol['ratio']
        if 'beta' in k: return tol['beta']
        if 'f1' in k: return tol['f1']
        if 'jsd' in k: return tol['jsd']
        return 1e-6
    validation={}; all_pass=True
    for k,e in expected.items():
        a=computed[k]; t=tolerance(k)
        if isinstance(e,list):
            diffs=[abs(float(x)-float(y)) for x,y in zip(a,e)]; ok=max(diffs)<=t
            delta=diffs
        else:
            delta=abs(float(a)-float(e)); ok=delta<=t
        validation[k]={'expected':e,'observed':a,'tolerance':t,'pass':bool(ok),'abs_delta':delta}
        all_pass=all_pass and ok
    report={'target_count':len(expected),'pass_count':sum(1 for x in validation.values() if x['pass']),'all_33_pass':bool(all_pass),'validation':validation}
    (args.out_dir/'P1R11_33_TARGET_VALIDATION.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({'all_33_pass':all_pass,'pass_count':report['pass_count'],'target_count':report['target_count'],'out_dir':str(args.out_dir)},indent=2))
    if not all_pass: raise SystemExit(2)

if __name__=='__main__': main()
