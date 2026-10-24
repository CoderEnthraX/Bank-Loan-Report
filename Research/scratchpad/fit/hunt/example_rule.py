# Example rule module for hookeval.py: oracle-free baseline (always 1.8 ATR, no extra filter).
def stop_fn(P, i, d, entry, stop, A, ctx):
    return stop
def arm_fn(P, i, d, ctx):
    return True
