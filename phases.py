# -*- coding: utf-8 -*-
"""
Created on Sun Jun 10 13:49:29 2018
@author: Lucia Pie
"""
import networkx as nx
import itertools as it
import random
import calculation as calc
from math import exp


def creat_network(rows, cols, neigh_num):
    g = nx.grid_2d_graph(rows, cols, periodic = False)  # periodic set to True creates a toroid
        
    if neigh_num == 8:
        # adding second order connections
        new_edges = []
        
        # saving new edges to create
        for node in g.nodes():
            neighbors = g.neighbors(node)
            neighbor_pairs = it.combinations(neighbors, 2)
            for pair in neighbor_pairs:
                common_node = list((set(g.neighbors(pair[0])) & set(g.neighbors(pair[1]))) - {node})
                if common_node:
                    if (node, common_node[0]) not in new_edges and (common_node[0], node) not in new_edges:
                        new_edges.append((node, common_node[0]))
        
        # creating new edges
        for node_pair in new_edges:
            g.add_edge(node_pair[0], node_pair[1])
            
    elif neigh_num == 12:
        # adding second order connections
        new_edges = []
        
        # saving new edges to create
        for node in g.nodes():
            neighbors = g.neighbors(node)
            neighbor_pairs = it.combinations(neighbors, 2)
            for pair in neighbor_pairs:
                if (pair[0], pair[1]) not in new_edges and (pair[1], pair[0]) not in new_edges:
                    new_edges.append((pair[0], pair[1]))
        
        # creating new edges
        for node_pair in new_edges:
            g.add_edge(node_pair[0], node_pair[1])
            
    elif neigh_num != 4:
        print('Invalid option for neigh_num.')
        
    return g
       
def network_initialization(g, cols, c_strategy_init, g_strategy_init, randomseed):
    random.seed(randomseed)
    rows = int(g.number_of_nodes() / cols)
    for node in g.nodes():
        g.node[node]['cooperation'] = random.choice(c_strategy_init)
        g.node[node]['gossip'] = random.choice(g_strategy_init)
        g.node[node]['last_c_rep'] = [['NA'] * cols for i in range(rows)]  # how people remember others' last behavior
        g.node[node]['c_str_rep'] = [['NA'] * cols for i in range(rows)]  # whether people know others' actual strategy
        g.node[node]['g_str_rep'] = [['NA'] * cols for i in range(rows)]
        g.node[node]['rep_num'] = [[0] * cols for i in range(rows)]  # how many times the agent has received gossip about another agent
        """
        Now I suppose that the more gossip one has received, the more likely he would know one's true strategy.
        In reality, the information can be inaccurate. In the future, I'll change it to a real model-based strategy.
        """
        g.node[node]['inter_with_agent'] = [[0] * cols for i in range(rows)]  # how many times have the agent interacted with the current agent
        """
        It is designed especially for the new O2 who would act nicely twice at the beginning.
        """
        g.node[node]['last_g_rep'] = [['NA'] * cols for i in range(rows)]
        g.node[node]['accum_payoff'] = 0.
        g.node[node]['inter_time'] = 0  # how many times an agent has interacted in the whole process
        g.node[node]['aver_payoff'] = 0.  # aver_payoff in the whole process
        g.node[node]['last_payoff'] = 0.
        g.node[node]['iter_payoff_all'] = 0.
        g.node[node]['iter_inter_time'] = 0
        g.node[node]['iter_inter_avg'] = 0.
        g.node[node]['last_action'] = 'NA'
        g.node[node]['last_gossip'] = 'NA'  # last time when this agent was chosen in a gossip phase, whether he gossiped or not
        g.node[node]['inf_accur'] = 0.
    return g

def cooperation(g, group_num, subset_size, c, r):
    # initialization for the current iteration
    for node in g:
        g.node[node]['iter_payoff_all'] = 0.
        g.node[node]['iter_inter_time'] = 0
        g.node[node]['iter_inter_avg'] = 0.
    
    # choose the pairs/groups to interact
    # only modify this part if switch to a PGG
    """
    We may need to think about whether a full interaction will bring about a different result,
    especially when every one interact with all of his neighbors.
    """  
    group_list = calc.selectfromlist(list(g.edges()), min(group_num, len(list(g.edges()))))
    
    for group in group_list:
        # decide their action, action is saved in 'last_action'
        for node in group:
            if g.node[node]['cooperation'] == 'O1' or g.node[node]['cooperation'] == 'O3':
                # whether there is a gossiper neighbor in the PGG
                gossiper_in_neighbor = calc.count_in_list(g.node[node]['last_g_rep'], list(set(g.neighbors(node)) & set(group)), 'G')
                                
                if gossiper_in_neighbor > 0:
                    g.node[node]['last_action'] = 'C'
                elif g.node[node]['cooperation'] == 'O3':
                    defector_num = calc.count_in_list(g.node[node]['last_c_rep'], group, 'D')
                    if g.node[node]['last_c_rep'][node[0]][node[1]] == 'D':  # don't count for their own reputation
                        defector_num -= 1
                    if defector_num >= subset_size / 2.:
                        g.node[node]['last_action'] = 'D'
                    else:
                        g.node[node]['last_action'] = 'C'
                else:
                    g.node[node]['last_action'] = 'D'
                    
            elif g.node[node]['cooperation'] == 'O2':
                defector_num = calc.count_in_list(g.node[node]['last_c_rep'], group, 'D')
                if g.node[node]['last_c_rep'][node[0]][node[1]] == 'D':  # don't count for their own reputation
                    defector_num -= 1
                if defector_num >= subset_size / 2.:
                    g.node[node]['last_action'] = 'D'
                else:
                    g.node[node]['last_action'] = 'C'
                
                # would act nicely twice if any of the agents in the group is new
                for node2 in group:
                    if node2 == node:
                        continue
                    elif g.node[node]['inter_with_agent'][node2[0]][node2[1]] < 2:
                        g.node[node]['last_action'] = 'C'
                    
            elif g.node[node]['cooperation'] == 'O4':
#                # assume that reputation is transparent
                defector_num = calc.count_in_nodes(g, group, 'cooperation', 'D')
                
#                # assume that people need to KNOW about other's strategies but it's possible for them to know the strategies
#                defector_num = calc.count_in_list(g.node[node]['c_str_rep'], group, 'D')
#                if g.node[node]['c_str_rep'][node[0]][node[1]] == 'D':  # don't count for their own reputation
#                    defector_num -= 1
#                    
#                if defector_num >= subset_size / 2.:
#                    g.node[node]['last_action'] = 'D'
#                else:
#                    g.node[node]['last_action'] = 'C'
#                    
#                # would act nicely twice if any of the agents in the group is new
#                for node2 in group:
#                    if node2 == node:
#                        continue
#                    elif g.node[node]['inter_with_agent'][node2[0]][node2[1]] < 2:
#                        g.node[node]['last_action'] = 'C'
                                
            else:
                g.node[node]['last_action'] = g.node[node]['cooperation']
    
        # cooperation game
        count_C = calc.count_in_nodes(g, group, 'last_action', 'C')
        aver_pay = count_C * c * r / float(subset_size)

        for node in group:            
            g.node[node]['inter_time'] += 1
            g.node[node]['iter_inter_time'] += 1
            if g.node[node]['last_action'] == 'C':
                g.node[node]['accum_payoff'] += aver_pay - c
                g.node[node]['iter_payoff_all'] += aver_pay - c
                g.node[node]['last_payoff'] = aver_pay - c
            else:
                g.node[node]['accum_payoff'] += aver_pay
                g.node[node]['iter_payoff_all'] += aver_pay
                g.node[node]['last_payoff'] = aver_pay
            g.node[node]['aver_payoff'] = g.node[node]['accum_payoff'] / g.node[node]['inter_time']
            g.node[node]['iter_inter_avg'] = g.node[node]['iter_payoff_all'] / g.node[node]['iter_inter_time']
                        
            # agents in the cooperation game update their partner's reputation
            # know their neighbors' last behavior
            for node2 in group:
                if node2 == node:
                    continue
                g.node[node]['inter_with_agent'][node2[0]][node2[1]] += 1
                if node2 not in list(g.neighbors(node)):
                    continue
                g.node[node]['last_c_rep'][node2[0]][node2[1]] = g.node[node2]['last_action']
#                g.node[node]['rep_num'][node2[0]][node2[1]] += 1
                """
                I commented it because I assume that people can't know the partner's true strategy through direct interaction.
                They can only get this infomration through gossip.
                """

    return g

def gossip_talk(g, gossiper_node, target_node, receiver_node, gc):
    if target_node == receiver_node:
        return g
    else:
        g.node[receiver_node]['rep_num'][target_node[0]][target_node[1]] += 1
        g.node[gossiper_node]['last_gossip'] = 'G'
        g.node[receiver_node]['last_g_rep'][gossiper_node[0]][gossiper_node[1]] = 'G'
        g.node[gossiper_node]['accum_payoff'] -= gc
        g.node[gossiper_node]['iter_payoff_all'] -= gc        
        g.node[gossiper_node]['last_payoff'] -= gc
        g.node[gossiper_node]['aver_payoff'] = g.node[gossiper_node]['accum_payoff'] / g.node[gossiper_node]['inter_time']
        g.node[gossiper_node]['iter_inter_avg'] = g.node[gossiper_node]['iter_payoff_all'] / g.node[gossiper_node]['iter_inter_time']
        return g

def non_gossip_talk(g, gossiper_node, receiver_node):
    g.node[receiver_node]['last_g_rep'][gossiper_node[0]][gossiper_node[1]] = 'N'
    g.node[gossiper_node]['last_gossip'] = 'N'
    return g
    
def gossiping(g, gossiper_num, target_num, receiver_num, gc):
# a fixed amount of agents will be chosen, but the agents chosen are not necessarily gossipers
# the chosen agent will talk to people, but he will gossip only when he is a gossiper and knows something
    # choose gossipers
    gossiper_size = min(gossiper_num, len(list(g.nodes())))
    gossiper_list = calc.selectfromlist(g.nodes(), gossiper_size)
    
    # talking
    for node in gossiper_list:
        g.node[node]['last_gossip'] = 'N'
        
        # choose some neighbors to talk
        # the receiver list can be someone else in future models
        receiver_list_all = []
        receiver_size = min(receiver_num, len(list(g.neighbors(node))))
        for neighbor in g.neighbors(node):
            receiver_list_all.append(neighbor)
        receiver_list = calc.selectfromlist(receiver_list_all, receiver_size)
        
        if g.node[node]['gossip'] == 'G':
            # choose some targets to gossip about
            target_list_all = []
            target_list = []
            for target in g.nodes():
                if g.node[node]['c_str_rep'][target[0]][target[1]] != 'NA' or g.node[node]['last_c_rep'][target[0]][target[1]] != 'NA':
                    if target == node:
                        continue
                    target_list_all.append(target)
            target_size = min(target_num, len(target_list_all))
            target_list = calc.selectfromlist(target_list_all, target_size)
            """
            Now people choose targets from the agents whose reputation/last_action has already be known.
            So as long as you're a gossiper, you can always find someone you know to gossip about.
            It's unlikely that a gossiper don't talk during a gossiping phase.
            So now gossip rate is approximately the same as proportion of gossipers.
            """
            
            # gossip to each receiver about each target
            for target in target_list:
                for receiver in receiver_list:
                    g = gossip_talk(g, node, target, receiver, gc)
        
        elif g.node[node]['gossip'] == 'N':
            for receiver in receiver_list:
                g = non_gossip_talk(g, node, receiver)  # if someone is chosen but didn't gossip, people will think the agent is not a gossiper

    return g

def reproduction(g, cols, fermi_num, payoff_index, s, mu_rate, c_strategy, g_strategy):
    n = g.number_of_nodes()
    fermi_index_all = list(range(n))
    random.shuffle(fermi_index_all)
    # the indices of the students chosen in the current iteration
    fermi_index = [fermi_index_all[i] for i in range(min(fermi_num, n))]
    
    for student_index in fermi_index:
        student = calc.order2position(student_index, cols)
        
        # learn only from immediate neighbors
        teacher = random.choice(list(g.neighbors(student)))
        
        # can also try letting them learn from a random teacher
        # teacher = random.choice(list(g.nodes()))
    
        p = 1. / (1 + exp(0 - s * (g.node[teacher][payoff_index] - g.node[student][payoff_index])))
        
        if random.random() < p:
            g.node[student]['cooperation'] = g.node[teacher]['cooperation']
            g.node[student]['gossip'] = g.node[teacher]['gossip']
            
            # born as a completely new agent
            g.node[student]['accum_payoff'] = 0
            g.node[student]['inter_time'] = 0
            g.node[student]['inter_with_agent'] = [[0] * cols for i in range(int(n / cols))]

        if random.random() < mu_rate:
            g.node[student]['cooperation'] = random.choice(c_strategy)
            g.node[student]['gossip'] = random.choice(g_strategy)

    return g

def modelupdate(g, victim_num, target_num, f_rate, rs, rep_diff):
    victim_list = calc.selectfromlist(g.nodes(), victim_num)
    
    for victim in victim_list:
        target_list = calc.selectfromlist(list(g.nodes()), target_num)
        
        for target in target_list:
            if target == victim:
                continue
            if random.random() < f_rate:               
                if g.node[victim]['rep_num'][target[0]][target[1]] > 0:
                    g.node[victim]['rep_num'][target[0]][target[1]] -= 1
                p = 1 / (1 + exp(- rs * (g.node[victim]['rep_num'][target[0]][target[1]] - rep_diff)))
                if random.random() < p:
                    g.node[victim]['c_str_rep'][target[0]][target[1]] = g.node[target]['cooperation']
                else:
                    g.node[victim]['c_str_rep'][target[0]][target[1]] = g.node[victim]['last_c_rep'][target[0]][target[1]]
    
    for node in g.nodes():
        rep_num = 0.
        sum_num = 0.
        for node2 in g.nodes():
            sum_num += 1
            if g.node[node2]['cooperation'] == g.node[node]['c_str_rep'][node2[0]][node2[1]]:
                rep_num += 1
        g.node[node]['inf_accur'] = rep_num / sum_num
        
    return g


"""
############
# Note:
############
Now the setting is that when people interact directly, they'll only remember their partner's behavior in their 'last_c_rep,'
but they won't update their 'c_str_rep' until the modelupdate phase.


############
# To do list:
############
adding trust rate
"""