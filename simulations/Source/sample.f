**==sample.spg  processed by SPAG 4.52O  at 10:45 on  5 Jun 1996
 
      SUBROUTINE SAMPLE(I, En, Vir)
c     writes quantities to file
      IMPLICIT NONE
      INCLUDE 'parameter.inc'
      INCLUDE 'conf.inc'
      INCLUDE 'system.inc'
      INCLUDE 'potential.inc'
      INTEGER I
      DOUBLE PRECISION En, enp, Vir, press, CORP, vol, rho
 
      IF (NPART.NE.0) THEN
         enp = En/DBLE(NPART)
         vol = BOX**3
         rho = NPART/vol
         press = rho/BETA + Vir/(3.D0*vol)
         IF (TAILCO) press = press + CORP(RC, rho)
      ELSE
         rho = 0.D0
         enp = 0.D0
         press = 0.D0
      END IF
      WRITE (66, *) I, SNGL(enp), SNGL(press), SNGL(rho)
      RETURN
      END

      SUBROUTINE SAMPLEMETRICS(I, En, Vir, Attempt, Nacc, Attv, Accv)
c     Writes transparent run diagnostics to fort.67.
c     The pressure estimator excludes the hard-core contact contribution
c     and is therefore labelled p_continuous rather than total pressure.
      IMPLICIT NONE
      INCLUDE 'parameter.inc'
      INCLUDE 'conf.inc'
      INCLUDE 'system.inc'
      INCLUDE 'potential.inc'
      INCLUDE 'npt.inc'
      INTEGER I, Attempt, Nacc, Attv, Accv
      DOUBLE PRECISION En, Vir, vol, rho, eta, pcontinuous
      DOUBLE PRECISION fracp, fracv

      vol = BOX**3
      rho = NPART/vol
      eta = PI*rho/6.D0
      pcontinuous = rho/BETA + Vir/(3.D0*vol)
      fracp = 0.D0
      fracv = 0.D0
      IF (Attempt.GT.0) fracp = DBLE(Nacc)/DBLE(Attempt)
      IF (Attv.GT.0) fracv = DBLE(Accv)/DBLE(Attv)

      WRITE (67, 99001) I, En/DBLE(NPART), rho, eta, P,
     &                  pcontinuous, Attempt, Nacc, fracp,
     &                  Attv, Accv, fracv
      RETURN
99001 FORMAT (i12, 5(1x,e20.12), 2(1x,i12), 1x,f12.8,
     &        2(1x,i12), 1x,f12.8)
      END
