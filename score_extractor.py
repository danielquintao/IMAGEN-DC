import re
import numpy as np
def parser():
    txt = open("wp4_text_(simple).txt",'r').read()
    score_re = re.compile("(variable labels |VARIABLE LABELS |VARIABLE LABES |)(\w+|(\w.\w+)) .*?(MEAN|SUM|mean|sum)( |)\(([a-zA-Z0-9 .,_]+)\)")
    match = score_re.findall(txt)
    names = []
    ops = []
    argsl = []
    for m in match:
        name = m[1].lower()
        name2 = re.findall("\w\.(\w+)",name)
        if name2:
            name = name2[0]
        op = m[3].lower()
        args = m[5].lower().replace("\n","")
        limits = re.findall("(.*) to (.*)",args)
        if limits:
            #"To" form
            start = limits[0][0]
            start_parse = re.findall("([a-zA-Z.]+)([0-9]+)",start)
            if len(start_parse) == 1:
                [base,start_nb] = start_parse[0]
            else:
                continue
            base_parse = re.findall("\w\.(\w+)",base)
            if len(base_parse) == 1:
                base = base_parse[0]
            end = limits[0][1]
            end_nb = re.findall("[a-zA-Z.]+([0-9]+)",end)[0]
            args = []
            for i in range(int(start_nb),int(end_nb)+1):
                args.append(base+str(i))
        else:
            #Standard form
            args = re.findall("(\w\.|)([a-zA-Z0-9_]+)",args)
            for i in range(len(args)):
                args[i] = args[i][1]
        names.append(name)
        ops.append(op)
        argsl.append(args)
    return names,ops,argsl

def interpreter(db,name,op,args):
    n_args = db.find(args)
    args_indexs = db.get_index(n_args)
    if op == "sum":
        op = np.sum
    if op == "mean":
        op = np.mean
    return name,op,args_indexs

def compute_score(db):
    names,ops,argsl = parser()
    for i,(name,op,args) in enumerate(zip(names,ops,argsl)):
        print(i,len(names),name,op,args)
        name,op,args_indexs = interpreter(db,name,op,args)
        new_arr = db.tf[:,:,args_indexs]
        new_arr = op(new_arr,axis=2)
        new_arr = np.reshape(new_arr,new_arr.shape+(1,))
        db.add_question(name,new_arr)


#Corrections
def correct_surps(db):
    l = ["surps"+str(i)+"_surps" for i in [1,4,7,13,20,23]]
    l = db.get_index(l)
    db.tf[3,:,l] = 5-db.tf[3,:,l]

def correct(db):
    correct_surps(db)

if __name__ == "__main__":
    tf,time,ind,questions = load_db()
    tf,questions= score_extractor(tf,questions)
    #print(questions)
    with open("3darray_scores.pickle","wb") as f:
        pickle.dump([tf,time,ind,questions],f)
