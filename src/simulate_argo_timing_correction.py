#!/usr/bin/python

from pathlib import Path
argo_path = Path('/Users/GordonC/Documents/data/Argo/dac')

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from netCDF4 import Dataset

import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style='ticks', palette='colorblind')

import argopandas as argo
import bgcArgoDMQC as bgc

# get bio index
bio = argo.bio_prof[:]
# only oxygen profiles
doxy = bio[bio['parameters'].str.contains('DOXY')]
# only meds files
meds = doxy[doxy['file'].str.contains('meds')]

# get a recent profile
n = -1
fn = Path('garbage')
while not fn.exists():
    fn = argo_path / meds['file'].iloc[n]
    n = n-1
# get oxygen and pressure
nc = Dataset(fn)
pres = nc['PRES'][:].compressed()
doxy = nc['DOXY'][:].compressed()
# grab temperature from core file, cross fingers that dimensions match
core_fn = Path(fn.as_posix().replace('BR', 'R'))
cc = Dataset(core_fn)
temp = cc['TEMP'][:].compressed()

# arbitrarily assign times based on 10-15 m/min ascent w/ small amount of noise
# NOTE: speed is the villian here when it looks bad, meas need to be frequent
# should look at typical ascent rates, though I am pretty sure it is 10-15m/min
vv = 5 # vertical vel in m/min
time = -(pres - np.max(pres))/vv/60/24 # time in days 

# smooth oxygen
w = 7
# do from bottom up so that nan values are at depth
doxy_smooth = pd.Series(doxy[::-1]).rolling(w).mean().values[::-1]

# artificially increase sampling rate
# pres_hr = np.arange(0, 2000, 0.1)
# time_hr = -(pres_hr - np.max(pres_hr))/vv/60/24 # time in days 
# f = interp1d(pres, doxy, kind='linear', bounds_error=False, fill_value='extrapolate')
# doxy_hr = f(pres_hr)
# f = interp1d(pres, temp, kind='linear', bounds_error=False, fill_value='extrapolate')
# temp_hr = f(pres_hr)

# correct for a boundary layer thickness that corresponds to tau=70 at 20 deg C
Il = 125
doxy_corr = bgc.correct_response_time(time, doxy, temp, Il)
doxy_corr_smooth = bgc.correct_response_time(time, doxy_smooth, temp, Il)
# doxy_corr_hr = bgc.correct_response_time(time_hr, doxy_hr, temp_hr, Il)

# NOTE: it would be nice to put a vertical rug on this plot to show location of obs

# plot temperature and oxygen and corrected oxygen
fig, axes = plt.subplots(1, 2, sharey=True)
axes[0].plot(temp, pres)
axes[0].set_xlabel('Temperature ({}C)'.format(chr(176)))
axes[0].set_ylabel('Pressure (dbar)')

axes[1].plot(doxy, pres, label='Argo Observation')
axes[1].plot(doxy_corr, pres, label='Time Response Correction,\n$I_L = 125$, $\\tau_{20^oC} = 70$s')
axes[1].plot(doxy_corr_smooth, pres, label='Time Response Correction\nof Smoothed Oxygen ($w={}$)'.format(w))
# axes[1].plot(doxy_corr_hr, pres_hr, label='Time Response Correction\nwith Artificial Resolution (0.2dbar)')
axes[1].set_xlabel('Diss. Oxygen ($\mathregular{\mu}$mol kg$^{-1}$)')
axes[1].legend(loc=2, fontsize=6)

axes[0].set_title('Vertical Velocity: {} m min$^{{-1}}$'.format(vv), loc='left')
axes[0].set_ylim((250,0))

wmo = fn.as_posix().split('/')[-3]
fig.savefig(Path('../figures/{}_DOXY_trc_example.png'.format(wmo)), bbox_inches='tight', dpi=350)

