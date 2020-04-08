from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import math
import numpy as np

from .agents import CoronavirusAgent, InteriorAgent, CoronavirusAgentState



class BoundaryPatch(Agent):
    def __init__(self, unique_id, pos, model):
        '''
        Creates a new patch of boundary

        '''
        super().__init__(unique_id, model)

    def step(self):
        return


class CoronavirusModel(Model):
    def __init__(self, num_agents=10, width=10, height=10, infection_probabilities=[0.7, 0.4]):
        self.num_agents = num_agents
        self.grid = MultiGrid(height, width, False)
        self.schedule = RandomActivation(self)
        self.datacollector = DataCollector(
            model_reporters={"Infected": all_infected,
                             "Healthy": all_healthy,
                             "Recovered": all_recovered}
        )
        self.global_max_index = 0
        self.infection_probabilities = infection_probabilities
        self.setup_interiors()
        self.setup_agents()

        self.running = True
        self.datacollector.collect(self)

    def get_unique_id(self):
        unique_id = self.global_max_index
        self.global_max_index += 1

        return unique_id

    def setup_agents(self):
        choices = [CoronavirusAgentState.HEALTHY, CoronavirusAgentState.INFECTED]
        
        home_coors = []
        for info in self.grid.coord_iter():
            contents = info[0]
            coors = info[1:]
            for object in contents:
                if object.color == "yellow":
                    home_coors.append(coors)

        for i in range(self.num_agents):
            a = CoronavirusAgent(self.get_unique_id(), self, self.random.choice(choices))
            self.schedule.add(a)

            ind = np.random.randint(0, len(home_coors), 1)[0]
            x, y = home_coors[ind]
            self.grid.place_agent(a, (x, y))

    def setup_interior(self, init_row, init_column, width=3, height=4, color="yellow", shape=None):
        for x in range(init_column, init_column + width):
            for y in range(init_row, init_row + height):
                interior = InteriorAgent(self.get_unique_id(), self, color, shape)
                self.grid.place_agent(interior, (x, y))

    def setup_interiors(self):
        homes_coor = [
            (0, 0),
            (0, 10),
            (0, 30),
            (5, 10),
            (10, 20)
        ]

        object_coor = (20, 10)
        for coor in homes_coor:
            self.setup_interior(coor[0], coor[1], shape="covid_agent_simulation/resources/wall.png")

        self.setup_interior(object_coor[0], object_coor[1],
                            width=20, height=10, shape="covid_agent_simulation/resources/grass.png")

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)

    def run_model(self, n):
        for i in range(n):
            self.step()


def all_infected(model):
    return get_all_in_state(model, CoronavirusAgentState.INFECTED)


def all_healthy(model):
    return get_all_in_state(model, CoronavirusAgentState.HEALTHY)


def all_recovered(model):
    return get_all_in_state(model, CoronavirusAgentState.RECOVERED)


def get_all_in_state(model, state):
    return len([1 for agent in model.schedule.agents
                if type(agent) == CoronavirusAgent and agent.state == state])
