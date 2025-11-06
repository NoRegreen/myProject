# discrete spider monkey optimization algorithm
import copy
import random
import get_influence
import operator_based_lists as obl
from igraph import *

def local_degree_based_replacement(g, meme_base):
    '''
    Based on the current individual, local search creates new meme individuals
    :param g:
    :param meme_base:(meme, meme_inf)
    :return: new_meme
    '''
    new_meme = []
    meme = meme_base[:]
    for memetype in meme:
        neighbors = g.neighbors(memetype)
        nei_and_degree = []
        for nei in neighbors:
            nei_d = g.outdegree(nei)
            nei_and_degree.append((nei, nei_d))

        SN = sorted(nei_and_degree, key=lambda x: x[1], reverse=True)
        for sn in SN:

            if sn[0] not in new_meme:
                new_meme.append(sn[0])
                break
    return new_meme


def select_localLeader_and_globalLeader(g, group_list, p):

    ll_list = []
    all_sm = []
    all_sm_inf = []

    for group in group_list:
        sm_list = []
        sm_inf_list = []
        for sm in group:
            sm_inf, _, _ = get_influence.calInf_byEDV(g, sm, p)
            sm_list.append(sm)
            sm_inf_list.append(sm_inf)
        all_sm.extend(sm_list)
        all_sm_inf.extend(sm_inf_list)
        Qll = sorted(zip(sm_list, sm_inf_list), key=lambda x: x[1], reverse=True)[0]  
        ll_list.append(Qll)

    gl = sorted(zip(all_sm, all_sm_inf), key=lambda x: x[1], reverse=True)[0]  

    return ll_list, gl


def get_searchSpace(g, keep_percent):
    '''
    Reduce the node search space according to the specified proportion of pre-preserved nodes
    :param g: network
    :param keep_percent: Pre-reserved node ratio
    :return: search_space
    '''

    original_searchSpace = []
    # 1. Use LIE to obtain the influence of each node
    node_inf_list = []
    for i in range(g.vcount()):
        original_searchSpace.append(i)
        seed_nodes = [i]
        node_inf, _, _ = get_influence.calInf_byEDV(g, seed_nodes, p=0.01)
        node_inf_list.append(node_inf)
    tuple_list = zip(original_searchSpace, node_inf_list)

    # 2. Sort in descending order of EDV value
    Q = sorted(tuple_list, key=lambda x: x[1], reverse=True)

    # 3. get the search space based on the Pre-reserved node ratio
    length = len(g.vs)

    m_index = int(length * keep_percent)
    selected_Q = Q[:m_index]

    search_space = list(map(lambda x: x[0], selected_Q))

    return search_space

def EDV_based_init(g, k, N, search_space):
    nodes_list = range(g.vcount())
    popu = []
    individuality = search_space[:k]

    for _ in range(N):
        new_individuality = individuality[:]
        for index, _ in enumerate(new_individuality):
            if random.uniform(0, 1) > 0.5:
                updated_search_space = list(set(nodes_list) - set(new_individuality))
                selected_node = random.choice(updated_search_space)
                new_individuality[index] = selected_node
        popu.append(new_individuality)

    return popu



def exe_group(popu, g):
    '''
     Divide the population according to the specified number of groups
    :param popu: population
    :param g: the number of groups
    :return: group_list
    '''

    group_list = [[] for _ in range(g)]

    for i, sm in enumerate(popu):
        index = i % g
        group_list[index].append(sm)
    return group_list


def update_sm_by_ll(g, sm, ll, group, p):
    ran_sm = random.choice(group)
    candidate_nodes = obl.get_candidate_nodes(sm, ll, ran_sm)
    sm_inf, _, _ = get_influence.calInf_byEDV(g, sm, p)

    i = random.randint(0, len(sm) - 1)
    flag = False
    while not flag and candidate_nodes:
        selected_node = random.choice(candidate_nodes)
        new_sm = sm[:]
        new_sm[i] = selected_node
        new_sm_inf, _, _ = get_influence.calInf_byEDV(g, new_sm, p)
        if new_sm_inf > sm_inf:
            sm_inf = new_sm_inf
            sm = new_sm[:]
        else:
            flag = True
        candidate_nodes.remove(selected_node)

    sm = sm[:]
    return sm


def update_sm_by_gl(g, sm, sm_inf, gl, group, p):
    gl_sm = gl[0]

    ran_sm = random.choice(group)
    candidate_nodes = obl.get_candidate_nodes(sm, gl_sm, ran_sm)


    i = random.randint(0, len(sm) - 1)
    flag = False
    while not flag and candidate_nodes:
        selected_node = random.choice(candidate_nodes)
        new_sm = sm[:]
        new_sm[i] = selected_node
        new_sm_inf, _, _ = get_influence.calInf_byEDV(g, new_sm, p)
        if new_sm_inf > sm_inf:
            sm_inf = new_sm_inf
            sm = new_sm[:]
        else:
            flag = True
        candidate_nodes.remove(selected_node)

    sm = copy.deepcopy(sm)
    return sm


def update_sm_by_ll_and_gl(g, sm, ll, gl, p):
    gl_sm = gl[0]
    sm_inf, _, _ = get_influence.calInf_byEDV(g, sm, p)
    candidate_nodes = obl.reverse_get_candidate_nodes(sm, gl_sm, ll)

    length = len(sm)
    for i in range(length):
        for selected_node in candidate_nodes:
            new_sm = sm[:]
            new_sm[i] = selected_node
            new_sm_inf, _, _ = get_influence.calInf_byEDV(g, new_sm, p)
            if new_sm_inf > sm_inf:
                sm_inf = new_sm_inf
                sm = new_sm[:]
                candidate_nodes.remove(selected_node)
                random.shuffle(candidate_nodes)
                break
    sm = copy.deepcopy(sm)
    return sm


def groups_tansferTo_population(group_list):
    new_popu = []
    for group in group_list:
        for sm in group:
            new_popu.append(sm)
    random.shuffle(new_popu)
    return new_popu


def dsmo(g, k, p, I, MG, pr, LLL, GLL, N):
    '''
    dsmo-algorithm
    :param g: social network
    :param k: seed set size
    :param p: dissemination probability
    :param I: the number of iterations
    :param MG: the maximum number of groups
    :param pr: the perturbation rate
    :param LLL: Local Leader Limit
    :param GLL: Global Leader Limit
    :param N: the spider monkey population size
    :return gl : target seed set
    '''

    # step1: Initialization
    # 1.1 Initialize the population
    search_space = get_searchSpace(g,1)  # Reduce the node search space according to the specified proportion of pre-reserved nodes
    popu = EDV_based_init(g, k, N, search_space)

    # 1.2 Measure the fitness of each individual
    sm_inf_list = []
    for sm in popu:
        sm_inf, _, _ = get_influence.calInf_byEDV(g, sm, p)
        sm_inf_list.append(sm_inf)
    Q = sorted(zip(popu, sm_inf_list), key=lambda x: x[1], reverse=True)

    # 1.3 select local leaders and global leader
    group_num = 1  # the number of groups
    group_list = exe_group(popu, group_num)  # Divide population
    ll_list = [Q[0]]
    gl = Q[0]

    ll_count_list = [0 for _ in range(len(group_list))]
    gl_count = 0


    # Step 2: Main Operation
    t = 1
    while t <= I:
        # 2.1 Leadership phase of LL
        for i1, group in enumerate(group_list):
            ll = ll_list[i1][0]
            for j1, sm in enumerate(group):
                if random.uniform(0, 1) >= pr:
                    sm1 = update_sm_by_ll(g, sm, ll, group, p)
                    group[j1] = copy.deepcopy(sm1)
            group_list[i1] = group

        # 2.2 Leadership phase of GL
        for i2, group in enumerate(group_list):
            max_sm_inf = ll_list[i2][1]
            for j2, sm in enumerate(group):
                sm_inf, _, _ = get_influence.calInf_byEDV(g, sm, p)
                sm_pro = (0.9 * sm_inf) / max_sm_inf + 0.1
                if random.uniform(0, 1) <= sm_pro:
                    sm2 = update_sm_by_gl(g, sm, sm_inf, gl, group, p)
                    group[j2] = copy.deepcopy(sm2)
            group_list[i2] = group



        # 2.3 Learning phase of LL
        new_ll_list, new_gl = select_localLeader_and_globalLeader(g, group_list, p)
        for i3, el in enumerate(ll_list):
            if new_ll_list[i3][1] > el[1]:
                ll_list[i3] = (new_ll_list[i3][0], new_ll_list[i3][1])
                ll_count_list[i3] = 0
            else:
                ll_count_list[i3] += 1

        # 2.4 Learning phase of GL
        if new_gl[1] > gl[1]:
            gl = (new_gl[0], new_gl[1])
            gl_count = 0
        else:
            gl_count += 1



        # 2.5 Decision phase of LL
        target = True
        x=None
        y=None

        for i4, group in enumerate(group_list):
            ll1 = ll_list[i4][0]
            if ll_count_list[i4] > LLL:

                ll_count_list[i4] = 0

                for j4, sm in enumerate(group):
                    if target and not set(gl[0]) - set(sm):
                        x=i4
                        y=j4
                        target = False
                        continue
                    if random.uniform(0, 1) >= pr:
                        sm3 = local_degree_based_replacement(g, sm)
                        group[j4] = sm3
                    else:
                        sm4 = update_sm_by_ll_and_gl(g, sm, ll1, gl, p)
                        group[j4] = sm4

            group_list[i4] = group
        if x is not None:
            group_list[x][y]=gl[0]


        # 2.6 Decision phase of GL
        if gl_count > GLL:
            gl_count = 0
            updated_popu = groups_tansferTo_population(group_list)
            if group_num < MG:
                group_num = group_num + 1
                group_list = exe_group(updated_popu, group_num)
            else:
                group_num = 1
                group_list = exe_group(updated_popu, group_num)

            updated_ll_list, _ = select_localLeader_and_globalLeader(g, group_list, p)

            ll_list = copy.deepcopy(updated_ll_list)

            ll_count_list = [0 for _ in range(len(group_list))]
        t += 1

    # Step 3: Return GL as the result
    return gl



if __name__ == '__main__':

    g = Graph(directed=True)# import datasets and construct the graph
    N = 20
    I = 100
    MG = 5
    pr = 0.1
    LLL = 3
    GLL = 5
    p = 0.01
    k=10

    result_gl = dsmo(g, k, p, I, MG, pr, LLL, GLL, N)
