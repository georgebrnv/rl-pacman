import pygame
import random
from enum import Enum
from .rooms import setupRoomOne

SPEED = 15
  
black = (0,0,0)
white = (255,255,255)
blue = (0,0,255)
green = (0,255,0)
red = (255,0,0)
purple = (255,0,255)
yellow   = ( 255, 255,0)

# Player and Hgosts size
w = 303-16 #Width
p_h = (7*60)+19 #Pacman height
m_h = (4*60)+19 #Monster height
b_h = (3*60)+19 #Binky height
i_w = 303-16-32 #Inky width
c_w = 303+(32-16) #Clyde width

Trollicon=pygame.image.load('images/Trollman.png')
pygame.display.set_icon(Trollicon)

pygame.init()
font = pygame.font.Font("freesansbold.ttf", 24)

class Wall(pygame.sprite.Sprite):
    def __init__(self,x,y,width,height, color):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.top = y
        self.rect.left = x

class Block(pygame.sprite.Sprite):
    def __init__(self, color, width, height):
        pygame.sprite.Sprite.__init__(self) 
        self.image = pygame.Surface([width, height])
        self.image.fill(white)
        self.image.set_colorkey(white)
        pygame.draw.ellipse(self.image,color,[0,0,width,height])
        self.rect = self.image.get_rect() 

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

class Player(pygame.sprite.Sprite):
    def __init__(self,x,y, filename):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(filename).convert()
        self.rect = self.image.get_rect()
        self.rect.top = y
        self.rect.left = x

    def move(self, dx, dy, walls, gate):
        # Get the old position, in case we need to go back to it
        old_x = self.rect.left
        old_y = self.rect.top
        
        # Try to move horizontally
        self.rect.left = old_x + dx
        
        # Check for wall collision
        if pygame.sprite.spritecollide(self, walls, False):
            # Hit a wall, go back
            self.rect.left = old_x
        else:
            # Try to move vertically
            self.rect.top = old_y + dy
            
            if pygame.sprite.spritecollide(self, walls, False):
                # Hit a wall, go back
                self.rect.top = old_y
        
        # Check gate collision
        if gate != False:
            if pygame.sprite.spritecollide(self, gate, False):
                # Hit gate, go back to original position
                self.rect.left = old_x
                self.rect.top = old_y

    def get_valid_directions(self, walls, gate):
        valid = []
        directions = [
            (Direction.RIGHT, 30, 0),
            (Direction.LEFT, -30, 0),
            (Direction.DOWN, 0, 30),
            (Direction.UP, 0, -30)
        ]

        for dir_enum, dx, dy in directions:
            # Test if we can move in this direction
            old_x = self.rect.left
            old_y = self.rect.top
            self.rect.left = old_x + dx
            self.rect.top = old_y + dy
            
            wall_hit = pygame.sprite.spritecollide(self, walls, False)
            
            # Restore position
            self.rect.left = old_x
            self.rect.top = old_y
            if not wall_hit:
                valid.append((dir_enum, dx, dy))

        return valid

    def get_valid_directions_mask(self, valid_directions):
        mask = [0, 0, 0, 0]
        for dir_enum, _, _ in valid_directions:
            if dir_enum == Direction.RIGHT:
                mask[0] = 1
            elif dir_enum == Direction.LEFT:
                mask[1] = 1
            elif dir_enum == Direction.UP:
                mask[2] = 1
            elif dir_enum == Direction.DOWN:
                mask[3] = 1
        return mask

#Inheritime Player klassist
class Ghost(Player):
    def __init__(self, x, y, filename):
        super().__init__(x, y, filename)
        self.direction = Direction.UP  # Start with a default direction
        self.previous_position = (x, y)
        self.follow_chance = 0.15  # 15% chance to follow Pacman
        self.start_y = y  # Remember starting Y position
        self.has_left_spawn = False  # Track if ghost has ever left spawn
        self.spawn_exit_target = 303  # Target x position for exiting spawn
    
   
    def is_in_spawn(self):
        """Check if ghost is still in spawn area"""
        # Ghost is in spawn if it hasn't left yet and is still in the spawn box
        # The spawn area is roughly where ghosts start (middle box area)
        if not self.has_left_spawn:
            # Check if we're still in the spawn box area
            # The gate is at y=242, ghosts spawn around y=259 (m_h) and y=199 (b_h)
            if self.rect.top < 240:  # Above the gate line
                self.has_left_spawn = True
                return False
            return True
        return False
    
    def move(self, dx, dy, walls, gate):
        # Get the old position, in case we need to go back to it
        old_x = self.rect.left
        old_y = self.rect.top
        self.rect.left = old_x + dx
        self.rect.top = old_y + dy
        # Check wall collision
        if pygame.sprite.spritecollide(self, walls, False):
            # Hit a wall, go back
            self.rect.left = old_x
            self.rect.top = old_y
    
    def get_reverse_direction(self, direction):
        """Get the opposite direction"""
        if direction == Direction.UP:
            return Direction.DOWN
        elif direction == Direction.DOWN:
            return Direction.UP
        elif direction == Direction.LEFT:
            return Direction.RIGHT
        elif direction == Direction.RIGHT:
            return Direction.LEFT
        return direction
    
    # Random movement with occasional Pacman following
    def choose_move(self, pacman_pos, walls, gate=None):
        import random
        
        # Get valid directions (returns list of tuples: (Direction, dx, dy))
        valid_dirs = self.get_valid_directions(walls, gate)
        
        if not valid_dirs:
            # No valid moves, return no movement
            return (0, 0)
        
        # Priority 1: If in spawn area, focus on getting out
        if self.is_in_spawn():
            # Step 1: Move to center column if not there (gate is at x=282-324)
            if abs(self.rect.left - self.spawn_exit_target) > 20:
                # Need to move horizontally to center
                if self.rect.left < self.spawn_exit_target - 20:
                    for dir_enum, dx, dy in valid_dirs:
                        if dir_enum == Direction.RIGHT:  # Move right
                            self.direction = dir_enum
                            return (dx, dy)
                elif self.rect.left > self.spawn_exit_target + 20:
                    for dir_enum, dx, dy in valid_dirs:
                        if dir_enum == Direction.LEFT:  # Move left
                            self.direction = dir_enum
                            return (dx, dy)
            
            # Step 2: Move up to exit spawn
            for dir_enum, dx, dy in valid_dirs:
                if dir_enum == Direction.UP:  # Move up
                    self.direction = dir_enum
                    return (dx, dy)
            
            # If can't move up, try moving horizontally first to find a path
            horizontal_dirs = [d for d in valid_dirs if d[0] in [Direction.LEFT, Direction.RIGHT]]
            if horizontal_dirs:
                dir_enum, dx, dy = random.choice(horizontal_dirs)
                self.direction = dir_enum
                return (dx, dy)
            
            # Last resort - try any valid direction
            if valid_dirs:
                dir_enum, dx, dy = random.choice(valid_dirs)
                self.direction = dir_enum
                return (dx, dy)
        
        # Normal behavior when outside spawn - ghosts can move anywhere on the map
        # Remove reverse direction unless it's the only option
        reverse_dir = self.get_reverse_direction(self.direction)
        filtered_dirs = [d for d in valid_dirs if d[0] != reverse_dir]
        
        # If only reverse is available (dead end), use it
        if not filtered_dirs:
            filtered_dirs = valid_dirs
        
        # Decide whether to follow Pacman or move randomly
        if random.random() < self.follow_chance and len(filtered_dirs) > 0:
            # Follow Pacman - choose valid direction that gets us closer
            best_dir = None
            best_score = float('inf')
            
            for dir_enum, dx, dy in filtered_dirs:
                # Calculate Manhattan distance to Pacman after this move
                new_x = self.rect.left + dx
                new_y = self.rect.top + dy
                dist = abs(new_x - pacman_pos[0]) + abs(new_y - pacman_pos[1])
                
                if dist < best_score:
                    best_score = dist
                    best_dir = (dir_enum, dx, dy)
            
            if best_dir:
                self.direction = best_dir[0]
                return (best_dir[1], best_dir[2])
        
        # Random movement with preference to continue straight
        # Check if current direction is still valid
        for dir_enum, dx, dy in filtered_dirs:
            if dir_enum == self.direction:
                # 70% chance to continue in same direction if valid
                if random.random() < 0.7:
                    return (dx, dy)
                break
        
        # Need to choose a new direction
        if filtered_dirs:
            dir_enum, dx, dy = random.choice(filtered_dirs)
            self.direction = dir_enum
            return (dx, dy)
        
        # Should never reach here, but failsafe
        return (0, 0)

class PacmanGameAI:
    def __init__(self):
        self.screen = pygame.display.set_mode([606, 606])
        pygame.display.set_caption('Pacman')
        background = pygame.Surface(self.screen.get_size())
        background = background.convert()
        background.fill(black)
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        self.all_sprites_list = pygame.sprite.RenderPlain()
        self.block_list = pygame.sprite.RenderPlain()
        self.monsta_list = pygame.sprite.RenderPlain()
        self.pacman_collide = pygame.sprite.RenderPlain()
        self.wall_list = setupRoomOne(self.all_sprites_list)
        self.gate = self.gate_create(self.all_sprites_list)

        self.pacman = Player( w, p_h, "images/Trollman.png" )
        self.blinky = Ghost( w, b_h, "images/Blinky.png" )
        self.pinky = Ghost( w, m_h, "images/Pinky.png" )
        self.inky = Ghost( i_w, m_h, "images/Inky.png" )
        self.clyde = Ghost( c_w, m_h, "images/Clyde.png" )


        # Create the player paddle object
        self.all_sprites_list.add(self.pacman)
        self.pacman_collide.add(self.pacman) 
        self.monsta_list.add(self.blinky)
        self.all_sprites_list.add(self.blinky)
        self.monsta_list.add(self.pinky)
        self.all_sprites_list.add(self.pinky) 
        self.monsta_list.add(self.inky)
        self.all_sprites_list.add(self.inky)
        self.monsta_list.add(self.clyde)
        self.all_sprites_list.add(self.clyde)

        # Draw the grid
        self.grid()

        self.best_score = 0
        self.score = 0
        self.frame_iteration = 0

    def play_step(self, action):
        self.frame_iteration += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # Make move
        self._move(action)

        # Move ghosts - pass None for gate since ghosts can pass through
        pacman_pos = [self.pacman.rect.left, self.pacman.rect.top]
        dx, dy = self.pinky.choose_move(pacman_pos, self.wall_list, None)
        self.pinky.move(dx, dy, self.wall_list, None)
  
        dx, dy = self.blinky.choose_move(pacman_pos, self.wall_list, None)
        self.blinky.move(dx, dy, self.wall_list, None)
  
        dx, dy = self.inky.choose_move(pacman_pos, self.wall_list, None)
        self.inky.move(dx, dy, self.wall_list, None)
  
        dx, dy = self.clyde.choose_move(pacman_pos, self.wall_list, None)
        self.clyde.move(dx, dy, self.wall_list, None)

        game_over = False
        reward = 0

        # Check if 'ate' food
        blocks_hit_list = pygame.sprite.spritecollide(self.pacman, self.block_list, True)
        # Check the list of collisions.
        if len(blocks_hit_list) > 0:
            self.score +=len(blocks_hit_list)
            reward += 10
        # Check if collided with ghosts
        monsta_hit_list = pygame.sprite.spritecollide(self.pacman, self.monsta_list, False)
        if monsta_hit_list:
            game_over = True
            reward -= 10
            return reward, game_over, self.score   

        # Update UI
        self.screen.fill(black)
        self.wall_list.draw(self.screen)
        self.gate.draw(self.screen)
        self.all_sprites_list.draw(self.screen)
        self.monsta_list.draw(self.screen)
        text=font.render("Score: "+str(self.score)+"/"+str(self.best_score), True, red)
        self.screen.blit(text, [10, 10])

        pygame.display.flip()
        self.clock.tick(SPEED)

        return reward, game_over, self.score


    def _move(self, action):
        # [right, left, up ,down]
        if action == [1, 0, 0, 0]:
            self.pacman.move(30, 0, self.wall_list, self.gate)
        elif action == [0, 1, 0, 0]:
            self.pacman.move(-30, 0, self.wall_list, self.gate)
        elif action == [0, 0, 1, 0]:
            self.pacman.move(0, 30, self.wall_list, self.gate)
        elif action == [0, 0, 0, 1]:
            self.pacman.move(0, -30, self.wall_list, self.gate)

    def grid(self):
        for row in range(19):
            for column in range(19):
                if (row == 7 or row == 8) and (column == 8 or column == 9 or column == 10):
                    continue
                else:
                    block = Block(yellow, 4, 4)

                    # Set a random location for the block
                    block.rect.x = (30*column+6)+26
                    block.rect.y = (30*row+6)+26

                    b_collide = pygame.sprite.spritecollide(block, self.wall_list, False)
                    p_collide = pygame.sprite.spritecollide(block, self.pacman_collide, False)
                    if b_collide:
                      continue
                    elif p_collide:
                      continue
                    else:
                        # Add the block to the list of objects
                        self.block_list.add(block)
                        self.all_sprites_list.add(block)

    def gate_create(self, all_sprites_list):
        gate = pygame.sprite.RenderPlain()
        gate.add(Wall(282,242,42,2,white))
        all_sprites_list.add(gate)
        return gate

