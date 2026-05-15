# Period windows and Feigenbaum drift

This report adds a more explicit period-doubling lane to the repo. Instead of only showing the bifurcation picture, it scans the parameter axis directly, detects stable periods from the tail, and then measures the superstable centers of the doubling cascade.

## Direct period scan

- chaotic or unresolved points on this scan: 321/820 (39.1%)
- detected period 1: 0/820 (0.0%)
- detected period 2: 365/820 (44.5%)
- detected period 4: 76/820 (9.3%)
- detected period 8: 18/820 (2.2%)
- detected period 16: 5/820 (0.6%)
- detected period 32: 1/820 (0.1%)
- detected period 64: 0/820 (0.0%)

This is not a proof that the whole interval has that exact period. It is a sampled public summary. But it is enough to make the stable windows show up as a real scan object instead of a vague visual impression.

## Superstable points

At the center of a stable band, the critical point `x = 0.5` falls back onto itself after one whole cycle. Those are the superstable points used in the lower panels of the new figure.

- period 2: r ≈ 3.236067977498
- period 4: r ≈ 3.498561699327
- period 8: r ≈ 3.554640862769
- period 16: r ≈ 3.566667379856
- period 32: r ≈ 3.569243531637
- period 64: r ≈ 3.569795293750

## Feigenbaum gap-ratio estimates

- using periods 2, 4, and 8: δ ≈ 4.680771
- using periods 4, 8, and 16: δ ≈ 4.662960
- using periods 8, 16, and 32: δ ≈ 4.668404
- using periods 16, 32, and 64: δ ≈ 4.668954

## Reading

- the top scan makes the stable windows explicit: low periods occupy wide clean bands, then the doubling cascade compresses as chaos takes over more of the axis
- the superstable sequence climbs toward the chaos onset near `r ≈ 3.57`, which is why the lower-left plot bunches up so quickly
- the δ estimates are still rough because this is a small public calculation, but the drift is already in the right direction and makes the scaling story visible

Open `assets/period-doubling-atlas.svg`, `assets/period-doubling-atlas.png`, and `notebooks/period_doubling_feigenbaum.ipynb` next.
