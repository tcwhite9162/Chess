from config import SCREEN_HEIGHT, SCREEN_WIDTH
from renderer import render_board
from gamestate import GameState
from game.board import Board
import pygame
import sys

def main():
    pygame.init()
    window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    board = Board()
    gamestate = GameState(active_palette_index=2)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_l:
                    gamestate.next_palette()
                    board.flag_for_redraw()
                
                if event.key == pygame.K_j:
                    gamestate.previous_palette()
                    board.flag_for_redraw()
                
                if event.key == pygame.K_k:
                    gamestate.toggle_contrast_level()
                    board.flag_for_redraw()
                    
                if event.key == pygame.K_r:
                    board.reset_board()

            if event.type == pygame.MOUSEBUTTONDOWN:
                gamestate.handle_click(pygame.mouse.get_pos(), board)
                
        if board.needs_rendered:
            render_board(window, board, gamestate)
            pygame.display.update()
            board.needs_rendered = False

if __name__ == "__main__":
    main()