import sys
from run import gol
import copy

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.cost = sys.maxsize

class MyPoint:
    def __init__(self, x, y, time, previous):
        self.x = x
        self.y = y
        self.time = time
        self.previous = previous


class Route:
    def __init__(self, transportation_network, vehicle, start_square_unit, end_square_unit):
        self.__transportation_network = transportation_network
        self.__vehicle = vehicle
        self.__start_square_unit = start_square_unit
        self.__end_square_unit = end_square_unit
        self.__obstacle_set = []
        self.__open_set = []
        self.__close_set = []
        self.__dimension_length = self.__transportation_network.dimension[0]
        self.__dimension_width = self.__transportation_network.dimension[1]
        self.__grid_df = self.__transportation_network.grid_df
        self.__vehicle_df = self.__transportation_network.vehicle_df

        param = gol.get_value('param')
        self.route_param_1 = int(param[3]) # running constrains
        self.route_param_2 = int(param[4]) # stop constrains


    def default_algo_to_generate_route(self):
        """
        Call __astar_path() to create a full route of vehicle

        Here, the parking positions of other vehicles are also used as obstacles and the vehicle is not allowed to pass.
        The user does not need to do the same.

        @return self.__astar_path() (a path: <List<Tuple<int, int>, Tuple<int, int>, ...>>)
        """
        self.__obstacle_set = set(self.__grid_df.loc[self.__grid_df['IsObstacle'] == True]['SquareUnitIndex'])

        for row_vehicle in self.__vehicle_df.itertuples():
            current_vehicle = getattr(row_vehicle, "Vehicle")
            if current_vehicle is not self.__vehicle: 
                self.__obstacle_set.add(current_vehicle.park_position)
        return self.__astar_path()

    def __astar_path(self):
        """
        Use A* algorithm to create a full route of the vehicle

        @return self.__build_path(p) (a path: <List<Tuple<int, int>, Tuple<int, int>, ...>>)
        """
        start_point = Point(self.__start_square_unit[0], self.__start_square_unit[1])
        start_point.cost = 0 
        self.__open_set.append(start_point)
        while True:
            index = self.__select_point_in_open_set()
            if index < 0:
                print('No path found')
                return []
            p = self.__open_set[index]

            if self.__is_end_point(p):
                return self.__build_path(p)

            del self.__open_set[index]
            self.__close_set.append(p)

            x = p.x
            y = p.y
            self.__process_point(x - 1, y, p)
            self.__process_point(x, y - 1, p)
            self.__process_point(x + 1, y, p)
            self.__process_point(x, y + 1, p)

    def __base_cost(self, p):
        """Distance to start point"""
        x_dis = abs(p.x - self.__start_square_unit[0])
        y_dis = abs(p.y - self.__start_square_unit[1])
        return x_dis + y_dis

    def __heuristic_cost(self, p):
        """Distance to end point"""
        x_dis = abs(self.__end_square_unit[0] - p.x)
        y_dis = abs(self.__end_square_unit[1] - p.y)
        return x_dis + y_dis

    def __total_cost(self, p):
        return self.__base_cost(p) + self.__heuristic_cost(p)

    def __is_valid_point(self, x, y):
        if x < 0 or y < 0:
            return False
        if x >= self.__dimension_length or y >= self.__dimension_width:
            return False
        return not self.__is_obstacle(x, y)

    def __is_obstacle(self, x, y):
        for point in self.__obstacle_set:
            if point[0] == x and point[1] == y:
                return True
        return False

    def __is_in_point_set(self, p, point_set):
        for point in point_set:
            if point.x == p.x and point.y == p.y:
                return True
        return False

    def __is_in_open_set(self, p):
        return self.__is_in_point_set(p, self.__open_set)

    def __is_in_close_set(self, p):
        return self.__is_in_point_set(p, self.__close_set)

    def __is_start_point(self, p):
        return p.x == self.__start_square_unit[0] and p.y == self.__start_square_unit[1]

    def __is_end_point(self, p):
        return p.x == self.__end_square_unit[0] and p.y == self.__end_square_unit[1]

    def __process_point(self, x, y, parent):
        if not self.__is_valid_point(x, y):
            return

        p = Point(x, y)

        if self.__is_in_close_set(p):
            return

        if not self.__is_in_open_set(p):
            p.parent = parent
            p.cost = self.__total_cost(p)
            self.__open_set.append(p)

    def __select_point_in_open_set(self):
        index = 0
        selected_index = -1
        min_cost = sys.maxsize
        for p in self.__open_set:
            cost = p.cost
            if cost < min_cost:
                min_cost = cost
                selected_index = index
            index += 1
        return selected_index

    def __build_path(self, p):
        path = []
        while True:
            path.insert(0, (p.x, p.y))
            if self.__is_start_point(p):
                break
            else:
                p = p.parent
        return path

    def get_grids_taken(self, park_positions):

        import numpy as np
        import copy
        working_time = 4

        self.__obstacle_set = set(copy.deepcopy(self.__grid_df.loc[self.__grid_df['IsObstacle'] == True]['SquareUnitIndex']))  # set
        grid_traffic = []
        max_route_length = 0
        for emu_vehicle in self.__vehicle_df.itertuples():
            current_vehicle = getattr(emu_vehicle, "Vehicle")
            status = getattr(emu_vehicle, "Status")
            if current_vehicle is not self.__vehicle:
                dynamic_route = copy.deepcopy(self.__vehicle_df.loc[current_vehicle.id, 'DynamicRoute'])
                reservation_to_release = copy.deepcopy(self.__vehicle_df.loc[current_vehicle.id, 'ReservationToRelease'])
                if (isinstance(dynamic_route, list) == False and np.isnan(dynamic_route) == True):
                    continue
                if (isinstance(reservation_to_release, list) == False and np.isnan(reservation_to_release) == True):
                    dynamic_route = dynamic_route
                else:
                    dynamic_route = dynamic_route[len(reservation_to_release) - len(dynamic_route):]
                grid_traffic.append(dynamic_route)
                max_route_length = np.max([max_route_length, len(dynamic_route)])

        grids_taken = [[]for i in range(10000)]


        for x in range(self.__dimension_length):
            for y in range(self.__dimension_width):
                if( x==self.__start_square_unit[0] and y==self.__start_square_unit[1]):
                    continue
                occupied = self.__grid_df.loc[self.__grid_df['SquareUnitIndex'] == (x, y)]['OccupiedVehicle']
                if ("NaN" not in str(occupied)):
                    for i in range(working_time+self.route_param_2):
                        grids_taken[i].append((x, y))

        for route in grid_traffic:
            if (len(route) == 0):
                continue
            for i in range(working_time+self.route_param_2):
                grids_taken[i].append(route[0])
            for i in range(len(route)):
                for j in range(self.route_param_1):
                    if (i - j >= 0):
                        grids_taken[i - j].append(route[i])
                    grids_taken[i + j + 1].append(route[i])
            for i in range(working_time+self.route_param_2):
                grids_taken[i].append(route[len(route)-1])

        return grids_taken

    def get_next(self, p, visit_log_, grids_taken, status):
        visit_log = visit_log_
        if (status == "Idle"):
            all_moves = [[0, 1], [0, -1], [1, 0], [-1, 0]]
        else:
            all_moves = [[1, 0], [-1, 0], [0, 1], [0, -1]]
        next_possible_points = []
        for move in all_moves:
            next = MyPoint(p.x + move[0], p.y + move[1], p.time + 1, p)
            if(self.__is_obstacle(next.x, next.y)):
                continue
            if(self.__is_valid_point(next.x, next.y) == False):
                continue
            if(next.time < len(grids_taken) and (next.x, next.y) in grids_taken[next.time]):
                continue
            if( visit_log[next.time][next.x][next.y] > 0):
                continue
            if(p.previous is not None and p.previous.x == next.x and p.previous.y == next.y):
                continue
            next_possible_points.append(next)
            visit_log[next.time][next.x][next.y] = 1
        return next_possible_points, visit_log

    def BFS(self, grids_taken, status):

        import queue
        import numpy as np
        import copy

        start_p = MyPoint(self.__start_square_unit[0], self.__start_square_unit[1], 0, None)
        end_p = [self.__end_square_unit[0], self.__end_square_unit[1]]
        Q = queue.Queue()
        Q.put(start_p)
        visit_log = np.zeros([10000, self.__dimension_length, self.__dimension_width])
        visit_log[start_p.time][start_p.x][start_p.y] = 1
        while(Q.empty() == False):
            p = Q.get()
            next_avaliable_points, visit_log = self.get_next(p, visit_log, grids_taken, status)
            for next_point in next_avaliable_points:
                if(next_point.x == end_p[0] and next_point.y == end_p[1]):
                    route = []
                    route_p = next_point
                    while(True):
                        route.append((route_p.x, route_p.y))
                        if(route_p.x == start_p.x and route_p.y == start_p.y):
                            break
                        route_p = route_p.previous
                    route.reverse()
                    return route
                Q.put(next_point)
        return None

    def user_algo(self):

        import copy

        self.__obstacle_set = set(
            copy.deepcopy(self.__grid_df.loc[self.__grid_df['IsObstacle'] == True]['SquareUnitIndex']))

        park_positions = []
        for row_vehicle in self.__vehicle_df.itertuples():
            current_vehicle = getattr(row_vehicle, "Vehicle")
            if current_vehicle is not self.__vehicle:
                park_positions.append(current_vehicle.park_position)
            else:
                status = getattr(row_vehicle, "Status")

        for row_vehicle in self.__vehicle_df.itertuples():
            current_vehicle = getattr(row_vehicle, "Vehicle")
            if current_vehicle is not self.__vehicle:
                self.__obstacle_set.add(current_vehicle.park_position)

        gids_taken = self.get_grids_taken(park_positions)

        path = self.BFS(gids_taken, status)

        return path