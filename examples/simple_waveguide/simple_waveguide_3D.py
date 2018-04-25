import emopt
from emopt.misc import NOT_PARALLEL

import numpy as np
from math import pi

from petsc4py import PETSc

####################################################################################
# Simulation parameters
####################################################################################
X = 5.0
Y = 3.0
Z = 2.0
dx = 0.03
dy = dx
dz = dx

wavelength = 1.55

#####################################################################################
# Setup simulation
#####################################################################################
sim = emopt.fdfd.FDFD_3D(X,Y,Z,dx,dy,dz,wavelength, rtol=1e-5)
sim.w_pml = [0.2, 0.2, 0.2, 0.2]

X = sim.X
Y = sim.Y
Z = sim.Z

Nx = sim.Nx
Ny = sim.Ny
Nz = sim.Nz

#####################################################################################
# Define the geometry/materials
#####################################################################################
r1 = emopt.grid.Rectangle(X/2, Y/2, 2*X, 0.5); r1.layer = 1
r2 = emopt.grid.Rectangle(X/2, Y/2, 2*X, 2*Y); r2.layer = 2

r1.material_value = 3.45**2
r2.material_value = 1.444**2

eps = emopt.grid.StructuredMaterial3D(X, Y, Z, dx, dy, dz)
eps.add_primitive(r2, -Z, Z)
eps.add_primitive(r1, Z/2-0.11, Z/2+0.11)

mu = emopt.grid.ConstantMaterial3D(1.0)

sim.set_materials(eps, mu)
sim.build()

#####################################################################################
# Setup the sources
#####################################################################################

Jx = np.zeros([Nz, Ny, Nx], dtype=np.complex128)
Jy = np.zeros([Nz, Ny, Nx], dtype=np.complex128)
Jz = np.zeros([Nz, Ny, Nx], dtype=np.complex128)
Mx = np.zeros([Nz, Ny, Nx], dtype=np.complex128)
My = np.zeros([Nz, Ny, Nx], dtype=np.complex128)
Mz = np.zeros([Nz, Ny, Nx], dtype=np.complex128)

Jy[Nz/2, Ny/2, Nx/2] = 1.0
#Jx[Nz/2, Ny/2-8:Ny/2+8, Nx/2-8:Nx/2+8] = 3.5
#My[Nz/2, Ny/2-8:Ny/2+8, Nx/2-8:Nx/2+8] = 1.0

src = [Jx, Jy, Jz, Mx, My, Mz]
sim.set_sources(src)

sim.solve_forward()


#R = sim._Rst
#Interp = sim._Interp
#flr = Interp*(R*sim.x)
#scatter, flr_full = PETSc.Scatter.toZero(flr)
#scatter.scatter(flr, flr_full,False, PETSc.Scatter.Mode.FORWARD)

if(NOT_PARALLEL):
    #flr = flr_full
    fields = sim.fields

    Ez = fields[1::6]
    Ez = np.reshape(Ez, (Nz, Ny, Nx))

    #Ezlr = x2h[0::6]
    #Ezlr = np.reshape(Ezlr, (int(Nz/2), int(Ny/2), int(Nx/2)))

if(NOT_PARALLEL):
    import matplotlib.pyplot as plt

    #eps_slice = eps_grid[wg_slice.i, wg_slice.j, wg_slice.k].real
    #eps_slice = eps_slice[0, :, :]

    Ez_slice = Ez[Nz/2, :, :]
    #Ez_slice = Ez_slice[:, 0, :]

    vmax = np.max(np.real(Ez_slice))
    f = plt.figure()
    ax = f.add_subplot(111)
    ax.imshow(np.real(Ez_slice), extent=[0,X,0,Y], vmin=-vmax, vmax=vmax, cmap='seismic')
    plt.show()

    #Ez_slice = Ezlr[:, int(Ny/4), :]

    #vmax = np.max(np.real(Ez_slice))
    #f = plt.figure()
    #ax = f.add_subplot(111)
    #ax.imshow(np.real(Ez_slice), extent=[0,Nx,0,Nz], vmin=-vmax, vmax=vmax, cmap='seismic')
    #plt.show()