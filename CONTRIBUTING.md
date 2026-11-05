# How to suggest changes

Thank you for looking at this project. The repository owner reviews every change; nothing reaches the
`main` branch without being merged by the owner.

## The short version

1. **Fork** the repository (button at the top right of the GitHub page) or, if you have no fork access, ask the
   owner for access.
2. **Create a branch** with a descriptive name, e.g. `analysis-gofr-comparison` or `docs-fix-typo`.
3. Make your change, run the checks below, and **commit** with a clear message.
4. **Open a pull request** to `main`. Fill in the template: what changed, why, how you checked it.
5. The owner reviews, may ask questions or request changes, then approves and merges.

For a question, an idea, or something you found confusing, open an **Issue** instead (templates provided).

## What is welcome

* Corrections and clarifications in the documentation (`docs/`, READMEs).
* New analysis scripts in `analysis/` (with a short header comment: what it does, what it needs).
* Reproduction attempts: new runs in a **new, clearly named folder**, with inputs and manifest.
* Answers to the open questions in [docs/NEXT_STEPS.md](docs/NEXT_STEPS.md).

## Rules that protect the record

* **Do not edit or delete existing run folders** under `simulations/` (they are the record of what was run).
  Add a new folder instead and describe it in the pull request.
* **Do not commit large files.** No `*.lammpstrj` trajectories, no executables, no files above 5 MB. Summaries
  (CSV, small figures) are fine. Tell the owner if a large file should be shared; see [docs/DATA.md](docs/DATA.md).
* **No copyrighted material**: no paper PDFs, no book code, no credentials or personal data.
* **Use relative paths** in scripts (never `/home/yourname/...`).
* **State the cluster definition** whenever you quote a cluster size (q6 bond-order as in the paper, or CNA/PTM
  fcc + hcp). The numbers differ; see [docs/reports/04_cluster_size_comparison.pdf](docs/reports/04_cluster_size_comparison.pdf).
* Keep numbers traceable: give the run folder, frame and cumulative cycle count.

## Checks before opening a pull request

```bash
python analysis/analyze_example_frames.py     # still prints the expected table (docs/REPRODUCE.md)
git status                                    # no trajectories, binaries or stray files
```

If you changed a script, say how you tested it. If you changed text, check that links still work.
