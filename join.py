from operator import itemgetter
import numpy as np

def join(*t):
        d = {} # KEY: -inf (headers) or individual's id
               # VAL: list of values per question (including ID), with Nones for alignment
               # NOTE questions are tagged with the timestep, e.g. '3_xxx' for 'xxx' in FU3
        #Addition phase
        def add_dict(d,l1,offset=0):
                key = l1[0]
                try:
                        d[key] += l1[1:]
       	        except KeyError:
                        try:
                                d[key] = [l1[0]] + [None]*offset + l1[1:]
                        except:
                                print(l1[0],offset,l1[1:],l1)
                                assert False
        maxlen = 1
        for ti in t:
                for r in ti:
                        if r[0] == 'ID':
                                r[0] = -np.inf # to help sorting later
                        add_dict(d,r,offset=maxlen-1)
                maxlen += len(ti[0])-1 # "-1" because the column 'ID' is common to all rows
                #Normalisation phase
                for key in d:
                        d[key] += [None]*(maxlen-len(d[key]))
        #Arrayisation phase
        l = list(d.values())
        l = sorted(l,key=itemgetter(0))
        l[0][0] = 'ID'
        return l
