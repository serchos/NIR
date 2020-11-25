import io, math
#isinstance - возвращает флаг, указывающий на то, является ли указанный объект экземпляром указанного класса
#fabs - возвращает абсолютное значение (модуль)
#pow - возведение в степень
#zip - объединяет в кортежи элементы из последовательностей переданных в качестве аргументов



def L1_metric(precedent, current_case, param_weights_list):
    result_distance = 0

    for i_param_precedent, i_param_current_case, weight_i_param in zip(precedent, current_case, param_weights_list):
        result_distance += math.fabs(weight_i_param * (i_param_precedent - i_param_current_case))

    return result_distance



def euclid_metric(precedent, current_case, param_weights_list):
    result_distance = 0

    for i_param_precedent, i_param_current_case, weight_i_param in zip(precedent, current_case, param_weights_list):
        result_distance += math.pow(weight_i_param * (i_param_precedent - i_param_current_case), 2)

    return math.sqrt(result_distance)



def chebyshev_metric(precedent, current_case, param_weights_list):
    result_distance, current_distance = 0, 0

    for i_param_precedent, i_param_current_case, weight_i_param in zip(precedent, current_case, param_weights_list):
        current_distance = math.fabs(weight_i_param * (i_param_precedent - i_param_current_case))
        
        if current_distance > result_distance:
            result_distance = current_distance

    return result_distance