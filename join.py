from operator import itemgetter
import numpy as np

def join(*t):
        d = {}
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
                                r[0] = -np.inf
                        add_dict(d,r,offset=maxlen-1)
                maxlen += len(ti[0])-1
                #Normalisation phase
                for key in d:
                        d[key] += [None]*(maxlen-len(d[key]))
        #Arrayisation phase
        #d[-np.inf] = d['ID'] #Python 3. isn't able to compare str with int
        #del d['ID']
        l = list(d.values())
        #print([i[0] for i in l])
        l = sorted(l,key=itemgetter(0))
        l[0][0] = 'ID'
        #print("\n\n")
        #print([i[0] for i in l])
        #l.insert(0,l[-1])
        #del l[-1]
        return l
"""
t1 = [[0,45,45],
		[1,78,45],
		[2,78,78]]

t2 = [[0,78,78],
		[4,78,78]]

t3 = [[2,89,89],
		[3,25,25]]

t4 = [[3,47,47],
		[4,89,89]]

print(join(t1,t2,t3,t4))
"""
