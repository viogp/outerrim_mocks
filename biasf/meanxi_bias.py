import sys,os
import numpy as np
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt

def chi2(obs,model,err):
	val = 0.
	for i,iobs in enumerate(obs):
		val = val + (iobs-model[i])**2/(err[i]*err[i])
	return val

space = 'rspace' #'zspace'
snap = '266'

weight = True

loglog = True
plotmean = True
plotbias = True

# Path to DM monopole
fxidm = '/users/savila/CorrelationTools/xir/OuterRim_new.b1.00.z0.865.2PCF'
rdm, xidm = np.loadtxt(fxidm ,unpack = True)

# Read the HMF mass bins
halodir = '/mnt/lustre/eboss/OuterRim/OuterRim_sim/'
mfile = halodir + 'hmfs/hmf_'+snap+'.txt'
mlow, mhigh, mhmed = np.loadtxt(mfile, usecols= (0, 1, 3), unpack=True)

# Path to CUTE output and plots
ocat = '/mnt/lustre/eboss/OuterRim/OuterRim_sim/ascii/OuterRim_STEP266_z0.865/subvols27/biasf/'
path2plot = ocat+'plots/'

# Find number of separation bins and define matrices
r0 = np.loadtxt(ocat+space+'_full_000_'+str(mlow[0])+'.txt', usecols=(0), unpack=True)
mxi, exi = [np.zeros((len(mlow),len(r0))) for i in range(2)]
if weight:
	wsum = np.zeros((len(mlow),len(r0)))

# Get the mean two point correlation function at each mass bin
for i, imlow in enumerate(mlow):
	icount = 0
	for ix in range(3):
		for iy in range(3):
			for iz in range(3):
				namebox = str(ix)+str(iy)+str(iz)
				boxfile = ocat+space+'_full_'+namebox+'_'+str(imlow)+'.txt'

				if (not os.path.isfile(boxfile)):
					print('Not found {}'.format(boxfile)) ; sys.exit()

				r, xi, err, dd = np.loadtxt(boxfile, usecols=(0,1,2, 3), unpack=True)
				if (not (r==r0).all()):
					print('{}: Different bins? {}, {}'.format(boxfile,r,r0)) ; sys.exit()

				if weight:
					xiclean = np.zeros(len(xi))
					w = np.zeros(len(err))
					# Account for bins with no pairs
					ind = np.where((dd>1) & (np.absolute(err)>0.)) 
					if(np.shape(ind)[1] > 0):
						xiclean[ind] = xi[ind]
						w[ind] = 1./(err[ind]**2) 
					# Add values
					mxi[i,:] = mxi[i,:] + np.multiply(xiclean,w)
					wsum[i,:] = wsum[i,:] + w 
				else:
					mxi[i,:] = mxi[i,:] + xi
					icount += 1

	if weight:
		ww = wsum[i,:]
		ind = np.where(ww>0.)                                                                       
		if(np.shape(ind)[1] > 0): 
			mxi[i,ind] = mxi[i,ind]/ww[ind]
			exi[i,ind] = np.sqrt(1./ww[ind])
		# Account for bins with no pairs
		ind = np.where(ww<=0.)
		if(np.shape(ind)[1] > 0): 
			mxi[i,ind] = -999.
			exi[i,ind] = -999.

	else:
		mxi[i,:] = mxi[i,:]/icount

if not weight:
	nbox = icount
	# Calculate the standard error
	for i, imlow in enumerate(mlow):
		for ix in range(3):
			for iy in range(3):
				for iz in range(3):
					namebox = str(ix)+str(iy)+str(iz)
					boxfile = ocat+space+'_full_'+namebox+'_'+str(imlow)+'.txt'

					r, xi = np.loadtxt(boxfile, usecols=(0,1), unpack=True)

					exi[i,:] = exi[i,:] + (xi - mxi[i,:])**2
		exi[i,:] = np.sqrt(exi[i,:]/(nbox*nbox-nbox))


# Plot averaged monopole with errors for each mass bin
if plotmean:
	fig = plt.figure(figsize = (8., 9.))
	ax = fig.add_subplot(111)
	cm = plt.get_cmap('YlGnBu')
	cols = plt.cm.Spectral(np.linspace(0,1,len(mlow)))
	ax.set_prop_cycle('color',cols)

	if loglog:
		xtit = '${\\rm log_{10}(r /h^{-1}\\rm{Mpc})}$'
		ytit = '${\\rm log_{10}\\xi(r)}$'
		xmin=-1. ; xmax=2.25 ; ymin=-3.5 ; ymax=2.
	else:
		xtit = '${\\rm r /h^{-1}\\rm{Mpc}}$'
		ytit = '${\\rm r^{2}\\xi(r)}$'
		xmin=-5 ; xmax=200. ; ymin=-10. ; ymax=100
	plt.xlabel(xtit) ; plt.ylabel(ytit)
	plt.xlim(xmin,xmax) ; plt.ylim(ymin,ymax)

	for i, imlow in enumerate(mlow):
		yy1 = mxi[i,:] ; err1 = exi[i,:]
		leg = '['+str(imlow)+','+str(mhigh[i])+')'
		#'$\leq M_{\\rm halo}(h^{-1}\\rm{M_{\odot}})<$'+\

		if loglog:
			ind = np.where(yy1>0)
			xx = np.log10(r0[ind])
			yy = np.log10(yy1[ind])

			low = np.log10(yy1[ind]+err1[ind]) - yy
			high = yy - np.log10(yy1[ind]-err1[ind])
		else:
			ind = np.where(yy1>-999.)
			xx = r0[ind]
			yy = yy1[ind]*r0[ind]*r0[ind]
			low = r0[ind]*r0[ind]*err1[ind]
			high = r0[ind]*r0[ind]*err1[ind]

		ax.errorbar(xx, yy, yerr=[low,high], label=leg)

	leg = ax.legend(loc=1, handlelength=0, handletextpad=0)
	for item in leg.legendHandles:
		item.set_visible(False)
	for color,text in zip(cols,leg.get_texts()):
		text.set_color(color)
		leg.draw_frame(False)

	#Plot DM
	ind = np.where(xidm>0.)
	if loglog:
		ind = np.where(xidm>0)
		xx = np.log10(rdm[ind])
		yy = np.log10(xidm[ind])
	else:
		xx = rdm
		yy = xidm*rdm*rdm
	ax.plot(xx,yy,color='k')
	ax.text(xmin+0.05*(xmax-xmin),ymin+0.05*(ymax-ymin), 'DM')

	# Save fig
	plotname = 'mean2PCF.png'
	fig.savefig(path2plot + plotname)
	print ('Ouput: {}{}'.format(path2plot,plotname))

##############################################
# Calculate the bias in different mass ranges
# and different separation ranges
rmin = [8.,10.,20.]
rmax = [70.,80.]
abias = np.linspace(0.1,100.,10000)
chis = np.zeros((len(abias))) ; chis.fill(999.)

mbias = np.zeros((len(rmin)*len(rmax),len(mlow))) ; mbias.fill(-999.)
diff = np.zeros((len(rmin)*len(rmax)))
rlrh_name = []

icount = -1
for rl in rmin:
	for rh in rmax:
		icount += 1
		rlrh_name = np.append(rlrh_name,'rl'+str(rl)+'_rh'+str(rh))

		rind = np.where((r0>=rl) & (r0<=rh))
		rr1 = r0[rind]

		# Plot bias
		if plotbias:
			fig = plt.figure(figsize = (8., 9.))
			ax = fig.add_subplot(111)
			cm = plt.get_cmap('summer')
			cols = plt.cm.Spectral(np.linspace(0,1,len(mlow)))
			#ax.set_prop_cycle('color',cols)
			xtit = '${\\rm r (h^{-1}\\rm{Mpc})}$'
			ytit = '${\\rm \sqrt{\\xi_{hh}/\\xi_{DM}}}$'
			xmin=min(rmin) ; xmax=max(rmax) ; ymin=0.5 ; ymax=6.5
			plt.xlabel(xtit) ; plt.ylabel(ytit)
			plt.xlim(xmin,xmax) ; plt.ylim(ymin,ymax)

		idiff = 0
		for i, imlow in enumerate(mlow):
			oxi2 = mxi[i,:] ; oerr2=exi[i,:]
			oxi1 = oxi2[rind] ; oerr1 = oerr2[rind]
			ind = np.where((oxi1 > -999.) & (oerr1 > -999.))
			if(np.shape(ind)[1] > 1):
				rr = rr1[ind]
				oxi = oxi1[ind] ; oerr = oerr1[ind]
			else:
				continue

			dm = np.interp(rr, rdm, xidm)
			for ib,bb in enumerate(abias):
				dmh = bb*bb*dm
				chis[ib] = chi2(oxi,dmh,oerr)

			ib = np.where(chis == np.nanmin(chis))
			bias = abias[ib][0]
			mbias[icount,i] = bias

			bb = np.sqrt(oxi/dm)
			ebb= oerr/(2*bb)
			mbb = np.zeros(len(bb)) ; mbb.fill(bias)
			idiff = idiff + chi2(bb,mbb,ebb)

			if plotbias:
				leg = '['+str(imlow)+','+str(mhigh[i])+')'
				ax.errorbar(rr, bb, ebb, label=leg, color=cols[i])
				ax.plot([xmin,xmax],[bias,bias], \
						linestyle='--',color=cols[i])

		diff[icount] = idiff

		if plotbias:
			leg = ax.legend(loc=1, handlelength=0, handletextpad=0)
			for item in leg.legendHandles:
				item.set_visible(False)
			for color,text in zip(cols,leg.get_texts()):
				text.set_color(color)
				leg.draw_frame(False)


			# Save fig
			plotname = 'bias_'+rlrh_name[icount]+'.png'
			fig.savefig(path2plot + plotname)
			print ('Ouput: {}{}'.format(path2plot,plotname))

# Write out the bias function measured within
# the separation range best fitted by a constant bias.
ind = np.where(diff == np.nanmin(diff))

bb = np.squeeze(mbias[ind,:]) # Remove single-dimensional entries
tofile = zip(mhmed,bb)

bfile = halodir + 'bias_'+rlrh_name[icount]+'.txt'
with open(bfile,'w') as outf:
	np.savetxt(outf,tofile,fmt=('%10.5f %10.5f'))
	outf.closed
print ('Bias function in: {}'.format(bfile))
