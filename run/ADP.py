import numpy as np
import copy
import random
import json
import os
import time
from run.run_file import main
from run import gol

SERVER_ROOT = os.path.dirname(os.path.abspath(os.path.join(__file__, '../')))

def AGV(id, params, seed):
    param = params[id]
    gol._init()
    gol.set_value("param", param)
    main(True, seed)
    param = gol.get_value('param')
    index = 'output/'
    for num in param:
        index += str(num)
        index += "_"
    index += "/statistics_output.json"
    with open(os.path.join(SERVER_ROOT, index), 'r') as f:
        out_file = json.load(f)
    times = float(out_file['Adjusted Average Job Cycle Time [s]'])
    return times, out_file

def write_reward_log(param, seed, out_file):
    name_idx = "param"
    for i in param:
        name_idx += '_' + str(i)
    with open(os.path.join(SERVER_ROOT, 'search_logs/' + name_idx + '.txt'), 'a+') as f:
        f.write(str(seed) + ' '
                + str(out_file['Total Number of Job Generated']) + ' '
                + str(out_file['Finished Job']['Quantity']) + ' '
                + str(out_file['Unfinished Job']['Quantity']) + ' '
                + str(out_file['Delay Due To Waiting for Pick Up (Job) [s]']) + ' '
                + str(out_file['Delay Due To Traffic Congestion (Loaded Vehicle) [s]']) + ' '
                + str(out_file['Delay Due To Traffic Congestion (Empty Vehicle) [s]']) + ' '
                + str(out_file['Duration Without Load [s]']) + ' '
                + str(out_file['Adjusted Average Job Cycle Time [s]']) + '\n')


def ADP(k, n0, T, params):
    X0 = np.zeros([n0,k])
    V = np.zeros(k)
    budgets = T
    for i in range(n0):
        seed = random.randint(0, 10000000)
        for j in range(k):
            budgets -= 1
            X0[i][j], out_file = AGV(j, params, seed)
            write_reward_log(params[j], seed, out_file)
    
    estmean = np.mean(X0, axis = 0)
    estvar = np.var(X0, axis = 0)
    N = n0*np.ones_like(estmean)
    pv = estvar/N

    start = time.time()

    for budget in range(budgets):
        id1 = int(np.argmin(estmean))
        cm = [i for i in range(k)]
        del cm[id1]
        
        for i in range(k):
            nv = copy.deepcopy(pv)
            M = copy.deepcopy(N)
            M[i] = N[i] + 1
            nv[i] = estvar[i]/M[i]
            
            V1 = np.zeros(k-1)
            for b in range(k-1):
                V1[b] = (estmean[id1]-estmean[cm[b]])**2/(nv[id1]+nv[cm[b]])

            V[i] = np.min(V1)
        
        id2 = int(np.argmax(V))
        mm = estmean[id2]
        seed = random.randint(0, 10000000)
        x, out_file = AGV(id2, params, seed)
        write_reward_log(params[id2], seed, out_file)
        estmean[id2] = (estmean[id2]*N[id2]+x)/(N[id2]+1)
        estvar[id2] = ((N[id2]-1)*estvar[id2]+(x-mm)*(x-estmean[id2]))/N[id2]
        N[id2] = N[id2]+1
        pv[id2]=estvar[id2]/N[id2]
    
    return estmean
