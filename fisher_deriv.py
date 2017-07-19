from classy import Class
import numpy as np
import matplotlib.pyplot as plt
import subprocess
import matplotlib as mpl
from numpy import linalg

font = {'family':'serif','weight':'normal','size':12}
mpl.rcParams['xtick.major.size'] = 7
mpl.rcParams['xtick.major.width'] = 1
mpl.rcParams['xtick.minor.size'] = 3
mpl.rcParams['xtick.minor.width'] = 1
mpl.rcParams['ytick.major.size'] = 7
mpl.rcParams['ytick.major.width'] = 1
mpl.rcParams['ytick.minor.size'] = 3
mpl.rcParams['ytick.minor.width'] = 1
mpl.rcParams['axes.labelsize'] = 16
mpl.rc('font', **font)        

def run_fisher(param,cv,delta,mass = [1.0],num = 25,deg = 3,run = 'False',**kwargs):

    def run_CLASS(dict):
        cosmo = Class()
        cosmo.set(dict)
        cosmo.compute()
        output = cosmo.lensed_cl(2500)
        return output['ell'],output['tt'],output['te'],output['ee']

    cv_floats = []
    cv_strings = []
    param_floats = []
    param_strings = []
    for i in range(len(cv)):
        if isinstance(cv[i],basestring):
            cv_strings.append(cv[i])
            param_strings.append(param[i])
        else:
            cv_floats.append(cv[i])
            param_floats.append(param[i])

    high = np.reshape([cv_floats]*len(cv_floats),(len(cv_floats),len(cv_floats)))
    low = np.reshape([cv_floats]*len(cv_floats),(len(cv_floats),len(cv_floats)))
    span = []
    for i in range(len(high)):
        high[i][i] = high[i][i]+delta[i]
        low[i][i] = low[i][i]-delta[i]
        span.append(np.linspace(low[i][i],high[i][i],num))
    runs = np.reshape([cv_floats]*len(cv_floats)*num,(len(cv_floats),num,len(cv_floats)))
    for i in range(len(runs)):
        runs[i][:,i] = span[i]

    def save():
        ell = []
        cl_tt = []
        cl_te = []
        cl_ee = []
        for i in range(len(runs)):
            for j in range(len(runs[i])):
                dict = {param_floats[k]:runs[i][j][k] for k in range(len(param_floats))}
                string_dict = {param_strings[k]:cv_strings[k] for k in range(len(param_strings))}
                dict.update(string_dict)
                ell.append(run_CLASS(dict)[0])
                cl_tt.append(run_CLASS(dict)[1])
                cl_te.append(run_CLASS(dict)[2])
                cl_ee.append(run_CLASS(dict)[3])
        ell = np.reshape(ell,(len(cv_floats),num,2501))
        cl_tt = np.reshape(cl_tt,(len(cv_floats),num,2501))
        cl_te = np.reshape(cl_te,(len(cv_floats),num,2501))
        cl_ee = np.reshape(cl_ee,(len(cv_floats),num,2501))
        np.save('ell',ell)
        np.save('cl_tt',cl_tt)
        np.save('cl_te',cl_te)
        np.save('cl_ee',cl_ee)

    if run == 'True':
        save()

    def load():
        ell = np.load('ell.npy')
        cl_tt = np.load('cl_tt.npy')
        cl_te = np.load('cl_te.npy')
        cl_ee = np.load('cl_ee.npy')
        return ell,cl_tt,cl_te,cl_ee

    ell,cl_tt,cl_te,cl_ee = load()

    scale = np.asarray((2.7255**2)*(10**12)).reshape(1,1,1)

    ell = np.transpose(ell,(0,2,1))
    cl_tt = np.transpose(cl_tt,(0,2,1))
    cl_te = np.transpose(cl_te,(0,2,1))
    cl_ee = np.transpose(cl_ee,(0,2,1))
    cl_tt = cl_tt*scale
    cl_te = cl_te*scale
    cl_ee = cl_ee*scale

    def poly_fit(x,y,deg):
        poly = []
        for i in range(len(y)):
            for j in range(len(y[i])):
                poly.append(np.polyfit(x[i],y[i][j],deg))
        poly = np.reshape(poly,(len(y),len(y[0]),deg+1))
        return poly


    def deriv(cl):
        poly_coeff = poly_fit(span,cl,deg)
        deriv_coeff = []
        for i in range(len(poly_coeff)):
            for j in range(len(poly_coeff[i])):
                deriv_coeff.append(np.poly1d(np.polyder(poly_coeff[i][j])))
        deriv_coeff = np.reshape(deriv_coeff,(len(poly_coeff),len(poly_coeff[0]),1))
        deriv = []
        for i in range(len(deriv_coeff)):
            for j in range(len(deriv_coeff[i])):
                deriv.append(deriv_coeff[i][j][0](span[i][12]))
        deriv = np.reshape(deriv,(len(deriv_coeff),len(deriv_coeff[0])))
        return deriv

    deriv_tt,deriv_te,deriv_ee = deriv(cl_tt),deriv(cl_te),deriv(cl_ee)

    def plot(x,y,z):
        y_mod = x*(x+1.0)*y/(2*np.pi)
        z_mod = x*(x+1.0)*z/(2*np.pi)
        param_labels = ['\omega_b','\omega_{cdm}','H_0']
        fig,ax = plt.subplots()
#        ax.plot(x[0][2:],y_mod[0][2:],label = '$TT$')
#        ax.plot(x[0][2:],z_mod[0][2:],label = '$EE$')
        for i in range(len(y_mod)):
            ax.plot(x[0][2:],y_mod[i][2:],label = r'$%s$' %(param_labels[i]))
#            ax.plot(x[0],z_mod[i],label = r'$%s$' %(param_labels[i]))
        plt.xscale('log')
#        plt.yscale('log')
        plt.xlabel(r'$\ell$')
        plt.ylabel(r'$\partial{C_l^{TT}}/\partial{p}$')
#        plt.ylabel(r'$\ell(\ell+1)C_{\ell}/2\pi$ $[\mu \rm{K}^2]$')
        plt.title(r'CMB Power Spectra Derivatives')
        plt.legend(frameon = False, loc = 'upper right')
        plt.savefig('deriv.pdf')
        subprocess.call('open deriv.pdf',shell = True)

#    plot(ell[:,:,12],cl_tt[:,:,12],cl_ee[:,:,12])
#    plot(ell[:,:,12],deriv_tt,deriv_ee)

    def fisher(deriv,ell,cl,s,theta,fsky):
        ell = ell[:,:,12]
        cl = cl[:,:,12]
        s = np.asarray(s).reshape(1,1)
        theta = np.asarray(theta).reshape(1,1)
        #n is in units of muK-radians --> make sure that it matches with the units of C(l)
        n = np.square(s)*np.exp(ell*(ell+1.0)*np.square(theta)/(8.0*np.log10(2.0)))
        cl_mat = []
        cl_mat.append([cl_tt[0,:,12][2:]+n[0][2:],cl_te[0,:,12][2:]])
        cl_mat.append([cl_te[0,:,12][2:],cl_ee[0,:,12][2:]+n[0][2:]])
        inv = np.linalg.inv(np.reshape(cl_mat,(2,2,2499)).transpose(2,0,1))
        dmat = []
        dmat.append([deriv_tt[:,2:],deriv_te[:,2:]])
        dmat.append([deriv_te[:,2:],deriv_ee[:,2:]]) 
        dmat = np.reshape(dmat,(2,2,3,2499)).transpose(2,3,0,1)
        fish = []
        for i in range(len(cv_floats)):
            for j in range(len(cv_floats)):
                for k in range(len(ell[0,2:])):
                    fish.append(((2*ell[0][k]+1)*fsky/2)*np.trace(inv[k].dot(dmat[i][k].dot(inv[k]).dot(dmat[j][k]))))
        fish = np.reshape(fish,(len(cv_floats),len(cv_floats),len(ell[0][2:])))
        fish = np.sum(fish,axis = 2)
        return fish

    return fisher(deriv,ell,cl_tt,np.pi/270,7*np.pi/10800,0.75)

fisher_matrix = run_fisher(['output','lensing','omega_b','omega_cdm','H0'],['tCl,pCl,lCl','yes',0.02234,0.1189,67.8],[0.00023,0.0022,1.0])
print fisher_matrix
cov = np.linalg.inv(fisher_matrix)
wb = np.sqrt(cov[0][0])
wc = np.sqrt(cov[1][1])
h = np.sqrt(cov[2][2])
print wb,wc,h
