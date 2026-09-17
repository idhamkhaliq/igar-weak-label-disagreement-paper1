#!/usr/bin/env python3
"""Minimal read-only Parquet fallback for this P1R-11 closure package.

Scope is intentionally narrow: one-row-group flat Parquet files written by
parquet-cpp-arrow 23.0.1, SNAPPY compression, DataPageV1, optional scalar
columns, and PLAIN / RLE_DICTIONARY data encodings. It exists only so the
closure harness can run in an offline environment without pyarrow. It is not a
general Parquet implementation.
"""
from __future__ import annotations
import ctypes, ctypes.util, struct
from pathlib import Path
from typing import Iterable
import pandas as pd

# Thrift compact protocol type codes.
CT_STOP=0; CT_BOOL_TRUE=1; CT_BOOL_FALSE=2; CT_BYTE=3; CT_I16=4; CT_I32=5; CT_I64=6
CT_DOUBLE=7; CT_BINARY=8; CT_LIST=9; CT_SET=10; CT_MAP=11; CT_STRUCT=12

# Parquet physical types.
T_BOOLEAN=0; T_INT32=1; T_INT64=2; T_INT96=3; T_FLOAT=4; T_DOUBLE=5; T_BYTE_ARRAY=6; T_FIXED=7
# Parquet encodings.
E_PLAIN=0; E_RLE=3; E_RLE_DICTIONARY=8
# Parquet page types.
P_DATA=0; P_INDEX=1; P_DICTIONARY=2; P_DATA_V2=3
# Compression.
C_UNCOMPRESSED=0; C_SNAPPY=1


def _uvarint(buf: bytes, pos: int):
    n=0; shift=0
    while True:
        b=buf[pos]; pos+=1; n|=(b & 0x7f) << shift
        if not (b & 0x80): return n,pos
        shift+=7


def _zigzag(n: int) -> int: return (n >> 1) ^ -(n & 1)

def _sint(buf: bytes,pos: int):
    n,pos=_uvarint(buf,pos); return _zigzag(n),pos


def _val(buf: bytes,pos: int,t: int):
    if t==CT_BOOL_TRUE: return True,pos
    if t==CT_BOOL_FALSE: return False,pos
    if t==CT_BYTE:
        b=buf[pos]; pos+=1; return (b-256 if b>=128 else b),pos
    if t in (CT_I16,CT_I32,CT_I64): return _sint(buf,pos)
    if t==CT_DOUBLE: return struct.unpack_from('<d',buf,pos)[0],pos+8
    if t==CT_BINARY:
        n,pos=_uvarint(buf,pos); return buf[pos:pos+n],pos+n
    if t in (CT_LIST,CT_SET):
        h=buf[pos]; pos+=1; n=h>>4; et=h&0xf
        if n==15: n,pos=_uvarint(buf,pos)
        out=[]
        for _ in range(n):
            v,pos=_val(buf,pos,et); out.append(v)
        return out,pos
    if t==CT_MAP:
        n,pos=_uvarint(buf,pos)
        if n==0: return [],pos
        h=buf[pos]; pos+=1; kt=h>>4; vt=h&0xf
        out=[]
        for _ in range(n):
            k,pos=_val(buf,pos,kt); v,pos=_val(buf,pos,vt); out.append((k,v))
        return out,pos
    if t==CT_STRUCT: return _struct(buf,pos)
    raise ValueError(f'Unsupported compact type {t}')


def _struct(buf: bytes,pos: int):
    out={}; fid=0
    while True:
        h=buf[pos]; pos+=1
        if h==0: return out,pos
        delta=h>>4; t=h&0xf
        if delta: fid += delta
        else: fid,pos=_sint(buf,pos)
        v,pos=_val(buf,pos,t); out[fid]=v


_snappy=ctypes.CDLL(ctypes.util.find_library('snappy'))
_snappy.snappy_uncompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.POINTER(ctypes.c_size_t)]
_snappy.snappy_uncompress.restype=ctypes.c_int


def _decompress(payload: bytes, codec: int, expected: int) -> bytes:
    if codec==C_UNCOMPRESSED:
        if len(payload)!=expected: raise ValueError('Uncompressed page size mismatch')
        return payload
    if codec!=C_SNAPPY: raise ValueError(f'Unsupported codec {codec}')
    src=ctypes.create_string_buffer(payload)
    out=ctypes.create_string_buffer(expected)
    n=ctypes.c_size_t(expected)
    rc=_snappy.snappy_uncompress(src,len(payload),out,ctypes.byref(n))
    if rc!=0: raise RuntimeError(f'snappy_uncompress rc={rc}')
    if n.value!=expected: raise ValueError(f'Snappy output length {n.value} != expected {expected}')
    return out.raw[:n.value]


def _hybrid(buf: bytes, bit_width: int, count: int):
    out=[]; pos=0; mask=(1<<bit_width)-1 if bit_width else 0
    while len(out)<count:
        header,pos=_uvarint(buf,pos)
        if header & 1 == 0:
            run=header>>1; nb=(bit_width+7)//8
            if bit_width==0: value=0
            else:
                value=int.from_bytes(buf[pos:pos+nb],'little'); pos+=nb
            take=min(run,count-len(out)); out.extend([value]*take)
        else:
            groups=header>>1; nvals=groups*8; nbytes=groups*bit_width
            chunk=buf[pos:pos+nbytes]; pos+=nbytes
            if bit_width==0:
                vals=[0]*nvals
            else:
                # Parquet bit-packed values are consecutive little-endian bit fields.
                big=int.from_bytes(chunk,'little')
                vals=[(big>>(i*bit_width)) & mask for i in range(nvals)]
            out.extend(vals[:count-len(out)])
    return out


def _plain(buf: bytes, ptype: int, count: int):
    out=[]; pos=0
    if ptype==T_BYTE_ARRAY:
        for _ in range(count):
            n=struct.unpack_from('<I',buf,pos)[0]; pos+=4
            out.append(buf[pos:pos+n].decode('utf-8')); pos+=n
    elif ptype==T_INT32:
        out=list(struct.unpack_from('<'+'i'*count,buf,pos)); pos+=4*count
    elif ptype==T_INT64:
        out=list(struct.unpack_from('<'+'q'*count,buf,pos)); pos+=8*count
    elif ptype==T_FLOAT:
        out=list(struct.unpack_from('<'+'f'*count,buf,pos)); pos+=4*count
    elif ptype==T_DOUBLE:
        out=list(struct.unpack_from('<'+'d'*count,buf,pos)); pos+=8*count
    elif ptype==T_BOOLEAN:
        for i in range(count): out.append(bool((buf[i//8]>>(i%8))&1))
        pos=(count+7)//8
    else:
        raise ValueError(f'Unsupported PLAIN physical type {ptype}')
    return out,pos


def _metadata(data: bytes):
    if data[:4]!=b'PAR1' or data[-4:]!=b'PAR1': raise ValueError('Not a Parquet file')
    n=struct.unpack_from('<I',data,len(data)-8)[0]
    start=len(data)-8-n
    meta,end=_struct(data,start)
    if end!=len(data)-8: raise ValueError('Footer parse did not consume footer')
    return meta


def _name(x): return x.decode('utf-8') if isinstance(x,(bytes,bytearray)) else x


def _read_column(data: bytes, md: dict, ptype: int, expected_rows: int):
    codec=md[4]
    if codec not in (C_UNCOMPRESSED,C_SNAPPY): raise ValueError(f'Unsupported codec {codec}')
    start=md.get(11,md[9]); end=start+md[7]
    pos=start; dictionary=None; values=[]
    while pos<end and len(values)<expected_rows:
        header,body_pos=_struct(data,pos)
        ptype_page=header[1]; unc=header[2]; comp=header[3]
        raw=_decompress(data[body_pos:body_pos+comp],codec,unc)
        pos=body_pos+comp
        if ptype_page==P_DICTIONARY:
            dh=header[7]; n=dh[1]; enc=dh[2]
            if enc!=E_PLAIN: raise ValueError(f'Unsupported dictionary encoding {enc}')
            dictionary,used=_plain(raw,ptype,n)
            if used!=len(raw):
                # Plain fixed-width dictionaries should consume fully; byte arrays can too.
                if any(raw[used:]): raise ValueError('Unexpected dictionary trailing bytes')
            continue
        if ptype_page!=P_DATA: raise ValueError(f'Unsupported page type {ptype_page}')
        dh=header[5]; n=dh[1]; enc=dh[2]; def_enc=dh[3]
        if def_enc!=E_RLE: raise ValueError(f'Unsupported definition encoding {def_enc}')
        # Flat optional scalar: repetition max level is zero, so only definition levels appear.
        dlen=struct.unpack_from('<I',raw,0)[0]
        defs=_hybrid(raw[4:4+dlen],1,n)
        if any(x!=1 for x in defs): raise ValueError('Nulls are not supported by this narrow fallback')
        payload=raw[4+dlen:]
        if enc==E_RLE_DICTIONARY:
            if dictionary is None: raise ValueError('Dictionary data page without dictionary')
            bw=payload[0]; idx=_hybrid(payload[1:],bw,n)
            page=[dictionary[i] for i in idx]
        elif enc==E_PLAIN:
            page,used=_plain(payload,ptype,n)
        else:
            raise ValueError(f'Unsupported data encoding {enc}')
        values.extend(page)
    if len(values)!=expected_rows: raise ValueError(f'Decoded {len(values)} values, expected {expected_rows}')
    return values


def read_parquet(path: str|Path, columns: Iterable[str]|None=None) -> pd.DataFrame:
    path=Path(path); data=path.read_bytes(); meta=_metadata(data)
    if len(meta[4])!=1: raise ValueError('Fallback supports one row group only')
    nrows=int(meta[3]); rg=meta[4][0]
    schema={_name(se[4]):se for se in meta[2][1:]}
    chunks={_name(cc[3][3][0]):cc[3] for cc in rg[1]}
    names=list(chunks) if columns is None else list(columns)
    out={}
    for name in names:
        if name not in chunks: raise KeyError(f'{name} absent from {path.name}')
        se=schema[name]; rep=se.get(3)
        if rep!=1: raise ValueError(f'Fallback expects OPTIONAL scalar column: {name}, repetition={rep}')
        out[name]=_read_column(data,chunks[name],se[1],nrows)
    return pd.DataFrame(out)
