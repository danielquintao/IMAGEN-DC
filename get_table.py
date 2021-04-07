from openpyxl import load_workbook,Workbook
import re
import numpy as np
def get_table(f):
        wb = load_workbook(f)
        s = wb.active
        def iter_rows(s):
                empty_space = re.compile('\\s+')
                for row in s.iter_rows():
                        if not(row[0].value is None):
                                if isinstance(row[0].value, str) and empty_space.fullmatch(row[0].value):
                                        continue
                                yield [cell.value if not(cell.value is None) else np.inf for cell in row]
        #out = [[c.value for c in l] for l in s.rows]
        out = list(iter_rows(s))
        #Post process 0 : Change [0][0] to ID
        out[0][0] = "ID"
        #Post process 1 : remove doubles (duplicated lines -> happens in some files)
        def fusion(l1,l2):
                l = l1
                for i in range(len(l)):
                        if l[i] is None:
                                l[i] = l2[i]
                return l
        to_del = []
        for i in range(len(out)-1):
                if out[i][0] == out[i+1][0]:
                        out[i] = fusion(out[i],out[i+1])
                        to_del += [i+1]
        to_del.sort(reverse=True)
        for i in to_del:
                del out[i]
        #Post process 2 : add timestep and questionnaire name to labels and cut everything after the first space
        l = re.split("/",f)
        l = re.split("\.",l[1])                
        l2 = re.split('-',l[0])
        if len(l) != 2:
                assert False #File name doesn't match the format [questionnaire_name]-(bas|fu1|fu2|fu3)
        time = ['bas','fu1','fu2','fu3'].index(l2[1])
        for i in range(len(out[0])):
                if i != 0: #Don't change ID
                        name = str(out[0][i])
                        l = re.split('\s',name)
                        out[0][i] = str(time)+"_"+l[0]+"_"+l2[0]
        print("loaded table {} : ({},{}) timestep {}".format(f,len(out),len(out[0]),time))
        return out
                
def find_matching_columns(t):
        def match_form(n):
                return n[2:].lower(),int(n[0])
        #Get matching names
        names = t[0]
        d_names = {} #Match dictionary
        match_names = [] #Names matched with others
        max_dim = 0 #Maximum dimension of
        for index,n in enumerate(names):
                if index != 0:
                        m_form,time = match_form(n)
                else:
                        m_form,time = n,-1
                try:
                        d_names[m_form].append((index,time))
                        match_names.append(n)
                        max_dim = max(max_dim,len(d_names[m_form]))
                except KeyError:
                        d_names[m_form] = [(index,time)]
        #print(d_names)
        #print(match_names,len(match_names))
        #Add dimensions
        nb_timesteps = 4
        nb_ind = len(t)
        nb_questions = len(d_names)
        questions = sorted(list(d_names))
        tf = np.full((nb_timesteps,nb_ind,nb_questions),np.inf)
        conv = {"t":1,"f":0,"C":1,"fr":0,"en":1,"de":2,"PARIS":0,"NOTTINGHAM":1,
                "BERLIN":2,"HAMBURG":3,"DESDEN":4,"DUBLIN":5,"MANNHEIM":6,"LONDON":7,'Y':1,'N':0,'female':1,'male':0}
        #Add marks for QC
        for i,c in enumerate(["E","D","C","B","A"]):
                for j,add in enumerate(["-","","+"]):
                        conv[c+add] = i*3+j
        #Sometimes there are space after those patterns
        l = list(conv.keys())
        for k in l:
                conv[k+' '] = conv[k]
        for index_ind in range(1,nb_ind):
                for index_q in range(nb_questions):
                        q_name = questions[index_q]
                        indexs_tab = d_names[q_name]
                        for index,time in indexs_tab:
                                value = t[index_ind][index]
                                if q_name=="abs_csf_trans" and index_ind==2254:
                                        print(q_name,value,type(value))
                                if value is None:
                                        value = np.inf
                                try:
                                        tf[time,index_ind,index_q] = value
                                except ValueError:
                                        #Try to convert it
                                        try:
                                                value = int(value)
                                                tf[time,index_ind,index_q] = value
                                        except ValueError:
                                                try:
                                                        value = conv[value]
                                                        tf[time,index_ind,index_q] = value
                                                except KeyError:
                                                        print("error : '{}' not understood".format(value))
                                                        value = np.nan #Error value
                                                        tf[time,index_ind,index_q] = value
        #tf = np.delete(tf,0,axis=2)
        tf = np.delete(tf,0,axis=1)
        print("-",tf[:,0,0])
        print(tf.shape)
        timesteps = ["bas","fu1","fu2","fu3"]
        ind = np.array(t)[:,0]
        ind = np.delete(ind,0)
        print(tf)
        print(questions)
        print(timesteps)
        print(ind)
        return tf,timesteps,ind,questions
