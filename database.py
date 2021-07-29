from openpyxl import load_workbook,Workbook
import re
import numpy as np
import pickle
from get_table import *
from join import *
import os
from score_extractor import *
class Loadable:
    """ Class loadable from files (pickle, xlsx, ...) """
    def __init__(self):
        """ Initialize attributes that will be loaded """
        self.tf = None
        self.time = None
        self.ind = None
        self.q = None
    def paste(self,obj):
        """ Load initialized attributes in specific object """
        obj.tf = np.copy(self.tf)
        obj.time = np.copy(self.time)
        obj.ind = np.copy(self.ind)
        obj.q = np.copy(self.q)
    def load_from_pickle(self,fname):
        """ Load attributes from a given pickle file """
        #Load data
        with open(fname,'rb') as f:
            out = pickle.load(f,encoding='latin1')
        [self.tf,self.time,self.ind,self.q] = out
        #Correct types
        self.tf = np.array(self.tf).astype(np.float32)
        self.ind = np.array(self.ind).astype(np.int32)
        self.q = np.array(self.q).astype(str)
        self.time = np.array(self.time).astype(str)
        #Print the name of the loaded database
        print("DB loaded {}".format(fname))
        
    def load_from_xlsx(self,fnames,compute_scores=False):
        """ Load attributes from a given list of xlsx files """
        #Load tables one by one
        lt = []
        for f in fnames:
            lt.append(get_table(f))
        #Join tables
        t = join(*lt)
        #Align columns
        out = find_matching_columns(t)
        #Store data in attributes
        [self.tf,self.time,self.ind,self.q] = out

    def load_from_DB_folder(self,compute_scores=False):
        """ Build the db from all xslx and xslm files in DB/ folder """
        ld = os.listdir('DB/')
        ld = ['DB/'+i for i in ld if i[-5:] ==".xlsx" or i[-5:] == ".xlsm"]
        self.load_from_xlsx(ld,compute_scores=compute_scores) # this calls the homonymous function of the class Database (which inherits from Loadable)
        
    def save(self,fname):
        """ Save the database in a pickle file """
        #Save the database
        with open(fname,'wb') as f:
            pickle.dump([self.tf,self.time,self.ind,self.q],f)
        #Print the name of saved database
        print("DB saved {}".format(fname))

class Indexable:
    """ Structure that uses a table between indexs and labels. It makes it possible to ask for a specific column in a database using its name instead of its index """
    def __init__(self):
        """ Initialize a dictionnary to store links between names and indexs """
        self.question_dict = {}
    def reset(self):
        self.question_dict = {}
    def compute_indexs(self,q):
        """ Computes indexs for a list of labels : [l1,l2,l3,l4,...,ln]. l1 will point toward index 0, l2 to index 1, ... , ln to index n-1. """
        for i,lbl in enumerate(q):
            self.add_index(lbl,i)
    def add_index(self,l,i):
        """ Add an index to the dictionnary : label l points toward index i """
        self.question_dict[l] = i
    def remove_index(self,name):
        del self.question_dict[name]
    def get_index(self,lbl):
        """ Returns the index associated to the label lbl. If lbl is a list it will return the list of corresponding indexs : lbl = [l1,l2,...,ln] it will return [get_index(l1),get_index(l2),...,get_index(ln)] : this function is recursive on lists. """
        if isinstance(lbl,list):
                l = []
                for ll in lbl:
                        l.append(self.get_index(ll))
                return l
        return self.question_dict[lbl]

class UnknownPrefix(Exception):
    pass
class Searchable:
    """ Structure that makes it possible to search for all labels starting by a prefix. It's especially usefull when you want to use a Tab similar fonctionality that complete automatically your query. This way you don't need to know the exact name of questions in the database but only how it starts. Ex : for neoffi1 question just tip search_for("neoffi1") and it will return "neoffi1_neo" which is the real column name for neoffi1 in the database """
    def __init__(self):
        """ Initialize the structure (tree)"""
        self.lnames = {}
    def reset(self):
        self.lnames = {}
    def compute_names(self,names):
        """ Add a list of names in the structure /!\ don't use names with a '$' inside or the algorithm won't work!"""
        for name in names:
            self.add_name(name)
    def add_name(self,q):
        """ Add a specific name in the structure /!\ don't use names with a '$' inside or the algorithm won't work!"""
        d = self.lnames
        for s in q:
            try:
                d = d[s]
            except KeyError:
                d[s] = {}
                d = d[s]
        d["$"] = {} #'$' means the end of a word
    def remove_name(self,name):
        d = self.lnames
        prev = []
        for s in name+"$":
            try:
                prev.append((d,s))
                d = d[s]
            except KeyError:
                print(name,s,d.keys())
                raise UnknownPrefix #Unknown prefix
        prev.reverse()
        for i in range(1,len(prev)):
            (d,s) = prev[i]
            (d1,s1) = prev[i-1]
            if len(d.keys()) == 0:
                del d1[s1]
            else:
                break
    def get_name(self,name):
        """ Returns a list of names that have been inserted in the structure having the prefix [name]. If nobody matches it will raise a UnknownPrefix error"""
        d = self.lnames
        #Consumes the prefix to get the corresponding subtree
        for s in name:
            try:
                d = d[s]
            except KeyError:
                print(name,s,d.keys())
                raise UnknownPrefix #Unknown prefix
        #Travels trough the subtree and returns each word with this prefix
        l = []
        def _iter(d,_s):
            try:
                d["$"] #'$' means the end of a word
                return [_s]
            except KeyError:
                pass
            ls = []
            for k in d:
                ls += _iter(d[k],_s+k)
            return ls
        return _iter(d,name)
    
    def search_for(self,name):
        """ Alias for get_name """
        if isinstance(name,list):
            return [self.get_name(n) for n in name]
        return self.get_name(name)

    def find_all(self,name):
        """ Alias for search_for """
        return self.search_for(name)

    def find(self,name):
        """ Complete the prefix with the first question in lexicographic order in the DB """
        lnames = self.find_all(name)
        lnames = sorted(lnames)
        return lnames[0]

class Database(Loadable,Indexable,Searchable):
    """ Database object. Inherits from Loadable,Indexable and Searchable. It handles use of the database such as projections and cleaning operations """
    def __init__(self):
        """ Initialization of all inherited classes """
        #Init sub classes
        Loadable.__init__(self)
        Indexable.__init__(self)
        Searchable.__init__(self)
        
    def load_from_pickle(self,fname):
        """ Overload of Loadable.load_from_pickle to add questions to Indexable and Searchable structures """
        Loadable.load_from_pickle(self,fname)
        self.compute_indexs(self.q)
        self.compute_names(self.q)
        
    def load_from_xlsx(self,fnames,compute_scores=False): 
        """ Overload of Loadable.load_from_xlsx to add questions to Indexable and Searchable structures """
        Loadable.load_from_xlsx(self,fnames,compute_scores=compute_scores)
        self.compute_indexs(self.q)
        self.compute_names(self.q)
        #Correct few questions due to errors in the database (especially fu3
        # correct(self) # -- already called from compile.py
        #Computes scores
        if compute_scores:
            compute_score(self)
        
    def clean(self,hard_t=True,hard_q=True):
        """ Clean the database which means it will remove people who haven't answered to them.
        1st step : hard_t=True means it will remove everyone that haven't answered to questions at all timesteps (where hard=False keeps those who have answered to at least one). 
        2nd step : hard_q=True remove everyone who haven't answered to all questions among survivors from first step (where hard=False keeps those who have answered to at least one of those questions)"""
        #Only keeps people who have answered to all questions
        if hard_t:
            clean_array = np.any(np.logical_or(self.tf==np.inf,self.tf==-np.inf),axis=0)
        else:
            clean_array = np.all(np.logical_or(self.tf==np.inf,self.tf==-np.inf),axis=0)
        if hard_q:
            clean_array = np.any(clean_array,axis=1)
        else:
            clean_array = np.all(clean_array,axis=1)
        ind = np.where(clean_array!=True)[0]
        self.tf = self.tf[:,ind]
        self.ind = self.ind[ind]
    def add_question(self,name,t):
        """ Add a question column (usefull to add scores) """
        self.tf = np.concatenate([self.tf,t],axis=2)
        self.q = np.append(self.q,name)
        self.add_name(name)
        self.add_index(name,self.q.shape[0]-1)
    def remove_question(self,name):
        index = self.get_index(name)
        mask = np.ones(self.q.shape,dtype=np.bool)
        mask[index] = False
        self.tf = self.tf[:,:,mask]
        self.q = self.q[mask]
        self.remove_name(name)
        self.remove_index(name)
    def copy(self):
        """ Return a copy of the database """
        db = Database()
        Loadable.paste(self,db)
        db.compute_indexs(db.q) # not needed if we apply __getitem__ (db[...]) but necessary otherwise
        db.compute_names(db.q) # not needed if we apply __getitem__ (db[...]) but necessary otherwise
        return db
    def __getitem__(self,indexs):
        """ Makes it possible to index the database as it is possible with numpy arrays. However be carefull each time you do this it copies the database """
        (time,ind,q) = indexs
        db = Database()#self.copy()
        db.tf = self.tf[time,ind,q]
        db.time = self.time[time]
        db.ind = self.ind[ind]
        db.q = self.q[q]
        db.compute_indexs(db.q)
        db.compute_names(db.q)
        return db
    #Usefull methods
    def get_questions(self,ql):
        """ Project on one or several questions. ql can be a str or a list of str. It returns a Database object with shape (self.time.shape,self.ind.shape,ql.shape) if ql is a list else (self.time.shape,self.ind.shape,1). Carefull it copies the database. """
        if isinstance(ql,str):
            ql = [ql]
        q_inds = self.get_index(ql)
        return self.copy()[:,:,q_inds]
    def get_question(self,q):
        """ Alias for get_questions """
        return self.get_questions(q)
    def get_ind(self,ind_mask):
        """ Projects on a list or a mask of individuals (carefull it copies the database"""
        db1 = self.copy()[:,ind_mask,:]
        return db1
    #Analysis methods
    def covar(self,q1,q2,return_nb=False):
        dbb = self.get_questions([q1,q2])
        dbb.clean()
        if dbb.tf.shape[1] == 0:
            return -np.inf,0
        max0 = np.max(dbb.tf[:,:,0])
        min0 = np.min(dbb.tf[:,:,0])
        dbb.tf[:,:,0] = (dbb.tf[:,:,0]-min0)/(max0-min0)
        max1 = np.max(dbb.tf[:,:,1])
        min1 = np.min(dbb.tf[:,:,1])
        dbb.tf[:,:,1] = (dbb.tf[:,:,1]-min1)/(max1-min1)
        t1 = (dbb.tf[:,:,0]-np.mean(dbb.tf[:,:,0],axis=1)[:,np.newaxis])
        t2 = (dbb.tf[:,:,1]-np.mean(dbb.tf[:,:,1],axis=1)[:,np.newaxis])
        if return_nb:
            return np.mean(t1*t2,axis=1),dbb.tf.shape[1]
        return np.mean(t1*t2,axis=1)
    
    def correl(self,q1,q2,return_nb=False):
        dbb = self.get_questions([q1,q2])
        dbb.clean()
        if dbb.tf.shape[1] == 0:
            if return_nb:
                return np.nan,0
            return np.nan
        mean = np.mean(dbb.tf,axis=1)[:,np.newaxis,:]
        var = np.mean((dbb.tf-mean)**2,axis=1)[:,np.newaxis,:]
        out = (dbb.tf-mean)/(var**0.5)
        if return_nb:
            return np.mean(out[:,:,0]*out[:,:,1],axis=1),dbb.tf.shape[1]
        return np.mean(out[:,:,0]*out[:,:,1],axis=1)
        

if __name__=='__main__':
    #Load DB
    db = Database()
    db.load_from_DB_folder() # db.load_from_pickle("db.p")
    print("shape",db.tf.shape)
    print("timesteps : ",db.time)
    print("ind : ",db.ind)
    print("first 5 questions :",db.q[:5],"nb questions : ",db.q.shape)

    #Usefull methods :
    
    #Projections
    db2 = db.get_question("lacc_gmtrans") #It will return a new database (be carefull it duplicates internal arrays !) with only one question
    print("projection shape",db2.tf.shape)
    print("projection timesteps : ",db2.time)
    print("projection ind : ",db2.ind)
    print("projection questions : ",db2.q)
    db2.clean() #Will remove people with missing data
    print("clean projection shape",db2.tf.shape)
    print("clean projection timesteps : ",db2.time)
    print("clean projection ind : ",db2.ind)
    print("clean projection questions : ",db2.q)
    
    db3 = db.get_questions(['lacc_gmtrans','lacc_long726s']) #You can also ask for several questions
    print("projection2 shape",db3.tf.shape)
    db3.clean()
    print("clean project2 shape",db3.tf.shape)

    #Get_index
    ind = db.get_index("lacc_gmtrans") #Returns index of the question
    print("get_index",ind)
    inds = db.get_index(["lacc_gmtrans","lacc_long726s"]) #Returns indexs of questions
    print("get_index",inds)

    #SLicing
    db4 = db[[0,1],15:28,:] #You can slice databases
    print("slicing",db4.tf.shape) #Be carefull it also duplicates internal arrays !

    #Populations
    import pop
    pop.add_depressedfu3(db) #Add a column with 0s and 1s to flag depressed people at fu3
    print("first flags for depressed people",db.get_question('_depressedfu3').tf[0,:40,0])
