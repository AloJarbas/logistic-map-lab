# Logistic Map Lab

A tiny recurrence with enough structure to teach fixed points, period doubling, Lyapunov exponents, and chaos without hand-waving.

This repo keeps the scope narrow on purpose:
- one system,
- pure Python,
- generated SVG figures,
- small tests that check the math stays honest.

## What is here

- `logisticlab/core.py` — iteration, long-run tail sampling, orbit-density histograms, and Lyapunov exponent estimation
- `logisticlab/gallery.py` — figure generators for the bifurcation diagram, Lyapunov sweep, cobweb triptych, and orbit-density contrast card
- `scripts/generate_gallery.py` — one command to rebuild the assets
- `tests/test_core.py` — small verification checks for boundedness, fixed-point behavior, and Lyapunov sign

## Generated figures

### Bifurcation diagram

![Bifurcation diagram](assets/logistic-bifurcation.svg)

### Lyapunov sweep

![Lyapunov sweep](assets/lyapunov-sweep.svg)

### Cobweb triptych

![Cobweb triptych](assets/cobweb-triptych.svg)

### Orbit-density contrast

![Orbit-density contrast](assets/density-contrast.svg)

## Run it

```bash
python3 scripts/generate_gallery.py
python3 -m unittest discover -s tests
```

## Why this repo exists

The logistic map shows how much nonlinear structure can come out of one line:

```text
x[n+1] = r x[n] (1 - x[n])
```

That makes it a good public micro-lab:
- simple enough to inspect directly,
- rich enough to generate real artifacts,
- useful as a bridge from first dynamical-systems intuition to more serious chaos work.

## Good next moves

- add a small parameter-report CLI for fixed points, cycle hints, and Lyapunov classification
- add a notebook on period-doubling and Feigenbaum scaling
- add one comparison note on why the exact r = 4 invariant density is useful but still a special case
- branch into a second one-dimensional map only if the logistic lane already feels complete
