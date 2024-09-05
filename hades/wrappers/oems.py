# -*- coding: utf-8 -*-
"""
 Bent Patch Antenna Tutorial

 Tested with
  - python 3.10
  - openEMS v0.0.35+

 (c) 2016-2023 Thorsten Liebig <thorsten.liebig@gmx.de>

"""

### Import Libraries
import os, tempfile
import shutil
from os.path import dirname

from pylab import *
from mpl_toolkits.mplot3d import Axes3D

if 'OPENEMS_INSTALL_PATH' not in os.environ:
    os.environ['OPENEMS_INSTALL_PATH'] = dirname(shutil.which("openEMS"))
    print(os.environ['OPENEMS_INSTALL_PATH'])
from CSXCAD import CSXCAD

from openEMS.openEMS import openEMS
from openEMS.physical_constants import *

from hades.wrappers.ngsolve_w import make_geometry
import ngsolve as ng

### Setup the simulation
Sim_Path = './workdir/inductor'

post_proc_only = False
refresh_mesh = False
show_model = False
unit = 1e-6 # all length in mm

f0 = 2.4e9 # center frequency, frequency of interest!
lambda0 = round(C0/f0/unit) # wavelength in mm
fc = 0.5e9 # 20 dB corner frequency

# patch width in alpha-direction
patch_width  = 32 # resonant length in alpha-direction
patch_radius = 50 # radius
patch_length = 40 # patch length in z-direction

#substrate setup
substrate_epsR   = 3.38
substrate_kappa  = 1e-3 * 2*pi*2.45e9 * EPS0*substrate_epsR
substrate_width  = 80
substrate_length = 90
substrate_thickness = 1.524
substrate_cells = 4

#setup feeding
feed_pos   = -5.5  #feeding position in x-direction
feed_width = 2     #feeding port width
feed_R     = 50    #feed resistance

# size of the simulation box
SimBox_rad    = 2*100
SimBox_height = 1.5*200

### Setup FDTD parameter & excitation function
FDTD = openEMS(CoordSystem=0, EndCriteria=1e-4) # init a cylindrical FDTD
f0 = 2e9 # center frequency
fc = 1e9 # 20 dB corner frequency
FDTD.SetGaussExcite(f0, fc)
FDTD.SetBoundaryCond(['MUR', 'MUR', 'MUR', 'MUR', 'MUR', 'MUR']) # boundary conditions

### Setup the Geometry & Mesh
if refresh_mesh:
    geom = make_geometry('tests/test_layouts/ref_ind.gds', only_metal=True)
    mesh = ng.Mesh(geom.GenerateMesh())
    mesh.ngmesh.Export('test.stl', 'STL Format')
CSX = CSXCAD.ContinuousStructure()
FDTD.SetCSX(CSX)
copper = CSX.AddMetal("copper")
copper.AddPolyhedronReader("test.stl", priority=10)
FDTD.AddEdges2Grid(dirs='all', properties=copper)


# create substrate
substrate = CSX.AddMaterial('substrate', epsilon=substrate_epsR, kappa=substrate_kappa)
substrate.AddBox(start=[-20, -80, 70], stop=[140, 80, 90])
FDTD.AddEdges2Grid(dirs='all', properties=substrate)

# create ground
gnd = CSX.AddMetal('gnd') # create a perfect electric conductor (PEC)
gnd.AddBox(priority=10, start=[-20, -12.5, 81.5], stop=[-20, -7.5, 81.5])
FDTD.AddEdges2Grid(dirs='all', properties=gnd)

# apply the excitation & resist as a current source
start = [-20, 10, 81.5]
stop = [-20, -10, 81.5]
port = FDTD.AddLumpedPort(1, feed_R, start, stop, 'y', 1.0, priority=50, edges2grid='all')

mesh = CSX.GetGrid()
mesh.SmoothMeshLines('all', 0.5, 1.4)
## Add the nf2ff recording box
nf2ff = FDTD.CreateNF2FFBox()

### Run the simulation
if show_model:  # debugging only
    CSX_file = os.path.join(Sim_Path, "bent_patch.xml")
    if not os.path.exists(Sim_Path):
        os.mkdir(Sim_Path)
    CSX.Write2XML(CSX_file)
    from CSXCAD import AppCSXCAD_BIN
    os.system(AppCSXCAD_BIN + ' "{}"'.format(CSX_file))


if not post_proc_only:
    FDTD.Run(Sim_Path, verbose=3)

### Postprocessing & plotting
f = np.linspace(max(1e9,f0-fc),f0+fc,401)
port.CalcPort(Sim_Path, f)
Zin = port.uf_tot / port.if_tot
s11 = port.uf_ref/port.uf_inc
s11_dB = 20.0*np.log10(np.abs(s11))

figure()
plot(f/1e9, s11_dB)
grid()
ylabel('s11 (dB)')
xlabel('frequency (GHz)')

P_in = 0.5*np.real(port.uf_tot * np.conj(port.if_tot)) # antenna feed power

# plot feed point impedance
figure()
plot( f/1e6, real(Zin), 'k-', linewidth=2, label=r'$\Re(Z_{in})$' )
grid()
plot( f/1e6, imag(Zin), 'r--', linewidth=2, label=r'$\Im(Z_{in})$' )
title( 'feed point impedance' )
xlabel( 'frequency (MHz)' )
ylabel( 'impedance ($\Omega$)' )
legend( )


idx = np.where((s11_dB<-10) & (s11_dB==np.min(s11_dB)))[0]
if not len(idx)==1:
    print('No resonance frequency found for far-field calulation')
else:
    f_res = f[idx[0]]
    theta = np.arange(-180.0, 180.0, 2.0)
    print("Calculate NF2FF")
    nf2ff_res_phi0 = nf2ff.CalcNF2FF(Sim_Path, f_res, theta, 0, center=np.array([patch_radius+substrate_thickness, 0, 0])*unit, read_cached=True, outfile='nf2ff_xz.h5')

    figure(figsize=(15, 7))
    ax = subplot(121, polar=True)
    E_norm = 20.0*np.log10(nf2ff_res_phi0.E_norm/np.max(nf2ff_res_phi0.E_norm)) + nf2ff_res_phi0.Dmax
    ax.plot(np.deg2rad(theta), 10**(np.squeeze(E_norm)/20), linewidth=2, label='xz-plane')
    ax.grid(True)
    ax.set_xlabel('theta (deg)')
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.legend(loc=3)

    phi = theta
    nf2ff_res_theta90 = nf2ff.CalcNF2FF(Sim_Path, f_res, 90, phi, center=np.array([patch_radius+substrate_thickness, 0, 0])*unit, read_cached=True, outfile='nf2ff_xy.h5')

    ax = subplot(122, polar=True)
    E_norm = 20.0*np.log10(nf2ff_res_theta90.E_norm/np.max(nf2ff_res_theta90.E_norm)) + nf2ff_res_theta90.Dmax
    ax.plot(np.deg2rad(phi), 10**(np.squeeze(E_norm)/20), linewidth=2, label='xy-plane')
    ax.grid(True)
    ax.set_xlabel('phi (deg)')
    suptitle('Bent Patch Anteanna Pattern\nFrequency: {} GHz'.format(f_res/1e9), fontsize=14)
    ax.legend(loc=3)

    print( 'radiated power: Prad = {:.2e} Watt'.format(nf2ff_res_theta90.Prad[0]))
    print( 'directivity:    Dmax = {:.1f} ({:.1f} dBi)'.format(nf2ff_res_theta90.Dmax[0], 10*np.log10(nf2ff_res_theta90.Dmax[0])))
    print( 'efficiency:   nu_rad = {:.1f} %'.format(100*nf2ff_res_theta90.Prad[0]/real(P_in[idx[0]])))

show()

