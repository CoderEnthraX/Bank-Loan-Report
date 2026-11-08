import numpy as np
# simple power: SE of test-both excess ~1.9; true edge ~4.8 (train+valid pooled) -> P(obs <= -0.43)
from math import erf,sqrt
z=(-0.43-4.8)/1.92; print('z',z,'P',0.5*(1+erf(z/sqrt(2))))
z=(-0.43-4.8*0.5)/1.92; print('half edge: P',0.5*(1+erf(z/sqrt(2))))
