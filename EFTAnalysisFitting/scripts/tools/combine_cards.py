import os
import subprocess
import argparse
# local imports
import sys
fpath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(fpath,'..'))
from DATACARD_DICT import datacard_dict
from CONFIG_VERSIONS import versions_dict, WC_ALL
from MISC_CONFIGS import template_filename, datacard_dir

# combine subchannels in a channel
def combine_channel_subchannels(channel, version, datacard_dict, WC, ScanType, StatOnly):
    if StatOnly:
        SO_lab = '_StatOnly'
    else:
        SO_lab = ''
    dcdir = datacard_dir
    sname_ch = datacard_dict[channel]['info']['short_name']
    subchannels = datacard_dict[channel]['subchannels'].keys()
    cmd_str = 'combineCards.py'
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
        tfile = template_filename.substitute(channel=sname_ch, subchannel=sname_sch, WC=WC, ScanType=ScanType, purpose='DataCard_Yields', proc=SO_lab, version=version, file_type='txt')
        dc_file = os.path.join(dcdir, channel, version, tfile)
        dc_name = f' sch{sname_sch}'
        cmd_str += f'{dc_name}={dc_file}'
    print()
    # construct output file
    tfile_comb = template_filename.substitute(channel=sname_ch, subchannel='_combined', WC=WC, ScanType=ScanType, purpose='DataCard_Yields', proc=SO_lab, version=version, file_type='txt')
    comb_file = os.path.join(datacard_dir, 'combined_datacards', 'channel', tfile_comb)
    cmd_str += f'> {comb_file}'
    # run combine script
    # stdout = subprocess.PIPE
    stdout = None
    proc = subprocess.run(cmd_str, shell=True, stdout=stdout)

# combine all channels
def combine_all_channels(datacard_dict, WC, ScanType, StatOnly):
    if StatOnly:
        SO_lab = '_StatOnly'
    else:
        SO_lab = ''
    dcdir = datacard_dir
    channels = datacard_dict.keys()
    cmd_str = 'combineCards.py'
    print(f'Channel: ', end='')
    n_ch_added = 0
    for i, ch in enumerate(channels):
        WCs = versions_dict[ch]['EFT_ops']
        if not WC in WCs:
            continue
        else:
            n_ch_added += 1
        print(ch, end='')
        # if i == (len(channels)-1):
        #     print(ch)
        # else:
        #     print(ch,', ', end='')
        v = versions_dict[ch]['v']
        version = f'v{v}'
        if versions_dict[ch]['lumi'] == '2018':
            print(' (2018 scaled)', end='')
        sname_ch = datacard_dict[ch]['info']['short_name']
        # loop through subchannels
        subchannels = datacard_dict[ch]['subchannels'].keys()
        for j, subch in enumerate(subchannels):
            sname_sch = datacard_dict[ch]['subchannels'][subch]['info']['short_name']
            # update subchannel name if there is rescaling
            if versions_dict[ch]['lumi'] == '2018':
                sname_sch += '_2018_scaled'
                # print(' (2018 scaled)', end='')
            tfile_ch = template_filename.substitute(channel=sname_ch, subchannel=sname_sch, WC=WC, ScanType=ScanType, purpose='DataCard_Yields', proc=SO_lab, version=version, file_type='txt')
            dc_file = os.path.join(dcdir, ch, version, tfile_ch)
            dc_name = f' ch{sname_ch}sch{sname_sch}'
            cmd_str += f'{dc_name}={dc_file}'
        if i != (len(channels) - 1):
            print(', ', end='')
    print()
    # stop here if there weren't any WC matches
    if n_ch_added == 0:
        print('No channels have the following WC: '+WC+', combineCards.py will not be run!')
        return
    # construct output file
    tfile_comb = template_filename.substitute(channel='all', subchannel='_combined', WC=WC, ScanType=ScanType, purpose='DataCard_Yields', proc=SO_lab, version='vCONFIG_VERSIONS', file_type='txt')
    comb_file = os.path.join(datacard_dir, 'combined_datacards', 'full_analysis', tfile_comb)
    cmd_str += f'> {comb_file}'
    # run combine script
    # stdout = subprocess.PIPE
    stdout = None
    proc = subprocess.run(cmd_str, shell=True, stdout=stdout)


if __name__=='__main__':
    # parse commmand line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--Channel',
                        help=f'Which channel? ["all" (default), "0Lepton_2FJ", "0Lepton_3FJ", "2Lepton_OS", "2Lepton_SS"]')
    parser.add_argument('-w', '--WC',
                        help=f'Which Wilson Coefficient to study for 1D limits? ["all" (default), "cW" (default), ...]')
    parser.add_argument('-s', '--ScanType',
                        help=f'What type of EFT scan was included in this file? ["_1D" (default),]')
    args = parser.parse_args()
    # list of channels
    if args.Channel is None:
        args.Channel = 'all'
    if args.Channel == 'all':
        channels = datacard_dict.keys()
    else:
        channels = [args.Channel]
    if args.WC is None:
        args.WC = 'all'
    if args.WC == 'all':
        WCs_loop = WC_ALL
    else:
        WCs_loop = [args.WC]
    if args.ScanType is None:
        args.ScanType = '_1D'
    #########################
    # outer loop (over WC)
    for WC in WCs_loop:
        print(f'WC: '+WC)
        #########################
        # combine channel subchannels
        print('Combining subchannels for each available channel:')
        print('=================================================')
        for channel in channels:
            WCs = versions_dict[channel]['EFT_ops']
            if not WC in WCs:
                continue
            v = versions_dict[channel]['v']
            VERSION = f'v{v}'
            for StatOnly in [False, True]:
                print('Stat only? ', StatOnly)
                combine_channel_subchannels(channel, VERSION, datacard_dict, WC=WC, ScanType=args.ScanType, StatOnly=StatOnly)
        print('=================================================\n')
        #########################
        # combine all channels
        print('Combining all channels (complete analysis):')
        print('=================================================')
        for StatOnly in [False, True]:
            print('Stat only? ', StatOnly)
            combine_all_channels(datacard_dict, WC=WC, ScanType=args.ScanType, StatOnly=StatOnly)
        print('=================================================\n')
        #########################