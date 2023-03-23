import numpy as np

class Request:
    def __init__(self, vehicle, vehicle_df, grid_df):
        self.__vehicle = vehicle
        self.__vehicle_df = vehicle_df
        self.__grid_df = grid_df
        self.__partial_route_length = 1

    def user_algo(self):
        temp_route = []
        partial_route = []
        dynamic_route = self.__vehicle_df.loc[self.__vehicle.id, 'DynamicRoute']
        reservation_to_release = self.__vehicle_df.loc[self.__vehicle.id, 'ReservationToRelease']
        if not isinstance(reservation_to_release, list) and np.isnan(reservation_to_release):
            temp_route += dynamic_route
        else:
            temp_route += dynamic_route[len(reservation_to_release) - len(dynamic_route):]

        if len(temp_route) > self.__partial_route_length:
            for i in range(self.__partial_route_length):
                partial_route.append(temp_route[i])
        else:
            partial_route = temp_route
        return partial_route

