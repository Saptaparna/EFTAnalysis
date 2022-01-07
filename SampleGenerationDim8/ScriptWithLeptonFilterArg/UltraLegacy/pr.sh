voms-proxy-init --valid 192:00 -voms cms

dasgoclient -query="file dataset=/Neutrino_E-10_gun/RunIISummer20ULPrePremix-UL18_106X_upgrade2018_realistic_v11_L1v1-v2/PREMIX" > pileup_files.txt

cp /tmp/x509up_u100637 .

# test locally 
# sh Job_1.sh 1 100 200