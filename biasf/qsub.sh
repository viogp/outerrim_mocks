#!/bin/bash

logpath=/mnt/lustre/gonzalev/Junk

path2code=/users/gonzalev/eboss/mock_construction/biasf/

code2run=write_input.py

space=rspace #zspace

xx=(0) #(0 1 2)
yy=(0) #(0 1 2)
zz=(0) #(0 1 2)

for ix in ${xx[@]} ; do
    for iy in ${yy[@]} ; do
	for iz in ${zz[@]} ; do
	    name=bias_${ix}${iy}${iz}
	    logname=${logpath}/${name}.%j.log

	    cat << EOF - run.sh | sbatch
#!/bin/bash
#
#SBATCH --nodes=1  
#SBATCH --ntasks=1
#SBATCH --time=0-9:00:00
#SBATCH -p sciama4.q
#SBATCH --job-name=${name}
#SBATCH -o ${logname}  
#SBATCH -D ${path2code}
#SBATCH --export=ix=${ix},iy=${iy},iz=${iz},space=${space},code2run=${code2run}
#
#
# Run script follows 
EOF

            #qsub run.sh -v space=$space,ix=$ix,iy=$iy,iz=$iz,code2run=$code2run
            ## Testing
            #qsub -I run.sh -v space=$space,ix=$ix,iy=$iy,iz=$iz,code2run=$code2run

	    sleep 5s
	done
    done
done

echo 'End of the script'
