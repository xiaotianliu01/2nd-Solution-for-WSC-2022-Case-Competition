import datetime as dt
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from standard.action import Action
from xml_parser.xml_parser import XmlParser
from xml_parser.element_creator import ElementCreator
from config_pack.file_config import FileConfig
from standard.sandbox import Sandbox
import argparse
from run import gol

class RunFile(Sandbox):
    def __init__(self, xml_file_name, seed=0):
        super().__init__()
        self.__xml_file_name = xml_file_name

        file_name = self.__xml_file_name
        xml_parser = XmlParser()
        gridmvoer_system_dict = xml_parser.parse_to_dict(file_name)
        creator = self.add_child(ElementCreator())
        creator.create(gridmvoer_system_dict, seed)

        self.__on_end = Action().add(creator.gridmover_system_handler.end)

    @property
    def on_end(self):
        return self.__on_end

def get_args():
    parser = argparse.ArgumentParser(description='AGV')
    parser.add_argument(
        '--r',
        type=int,
        default=64,
        help='maximum distance in deployment algorithm')
    parser.add_argument(
        '--c',
        type=int,
        default=10,
        help='maximum capacity in deployment algorithm')
    parser.add_argument(
        '--route-param-1',
        type=int,
        default=2,
        help='route parameter 1 in routing algorithm')
    parser.add_argument(
        '--route-param-2',
        type=int,
        default=3,
        help='route parameter 2 in routing algorithm')
    parser.add_argument(
        '--seed',
        type=int,
        default=1,
        help='random seed for the system')
    parser.add_argument(
        '--scenario',
        type=int,
        default=2,
        help='scenario')
    args = parser.parse_args()
    return args
    
def main(param_search, seed):
    if(param_search == False):
        args = get_args()
        param = [1, args.r, args.c, args.route_param_1, args.route_param_2]
        gol._init()
        gol.set_value("param", param)
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.INFO)
        logging.disable(level=logging.INFO)
        logging.disable(level=logging.CRITICAL)
    file_config = FileConfig()
    xml_file_name = file_config.get_input_folder() + '/scenario_' + str(args.scenario) + '.xml'
    sim_start_time = dt.datetime.now()
    # You can change random_seed to get different job generation situations. For example, random_seed=1,2,...
    if(param_search == False):
        random_seed = args.seed
    else:
        random_seed = seed
    main = RunFile(xml_file_name=xml_file_name, seed=random_seed)
    main.run(duration=dt.timedelta(days=10))
    main.on_end.invoke()
    sim_end_time = dt.datetime.now()
    logging.info('CPU time is {}'.format((sim_end_time - sim_start_time).total_seconds()))

if __name__ == '__main__':
    main(False, 0)