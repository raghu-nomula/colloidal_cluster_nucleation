c conf.inc
      double precision x,y,z
      integer npart,ptype
      common/conf1/x(npmax),y(npmax),z(npmax),npart
      common/conf2/ptype(npmax)
c
c     x(i),y(i),z(i)    : position particle i
c     npart             : actual number of particles
c     ptype(i)          : particle type, 1 = positive, 2 = negative
