from carspy import CarsSpectrum
import numpy as np
import plotly.graph_objects as go

INIT_COMP = {'N2': 0.79,
             'Ar': 0.0,
             'CO2': 0,
             'CO': 0,
             'H2': 0,
             'O2': 0.21,
             'H2O': 0,
             'CH4': 0}

DEFAULT_SETTINGS = {
    "pressure": 1,
    "temperature": 1750,
    "pump_lw": 1.01,
    "nu_start": 2250,
    "nu_end": 2350,
    "pump_ls": "Gaussian",
    "chi_rs": "isolated",
    "convol": "Y",
    "doppler_effect": False
}


def synthesize_cars(pressure=1, temperature=1750, pump_lw=1.01,
                    nu_start=2250, nu_end=2350,
                    pump_ls='Gaussian', chi_rs='isolated',
                    convol='Y', doppler_effect=False):
    synth_mode = {'pump_ls': pump_ls,
                  'chi_rs': chi_rs,
                  'convol': convol,
                  'doppler_effect': doppler_effect,
                  'chem_eq': False}

    nu = np.linspace(nu_start, nu_end, num=10000)
    cars = CarsSpectrum(pressure=pressure, init_comp=INIT_COMP,
                        chi_set="SET 1")
    _, spect = cars.signal_as(temperature=temperature,
                              nu_s=nu,
                              synth_mode=synth_mode,
                              pump_lw=pump_lw)

    return nu, spect


def plot_cars(nu=None, spect=None):
    if nu is None and spect is None:
        nu, spect = synthesize_cars()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=nu, y=spect/spect.max(),
        mode='lines',
        name="CARS Signal",
    ))

    fig.update_traces(hoverinfo='skip', selector=dict(type='scatter'))
    fig.update_layout(height=400,
                      margin={'l': 20, 'b': 10, 'r': 10, 't': 10},
                      xaxis_title="Wavenumber [1/cm]",
                      yaxis_title="Signal [-]")

    return fig
