from config import SCREEN_HEIGHT, SCREEN_WIDTH, START_FEN, SQUARE_SIZE
from renderer import render_board, render_gameover
from helpers.input import detect_promotion_click
from helpers.setup import setup_from_fen
from gamestate import GameState
from game.board import Board
import pygame
import sys

def main():
    pygame.init()
    pygame.font.init()
    window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    board = Board()
    gamestate = GameState(active_palette_index=2)
    setup_from_fen(START_FEN, board, gamestate, SQUARE_SIZE)

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
                    setup_from_fen(START_FEN, board, gamestate, SQUARE_SIZE)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if gamestate.awaiting_promotion:
                    row, col, color = gamestate.awaiting_promotion
                    chosen_type = detect_promotion_click(pygame.mouse.get_pos(), row, col, color)
                    if chosen_type:
                        board.promote_pawn(row, col, color, chosen_type)

                        gamestate.awaiting_promotion = None
                        gamestate.toggle_turn()
                        gamestate.clear_selection()
                        gamestate.check_gameover(board)
                        board.flag_for_redraw()
                        continue

                gamestate.handle_click(pygame.mouse.get_pos(), board)
                
        if board.needs_rendered:
            render_board(window, board, gamestate)
            board.needs_rendered = False

        if gamestate.is_gameover:
            render_gameover(window, board, gamestate)
        
        pygame.display.update()


if __name__ == "__main__":
    main()