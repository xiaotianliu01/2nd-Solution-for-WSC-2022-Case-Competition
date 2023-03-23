import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from run.ADP import ADP
import numpy as np
from concurrent import futures

def search(partial_route_length_list, vehicle_maximum_capacity_list, job_maximum_distance_list, route_param_1, route_param_2, budget):

    total_combs = len(partial_route_length_list)*len(vehicle_maximum_capacity_list)*len(job_maximum_distance_list)*len(route_param_1)*len(route_param_2)
    params = [[] for i in range(total_combs)]
    cnt = 0
    for partial_route_length in partial_route_length_list:
        for vehicle_maximum_capacity in vehicle_maximum_capacity_list:
            for job_maximum_distance in job_maximum_distance_list:
                for route_1 in route_param_1:
                    for route_2 in route_param_2:
                        params[cnt] = [partial_route_length, vehicle_maximum_capacity, job_maximum_distance, route_1, route_2]
                        cnt += 1

    estmean = ADP(total_combs, 6, budget, params)
    best_combs = params[int(np.argmin(estmean))]
    best_time = estmean[int(np.argmin(estmean))]
    print("Best Parameter Combination: " + str(best_combs) + " Best Time: " + str(best_time))

if __name__ == '__main__':
    partial_route_length_list = [1]
    vehicle_maximum_capacity_list = [[1, 4], [7, 10]]
    job_maximum_distance_list = [i+1 for i in range(0, 100, 8)]
    route_param_1 = [1, 2, 3, 4]
    route_param_2 = [0, 1, 2, 3]

    budget = 200
    import sys
    import os
    
    futures_list = []

    with futures.ProcessPoolExecutor(max_workers=30) as executor:
        for i in range(len(job_maximum_distance_list)):
            for vehicle_maximum_capacity_sub_list in vehicle_maximum_capacity_list:
                a = executor.submit(search, partial_route_length_list, vehicle_maximum_capacity_sub_list, [job_maximum_distance_list[i]], route_param_1, route_param_2, budget)
                futures_list.append(a)

        for item in futures.as_completed(futures_list):
            if item.exception() is not None:
                print(item.exception())
            else:
                print('success')