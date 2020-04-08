from enum import Enum
import math

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
                     "Layer": 2,
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

        valid_steps = [p for p in possible_steps if not self.__is_cell_taken(p)]
        if len(valid_steps) > 0:
            self.model.grid.move_agent(self, self.random.choice(valid_steps))

    def infect(self):
        neighbors = self.model.grid.get_neighbors(self.pos, True, False,
                                                  len(self.model.infection_probabilities))
        for n in neighbors:
            if type(n) == CoronavirusAgent and \
                    n.state == CoronavirusAgentState.HEALTHY and \
                    self.random.uniform(0, 1) < self.model.infection_probabilities[moore_distance(self.pos, n.pos) - 1]:
                n.state = CoronavirusAgentState.INFECTED

    def step(self):
        self.move()
        if self.state == CoronavirusAgentState.INFECTED:
            if self.infected_steps >= self.max_infection_steps:
                self.state = CoronavirusAgentState.RECOVERED
            else:
                self.infected_steps += 1
                self.infect()

    def __is_cell_taken(self, pos):
        agents_in_cell = self.model.grid.get_cell_list_contents(pos)
        for a in agents_in_cell:
            if type(a) == CoronavirusAgent:
                return True
        return False



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
                     "Layer": 0,
                     "w": 1,
                     "h": 1}
        return portrayal


def moore_distance(p1, p2):
    return math.floor(math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2))
