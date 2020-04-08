
from mesa.visualization.ModularVisualization import ModularServer
from .model import CoronavirusModel, CoronavirusAgentState
from .agents import CoronavirusAgent, InteriorAgent

from mesa.visualization.modules import CanvasGrid
from mesa.visualization.modules import ChartModule
from mesa.visualization.UserParam import UserSettableParameter


class BackgroundSetter(VisualizationElement):
    def __init__(self, url):
        self.js_code = 'document.getElementsByClassName("world-grid")[0].style.background = ' \
        '"url(' + "'{}'".format(url) +')";'


def agent_portrayal(agent):

    return agent.get_portrayal()


num_cells_row = 50
num_cells_column = 50
grid = CanvasGrid(agent_portrayal, num_cells_row, num_cells_column, 700, 700)


back = BackgroundSetter("https://www.tooploox.com/cdn/academic-program.png-24378a904f32a566ccf799a2dc4bdf8928d75bbe.png")
grid = CanvasGrid(agent_portrayal, 10, 10, 500, 500)

chart = ChartModule([
    {"Label": "Infected", "Color": "#FF0000"}, 
    {"Label": "Healthy", "Color": "#00FF00"},
    {"Label": "Recovered", "Color": "#666666"}],
    data_collector_name='datacollector'
)

model_params = {
    "num_agents":
        UserSettableParameter('slider', "Number of agents", 10, 2, 200, 1,
                              description="Choose how many agents to include in the model"),
    "width": num_cells_column,
    "height": num_cells_row
}

server = ModularServer(CoronavirusModel, [grid, chart, back], "Coronavirus Model", model_params)
server.port = 8521
