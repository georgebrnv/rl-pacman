from math import sqrt
import torch
import random
import numpy as np
from collections import deque, List
from pacman.pacman import Direction, PacmanGameAI

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0
        self.gamma = 0.9 # Discount rate
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = None
        self.trainer = None

    def get_state(self, game: PacmanGameAI):
        pacman_position = [game.pacman.rect.left, game.pacman.rect.top]
        blinky_position = [game.blinky.rect.left, game.blinky.rect.top]
        pinky_position = [game.pinky.rect.left, game.pinky.rect.top]
        inky_position = [game.inky.rect.left, game.inky.rect.top]
        clyde_position = [game.clyde.rect.left, game.clyde.rect.top]

        valid_directions = game.pacman.get_valid_directions(game.wall_list, game.gate)
        valid_directions_mask = game.pacman.get_valid_directions_mask(valid_directions)

        pacman_blinky_euc_dist = sqrt((pacman_position[0]-blinky_position[0])**2 + (pacman_position[1] - blinky_position[1])**2)
        pacman_pinky_euc_dist = sqrt((pacman_position[0]-pinky_position[0])**2 + (pacman_position[1] - pinky_position[1])**2)
        pacman_inky_euc_dist = sqrt((pacman_position[0]-inky_position[0])**2 + (pacman_position[1] - inky_position[1])**2)
        pacman_clyde_euc_dist = sqrt((pacman_position[0]-clyde_position[0])**2 + (pacman_position[1] - clyde_position[1])**2)
        
        safety_score_list = [0., 0., 0., 0.]
        for index, direction in enumerate(valid_directions_mask):

            if direction == 0:
                continue

            pacman_new_position = [pacman_position[0], pacman_position[1]]
            if index == 0:
                pacman_new_position[0] += 30
            elif index == 1:
                pacman_new_position[0] -= 30
            elif index == 2:
                pacman_new_position[1] -= 30
            else:
                pacman_new_position[1] += 30

            pacman_blinky_euc_dist_new = sqrt((pacman_new_position[0]-blinky_position[0])**2 + (pacman_new_position[1] - blinky_position[1])**2)
            pacman_pinky_euc_dist_new = sqrt((pacman_new_position[0]-pinky_position[0])**2 + (pacman_new_position[1] - pinky_position[1])**2)
            pacman_inky_euc_dist_new = sqrt((pacman_new_position[0]-inky_position[0])**2 + (pacman_new_position[1] - inky_position[1])**2)
            pacman_clyde_euc_dist_new = sqrt((pacman_new_position[0]-clyde_position[0])**2 + (pacman_new_position[1] - clyde_position[1])**2)

            safety_score_blinky = pacman_blinky_euc_dist_new - pacman_blinky_euc_dist
            safety_score_pinky = pacman_pinky_euc_dist_new - pacman_pinky_euc_dist
            safety_score_inky = pacman_inky_euc_dist_new - pacman_inky_euc_dist
            safety_score_clyde = pacman_clyde_euc_dist_new - pacman_clyde_euc_dist
            
            safety_score = (min(safety_score_blinky, safety_score_pinky, safety_score_inky, safety_score_clyde) + 30) /60

            safety_score_list[index] = safety_score

        food_grid = self.get_food_grid(pacman_position, game.block_list)
        flattened_food_grid = [cell for row in food_grid for cell in row]

        state = valid_directions_mask + safety_score_list + flattened_food_grid

        return state

    def get_food_grid(self, pacman_pos, block_list) -> List[[]]:
        grid = [[0 for _ in range(5)] for _ in range(5)]
        px, py = pacman_pos

        for block in block_list:
            bx, by = block.rect.x, block.rect.y
            grid_x = (bx - px) // 30 + 2
            grid_y =(by - py) // 30 + 2

            if 0 <= grid_x < 5 and 0 <= grid_y < 5:
                grid[grid_y][grid_x] = 1

        return grid


    def remember(self, state, action, reward, next_state, game_over):
        pass

    def train_long_memory(self):
        pass

    def train_short_memory(self, state, action, reward, next_state, game_over):
        pass

    def get_action(self, state):
        self.epsilon = 80 - self.n_games
        move = [0, 0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move_idx = random.randint(0, 3)
            move[move_idx] = 1
        print(f'No more random moves..')


def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = []
    best_score = 0
    agent = Agent()
    game = PacmanGameAI()
    while True:

        state_old = agent.get_state(game)
        move = agent.get_action(state_old)

        reward, game_over, score = game.play_step([1, 0, 0, 0])
        if game_over:
            game.reset()
            agent.n_games += 1

            if score > best_score:
                best_score = score

                print(f'Game: {agent.n_games} | Score: {score} | Best Score: {best_score}')




if __name__ == "__main__":
    train()
