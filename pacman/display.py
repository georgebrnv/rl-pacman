# display.py - Pygame visualization for Pacman
import pygame
import math
from .game import Directions

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)
CYAN = (0, 255, 255)
PURPLE = (128, 0, 128)
WALL_COLOR = (0, 51, 255)
FOOD_COLOR = (255, 255, 255)
CAPSULE_COLOR = (255, 255, 255)
SCARED_COLOR = (0, 255, 255)

class PacmanDisplay:
    def __init__(self, width=800, height=600, grid_size=20, fps=10):
        pygame.init()
        self.grid_size = grid_size
        self.fps = fps
        self.width = width
        self.height = height
        
        # Colors for ghosts
        self.ghost_colors = [RED, PINK, CYAN, ORANGE]
        
        # Initialize display
        self.screen = None
        self.clock = pygame.time.Clock()
        self.is_initialized = False
        
    def initialize(self, state):
        """Initialize the display with the game state"""
        # Calculate window size based on maze
        maze_width = state.walls.width
        maze_height = state.walls.height
        
        self.width = maze_width * self.grid_size
        self.height = maze_height * self.grid_size
        
        # Create window
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Pacman RL")
        
        self.is_initialized = True
        
    def render(self, state):
        """Render the current game state"""
        if not self.is_initialized:
            self.initialize(state)
        
        # Clear screen
        self.screen.fill(BLACK)
        
        # Draw maze
        self._draw_walls(state)
        self._draw_food(state)
        self._draw_capsules(state)
        
        # Draw agents
        self._draw_pacman(state)
        self._draw_ghosts(state)
        
        # Draw score
        self._draw_score(state)
        
        # Update display
        pygame.display.flip()
        self.clock.tick(self.fps)
        
    def _draw_walls(self, state):
        """Draw the maze walls"""
        walls = state.get_walls()
        for x in range(walls.width):
            for y in range(walls.height):
                if walls[x][y]:
                    screen_x = x * self.grid_size
                    screen_y = (walls.height - 1 - y) * self.grid_size
                    pygame.draw.rect(self.screen, WALL_COLOR,
                                   (screen_x, screen_y, self.grid_size, self.grid_size))
    
    def _draw_food(self, state):
        """Draw food pellets"""
        food = state.get_food()
        for x in range(food.width):
            for y in range(food.height):
                if food[x][y]:
                    screen_x = x * self.grid_size + self.grid_size // 2
                    screen_y = (food.height - 1 - y) * self.grid_size + self.grid_size // 2
                    pygame.draw.circle(self.screen, FOOD_COLOR,
                                     (screen_x, screen_y), self.grid_size // 6)
    
    def _draw_capsules(self, state):
        """Draw power capsules"""
        capsules = state.get_capsules()
        for (x, y) in capsules:
            screen_x = x * self.grid_size + self.grid_size // 2
            screen_y = (state.walls.height - 1 - y) * self.grid_size + self.grid_size // 2
            pygame.draw.circle(self.screen, CAPSULE_COLOR,
                             (screen_x, screen_y), self.grid_size // 3)
    
    def _draw_pacman(self, state):
        """Draw Pacman"""
        pos = state.get_pacman_position()
        x, y = pos
        
        screen_x = int(x * self.grid_size + self.grid_size // 2)
        screen_y = int((state.walls.height - 1 - y) * self.grid_size + self.grid_size // 2)
        
        # Get direction for mouth animation
        direction = state.get_pacman_state().get_direction()
        
        # Draw Pacman as a circle with mouth
        radius = int(self.grid_size * 0.4)
        
        # Calculate mouth angle based on direction
        if direction == Directions.EAST:
            start_angle = 30
        elif direction == Directions.WEST:
            start_angle = 210
        elif direction == Directions.NORTH:
            start_angle = 300
        elif direction == Directions.SOUTH:
            start_angle = 120
        else:
            start_angle = 30
        
        # Draw Pacman body
        pygame.draw.circle(self.screen, YELLOW, (screen_x, screen_y), radius)
        
        # Draw mouth (triangle)
        if direction != Directions.STOP:
            mouth_angle = math.radians(start_angle)
            mouth_size = math.radians(30)
            
            points = [(screen_x, screen_y)]
            points.append((screen_x + radius * math.cos(mouth_angle - mouth_size),
                          screen_y - radius * math.sin(mouth_angle - mouth_size)))
            points.append((screen_x + radius * math.cos(mouth_angle + mouth_size),
                          screen_y - radius * math.sin(mouth_angle + mouth_size)))
            
            pygame.draw.polygon(self.screen, BLACK, points)
    
    def _draw_ghosts(self, state):
        """Draw all ghosts"""
        ghost_states = state.get_ghost_states()
        
        for i, ghost_state in enumerate(ghost_states):
            pos = ghost_state.get_position()
            x, y = pos
            
            screen_x = int(x * self.grid_size + self.grid_size // 2)
            screen_y = int((state.walls.height - 1 - y) * self.grid_size + self.grid_size // 2)
            
            # Choose color based on scared state
            if ghost_state.scared_timer > 0:
                color = SCARED_COLOR
                # Add flashing effect when scared time is running out
                if ghost_state.scared_timer < 10 and ghost_state.scared_timer % 2 == 0:
                    color = WHITE
            else:
                color = self.ghost_colors[i % len(self.ghost_colors)]
            
            # Draw ghost body (circle)
            radius = int(self.grid_size * 0.4)
            pygame.draw.circle(self.screen, color, (screen_x, screen_y), radius)
            
            # Draw ghost bottom (wavy)
            bottom_y = screen_y + radius // 2
            for j in range(3):
                wave_x = screen_x - radius + (j * radius * 2 // 3)
                pygame.draw.circle(self.screen, color,
                                 (wave_x + radius // 3, bottom_y), radius // 3)
            
            # Draw eyes
            if ghost_state.scared_timer == 0:
                eye_radius = radius // 5
                eye_y = screen_y - radius // 3
                
                # Left eye
                pygame.draw.circle(self.screen, WHITE,
                                 (screen_x - radius // 3, eye_y), eye_radius)
                pygame.draw.circle(self.screen, BLACK,
                                 (screen_x - radius // 3, eye_y), eye_radius // 2)
                
                # Right eye
                pygame.draw.circle(self.screen, WHITE,
                                 (screen_x + radius // 3, eye_y), eye_radius)
                pygame.draw.circle(self.screen, BLACK,
                                 (screen_x + radius // 3, eye_y), eye_radius // 2)
    
    def _draw_score(self, state):
        """Draw the score on screen"""
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {state.get_score()}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Draw win/lose message
        if state.is_win():
            win_text = font.render("YOU WIN!", True, GREEN)
            text_rect = win_text.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(win_text, text_rect)
        elif state.is_lose():
            lose_text = font.render("GAME OVER", True, RED)
            text_rect = lose_text.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(lose_text, text_rect)
    
    def close(self):
        """Close the display"""
        if self.is_initialized:
            pygame.quit()
            self.is_initialized = False
    
    def check_quit_event(self):
        """Check for quit events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True
        return False
    
    def get_user_action(self):
        """Get action from keyboard input"""
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            return Directions.NORTH
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            return Directions.SOUTH
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            return Directions.WEST
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            return Directions.EAST
        elif keys[pygame.K_SPACE]:
            return Directions.STOP
        
        return None