# Replication notebook index

This directory is the written laboratory notebook for the clean no-swap
replication. Read these files in numerical order. Each phase record states the
purpose, source files, changes, commands, numerical results, interpretation,
limitations, and the decision that controls the next phase.

## Records

1. [Phase 1: instrumentation and two clean branches](PHASE_01_INSTRUMENTATION.md)
2. [Phase 2: independent liquid validation](PHASE_02_LIQUID_VALIDATION.md)
3. [Phase 3: volume tuning and medium-run gate](PHASE_03_VOLUME_TUNING.md)
4. [Phase 4: segmented production preparation](PHASE_04_PRODUCTION_PREPARATION.md)
5. [Phase 5: production execution guide](PHASE_05_EXECUTION_GUIDE.md)
6. [Engineering changes: what changed and why](CODE_AND_WORKFLOW_CHANGE_LOG.md)
7. [Configuration lineage](CONFIGURATION_LINEAGE.md)
8. [Parameter and decision register](DECISIONS.md)
9. [Known limitations](KNOWN_LIMITATIONS.md)
10. [Template for future phases](PHASE_TEMPLATE.md)

## Bookkeeping rule

No long simulation should begin until its input configuration, executable,
input parameters, seed, purpose, expected output and stopping condition are
recorded. No result should be promoted to the next phase until its validation
and limitations are written down.
