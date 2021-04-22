# A Dash webapp for `carspy`

CARSpy is a Python library for synthesizing and fitting experimental Coherent
Anti-Stokes Raman Spectra (CARS).
Briefly, CARSpy has implemented a wide range of physical models that take into account of temperatural broadening, collisional narrowing (at high pressures),
the effect of laser linewidth on the CARS spectra (cross-coherence), etc. It is currently optimized for nitrogen but can be easily adapted for other common species.
This web app is built with [Dash](https://dash.plotly.com) to demonstrate the most basic functions of CARSpy.
To test it out locally on your actual experimental data, simply install CARSpy via

```console
$ pip install carspy
```

Please check out the [project homepage](https://github.com/chuckedfromspace/carspy) and the [documentation](https://carspy.readthedocs.io) for detailed instructions on using CARSpy for data analysis.
