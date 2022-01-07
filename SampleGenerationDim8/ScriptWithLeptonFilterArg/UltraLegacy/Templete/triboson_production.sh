#!/bin/bash

# A POSIX variable
OPTIND=1         # Reset in case getopts has been used previously in the shell.

# Initialize our own variables:
YEAR=2018
NTHREADS=1 #8 default

while getopts "h?y:s:n:o:a:l:b:dcp:f" opt; do
    case "$opt" in
    h|\?)
        echo 'triboson-production -y YEAR -s SAMPLE -n NEVENTS -o OUTPUT_DIR -p PILEUP_FILES [-d -c] -a NPART -l LEPTONFILTER 

If the -d (dry run) flag is set, only the environment and the config file will be created.
otherwise, the cmsRun command will be executed.

The -c flag enables the cleanup of temporary directories in the end, which is recommended for
large scale production to save space.

PILEUP_FILES needs to be a file in which the the pileup files are listed, separated by newlines.
You can get this list with the dasgoclient:
    dasgoclient -query="file dataset=/Neutrino_E-10_gun/RunIISummer17PrePremix-PUAutumn18_102X_upgrade2018_realistic_v15-v1/GEN-SIM-DIGI-RAW" > pileup_files.txt'
        exit 0
        ;;
    y)  YEAR=$OPTARG
        # e.g. 2016, 2017, 2018
        ;;
    s)  SAMPLE=$OPTARG
        # e.g. WWW_dim8, WZZ_dim8, WWZ_dim8 or ZZZ_dim8
        ;;
    p)  PILEUP_FILES=$OPTARG
        ;;
    d)  DRY_RUN=1
        # cleanup temporary files in the end, recommended for large scale production
        ;;
    c)  CLEANUP=1
        # Only setup but exit script before actually running cmsRun
        ;;
    o)  OUTPUT_DIR=$OPTARG
        # Output directory of this production
        ;;
    n)  NEVENTS=$OPTARG
        ;;
    a)  NPART=$OPTARG
        ;;
    l)  LEPTONFILTER=$OPTARG
        ;;
    b)  SEED=$OPTARG
        ;;
    f)  CopyToEos=1 # to copy the outfile to cmslpc eos space
        ;;
    esac
done

echo 'LEPTONFILTER='
echo ${LEPTONFILTER}

shift $((OPTIND-1))

if [ -z "$NEVENTS" ]
then
      echo "-n NEVENTS not specified!"
      exit 1
fi

if [ -f "$PILEUP_FILES" ]; then
    echo "$PILEUP_FILES exist"
else 
    echo "$PILEUP_FILES does not exist!"
    exit 1
fi

PILEUP_INPUT=$(shuf -n 2 $PILEUP_FILES | tr '\n' ',')
PILEUP_INPUT=${PILEUP_INPUT::-1}

if [[ "$PILEUP_INPUT" = *?.root ]]; then
    echo "Pileup input looks OK"
else
    echo "Something unexpected happened with the pileup input!"
    exit 1
fi

case "$YEAR" in

2016)  echo "The year $YEAR is not supported!"
    CONDITIONS=80X_mcRun2_asymptotic_2016_TrancheIV_v8
    BEAMSPOT=Realistic50ns13TeVCollision # yes, 50 ns is not correct but this is also used in official 2016 MC productions
    exit 1
    ;;
2017)  echo "The year $YEAR is not supported!"
    CONDITIONS=94X_mc2017_realistic_v17
    BEAMSPOT=Realistic25ns13TeVEarly2017Collision
    exit 1
    ;;
2018)  echo "The year is $YEAR"
    CAMPAIGN=RunIISummer20UL18
    ERA=Run2_2018
    NANOERA=Run2_2018,run2_nanoAOD_106Xv2
    CONDITIONS=106X_upgrade2018_realistic_v4
    CONDITIONS_SIM=106X_upgrade2018_realistic_v11_L1v1
    CONDITIONS_HLT=102X_upgrade2018_realistic_v15
    CONDITIONS_MINIAOD=106X_upgrade2018_realistic_v16_L1v1
    BEAMSPOT=Realistic25ns13TeVEarly2018Collision
    HLTSTEP=2018v32
    ;;
*) echo "Year $YEAR is not valid, did you forget to specify it with the -y option?"
   exit 1
   ;;
esac

if [ "$DRY_RUN" ]
then
      echo "Script will be exited after config file is generated"
else
      echo "The full script will be run, including the cmsRun command and cleaning on the directory"
      if [ "$CLEANUP" ]
      then
            echo "Temporary files and directories will be cleaned up after script is finished"
      else
            echo "No files and directories will be cleaned up in the end,"
            echo "which is not recommended for large scale production (consider setting the -c flag)."
      fi
fi



# The following part should not be manually configured
FRAGMENT_BASE_URL=http://nuhep.northwestern.edu/~sapta/LeptonFilter
GRIDPACK_BASE_URL=GRIDPACK_BASE_URL_REPLACE

FRAGMENT=wmLHEGS-fragment-${YEAR}_${LEPTONFILTER}.py
GRIDPACK=GRIDPACK_REPLACE

STEP0_NAME=${SAMPLE}-${CAMPAIGN}wmLHEGEN_${NPART}
STEP1_NAME=${SAMPLE}-${CAMPAIGN}SIM_${NPART}
STEP2_NAME=${SAMPLE}-${CAMPAIGN}DIGIPremix_${NPART}
STEP3_NAME=${SAMPLE}-${CAMPAIGN}HLT_${NPART}
STEP4_NAME=${SAMPLE}-${CAMPAIGN}RECO_${NPART}
STEP5_NAME=${SAMPLE}-${CAMPAIGN}MiniAODv2_${NPART}
STEP6_NAME=${SAMPLE}-${CAMPAIGN}NanoAODv9_${NPART}

curl -s --insecure https://test-qiguo.web.cern.ch/test-qiguo/VVV/Sample_Production/LHEReweight/CMSSW_10_6_26_PhysicsTools_NanoAOD_plugins.patch --retry 2 --create-dirs -o CMSSW_10_6_26_PhysicsTools_NanoAOD_plugins.patch
if [ -s CMSSW_10_6_26_PhysicsTools_NanoAOD_plugins.patch ]
then
  echo "get CMSSW_10_6_26_PhysicsTools_NanoAOD_plugins.patch"
else
  echo "can not get CMSSW_10_6_26_PhysicsTools_NanoAOD_plugins.patch"
  exit $?;
fi

curl -s --insecure $GRIDPACK_BASE_URL/$GRIDPACK --retry 2 --create-dirs -o $GRIDPACK
if [ -s $GRIDPACK ]
then
  echo "get $GRIDPACK"
else
  echo "can not get $GRIDPACK_BASE_URL/$GRIDPACK"
  echo "curl -s --insecure $GRIDPACK_BASE_URL/$GRIDPACK --retry 2 --create-dirs -o $GRIDPACK"
  exit $?;
fi

# ============= GEN,LHE ==============
# ============= GEN,LHE ==============
export SCRAM_ARCH=slc7_amd64_gcc700

source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_10_6_19_patch3/src ] ; then
  echo release CMSSW_10_6_19_patch3 already exists
else
  scram p CMSSW CMSSW_10_6_19_patch3
fi
cd CMSSW_10_6_19_patch3/src
eval `scram runtime -sh`

curl -s --insecure $FRAGMENT_BASE_URL/$FRAGMENT --retry 2 --create-dirs -o Configuration/GenProduction/python/$FRAGMENT
if [ -s Configuration/GenProduction/python/$FRAGMENT ]
then
  echo "get $FRAGMENT"
else
  echo "can not get $FRAGMENT"
  exit $?;
fi

scram b -j8
cd ../../

#insert gridpack path info fragment
PWDESC=$(echo $PWD | sed 's_/_\\/_g')
sed -i "s/\$GRIDPACK/$PWDESC\/$GRIDPACK/g" $CMSSW_VERSION/src/Configuration/GenProduction/python/$FRAGMENT



seed=$SEED

cmsDriver.py Configuration/GenProduction/python/$FRAGMENT \
    --python_filename ${STEP0_NAME}_cfg.py \
    --fileout file:${STEP0_NAME}.root \
    --mc \
    --eventcontent RAWSIM,LHE \
    --datatier GEN,LHE \
    --conditions $CONDITIONS \
    --beamspot $BEAMSPOT \
    --step LHE,GEN \
    --geometry DB:Extended \
    --nThreads $NTHREADS \
    --era $ERA \
    --no_exec \
    --customise Configuration/DataProcessing/Utils.addMonitoring \
    --customise_commands process.RandomNumberGeneratorService.externalLHEProducer.initialSeed="int(${seed})" \
    -n $NEVENTS

cmsRun ${STEP0_NAME}_cfg.py
# ============= GEN,LHE ==============
# ============= GEN,LHE ==============

# ============= SIM ==============
# ============= SIM ==============

export SCRAM_ARCH=slc7_amd64_gcc700

source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_10_6_17_patch1/src ] ; then
  echo release CMSSW_10_6_17_patch1 already exists
else
  scram p CMSSW CMSSW_10_6_17_patch1
fi
cd CMSSW_10_6_17_patch1/src
eval `scram runtime -sh`

scram b -j4
cd ../..

cmsDriver.py \
  --python_filename ${STEP1_NAME}_cfg.py \
  --eventcontent RAWSIM \
  --customise Configuration/DataProcessing/Utils.addMonitoring \
  --datatier GEN-SIM \
  --fileout file:${STEP1_NAME}.root \
  --conditions $CONDITIONS_SIM \
  --beamspot $BEAMSPOT \
  --step SIM \
  --geometry DB:Extended \
  --filein file:${STEP0_NAME}.root \
  --era $ERA \
  --runUnscheduled \
  --no_exec \
  --mc \
  -n $NEVENTS

cmsRun ${STEP1_NAME}_cfg.py
# ============= SIM ==============
# ============= SIM ==============

# ============= DIGI,DATAMIX,L1,DIGI2RAW ==============
# ============= DIGI,DATAMIX,L1,DIGI2RAW ==============

export SCRAM_ARCH=slc7_amd64_gcc700

source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_10_6_17_patch1/src ] ; then
  echo release CMSSW_10_6_17_patch1 already exists
else
  scram p CMSSW CMSSW_10_6_17_patch1
fi
cd CMSSW_10_6_17_patch1/src
eval `scram runtime -sh`

scram b -j4
cd ../..


cmsDriver.py  \
    --python_filename ${STEP2_NAME}_cfg.py \
    --eventcontent PREMIXRAW \
    --customise Configuration/DataProcessing/Utils.addMonitoring \
    --datatier GEN-SIM-DIGI \
    --fileout file:${STEP2_NAME}.root \
    --pileup_input "$PILEUP_INPUT" \
    --conditions $CONDITIONS_SIM \
    --step DIGI,DATAMIX,L1,DIGI2RAW \
    --procModifiers premix_stage2 \
    --geometry DB:Extended \
    --filein file:${STEP1_NAME}.root \
    --datamix PreMix \
    --era $ERA \
    --runUnscheduled \
    --no_exec \
    --mc \
    -n $NEVENTS

cmsRun ${STEP2_NAME}_cfg.py
# ============= DIGI,DATAMIX,L1,DIGI2RAW ==============
# ============= DIGI,DATAMIX,L1,DIGI2RAW ==============

# ============= HLT ==============
# ============= HLT ==============

export SCRAM_ARCH=slc7_amd64_gcc700

source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_10_2_16_UL/src ] ; then
  echo release CMSSW_10_2_16_UL already exists
else
  scram p CMSSW CMSSW_10_2_16_UL
fi
cd CMSSW_10_2_16_UL/src
eval `scram runtime -sh`

scram b -j4
cd ../..

cmsDriver.py  \
  --python_filename ${STEP3_NAME}_cfg.py \
  --eventcontent RAWSIM \
  --customise Configuration/DataProcessing/Utils.addMonitoring \
  --datatier GEN-SIM-RAW \
  --fileout file:${STEP3_NAME}.root \
  --conditions $CONDITIONS_HLT \
  --customise_commands 'process.source.bypassVersionCheck = cms.untracked.bool(True)' \
  --step HLT:$HLTSTEP \
  --geometry DB:Extended \
  --filein file:${STEP2_NAME}.root \
  --era $ERA \
  --no_exec \
  --mc \
  -n $NEVENTS

cmsRun ${STEP3_NAME}_cfg.py
# ============= HLT ==============
# ============= HLT ==============

# ============= AODSIM ==============
# ============= AODSIM ==============

export SCRAM_ARCH=slc7_amd64_gcc700

source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_10_6_17_patch1/src ] ; then
  echo release CMSSW_10_6_17_patch1 already exists
else
  scram p CMSSW CMSSW_10_6_17_patch1
fi
cd CMSSW_10_6_17_patch1/src
eval `scram runtime -sh`

scram b -j4
cd ../..

cmsDriver.py  \
  --python_filename ${STEP4_NAME}_cfg.py \
  --eventcontent AODSIM \
  --customise Configuration/DataProcessing/Utils.addMonitoring \
  --datatier AODSIM \
  --fileout file:${STEP4_NAME}.root \
  --conditions $CONDITIONS_SIM \
  --step RAW2DIGI,L1Reco,RECO,RECOSIM,EI \
  --geometry DB:Extended \
  --filein file:${STEP3_NAME}.root \
  --era $ERA \
  --runUnscheduled \
  --no_exec \
  --mc \
  -n $NEVENTS

cmsRun ${STEP4_NAME}_cfg.py
# ============= AODSIM ==============
# ============= AODSIM ==============

# ============= MINIAODSIM ==============
# ============= MINIAODSIM ==============

export SCRAM_ARCH=slc7_amd64_gcc700

source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_10_6_20/src ] ; then
  echo release CMSSW_10_6_20 already exists
else
  scram p CMSSW CMSSW_10_6_20
fi
cd CMSSW_10_6_20/src
eval `scram runtime -sh`

scram b -j4
cd ../..

cmsDriver.py  \
  --python_filename ${STEP5_NAME}_cfg.py \
  --eventcontent MINIAODSIM \
  --customise Configuration/DataProcessing/Utils.addMonitoring \
  --datatier MINIAODSIM \
  --fileout file:${STEP5_NAME}.root \
  --conditions $CONDITIONS_MINIAOD \
  --step PAT \
  --procModifiers run2_miniAOD_UL \
  --geometry DB:Extended \
  --filein file:${STEP4_NAME}.root \
  --era $ERA \
  --runUnscheduled \
  --no_exec \
  --mc \
  -n $NEVENTS

cmsRun ${STEP5_NAME}_cfg.py
# ============= MINIAODSIM ==============
# ============= MINIAODSIM ==============

# ============= NANOAODSIM ==============
# ============= NANOAODSIM ==============

export SCRAM_ARCH=slc7_amd64_gcc700

source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_10_6_26/src ] ; then
  echo release CMSSW_10_6_26 already exists
else
  scram p CMSSW CMSSW_10_6_26
fi
cd CMSSW_10_6_26/src
eval `scram runtime -sh`

git cms-init --upstream-only
git cms-addpkg PhysicsTools/NanoAOD

cp ../../CMSSW_10_6_26_PhysicsTools_NanoAOD_plugins.patch .

patch PhysicsTools/NanoAOD/plugins/GenWeightsTableProducer.cc < CMSSW_10_6_26_PhysicsTools_NanoAOD_plugins.patch

scram b -j4
cd ../..

cmsDriver.py  \
    --python_filename ${STEP6_NAME}_cfg.py \
    --eventcontent NANOAODSIM \
    --customise Configuration/DataProcessing/Utils.addMonitoring \
    --datatier NANOAODSIM \
    --fileout file:${STEP6_NAME}.root \
    --conditions $CONDITIONS_MINIAOD \
    --step NANO \
    --filein file:${STEP5_NAME}.root \
    --era $NANOERA \
    --no_exec \
    --mc \
    -n $NEVENTS

cmsRun ${STEP6_NAME}_cfg.py
# ============= NANOAODSIM ==============
# ============= NANOAODSIM ==============


# Validate the config files
python2 ${STEP0_NAME}_cfg.py
python2 ${STEP1_NAME}_cfg.py
python2 ${STEP2_NAME}_cfg.py
python2 ${STEP3_NAME}_cfg.py
python2 ${STEP4_NAME}_cfg.py
python2 ${STEP5_NAME}_cfg.py
python2 ${STEP6_NAME}_cfg.py

if [ "$DRY_RUN" ]
then
      exit 1
fi

## copy file
if [ "$CopyToEos" ]
then
xrdcp -r -f ${STEP5_NAME}.root root://cmseos.fnal.gov//store/user/
xrdcp -r -f ${STEP6_NAME}.root root://cmseos.fnal.gov//store/user/
fi

## cleanup temporary working directories
if [ "$CLEANUP" ]
then
    # The full event after the premixig before recuding it to AOD is too large and too easy to recalculate to justify saving it
    rm ${STEP0_NAME}.root
    rm ${STEP1_NAME}.root
    rm ${STEP2_NAME}.root
    rm ${STEP3_NAME}.root
    rm ${STEP4_NAME}.root

    rm -rf rm -rf CMSSW_*
    rm -rf *_cfg.py
fi
