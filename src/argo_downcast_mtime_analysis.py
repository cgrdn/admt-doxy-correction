#!/usr/bin/python

import regex as re

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style='ticks', palette='colorblind')

import argopandas as argo
from bgcArgoDMQC import correct_response_time, correct_response_time_Tconst

# grab floats we are interested in
# downcasts = argo.bio_prof.subset_direction('desc') \
    # .subset_parameter('MTIME') \
    # .subset_parameter('DOXY')

# the above retruns mostly profiles for 6904117 so lets just look at that float
bio = argo.float(6904117).bio_prof
df = bio.levels[['PRES', 'MTIME', 'DOXY']]
# goes from 1,601,934 to 139,803 points! (only 8.7% valid)  
df = df[~df.DOXY.isna()]
df = df[~df.MTIME.isna()]

# assign direction to each data point - this takes a minute
df['direction'] = ['descent' if re.match('.*D\.nc', f) \
    else 'ascent' \
    for f in df.index.get_level_values('file')]

style = len(df.index.get_level_values('file').unique())*['']
fig, ax = plt.subplots()
ax.plot(np.nan, np.nan, color=sns.color_palette('colorblind')[0], label='Ascending')
ax.plot(np.nan, np.nan, color=sns.color_palette('colorblind')[1], label='Descending')
ax.legend(loc=4)
sns.lineplot(x='DOXY', y='PRES', data=df,
    hue='direction', style='file', dashes=style,
    sort=False, legend=False, ax=ax, alpha=0.5
)
ax.set_ylim((200,0))

paired_profiles = df.loc[[
    'coriolis/6904117/profiles/BR6904117_001.nc',
    'coriolis/6904117/profiles/BR6904117_002D.nc'
]]

style = len(paired_profiles.index.get_level_values('file').unique())*['']
fig, ax = plt.subplots()
ax.plot(np.nan, np.nan, color=sns.color_palette('colorblind')[0], label='Ascending')
ax.plot(np.nan, np.nan, color=sns.color_palette('colorblind')[1], label='Descending')
ax.legend(loc=4)
sns.lineplot(x='DOXY', y='PRES', data=paired_profiles,
    hue='direction', style='file', dashes=style,
    sort=False, legend=False, ax=ax
)
ax.set_ylim((200,0))