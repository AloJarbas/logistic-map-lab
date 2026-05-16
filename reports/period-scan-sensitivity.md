# Period-scan sensitivity

This report asks a narrower question than the main period-doubling atlas: how much of the stable-window picture disappears if the scan tail is too short?

The comparison keeps the same `r` grid and the same tolerance. Only the scan patience changes:

- short scan: `warmup = 1200`, `keep = 64`
- deep scan: `warmup = 3600`, `keep = 512`

## Main read

- recovered stable points in the deeper scan: 21/820 (2.6%)
- stable points lost by the deeper scan: 0
- period shifts between two stable detections: 0
- deepest detected period in the deeper scan: 32
- recovered windows start showing up around `r ≈ 3.001221` and keep appearing as late as `r ≈ 3.870574`

## Count comparison

- period 2: short 361, deep 366
- period 4: short 75, deep 78
- period 8: short 16, deep 18
- period 16: short 0, deep 4
- period 32: short 0, deep 1
- chaos or unresolved: short 340, deep 319

## Reading

- the short scan does not rewrite the whole picture; it mainly erases the thin stable bands near chaos onset and a few narrower windows farther right
- that means the cutoff problem is selective, not uniform: the wide low-period windows survive, while the narrow ones disappear first
- a deeper tail also resolves some windows to higher periods instead of only flipping chaos to stable, which is why the zoom panel shows orange points climbing above the blue ones

Open `assets/period-scan-sensitivity.svg`, `assets/period-scan-sensitivity.png`, and `notebooks/period_scan_sensitivity.ipynb` next.
