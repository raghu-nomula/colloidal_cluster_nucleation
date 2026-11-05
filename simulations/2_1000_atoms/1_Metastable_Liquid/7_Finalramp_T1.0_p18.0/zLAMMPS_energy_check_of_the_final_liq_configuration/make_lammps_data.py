#!/usr/bin/env python3
"""Create LAMMPS atomic data files from the final MC-NPT configurations."""

from math import sqrt
from pathlib import Path


HERE = Path(__file__).resolve().parent
RUN = HERE.parent


def write_data(path, box, atoms, comment):
    with path.open("w") as handle:
        handle.write(f"{comment}\n\n")
        handle.write(f"{len(atoms)} atoms\n2 atom types\n\n")
        handle.write(f"0.0 {box:.16g} xlo xhi\n")
        handle.write(f"0.0 {box:.16g} ylo yhi\n")
        handle.write(f"0.0 {box:.16g} zlo zhi\n\n")
        handle.write("Masses\n\n1 1.0\n2 1.0\n\nAtoms # atomic\n\n")
        for atom_id, atom_type, x, y, z in atoms:
            handle.write(f"{atom_id} {atom_type} {x:.16g} {y:.16g} {z:.16g}\n")


def validate_configuration(label, box, atoms, sigma=1.0):
    """Prove that plain LAMMPS Yukawa is sufficient for this run-0 test."""
    counts = {1: 0, 2: 0}
    minimum = float("inf")
    minimum_pair = None
    for i, atom_i in enumerate(atoms[:-1]):
        id_i, type_i, x_i, y_i, z_i = atom_i
        counts[type_i] = counts.get(type_i, 0) + 1
        for atom_j in atoms[i + 1:]:
            id_j, _, x_j, y_j, z_j = atom_j
            displacement = []
            for delta in (x_i - x_j, y_i - y_j, z_i - z_j):
                displacement.append(delta - box * round(delta / box))
            distance = sqrt(sum(delta * delta for delta in displacement))
            if distance < minimum:
                minimum = distance
                minimum_pair = (id_i, id_j)
    counts[atoms[-1][1]] = counts.get(atoms[-1][1], 0) + 1
    if counts != {1: 500, 2: 500}:
        raise ValueError(f"{label}: expected 500 atoms of each type; found {counts}")
    if minimum < sigma:
        raise ValueError(
            f"{label}: hard-core overlap for pair {minimum_pair}: "
            f"r_min={minimum:.16g} < sigma={sigma}"
        )
    print(
        f"{label}: type counts {counts}; minimum-image r_min={minimum:.12f} "
        f"for pair {minimum_pair} (no hard-core overlap)"
    )


def read_restart(path):
    lines = path.read_text().splitlines()
    box = float(lines[0].split()[0])
    count = int(lines[1])
    atoms = []
    for atom_id, line in enumerate(lines[3:3 + count], 1):
        x, y, z, atom_type = line.split()
        atoms.append((atom_id, int(atom_type), float(x), float(y), float(z)))
    if len(atoms) != count:
        raise ValueError(f"Expected {count} restart atoms, found {len(atoms)}")
    return box, atoms


def read_last_dump_frame(path):
    lines = path.read_text().splitlines()
    starts = [i for i, line in enumerate(lines) if line == "ITEM: TIMESTEP"]
    start = starts[-1]
    count = int(lines[start + 3])
    bounds = [tuple(map(float, lines[start + 5 + i].split())) for i in range(3)]
    lengths = [hi - lo for lo, hi in bounds]
    if max(lengths) - min(lengths) > 1e-10:
        raise ValueError("Expected a cubic box")
    atoms = []
    for line in lines[start + 9:start + 9 + count]:
        atom_id, atom_type, x, y, z = line.split()
        atoms.append((int(atom_id), int(atom_type), float(x), float(y), float(z)))
    if len(atoms) != count:
        raise ValueError(f"Expected {count} dump atoms, found {len(atoms)}")
    atoms.sort()
    return lengths[0], atoms


restart_box, restart_atoms = read_restart(RUN / "final_config.res")
dump_box, dump_atoms = read_last_dump_frame(RUN / "traj.lammpstrj")

validate_configuration("Full-precision restart", restart_box, restart_atoms)
validate_configuration("Rounded final dump frame", dump_box, dump_atoms)

write_data(
    HERE / "from_final_restart.data",
    restart_box,
    restart_atoms,
    "Full-precision final MC-NPT restart configuration",
)
write_data(
    HERE / "from_last_dump_frame.data",
    dump_box,
    dump_atoms,
    "Last MC-NPT trajectory frame (rounded text coordinates)",
)

print(f"Wrote {len(restart_atoms)} atoms; restart box = {restart_box:.16g}")
print(f"Wrote {len(dump_atoms)} atoms; dump box = {dump_box:.16g}")
