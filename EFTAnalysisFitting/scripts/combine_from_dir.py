import os
import subprocess
import argparse


if __name__=='__main__':
    # file globals
    datacard_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                '..')
    output_base = 'output'
    output_dir = os.path.join(datacard_dir, output_base)
    # make paths absolute
    datacard_dir = os.path.abspath(datacard_dir)
    output_dir = os.path.abspath(output_dir)
    # parse commmand line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--Directory',
                        help=f'Which datacard subdirectory? Assumes starting point is {datacard_dir}. e.g. "combined_datacards/full_analysis" (default)')
    parser.add_argument('-a', '--Asimov', help='Use Asimov? "y"(default)/"n".')
    parser.add_argument('-p', '--Precision', help='What is desired precision / step size? e.g. "0.001" (default)')
    parser.add_argument('-pc', '--PrecisionCoarse', help='What is desired precision / step size when POI range > 10? e.g. "0.01" (default)')
    parser.add_argument('-V', '--Verbose', help='Include "combine" output? 0 (default) / 1. "combine" output only included if Verbose>0.')
    args = parser.parse_args()
    # fill defauls if necessary
    if args.Directory is None:
        args.Directory = 'combined_datacards/full_analysis'
    if args.Asimov is None:
        args.Asimov = 'y'
    if args.Asimov == 'y':
        asi_str = '-t -1'
    else:
        asi_str = ''
    if args.Precision is None:
        args.Precision = 0.001
    else:
        args.Precision = float(args.Precision)
    if args.PrecisionCoarse is None:
        args.PrecisionCoarse = 0.01
    else:
        args.PrecisionCoarse = float(args.PrecisionCoarse)
    if args.Verbose is None:
        args.Verbose = 0
    else:
        args.Verbose = int(args.Verbose)
    if args.Verbose > 0:
        stdout = None
    else:
        stdout = subprocess.PIPE
    # update output directory
    output_dir = os.path.join(output_dir, args.Directory)
    # find all files in directory
    dc_dir = os.path.join(datacard_dir, args.Directory)
    dc_base_list = os.listdir(dc_dir)
    # loop through files
    for dc_base in dc_base_list:
        # go to card directory
        os.chdir(dc_dir)
        # construct file names
        cardfile_base = dc_base.replace('.txt', '')
        cardfile = os.path.join(dc_dir, dc_base)
        workspacefile = os.path.join(output_dir,'workspace_'+cardfile_base+f'.root')
        print("=========================================================")
        print(f"Attempting to read the following datacard: {cardfile}")
        # make workspace
        print('Generating workspace')
        _ = subprocess.run(f'text2workspace.py {cardfile} -P HiggsAnalysis.AnalyticAnomalousCoupling.AnomalousCouplingEFTNegative:analiticAnomalousCouplingEFTNegative -o {workspacefile} --X-allow-no-signal --PO eftOperators=cG', shell=True, stdout=stdout)
        # run combine
        os.chdir(output_dir)
        print(f'Running combine from output directory: {output_dir}')
        # first find appropriate range:
        print('Determining appropriate POI range and steps:')
        # first run combine using a coarse scan
        # FIXME! Allow changing range or original step size
        _ = subprocess.run(f'combine -M MultiDimFit {workspacefile} --algo=grid --points 201 --alignEdges 1 {asi_str} --redefineSignalPOIs k_cG --freezeParameters r --setParameters r=1 --setParameterRanges k_cG=-50,50 --verbose -1 -n _{cardfile_base}_coarse', stdout=stdout, shell=True)
        # assuming for now we always want a 95% CL, so threshold always 4.
        # FIXME! Add this as a flag in argparse.
        rangescript = os.path.join(datacard_dir, 'scripts', 'find_POI_range.py')
        proc = subprocess.run(f'python {rangescript} -f {output_dir}/higgsCombine_{cardfile_base}_coarse.MultiDimFit.mH120.root -T 4.0 -s {args.Precision} -sc {args.PrecisionCoarse}', shell=True, stdout=subprocess.PIPE)
        # parse results
        poi_dict = {i.split(':')[0]:float(i.split(':')[1]) for i in proc.stdout.decode().strip('\n').split(';')}
        poi_dict['steps'] = int(poi_dict['steps'])
        print(f'LL: {poi_dict["LL"]}; UL: {poi_dict["UL"]}; steps: {poi_dict["steps"]}')
        range_ = poi_dict["UL"] - poi_dict["LL"]
        if range_ > 10:
            prec = args.PrecisionCoarse
        else:
            prec = args.Precision
        print(f'LL + (steps-1) * {prec} = {poi_dict["LL"] + (poi_dict["steps"]-1) * prec}')
        # run combine using appropriate range and steps
        print('Running combine with appropriate range & steps:')
        print('With systematics:')
        _ = subprocess.run(f'combine -M MultiDimFit {workspacefile} --algo=grid --points {poi_dict["steps"]} --alignEdges 1 {asi_str} --redefineSignalPOIs k_cG --freezeNuisanceGroups nosyst --freezeParameters r --setParameters r=1 --setParameterRanges k_cG={poi_dict["LL"]},{poi_dict["UL"]} --verbose -1 -n _{cardfile_base}', stdout=stdout, shell=True)
        print(f'Finished running combine. Expected file output: higgsCombine_{cardfile_base}.MultiDimFit.mH120.root')
        print('Without systematics:')
        _ = subprocess.run(f'combine -M MultiDimFit {workspacefile} --algo=grid --points {poi_dict["steps"]} --alignEdges 1 {asi_str} --redefineSignalPOIs k_cG --freezeNuisanceGroups allsyst --freezeParameters r --setParameters r=1 --setParameterRanges k_cG={poi_dict["LL"]},{poi_dict["UL"]} --verbose -1 -n _{cardfile_base}_nosyst', stdout=stdout, shell=True)
        print(f'Finished running combine. Expected file output: higgsCombine_{cardfile_base}_nosyst.MultiDimFit.mH120.root')
        print("=========================================================\n")
