
from pathlib import Path
import pandas as pd
from netCDF4 import Dataset

import ftplib

# define a function to grab file from gdac
def download_file(ftp, fn, local_dir):
    '''
    download an Argo file given a file name formatted in the same way as in the
    Argo index files
    '''
    local_file = local_dir / fn

    if local_file.exists():
        print(f'file {fn} previously downloaded')
    else:
        print(f'downloading file {fn}...', end='')
        local_file.parent.mkdir(parents=True, exist_ok=True)
        lf = open(local_file, 'wb')
        # retrieve the file on FTP server,
        ftp.retrbinary('RETR ' + fn, lf.write)
        lf.close()
        print('done')

    return

# get all bgc floats with an MTIME parameter, which is simple since the BGC
# Argo index has a 'parameters' field where it is listed

# get bgc index, replace with your local path to the index
argo_path = Path('/Users/GordonC/Documents/data/Argo')
bgc_file = argo_path / 'argo_bio-profile_index.txt.gz'
bx = pd.read_csv(bgc_file, header=8, compression='gzip')
bx['wmo'] = [int(f.split('/')[-3]) for f in bx['file']]

# subset to only oxygen floats, and then only floats with timing
bx = bx[bx['parameters'].str.contains('DOXY')]
bx_time = bx[bx['parameters'].str.contains('MTIME')]

# seeing if floats have NB_SAMPLE_CTD is slightly more complicated and
# computationally heavy, need to load the actual profile file to see if the
# field exists. 

# first, get the unique floats with oxygen
doxy_floats = bx['wmo'].unique()

# NB_SAMPLE_CTD is in core file, so get the core index
core_file = argo_path / 'ar_index_global_prof.txt.gz'
cx = pd.read_csv(core_file, header=8, compression='gzip')
# populate wmo column
cx['wmo'] = [int(f.split('/')[-3]) for f in cx['file']]
# get the core files that correspond to our doxy floats
cx_doxy = cx[cx['wmo'].isin(doxy_floats)]

# there are ~1500 DOXY floats, load the most recent profile from each and
# check for NB_SAMPLE_ID - note that taking the most recent profile means it
# might not be present in past profiles, if a given DAC perhaps updated their
# processing chain
dac_dir = argo_path / 'dac'
url = 'ftp.ifremer.fr'
ftp = ftplib.FTP(url)
ftp.login()
ftp.cwd('ifremer/argo/dac')

# list to keep track of presence or NB_SAMPLE_CTD
sample_ix = []
# loop through oxygen floats
for flt in doxy_floats:
    # get most recent core file
    recent_core = cx_doxy[cx_doxy['wmo'] == flt]['file'].iloc[-1]
    # download it
    download_file(ftp, recent_core, dac_dir)
    # read it in
    nc = Dataset(dac_dir / recent_core)
    # check for NB_SAMPLE_CTD
    sample_ix.append('NB_SAMPLE_CTD' in nc.variables.keys())

# now get the floats and core index that have NB_SAMPLE_CTD in their most
# recent profile
nb_doxy_floats = doxy_floats[sample_ix]
nb_doxy_ix = cx_doxy[cx_doxy['wmo'].isin(nb_doxy_floats)]

# check - do any floats with NB_SAMPLE_CTD not have MTIME?
nb_no_mtime = set(nb_doxy_floats) - set(bx_time['wmo'].unique())