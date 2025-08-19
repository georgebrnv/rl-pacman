# game.py - Core Pacman game logic
import random
from enum import Enum
from typing import List, Tuple, Optional
import copy

class Directions(Enum):
    NORTH = 'North'
    SOUTH = 'South'  
    EAST = 'East'
    WEST = 'West'
    STOP = 'Stop'

    @staticmethod
    def reverse(direction):
        if direction == Directions.NORTH:
            return Directions.SOUTH
        if direction == Directions.SOUTH:
            return Directions.NORTH
        if direction == Directions.EAST:
            return Directions.WEST
        if direction == Directions.WEST:
            return Directions.EAST
        return direction

class Actions:
    @staticmethod
    def direction_to_vector(direction, speed=1.0):
        if direction == Directions.NORTH:
            return (0, speed)
        if direction == Directions.SOUTH:
            return (0, -speed)
        if direction == Directions.EAST:
            return (speed, 0)
        if direction == Directions.WEST:
            return (-speed, 0)
        return (0, 0)
    
    @staticmethod
    def get_possible_actions(position, walls):
        possible = []
        x, y = int(position[0]), int(position[1])
        
        if y + 1 < walls.height and not walls[x][y+1]:
            possible.append(Directions.NORTH)
        if y - 1 >= 0 and not walls[x][y-1]:
            possible.append(Directions.SOUTH)
        if x + 1 < walls.width and not walls[x+1][y]:
            possible.append(Directions.EAST)
        if x - 1 >= 0 and not walls[x-1][y]:
            possible.append(Directions.WEST)
        
        possible.append(Directions.STOP)
        return possible

    @staticmethod
    def vector_to_direction(vector):
        dx, dy = vector
        if dy > 0:
            return Directions.NORTH
        if dy < 0:
            return Directions.SOUTH
        if dx > 0:
            return Directions.EAST
        if dx < 0:
            return Directions.WEST
        return Directions.STOP

class Grid:
    def __init__(self, width, height, initial_value=False):
        self.width = width
        self.height = height
        self.data = [[initial_value for _ in range(height)] for _ in range(width)]
    
    def __getitem__(self, x):
        return self.data[x]
    
    def __setitem__(self, x, value):
        self.data[x] = value
    
    def copy(self):
        g = Grid(self.width, self.height)
        g.data = [row[:] for row in self.data]
        return g
    
    def count(self, item=True):
        return sum([row.count(item) for row in self.data])
    
    def as_list(self):
        """Get list of (x,y) positions where grid is True"""
        positions = []
        for x in range(self.width):
            for y in range(self.height):
                if self.data[x][y]:
                    positions.append((x, y))
        return positions

class Configuration:
    def __init__(self, position, direction):
        self.position = position
        self.direction = direction
    
    def get_position(self):
        return self.position
    
    def get_direction(self):
        return self.direction
    
    def generate_successor(self, vector):
        x, y = self.position
        dx, dy = vector
        new_pos = (x + dx, y + dy)
        
        if vector == (0, 0):
            new_direction = Directions.STOP
        else:
            new_direction = Actions.vector_to_direction(vector)
        
        return Configuration(new_pos, new_direction)

class AgentState:
    def __init__(self, start_configuration, is_pacman=False):
        self.start = start_configuration
        self.configuration = start_configuration
        self.is_pacman = is_pacman
        self.scared_timer = 0
    
    def copy(self):
        state = AgentState(self.start, self.is_pacman)
        state.configuration = Configuration(
            self.configuration.position,
            self.configuration.direction
        )
        state.scared_timer = self.scared_timer
        return state
    
    def get_position(self):
        return self.configuration.get_position()
    
    def get_direction(self):
        return self.configuration.get_direction()

class GameState:
    # Constants
    SCARED_TIME = 40
    COLLISION_TOLERANCE = 0.7
    TIME_PENALTY = 1
    
    def __init__(self, layout=None):
        if layout:
            self.initialize(layout)
    
    def initialize(self, layout):
        self.layout = layout
        self.food = layout.food.copy()
        self.capsules = layout.capsules[:]
        self.walls = layout.walls
        self.score = 0
        self.score_change = 0
        
        # Initialize agents
        self.agent_states = []
        num_ghosts = 0
        
        for agent_idx, pos in sorted(layout.agent_positions):
            if agent_idx == 0:  # Pacman
                config = Configuration(pos, Directions.STOP)
                self.agent_states.append(AgentState(config, is_pacman=True))
            else:  # Ghost
                config = Configuration(pos, Directions.STOP)
                state = AgentState(config, is_pacman=False)
                self.agent_states.append(state)
                num_ghosts += 1
        
        self.num_ghosts = num_ghosts
        self._win = False
        self._lose = False
        self._food_eaten = None
        self._capsule_eaten = None
        self.num_moves = 0
    
    def deep_copy(self):
        state = GameState()
        state.layout = self.layout
        state.food = self.food.copy()
        state.capsules = self.capsules[:]
        state.walls = self.walls
        state.score = self.score
        state.score_change = self.score_change
        state.agent_states = [agent.copy() for agent in self.agent_states]
        state.num_ghosts = self.num_ghosts
        state._win = self._win
        state._lose = self._lose
        state._food_eaten = self._food_eaten
        state._capsule_eaten = self._capsule_eaten
        state.num_moves = self.num_moves
        return state
    
    def get_legal_actions(self, agent_index=0):
        if self.is_win() or self.is_lose():
            return []
        
        if agent_index == 0:  # Pacman
            return self.get_legal_pacman_actions()
        else:  # Ghost
            return self.get_legal_ghost_actions(agent_index)
    
    def get_legal_pacman_actions(self):
        return Actions.get_possible_actions(
            self.get_pacman_position(), 
            self.walls
        )
    
    def get_legal_ghost_actions(self, ghost_index):
        conf = self.agent_states[ghost_index].configuration
        possible_actions = Actions.get_possible_actions(
            conf.get_position(),
            self.walls
        )
        
        # Ghosts can't stop
        if Directions.STOP in possible_actions:
            possible_actions.remove(Directions.STOP)
        
        # Ghosts can't reverse unless at dead end
        reverse = Directions.reverse(conf.get_direction())
        if reverse in possible_actions and len(possible_actions) > 1:
            possible_actions.remove(reverse)
        
        return possible_actions
    
    def generate_successor(self, agent_index, action):
        if self.is_win() or self.is_lose():
            raise Exception("Can't generate successor of terminal state")
        
        state = self.deep_copy()
        
        if agent_index == 0:  # Pacman
            state._apply_pacman_action(action)
            state.score_change -= self.TIME_PENALTY  # Time penalty
        else:  # Ghost
            state._apply_ghost_action(action, agent_index)
            if state.agent_states[agent_index].scared_timer > 0:
                state.agent_states[agent_index].scared_timer -= 1
        
        state._check_death(agent_index)
        state.score += state.score_change
        state.score_change = 0
        state.num_moves += 1
        
        return state
    
    def _apply_pacman_action(self, action):
        legal = self.get_legal_pacman_actions()
        if action not in legal:
            raise Exception(f"Illegal pacman action: {action}")
        
        pacman_state = self.agent_states[0]
        vector = Actions.direction_to_vector(action, 1.0)
        pacman_state.configuration = pacman_state.configuration.generate_successor(vector)
        
        # Check for food/capsule consumption
        position = pacman_state.get_position()
        x, y = int(position[0]), int(position[1])
        
        # Eat food
        if self.food[x][y]:
            self.score_change += 10
            self.food[x][y] = False
            self._food_eaten = (x, y)
            
            if self.food.count() == 0:
                self.score_change += 500
                self._win = True
        
        # Eat capsule
        if position in self.capsules:
            self.capsules.remove(position)
            self._capsule_eaten = position
            self.score_change += 50  # Bonus for eating capsule
            for i in range(1, len(self.agent_states)):
                self.agent_states[i].scared_timer = self.SCARED_TIME
    
    def _apply_ghost_action(self, action, ghost_index):
        legal = self.get_legal_ghost_actions(ghost_index)
        if action not in legal:
            raise Exception(f"Illegal ghost action: {action}")
        
        ghost_state = self.agent_states[ghost_index]
        speed = 0.5 if ghost_state.scared_timer > 0 else 1.0
        vector = Actions.direction_to_vector(action, speed)
        ghost_state.configuration = ghost_state.configuration.generate_successor(vector)
    
    def _check_death(self, agent_index):
        pacman_position = self.get_pacman_position()
        
        if agent_index == 0:  # Pacman just moved
            for i in range(1, len(self.agent_states)):
                ghost_state = self.agent_states[i]
                if self._is_collision(pacman_position, ghost_state.get_position()):
                    self._handle_collision(ghost_state, i)
        else:  # Ghost just moved
            ghost_state = self.agent_states[agent_index]
            if self._is_collision(pacman_position, ghost_state.get_position()):
                self._handle_collision(ghost_state, agent_index)
    
    def _is_collision(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]) <= self.COLLISION_TOLERANCE
    
    def _handle_collision(self, ghost_state, ghost_index):
        if ghost_state.scared_timer > 0:
            self.score_change += 200
            ghost_state.configuration = Configuration(ghost_state.start.position, ghost_state.start.direction)
            ghost_state.scared_timer = 0
        else:
            if not self._win:
                self.score_change -= 500
                self._lose = True
    
    # Accessor methods
    def get_pacman_state(self):
        return self.agent_states[0].copy()
    
    def get_pacman_position(self):
        return self.agent_states[0].get_position()
    
    def get_ghost_states(self):
        return self.agent_states[1:]
    
    def get_ghost_state(self, agent_index):
        if agent_index == 0 or agent_index >= len(self.agent_states):
            raise Exception("Invalid ghost index")
        return self.agent_states[agent_index]
    
    def get_ghost_position(self, agent_index):
        if agent_index == 0:
            raise Exception("Pacman's index passed to get_ghost_position")
        return self.agent_states[agent_index].get_position()
    
    def get_ghost_positions(self):
        return [s.get_position() for s in self.get_ghost_states()]
    
    def get_num_agents(self):
        return len(self.agent_states)
    
    def get_num_ghosts(self):
        return self.num_ghosts
    
    def get_score(self):
        return self.score
    
    def get_capsules(self):
        return self.capsules[:]
    
    def get_num_food(self):
        return self.food.count()
    
    def get_food(self):
        return self.food
    
    def get_walls(self):
        return self.walls
    
    def has_food(self, x, y):
        return self.food[x][y]
    
    def has_wall(self, x, y):
        return self.walls[x][y]
    
    def is_lose(self):
        return self._lose
    
    def is_win(self):
        return self._win