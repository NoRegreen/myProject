import random
import numpy as np

def get_candidate_nodes(l0,l1,l2):

    l1=list(set(l1)-set(l0))
    l2=list(set(l2)-set(l0))

    length1 = len(l1)
    length2 = len(l2)
    r1 = random.randint(0,length1)
    r2 = random.randint(0, length2)


    select_1=np.random.choice(l1, r1, replace=False)
    select_2=np.random.choice(l2, r2, replace=False)
    select_1=select_1.tolist()
    select_2=select_2.tolist()
    candidate_nodes=select_1+select_2
    candidate_nodes=list(set(candidate_nodes))



    return candidate_nodes

def  reverse_get_candidate_nodes(l0,l1,l2):
    l1 = list(set(l1) - set(l0))

    length1 = len(l1)
    length2 = len(l2)

    r1 = random.randint(0, length1)
    r2 = random.randint(0, length2)

    select_1 = np.random.choice(l1, r1, replace=False)
    select_2 = np.random.choice(l2, r2, replace=False)
    select_1 = select_1.tolist()
    select_2 = select_2.tolist()

    candidate_nodes = set(select_1) - set(select_2)
    candidate_nodes = list(candidate_nodes)

    return candidate_nodes
