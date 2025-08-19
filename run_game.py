#!/usr/bin/env python3
"""
Run a Pacman game with keyboard controls or watch random play.

Usage:
    python run_game.py                  # Play with keyboard
    python run_game.py --auto           # Watch random play
    python run_game.py --layout medium  # Use different layout
"""

import sys
import random
import pygame
from pacman import GameState, Directions, get_layout, PacmanDisplay

def play_manual_game(layout_name='small'):
    """Play Pacman with keyboard controls"""
    
    # Initialize game
    layout = get_layout(layout_name)
    state = GameState(layout)
    display = PacmanDisplay(fps=10)
    
    print("Pacman Game Controls:")
    print("  Arrow Keys or WASD - Move Pacman")
    print("  Space - Stop")
    print("  ESC - Quit")
    print("")
    print(f"Playing on layout: {layout_name}")
    
    # Game loop
    while not state.is_win() and not state.is_lose():
        # Render
        display.render(state)
        
        # Check for quit
        if display.check_quit_event():
            break
        
        # Get player action
        action = display.get_user_action()
        
        if action is not None:
            # Check if action is legal
            legal_actions = state.get_legal_actions(0)
            if action in legal_actions:
                # Move Pacman
                state = state.generate_successor(0, action)
                
                # Move ghosts
                for ghost_idx in range(1, state.get_num_agents()):
                    if not state.is_win() and not state.is_lose():
                        ghost_actions = state.get_legal_ghost_actions(ghost_idx)
                        if ghost_actions:
                            # Simple ghost AI - random with bias toward Pacman
                            pacman_pos = state.get_pacman_position()
                            ghost_pos = state.get_ghost_position(ghost_idx)
                            
                            # If scared, move away from Pacman
                            if state.get_ghost_state(ghost_idx).scared_timer > 0:
                                # Choose action that maximizes distance from Pacman
                                best_action = random.choice(ghost_actions)
                            else:
                                # 70% chance to move toward Pacman, 30% random
                                if random.random() < 0.7:
                                    # Simple greedy - choose action that minimizes distance
                                    best_dist = float('inf')
                                    best_action = ghost_actions[0]
                                    
                                    for action in ghost_actions:
                                        # Simulate the action
                                        dx, dy = 0, 0
                                        if action == Directions.NORTH:
                                            dy = 1
                                        elif action == Directions.SOUTH:
                                            dy = -1
                                        elif action == Directions.EAST:
                                            dx = 1
                                        elif action == Directions.WEST:
                                            dx = -1
                                        
                                        new_pos = (ghost_pos[0] + dx, ghost_pos[1] + dy)
                                        dist = abs(new_pos[0] - pacman_pos[0]) + abs(new_pos[1] - pacman_pos[1])
                                        
                                        if dist < best_dist:
                                            best_dist = dist
                                            best_action = action
                                else:
                                    best_action = random.choice(ghost_actions)
                            
                            state = state.generate_successor(ghost_idx, best_action)
    
    # Show final state
    display.render(state)
    pygame.time.wait(2000)
    
    print(f"\nGame Over!")
    print(f"Final Score: {state.get_score()}")
    print(f"Result: {'WIN' if state.is_win() else 'LOSE'}")
    
    display.close()

def play_auto_game(layout_name='small'):
    """Watch random play"""
    
    # Initialize game
    layout = get_layout(layout_name)
    state = GameState(layout)
    display = PacmanDisplay(fps=15)
    
    print("Watching Random Pacman")
    print(f"Layout: {layout_name}")
    print("Press ESC to quit")
    
    # Game loop
    step = 0
    while not state.is_win() and not state.is_lose() and step < 1000:
        # Render
        display.render(state)
        
        # Check for quit
        if display.check_quit_event():
            break
        
        # Random Pacman action
        legal_actions = state.get_legal_actions(0)
        if legal_actions:
            # Prefer moving over stopping
            if Directions.STOP in legal_actions and len(legal_actions) > 1:
                legal_actions.remove(Directions.STOP)
            action = random.choice(legal_actions)
            state = state.generate_successor(0, action)
        
        # Move ghosts
        for ghost_idx in range(1, state.get_num_agents()):
            if not state.is_win() and not state.is_lose():
                ghost_actions = state.get_legal_ghost_actions(ghost_idx)
                if ghost_actions:
                    action = random.choice(ghost_actions)
                    state = state.generate_successor(ghost_idx, action)
        
        step += 1
    
    # Show final state
    display.render(state)
    pygame.time.wait(2000)
    
    print(f"\nGame Over after {step} steps!")
    print(f"Final Score: {state.get_score()}")
    print(f"Result: {'WIN' if state.is_win() else 'LOSE' if state.is_lose() else 'TIMEOUT'}")
    
    display.close()

def main():
    # Parse arguments
    auto_play = '--auto' in sys.argv
    
    # Get layout
    layout_name = 'classic'
    for i, arg in enumerate(sys.argv):
        if arg == '--layout' and i + 1 < len(sys.argv):
            layout_name = sys.argv[i + 1]
    
    # Check if layout exists
    from pacman.layouts import LAYOUTS
    if layout_name not in LAYOUTS:
        print(f"Error: Unknown layout '{layout_name}'")
        print(f"Available layouts: {', '.join(LAYOUTS.keys())}")
        sys.exit(1)
    
    # Run game
    if auto_play:
        play_auto_game(layout_name)
    else:
        play_manual_game(layout_name)

if __name__ == "__main__":
    main()
