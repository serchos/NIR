from .Metrics_1 import MetricL1, MetricEuclid, MetricChebyshev, MetricSquareEuclid, MetricMinkowskiWithPow5, MetricUser
from config.db import get_db
from modules.OntologyMethods import getNodeKidsList
import networkx as nx



Fres, Ftemp = [], []
pairs_list = []
checked_nodes_list = []


#совпадение по род классам
def like(A, B):
    for a in list(A.ancestors()):
        for b in list(B.ancestors()):
            if a.name == b.name:
                return True
    return False


#------------------------------------------------------------------------------------------------------------
#
#------------------------------------------------------------------------------------------------------------
def Pairs(Q, C, CF1, CF2):
    i = 0
    F = []
    Ftemp = []
    checked_Q_list = []
    LSj = []
    flag = False
    
    Q_subclasses = list(Q.subclasses())
    С_subclasses = list(C.subclasses())
    
    while (len(checked_Q_list) != len(Q_subclasses)):
        Qi = Q_subclasses[i]

        for j in range(len(С_subclasses)):

            if (С_subclasses[j].name == Qi.name):
                Fj = (Qi.name, С_subclasses[j].name)
                Frec, LSjrec = Pairs(Qi, С_subclasses[j], CF1, CF2)
                if (Frec != []):
                    Ftemp = [Fj]
                    LSjtemp = [CF1]
                    Ftemp.extend(Frec)
                    LSjtemp.extend(LSjrec)
                else:
                    Ftemp = Fj
                    LSjtemp = CF1
                flag = True
                break
        if not flag:
            for j in range(len(С_subclasses)):
                if (like(Qi, С_subclasses[j])):
                    Fj = (Qi.name, С_subclasses[j].name)
                    Frec, LSjrec = Pairs(Qi, С_subclasses[j], CF1, CF2)

                    if (Frec != []):
                        Ftemp = [Fj]
                        LSjtemp = [CF2]
                        Ftemp.extend(Frec)
                        LSjtemp.extend(LSjrec)
                    else:
                        Ftemp = Fj
                        LSjtemp = CF2
        checked_Q_list.append(Qi)
        i += 1

        if (isinstance(Ftemp, list)):
            F.extend(Ftemp)
            LSj.extend(LSjtemp)
        elif (Ftemp not in F):
            F.append(Ftemp)
            LSj.append(LSjtemp)

    return F, LSj
    
    
def do_pairs_and_score_list(Q, C, CF1, CF2):
    score = 0
    F, LSj = Pairs(Q, C, CF1, CF2)
    for elem in LSj:
        score += elem
    sorted_pair_matches_list, sorted_score_list = sort_pair_matches_list(Q, C, CF1, CF2)
    if F not in sorted_pair_matches_list:
        sorted_pair_matches_list.insert(0, F)
        sorted_score_list.insert(0, score)

    return sorted_pair_matches_list, sorted_score_list
    
    
def count_LS_max(Q, CF1):
    LS_max = 0

    for node in list(Q.descendants()):
        if (node.name != "situation"):
            LS_max += CF1

    return LS_max



def do_perent_child_list(Q):
    perent_child_list = []

    for child in list(Q.subclasses()):
        perent_child_list.append((Q.name, child.name))

        if (list(child.subclasses()) != []):
            perent_child_list.extend(do_perent_child_list(child))

    return perent_child_list


def do_sit_and_prec_perent_child_list(Q, C):
    sit_perent_child_list = do_perent_child_list(Q)
    prec_perent_child_list = do_perent_child_list(C)
  
    return sit_perent_child_list, prec_perent_child_list


def check_elem_of_pair_in_list(list_of_pairs, elem_num, elem):

    for pair in list_of_pairs:
        if pair[elem_num] == elem:
            return True    
    return False


def do_pairs_sit_prec_without_shift(sit_perent_child_list, prec_perent_child_list, CF1, CF2):
    answer_vert_pairs_list = []
    LSj = 0

    for sit_perent_child_pair in sit_perent_child_list:
        for prec_perent_child_pair in prec_perent_child_list:
            if (sit_perent_child_pair[1] == prec_perent_child_pair[1]  and (not check_elem_of_pair_in_list(answer_vert_pairs_list, 0, sit_perent_child_pair[1])) and (not check_elem_of_pair_in_list(answer_vert_pairs_list, 1, prec_perent_child_pair[1]))):
                answer_vert_pairs_list.append((sit_perent_child_pair[1], prec_perent_child_pair[1]))
                LSj += CF1
            elif (sit_perent_child_pair[0] == prec_perent_child_pair[0] and (not check_elem_of_pair_in_list(answer_vert_pairs_list, 0, sit_perent_child_pair[1])) and (not check_elem_of_pair_in_list(answer_vert_pairs_list, 1, prec_perent_child_pair[1]))):
                answer_vert_pairs_list.append((sit_perent_child_pair[1], prec_perent_child_pair[1]))
                LSj += CF2

    return answer_vert_pairs_list, LSj

def do_pair_matches_list(Q, C, CF1, CF2):
    pair_matches_list, answer_score_list = [], []
    sit_perent_child_list, prec_perent_child_list = do_sit_and_prec_perent_child_list(Q, C)

    for i in range(len(sit_perent_child_list)):
         for j in range(len(prec_perent_child_list)):
            answer_vert_pairs_list, LSj = do_pairs_sit_prec_without_shift(sit_perent_child_list, prec_perent_child_list, CF1, CF2)
            pair_matches_list.append(answer_vert_pairs_list)
            answer_score_list.append(LSj)
            prec_perent_child_list = prec_perent_child_list[1:] + prec_perent_child_list[:1]

         sit_perent_child_list = sit_perent_child_list[1:] + sit_perent_child_list[:1]

    return pair_matches_list, answer_score_list
    
    
def sort_pair_matches_list(Q, C, CF1, CF2):

    sorted_pair_matches_list, sorted_score_list = [], []
    i = 0
    pair_matches_list, answer_score_list = do_pair_matches_list(Q, C, CF1, CF2)
    len_pair_matches_list = len(pair_matches_list)

    for lst in pair_matches_list:
        lst.sort()

    for lst, score in zip(pair_matches_list, answer_score_list):
        temp_list = pair_matches_list[i + 1:]
        if ((i + 1 < len_pair_matches_list) and (lst not in temp_list)):
            sorted_pair_matches_list.append(lst)
            sorted_score_list.append(score)
        elif ((i + 1 == len_pair_matches_list) and (lst not in sorted_pair_matches_list)):
            sorted_pair_matches_list.append(lst)
            sorted_score_list.append(score)
        i += 1

    return sorted_pair_matches_list, sorted_score_list
    
    # def count_number_of_case_nodes(Q):
    # number_of_nodes = len(getNodeKidsList(Q))
    
    # return number_of_nodes

# def isomorf_g(B, A):
    # GM = nx.algorithms.isomorphism.GraphMatcher(B,A)
    # for subgraph in GM.subgraph_isomorphisms_iter():
        # print(subgraph)

# def dekartMul(A, B):
    # result = []
    # if A == []:
        # return B
    # elif B == []:
        # return A
    # print('A', A)
    # print('B', B)
    # for a in A:
        # for b in B:
            # result.append([a, b])
    
    # if (len(A) == 1 and len(B) == 1):
        # return result[0]

    # return result
    
# def Pairs1(Q, C, O):
    # Step 1
    # checked_nodes_list = []
    # i =- 1
    # Fres = []
    # Ftemp = []
    # print("Pairs start with Q name: ", Q.name ,  " C name: ", C.name)
    # Q_Conc_list = list(Q.subclasses()) 
    # Q_Conc_Count = len(Q_Conc_list)
    # Step 2
    # while (Q_Conc_Count > len(checked_nodes_list)):
        # i += 1
        # print("i: ", i)
        # Qi = Q_Conc_list[i]
        # print("Qi name:", Qi.name)
        # Step 3
        # Fj = ();
        # for Cj in list(C.subclasses()):
            # if (Cj.name == Qi.name):
                # Fj = [(Qi.name, Cj.name)]
                # Frec = Pairs(Qi,Cj,O)
                # Ftemp = dekartMul(Frec, Fj)
                # Ftemp.append(dekartMul(Frec, Fj))
                # print("Ftemp:", Ftemp)
                # break
            # elif (like(Qi, Cj)):
                # Fj = [(Qi.name, Cj.name)]
                # Frec = Pairs(Qi,Cj,O)
                # Ftemp.append(dekartMul(Frec, Fj))
                # print("Ftemp extend like:", Ftemp) 
                # Fres.append(Ftemp)
                # Ftemp = []
        # if (Ftemp != []):
            # print("Ftemp extentd end:", Ftemp) 
            # Fres.extend(Ftemp)
        # checked_nodes_list.append(Q_Conc_list[i])
        
    # return Fres


# def Pairs(Q, C, O):
    # global checked_nodes_list
    # vertex_count = len(list(O.descendants())) - 1
    
    # Fres, Ftemp = [], []

    # for qi in list(Q.subclasses()):      
        # for cj in list(C.subclasses()):

            # if cj.name == qi.name:
                # if (Ftemp != []):
                    # Fres.append(Ftemp)

                # Fj = (qi.name, cj.name)
                # Frec = Pairs(qi, cj, O)
                # if (Frec != []):
                    # print('Frec decart', Frec)
                    # Ftemp = dekartMul(Frec, [Fj])
                # else:
                    # Ftemp = Fj

            # elif like(qi, cj):
                # if (Ftemp != []):
                    # Fres.append(Ftemp)    
                # Fj = (qi.name, cj.name)
                # Frec = Pairs(qi, cj, O)
                # if (Frec != []):
                    # Ftemp = dekartMul(Frec, [Fj])
                # else:
                    # Ftemp = Fj

    # if (Ftemp != []):
        # if (isinstance(Ftemp, list)):
            # Fres.extend(Ftemp)
        # else:
            # Fres.append(Ftemp)
             
    # return Fres

# def get_combination(list_pair):
    # set_list = []
    # for i in list_pair:
        # for j in list_pair:
            # if (i[0] != j[0] and i[1] != j[1]):
                # a = [i, j]
                # a.sort()
                # if a not in set_list:
                    # set_list.append(a)
    # return(set_list)


# def do_pairs_sets(pairs_list):
    
    # set_list = []
    # str_list = []
    
    # for elem in pairs_list:
        # set_list.append([elem])
        # if isinstance(elem, list):
            # str_list.append(str(elem[0] + elem[1]))
        # else:
            # str_list.append(str(elem[0] + elem[1]))
    # print('set_list', set_list)
    # print('str_list', str_list)
    # for pair in pairs_list:
        # for elem in set_list
            # if (pair in elem or 
        
        # set_list.append([elem])    
    
        
        # print('elem', elem)
        
        
    
    # return set_list

# def Pairs1(Q, C):
    
    # for q in list(Q.subclasses()):
        # cc = None
        # for c in list(C.subclasses()):
            # if q.name == c.name:
                # Fj = (q.name, c.name)
                # Frec = Pairs(q, c)
                # if Frec != []:
                    # Ftemp.extend(Frec)    #Ftemp = dekartMul(Frec, Fj)
                # Ftemp.append(Fj)        #Декартово??
                # cc = c
                # break
        # if cc and q.name == cc.name:
            # Fres.append(Ftemp)        
            # Ftemp = []
            # continue
        
        
        # for c in list(C.subclasses()):
            # if like(q, c):
                # Fres.append(Ftemp)
                # Fj = (q.name, c.name)
                # Frec = Pairs(q, c)
                # Ftemp = Frec
                # Ftemp.append(Fj)
        
        # if Ftemp != []:
            # Fres.append(Ftemp)
            # Ftemp = []

    # return Fres
        
    
# defPairs(Q, C, X):
    # global checked_nodes_list
    # Fres, Ftemp = [], []
    # print('Pairs start...')
    # ищем совпадение по имени
    # print('Q subclasses', Q.name)
    # print('C subclasses', C.name)
    # for qi in list(Q.subclasses()):
        # cc = None
        # i+=1
        # print('qi.name', qi.name)
        # if qi.name not in checked_nodes_list:
            # for cj in list(C.subclasses()):
                # если имена равны
                # print('cj.name', cj.name)
                # if cj.name == qi.name:
                    # LSj + CF1
                    # Fj = (qi.name, cj.name)
                    # print('Fj', Fj)
                    # Frec = Pairs(qi, cj, X)
                    # print('Frec-', Frec)
                    # if Frec != []:
                        # Ftemp.extend(Frec)    #Ftemp = dekartMul(Frec, Fj)
                    # Ftemp.append(Fj)        #Декартово??
                    # print('Ftemp', Ftemp)
                    # print('qi.namehghgfhvj', qi.name)
                    # checked_nodes_list.append(qi.name)
                    
                    # break
    
                # ищем подобные (с одинаковыми родителями)
                # elif like(qi, cj):
                    # Fres.append(Ftemp)
                    # print('qi.nameh11111', qi.name)
                    # checked_nodes_list.append(qi.name)
                    # LSj + CF2 
                    # Fj = (qi.name, cj.name)
                    # Frec = Pairs(qi, cj, X)
                    # if Frec != []:
                        # Ftemp.extend(Frec)
                    # Ftemp.append(Fj) #Ftemp = Frec  F
                    # Frec = Pairs(Q,C,O) [(), (), (), ()]
                    # Ftemp = Frec  Ftemp
            # if Ftemp != []:
                # Fres.append(Ftemp)
                # Ftemp = []
    # print('checked_nodes_list', len(checked_nodes_list))   
    # print('len(names_nodes_list)', list(X.subclasses()))
    # Fres.append(Ftemp)
    # return Fres
    
    # def do_perent_child_list(Q):
    # perent_child_list = []

    # for child in list(Q.subclasses()):
        # temp_list = list(child.ancestors())
        # for elem in temp_list:
            # if (elem.name != 'Thing' and elem.name != 'case' and elem.name != child.name):
                # perent_child_list.append((elem.name, child.name))

        # if (list(child.subclasses()) != []):
            # perent_child_list.extend(do_perent_child_list(child))

    # return perent_child_list