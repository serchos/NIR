import io
from .metrics import L1_metric, euclid_metric, chebyshev_metric
from .degree_of_similarity import degree_of_similarity

metrics_array = {'metric_L1': L1_metric, 'metric_Euclid': euclid_metric, 'metric_Chebyshev': chebyshev_metric}
#enumerate()- применяется для итерируемых коллекций (строки, списки, словари и др.) и создает объект, который генерирует кортежи, состоящие из двух элементов индекса элемента и самого элемента



def kNN_for_all_cases(precedents_matrix, cases_matrix, neighbors_count, metric_name, param_weights_list, lower_bounds_for_parametrs_list, upper_bounds_for_parametrs_list):
    solutions_list_for_all_cases, max_count_voters_list_for_all_cases = [], []
    
    distance_max = metrics_array[metric_name](lower_bounds_for_parametrs_list, upper_bounds_for_parametrs_list, param_weights_list)

    for current_case in cases_matrix:
        solution, max_count_voters = kNN_for_one_case(precedents_matrix, current_case, neighbors_count, metric_name, param_weights_list, distance_max)
        solutions_list_for_all_cases.append(solution)
        max_count_voters_list_for_all_cases.append(max_count_voters)
        
    return solutions_list_for_all_cases, max_count_voters_list_for_all_cases



def kNN_for_one_case(precedents_matrix, current_case, neighbors_count, metric_name, param_weights_list, distance_max):
    precedents_parametrs_matrix, precedents_answers_list = split_precedents_matrix(precedents_matrix)
    greatest_deg_similarity_value_list, k_nearest_answers_list = [], []

    for precedet_id, precedet_parametrs in enumerate(precedents_parametrs_matrix):  
        distance = metrics_array[metric_name](precedet_parametrs, current_case, param_weights_list)
        # print(distance)
        deg_similarity = degree_of_similarity(distance, distance_max)
        # print(deg_similarity)
        if len(greatest_deg_similarity_value_list) < neighbors_count:
            greatest_deg_similarity_value_list.append(deg_similarity)
            k_nearest_answers_list.append(precedents_answers_list[precedet_id])
        else:
            if len(greatest_deg_similarity_value_list) == neighbors_count:
                min_deg_similarity, min_deg_similarity_position = find_min_deg_similarity(greatest_deg_similarity_value_list)
            if (deg_similarity > min_deg_similarity):
                greatest_deg_similarity_value_list[min_deg_similarity_position] = deg_similarity
                k_nearest_answers_list[min_deg_similarity_position] = precedents_answers_list[precedet_id]
                min_deg_similarity, min_deg_similarity_position = find_min_deg_similarity(greatest_deg_similarity_value_list)
    
    solution, max_count_voters = voting(k_nearest_answers_list)

    return solution, max_count_voters



def split_precedents_matrix(precedents_matrix):
    precedents_parametrs_matrix, precedents_answers_list = [], []
    
    for str in precedents_matrix:
        precedents_parametrs_matrix.append(str[:-1]) 
        precedents_answers_list.append(str[-1])
        
    return precedents_parametrs_matrix, precedents_answers_list



def find_min_deg_similarity(greatest_deg_similarity_value_list):
    min_deg_similarity, min_deg_similarity_position = greatest_deg_similarity_value_list[0], 0
    
    for i, deg_similarity_i in enumerate(greatest_deg_similarity_value_list):
        if deg_similarity_i < min_deg_similarity:
            min_deg_similarity = deg_similarity_i
            min_deg_similarity_position = i
    
    return min_deg_similarity, min_deg_similarity_position



def voting(k_nearest_answers_list): 
    max_count_voters = 0
    
    for i_answer in k_nearest_answers_list:
        count_voters_for_i_answer = 0
        
        for j_answer in k_nearest_answers_list:
            if i_answer == j_answer:
                count_voters_for_i_answer += 1
        
        if count_voters_for_i_answer > max_count_voters:
            max_count_voters = count_voters_for_i_answer
            result_answer_of_voting = i_answer
    
    return result_answer_of_voting, max_count_voters