# Known limitations and cautions

1. The Fortran `p_continuous` pressure omits the hard-core contact term. It is
   retained only as a continuous-force diagnostic.
2. The paper does not state the brute-force `p*=18` displacement size. The two
   `dr` branches are therefore a controlled comparison, not two equally direct
   claims of exact dynamical replication.
3. Raw MC cycles from different `dr` values are not equal physical time.
4. PTM and CNA can miss very small or strongly distorted embryos. Their absence
   is strong evidence for a liquid parent but not a mathematical proof that no
   local ordering exists.
5. The low-index structure-factor scan is a warning metric, not a complete
   classifier.
6. The current scripts reset cycle numbering inside each executable segment.
   Manifests preserve segment lengths, but a combined cumulative trajectory
   tool is still needed before multi-segment production analysis.
7. Fortran attempt counters are default integers. Long jobs should be divided
   into restartable segments to avoid approaching 32-bit integer overflow.
8. `nohup` survives terminal closure on a normal Linux session, but the CPU
   cannot compute while the machine is suspended.
9. The Codex command sandbox may reap detached processes when its tool session
   exits; supervised commands are used for short tests here.

