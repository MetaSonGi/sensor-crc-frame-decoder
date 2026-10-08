"""Incremental demo wire protocol: sync, length, payload, CRC-16/CCITT-FALSE."""
import argparse, json, struct
from pathlib import Path
SYNC=b'\xaa\x55'

def crc16(data):
    crc=0xffff
    for byte in data:
        crc^=byte<<8
        for _ in range(8): crc=((crc<<1)^0x1021)&0xffff if crc&0x8000 else (crc<<1)&0xffff
    return crc

def encode(asset,sequence,temperature,current):
    payload=struct.pack('>BIhh',asset,sequence,round(temperature*100),round(current*1000))
    body=bytes([len(payload)])+payload
    return SYNC+body+struct.pack('>H',crc16(body))

class Decoder:
    def __init__(self): self.buffer=bytearray(); self.crc_errors=0; self.discarded=0; self.last_sequence={}
    def feed(self,chunk):
        self.buffer.extend(chunk); records=[]
        while len(self.buffer)>=3:
            index=self.buffer.find(SYNC)
            if index<0:
                keep=1 if self.buffer[-1]==SYNC[0] else 0
                self.discarded+=len(self.buffer)-keep; self.buffer=self.buffer[-keep:] if keep else bytearray(); break
            if index: self.discarded+=index; del self.buffer[:index]
            if len(self.buffer)<3: break
            length=self.buffer[2]
            if length!=9: self.discarded+=1; del self.buffer[0]; continue
            total=length+5
            if len(self.buffer)<total: break
            raw=bytes(self.buffer[:total]); expected=struct.unpack('>H',raw[-2:])[0]
            if crc16(raw[2:-2])!=expected:
                self.crc_errors+=1; del self.buffer[0]; continue
            del self.buffer[:total]
            asset,seq,temp,current=struct.unpack('>BIhh',raw[3:-2]); previous=self.last_sequence.get(asset)
            stale=previous is not None and seq<=previous
            if not stale: self.last_sequence[asset]=seq
            records.append({'asset_id':asset,'sequence':seq,'temperature_c':temp/100,'current_a':current/1000,
                            'accepted':not stale,'status':'stale_or_duplicate' if stale else 'ok'})
        return records

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--input',default=str(Path(__file__).with_name('frames.hex')))
    p.add_argument('--chunk-size',type=int,default=3); a=p.parse_args()
    if a.chunk_size<1: p.error('chunk-size must be positive')
    raw=bytes.fromhex(Path(a.input).read_text()); d=Decoder(); records=[]
    for i in range(0,len(raw),a.chunk_size): records+=d.feed(raw[i:i+a.chunk_size])
    print(json.dumps({'records':records,'crc_errors':d.crc_errors,'discarded_bytes':d.discarded,'buffered_bytes':len(d.buffer)},indent=2))
