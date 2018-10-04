# -*- coding: utf-8 -*-
"""
Created on Sun Jun 10 13:18:11 2018
@author: Xinyue Pan
"""
import globals as gl
import phases as ph
import calculation as calc
import datetime
import os
import matplotlib.pyplot as plt
import numpy as np


if __name__ == "__main__":
    try:
        currentDT = datetime.datetime.now()
        start_h = str(currentDT.hour).zfill(2) 
        start_m = str(currentDT.minute).zfill(2)
        
        j = 0
        
        # create network
        g = ph.creat_network(gl.rows, gl.cols, gl.neigh_num)
        g = ph.network_initialization(g, gl.cols, gl.c_strategy_init, gl.g_strategy_init, gl.randomseed)
        
        # initialize stats
        if not os.path.exists(gl.folder_name):
            os.makedirs(gl.folder_name)
        f = open(gl.filename, 'w')
        fp = open(gl.payoffFile, 'w')
        fm = open(gl.modelAccuracy, 'w')
        
        c_rate = []
        g_rate = []
#        trust_rate = []
        inf_accur = [[0.] * gl.str_num for i in range(gl.iteration)]
        aver_payoff = [[0.] * gl.str_num for i in range(gl.iteration)]
        strategies = [[0.] * gl.str_num for i in range(gl.iteration)]
        
        print("initialized.")
        
        # for each iteration
        while j < gl.iteration:            
            # run different evolutionary phases
            # cooperation
            group_num = len(list(g.edges()))  # it's now a full interaction
            g = ph.cooperation(g, group_num, gl.subset_size, gl.c, gl.r)
            
            # look into everyone's last action, # of known cooperators divided by the sum of known cooperators and defectors
            c_rate.append(calc.count_in_nodes(g, g.node(), 'last_action', 'C') / float(calc.count_in_nodes(g, g.node(), 'last_action', 'C') + calc.count_in_nodes(g, g.node(), 'last_action', 'D')))
            
            # gossiping phase
            g = ph.gossiping(g, gl.gossiper_num, gl.target_num, gl.receiver_num, gl.gc)
            g_rate.append(calc.count_in_nodes(g, g.node(), 'last_gossip', 'G') / float(calc.count_in_nodes(g, g.node(), 'last_gossip', 'G') + calc.count_in_nodes(g, g.node(), 'last_gossip', 'N')))
            
            # payoff data
            i = 0
            for cstr in gl.c_strategy_clean:
                for gstr in gl.g_strategy_clean:
                    aver_payoff[j][i] = calc.aver_in_nodes_combined(g, g.nodes(), 'aver_payoff', 'cooperation', cstr, 'gossip', gstr)
                    i += 1
                    
            # forgetting and reputation updating phase
            g = ph.modelupdate(g, gl.f_victim, gl.f_target_num, gl.f_rate, gl.rs, gl.rep_diff)
            
            # information accuracy data
            i = 0
            for cstr in gl.c_strategy_clean:
                for gstr in gl.g_strategy_clean:
                    inf_accur[j][i] = calc.aver_in_nodes_combined(g, g.nodes(), 'inf_accur', 'cooperation', cstr, 'gossip', gstr)
                    i += 1
        
            # reproduction
            g = ph.reproduction(g, gl.cols, gl.fermi_num, 'aver_payoff', gl.s, gl.mu_rate, gl.c_strategy, gl.g_strategy)
            
            # proportion data
            i = 0
            for cstr in gl.c_strategy_clean:
                for gstr in gl.g_strategy_clean:
                    strategies[j][i] = calc.calculate_comb_prop(g, 'cooperation', cstr, 'gossip', gstr)
                    i += 1
            
#            # draw network
#            if gl.network_num != 0:
#                if j % int(gl.iteration / gl.network_num) == 0 or j == gl.iteration - 1:
#                    # the first parameter is color, the second one is label
#                    calc.draw_network(g, 'last_action', 'cooperation', gl.folder_name, gl.condition_name, gl.randomseed, j, gl.color_book)
#                    calc.draw_network(g, 'cooperation', 'gossip', gl.folder_name, gl.condition_name, gl.randomseed, j, gl.color_book)
#                    calc.draw_network(g, 'gossip', 'cooperation', gl.folder_name, gl.condition_name, gl.randomseed, j, gl.color_book)
#               
            if j % 10 == 0:
                print("time:", j)
        
            # update iteration count
            j += 1
        
        # proportion plot
        i = 0
        for cstr in gl.c_strategy_clean:
            for gstr in gl.g_strategy_clean:
                if gstr == 'G':
                    plt.plot([strategies[k][i] for k in range(gl.iteration)], '-', color = gl.color_book.get(cstr))
                elif gstr == 'N':
                    plt.plot([strategies[k][i] for k in range(gl.iteration)], '--', color = gl.color_book.get(cstr))
                i += 1
        plt.ylim([-0.1, 1.1])
        plt.legend(gl.strategy_name)
        plt.xlim([0, gl.iteration])
        plt.title('Proportion')
        fig = plt.gcf()
#        plt.show()
        fig.savefig(gl.folder_name + '/' + gl.condition_name + '_' + str(gl.randomseed) + '_proportion.png')
        plt.close()
        
        # payoff plot
        i = 0
        for cstr in gl.c_strategy_clean:
            for gstr in gl.g_strategy_clean:
                if gstr == 'G':
                    plt.plot([aver_payoff[k][i] for k in range(gl.iteration)], '-', color = gl.color_book.get(cstr))
                elif gstr == 'N':
                    plt.plot([aver_payoff[k][i] for k in range(gl.iteration)], '--', color = gl.color_book.get(cstr))
                i += 1
        aver_payoff_all = list(np.sum(np.array(aver_payoff) * np.array(strategies), axis = 1))
        plt.plot(aver_payoff_all, '--', color = gl.color_book.get('AVG'))
        lengendlist = [gl.strategy_name[a] for a in range(gl.str_num)]
        lengendlist.append('AVG')
        plt.legend(lengendlist)
        plt.xlim([0, gl.iteration])
        plt.title('Accumulated payoff')
        fig = plt.gcf()
#        plt.show()
        fig.savefig(gl.folder_name + '/' + gl.condition_name + '_' + str(gl.randomseed) + '_aver_payoff.png')
        plt.close()
        
        # model_accuracy plot
        i = 0
        for cstr in gl.c_strategy_clean:
            for gstr in gl.g_strategy_clean:
                if gstr == 'G':
                    plt.plot([inf_accur[k][i] for k in range(gl.iteration)], '-', color = gl.color_book.get(cstr))
                elif gstr == 'N':
                    plt.plot([inf_accur[k][i] for k in range(gl.iteration)], '--', color = gl.color_book.get(cstr))
                i += 1
        inf_accur_all = list(np.sum(np.array(inf_accur) * np.array(strategies), axis = 1))
        plt.plot(inf_accur_all, '--', color = gl.color_book.get('AVG'))
        lengendlist = [gl.strategy_name[a] for a in range(gl.str_num)]
        lengendlist.append('AVG')
        plt.legend(lengendlist)
#        plt.ylim([-0.1, 1.1])
        plt.xlim([0, gl.iteration])
        plt.title('Information accuracy')
        fig = plt.gcf()
#        plt.show()
        fig.savefig(gl.folder_name + '/' + gl.condition_name + '_' + str(gl.randomseed) + '_inf_accur.png')
        plt.close()
        
        # rate plot
        plt.plot(c_rate, '--', color = gl.color_book.get('C'))
        plt.plot(g_rate, '--', color = gl.color_book.get('G'))
        plt.plot(inf_accur_all, '-', color = gl.color_book.get('G'))
        plt.legend(['cooperation rate', 'gossip rate', 'model accuracy'])
        plt.ylim([-0.1, 1.1])
        plt.xlim([0, gl.iteration])
        plt.title('Rate')
        fig = plt.gcf()
#        plt.show()
        fig.savefig(gl.folder_name + '/' + gl.condition_name + '_' + str(gl.randomseed) + '_rate.png')
        plt.close()
        
        # proportion file
        f.write('Step')
        for i in gl.strategy_name:
            f.write('\t' + i)
        f.write('\tCR\tGR\n')
        for j in range(gl.iteration):
            f.write(str(j))
            for i in range(gl.str_num):
                f.write('\t' + str(format(strategies[j][i], '.2f')))
            f.write('\t' + str(format(c_rate[j], '.2f')) + '\t' + str(format(g_rate[j], '.2f')) + '\n')
        
        # payoff file
        fp.write('Step')
        for i in gl.strategy_name:
            fp.write('\t' + i)
        fp.write('\tAVG\n')
        for j in range(gl.iteration):
            fp.write(str(j))
            for i in range(gl.str_num):
                fp.write('\t' + str(format(aver_payoff[j][i], '.2f')))
            fp.write('\t' + str(format(aver_payoff_all[j], '.2f')) + '\n')
          
        # model accuracy
        fm.write('Step')
        for i in gl.strategy_name:
            fm.write('\t' + i)
        fm.write('\tAVG\n')
        for j in range(gl.iteration):
            fm.write(str(j))
            for i in range(gl.str_num):
                fm.write('\t' + str(format(inf_accur[j][i], '.2f')))
            fm.write('\t' + str(format(inf_accur_all[j], '.2f')) + '\n')
            
        currentDT = datetime.datetime.now()
        end_h = str(currentDT.hour).zfill(2)
        end_m = str(currentDT.minute).zfill(2)
        
    finally:
        # close output result files
        f.close()
        fp.close()
        fm.close()
        
        # print the time cost
        print('\nstart: ', start_h, ':', start_m, '\nend:   ', end_h, ':', end_m, '\nStay optimistic!')