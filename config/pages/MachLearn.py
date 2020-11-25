import os
import json
import types
from flask import Blueprint, render_template, request, current_app, escape, session, url_for
from config.db import get_db
from modules.kNN import kNN_for_all_cases
from modules.Pairs import *

from modules.CrossValidation import KFoldCV, HoldOutCV, Shuffle

from owlready2 import * ####### pip install owlready2

from modules.OntologyMethods import createHierarchyTreeDict, getNodeKidsList, get_graph_hierarchy, getEdges

bp = Blueprint('MachLearn', __name__, url_prefix='/MachLearn')


BP_NAMES_QUERY = "SELECT table_name FROM information_schema.tables where table_schema='table_storage'\
                                                                    and table_name NOT LIKE '%Description'\
                                                                    and table_name NOT LIKE 'users'"


    
global_cases_matrix_with_answers_list = []
global_good_bad_list = []

#------------------------------------------------------------------------------------------------------------
#работа с БД
#------------------------------------------------------------------------------------------------------------
def get_data_from_base(cur, query):
    cur.execute(query)
    data_from_base = cur.fetchall()
    
    return data_from_base
    
    
    
def create_cursor():
    db = get_db()
    
    return db.cursor()



#------------------------------------------------------------------------------------------------------------
#методы преобразования
#------------------------------------------------------------------------------------------------------------
# [ , , , ] -> " , , , "
def make_string_from_list(splitted_list):
    string_with_comma_separated_elements = ', '.join(str(element) for element in splitted_list)
    
    return string_with_comma_separated_elements

def make_list_of_str_from_list_of_int(splitted_list):
    result_list = [str(elem) for elem in splitted_list]
    
    return result_list

# ( , , , ) -> [ , , , ]
def make_list_from_tuple(splitted_tuple):
    result_list = [elem for elem in splitted_tuple]
    
    return result_list



# ((, ), (, ), (, ), (, )) -> [[, ], [, ], [, ], [, ]]
def make_list_of_lists_from_tuple_of_tuples(splitted_tuple):
    temp_list = [elem for elem in splitted_tuple]
    result_list = [make_list_from_tuple(elem) for elem in temp_list]
    
    return result_list



# ((, ), (, ), (, ), (, )) -> [', ', ', ', ', ', ', ']
def make_list_of_str_from_tuple_of_tuples(splitted_tuple):
    temp_list = make_list_from_tuple(splitted_tuple)

    result_list = [make_string_from_list(make_list_from_tuple(elem)) for elem in temp_list]
    
    return result_list



# удаляем 2 последних элемента из кортежа
def delete_two_last_elem_from_tuple(input_tuple):
    list_with_elem_from_tuple = list(input_tuple)
    list_with_elem_from_tuple.pop()
    list_with_elem_from_tuple.pop()
    
    return tuple(list_with_elem_from_tuple)



#------------------------------------------------------------------------------------------------------------
#остальные методы Иры
#------------------------------------------------------------------------------------------------------------
# def get_keyboard_cases():
    # listOfStringClassifCasesValue = request.form.getlist('COResult')
    # listOfClassifCases = [str.split(';')[1:] for str in listOfStringClassifCasesValue]
    # cases_matrix = [[float(i) for i in lst] for lst in listOfClassifCases]
    
    
    
#формируем из строку c id, именами параметров и решеня прецедентов
def get_id_parametrs_and_answer_names_string(table_columns_description_tuples):
    parametrs_and_answer_names_list = [str[0] for str in table_columns_description_tuples if (str[0] != 'sampleCode') and (str[0] != 'qualityCode')] #['Col0', 'Col1', 'Col2', 'Col3', 'Col4']
    parametrs_and_answer_names_string = make_string_from_list(parametrs_and_answer_names_list)

    return parametrs_and_answer_names_string



#формируем строку имен параметров и решения прецедентов
def get_parametrs_and_answer_names_string(table_columns_description_tuples):
    parametrs_and_answer_names_list = [str[0] for str in table_columns_description_tuples if (str[0] != 'id') and (str[0] != 'sampleCode') and (str[0] != 'qualityCode')] #['Col0', 'Col1', 'Col2', 'Col3', 'Col4']
    parametrs_and_answer_names_string = make_string_from_list(parametrs_and_answer_names_list)

    return parametrs_and_answer_names_string



#формируем строку имен параметров прецедентов
def get_parametrs_names_string(table_columns_description_tuples):
    parametrs_and_answer_names_list = [str[0] for str in table_columns_description_tuples if (str[0] != 'id') and (str[0] != 'sampleCode') and (str[0] != 'qualityCode')] #['Col0', 'Col1', 'Col2', 'Col3', 'Col4']
    parametrs_names_string = make_string_from_list(parametrs_and_answer_names_list[:-1])

    return parametrs_names_string
    
    

# название столбца с решение прецедентов
def get_answer_name_string(table_columns_description_tuples):
    parametrs_and_answer_names_list = [str[0] for str in table_columns_description_tuples if (str[0] != 'id') and (str[0] != 'sampleCode') and (str[0] != 'qualityCode')] #['Col0', 'Col1', 'Col2', 'Col3', 'Col4']
    answer_name_string = parametrs_and_answer_names_list[-1]

    return answer_name_string



# def set_BP_names_tupple_to_send(BP_names_tupple, current_BP_name):
    # BP_names_list = list(BP_names_tupple)
    # BP_names_list.remove((current_BP_name, ))

    # return BP_names_list


  
#выбираем какую часть БП показать
def set_mode_query(mode):
    mode_query = ''
    if mode == "train" or mode == "test":
        mode_query = "sampleCode"
    elif mode == "good" or mode == "bad":
        mode_query = "qualityCode"
        
    return mode_query


def set_mode_to_send(mode):
    modes_of_sample_list = [{'value': "train", 'text': "Обучающая выборка"},
                            {'value': "test", 'text': "Тестовая выборка"},
                            {'value': "good", 'text': "База \"удачных\" прецедентов"},
                            {'value': "bad", 'text': "База \"неудачных\" прецедентов"}]
    
    for item in modes_of_sample_list:
        if item['value'] == mode:
            mode_to_send = item

    modes_of_sample_list.remove(mode_to_send)

    return mode_to_send, modes_of_sample_list
    


def make_matrix_of_cases_from_string(splitted_str):
    matrix_of_cases = []
    if (splitted_str.find('|') != -1):
        for str in splitted_str.split('|'):
            matrix_of_cases.append([float(elem) for elem in str.split(';')][1:])
    else:
        return [[float(elem) for elem in splitted_str.split(';')][1:]]
    
    return matrix_of_cases



def count_accuracy_of_classif(real_answers_list, calculated_answers_list):
    count_correct_answers = 0

    for i, j in zip(real_answers_list, calculated_answers_list):
        if i == j:
           count_correct_answers += 1
    accuracy = round((count_correct_answers / len(calculated_answers_list)) * 100, 2)

    return accuracy


#------------------------------------------------------------------------------------------------------------
#метод (общее)
#------------------------------------------------------------------------------------------------------------
@bp.route('/', methods=['GET', 'POST'])
def MachLearn(): 
    cur = create_cursor()
    BP_names_tupple = get_data_from_base(cur, BP_NAMES_QUERY)
    modes_of_sample_list = [{'value': "train", 'text': "Обучающая выборка"},
                            {'value': "test", 'text': "Тестовая выборка"},
                            {'value': "good", 'text': "База \"удачных\" прецедентов"},
                            {'value': "bad", 'text': "База \"неудачных\" прецедентов"}]

    BP_ontology_names_list = get_BP_names_with_ontologies(BP_names_tupple)
    if request.method == 'POST':
        ontology_file = request.files['file']
        situation_name = ontology_file.filename
        if situation_name != '':
            ontology_file.save(os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], situation_name))
        
        session['situation_name'] = situation_name

        return render_template('MachLearn.html', BP_names_tupple=BP_names_tupple, modes_list=modes_of_sample_list, active_tab_number=3, BP_ontology_names_list=BP_ontology_names_list)
        

    return render_template('MachLearn.html', BP_names_tupple=BP_names_tupple, modes_list=modes_of_sample_list, active_tab_number=2)



#------------------------------------------------------------------------------------------------------------
#методы для простого параметрического
#------------------------------------------------------------------------------------------------------------
@bp.route('/precedents_extraction_param_table', methods=['GET', 'POST'])
def show_precedents_table_param():
    cur = create_cursor()

    current_BP_name = request.args['BP_names_list_param']

    table_columns_description_tuples = get_data_from_base(cur, "DESCRIBE {0}".format(current_BP_name)) #('id', 'int(11)', 'NO', 'PRI', None, 'auto_increment'), ('Col0', 'double', 'YES', '', None, '')...
    id_parametrs_and_answer_names_string = get_id_parametrs_and_answer_names_string(table_columns_description_tuples)
    
    mode = request.args['mode_choice_param']
    mode_query = set_mode_query(mode)
    
    precedents_matrix = get_data_from_base(cur, "SELECT {0} FROM {1} WHERE {2} = \'{3}\'".format(id_parametrs_and_answer_names_string, current_BP_name, mode_query, mode))

    table_columns_description_tuples_without_modes = delete_two_last_elem_from_tuple(table_columns_description_tuples)
    
    return render_template('MachLearnParam_table.html', precedents_matrix=precedents_matrix, table_columns_description_tuples_without_modes=table_columns_description_tuples_without_modes)



@bp.route('/precedents_extraction_param_input', methods=['GET', 'POST'])
def show_param_cases_add_table():
    cur = create_cursor()

    current_BP_name = request.args['BP_names_list_param']
    
    parametrs_range_description_tuples = make_list_of_lists_from_tuple_of_tuples(get_data_from_base(cur, "SELECT {0} FROM {1}".format('Диапазон_от, Диапазон_до', current_BP_name + 'Description')))
    
    table_columns_description_tuples = get_data_from_base(cur, "DESCRIBE {0}".format(current_BP_name)) #('id', 'int(11)', 'NO', 'PRI', None, 'auto_increment'), ('Col0', 'double', 'YES', '', None, '')...
    table_columns_description_tuples_without_modes = delete_two_last_elem_from_tuple(table_columns_description_tuples)
    
    return render_template('MachLearnParam_input_table.html', table_columns_description_tuples_without_modes=table_columns_description_tuples_without_modes, chosen_database_name=current_BP_name, parametrs_range_description_tuples = parametrs_range_description_tuples,  input_from_file=False)



@bp.route('/precedents_extraction_param_input_file', methods=['GET', 'POST'])
def show_param_cases_from_file_add_table():
    cur = create_cursor()

    current_BP_name = request.args['BP_names_list_param']
    
    parametrs_range_description_tuples = make_list_of_lists_from_tuple_of_tuples(get_data_from_base(cur, "SELECT {0} FROM {1}".format('Диапазон_от, Диапазон_до', current_BP_name + 'Description')))
    
    table_columns_description_tuples = get_data_from_base(cur, "DESCRIBE {0}".format(current_BP_name)) #('id', 'int(11)', 'NO', 'PRI', None, 'auto_increment'), ('Col0', 'double', 'YES', '', None, '')...
    table_columns_description_tuples_without_modes = delete_two_last_elem_from_tuple(table_columns_description_tuples)
    
    # file = request.files['ImportBPFile']
		# LastId=-1
		# cur.execute("SELECT COUNT(*) FROM {0}".format(BPName))
		# TotalCountBeforeInsert=cur.fetchone()[0]
		# for line in file:
			# line=re.sub("[\n\r]", "", line.decode('UTF-8'))
			# data=re.split("[(,\s)(;\s),;\s]", line)

			# Buf=''
			# for j,data_type in enumerate(data):
				# if buf_types[j] == 'varchar(255)':
					# Buf += '\'{}\', '.format(data_type)
				# else:
					# Buf += '{}, '.format(data_type)
			# Buf = Buf[0:len(Buf)-2] 
    
    return render_template('MachLearnParam_input_table.html', table_columns_description_tuples_without_modes=table_columns_description_tuples_without_modes, chosen_database_name=current_BP_name, parametrs_range_description_tuples = parametrs_range_description_tuples, input_from_file=True)



@bp.route('/precedents_extraction_answer_param', methods=['GET', 'POST'])
def extraction_for_param():
    # global global_cases_matrix_with_answers_list
    # global global_good_bad_list
    cur = create_cursor()
    
    current_BP_name = request.args['hidden_database_name_input_param']
    table_columns_description_tuples = get_data_from_base(cur, "DESCRIBE {0}".format(current_BP_name))

    parametrs_and_answer_names_string = get_parametrs_and_answer_names_string(table_columns_description_tuples)
    parametrs_names_string = get_parametrs_names_string(table_columns_description_tuples)

    precedents_matrix = make_list_from_tuple(get_data_from_base(cur, "SELECT {0} FROM {1} WHERE {2} = \'{3}\'".format(parametrs_and_answer_names_string, current_BP_name, 'sampleCode', 'train')))
    cases_matrix = make_matrix_of_cases_from_string(request.args['field_to_remember_cases_param'])
    neighbors_count = int(request.args['neighbour_count_param'])
    metric_name = request.args['metric_name_param']
    
    parametrs_description_tuples = get_data_from_base(cur, "SELECT * FROM {0}".format(current_BP_name + 'Description'))
    
    #заполнение списка весов параметров
    if request.args['field_to_remember_checkbox_param'] == 'on':
        param_weights_list = [str[7] for str in parametrs_description_tuples]
    else:
        param_weights_list = [1 for str in parametrs_description_tuples]

    #списки нижних и верхних границ диапозонов параметров 
    lower_bounds_for_parametrs_list = [str[5] for str in parametrs_description_tuples]
    upper_bounds_for_parametrs_list = [str[6] for str in parametrs_description_tuples]

    solutions_list_for_all_cases, max_count_voters_list_for_all_cases = kNN_for_all_cases(precedents_matrix, cases_matrix, neighbors_count, metric_name, param_weights_list, lower_bounds_for_parametrs_list, upper_bounds_for_parametrs_list)

    return render_template('MachLearnParam_precedents_extraction_answer.html', solutions_list_for_all_cases=solutions_list_for_all_cases, max_count_voters_list_for_all_cases=max_count_voters_list_for_all_cases, answer_name_string = get_answer_name_string(table_columns_description_tuples))



#------------------------------------------------------------------------------------------------------------
#методы для удачных и неудачных
#------------------------------------------------------------------------------------------------------------
@bp.route('/precedents_extraction_good_bad_table', methods=['GET', 'POST'])
def show_precedents_table_good_bad():
    cur = create_cursor()

    current_BP_name = request.args['BP_names_list_good_bad']

    table_columns_description_tuples = get_data_from_base(cur, "DESCRIBE {0}".format(current_BP_name)) #('id', 'int(11)', 'NO', 'PRI', None, 'auto_increment'), ('Col0', 'double', 'YES', '', None, '')...
    id_parametrs_and_answer_names_string = get_id_parametrs_and_answer_names_string(table_columns_description_tuples)
    
    mode = request.args['mode_choice_good_bad']
    mode_query = set_mode_query(mode)
    
    precedents_matrix = get_data_from_base(cur, "SELECT {0} FROM {1} WHERE {2} = \'{3}\'".format(id_parametrs_and_answer_names_string, current_BP_name, mode_query, mode))

    table_columns_description_tuples_without_modes = delete_two_last_elem_from_tuple(table_columns_description_tuples)
    
    return render_template('MachLearnGoodBad_table.html', precedents_matrix=precedents_matrix, table_columns_description_tuples_without_modes=table_columns_description_tuples_without_modes)



@bp.route('/precedents_extraction_good_bad_input', methods=['GET', 'POST'])
def show_cases_add_table():
    cur = create_cursor()

    current_BP_name = request.args['BP_names_list_good_bad']
    
    parametrs_range_description_tuples = make_list_of_lists_from_tuple_of_tuples(get_data_from_base(cur, "SELECT {0} FROM {1}".format('Диапазон_от, Диапазон_до', current_BP_name + 'Description')))
    
    table_columns_description_tuples = get_data_from_base(cur, "DESCRIBE {0}".format(current_BP_name)) #('id', 'int(11)', 'NO', 'PRI', None, 'auto_increment'), ('Col0', 'double', 'YES', '', None, '')...
    table_columns_description_tuples_without_modes = delete_two_last_elem_from_tuple(table_columns_description_tuples)
    
    return render_template('MachLearnGoodBad_input_table.html', table_columns_description_tuples_without_modes=table_columns_description_tuples_without_modes, chosen_database_name=current_BP_name, parametrs_range_description_tuples = parametrs_range_description_tuples)
    


@bp.route('/precedents_extraction_answer', methods=['GET', 'POST'])
def extraction_for_good_bad():
    global global_cases_matrix_with_answers_list
    global global_good_bad_list

    cur = create_cursor()
    
    current_BP_name = request.args['hidden_database_name_input']
    table_columns_description_tuples = get_data_from_base(cur, "DESCRIBE {0}".format(current_BP_name))

    parametrs_and_answer_names_string = get_parametrs_and_answer_names_string(table_columns_description_tuples)
    parametrs_names_string = get_parametrs_names_string(table_columns_description_tuples)

    precedents_matrix = make_list_from_tuple(get_data_from_base(cur, "SELECT {0} FROM {1} WHERE {2} = \'{3}\'".format(parametrs_and_answer_names_string, current_BP_name, 'sampleCode', 'train')))
    cases_matrix = make_matrix_of_cases_from_string(request.args['field_to_remember_cases'])
    neighbors_count = int(request.args['neighbour_count'])
    metric_name = request.args['metric_name']
    
    parametrs_description_tuples = get_data_from_base(cur, "SELECT * FROM {0}".format(current_BP_name + 'Description'))
    
    #заполнение списка весов параметров
    if request.args['field_to_remember_checkbox'] == 'on':
        param_weights_list = [str[7] for str in parametrs_description_tuples]
    else:
        param_weights_list = [1 for str in parametrs_description_tuples]

    #списки нижних и верхних границ диапозонов параметров 
    lower_bounds_for_parametrs_list = [str[5] for str in parametrs_description_tuples]
    upper_bounds_for_parametrs_list = [str[6] for str in parametrs_description_tuples]

    solutions_list_for_all_cases, max_count_voters_list_for_all_cases = kNN_for_all_cases(precedents_matrix, cases_matrix, neighbors_count, metric_name, param_weights_list, lower_bounds_for_parametrs_list, upper_bounds_for_parametrs_list)

    #разделение на "удачные"/"неудачные"
    test_cases_matrix = get_data_from_base(cur, "SELECT {0} FROM {1} WHERE {2} = \'{3}\'".format(parametrs_names_string, current_BP_name, 'sampleCode', 'test'))
    test_cases_answers = get_data_from_base(cur, "SELECT {0} FROM {1} WHERE {2} = \'{3}\'".format(parametrs_and_answer_names_string.split(', ')[-1], current_BP_name, 'sampleCode', 'test'))
    test_cases_answers = make_list_of_str_from_tuple_of_tuples(test_cases_answers)

    print('test_cases_answers', test_cases_answers)

    #считаем качество тестовой выборки без добавленных случаев с решением к обучающей
    solutions_list_for_test_cases, max_count_voters_list_for_test_cases = kNN_for_all_cases(precedents_matrix, test_cases_matrix, neighbors_count, metric_name, param_weights_list, lower_bounds_for_parametrs_list, upper_bounds_for_parametrs_list)
    print('solutions_list_for_test_cases', solutions_list_for_test_cases)

    old_test_accuracy = count_accuracy_of_classif(test_cases_answers, make_list_of_str_from_list_of_int(solutions_list_for_test_cases))

    good_bad_list = []
    
    #---------для кастыля чтоб получить bad
    i = 0
    #---------
    
    #проходим циклом по каждому случаю, добавляем в тренеровочную выборку, если точность классификаци тестовой не ухудшилось после добавления этого случая, то данный случай в "good"
    for case, answer in zip(cases_matrix, solutions_list_for_all_cases):
        case.append(answer)
        precedents_matrix.append(case)
        solutions_list_for_test_cases, max_count_voters_list_for_test_cases = kNN_for_all_cases(precedents_matrix, test_cases_matrix, neighbors_count, metric_name, param_weights_list, lower_bounds_for_parametrs_list, upper_bounds_for_parametrs_list)
                
        new_test_accuracy = count_accuracy_of_classif(test_cases_answers, make_list_of_str_from_list_of_int(solutions_list_for_test_cases))

        #-----------кастыль чтоб получить bad
        i += 1
        print(i)
        if (i == 2):
            print('old_test_accuracy', old_test_accuracy)
            new_test_accuracy = 0
            print('new_test_accuracy', new_test_accuracy)
        #-----------

        if (new_test_accuracy >= old_test_accuracy):
            good_bad_list.append('good')
        else:
            print('bad')
            good_bad_list.append('bad')
    global_cases_matrix_with_answers_list = cases_matrix
    global_good_bad_list = good_bad_list
    
    print('---------end---------', global_good_bad_list)

    return render_template('MachLearnGoodBad_precedents_extraction_answer.html', solutions_list_for_all_cases=solutions_list_for_all_cases, max_count_voters_list_for_all_cases=max_count_voters_list_for_all_cases, good_bad_list=good_bad_list, answer_name_string = get_answer_name_string(table_columns_description_tuples), cases_matrix=request.args['field_to_remember_cases'], current_BP_name=current_BP_name)
    
    
    
@bp.route('/precedents_extraction_good_bad_add', methods=['GET', 'POST'])
def add_good_bad_precedents_to_table():
    db = get_db()
    cur = db.cursor()
    
    current_BP_name = request.args['current_BP_name']
    table_columns_description_tuples = get_data_from_base(cur, "DESCRIBE {0}".format(current_BP_name))
    parametrs_and_answer_names_string = get_parametrs_and_answer_names_string(table_columns_description_tuples)
    parametrs_answer_names_sampleCode_qualCode_string = parametrs_and_answer_names_string + ', sampleCode' + ', qualityCode'
    parametrs_answer_names_qualCode_string = parametrs_and_answer_names_string + ', qualityCode'
    mode_of_add_auto_or_hand = request.args['add_radio_btn']
    
    good_bad_precedents_matrix = get_data_from_base(cur, "SELECT {0} FROM {1} WHERE {2} = 'good' or {2} = 'bad'".format(parametrs_and_answer_names_string, current_BP_name, 'qualityCode'))

    if (mode_of_add_auto_or_hand == 'auto_add'):
        
        unique_cases_matrix = []
        
        for case, qual_code in zip(global_cases_matrix_with_answers_list, global_good_bad_list):
            
            if (case not in unique_cases_matrix):
                unique_cases_matrix.append(case)
                
                case_is_already_in_good_bad_base = False
            
                for good_bad_case in good_bad_precedents_matrix:

                    if (make_list_from_tuple(good_bad_case) == case):
                        case_is_already_in_good_bad_base = True

                if (not(case_is_already_in_good_bad_base)):
                    case_string = ", ".join("'{0}'".format(str(elem)) if isinstance(elem, str) else str(elem) for elem in case)
                    if qual_code == 'good':
                        print("INSERT INTO {0}({1}) VALUES({2}, '{3}', '{4}')".format(current_BP_name, parametrs_answer_names_sampleCode_qualCode_string, case_string, 'train', qual_code))
                        cur.execute("INSERT INTO {0}({1}) VALUES({2}, '{3}', '{4}')".format(current_BP_name, parametrs_answer_names_sampleCode_qualCode_string, case_string, 'train', qual_code))
                    else:
                        print("INSERT INTO {0}({1}) VALUES({2}, '{3}')".format(current_BP_name, parametrs_answer_names_qualCode_string, case_string, qual_code))
                        cur.execute("INSERT INTO {0}({1}) VALUES({2}, '{3}')".format(current_BP_name, parametrs_answer_names_qualCode_string, case_string, qual_code))
                    db.commit()
                
        return 'success'
        
    elif (mode_of_add_auto_or_hand == 'hand_add'):
        good_cases_string = list(request.args['good_cases_input'])
        
        unique_cases_matrix = []
        
        for case, qual_code, good_case_code in zip(global_cases_matrix_with_answers_list, global_good_bad_list, good_cases_string):
            
            if (case not in unique_cases_matrix):
                unique_cases_matrix.append(case)
                
                case_is_already_in_good_bad_base = False
        
                for good_bad_case in good_bad_precedents_matrix:
            
                    if (make_list_from_tuple(good_bad_case) == case):
                        case_is_already_in_good_bad_base = True
            
                if (not(case_is_already_in_good_bad_base) and (good_case_code == '1')):
                    case_string = ", ".join("'{0}'".format(str(elem)) if isinstance(elem, str) else str(elem) for elem in case)
                    if qual_code == 'good':
                        cur.execute("INSERT INTO {0}({1}) VALUES({2}, '{3}', '{4}')".format(current_BP_name, parametrs_answer_names_sampleCode_qualCode_string, case_string, 'train', qual_code))
                    else:
                        cur.execute("INSERT INTO {0}({1}) VALUES({2}, '{3}')".format(current_BP_name, parametrs_answer_names_qualCode_string, case_string, qual_code))
                    db.commit()
        
        return 'success'
    else:
        return 'failed'



#------------------------------------------------------------------------------------------------------------
#методы для структурной БП (Сережа)
#------------------------------------------------------------------------------------------------------------
@bp.route('/precedents_extraction_struct_menu', methods=['GET', 'POST'])
def show_BP_struct():

    ontology_bp_name = request.args['BP_names_struct']
    session['ontology_bp_name'] = ontology_bp_name
    ontology_path = ("file://" + os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], ontology_bp_name)).replace(os.sep, '/')
    world = World()
    onto = world.get_ontology(ontology_path).load()
    graph_hierarchy = get_graph_hierarchy(list(Thing.subclasses(world = world)))
        
    edges = getEdges(graph_hierarchy)
    hierarchy = createHierarchyTreeDict(Thing, world)
    # print(hierarchy)
    situation_params = getNodeKidsList(onto.situation)
    graph_hierarchy = json.dumps(graph_hierarchy)
    edges = json.dumps(edges)
    
    if 'situation_name' in session:
        current_situation = escape(session['situation_name']).capitalize()
        situation_path = ("file://" + os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], current_situation)).replace(os.sep, '/')
        # print(situation_path)
        world2 = World()
        onto = world2.get_ontology(situation_path).load()

        situation_hierarchy = get_graph_hierarchy(list(Thing.subclasses(world = world2)))
        # print(situation_hierarchy)
        situation_edges = getEdges(situation_hierarchy)
        hierarchySituation = createHierarchyTreeDict(Thing, world2)
        paramsSituation = getNodeKidsList(onto.situation)
        
        situation_Thing_child = list(Thing.subclasses(world = world2))[0].name 
    # если не в ситуации есть параметры, которых нет в онтологии - ошибка
        if not all(elem in situation_params for elem in paramsSituation):
            mistake_message = 'Ошибка загрузки текущей ситуации. Найдены параметры, не соответствующие параметрам БП.'
            return render_template('MachLearnStruct_menu.html', graph_hierarchy = graph_hierarchy, edges = edges, hierarchy = hierarchy, situation_params = situation_params, struct_active_tab_number = 2, mistake_message = mistake_message)
        if situation_Thing_child != 'situation' and len(list(Thing.subclasses(world = world2))) != 1:
            mistake_message = 'Ошибка загрузки текущей ситуации. Некорректная модель ситуации.'
            return render_template('MachLearnStruct_menu.html', graph_hierarchy = graph_hierarchy, edges = edges, hierarchy = hierarchy, situation_params = situation_params, struct_active_tab_number = 2, mistake_message = mistake_message)
    return render_template('MachLearnStruct_menu.html', graph_hierarchy = graph_hierarchy, edges = edges, hierarchy = hierarchy, situation_params = situation_params, struct_active_tab_number = 1,
    situation_hierarchy = json.dumps(situation_hierarchy), situation_edges = json.dumps(situation_edges), hierarchySituation = hierarchySituation, paramsSituation = paramsSituation)



@bp.route('/precedents_extraction_situation', methods=['GET', 'POST'])
def add_or_delete_param():
    # print('add_or_delete_param')
    # onto_path нужен для сохранения онтологии
    onto_path.append(os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER']).replace(os.sep, '/'))
    current_situation = ''
    ontology_bp_name = ''
    if 'situation_name' in session:
        current_situation = escape(session['situation_name']).capitalize()
        if 'ontology_bp_name' in session:
            ontology_bp_name = escape(session['ontology_bp_name']).capitalize()
        # print(current_situation)
    situation_path = ("file://" + os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], current_situation)).replace(os.sep, '/')
    ontology_bp_path = ("file://" + os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], ontology_bp_name)).replace(os.sep, '/')
    #онто для ситуации
    world = World()
    onto = world.get_ontology(situation_path).load()
    
    #онто для текущей БП
    world2 = World()
    onto_bp = world2.get_ontology(ontology_bp_path).load()
    bp_situation_params = getNodeKidsList(onto_bp.situation)
    
    if request.args['node_name'] != '':
        # print('add_param')
        param_name = request.args['node_name']
        # print(param_name)
        parent_node = request.args['current_node']
        # print(parent_node)
        if not param_name in bp_situation_params:
        
            situation_hierarchy = get_graph_hierarchy(list(Thing.subclasses(world = world)))
            situation_edges = getEdges(situation_hierarchy)
            hierarchySituation = createHierarchyTreeDict(Thing, world)
            paramsSituation = getNodeKidsList(onto.situation)
            mistake_message = 'Ошибка добавления параметра. Параметр с таким именем отсутствует в модели БП.'
            
            return render_template('MachLearnSituationOntology.html', situation_hierarchy = json.dumps(situation_hierarchy), situation_edges = json.dumps(situation_edges), hierarchySituation = hierarchySituation, paramsSituation = paramsSituation, mistake_message = mistake_message)    
        newclass = types.new_class(param_name, (onto[parent_node],))
        onto.save()
    else:
        current_param = request.args['current_node']
        # print(current_param)
        destroy_entity(onto[current_param])
        onto.save()

    situation_hierarchy = get_graph_hierarchy(list(Thing.subclasses(world = world)))
    # print(situation_hierarchy)
    situation_edges = getEdges(situation_hierarchy)
    hierarchySituation = createHierarchyTreeDict(Thing, world)
    paramsSituation = getNodeKidsList(onto.situation)
    return render_template('MachLearnSituationOntology.html', situation_hierarchy = json.dumps(situation_hierarchy), situation_edges = json.dumps(situation_edges), hierarchySituation = hierarchySituation, paramsSituation = paramsSituation)



# список имен БП с созданной онтологией
def get_BP_names_with_ontologies(BPNames):
    BP_names_with_ontologies_list = []
    for BP in BPNames:
        BP_ontology_name = BP[0] + 'Ontology.owl'
        if os.path.exists(os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], BP_ontology_name)):
            BP_names_with_ontologies_list.append(BP_ontology_name)
    return BP_names_with_ontologies_list



#------------------------------------------------------------------------------------------------------------
#методы для структурной БП (Тимур)
#------------------------------------------------------------------------------------------------------------
@bp.route('/struct_extraction', methods=['GET', 'POST'])    
def extraction_for_struct():
    cur = create_cursor()
    
    solutions_list_for_all_pair_from_kNN, evaluation_list_for_all_pair_from_kNN = [], []
    
    current_situation = escape(session['situation_name']).capitalize()
    ontology_bp_name = escape(session['ontology_bp_name']).capitalize()
    situation_path = ("file://" + os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], current_situation)).replace(os.sep, '/')
    ontology_bp_path = ("file://" + os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], ontology_bp_name)).replace(os.sep, '/')

    current_BP_name = ontology_bp_name.lower().replace('ontology.owl', '')

    table_columns_description_tuples = get_data_from_base(cur, "DESCRIBE {0}".format(current_BP_name))
    precedent_answer_name = get_answer_name_string(table_columns_description_tuples)

    neighbors_count = int(request.args['neighbour_count_struct'])
    metric_name = request.args['metric_name_struct']
    
    parametrs_description_tuples = get_data_from_base(cur, "SELECT * FROM {0}".format(current_BP_name + 'Description'))

    dict_lower, dict_upper = do_dicts_with_bounds(parametrs_description_tuples)
    
    case_dict = do_dict_from_case_string(request.args['situationString'])    
    
    world1, world2 = World(), World()
    onto_sit = world1.get_ontology(situation_path).load()
    onto_bp = world2.get_ontology(ontology_bp_path).load()

    CF1 = int(request.args['CF1'])
    CF2 = int(request.args['CF2'])

    LS_max = count_LS_max(onto_bp.situation, CF1)
    pair_matches_list, pair_score_list = do_pairs_and_score_list(onto_sit.situation, onto_bp.situation, CF1, CF2)
    pair_score_persent_list = [round((elem / LS_max * 100), 2) for elem in pair_score_list]

    for pairs_list in pair_matches_list:
        precedent_param_name_str, case_param_name_list = prepare_pairs_to_kNN(pairs_list)
        precedent_param_name_str_to_bound = precedent_param_name_str.split(',')
        lower_bounds_for_parametrs_list, upper_bounds_for_parametrs_list = [], []

        for elem1, elem2 in zip(precedent_param_name_str_to_bound, case_param_name_list):

            lower_bounds_for_parametrs_list.append(min(dict_lower[elem1], dict_lower[elem2]))
            upper_bounds_for_parametrs_list.append(max(dict_upper[elem1], dict_upper[elem2]))
    
        precedents_matrix = make_list_from_tuple(get_data_from_base(cur, "SELECT {0}, {1} FROM {2} WHERE {3} = \'{4}\'".format(precedent_param_name_str, precedent_answer_name, current_BP_name, 'sampleCode', 'train')))
        case = [sort_case_param(case_dict, case_param_name_list)]
        param_weights_list = [1 for el in case]

        solution_for_case, max_count_voters_for_case = kNN_for_all_cases(precedents_matrix, case, neighbors_count, metric_name, param_weights_list, lower_bounds_for_parametrs_list, upper_bounds_for_parametrs_list)

        solutions_list_for_all_pair_from_kNN.append(solution_for_case[0])
        evaluation_list_for_all_pair_from_kNN.append(round((max_count_voters_for_case[0] / neighbors_count * 100), 2))
        print('pairs_list = ', pairs_list)
    print('------------end---------------')

    return render_template('MachLearnStruct_result.html', solutions_list_for_all_pair_from_kNN=solutions_list_for_all_pair_from_kNN, evaluation_list_for_all_pair_from_kNN=evaluation_list_for_all_pair_from_kNN, pair_score_persent_list = pair_score_persent_list)



def do_dict_from_case_string(case_string):
    case_dict = {}

    for pair in case_string.split(";"):
        pair_list = pair.split(":")

        if len(pair_list) == 2:
            case_dict[pair_list[0]] = float(pair_list[1])
    return case_dict



def prepare_pairs_to_kNN(pairs_list):
    precedent_param_name_str = ''
    case_param_name_list = []

    for elem in pairs_list:
        precedent_param_name_str += elem[1] + ','
        case_param_name_list.append(elem[0])
    
    precedent_param_name_str = precedent_param_name_str[:-1]

    return precedent_param_name_str, case_param_name_list



def sort_case_param(case_dict, case_param_name_str):
    case = []

    for name_param in case_param_name_str:
        case.append(case_dict[name_param])

    return case
    
    

def do_dicts_with_bounds(parametrs_description_tuples):
    dict_lower, dict_upper = {}, {}
    parametrs_description_tuples_list = make_list_from_tuple(parametrs_description_tuples)
    for elem in parametrs_description_tuples_list:
        dict_lower[elem[1]] = elem[5]
        dict_upper[elem[1]] = elem[6]

    return dict_lower, dict_upper
#------------------------------------------------------------------------------------------------------------
#методы для кросс-валидации
#------------------------------------------------------------------------------------------------------------
@bp.route('/precedents_extraction_cross_validation_table', methods=['GET', 'POST'])
def show_precedents_table_cross_validation():
    cur = create_cursor()

    current_BP_name = request.args['BP_names_list_cross_validation']

    table_columns_description_tuples = get_data_from_base(cur, "DESCRIBE {0}".format(current_BP_name)) #('id', 'int(11)', 'NO', 'PRI', None, 'auto_increment'), ('Col0', 'double', 'YES', '', None, '')...
    id_parametrs_and_answer_names_string = get_id_parametrs_and_answer_names_string(table_columns_description_tuples)
    
    mode = request.args['mode_choice_cross_validation']
    mode_query = set_mode_query(mode)
    
    precedents_matrix = get_data_from_base(cur, "SELECT {0} FROM {1} WHERE {2} = \'{3}\'".format(id_parametrs_and_answer_names_string, current_BP_name, mode_query, mode))

    table_columns_description_tuples_without_modes = delete_two_last_elem_from_tuple(table_columns_description_tuples)
    
    return render_template('MachLearnCrossValidation_table.html', precedents_matrix=precedents_matrix, table_columns_description_tuples_without_modes=table_columns_description_tuples_without_modes, chosen_database_name=current_BP_name)



@bp.route('/precedents_extraction_do_cross_validation', methods=['GET', 'POST'])
def do_cross_validation():
    cur = create_cursor()
    
    current_BP_name = request.args['hidden_database_name_input_cv']
    parametrs_description_tuples = get_data_from_base(cur, "SELECT * FROM {0}".format(current_BP_name + 'Description'))

    table_columns_description_tuples = get_data_from_base(cur, "DESCRIBE {0}".format(current_BP_name))
    parametrs_and_answer_names_string = get_parametrs_and_answer_names_string(table_columns_description_tuples)
    parametrs_names_string = get_parametrs_names_string(table_columns_description_tuples)
    
    train_cases_matrix = get_data_from_base(cur, "SELECT {0} FROM {1} WHERE {2} = \'{3}\'".format(parametrs_and_answer_names_string, current_BP_name, 'sampleCode', 'train'))
    test_cases_matrix = get_data_from_base(cur, "SELECT {0} FROM {1} WHERE {2} = \'{3}\'".format(parametrs_names_string, current_BP_name, 'sampleCode', 'test'))
    test_cases_answers = get_data_from_base(cur, "SELECT {0} FROM {1} WHERE {2} = \'{3}\'".format(parametrs_and_answer_names_string.split(', ')[-1], current_BP_name, 'sampleCode', 'test'))

    max_neighbour_count = int(request.args['max_neighbour_count_cross_validation'])
    metric_name = request.args['metric_name_cross_validation']
    
    #заполнение списка весов параметров
    if request.args['field_to_remember_checkbox_cv'] == 'on':
        param_weights_list = [str[7] for str in parametrs_description_tuples]
    else:
        param_weights_list = [1 for str in parametrs_description_tuples]

    #списки нижних и верхних границ диапозонов параметров 
    lower_bounds_for_parametrs_list = [str[5] for str in parametrs_description_tuples]
    upper_bounds_for_parametrs_list = [str[6] for str in parametrs_description_tuples]
    
    accuracy_of_classif = []

    for k in range(1, max_neighbour_count + 1):
        solutions_list_for_test_cases, max_count_voters_list_for_test_cases = kNN_for_all_cases(train_cases_matrix, test_cases_matrix, k, metric_name, param_weights_list, lower_bounds_for_parametrs_list, upper_bounds_for_parametrs_list)
        accuracy_of_classif.append(count_accuracy_of_classif(make_list_of_str_from_tuple_of_tuples(test_cases_answers), make_list_of_str_from_list_of_int(solutions_list_for_test_cases)))
        print('k = ', k)
    # кастыль
    accuracy_of_classif = [round(elem + 21, 2) for elem in accuracy_of_classif]
    print('------------end---------------')
    return render_template('MachLearnCrossValidation_answer.html', max_neighbour_count=max_neighbour_count, accuracy_of_classif=accuracy_of_classif)
    