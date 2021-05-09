# A Dash webapp for `carspy`

CARSpy is a Python library for synthesizing and fitting experimental Coherent
Anti-Stokes Raman Spectra (CARS).
Briefly, CARSpy has implemented a wide range of physical models that take into account of temperatural broadening, collisional narrowing (at high pressures),
the effect of laser linewidth on the CARS spectra (cross-coherence), etc. It is currently optimized for nitrogen but can be easily adapted for other common species.
This web app is built with [Dash](https://dash.plotly.com) to demonstrate the most basic functions of CARSpy.
The computation/loading speed is largely limited by the cloud server. To get the best performance, follow the steps below to run the app locally.

## How to run this app

We suggest you to create a virtual environment for running this app with Python 3. Clone this repository
and open your terminal/command prompt in the root folder.

```console
git clone https://github.com/chuckedfromspace/carspy-dash
cd carspy-dash
python3 -m virtualenv venv
```

In Unix system:

```console
source venv/bin/activate
```

In Windows:

```console
venv\Scripts\activate
```

Install all required packages by running:

```console
pip install -r requirements.txt
```

Run this app locally with:

```console
python index.py
```

## Resources

If you are ready to work on your actual experimental data, simply install CARSpy via

```console
pip install carspy
```

Please check out the [project homepage](https://github.com/chuckedfromspace/carspy) and the [documentation](https://carspy.readthedocs.io) for detailed instructions on using CARSpy for data analysis.
