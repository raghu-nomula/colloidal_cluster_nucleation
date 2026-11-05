# Convenience build for the Fortran programs.
#   make            build mc_npt and block, and put the executable where the campaign scripts expect it
#   make clean      remove compiled files
# If your compiler is not called gfortran:  make FC=ifort
FC ?= gfortran

.PHONY: all build clean

all: build

build:
	$(MAKE) -C simulations/Source FC=$(FC) F77=$(FC) LD=$(FC)
	$(MAKE) -C simulations/Block  FC=$(FC) F77=$(FC) LD=$(FC)
	cp simulations/Source/mc_npt simulations/4_Clean_NoSwap_Replication/common/mc_npt_phase1
	@echo
	@echo "Built simulations/Source/mc_npt and copied it to 4_Clean_NoSwap_Replication/common/mc_npt_phase1"
	@echo "(a rebuilt binary has a different SHA-256 from the one in the run manifests; see docs/REPRODUCE.md)"

clean:
	$(MAKE) -C simulations/Source clean || true
	$(MAKE) -C simulations/Block clean || true
	rm -f simulations/Source/*.o simulations/Block/*.o simulations/4_Clean_NoSwap_Replication/common/mc_npt_phase1
