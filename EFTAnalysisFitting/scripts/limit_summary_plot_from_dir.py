# note: this requires uproot, and is typically ran on the GPU machine, rather than the LPC.
import os
import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator

# local imports
from DATACARD_DICT import datacard_dict
from extract_limits import get_lims, get_lims_w_best, CL_1sigma
from plotting import config_plots, ticks_in, ticks_sizes

config_plots()

datacard_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
# make paths absolute
datacard_dir = os.path.abspath(datacard_dir)


# this is a duplicate from limit_summary_plot.py
# could consider importing this function
def make_limit_summary_plot(root_file_dict_full, title, CL=0.95, add_hrule=True, plot_stat_only=True, xlim_factor=2.0, fixed_xlim=None, savefile=None):
    # bottom to top, plots 0, 1, 2, 3, ....
    # plot
    fig = plt.figure(figsize=(16, 8))
    ax = fig.add_axes([0.15, 0.1, 0.55, 0.8])
    # loop through files to plot
    LLs_all = []
    ULs_all = []
    yvals_all = []
    ylabels_all = []
    text_annot_all = []
    var_annot_all = []
    for i, item in enumerate(sorted(root_file_dict_full.items())):
        if i==0:
            label_total = r'Proj. (stat. $\bigoplus$ syst.)'
            label_stat = 'stat. only'
        else:
            label_total = None
            label_stat = None
        yval, info_dict = item
        yvals_all.append(yval)
        root_file_dict = info_dict['root_file_dict']
        ylabels_all.append(info_dict['ylabel'])
        var_of_choice = info_dict['variable_of_choice']
        # get limits and plot
        # total
        FT0, NLL, CL_list, NLL_cuts, LLs, ULs, FT0_best, NLL_best = get_lims_w_best([CL], FT0=None, NLL=None, root_file=root_file_dict['total'])
        err_low = FT0_best - LLs[0]
        err_high = ULs[0] - FT0_best
        ax.errorbar([FT0_best], [yval], xerr=[[err_low],[err_high]], c='black', capsize=8.0, linestyle='-', linewidth=2, capthick=2, markersize=16, marker='.', zorder=8, label=label_total)
        LLs_all.append(LLs[0])
        ULs_all.append(ULs[0])
        if abs(np.round(FT0_best, 3)) < 0.001:
            best_str = f'{0.0:0.3f}'
        else:
            best_str = f'{FT0_best:0.3f}'
        text_annot = rf'   ${best_str}\ ~^{{+ {err_high:0.3f} }}_{{- {err_low:0.3f} }}$'
        # stat only
        if plot_stat_only:
            FT0, NLL, CL_list, NLL_cuts, LLs, ULs, FT0_best_stat, NLL_best = get_lims_w_best([CL], FT0=None, NLL=None, root_file=root_file_dict['stat_only'])
            err_low = FT0_best - LLs[0]
            err_high = ULs[0] - FT0_best
            # ax.errorbar([FT0_best], [yval], xerr=[[err_low],[err_high]], c='blue', capsize=0., linestyle='-', linewidth=6, zorder=7, label=label_stat)
            ax.errorbar([FT0_best], [yval], xerr=[[err_low],[err_high]], c='magenta', capsize=0., linestyle='-', linewidth=6, zorder=7, label=label_stat)
            text_annot += rf'$\ ~^{{+ {err_high:0.3f} }}_{{- {err_low:0.3f} }}$'
        text_annot_all.append(text_annot)
        var_annot_all.append(rf'                                       {var_of_choice}')
    # axis labels
    ax.set_xlabel(r'Sensitivity to F$_{T0} / \Lambda^4$ [TeV]$^{-4}$')
    ax.set_title(title)
    # set xlim to be symmetric
    LLs_all = np.array(LLs_all)
    ULs_all = np.array(ULs_all)
    if xlim_factor is None:
        ax.set_xlim(fixed_xlim)
        # xlim = np.max(np.abs(fixed_xlim))
        xlim = np.min(np.abs(fixed_xlim))
    else:
        xlim = xlim_factor*np.max(np.abs([LLs_all, ULs_all]))
        ax.set_xlim([-xlim, xlim])
    # add dummy point above top for label space and below for aesthetics
    yvals = sorted(root_file_dict_full.keys())
    yrange = np.max(yvals) - np.min(yvals)
    ax.scatter([0.], [np.max(yvals) + 0.30 * yrange], s=0., alpha=0.)
    ax.scatter([0.], [np.min(yvals) - 0.1 * yrange], s=0., alpha=0.)
    # add rule between combined and others
    if add_hrule:
        yhrule = (yvals[-1] + yvals[-2]) / 2.
        ax.plot(ax.get_xlim(), [yhrule, yhrule], '--', c='gray', alpha=0.8)
    # annotations for sensitivity
    for yval, text_annot, var_annot in zip(yvals, text_annot_all, var_annot_all):
        ax.annotate(text_annot, (1.00*xlim, yval), xycoords='data', wrap=False, verticalalignment='center', zorder=100)
        ax.annotate(var_annot, (1.00*xlim, yval), xycoords='data', wrap=False, verticalalignment='center', zorder=100)
    # additional annotations
    # total, stat
    if plot_stat_only:
        header_str = '               total   stat.'
    else:
        header_str = '               total'
    header_y = np.min([np.max(yvals) + 0.5, np.max(yvals) + 0.30 * yrange])
    ax.annotate(header_str, (1.00*xlim, header_y), xycoords='data')
    # var of choice header
    var_header_str = ('                                       Variable of\n'+
                      '                                       choice')
    ax.annotate(var_header_str, (1.00*xlim, header_y), xycoords='data')
    # formatting
    ax.xaxis.set_minor_locator(AutoMinorLocator(5))
    ax = ticks_in(ax)
    ax = ticks_sizes(ax, major={'L':10,'W':1.1}, minor={'L':4,'W':0.8})
    ax.set_yticks(yvals)
    ax.set_yticklabels(ylabels_all)
    # only want vertical grid lines
    ax.grid(axis='y')
    # ax.legend(loc='upper left', bbox_to_anchor=(1,1))
    ax.legend(loc='upper left')
    # save?
    if not savefile is None:
        fig.savefig(savefile+'.pdf')
        fig.savefig(savefile+'.png')
    return fig, ax

def run_plot_channel(channel, datacard_dict, version, CL, plot_stat_only, xlim_factor, fixed_xlim):
    output_dir_sch = os.path.join(datacard_dir, 'output', 'combined_datacards', 'subchannel')
    output_dir_ch = os.path.join(datacard_dir, 'output', 'combined_datacards', 'channel')
    plot_dir = os.path.join(datacard_dir, 'plots', 'combined_datacards', 'subchannel')
    root_file_dict_full = {}
    fname_ch = datacard_dict[channel]['info']['file_name']
    # construct root file for each subchannel
    for i, subch in enumerate(sorted(datacard_dict[channel]['subchannels'].keys())):
        fname_sch = datacard_dict[channel]['subchannels'][subch]['info']['file_name']
        bin_info = {'output_dir': output_dir_sch, 'plot_dir': plot_dir,
                    'channel': fname_ch, 'subchannel': subch,
                    'version': version, 'bin_': 'All',
                    }
        root_file_all = os.path.join(bin_info['output_dir'],
                                     f'higgsCombine_datacard1opWithBkg_FT0_bin{bin_info["bin_"]}_'+
                                     f'{bin_info["channel"]}_{bin_info["subchannel"]}_{bin_info["version"]}.MultiDimFit.mH120.root')
        root_file_stat = os.path.join(bin_info['output_dir'],
                                      f'higgsCombine_datacard1opWithBkg_FT0_bin{bin_info["bin_"]}_'+
                                      f'{bin_info["channel"]}_{bin_info["subchannel"]}_{bin_info["version"]}_nosyst.MultiDimFit.mH120.root')
        root_file_dict = {'total': root_file_all, 'stat_only': root_file_stat, 'bin_info': bin_info}
        root_file_dict_full[i] = {'root_file_dict': root_file_dict, 'ylabel': datacard_dict[channel]['subchannels'][subch]['info']['ylabel_name'],
                                  'variable_of_choice': datacard_dict[channel]['info']['variable_of_choice']}
    # construct root file for channel (combined)
    N = len(datacard_dict[channel]['subchannels'].keys())-1
    bin_info = {'output_dir': output_dir_ch, 'plot_dir': plot_dir,
                'channel': fname_ch, 'subchannel': 'All',
                'version': version, 'bin_': 'All',
                }
    root_file_all = os.path.join(bin_info['output_dir'],
                                 f'higgsCombine_datacard1opWithBkg_FT0_bin{bin_info["bin_"]}_'+
                                 f'{bin_info["channel"]}{bin_info["subchannel"]}_{bin_info["version"]}.MultiDimFit.mH120.root')
    root_file_stat = os.path.join(bin_info['output_dir'],
                                  f'higgsCombine_datacard1opWithBkg_FT0_bin{bin_info["bin_"]}_'+
                                  f'{bin_info["channel"]}{bin_info["subchannel"]}_{bin_info["version"]}_nosyst.MultiDimFit.mH120.root')
    root_file_dict = {'total': root_file_all, 'stat_only': root_file_stat, 'bin_info': bin_info}
    root_file_dict_full[N+1.25] = {'root_file_dict': root_file_dict, 'ylabel': 'combined',
                                   'variable_of_choice': datacard_dict[channel]['info']['variable_of_choice']}
    # plot
    if plot_stat_only:
        stat_str = '_w_stat_only'
    else:
        stat_str = ''
    plotfile = os.path.join(plot_dir, f'sensitivity_summary_channel-{channel}{stat_str}')
    title = f'{int(CL*100)}% CL Sensitivity: {channel}'
    fig, ax = make_limit_summary_plot(root_file_dict_full, title, CL=CL, add_hrule=True, plot_stat_only=plot_stat_only,
                                      xlim_factor=xlim_factor, fixed_xlim=fixed_xlim, savefile=plotfile)
    return fig, ax

def run_plot_analysis(datacard_dict, version, CL, plot_stat_only, xlim_factor, fixed_xlim):
    # output_dir_sch = os.path.join(datacard_dir, 'output', 'combined_datacards', 'subchannel')
    output_dir_ch = os.path.join(datacard_dir, 'output', 'combined_datacards', 'channel')
    output_dir_full = os.path.join(datacard_dir, 'output', 'combined_datacards', 'full_analysis')
    plot_dir = os.path.join(datacard_dir, 'plots', 'combined_datacards', 'channel')
    root_file_dict_full = {}
    # construct root file for each channel
    for i, ch in enumerate(sorted(datacard_dict.keys())):
        fname_ch = datacard_dict[ch]['info']['file_name']
        bin_info = {'output_dir': output_dir_ch, 'plot_dir': plot_dir,
                    'channel': fname_ch, 'subchannel': 'All',
                    'version': version, 'bin_': 'All',
                    }
        root_file_all = os.path.join(bin_info['output_dir'],
                                     f'higgsCombine_datacard1opWithBkg_FT0_bin{bin_info["bin_"]}_'+
                                     f'{bin_info["channel"]}{bin_info["subchannel"]}_{bin_info["version"]}.MultiDimFit.mH120.root')
        root_file_stat = os.path.join(bin_info['output_dir'],
                                      f'higgsCombine_datacard1opWithBkg_FT0_bin{bin_info["bin_"]}_'+
                                      f'{bin_info["channel"]}{bin_info["subchannel"]}_{bin_info["version"]}_nosyst.MultiDimFit.mH120.root')
        root_file_dict = {'total': root_file_all, 'stat_only': root_file_stat, 'bin_info': bin_info}
        root_file_dict_full[i] = {'root_file_dict': root_file_dict, 'ylabel': datacard_dict[ch]['info']['ylabel_name'],
                                  'variable_of_choice': datacard_dict[ch]['info']['variable_of_choice']}
    # construct root file for channel (combined)
    N = len(datacard_dict.keys())-1
    bin_info = {'output_dir': output_dir_full, 'plot_dir': plot_dir,
                'channel': 'All', 'subchannel': 'All',
                'version': version, 'bin_': 'All',
                }
    root_file_all = os.path.join(bin_info['output_dir'],
                                 f'higgsCombine_datacard1opWithBkg_FT0_bin{bin_info["bin_"]}_'+
                                 f'channels{bin_info["channel"]}_{bin_info["version"]}.MultiDimFit.mH120.root')
    root_file_stat = os.path.join(bin_info['output_dir'],
                                  f'higgsCombine_datacard1opWithBkg_FT0_bin{bin_info["bin_"]}_'+
                                  f'channels{bin_info["channel"]}_{bin_info["version"]}_nosyst.MultiDimFit.mH120.root')
    root_file_dict = {'total': root_file_all, 'stat_only': root_file_stat, 'bin_info': bin_info}
    root_file_dict_full[N+1.25] = {'root_file_dict': root_file_dict, 'ylabel': 'combined',
                                   'variable_of_choice': ''}
    # plot
    if plot_stat_only:
        stat_str = '_w_stat_only'
    else:
        stat_str = ''
    plotfile = os.path.join(plot_dir, f'sensitivity_summary_all-channels{stat_str}')
    title = f'{int(CL*100)}% CL Sensitivity: All Channels'
    fig, ax = make_limit_summary_plot(root_file_dict_full, title, CL=CL, add_hrule=True, plot_stat_only=plot_stat_only,
                                      xlim_factor=xlim_factor, fixed_xlim=fixed_xlim, savefile=plotfile)
    return fig, ax


if __name__=='__main__':
    # confidence level
    CL = 0.95
    VERSION = 'v1'
    # loop through all channels and plot
    print("=========================================================")
    print("Making sensitivity plots for each channel...")
    for pstat in [True, False]:
        print(f'Include stat-only? {pstat}')
        for ch in datacard_dict.keys():
            print(ch)
            # fig, ax = run_plot_channel(ch, datacard_dict, version=VERSION, CL=CL, plot_stat_only=pstat, xlim_factor=2.0, fixed_xlim=None)
            fig, ax = run_plot_channel(ch, datacard_dict, version=VERSION, CL=CL, plot_stat_only=pstat, xlim_factor=None, fixed_xlim=[-2., 2.])
    print("=========================================================\n")
    #####
    print("=========================================================")
    print("Making sensitivity plots for full analysis...")
    for pstat in [True, False]:
        print(f'Include stat-only? {pstat}')
        # fig, ax = run_plot_analysis(datacard_dict, version=VERSION, CL=CL, plot_stat_only=pstat, xlim_factor=2.0, fixed_xlim=None)
        fig, ax = run_plot_analysis(datacard_dict, version=VERSION, CL=CL, plot_stat_only=pstat, xlim_factor=None, fixed_xlim=[-2., 2.])
    print("=========================================================\n")

    # plt.show()
