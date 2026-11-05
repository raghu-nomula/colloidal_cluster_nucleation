      SUBROUTINE ENER(En, Vir, R2, Isign)
c  ---calculates Yukawa pair energy and pair virial
c     Isign = +1 for same charge, -1 for opposite charge

      IMPLICIT NONE
      INCLUDE 'potential.inc'

      DOUBLE PRECISION R2, R, En, Vir, sigma, pref
      INTEGER Isign

      sigma = SQRT(SIG2)

c     ---hard core: overlap forbidden
      IF (R2.LT.SIG2) THEN
         En = 1.D20
         Vir = 0.D0

c     ---Yukawa interaction
      ELSE IF (R2.LE.RC2) THEN
         R = SQRT(R2)
         pref = EXP(-KAPPA*(R-sigma))

         En = DBLE(Isign)*pref/(R/sigma)

c        Vir_pair = -r du/dr
         Vir = DBLE(Isign)*pref*sigma*(KAPPA + 1.D0/R)

c     ---beyond cutoff
      ELSE
         En = 0.D0
         Vir = 0.D0
      END IF

      RETURN
      END
