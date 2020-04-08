from enum import Enum

from mesa import Agent


class CoronavirusAgentState(Enum):
    HEALTHY = 1
    INFECTED = 2
    RECOVERED = 3


class CoronavirusAgent(Agent):

    def __init__(self, unique_id, model, state, max_infection_steps=14, home_id=None):
        super().__init__(unique_id, model)
        self.state = state
        self.infected_steps = 0
        self.max_infection_steps = max_infection_steps
        self.home_id = home_id

    def get_portrayal(self):
        portrayal = {
                     # "Shape": "circle",
                     # "Filled": "true",
                     "Layer": 2,
                     # "r": 0.5,
                     "scale": 2.5}

        if self.state == CoronavirusAgentState.INFECTED:
            portrayal["Shape"] = "covid_agent_simulation/resources/sick.png"

        elif self.state == CoronavirusAgentState.RECOVERED:
            portrayal["Shape"] = "covid_agent_simulation/resources/recovered.png"
        else:
            portrayal["Shape"] = "covid_agent_simulation/resources/mario.png"
            portrayal['scale'] = 3.0
        return portrayal

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def infect(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        agent_cellmates = list(filter(lambda x: type(x) is self, cellmates))

        if len(agent_cellmates) > 1:
            other = self.random.choice(agent_cellmates)
            if other.state == CoronavirusAgentState.HEALTHY:
                other.state = CoronavirusAgentState.INFECTED

    def step(self):
        self.move()
        if self.state == CoronavirusAgentState.INFECTED:
            if self.infected_steps >= self.max_infection_steps:
                self.state = CoronavirusAgentState.RECOVERED
            else:
                self.infected_steps += 1
                self.infect()



class InteriorAgent(Agent):
    def __init__(self, unique_id, model, color="yellow", shape=None):
        super().__init__(unique_id, model)
        self.color = color
        if shape is not None:
            self.shape = shape
        else:
            self.shape = "rect"

    def step(self):
        pass

    def get_portrayal(self):
        portrayal = {"Shape": self.shape,
                     # "Filled": "true",
                     # "Color": self.color,
                     "Layer": 0,
                     # "w": 1,
                     # "h": 1
                     }
        return portrayal