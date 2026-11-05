**==store.spg  processed by SPAG 4.52O  at 10:45 on  5 Jun 1996
      SUBROUTINE STORE(Iout, Dr, Vmax)
c     writes configuration to disk
      IMPLICIT NONE
      INCLUDE 'parameter.inc'
      INCLUDE 'conf.inc'
      INCLUDE 'system.inc'
      INTEGER Iout, i
      DOUBLE PRECISION Dr, Vmax
 
      WRITE (Iout, *) BOX, HBOX
      WRITE (Iout, *) NPART
      WRITE (Iout, *) Dr, Vmax
      DO i = 1, NPART
         WRITE (Iout, *) X(i), Y(i), Z(i), PTYPE(i)
      END DO
      REWIND (Iout)
      RETURN
      END

      SUBROUTINE DUMPCONF(Icyc)
c     writes current configuration in LAMMPS trajectory format
      IMPLICIT NONE
      INCLUDE 'parameter.inc'
      INCLUDE 'conf.inc'
      INCLUDE 'system.inc'

      INTEGER Icyc, i

      WRITE (77,'(A)') 'ITEM: TIMESTEP'
      WRITE (77,'(I12)') Icyc
      WRITE (77,'(A)') 'ITEM: NUMBER OF ATOMS'
      WRITE (77,'(I12)') NPART
      WRITE (77,'(A)') 'ITEM: BOX BOUNDS pp pp pp'
      WRITE (77,'(2F20.10)') 0.0D0, BOX
      WRITE (77,'(2F20.10)') 0.0D0, BOX
      WRITE (77,'(2F20.10)') 0.0D0, BOX
      WRITE (77,'(A)') 'ITEM: ATOMS id type x y z'

      DO i = 1, NPART
         WRITE (77,'(I8,1X,I4,3(1X,F16.8))')
     &        i, PTYPE(i), X(i), Y(i), Z(i)
      END DO

      RETURN
      END
