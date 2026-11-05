# Phase 2 structural validation

`validate_structure.py` deliberately avoids q6. It validates restart geometry,
composition, hard-core overlaps, neighbor statistics, charge mixing, total and
partial RDFs, and low-index reciprocal-space density peaks. It also writes a
single-frame LAMMPS trajectory for independent OVITO PTM/CNA inspection.

The reciprocal-space peak is a warning diagnostic, not by itself a crystal
classifier. Final liquid/crystal classification should compare RDF evidence
with OVITO Polyhedral Template Matching and Common Neighbor Analysis.

`ovito_structure.py` performs those two independent OVITO classifications.
Use the `matsci` Conda environment, which contains NumPy, ASE and OVITO:

```bash
conda run -n matsci python analysis/ovito_structure.py INPUT \
  --output-dir OUTPUT
```
