#!/usr/bin/python

import regex as re

import numpy as np
from scipy.interpolate import interp1d

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

my_pair = [
    'coriolis/6904117/profiles/BR6904117_150.nc',
    'coriolis/6904117/profiles/BR6904117_151D.nc'
]
paired_profiles = df.loc[my_pair]

style = len(paired_profiles.index.get_level_values('file').unique())*['']
fig, ax = plt.subplots()
ax.plot(np.nan, np.nan, color=sns.color_palette('colorblind')[0], label='Ascending')
ax.plot(np.nan, np.nan, color=sns.color_palette('colorblind')[1], label='Descending')
ax.legend(loc=4)
sns.lineplot(x='DOXY', y='PRES', data=paired_profiles,
    hue='direction', style='file', dashes=style,
    sort=False, legend=False, ax=ax
)

# # I don't want to get temperature so lets correct for just using time
# corr_doxy = np.array([])
# for f in my_pair:
#     data = paired_profiles.loc[f]
#     corr_doxy = np.append(corr_doxy, 
#         correct_response_time_Tconst(data.MTIME.values, data.DOXY.values, 100))
# paired_profiles['DOXY_ADJUSTED_Tconst'] = corr_doxy
# style = len(paired_profiles.index.get_level_values('file').unique())*[(1,1)]
# sns.lineplot(x='DOXY_ADJUSTED_Tconst', y='PRES', data=paired_profiles,
#     hue='direction', style='file', dashes=style,
#     sort=False, legend=False, ax=ax
# )

# ok fine lets do it properly
phys = argo.float(6904117).prof
my_physical_pair = [f.replace('BR', 'R') for f in my_pair]
phys = phys[phys.file.isin(my_physical_pair)]
phys_data = phys.levels[['PRES', 'TEMP', 'PSAL']]
phys_data = phys_data[~phys_data.PRES.isna()]
phys_data = phys_data[~phys_data.TEMP.isna()]

# interpolate temperature to bgc grid
f = interp1d(phys_data.PRES, phys_data.TEMP, kind='linear', bounds_error=False)
paired_profiles['TEMP'] = f(paired_profiles['PRES'])

corr_doxy = np.array([])
for f in my_pair:
    data = paired_profiles.loc[f]
    corr_doxy = np.append(corr_doxy, 
        correct_response_time(data.MTIME.values, data.DOXY.values, data.TEMP.values, 110))
paired_profiles['DOXY_ADJUSTED'] = corr_doxy
style = len(paired_profiles.index.get_level_values('file').unique())*[(10,1)]
sns.lineplot(x='DOXY_ADJUSTED', y='PRES', data=paired_profiles,
    hue='direction', style='file', dashes=style,
    sort=False, legend=False, ax=ax
)

ax.set_ylim((100,0))
fig.set_size_inches(
    fig.get_figwidth()/3,
    fig.get_figheight(),
)