import sys
try:
    with open(sys.argv[1], 'r') as f:
        lines = [l for l in f if l.startswith("ATOM")]
    if not lines: sys.exit(1)
    x = [float(l[30:38]) for l in lines]
    y = [float(l[38:46]) for l in lines]
    z = [float(l[46:54]) for l in lines]
    cx, cy, cz = (max(x)+min(x))/2, (max(y)+min(y))/2, (max(z)+min(z))/2
    # Make a box big enough to cover the protein, max size 80
    sx, sy, sz = min(max(x)-min(x)+15, 80), min(max(y)-min(y)+15, 80), min(max(z)-min(z)+15, 80)
    print(f"{cx:.3f} {cy:.3f} {cz:.3f} {sx:.3f} {sy:.3f} {sz:.3f}")
except:
    sys.exit(1)
