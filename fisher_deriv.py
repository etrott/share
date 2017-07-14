from classy import Class
import numpy as np
import matplotlib.pyplot as plt
import subprocess

def run_fisher(param,mass,cv,delta,num,deg,run = 'False'):
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

    ell = np.transpose(ell,(0,2,1))
    cl_tt = np.transpose(cl_tt,(0,2,1))

    def poly_fit(x,y,deg):
        poly = []
        for i in range(len(y)):
            for j in range(len(y[i])):
                poly.append(np.polyfit(x[i],y[i][j],deg))
        poly = np.reshape(poly,(len(y),len(y[0]),deg+1))
        return poly

    print np.shape(poly_fit(span,cl_tt,deg))

#next step -- figure out a generalized way (i.e. for any degree fit) to convert the coefficients into derivatives

"""
    def fisher(deriv):
        matrix = []
        for i in range(len(deriv)):
            for j in range(len(deriv)):
                matrix.append(np.sum(deriv[i]*deriv[j]))
        matrix = np.reshape(matrix,(len(num_cv),len(num_cv)))
        return matrix
    return fisher(deriv)
"""

fisher_matrix = run_fisher(['output','lensing','Omega_b','Omega_cdm','H0'],[1.0],['tCl,pCl,lCl','yes',0.02234,0.1189,67.8],[0.00023,0.0022,1.0],25,3,run = 'False')
