# Second-Place-Solution-for-Winter-Simulation-Conference-WSC-2022-Case-Competition
Second Place Solution for [Winter Simulation Conference (WSC) 2022 Case Competition](https://competition.huaweicloud.com/information/1000041743/introduction)

## Create Environment
The codes are implemented with Python, the following packages are required
```bash
numpy
pygame
sortedcontainers
pandas
```
## Run Ranking and Selection to Find the Best Parameter Settings
Run the following
```bash
cd run
python param_search.py
```
You can specify the parameter space in ./run/param_search.py. The searching results will be saved under ./search_logs/.
## Simulate Under Certain Parameter Setting
Run the following
```bash
cd run
python run_file.py --r 100 --c 10 --route-param-1 2 --route-param-2 3 --seed 1 --scenario 2
```
## Visulization Under Certain Parameter Setting
The animation visualization is only applicable when you are not running the codes on a linux server. To see the animation, run the following
```bash
cd run
python run_file_with_animation.py --r 100 --c 10 --route-param-1 2 --route-param-2 3 --seed 1 --scenario 2
```
