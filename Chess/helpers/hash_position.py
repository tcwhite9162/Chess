import hashlib

def encode_position(grid, turn, castling_rights, en_passant_square):
    position_string = []

    for row in grid:
        for piece in row:
            if piece:
                position_string.append(f"{piece.type}{piece.color}")
            else:
                position_string.append(".")
    
    position_string.append(turn)

    for color in ['w', 'b']:
        for side in ['k', 'q']:
            position_string.append('1' if castling_rights[color][side] else '0')

    if en_passant_square:
        position_string.append(f"ep{en_passant_square[0]}{en_passant_square[1]}")
    else:
        position_string.append('ep--')

    return hashlib.sha256("".join(position_string).encode()).hexdigest()