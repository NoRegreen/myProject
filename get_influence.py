
import numpy as np

def calInf_byEDV(g,seed_nodes,p):
    '''
    calculate the EDV value of the given seed set
    :param g: network
    :param seed_nodes: the given seed set
    :param p: dissemination probability
    :return: the EDV value
    '''
    # get all neighbors of the seed set
    neighbors=set()
    for seed_node in seed_nodes:
        out_neighbors=g.successors(seed_node)
        neighbors.update(out_neighbors)
    neighbors=list(neighbors-set(seed_nodes))

    k=len(seed_nodes)
    if len(neighbors)==0:
        return k,0,neighbors
    count_list=[]


    for nei in neighbors:
        inter_set=set(seed_nodes).intersection(set(g.predecessors(nei)))
        count_list.append(len(inter_set))


    count_array=np.array(count_list)
    tmp=1-pow(1-p,count_array)
    first_inf=np.sum(tmp)
    edv_inf=k+first_inf
    return edv_inf,first_inf,neighbors




