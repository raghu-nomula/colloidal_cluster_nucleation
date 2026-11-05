# Configuration lineage

This record prevents ambiguity about which output became which input.

```text
Original ramped p*=18 liquid
  2_1000_atoms/2_Actual_KMC_for_nucleation/
  metastable_liquid_N1000_T1_P18.res
  SHA256 c6264c653ea21f6ec507875f71bbbc28fe6cb4bd9730a0bfe63a9cb752b3fd31
        |
        +-- original 50k -> 450k continuation history
        |                    |
        |                    +-- old 500k endpoint
        |                        500K_final_config.res
        |                        SHA256 7e406f2b61fc128cf919327341723516e88824c44104a88e84fb0d4fc09c00a0
        |                              |
        |                              +-- copied unchanged to
        |                                  common/validated_parent_N1000_T1_P18.res
        |                                  (future production parent)
        |
        +-- Phase 1 pilot, dr=0.01, 200 cycles
        |     validation output only; not propagated
        |
        +-- Phase 1 pilot, dr=0.04, 200 cycles
              validation output only; not propagated

common/validated_parent_N1000_T1_P18.res
        |
        +-- Phase 2 validated pilot, dr=0.01, 200 cycles
        |     validation output only; not propagated
        |
        +-- Phase 2 validated pilot, dr=0.04, 200 cycles
              validation output only; not propagated
```

The important rule is that both future branches return to the identical
validated parent. Neither branch starts from the final configuration of the
other branch or from a 200-cycle validation output.
