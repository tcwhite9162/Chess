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
    gamestate = GameState(palette_index=2)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_l:
                    gamestate.increase_palette_index()
                    board.mark_dirty()
                
                if event.key == pygame.K_j:
                    gamestate.decrease_palette_index()
                    board.mark_dirty()
                
                if event.key == pygame.K_k:
                    gamestate.toggle_contrast()
                    board.mark_dirty()

            if event.type == pygame.MOUSEBUTTONDOWN:
                gamestate.handle_click(pygame.mouse.get_pos(), board)
                
        if board.needs_rendered:
            render_board(window, board, gamestate)
            pygame.display.update()
            board.needs_rendered = False

if __name__ == "__main__":
    main()