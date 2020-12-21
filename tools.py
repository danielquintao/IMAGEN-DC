import numpy as np
from operator import itemgetter, attrgetter
import matplotlib.pyplot as plt
import tensorflow as tf
from openpyxl import Workbook
#Usefull
def save(data,filename):
    data = np.array(data)
    wb = Workbook()
    s = wb.active
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            s.cell(column=j+1,row=i+1).value = data[i,j]
    wb.save(filename)

def add_regions(db):
    g1 = ['bascbr+fobbr','posorbgy','antorbgy','inffroorbgy','latorbgy']
    g2 = ['midfrogy','supmedfrogy','supfrogy']
    g3 = ['medfrocbr','medorbgy','recgy','sca']
    g4 = ['medpocgy','medprcgy','prcgy','pocgy','medpocgy','cal+cbr']
    g5 = ['inffrogy','inffroorbgy','inffroanggy']
    d = {'orb':g1,'mid-supfro':g2,'med-rec':g3,'prc-poc':g4,'inffro':g5}
    for k in d:
        for side in ['l','r']:
            for t in ["trans","long"]:
                regions = [side+i+'_gm'+t for i in d[k]]
                data = db.get_questions(regions).tf
                data2 = np.sum(data,axis=2)
                #print(data2)
                #print(data2.shape)
                data = np.reshape(data2,data.shape[:-1]+(1,))
                #print(data)
                #assert False
                db.add_question(side+k+'_gm'+t,data)
    
def plot_side_question_pop(db,question,pop):
    """ Plot the variables question (str) with 2 colors according to the value of the population pop (str) """
    db2 = db.get_questions([question,pop])
    db2.clean()
    print("plot",db2.tf.shape)
    ind_pop = np.where(db2.tf[0,:,1]==1)[0]
    ind_npop = np.where(db2.tf[0,:,1]==0)[0]
    print("pop",len(ind_pop))
    print("npop",len(ind_npop))
    for i in ind_pop:
        plt.plot([i]*db2.tf.shape[0],db2.tf[:,i,0],color='red',marker='.')
    mean = db2.tf[:,ind_pop,0].mean()
    plt.plot([0,max(max(ind_pop),max(ind_npop))],[mean,mean],color='red')
    for i in ind_npop:
        plt.plot([i]*db2.tf.shape[0],db2.tf[:,i,0],color='blue',marker='.',alpha=np.log(len(ind_npop))*10/len(ind_npop))
    mean = db2.tf[:,ind_npop,0].mean()
    plt.plot([0,max(max(ind_pop),max(ind_npop))],[mean,mean],color='blue')
    plt.show()
