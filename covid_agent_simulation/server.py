from mesa.visualization.ModularVisualization import ModularServer, VisualizationElement
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.modules import ChartModule
from mesa.visualization.UserParam import UserSettableParameter

from .model import CoronavirusModel
from .utils import get_config

import numpy as np


class BackgroundSetter(VisualizationElement):
    def __init__(self, url):
        self.js_code = 'document.getElementsByClassName("world-grid")[0].style.background = ' \
        '"url(' + "'{}'".format(url) +')";'


def agent_portrayal(agent):
    return agent.get_portrayal()


config = get_config('./covid_agent_simulation/configs/designed_shapes.yml')
grid = CanvasGrid(agent_portrayal,
                  config['common']['grid']['cols'],
                  config['common']['grid']['rows'],
                  config['common']['grid']['px_cols'],
                  config['common']['grid']['px_rows'])

# Uncomment to use remote image as a background
# "back" object must be also included in the ModularServer parameters.
# back = BackgroundSetter("https://www.tooploox.com/cdn/academic-program.png-24378a904f32a566ccf799a2dc4bdf8928d75bbe.png")

chart = ChartModule([
    {"Label": "Infected", "Color": "#F40909"},
    {"Label": "Healthy", "Color": "#00C38C"},
    {"Label": "Recovered", "Color": "#006EFF"}],
    data_collector_name='datacollector'
)

model_params = {
    "num_agents":
        UserSettableParameter('slider', "Number of agents", 10, 2, 200, 1,
                              description="Choose how many agents to include in the model"),
    "going_out_prob_mean":
        UserSettableParameter('slider', "Average probability of leaving home", 0.5, 0, 1, 0.1,
                               description="Choose how probably, in general, will be going out"),

    "scenario": UserSettableParameter('choice', 'Scenario', value='store',
                                      choices=['store', 'park', 'forest']),
    "config": config
}


server = ModularServer(CoronavirusModel, [grid, chart], "Coronavirus Model", model_params)
server.port = 8521
