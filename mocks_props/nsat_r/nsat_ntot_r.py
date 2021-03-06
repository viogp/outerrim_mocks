import sys,os
import numpy as np
from iotools import check_file
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib import gridspec
from distinct_colours import get_distinct
import mpl_style
plt.style.use(mpl_style.style1)

Testing = False

istep = 266

typemock=['NFW','part']
lsty=['-',':']

xboxs = ['0','1','2']
yboxs = ['0','1','2']
zboxs = ['0','1','2']

if (Testing):
	xboxs = ['0'] ; yboxs = ['1'] ; zboxs =['2']

# Bins in distance (Mpc/h)
rmin = -3 ; rmax = 2. ; dr = 0.05
rbins = np.arange(rmin,rmax,dr)
rhist = rbins +dr*0.5

# Figure 
fig = plt.figure()
xtit = "${\\rm log}_{10}(r\,h^{-1}{\\rm Mpc})$"
ytit = "${\\rm log}_{10}(N_{\\rm sat,dex}/N_{\\rm sat, tot})$"
xmin = -2 ; xmax = 0.7
ymin = -5 ; ymax = -0.4

ax = fig.add_subplot(111)
ax.set_xlim(xmin,xmax) ; ax.set_ylim(ymin,ymax)
ax.set_xlabel(xtit) ; ax.set_ylabel(ytit)

# Count mocks to set colour
colmax = 0
for tmock in typemock:
	count = 0
	with open(tmock+'_mocks.txt', 'r') as ff:
		for line in ff: count += 1
	if (count>colmax) : colmax = count
cols = get_distinct(colmax)

# Loop over mocks and boxes
minr = 999. ; maxr = -999.
for itm, tmock in enumerate(typemock):
	# Initialise the matrix to store the number of sat at different distances
	with open(tmock+'_mocks.txt', 'r') as ff:
		mocks = [line.strip() for line in ff]

	for im, mock in enumerate(mocks):
		avgr = 0. ; ntot = 0.
		kval1 = mock.split('K')[1]
		kval = kval1.split('_')[0]

		nsatr = np.zeros(shape=(len(rbins)))
		for xbox in xboxs:
			for ybox in yboxs:
				for zbox in zboxs:
					ibox = xbox+ybox+zbox #; print('Box: {}'.format(ibox))

					# Change the mock names to the box we are working with
					mockfile = mock.replace('mock000','mock'+ibox)
					check_file(mockfile) ; print('Mockfile: {}'.format(mockfile))

					# Read mock catalogue
					# x 0, y 1,z 2(Mpc/h), vx 3, vy 4, vz 5(comoving peculiar in km/s), 
					# lmass 6(np.log10(fof_halo_mass)), cen 7(-1=sat, 0=cen), 
					# dvx 8, dvy 9, dvz 10, dx 11, dy 12, dz 13, tag 14(fof_halo_tag)  
					ldx = [] ; ldy = [] ; ldz = []
					with open(mockfile, 'rb') as ff:
						for line in ff:
							cen = int(line.strip().split()[7])
							if (cen<0):
								ldx.append(float(line.strip().split()[11]))
								ldy.append(float(line.strip().split()[12]))
								ldz.append(float(line.strip().split()[13]))
					dx = np.asarray(ldx,dtype=float)
					dy = np.asarray(ldy,dtype=float)
					dz = np.asarray(ldz,dtype=float)
					ldx = [] ; ldy = [] ; ldz = []

					# Get r in kpc/h for satellite galaxies
					rsat = np.sqrt(dx*dx + dy*dy + dz*dz)

					# Average r
					avgr = avgr + np.sum(rsat)
					ntot = ntot + len(rsat)

					# Limits of logr
					ind = np.where(rsat>0.)
					lrsat = np.log10(rsat[ind])
					if(np.min(lrsat)<minr) : minr = np.min(lrsat)
					if(np.max(lrsat)>maxr) : maxr = np.max(lrsat)

					# Histogram
					H, bin_edges = np.histogram(lrsat, bins=np.append(rbins,rmax))
					nsatr = nsatr + H
					print('    Nmin={:.2f}, Nmax={:.2f}'.format(np.min(nsatr),np.max(nsatr)))

		ytot = np.sum(nsatr)
		ind = np.where(nsatr>0)
		ax.plot(rhist[ind],np.log10(nsatr[ind]/ytot),label=tmock+', K='+kval,
				linestyle=lsty[itm],color=cols[im]) 
		#ax.plot(np.log10(rhist[ind]),nsatr[ind]/ymax,label=tmock+', K='+kval,
		#		linestyle=lsty[itm],color=cols[im]) #lineal 

		# Arrows/lines to show the median values
		dy = 0.05*(ymax-ymin) 
		avgr = avgr/ntot
		ax.arrow(np.log10(avgr),ymax-dy,0,dy,color=cols[im],ls=lsty[itm],
				 length_includes_head=True,
				 head_width=dy*0.1, head_length=dy*0.3)

print('    Rmin={:.2f}, Rmax={:.2f} Mpc'.format(minr,maxr))

# Legend
leg = ax.legend(loc=0)
leg.draw_frame(False)

# Save figure
#plotfile = '/mnt/lustre/eboss/OuterRim/mocks/plots/nsat_r_'+str(istep)+'.png'
plotfile = '/mnt/lustre/eboss/OuterRim/mocks/plots/nsat_ntot_r_'+str(istep)+'.png'
fig.savefig(plotfile)
print 'Output: ',plotfile
