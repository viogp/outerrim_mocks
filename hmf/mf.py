import sys, os, glob, getpass
sys.path.append('/mnt/lustre/eboss/OuterRim/genericio/python/')
import genericio as gio
import numpy as np
import matplotlib ; matplotlib.use('Agg')                                    
from matplotlib import pyplot as plt  
from distinct_colours import get_distinct 
cols = get_distinct(10) 

# Bins
edges = np.array([10.3, 10.7, 10.8, 10.9, 11., 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7, 11.8, 11.9, 12., 12.1, 12.2, 12.3, 12.4, 12.5, 12.7, 13., 13.5, 14., 15., 16., 17.])
mhist = np.array([10.5, 10.75, 10.85, 10.95, 11.05, 11.15, 11.25, 11.35, 11.45, 11.55, 11.65, 11.75, 11.85, 11.95, 12.05, 12.15, 12.25, 12.35, 12.45, 12.6, 12.85, 13.25, 13.75, 14.5, 15.5, 16.5])
dm = edges[1:]-edges[:-1]

###################
# Directory with the OuterRim simulation haloes
halodir = '/mnt/lustre/eboss/OuterRim/OuterRim_sim/'

# OuterRim simulation characteristics (FOF b=0.168 here)
mp  = 1.9E+09 # Msol/h
lbox= 3000.   # Mpc/h

# Get the conversion between the name of the time step and redshift
step = np.genfromtxt(halodir+'step_redshift.txt',usecols=0,dtype=int)
redshift = np.genfromtxt(halodir+'step_redshift.txt',usecols=1)

# Initialize the parameters for the figure ------------------
plt.rcParams['legend.numpoints'] = 1 
plt.rcParams['axes.labelsize'] = 10.0 ; fs = 20 
plt.rcParams['lines.linewidth'] = 2 
fig = plt.figure(figsize=(8.5,9.))

xtit = "${\\rm log}_{10}(\\rm{M/M_{\odot}}h^{-1})$"
ytit = "${\\rm log}_{10}(\Phi/ Mpc^{-3}h^3 {\\rm dlog}_{10}M)$"
                                                                             
xmin = 10. ; xmax = 16.                                                      
ymin = -6.5 ; ymax = 0.    

jj = 111                                                                     
ax = fig.add_subplot(jj) 
ax.set_xlim(xmin,xmax) ; ax.set_ylim(ymin,ymax)                              
ax.set_xlabel(xtit,fontsize = fs) ; ax.set_ylabel(ytit,fontsize = fs)        
#-------------------------------------------------------------                

#for iz,istep in enumerate(step):  # Loop over all redshifts
# Loop over a subset of redshifts
for iz,istep in enumerate([266]):    
    zz = redshift[np.where(step == istep)]
    print 'Processing snapshot at redshift ',zz
    nroot = halodir+'HaloCatalog/STEP'+str(istep)    

    # Initialize to 0 the halo mass functions
    ycount, yh = [np.zeros(len(mhist)) for _ in range(2)]

    # Loop over each of the sub volumes the 
    infiles = glob.glob(nroot+'/*'+str(istep)+'.fofproperties#*')
    for inf,infile in enumerate(infiles):
        # Print out once the information stored in each file
        if (iz == 0 and inf == 0):
            print infile
            gio.gio_inspect(infile)
            print '----------------------------'
        
        # Read the number of particles per halo
        in_count = mp*gio.gio_read(infile, "fof_halo_count")    
        ind = np.where(in_count >0.)
        count = np.log10(in_count[ind])    
        H, bins_edges = np.histogram(count,bins=edges)
        ycount = ycount + H

        # FOF mass (Msun/h)
        in_mh = gio.gio_read(infile, "fof_halo_mass")
        ind = np.where(in_mh >0.) ; mh = np.log10(in_mh[ind])
        H, bins_edges = np.histogram(count,bins=edges)
        yh = yh + H

        # Testing----------------------
        #if inf>1:
        #    break
        #-----------------------------
        
    ycount = ycount/dm/(lbox**3)
    yh = yh/dm/(lbox**3)

    # Write Halo Mass function to a file
    tofile = zip(edges[:-1],edges[1:],mhist,ycount)
    outfile = halodir+'hmf.txt'
    with open(outfile, 'w') as outf:
        outf.write('# log10Mmin_bin log10Mmax_bin log10Mmean_bin Nhalos/dm/vol \n')
        np.savetxt(outf,tofile,fmt=('%10.5f %10.5f %10.5f %6.4e'))      
    outf.closed  

    # Plot for all redshifts
    ind = np.where(ycount >0.)
    ax.plot(mhist[ind],np.log10(ycount[ind]),\
                color=cols[iz],label='z='+str(zz))

    ind = np.where(yh >0.)
    ax.plot(mhist[ind],np.log10(yh[ind]),\
                color=cols[len(cols)-iz-1],linestyle=':',label=' from mass')


# Legend
plt.legend(loc=3,prop={'size':(fs-2)}) 

# Directory with outputs (it'll be generated if it doesn't exist)
outdir = '/users/'+getpass.getuser()+'/Outputs/out_shams/'
if (not os.path.exists(outdir)): os.makedirs(outdir)

# Save figure
plotfile = outdir+'outerrim_hmf.pdf'
fig.savefig(plotfile)
print 'Output: ',plotfile
print '        ',outfile
