import config as cfg
import cairosvg
import pygame
import io
_images_cache = {}

class Piece:
    def __init__(self, color, type_str, square_size):
        self.color = color
        self.type  = type_str
        self.code  = f"{color}{type_str}"
        if self.code not in _images_cache:
            svg_path = f"assets/{cfg.PIECE_SET}{self.code}.svg"
            png_bytes = cairosvg.svg2png(url=svg_path, output_width=square_size, output_height=square_size)
            image_stream = io.BytesIO(png_bytes)
            image = pygame.image.load(image_stream).convert_alpha()
            _images_cache[self.code] = image
        self.image = _images_cache[self.code]
        self.size  = square_size

    def copy(self):
        return Piece(self.color, self.type, self.size)

    def __repr__(self):
        colors = {'w': "White", 'b': "Black"}
        pieces = {'p': "Pawn", 'n': "Knight", 'b': "Bishop", 'r': "Rook", 'q': 'Queen', 'k': 'King'}
        c = colors[self.code[0]]
        p = pieces[self.code[1]]
        return c + ' ' + p