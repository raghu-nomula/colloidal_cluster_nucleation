# Path changes made in this repository (copies only)

The original run folders on Raghu's PC were not edited. In this repository the following scripts were changed so that they work from any location:

- Run scripts that had `ROOT="/home/raghu/.../2_MC_NPT_Yukawa_potential"` now find `ROOT` themselves: they walk up from the script's folder until they reach the folder that contains `Source/` (that is `simulations/`).
- `4_Clean_NoSwap_Replication/analyze_both_when_complete.sh`: the Python path of Raghu's conda environment is replaced by `${PYTHON:-python3}`.

Files changed:

- `simulations/2_1000_atoms/1_Metastable_Liquid/1_Ramp_T2_rho0.5_p5/run.sh`
- `simulations/2_1000_atoms/1_Metastable_Liquid/2_Ramp_T2_p10/run.sh`
- `simulations/2_1000_atoms/1_Metastable_Liquid/3_Ramp_T2_p15/run.sh`
- `simulations/2_1000_atoms/1_Metastable_Liquid/4_Ramp_T2_p18/run.sh`
- `simulations/2_1000_atoms/1_Metastable_Liquid/5_Ramp_T1.5_p18/run.sh`
- `simulations/2_1000_atoms/1_Metastable_Liquid/6_Ramp_T1.2_p18/run.sh`
- `simulations/2_1000_atoms/1_Metastable_Liquid/7_Finalramp_T1.0_p18.0/run.sh`
- `simulations/2_1000_atoms/2_Actual_KMC_for_nucleation/1_step_50K/run.sh`
- `simulations/2_1000_atoms/2_Actual_KMC_for_nucleation/2_step_50K_to_500K/run.sh`
- `simulations/2_1000_atoms/2_Actual_KMC_for_nucleation/3_step_500K_to_15000K/run.sh`
- `simulations/2_1000_atoms/2_Actual_KMC_for_nucleation/4_step_1.5M_to_3.5M/run.sh`
- `simulations/2_1000_atoms/2_Actual_KMC_for_nucleation/zLiquid_Check/run.sh`
- `simulations/3_Tests_for_codes/1_test_q6_py_code/run.sh`
- `simulations/3_Tests_for_codes/2_test_high_press/run.sh`
- `simulations/4_Clean_NoSwap_Replication/analyze_both_when_complete.sh`
