# layouts.py - Maze layouts for Pacman
from .game import Grid, Configuration, Directions

class Layout:
    def __init__(self, layout_text):
        self.width = len(layout_text[0])
        self.height = len(layout_text)
        self.walls = Grid(self.width, self.height, False)
        self.food = Grid(self.width, self.height, False)
        self.capsules = []
        self.agent_positions = []
        self.num_ghosts = 0
        
        self._process_layout(layout_text)
    
    def _process_layout(self, layout_text):
        max_y = self.height - 1
        for y in range(self.height):
            for x in range(self.width):
                layout_char = layout_text[max_y - y][x]
                self._process_layout_char(x, y, layout_char)
    
    def _process_layout_char(self, x, y, layout_char):
        if layout_char == '%':
            self.walls[x][y] = True
        elif layout_char == '.':
            self.food[x][y] = True
        elif layout_char == 'o':
            self.capsules.append((x, y))
        elif layout_char == 'P':
            self.agent_positions.append((0, (x, y)))
        elif layout_char in ['G', '1', '2', '3', '4']:
            self.num_ghosts += 1
            self.agent_positions.append((self.num_ghosts, (x, y)))
        elif layout_char == ' ':
            pass
        else:
            pass  # Ignore other characters

    def get_num_ghosts(self):
        return self.num_ghosts

# Predefined layouts
LAYOUTS = {
    'tiny': [
        "%%%%%%",
        "%P.G.%",
        "%%%%%%"
    ],
    
    'small': [
        "%%%%%%%%%%%%",
        "%......%G..%",
        "%.%%...%...%",
        "%.%o.%.%...%",
        "%.%.%%.%...%",
        "%.....P%...%",
        "%%%%%%%%%%%%"
    ],
    
    'medium': [
        "%%%%%%%%%%%%%%%%%%%%",
        "%......%G  %......%",
        "%.%%...%%  %%...%%.%",
        "%.%o.%........%.o%.%",
        "%.%%.%.%%%%%%.%.%%.%",
        "%........P.........%",
        "%%%%%%%%%%%%%%%%%%%%"
    ],
    
    'classic': [
        "%%%%%%%%%%%%%%%%%%%%%%%%%%%%",
        "%............%%............%",
        "%.%%%%.%%%%%.%%.%%%%%.%%%%.%",
        "%o%%%%.%%%%%.%%.%%%%%.%%%%o%",
        "%.%%%%.%%%%%.%%.%%%%%.%%%%.%",
        "%..........................%",
        "%.%%%%.%%.%%%%%%%%.%%.%%%%.%",
        "%.%%%%.%%.%%%%%%%%.%%.%%%%.%",
        "%......%%....%%....%%......%",
        "%%%%%%.%%%%% %% %%%%%.%%%%%%",
        "%%%%%%.%%%%% %% %%%%%.%%%%%%",
        "%%%%%%.%%          %%.%%%%%%",
        "%%%%%%.%% %%%  %%% %%.%%%%%%",
        "%........  %G  G%  ........%",
        "%%%%%%.%% %%%%%%%% %%.%%%%%%",
        "%%%%%%.%%          %%.%%%%%%",
        "%%%%%%.%% %%%%%%%% %%.%%%%%%",
        "%............%%............%",
        "%.%%%%.%%%%%.%%.%%%%%.%%%%.%",
        "%o.%%%.......P........%%%.o%",
        "%%.%%%.%%.%%%%%%%%.%%.%%%.%%",
        "%......%%....%%....%%......%",
        "%.%%%%%%%%%%.%%.%%%%%%%%%%.%",
        "%..........................%",
        "%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
    ],
    
    'test': [
        "%%%%%%%",
        "% . . %",
        "% %%% %", 
        "% %P% %",
        "% %%% %",
        "%.%G%.%",
        "%%%%%%%"
    ],
    
    'original': [
        "%%%%%%%%%%%%%%%%%%%%%%%%%%%%",
        "%............%%............%",
        "%.%%%%.%%%%%.%%.%%%%%.%%%%.%",
        "%o%%%%.%%%%%.%%.%%%%%.%%%%o%",
        "%.%%%%.%%%%%.%%.%%%%%.%%%%.%",
        "%..........................%",
        "%.%%%%.%%.%%%%%%%%.%%.%%%%.%",
        "%.%%%%.%%.%%%%%%%%.%%.%%%%.%",
        "%......%%....%%....%%......%",
        "%%%%%%.%%%%% %% %%%%%.%%%%%%",
        "%%%%%%.%%%%% %% %%%%%.%%%%%%",
        "%%%%%%.%%          %%.%%%%%%",
        "%%%%%%.%% %%%-%%% %%.%%%%%%",
        "%%%%%%.%% %G    G% %%.%%%%%%",
        "   %...   %G    G%   ...%   ",
        "%%%%%%.%% %G    G% %%.%%%%%%",
        "%%%%%%.%% %%%%%%%% %%.%%%%%%",
        "%%%%%%.%%          %%.%%%%%%",
        "%%%%%%.%% %%%%%%%% %%.%%%%%%",
        "%............%%............%",
        "%.%%%%.%%%%%.%%.%%%%%.%%%%.%",
        "%o.%%%....... P.......%%%.o%",
        "%%.%%%.%%.%%%%%%%%.%%.%%%.%%",
        "%......%%....%%....%%......%",
        "%.%%%%%%%%%%.%%.%%%%%%%%%%.%",
        "%..........................%",
        "%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
    ]
}

def get_layout(name='small'):
    """Get a predefined layout by name"""
    if name not in LAYOUTS:
        raise ValueError(f"Unknown layout: {name}. Available: {list(LAYOUTS.keys())}")
    return Layout(LAYOUTS[name])