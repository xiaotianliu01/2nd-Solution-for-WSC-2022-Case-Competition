import datetime
import sys
import numpy as np
import copy
from run import gol

class Deployment:
    def __init__(self, available_job_df, vehicle_df):
        self.__available_job_df = available_job_df
        self.__vehicle_df = vehicle_df
        param = gol.get_value('param')
        self.__vehicle_maximum_capacity = int(param[1])
        self.__job_maximum_distance = int(param[2])

    def __get_minimum_arrival_time(self, job_maximum_waiting_time):
        minimum_arrival_time = datetime.datetime.now() - datetime.timedelta(seconds=job_maximum_waiting_time)
        return minimum_arrival_time

    def __get_distance(self, start_square_unit_index, end_square_unit_index):
        return abs(end_square_unit_index[0] - start_square_unit_index[0]) + abs(end_square_unit_index[1] - start_square_unit_index[1])

    def __get_distance_all_jobs(self, current_job, job_list, vehicle, current_staus):

        dynamic_route = self.__vehicle_df.loc[vehicle.id, 'DynamicRoute']
        reservation_to_release = self.__vehicle_df.loc[vehicle.id, 'ReservationToRelease']
        first_job_distance = 0
        if (isinstance(dynamic_route, list) == False and np.isnan(dynamic_route) == True):
            if (current_staus == 'Pick'):
                first_job_distance = self.__get_distance(job_list[0].picking_posistion, job_list[0].delivery_position)
            elif (current_staus == 'Delivery'):
                first_job_distance = 0
        else:
            if (isinstance(reservation_to_release, list) == False and np.isnan(
                    reservation_to_release) == True):
                dynamic_route = dynamic_route
            else:
                dynamic_route = dynamic_route[len(reservation_to_release) - len(dynamic_route):]
            if(dynamic_route == []):
                if (current_staus == 'Pick'):
                    first_job_distance = self.__get_distance(job_list[0].picking_position,
                                                             job_list[0].delivery_position)
                elif (current_staus == 'Delivery'):
                    first_job_distance = 0
            else:
                current_pos = dynamic_route[0]
                if (current_staus == 'Pick'):
                    first_job_distance = 1 + self.__get_distance(current_pos, job_list[0].picking_position) + self.__get_distance(job_list[0].picking_position, job_list[0].delivery_position)

                elif (current_staus == 'Delivery'):
                    first_job_distance = 1 + self.__get_distance(current_pos, job_list[0].delivery_position)

        full_distance = first_job_distance
        for job_index in range(1, len(job_list)):
            full_distance += self.__get_distance(job_list[job_index-1].delivery_position, job_list[job_index].picking_position)
            full_distance += self.__get_distance(job_list[job_index].picking_position,
                                                 job_list[job_index].delivery_position)
        full_distance += self.__get_distance(job_list[-1].delivery_position, current_job.picking_position)
        return full_distance

    def user_algo(self):

        job_maximum_waiting_time = 300  # The maximum waiting time. Adjust according to the specific situation of the system

        # Distinguish whether the job has been waiting for a long time according to the arrival time of the job
        long_wait_job_df = self.__available_job_df.loc[
            self.__available_job_df['ArrivalTime'] < self.__get_minimum_arrival_time(job_maximum_waiting_time)]

        job_id_list = long_wait_job_df['JobId'].tolist()

        remaining_job_df = self.__available_job_df[
            ~self.__available_job_df['JobId'].isin(job_id_list)]

        vehicle_to_jobs_dict = {}
        vehicle_to_jobs_dict.update(
            self.user__get_vehicle_to_jobs_dict(long_wait_job_df, self.__vehicle_df, sys.maxsize))
        vehicle_to_jobs_dict.update(
            self.user__get_vehicle_to_jobs_dict(remaining_job_df, self.__vehicle_df, self.__job_maximum_distance))

        # Copy a previous allocation from vehicle_df
        all_vehicle_to_jobs_dict = {}
        for row_vehicle in self.__vehicle_df.itertuples():
            if getattr(row_vehicle, "JobList") is not np.nan:
                all_vehicle_to_jobs_dict[getattr(row_vehicle, "Vehicle")] = getattr(row_vehicle,
                                                                                    "JobList").copy() 
            else:
                all_vehicle_to_jobs_dict[getattr(row_vehicle, "Vehicle")] = np.nan

        # Compare all_vehicle_to_jobs_dict with vehicle_to_jobs_dict and add and delete on all_vehicle_to_jobs_dict
        for vehicle, jobs in vehicle_to_jobs_dict.items():
            for job in jobs:
                for vehicle_key in all_vehicle_to_jobs_dict.keys():
                    if isinstance(all_vehicle_to_jobs_dict[vehicle_key], list) and job in all_vehicle_to_jobs_dict[
                        vehicle_key]:
                        
                        all_vehicle_to_jobs_dict[vehicle_key].remove(job)
                        if len(all_vehicle_to_jobs_dict[vehicle_key]) == 0:
                            all_vehicle_to_jobs_dict[vehicle_key] = np.nan
                        break
            if isinstance(all_vehicle_to_jobs_dict[vehicle], list):
                all_vehicle_to_jobs_dict[vehicle] += jobs
            else:
                all_vehicle_to_jobs_dict[vehicle] = jobs

        return all_vehicle_to_jobs_dict

    def user__get_vehicle_to_jobs_dict(self, job_df, vehicle_df, distance):
        import itertools
        best_dict = {}
        min_distance = 10000
        jobbs = []
        for temp_row_job in job_df.itertuples():
            jobbs.append(temp_row_job)
        if(len(jobbs) > 4):
            job_permutations = [jobbs]
        else:
            job_permutations = list(itertools.permutations(jobbs))

        for jobs in job_permutations:
            all_jobs = list(jobs)
            vehicle_to_jobs_dict = {}
            sum_distance = 0
            for row_job in all_jobs:
                job_vehicle_distance = distance  # Used to limit the maximum distance between work and vehicle
                target_vehicle = None
                job_vehicle_current_distance = sys.maxsize  # It is used to store the calculated distance of the job in the previously assigned vehicle, if applicable
                for row_vehicle in vehicle_df.itertuples():
                    current_staus = getattr(row_vehicle, "Status")

                    current_job_list = getattr(row_vehicle, "JobList")
                    current_vehicle = getattr(row_vehicle, "Vehicle")
                    if current_staus == 'Park':
                        continue

                    if not isinstance(current_job_list, list) and np.isnan(current_job_list):

                        temp_distance = self.__get_distance(getattr(row_job, "Job").picking_position,
                                                            getattr(row_vehicle, "StartPosition"))

                        if temp_distance < job_vehicle_distance:
                            job_vehicle_distance = temp_distance
                            target_vehicle = current_vehicle
                    else:
                        if getattr(row_job, "Job") in current_job_list:
                            if getattr(row_job, "Job") == current_job_list[0]:
                                job_vehicle_current_distance = self.__get_distance(getattr(row_job, "Job").picking_position,
                                                                                   getattr(row_vehicle, "StartPosition"))
                            else:

                                job_vehicle_current_distance = self.__get_distance_all_jobs(
                                    getattr(row_job, "Job"),
                                    current_job_list[:current_job_list.index(getattr(row_job,"Job"))], current_vehicle, current_staus)

                        elif len(current_job_list) < self.__vehicle_maximum_capacity:
                            if current_vehicle in vehicle_to_jobs_dict.keys():
                                if len(vehicle_to_jobs_dict[current_vehicle]) + len(
                                        current_job_list) < self.__vehicle_maximum_capacity:
                                    
                                    temp_distance = self.__get_distance_all_jobs(getattr(row_job, "Job"),
                                                                        current_job_list, current_vehicle, current_staus)

                                    if temp_distance < job_vehicle_distance:
                                        job_vehicle_distance = temp_distance
                                        target_vehicle = current_vehicle
                            else:
                                temp_distance = self.__get_distance_all_jobs(getattr(row_job, "Job"), current_job_list, current_vehicle, current_staus)
                                if temp_distance < job_vehicle_distance:
                                    job_vehicle_distance = temp_distance
                                    target_vehicle = current_vehicle

                sum_distance += job_vehicle_distance

                if target_vehicle is not None:
                    if job_vehicle_current_distance < sys.maxsize:
                        if job_vehicle_distance < job_vehicle_current_distance:
                            if target_vehicle in vehicle_to_jobs_dict:
                                vehicle_to_jobs_dict[target_vehicle].append(getattr(row_job, "Job"))
                            else:
                                vehicle_to_jobs_dict[target_vehicle] = [getattr(row_job, "Job")]
                    else:
                        if target_vehicle in vehicle_to_jobs_dict:
                            vehicle_to_jobs_dict[target_vehicle].append(getattr(row_job, "Job"))
                        else:
                            vehicle_to_jobs_dict[target_vehicle] = [getattr(row_job, "Job")]

            if(sum_distance < min_distance):
                min_distance = sum_distance
                best_dict = vehicle_to_jobs_dict

        return best_dict
