import database
import pop
import numpy as np
from tools import *
import re

def compute_T(data,p):
    """ Compute T value for data of shape (nb_ind,nb_vol + p) with p the number of parameters of the model"""
    lT = []
    for ind in range(data.shape[2]-p): #for each region compute the T value
        #get volume for the currently investigated area
        vol = data[0,:,ind]

        #matrix X (cf poly)
        x = np.concatenate([np.ones((data.shape[1],1)),data[0,:,-p:]],axis=1)
        
        #Compute T value (cf poly)
        xx = np.dot(x.T,x)
        xx1 = np.linalg.inv(xx)
        beta = np.dot(np.dot(xx1,x.T),vol)
        sig = np.sum((vol - np.dot(x,beta))**2)
        sig2 = sig/(len(vol)-x.shape[1]-1)
        T = beta[p]/((sig2*xx1[p,p])**0.5)
        #Add T value to the list as well as all parameters of the model
        lT.append((T,*beta,sig))
    #lT2 = [lT[i] for i in range(len(lT)) if not(np.isnan(lT[i][0]))]
    return lT

# ---------------
#
#  IMAGEN DB PART
#
# ---------------

#Load DB
db = database.Database()
db.load_from_pickle("db.p")
#Add population
pop.add_depressedfu3(db)
pop.add_dcmadepfu3(db)
add_regions(db)
#Get questions
qgm = [q for q in db.q if re.fullmatch('.*_gmtrans',q)]
#Remove some regions
qgm.remove("tiv_gmtrans") #is a covariable
qgm.remove("loc_gmtrans") #0 column (too small)
qgm.remove("roc_gmtrans") #same
qgm.remove("linflatven_gmtrans") #same
qgm.remove("rinflatven_gmtrans") #same
qgm.remove("names_gmtrans") #useless
qstudy = '_dcmadepfu3'
qpart = ['gender_dawbastd','tiv_trans',qstudy] #len 3

#Extract questions and remove missing data
dbb = db[[3],:,:].get_questions(qgm+qpart)
dbb.clean()

# ---------------
#
#   STATS PART
#
# ---------------

#Preprocess covariables
p = len(qpart)
data = dbb.tf #get full array from dbof shape (nb_ind,nb_vol+p)

data[0,:,:-p] = np.log(data[0,:,:-p]) #log vol
data[0,:,-3] = 2-data[0,:,-3] #Gender was initialy 1 for boys and 2 for girls
data[0,:,-2] = np.log(data[0,:,-2]) #log tiv

#Compute T values
tv = np.array(compute_T(data,p)) #Get T values and parameters for full model
tvr = np.array(compute_T(data[:,:,:-1],p-1)) #Get T values and parameters for reduced model (without last variable wich is the one for depressed population. Thus the T value isn't very interesting but we will use sigma (last parameter of the model).

#Add regions name and sort by T value for full model
print(len(qgm),tv.shape)
rtv = list(zip(qgm,*tv.T))
rtv = sorted(rtv,key=itemgetter(1))

#Add regions name and sort by T value for reduced model
rtvr = list(zip(qgm,*tvr.T))
rtvr = sorted(rtvr,key=itemgetter(1))

#Save files
save(rtvr,qstudy+'_rtvr.xlsx')
save(rtv,qstudy+'_rtv.xlsx')

#Compute Fisher (cf poly)
f = (tvr[:,-1]-tv[:,-1])/tv[:,-1]*(tv.shape[0]-p-1)

#Add regions name and sort by T value for Fisher
rf = list(zip(qgm,f))
rf = sorted(rf,key=itemgetter(1))

#Save file
save(rf,qstudy+'_rf.xlsx')
