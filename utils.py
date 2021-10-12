from pathlib import Path
from carspy import CarsSpectrum, CarsFit
from carspy.utils import pkl_load, downsample
from carspy.convol_fcn import asym_Gaussian, asym_Voigt
import numpy as np
from lmfit.printfuncs import fit_report
import plotly.graph_objects as go

INIT_COMP = {'N2': 0.79,
             'Ar': 0.0,
             'CO2': 0,
             'CO': 0,
             'H2': 0,
             'O2': 0.21,
             'H2O': 0,
             'CH4': 0}

DEFAULT_SETTINGS_CONDITIONS = {
    "pressure": 1,
    "temperature": 1750,
    "comp": INIT_COMP,
}

DEFAULT_SETTINGS_MODELS = {
    "pump_lw": 1.0,
    "nu_start": 2262,
    "nu_end": 2345,
    "num_sample": 5000,
    "pump_ls": "Gaussian",
    "chi_rs": "isolated",
    "convol": "Yuratich",
    "doppler_effect": "disable"
}

DEFAULT_SETTINGS_SLIT = {
    "sigma": 1.2,
    "k": 1.2,
    "a_sigma": 0.2,
    "a_k": 0.5,
    "sigma_L_l": 0.2,
    "sigma_L_h": 0.4,
    "slit": "sGaussian"
}

DEFAULT_SETTINGS_FIT = {
    "sample_length": 120,
    "noise_level": 1.5,
    "offset": 0.5
}

SPECT_PATH = Path(__file__).parent / "_data/_DEFAULT_SPECTRUM"
SIGNAL_PATH = Path(__file__).parent / "_data/_DEFAULT_FIT_SIGNAL"
DEFAULT_SPECTRUM = pkl_load(SPECT_PATH)
DEFAULT_FIT_SIGNAL = pkl_load(SIGNAL_PATH)


def synthesize_cars(pressure=1, temperature=1750, pump_lw=1.0,
                    nu_start=2262, nu_end=2345, num_sample=5000,
                    pump_ls='Gaussian', chi_rs='isolated',
                    convol='Y', doppler_effect=False, comp=None):
    synth_mode = {'pump_ls': pump_ls,
                  'chi_rs': chi_rs,
                  'convol': convol,
                  'doppler_effect': doppler_effect,
                  'chem_eq': False}

    if comp is None:
        comp = INIT_COMP

    nu = np.linspace(nu_start, nu_end, num=num_sample)
    cars = CarsSpectrum(pressure=pressure, init_comp=comp,
                        chi_set="SET 3")
    _, spect = cars.signal_as(temperature=temperature,
                              nu_s=nu,
                              synth_mode=synth_mode,
                              pump_lw=pump_lw)

    return nu, spect


def plot_cars(nu=None, spect=None, y_scale="Linear"):
    if nu is None and spect is None:
        nu, spect = synthesize_cars()
    nu = np.array(nu)
    spect = np.array(spect)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=nu, y=spect/spect.max(),
        mode='lines',
        name="CARS Signal",
    ))

    fig.update_traces(hoverinfo='skip', selector=dict(type='scatter'))
    fig.update_layout(height=400,
                      margin={'l': 10, 'b': 10, 'r': 10, 't': 10},
                      xaxis_title="Wavenumber [1/cm]",
                      yaxis_title="Signal [-]")
    if y_scale == "Log":
        fig.update_yaxes(type="log", range=[-2.5, 0.2], dtick=1)

    return fig


def slit_profile(nu, parameters):
    lineshape = parameters["slit"]
    parameters.pop("slit")
    if lineshape == "sGaussian":
        parameters = {key: parameters[key]
                      for key in list(parameters.keys())[:4]}
        spect = asym_Gaussian(np.array(nu), 1/2*(nu[0] + nu[-1]),
                              **parameters, offset=0)
    elif lineshape == "sVoigt":
        spect = asym_Voigt(np.array(nu), 1/2*(nu[0] + nu[-1]),
                           **parameters, offset=0)
    return spect


def plot_slit(nu, parameters):
    spect = slit_profile(nu, parameters)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=nu, y=spect/spect.max(),
        mode='lines',
    ))

    fig.update_traces(hoverinfo='skip', selector=dict(type='scatter'))
    fig.update_layout(height=280,
                      margin={'l': 10, 'b': 10, 'r': 10, 't': 10},
                      xaxis_title="Wavenumber [1/cm]",
                      yaxis_title="Signal [-]")

    return fig


def plot_placeholder(height=400):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[0], y=[0],
        mode='lines',
    ))

    fig.update_traces(hoverinfo='skip', selector=dict(type='scatter'))
    fig.update_layout(height=height,
                      margin={'l': 10, 'b': 10, 'r': 10, 't': 10},
                      xaxis_title="Wavenumber [1/cm]",
                      yaxis_title="Signal [-]")

    return fig


def downsample_synth(nu, spect, nu_start, nu_end, sample_length, noise_level,
                     offset, slit_parameters):
    np.random.seed(42)
    noise = np.random.rand(sample_length)
    slit_fcn = slit_profile(nu, slit_parameters)
    nu_expt = np.linspace(nu_start+2, nu_end-2, num=sample_length)
    spect_conv = np.convolve(spect, slit_fcn, 'same')
    spect_expt = (downsample(nu_expt, nu, spect_conv) + noise*noise_level
                  - offset)
    x_range = [nu_start, nu_end]

    return nu_expt, spect_expt, x_range


def plot_fitting(nu_expt, spect_expt, x_range, mode="markers"):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=np.array(nu_expt), y=np.array(spect_expt)/np.array(spect_expt).max(),
        mode=mode,
        name="CARS Signal",
    ))

    fig.update_traces(hoverinfo='skip', selector=dict(type='scatter'))
    fig.update_layout(height=400,
                      margin={'l': 10, 'b': 10, 'r': 10, 't': 10},
                      xaxis_title="Wavenumber [1/cm]",
                      yaxis_title="Signal [-]",
                      xaxis_range=x_range)
    return fig


def add_fit_result(fig, nu, spect):
    fig.add_trace(go.Scatter(
        x=np.array(nu), y=np.array(spect)/np.array(spect).max(),
        mode="lines",
        name="Best Fit"
    ))
    return fig


def least_sqrt_fit(nu_expt, spect_expt, slit_parameters, settings_models,
                   settings_conditions):
    modes = {
        'power_factor': 0,
        'downsample': 'local_mean',
        'slit': slit_parameters['slit'],
        'pump_ls': settings_models['pump_ls'],
        'chi_rs': settings_models['chi_rs'],
        'convol': settings_models['convol'],
        'doppler_effect': settings_models['doppler_effect'],
        'chem_eq': False,
        'fit': 'custom'
    }

    init_comp = settings_conditions['comp']
    fit_expt = CarsFit(np.array(spect_expt), np.array(nu_expt),
                       fit_mode=modes, ref_fac=80,
                       pressure=settings_conditions['pressure'],
                       init_comp=init_comp)
    fit_expt.preprocess()
    params = (
        ('temperature', 1500, True, 250, 3000),
        ('del_Tv', 0, False),
        ('x_mol', init_comp['N2'], False),
        ('nu_shift', 0, False),
        ('nu_stretch', 1, False),
        ('pump_lw', 0.2, False),
        ('param1', slit_parameters['sigma'], False),
        ('param2', slit_parameters['k'], False),
        ('param3', slit_parameters['a_sigma'], False),
        ('param4', slit_parameters['a_k'], False),
        ('param5', slit_parameters['sigma_L_l'], False),
        ('param6', slit_parameters['sigma_L_h'], False)
    )

    fit_expt.ls_fit(add_params=params, show_fit=False)
    return fit_expt.fit_result


def unpack_lmfit(result):
    nu = result.userkws['nu_expt']
    signal_expt = result.data
    best_fit = result.best_fit
    T_fit = result.params['temperature'].value
    dT = result.params['temperature'].stderr
    report = fit_report(result)
    return {
        'nu': nu,
        'signal_expt': signal_expt,
        'best_fit': best_fit,
        'T_fit': T_fit,
        'dT': dT,
        'report': report
    }


if __name__ == "__main__":
    from carspy.utils import pkl_dump
    pkl_dump("_DEFAULT_SPECTRUM", synthesize_cars())
