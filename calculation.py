# -*- coding: utf-8 -*-
"""
Created on Mon Jun 11 17:25:42 2018
@author: Xinyue Pan
"""
import random
import networkx as nx
import matplotlib.pyplot as plt


############
# count
############
def count_in_nodes(graph, subset_list, index, strategy):
    count = 0.
    for node in subset_list:
        if graph.node[node][index] == strategy:
            count += 1
    return count

def count_in_list(search_list, subset_list, strategy):
    count = 0.
    for node in subset_list:
        if search_list[node[0]][node[1]] == strategy:
            count += 1
    return count


############
# proportion
############
def calculate_prop(graph, index, strategy):
    count = 0.
    for node in graph.nodes():
        if graph.node[node][index] == strategy:
            count += 1.
    if count != 0:
        return count / float(graph.number_of_nodes())
    elif count == 0:
        return 0

def calculate_comb_prop(graph, index1, strategy1, index2, strategy2):
    count = 0.
    for node in graph.nodes():
        if graph.node[node][index1] == strategy1 and graph.node[node][index2] == strategy2:
            count += 1.
    if count != 0:
        return count / float(graph.number_of_nodes())
    elif count == 0:
        return 0


############
# average
############
def aver_in_nodes_all(graph, subset_list, index):
    value_sum = 0.
    num = 0
    for node in subset_list:
        value_sum += graph.node[node][index]
        num += 1
    if num != 0:
        aver = value_sum / num
    elif num == 0:
        aver = 0.
    return aver

def aver_in_nodes(graph, subset_list, index, strategy_index, strategy):
    value_sum = 0.
    num = 0
    for node in subset_list:
        if graph.node[node][strategy_index] == strategy:
            value_sum += graph.node[node][index]
            num += 1
    if num != 0:
        aver = value_sum / num
    elif num == 0:
        aver = 0.
    return aver

def aver_in_nodes_combined(graph, subset_list, index, strategy_index1, strategy1, strategy_index2, strategy2):
    value_sum = 0.
    num = 0
    for node in subset_list:
        if graph.node[node][strategy_index1] == strategy1 and graph.node[node][strategy_index2] == strategy2:
            value_sum += graph.node[node][index]
            num += 1
    if num != 0:
        aver = value_sum / num
    elif num == 0:
        aver = 0.
    return aver


############
# network
############
def common_neighbor(graph, node1, node2):
    common_neighbor = list((set(graph.neighbors(node1)) & set(graph.neighbors(node2))))
    return common_neighbor

def order2position(order, cols):
    n = int(order % cols)
    m = int((order - n) / cols)
    return (m, n)

def draw_network(g, color, label, folder_name, condition_name, randomseed, j, color_book):
    color_values = [color_book.get(node, color_book[g.node[node][color]]) for node in g.nodes()]
    label_values = {}
    for node in list(g.nodes()):
        label_values[node] = g.node[node][label]
    nx.draw(g, pos = nx.spectral_layout(g), node_color = color_values, labels = label_values)
    plt.figtext(0.8, 0.9, 'iteration = ' + str(j))
    title = 'color: ' + color + ', label: ' + label
    plt.figtext(0, 0.9, title)
    fig = plt.gcf()
    fig.savefig(folder_name + '/' + condition_name + '_' + str(randomseed) + '_c' + color + '_l' + label + '_iter' + str(j) + '.png')
#    plt.show()
    plt.close()


############
# list
############
def selectfromlist(list_name, num):
    index_all = []
    selected_list = []
    for i in range(len(list(list_name))):
        index_all.append(i)
    random.shuffle(index_all)
    for j in range(num):
        selected_list.append(list(list_name)[index_all[j]])
    return selected_list
    
def delete_duplicate(mylist):
    newlist = []
    for i in mylist:
        if i not in newlist:
            newlist.append(i)
    return newlist