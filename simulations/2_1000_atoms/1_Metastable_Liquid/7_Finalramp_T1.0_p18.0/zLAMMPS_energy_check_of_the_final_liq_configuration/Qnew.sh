#!/bin/bash -l

#############################
# example for an MP job
#############################

#SBATCH --job-name=example
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=20
##SBATCH --exclusive
#SBATCH --time=00:15:00
#SBATCH --partition=porelab

# You may not place bash commands before the last SBATCH directive

# Make sure module command is available
source /etc/profile

# Load the cluster-installed LAMMPS that has MANYBODY/eam/alloy
module purge
module load eb/D12 GCC/12.3.0 OpenMPI/4.1.5
module load LAMMPS/29Aug2024_update2-kokkos

# Use the LAMMPS from the loaded module
lmp=$(which lmp)

echo "Using LAMMPS binary:"
echo "$lmp"

echo "Checking EAM support:"
$lmp -h | grep -i "eam/alloy"

# Set OpenMP threads
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}

echo "OMP_NUM_THREADS = $OMP_NUM_THREADS"

# Make folders again safely, in case they do not exist
# Run LAMMPS
#srun "$lmp" -in in.restart
srun "$lmp" -in   in.dump



