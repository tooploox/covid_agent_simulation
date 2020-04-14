from enum import Enum
import math
import random

import numpy as np
from mesa import Agent


class InteriorType(Enum):
    INSIDE = 1
    OUTSIDE = 2


class CoronavirusAgentState(Enum):
    HEALTHY = 1
    INFECTED = 2
    RECOVERED = 3


class CoronavirusAgent(Agent):

    def __init__(self, unique_id, model, state, max_infection_steps=28, going_out_prob=0.1,
                 max_being_out_steps=10, home_id=None, config=None, outside_agents_counter=None):
        super().__init__(unique_id, model)
        self.state = state
        self.infected_steps = 0
        self.outside_steps = 0
        self.max_infection_steps = max_infection_steps
        self.max_being_out_steps = max_being_out_steps
        self.home_id = home_id
        self.going_out_prob = going_out_prob
        self.config = config
        self.outside_agents_counter = outside_agents_counter

        self.target_cell = None

    def get_portrayal(self):

        portrayal = {
            "Layer": 1,
            "w": 0.5,
            "h": 0.5,
            "r": 0.7,
            "Filled": "true",
            "text": str(self.unique_id)[:-2],
            "text_color": 'black'
        }

        if self.state == CoronavirusAgentState.INFECTED:
            portrayal["Shape"] = self.config["agent"]["infected"]["shape"]
            portrayal["Color"] = self.config["agent"]["infected"]["color"]

        elif self.state == CoronavirusAgentState.RECOVERED:
            portrayal["Shape"] = self.config["agent"]["recovered"]["shape"]
            portrayal["Color"] = self.config["agent"]["recovered"]["color"]
        else:
            portrayal["Shape"] = self.config["agent"]["healthy"]["shape"]
            portrayal["Color"] = self.config["agent"]["healthy"]["color"]

        return portrayal

    def set_home_address(self, cell):
        self.home_cell = cell

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )

        if self.__is_home(self.pos):
            valid_id = self.home_id
        else:
            valid_id = None
        valid_steps = [p for p in possible_steps if not self.__is_cell_taken(p) and
                       self.model.get_cell_id(p) == valid_id
                       and self.__is_accessible(p)]

        cell_scores = []
        for step in valid_steps:
            cell_score = 0

            neighbors = self.model.grid.get_neighbors(step, moore=True,
                                                      include_center=False)
            moore_max_objects = 8
            agents = [x for x in neighbors if isinstance(x, CoronavirusAgent)]

            if self.target_cell is not None:
                distance_to_target = moore_distance(step, self.target_cell)
                score_bias = 0
                if distance_to_target > 0:
                    # prefer cells that minimize distance to target cell
                    cell_score += 1/distance_to_target + score_bias
                else:
                    cell_score += score_bias

            # prefer cells where there are fever agents around
            cell_score += 1-(len(agents)/moore_max_objects)
            cell_scores.append(cell_score)

        if len(valid_steps) > 0:
            # There are usually more than one cell with the same score.
            top_steps = np.argwhere(cell_scores == np.max(cell_scores)).flatten()
            self.model.grid.move_agent(self,
                                       valid_steps[self.random.choice(top_steps)])

    def go_out(self):
        self.target_cell = self.random.choice(self.model.available_target_cells)
        entrance_cell = random.choice(self.model.common_area_entrance)

        entrance_area = [(entrance_cell[0] + a, entrance_cell[1] + b)
                         for a, b in zip([0, 0], [0, 1])]
        teleport_to_cell = random.choice(entrance_area)
        self.model.grid.move_agent(self, teleport_to_cell)
        self.outside_agents_counter.add()

    def return_home(self):
        self.model.grid.move_agent(self, self.home_cell)
        self.outside_steps = 0
        self.outside_agents_counter.subtract()

    def infect(self):
        neighbors = self.model.grid.get_neighbors(self.pos, True, False,
                                                  len(self.model.infection_probabilities))
        for n in neighbors:
            if type(n) == CoronavirusAgent and \
                    n.state == CoronavirusAgentState.HEALTHY and \
                    self.random.uniform(0, 1) <\
                    self.model.infection_probabilities[moore_distance(self.pos, n.pos) - 1] and \
                    (self.home_id == n.home_id or not(self.__is_home(self.pos) or self.__is_home(n.pos))):
                print(self.random.uniform(0, 1))
                n.state = CoronavirusAgentState.INFECTED

    def step(self):
        if self.__location(self.pos) == InteriorType.INSIDE:
            # agent is at home and might go out
            movement_choice = random.choices(
                [0, 1],
                [1-self.going_out_prob, self.going_out_prob],
                k=1
            )
            if movement_choice == [1]\
                    and self.outside_agents_counter.count\
                    < self.model.num_agents_allowed_outside:
                self.go_out()
            else:
                self.move()
        else:
            # agent location is outside
            if self.outside_steps > self.max_being_out_steps:
                self.return_home()
            else:
                self.move()
                self.outside_steps += 1

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

    def __is_accessible(self, pos):
        agents_in_cell = self.model.grid.get_cell_list_contents(pos)
        for a in agents_in_cell:
            if type(a) == InteriorAgent:
                if not a.accessible:
                    return False
        return True

    def __is_home(self, pos):
        agents_in_cell = self.model.grid.get_cell_list_contents(pos)
        for a in agents_in_cell:
            if type(a) == InteriorAgent and a.home_id == self.home_id:
                return True
        return False

    def __location(self, pos):
        this_cell = self.model.grid.get_cell_list_contents([pos])
        interior_agent = [el for el in this_cell if type(el) == InteriorAgent]
        return interior_agent[0].interior_type


class InteriorAgent(Agent):
    def __init__(self, unique_id, model, color="yellow", shape=None, interior_type=None, home_id=None,
                 accessible=True):
        super().__init__(unique_id, model)
        self.color = color
        self.interior_type = interior_type
        self.home_id = home_id
        if shape is not None:
            self.shape = shape
        else:
            self.shape = "rect"
        self.accessible = accessible

    def step(self):
        pass

    def get_portrayal(self):
        portrayal = {"Shape": self.shape,
                     "Filled": "true",
                     "Color": self.color,
                     "Layer": 0,
                     "w": 1,
                     "h": 1}
        return portrayal


class WallAgent(Agent):

    def __init__(self, unique_id, model, color="black", type='horizontal'):
        super().__init__(unique_id, model)
        self.color = color
        self.type = type.lower()

    def step(self):
        pass

    def get_portrayal(self):
        portrayal = {"Shape": 'rect',
                     "Filled": "true",
                     "Color": self.color,
                     "Layer": 4,
                     "w": 1,
                     "h": 1}

        return portrayal


def moore_distance(p1, p2):
    return math.floor(math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2))