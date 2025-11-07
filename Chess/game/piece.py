import pygame

_images_cache = {}

class Piece:
    def __init__(self, color, type_str, square_size):
        self.color = color
        self.type = type_str
        self.code = f"{color}{type_str}"
        if self.code not in _images_cache:
            image = pygame.transform.scale(pygame.image.load(f"assets/{self.code}.png"), (square_size, square_size))
            _images_cache[self.code] = image
        self.image = _images_cache[self.code]

    def __repr__(self):
        colors = {'w': "White", 'b': "Black"}
        pieces = {'p': "Pawn", 'n': "Knight", 'b': "Bishop", 'r': "Rook", 'q': 'Queen', 'k': 'King'}
        c = colors[self.code[0]]
        p = pieces[self.code[1]]
        return c + ' ' + p