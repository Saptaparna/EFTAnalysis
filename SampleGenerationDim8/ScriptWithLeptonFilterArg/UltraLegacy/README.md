1. update json file which contains the parameter of the scripts
    ```
    example:
    Config/WWW.json

2. generate run scripts:
    python Scripts.py --json Config/WWW.json

2. sh pr.sh

3. update submitJob.sh by hand
    1. only generate the submit file and excutable for debug
        bash submitCondorJob.sh {Npart} {Nqueue} 
    2. generate submit file and excutable, then submit condor jobs 
        bash submitCondorJob.sh {Npart} {Nqueue} run
    
4. merge root files
    1. haddNano.py from NanoAOD-tool 