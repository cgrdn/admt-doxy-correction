import numpy as np

import argopandas as argo

import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style='ticks', palette='colorblind')
import cmocean.cm as cmo

import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

def max_gradient(pres, doxy):
    grad = doxy.diff()/pres.diff()
    max_grad = -np.inf
    for i in grad.index.unique('N_PROF'):
        max_grad = max(max_grad, grad.loc[i][grad.loc[i].abs() < 99999].abs().max())
    return max_grad

def format_global_map(ax):
    ax.set_xticks([-180, -120, -60, 0, 60, 120, 180], crs=ccrs.PlateCarree())
    ax.set_yticks([-90, -60, -30, 0, 30, 60, 90], crs=ccrs.PlateCarree())
    lon_formatter = LongitudeFormatter(zero_direction_label=True)
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)

fig = plt.figure()
axis = fig.add_subplot(projection=ccrs.PlateCarree())
axis.set_global()
axis.stock_img()

for year in range(2020, 2023):
    for month in range(1, 13):
        print(f'{year}-{month:02d}')
        end_date = f'{year}-{month+1:02d}' if month != 12 else f'{year+1}-01'
        try:
            ix = argo.bio_prof.subset_date(f'{year}-{month:02d}', end_date).subset_parameter('DOXY')
            data = ix.levels[['PRES', 'DOXY', 'DOXY_QC']]
        except:
            ix = argo.bio_prof.subset_date(f'{year}-{month:02d}', end_date).subset_parameter('DOXY')
            data = ix.levels[['PRES', 'DOXY', 'DOXY_QC']]

        ix['max_doxy_grad'] = [max_gradient(data.loc[i].PRES, data.loc[i].DOXY) for i in ix.file]
        ix.loc[ix['max_doxy_grad'] < 0, 'max_doxy_grad'] = np.nan

        g = axis.scatter(
            x=ix.longitude, y=ix.latitude, 
            c=ix.max_doxy_grad, cmap=cmo.amp,
            s=5, vmin=0, vmax=12, 
            transform=ccrs.PlateCarree()
        )

cb = plt.colorbar(g, orientation='horizontal')
cb.set_label('Max Abs DOXY Gradient ($\mathregular{\mu}$mol kg$^{-1}$ dbar$^{-1}$)')

format_global_map(axis)
fig.savefig('DOXY_GRADIENT_map.png', bbox_inches='tight', dpi=300)
