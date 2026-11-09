"""Metadata-level look at a compiled .ex5 (no decryption, no disassembly): size, header bytes, entropy per block, and the readable
ASCII / UTF-16LE strings (what a hex viewer shows)."""
import sys, math, re, collections
p = sys.argv[1]; b = open(p, 'rb').read()
print('size', len(b), 'bytes; first 16 bytes:', b[:16].hex(' '), '|', b[:4])
def ent(x):
    c = collections.Counter(x); n = len(x)
    return -sum(v / n * math.log2(v / n) for v in c.values()) if n else 0
blk = 16384
es = [ent(b[k:k + blk]) for k in range(0, len(b), blk)]
print('entropy per 16 KB block (8.0 = random / encrypted):', ' '.join('%.2f' % e for e in es))
asc = [m.group().decode() for m in re.finditer(rb'[\x20-\x7e]{6,}', b)]
u16 = [m.group().decode('utf-16le') for m in re.finditer(rb'(?:[\x20-\x7e]\x00){5,}', b)]
print('ASCII strings >= 6 chars:', len(asc), '| UTF-16 strings >= 5 chars:', len(u16))
for s in u16[:80]: print('  U16:', s[:160])
for s in asc[:40]: print('  ASC:', s[:160])
