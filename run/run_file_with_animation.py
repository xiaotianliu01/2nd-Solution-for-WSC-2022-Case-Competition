import datetime
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from standard.action import Action
from xml_parser.xml_parser import XmlParser
from xml_parser.element_creator import ElementCreator
from config_pack.file_config import FileConfig
from standard.sandbox import Sandbox
from animation.animation_main import AnimationMain
import argparse
from run import gol


class RunFileWithAnimation(Sandbox):
    def __init__(self, xml_file_name=None, seed=0):
        super().__init__()
        self.__xml_file_name = xml_file_name
        if self.__xml_file_name is not None:
            xml_parser = XmlParser()
            gridmover_system_dict = xml_parser.parse_to_dict(self.__xml_file_name)
            element_creator = self.add_child(ElementCreator())
            element_creator.create(gridmover_system_dict, seed)
            self.__on_end = Action().add(element_creator.gridmover_system_handler.end)
            transportation_network_dict = gridmover_system_dict['GridMoverSystem']['TransportationNetwork'] if \
                'TransportationNetwork' in gridmover_system_dict['GridMoverSystem'] else dict()
            self.dimension = eval(
                transportation_network_dict['Dimension']) if 'Dimension' in transportation_network_dict else (
                30, 35)

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
        help='route parameter 2 in routing algorithm')
    parser.add_argument(
        '--scenario',
        type=int,
        default=2,
        help='scenario')
    args = parser.parse_args()
    return args
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    args = get_args()
    param = [1, args.r, args.c, args.route_param_1, args.route_param_2]
    gol._init()
    gol.set_value("param", param)
    logging.basicConfig(level=logging.INFO)
    file_config = FileConfig()
    xml_file_name = file_config.get_input_folder() + '/scenario_' + str(args.scenario) + '.xml'
    # You can change random_seed to get different job generation situations. For example, random_seed=1,2,...
    random_seed = args.seed
    animation_test = RunFileWithAnimation(xml_file_name=xml_file_name, seed=random_seed)
    animation_test.run(duration=datetime.timedelta(days=10))
    animation_test.on_end.invoke()
    animation_main = AnimationMain(animation_test.dimension, random_seed)
    animation_main.run()




