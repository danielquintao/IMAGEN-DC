import numpy as np

def add_pop(db,ind,name):
    arr = np.zeros((*db.tf.shape[:2],1))
    arr[:,ind,:] = 1
    db.add_question(name,arr)

#Depressive

def add_dcmadepfu3(db):
    ind = np.where(db.get_question("centre_dcmadep").tf[3,:,0]!=np.inf)[0]
    add_pop(db,ind,'_dcmadepfu3')

def add_depressedfu3(db):
    ind = np.where(db.get_question("centre_diag").tf[3,:,0]!=np.inf)[0]
    add_pop(db,ind,'_depressedfu3')

def add_depressedfu2(db):
    ind = np.where(db.get_question("centre_diag").tf[2,:,0]!=np.inf)[0]
    add_pop(db,ind,'_depressedfu2')

def add_maintainer(db):
    dtable = db.get_question("_depressed").tf[[0,2,3],:,:]
    dd = []
    dn = []
    for i in range(3):
        dd.append(np.where(dtable[i])[0])
        dn.append(np.where(np.logical_not(dtable[i]))[0])
    dd2index = np.intersect1d(dn[0],np.intersect1d(dd[1],dd[2]))
    pop = np.zeros((4,db.tf.shape[1]))
    pop[:,dd2index] = 1
    pop = np.reshape(pop,(4,-1,1))
    add_pop(db,dd2index,"_maintainer")

#Alcool

def add_alcoolfu3(db):
    ind = np.where(db.get_question("audit_abuse_flag_audit").tf[3,:,0 ]==1)
    add_pop(db,ind,'_alcool')
