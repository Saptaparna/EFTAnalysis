'''
Create single bin ROOT files.

NOTE: Auto-fills "-1" in observation line of datacard (so this will come from the "h_data_obs" histogram).

This script should be run using miniconda VVV environment (needs uproot).
'''
import os
import subprocess
import argparse
import uproot
# local imports
import sys
fpath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(fpath,'..'))
from DATACARD_DICT import datacard_dict
from CONFIG_VERSIONS import versions_dict
from MISC_CONFIGS import template_filename, datacard_dir

# generic function
def split_func(ddir, fname, sname_sch, dc_file):
    dc_upr = uproot.open(os.path.join(ddir, fname))
    # how many bins?
    bins = len(dc_upr[dc_upr.keys()[0]].to_numpy()[0])
    for i in range(bins):
        bin_n = i+1
        # updated file name
        # dc_file_bin = dc_file.replace(sname_sch, sname_sch+f'_bin{bin_n}')
        dc_file_bin = fname.split('.')
        dc_file_bin[1] = dc_file_bin[1] + f'_bin{bin_n}'
        dc_file_bin = os.path.join(ddir, '.'.join(dc_file_bin))
        with uproot.recreate(dc_file_bin) as file_:
            for k in dc_upr.keys():
                k = k.split(';')[0]
                n, bin_edges = dc_upr[k].to_numpy()
                n_new = n[i:i+1]
                # increase n_new to avoid normalization error
                if n_new[0] < 1e-4:
                    n_new[0] = 1e-4
                bin_edges_new = bin_edges[i:i+2]
                file_[k] = (n_new, bin_edges_new)
        # also want to update the datacard
        update_datacard(ddir, dc_file, bin_n)

# new datacard
def update_datacard(ddir, dc_name, bin_n):
    # create new datacard file name
    dc_new = dc_name.split('.')
    dc_new[1] = dc_new[1] + f'_bin{bin_n}'
    dc_new = '.'.join(dc_new)
    # load contents of full datacard
    with open(os.path.join(ddir, dc_name), 'r') as f:
        lines = [l.strip() for l in f.readlines()]
    # create new file, updating the root file lines
    with open(os.path.join(ddir, dc_new), 'w') as f:
        for line in lines:
            if line[:6] == 'shapes':
                line_new = line.split('.')
                line_new[1] = line_new[1] + f'_bin{bin_n}'
                line_new = '.'.join(line_new)
            elif line[:11] == 'observation':
                line_new = 'observation -1'
            else:
                line_new = line
            f.write(line_new+'\n')

# split subchannels in a channel
def split_channel_subchannels(channel, version, datacard_dict, WC, ScanType):
    dcdir = datacard_dir
    sname_ch = datacard_dict[channel]['info']['short_name']
    subchannels = datacard_dict[channel]['subchannels'].keys()
    print(f'Channel: {channel}; Subchannel: ', end='')
    for i, subch in enumerate(subchannels):
        if i == (len(subchannels)-1):
            print(subch, end='')
        else:
            print(subch,', ', end='')
        sname_sch = datacard_dict[channel]['subchannels'][subch]['info']['short_name']
        # update subchannel name if there is rescaling
        if versions_dict[channel]['lumi'] == '2018':
            sname_sch += '_2018_scaled'
            print(' (2018 scaled)', end='')
        tfile = template_filename.substitute(channel=sname_ch, subchannel=sname_sch, WC=WC, ScanType=ScanType, purpose='DataCard_Yields', proc='_Cleaned', version=version, file_type='root')
        dc_file = template_filename.substitute(channel=sname_ch, subchannel=sname_sch, WC=WC, ScanType=ScanType, purpose='DataCard_Yields', proc='', version=version, file_type='txt')
        # dc_file = os.path.join(dcdir, channel, version, tfile)
        # run helper functions
        dir_ = os.path.join(dcdir, channel, version)
        split_func(dir_, tfile, sname_sch, dc_file)
    print()


if __name__=='__main__':
    # parse commmand line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--WC',
                        help=f'Which Wilson Coefficient to study for 1D limits? ["cW" (default),]')
    parser.add_argument('-s', '--ScanType',
                        help=f'What type of EFT scan was included in this file? ["_1D" (default),]')
    args = parser.parse_args()
    if args.WC is None:
        args.WC = 'cW'
    if args.ScanType is None:
        args.ScanType = '_1D'
    #########################
    # split channel subchannels
    print('Splitting subchannels into single bins for each available channel:')
    print('=================================================')
    for channel in datacard_dict.keys():
        v = versions_dict[channel]['v']
        VERSION = f'v{v}'
        split_channel_subchannels(channel, VERSION, datacard_dict, WC=args.WC, ScanType=args.ScanType)
    print('=================================================\n')
    #########################