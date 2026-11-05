c potential.inc 
      double precision eps4,sig2,mass,ecut,rc2,pi
     $             ,eps48,rc,kappa
      logical tailco,shift
      common/pot1/pi,eps4,eps48,sig2,mass,rc,rc2,ecut
     $        ,kappa,tailco,shift
c
c     pi        : pi = 3.14 ..
c     eps4      : old LJ parameter, not used for Yukawa
c     eps48     : old LJ parameter, not used for Yukawa
c     sig2      : sigma*sigma
c     mass      : mass, not important in MC
c     rc        : cut-off radius
c     rc2       : rc*rc
c     ecut      : old shift parameter, not used for Yukawa
c     kappa     : inverse Debye screening length
c     tailco    : must be false for Yukawa
c     shift     : must be false for Yukawa
