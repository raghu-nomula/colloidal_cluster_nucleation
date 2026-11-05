      SUBROUTINE MCVOL(En, Vir, Attempt, Acc, Vmax, Iseed)
c     attempts to change the volume using full energy recalculation
      IMPLICIT NONE
      INCLUDE 'parameter.inc'
      INCLUDE 'conf.inc'
      INCLUDE 'potential.inc'
      INCLUDE 'system.inc'
      INCLUDE 'npt.inc'

      DOUBLE PRECISION enn, En, RANF, Vir, virn
      DOUBLE PRECISION boxn, vo, vn, lnvn, Vmax, f, arg
      DOUBLE PRECISION boxo, hboxo
      INTEGER Attempt, Acc, i, Iseed

      Attempt = Attempt + 1

c     ---old volume
      vo = BOX*BOX*BOX

c     ---trial move in ln(V)
      lnvn = LOG(vo) + (RANF(Iseed)-0.5D0)*Vmax
      vn = EXP(lnvn)
      boxn = vn**(1.D0/3.D0)

c     ---reject if cutoff would exceed half box
      IF (0.5D0*boxn.LE.RC) THEN
         RETURN
      END IF

c     ---store old box
      boxo = BOX
      hboxo = HBOX

c     ---scale coordinates
      f = boxn/BOX
      DO i = 1, NPART
         X(i) = f*X(i)
         Y(i) = f*Y(i)
         Z(i) = f*Z(i)
      END DO

      BOX = boxn
      HBOX = 0.5D0*BOX

c     ---RC is fixed for Yukawa, do not scale RC

c     ---calculate new full energy
      CALL TOTERG(enn, virn)

c     ---NpT acceptance
      arg = EXP(-BETA*(P*(vn-vo)
     &      -(NPART+1)*LOG(vn/vo)/BETA + enn-En))

      IF (RANF(Iseed).LT.arg) THEN
c        ---accepted
         Acc = Acc + 1
         En = enn
         Vir = virn
      ELSE
c        ---rejected: restore old coordinates and box
         f = 1.D0/f
         DO i = 1, NPART
            X(i) = f*X(i)
            Y(i) = f*Y(i)
            Z(i) = f*Z(i)
         END DO

         BOX = boxo
         HBOX = hboxo
      END IF

      RETURN
      END
