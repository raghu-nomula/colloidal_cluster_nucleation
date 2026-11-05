#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

# Regenerate and validate when the original MC files accompany this folder.
# Otherwise use the already generated, portable LAMMPS data files.
if [[ -f ../final_config.res && -f ../traj.lammpstrj ]]; then
    python3 make_lammps_data.py
else
    echo "Original MC files not present; using the pre-generated data files."
    [[ -f from_final_restart.data && -f from_last_dump_frame.data ]] || {
        echo "ERROR: LAMMPS data files are missing." >&2
        exit 1
    }
fi

if command -v lmp >/dev/null 2>&1; then
    lammps=lmp
elif command -v lmp_mpi >/dev/null 2>&1; then
    lammps=lmp_mpi
elif command -v lammps >/dev/null 2>&1; then
    lammps=lammps
else
    echo "LAMMPS executable not found (tried lmp, lmp_mpi, and lammps)." >&2
    exit 127
fi

"$lammps" -in in.restart -log log.restart
"$lammps" -in in.dump -log log.dump
