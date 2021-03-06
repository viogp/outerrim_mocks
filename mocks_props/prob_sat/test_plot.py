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
	typemock = ['part']
	xboxs = ['0'] ; yboxs = ['1'] ; zboxs =['2']

# Bins in distance (Mpc/h)
nmin = 0.5 ; nmax = 50.5 ; dn = 1
nbins = np.arange(nmin,nmax,dn)
nhist = nbins +dn*0.5

# Figure 
fig = plt.figure()
xtit = "Number of Satellites"
ytit = "$N_{\\rm sat}/N_{\\rm sat,max}$"
xmin = 0. ; xmax = 5.

ax = fig.add_subplot(111)
ax.set_xlim(xmin,xmax) 
ax.set_xlabel(xtit) ; ax.set_ylabel(ytit)
ind = np.where(nhist<=xmax)
ax.set_xticks(list(nhist[ind]),minor=False)
ax.tick_params(axis='x', which='minor', bottom=False, top=False)

# Count mocks to set colour
colmax = 0
for tmock in typemock:
	count = 0
	with open(tmock+'_mocks.txt', 'r') as ff:
		for line in ff: count += 1
	if (count>colmax) : colmax = count
cols = get_distinct(colmax)

# Loop over mocks and boxes
maxn = -999.
for itm, tmock in enumerate(typemock):
	# Path to nsat
	nsatpath = '/mnt/lustre/eboss/OuterRim/mocks/nsat_'

	with open(tmock+'_mocks.txt', 'r') as ff:
		mocks = [line.strip() for line in ff]

	for im, mock1 in enumerate(mocks):
		mock2 = mock1.split('/')[-1]
		mock = mock2.replace('galaxies','nsat')
		print('Mock: {}'.format(mock))

		beta1 = mock.split('beta')[1] 
		beta = 'beta='+beta1.split('_')[0] 
		if (beta1.split('_')[0] == '0.000'):
			beta = 'Poisson'
		elif (beta1.split('_')[0] == '-2.000'):
			beta = 'Next integer'

		pnsat = np.zeros(shape=(len(nhist)))
		for xbox in xboxs:
			for ybox in yboxs:
				for zbox in zboxs:
					ibox = xbox+ybox+zbox #; print('Box: {}'.format(ibox))

					# Change the mock names to the box we are working with
					imock = mock.replace('mock000','mock'+ibox)
					mockfile = nsatpath+tmock+'/'+imock
					check_file(mockfile) #; print('Mockfile: {}'.format(mockfile))

					# Read the catalogue with number of satellites
					# tag 0, nsat 1
					lnsat = []
					with open(mockfile, 'rb') as ff:
						for line in ff:
							lnsat.append(int(line.strip().split()[1]))

					nsat = np.asarray(lnsat,dtype=int) 
					lnsat = []
					if (np.max(nsat) > maxn): maxn=np.max(nsat)

					# Histogram
					ind = np.where(nsat>0)
					H, bin_edges = np.histogram(nsat[ind], bins=np.append(nbins,nmax))
					pnsat = pnsat + H
					nsat = []

		print('    Nmax={}'.format(maxn))
		intpn = np.sum(pnsat)*dn
		pn = pnsat/np.max(pnsat) #/intpn
		# Lines plot
		#ax.plot(nhist,pn,label=tmock+', '+beta,
		#		linestyle=lsty[itm],color=cols[im])
		# Step plot
		tmp = np.insert(pn,0,pn[0])
		yy = np.asarray(tmp,dtype=float)
		tmp = np.insert(nhist,0,nhist[0]-1)
		xx = np.asarray(tmp,dtype=float) + 0.5
		ax.step(xx,yy,label=tmock+', '+beta,
				linestyle=lsty[itm],color=cols[im])

# Legend
leg = ax.legend(loc=1)
leg.draw_frame(False)

# Save figure
plotfile = '/mnt/lustre/eboss/OuterRim/mocks/plots/tests/nsat_max_'+str(istep)+'.png'
fig.savefig(plotfile)
print 'Output: ',plotfile
