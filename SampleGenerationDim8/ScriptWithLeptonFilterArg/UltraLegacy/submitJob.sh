max=1

for i in `seq 1 $max`
do
    bash submitCondorJob.sh  $i 2
    # bash submitCondorJob.sh $i 2 run
done
