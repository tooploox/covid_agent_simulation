from mesa.visualization.ModularVisualization import ModularServer, VisualizationElement
from .model import CoronavirusModel, CoronavirusAgentState, BoundaryPatch, CoronavirusAgent

from mesa.visualization.modules import CanvasGrid
from mesa.visualization.modules import ChartModule
from mesa.visualization.UserParam import UserSettableParameter


class BackgroundSetter(VisualizationElement):
    def __init__(self, url):
        self.js_code = 'document.getElementsByClassName("world-grid")[0].style.background = ' \
        '"url(' + "'{}'".format(url) +')";'


def agent_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "r": 0.5}


def agent_portrayal(agent):
    if type(agent) is CoronavirusAgent:
        portrayal = {"Shape": "circle",
                     "Filled": "true",
                     "r": 0.5}
        if agent.state == CoronavirusAgentState.INFECTED:
            portrayal["Color"] = "red"
            portrayal["Layer"] = 0
        elif agent.state == CoronavirusAgentState.RECOVERED:
            portrayal["Color"] = "grey"
            portrayal["Layer"] = 2
            portrayal['r'] = 0.15
        else:
            portrayal["Color"] = "green"
            portrayal["Layer"] = 1
            portrayal['r'] = 0.25
    elif type(agent) is BoundaryPatch:
        portrayal = {}
        portrayal["Color"] = "grey"
        portrayal["Shape"] = "rect"
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 0
        portrayal["w"] = 1
        portrayal["h"] = 1
    return portrayal


back = BackgroundSetter("https://www.tooploox.com/cdn/academic-program.png-24378a904f32a566ccf799a2dc4bdf8928d75bbe.png")
grid = CanvasGrid(agent_portrayal, 10, 10, 500, 500)

chart = ChartModule([
    {"Label": "Infected", "Color": "#FF0000"}, 
    {"Label": "Healthy", "Color": "#00FF00"},
    {"Label": "Recovered", "Color": "#666666"}],
    data_collector_name='datacollector'
)

model_params = {
    "N": UserSettableParameter('slider', "Number of agents", 10, 2, 200, 1,
                               description="Choose how many agents to include in the model"),
    "width": 10,
    "height": 10
}

server = ModularServer(CoronavirusModel, [grid, chart, back], "Coronavirus Model", model_params)
server.port = 8521
