#!/usr/bin/python

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

import argopandas as argo
from bgcArgoDMQC import correct_response_time

# get oxygen floats with timing and oxygen data
ix = argo.bio_prof.subset_parameter('DOXY')
ix = ix.subset_parameter('MTIME')
# select just one float
flt = np.unique([f.split('/')[1] for f in ix.file])[-1]
ix = ix.subset_float(flt)
ix = ix[ix.file == ix.file.iloc[-1]]
# get the data for those floats
df = ix.levels[['PRES', 'MTIME', 'DOXY']]

# after some inspection, this is the N_PROF index we want
fn = ix.file.iloc[0]
bprof = df

# grab the corresponding core file
cx = argo.float(flt).prof
cx = cx[cx.file == cx.file.iloc[-1]]
# N_PROF doesn't match here, but this is the only one with valid T/S data
cprof = cx.levels[['PRES', 'TEMP', 'PSAL']]

# using pressure as the common axis, interpolate t, T, O to common axis
dz = 2.5
interp_pres = np.arange(0, 1000+dz, dz)
# fill in a dataframe with interpolated values
idf = pd.DataFrame()
idf['PRES'] = interp_pres
for key, source in zip(['MTIME', 'DOXY', 'TEMP'], [bprof, bprof, cprof]):
    f = interp1d(source['PRES'], source[key], bounds_error=False)
    idf[key] = f(interp_pres)

# correct for an arbitrary thickness
Il = 125
doxy_corr = correct_response_time(idf['MTIME'], idf['DOXY'], idf['TEMP'], Il)

print('done')