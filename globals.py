# -*- coding: utf-8 -*-
"""
Created on Sun Jun 10 13:06:05 2018
@author: Xinyue Pan
"""
import random
import calculation as calc


############
# setting up
############
randomseed = random.randrange(100000)
#randomseed = 24884

iteration = 1500

rows = 10
cols = 10
n = rows * cols 	# number of agents
# number of neighbors: 4, 8, or 12
neigh_num = 8

# strategies
# the strategies used in exploration
c_strategy = ['D', 'O2']
g_strategy = ['N']
# initial strategies
c_strategy_init = ['D']
g_strategy_init = ['N']
# all the strategies possibly existing in the population
c_strategy_all = c_strategy + c_strategy_init
g_strategy_all = g_strategy + g_strategy_init
c_strategy_clean = calc.delete_duplicate(c_strategy_all)
g_strategy_clean = calc.delete_duplicate(g_strategy_all)
"""
C: always cooperate
D: always defect
O2: do what the majority did last time regardless of their actual strategy
O4: only defect when it's sure that the partner is pure defector regardless the partner's last action
"""


############
# cooperation parameters
############
subset_size = 2  # two people play a cooperation game
l = 2
r = 2 * l / (l + 1)
#r = 1.75  # multification factor
#l = r / (2 - r)
c = 2 / (r - 1)  # contribution
# This enables the payoff matrix to be {(C, C): (1, 1), (C, D): (-1, 2), (D, C): (2, -1), (D, D): (0, 0)} in a 2-agent PGG, i.e., a CG.


############
# gossip parameters
############
gossiper_num = int(n * 1)  # how many people act in the gossiping phase
receiver_num = 8  # how many people will a gossiper gossip to
"""
Remember that when choosing receivers, use the mininum of gossip_size and # of neighbors.
"""
target_num = 20  # how many people will a gossiper gossip about at one time

gc = (c * (r - 1)) / 2 * 0  # the cost of gossiping about one target to one person
"""
It should be adjusted as the ratio of the # of gossipers activated to the # of PGG interactions per iteration changes.

It depends on the expectation of payoff in the current population (also depends on how many cooperators are there).
If in each iteration, 2 people are chosen to play CG and 1 gossiper is chosen, the expectation of payoff when p(C) = p(D) is 0.5. Therefore, the cost is 0.2 / (0.5 * 2) = 20% of the expectation of payoff.
However, as P(C) decreases, the relative cost of gossip increases.

Need a double thought.
"""

rep_diff = 10  # # of gossip needed for a 50% probability of knowing someone's true strategy
rs = 0.3  # the shape of the curve which convert # of gossip into the cognitive model of the partner's strategy

f_victim = n
f_target_num = n
f_rate = 0.05


############
# reproduction parameters
############
fermi_num = int(n * 0.1)  # how many agents we apply Fermi rule to. Would that affect?
s = 5. / c
"""
c equals to the difference between the highest and the lowest payoff.
It also needs a double thought.
"""
mu_rate = 0.05


############
# plotting and files
############
# # of network plots
network_num = 5

# data
strategy_name = []

for cstr in c_strategy_clean:
    for gstr in g_strategy_clean:
        strategy_name.append(cstr + gstr)

c_str_num = len(c_strategy_clean)
g_str_num = len(g_strategy_clean)
str_num = c_str_num * g_str_num

# files
initstr = ''.join(c_strategy_init) + ''.join(g_strategy_init)
allstrategies = ''.join(c_strategy) + ''.join(g_strategy)
condition_name = 'init' + initstr + '_all' + allstrategies + '_mu' + str(format(mu_rate, '.2f')) + '_neigh_num' + str(neigh_num) + '_c' + str(format(c, '.2f')) + '_r' + str(format(r, '.2f')) + '_l' + str(format(l, '.2f')) + '_gc' + str(format(gc, '.2f'))
folder_name = './outputs/' + condition_name
# files to save
filename = folder_name + '/' + condition_name + '_' + str(randomseed) + '_proportion.txt'
payoffFile = folder_name + '/' + condition_name + '_' + str(randomseed) + '_payoff.txt'
modelAccuracy = folder_name + '/' + condition_name + '_' + str(randomseed) + '_model_accuracy.txt'

# plotting
#color_book = {'C': '#7ACFAD', 'D': '#FFC6DC', 'O1': '#878B96', 'O2': '#FF5319', 'O3': '#878B96', 'O4': '#9189F6', 'NA': '#878B96', 'G': '#E3BB6B', 'N': '#5ED3F4', 'AVG': '#372F22'}
#color_book = {'C': '#7C8491', 'D': '#D7E1E5', 'O1': '#878B96', 'O2': '#f8ebd8', 'O3': '#878B96', 'O4': '#F5E2D0', 'NA': '#878B96', 'G': '#9B887D', 'N': '#6B5152', 'AVG': '#372F22'}
#color_book = {'C': '#5B0E06', 'D': '#E8D8BB', 'O1': '#E4EDE2', 'O2': '#E0FCA3', 'O3': '#E4EDE2', 'O4': '#26857B', 'NA': '#E4EDE2', 'G': '#7C8491', 'N': '#D7E1E5', 'AVG': '#7F6449'}
color_book = {'C': '#af967f', 'D': '#204a97', 'O1': '#d3d0cd', 'O2': '#70ac9b', 'O3': '#d3d0cd', 'O4': '#99533e', 'NA': '#d3d0cd', 'G': '#2b5679', 'N': '#aca9a6', 'AVG': '#292929'}