from enum import Enum
import math
import random

from mesa import Agent


class InteriorType(Enum):
    INSIDE = 1
    OUTSIDE = 2

class CoronavirusAgentState(Enum):
    HEALTHY = 1
    INFECTED = 2
    RECOVERED = 3


class CoronavirusAgent(Agent):

    def __init__(self, unique_id, model, state, max_infection_steps=28, going_out_prob=0.1, home_id=None):
        super().__init__(unique_id, model)
        self.state = state
        self.infected_steps = 0
        self.max_infection_steps = max_infection_steps
        self.home_id = home_id
        self.going_out_prob = going_out_prob

    def get_portrayal(self):
        portrayal = {"Layer": 1,
                     "Shape": "circle",
                     "Filled": "true",
                     "r": 0.5}

        if self.state == CoronavirusAgentState.INFECTED:
            portrayal["Color"] = "red"
        elif self.state == CoronavirusAgentState.RECOVERED:
            portrayal["Color"] = "grey"
        else:
            portrayal["Color"] = "green"
        return portrayal

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )

        valid_steps = [p for p in possible_steps if not self.__is_cell_taken(p)]
        if len(valid_steps) > 0:
            self.model.grid.move_agent(self, self.random.choice(valid_steps))

    def go_out(self, entrance_cell=(10,20)):
        entrance_area = [(entrance_cell[0]+a, entrance_cell[1]+ b) for a, b in zip([0, 1, 2, 3], [0, 1, 2, 3])]
        teleport_to_cell = random.choice(entrance_area)
        self.model.grid.move_agent(self, teleport_to_cell)

    def infect(self):
        neighbors = self.model.grid.get_neighbors(self.pos, True, False,
                                                  len(self.model.infection_probabilities))
        for n in neighbors:
            if type(n) == CoronavirusAgent and \
                    n.state == CoronavirusAgentState.HEALTHY and \
                    self.random.uniform(0, 1) < self.model.infection_probabilities[moore_distance(self.pos, n.pos) - 1]:
                n.state = CoronavirusAgentState.INFECTED

    def step(self):
        if self.__location(self.pos) == InteriorType.INSIDE:
            movement_choice = random.choices(
                [0, 1],
                [1-self.going_out_prob, self.going_out_prob],
                k=1
            )
            if movement_choice == [1]:
                self.go_out()
            else:
                self.move()
        else:
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

    def __location(self, pos):
        this_cell = self.model.grid.get_cell_list_contents([pos])
        interior_agent = [el for el in this_cell if type(el) == InteriorAgent]
        return interior_agent[0].interior_type


class InteriorAgent(Agent):
    def __init__(self, unique_id, model, color="yellow", shape=None, interior_type=None):
        super().__init__(unique_id, model)
        self.color = color
        self.interior_type = interior_type
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
                     "h": 1,
                     "Color": self.color,
                     "Filled": "true"}
        return portrayal


def moore_distance(p1, p2):
    return math.floor(math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2))
