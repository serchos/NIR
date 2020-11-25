from owlready2 import *
#isinstance - возвращает флаг, указывающий на то, является ли указанный объект экземпляром указанного класса
#fabs - возвращает абсолютное значение (модуль)
#pow - возведение в степень
#zip - объединяет в кортежи элементы из последовательностей переданных в качестве аргументов


def createHierarchyTreeDict(Thing, world):
    hierarchy = {}
    hierarchy_list = {}
    hierarchy[Thing.name] = getHierarchyTreeDict(list(Thing.subclasses(world = world)), hierarchy_list)
    return hierarchy
def getHierarchyTreeDict(onto_classes, hierarchy_list):
    hierarchy_list = {}
    for onto_class in onto_classes:
        if not list(onto_class.subclasses()):
            hierarchy_list[onto_class.name] = {}
        else:
            hierarchy_list[onto_class.name] = getHierarchyTreeDict(list(onto_class.subclasses()), hierarchy_list)
    return hierarchy_list
# для списка параметров текущей ситуации
def getNodeKidsListRecursive(node, kidsList):
    for kid in list(node.subclasses()):
        kidsList.append(kid.name)
        if list(kid.subclasses()):
            getNodeKidsListRecursive(kid, kidsList)
    return kidsList
def getNodeKidsList(node):
    kidsList = []
    getNodeKidsListRecursive(node, kidsList)
    return kidsList
def get_graph_hierarchy(list_subclasses):
    graph_hierarchy = {}
    graph_hierarchy[Thing.name] = get_list_class_names(list_subclasses)
    for node in list_subclasses:
        add_nodes_to_hierarchy(graph_hierarchy, node, list(node.subclasses()))
    return graph_hierarchy
        
def add_nodes_to_hierarchy(graph_hierarchy, node, list_subclasses):
    graph_hierarchy[node.name] = get_list_class_names(list_subclasses)
    for subclass in list_subclasses:
        add_nodes_to_hierarchy(graph_hierarchy, subclass, list(subclass.subclasses()))
def get_list_class_names(list_classes):
    list_names = []
    for onto_class in list_classes:
        list_names.append(onto_class.name)
    return list_names


#ребра в формате {from: 1, to: 3} для vis.js
def getEdges(graph_hierarchy):
    i = 1
    list_edges = []
    list_onto_name_number = {}
    for key in graph_hierarchy:
        list_onto_name_number[key] = i
        i += 1   
    for key, values in graph_hierarchy.items():
        if values:
            for value in values:
                edge = {}
                edge['from'] = key#list_onto_name_number[key]
                edge['to'] = value#list_onto_name_number[value]
                #edge[list_onto_name_number[key]] = list_onto_name_number[value]
                list_edges.append(edge)
    return list_edges