from typing import Union, List, Dict

State = Dict[str, Union[int, List[List[List[int]]]]]


from typing import Union, Tuple

Move = Union[Tuple[str, int, int, int, int], Tuple[str, int, int, int, int, int, int, int]]


WHITE = 1
BLACK = -1

SET_PIECE = 'set'
MOVE_PIECE = 'move'
REMOVE_PIECE = 'remove' 

MOVE_TYPE = 0
MOVE_COLOR = 1
MOVE_X = 2
MOVE_Y = 3
MOVE_Z = 4


def is_end(state: State) -> bool:
    return state['white_remaining'] == 0 and state['black_remaining'] == 0 and (state['white_count'] <= 2 or state['black_count'] <= 2)

def can_move(state: State, player: int) -> bool:
    # Check if there are any legal moves available for 'player'
    return any(get_moves(state, player, False))

WINNING_SCORE = 100000
LINE_VALUE = 500  # Vrednost za formiranje linije
JUMPING_VALUE = 150 
mill_potential_value = 1000  
block_mill_value = 800  
def evaluate(state: State, current_player: int, last_move: Move = None) -> int:
    value = 0  # Initialize the value variable
    opponent = -current_player

    mill_potential_value = 1000  # Value for potential mills
    block_mill_value = 800  # Value for blocking opponent mills

    # Basic evaluation based on the number and positions of pieces
    for square in range(3):
        for line in range(3):
            line_sum = sum(state['pieces'][square][line])
            col_sum = sum(state['pieces'][square][i][line % 2] for i in range(3))

            if abs(line_sum) == 3:  # Complete mill
                value += (LINE_VALUE if line_sum / 3 == current_player else -LINE_VALUE)
            if abs(col_sum) == 3:  # Complete mill
                value += (LINE_VALUE if col_sum / 3 == current_player else -LINE_VALUE)

            # Evaluate potential and blocked mills
            if state['pieces'][square][line].count(current_player) == 2 and state['pieces'][square][line].count(None) == 1:
                value += mill_potential_value
            if state['pieces'][square][line].count(opponent) == 2 and state['pieces'][square][line].count(None) == 1:
                value += block_mill_value

    # Evaluate jumping value
    if state['white_count'] == 3:
        value += (JUMPING_VALUE if current_player == WHITE else -JUMPING_VALUE)
    if state['black_count'] == 3:
        value += (JUMPING_VALUE if current_player == BLACK else -JUMPING_VALUE)

    # Winning condition
    if state['black_count'] <= 2 or not can_move(state, BLACK):
        return (WINNING_SCORE if current_player == WHITE else -WINNING_SCORE)
    if state['white_count'] <= 2 or not can_move(state, WHITE):
        return (WINNING_SCORE if current_player == BLACK else -WINNING_SCORE)

    # Additional points for the possibility of forming a line again after moving a piece
    if last_move and last_move[MOVE_TYPE] == MOVE_PIECE and can_form_line_again(state, current_player, last_move[5], last_move[6], last_move[7]):
        value += 150
    elif last_move and last_move[MOVE_TYPE] == REMOVE_PIECE and can_form_line_again(state, current_player, last_move[2], last_move[3], last_move[4]):
        value += 500

    return value

def can_form_line_again(state: State, player: int, from_x: int, from_y: int, from_z: int) -> bool:
    # Save the original state to restore later
    original_state = state['pieces'][from_x][from_y][from_z]
    state['pieces'][from_x][from_y][from_z] = 0

    # Check potential moves to reform the line
    potential_moves = get_neighboaring_empty_spots(state, from_x, from_y, from_z)
    for to_x, to_y, to_z in potential_moves:
        # Temporarily make the move
        state['pieces'][to_x][to_y][to_z] = player
        # Check if it forms a line
        if is_making_line(state, ('move', player, to_x, to_y, to_z, from_x, from_y, from_z)):
            # Restore the state before returning
            state['pieces'][to_x][to_y][to_z] = 0
            state['pieces'][from_x][from_y][from_z] = original_state
            return True
        # Restore the state after checking
        state['pieces'][to_x][to_y][to_z] = 0

    # Restore the original state
    state['pieces'][from_x][from_y][from_z] = original_state
    return False


def get_neighboaring_empty_spots(state, x, y, z):
    pieces = state['pieces']
    
    # left
    if y != 1 and z - 1 >= 0 and pieces[x][y][z - 1] == 0:
        yield x, y, z - 1
    
    # right
    if y != 1 and z + 1 <= 2 and pieces[x][y][z + 1] == 0:
        yield x, y, z + 1
    
    # up
    if z != 1 and y - 1 >= 0 and pieces[x][y - 1][z] == 0:
        yield x, y - 1, z
    
    # down
    if z != 1 and y + 1 <= 2 and pieces[x][y + 1][z] == 0:
        yield x, y + 1, z
    
    # cross-square out
    if (y == 1 or z == 1) and x - 1 >= 0 and pieces[x - 1][y][z] == 0:
        yield x - 1, y, z
    
    # cross-square in
    if (y == 1 or z == 1) and x + 1 <= 2 and pieces[x + 1][y][z] == 0:
        yield x + 1, y, z
def get_moves(state: State, player: int, line_made: bool) -> list[Move]:
    moves = []
    if line_made:
        # Koristi funkcije get_non_mill_pieces i get_mill_pieces za dobijanje figura
        non_mill_pieces = get_non_mill_pieces(state, -player)
        mill_pieces = get_mill_pieces(state, -player)
        
        if non_mill_pieces:
            moves.extend(non_mill_pieces)
        else:
            moves.extend(mill_pieces)
    else:
        # Proces postavljanja i pomeranja figura
        if state[f'{color(player)}_remaining'] > 0:
            # Logika za postavljanje figura
            for s, square in enumerate(state['pieces']):
                for i, row in enumerate(square):
                    for j, element in enumerate(row):
                        if i == 1 and j == 1:  # preskakanje centralne tačke
                            continue
                        if element == 0:
                            moves.append(('set', player, s, i, j))
        else:
            # Logika za pomeranje figura
            for s, square in enumerate(state['pieces']):
                for i, row in enumerate(square):
                    for j, element in enumerate(row):
                        if element == player:
                            if state[f'{color(player)}_count'] <= 3:
                                # Skakanje na bilo koje prazno mesto
                                for x, square_x in enumerate(state['pieces']):
                                    for y, row_y in enumerate(square_x):
                                        for z, _ in enumerate(row_y):
                                            if state['pieces'][x][y][z] == 0:
                                                moves.append(('move', player, x, y, z, s, i, j))
                            else:
                                # Standardno pomeranje na susedna prazna mesta
                                for x, y, z in get_neighboaring_empty_spots(state, s, i, j):
                                    moves.append(('move', player, x, y, z, s, i, j))
    return moves

def get_non_mill_pieces(state: State, opponent: int) -> list[Move]:
    non_mill_pieces = []
    for s, square in enumerate(state['pieces']):
        for i, row in enumerate(square):
            for j, piece in enumerate(row):
                if piece == opponent:
                    if not is_making_line(state, ('check', opponent, s, i, j)):
                        non_mill_pieces.append(('remove', -opponent, s, i, j))
    return non_mill_pieces

def get_mill_pieces(state: State, opponent: int) -> list[Move]:
    mill_pieces = []
    for s, square in enumerate(state['pieces']):
        for i, row in enumerate(square):
            for j, piece in enumerate(row):
                if piece == opponent:
                    if is_making_line(state, ('check', opponent, s, i, j)):
                        mill_pieces.append(('remove', -opponent, s, i, j))
    return mill_pieces

def isMoveValid(move: Move, state: State) -> bool:
    move_type, player, x, y, z, *rest = move

    if move_type == SET_PIECE:
        # Proverava da li je polje slobodno za postavljanje figure
        return state['pieces'][x][y][z] == 0 and state[f'{color(player)}_remaining'] > 0

    elif move_type == MOVE_PIECE:
        from_x, from_y, from_z = rest
        # Proverava da li igrač pomeri svoju figuru na slobodno mesto
        # Ako igrač ima 3 ili manje figura, može se pomerati na bilo koje slobodno mesto
        if state['pieces'][from_x][from_y][from_z] == player:
            if state['white_count' if player == WHITE else 'black_count'] <= 3:
                return state['pieces'][x][y][z] == 0  # Dozvoljeno skakanje
            else:
                return state['pieces'][x][y][z] == 0 and any(
                    (x, y, z) == spot for spot in get_neighboaring_empty_spots(state, from_x, from_y, from_z)
                )
        return False

    elif move_type == REMOVE_PIECE:
        # Proverava da li igrač uklanja protivničku figuru koja nije deo linije, osim ako su sve protivničke figure u linijama
        if state['pieces'][x][y][z] == -player:
            if not is_making_line(state, move) or all_figures_in_line(state, -player):
                return True

    return False


def color(player):
    return 'white' if player == WHITE else 'black'

def all_figures_in_line(state, player):
    for s, square in enumerate(state['pieces']):
        for i, row in enumerate(square):
            for j, element in enumerate(row):
                if element == player:
                    if not is_making_line(state, ('check', player, s, i, j)):
                        return False
    return True

def is_making_line(state: State, move: Move) -> bool:
    pieces = state['pieces']
    _, _, x, y, z, *_ = move

    # Provera horizontalne linije u trenutnom kvadratu
    if abs(sum(pieces[x][y])) == 3:
        return True
    
    # Provera vertikalne linije u trenutnom kvadratu
    if abs(sum(pieces[x][i][z] for i in range(3))) == 3:
        return True
    
    # Provera horizontalne linije kroz srednji red svih kvadrata
    if y == 1 and abs(sum(pieces[i][y][z] for i in range(3))) == 3:
        return True
    
    # Provera vertikalne linije kroz srednju kolonu svih kvadrata
    if z == 1 and abs(sum(pieces[x][i][1] for i in range(3))) == 3:
        return True

    return False


def apply_move(state: State, move: Move):
    pieces = state['pieces']
    if move is None:
        raise ValueError("A move cannot be None")
    if move[MOVE_TYPE] == SET_PIECE:
        _, color, x, y, z = move
        if None in (x, y, z):
            raise ValueError(f"Invalid move coordinates: {move}")
        pieces[x][y][z] = color
        state['white_remaining' if color == WHITE else 'black_remaining'] -= 1
        state['white_count' if color == WHITE else 'black_count'] += 1
    elif move[MOVE_TYPE] == REMOVE_PIECE:
        _, color, x, y, z = move
        pieces[x][y][z] = 0
        state['white_count' if color == WHITE else 'black_count'] -= 1
    elif move[MOVE_TYPE] == MOVE_PIECE:
        _, color, to_x, to_y, to_z, from_x, from_y, from_z = move
        pieces[from_x][from_y][from_z] = 0
        pieces[to_x][to_y][to_z] = color
        
    state['turn'] += 1


def undo_move(state: State, move: Move):
    pieces = state['pieces']
    if move[MOVE_TYPE] == SET_PIECE:
        _, color, x, y, z = move
        pieces[x][y][z] = 0
        state['white_remaining' if color == WHITE else 'black_remaining'] += 1
        state['white_count' if color == WHITE else 'black_count'] -= 1
    elif move[MOVE_TYPE] == REMOVE_PIECE:
        _, color, x, y, z = move
        pieces[x][y][z] = color * -1
        state['white_count' if color == WHITE else 'black_count'] += 1
    elif move[MOVE_TYPE] == MOVE_PIECE:
        _, color, to_x, to_y, to_z, from_x, from_y, from_z = move
        pieces[from_x][from_y][from_z] = color
        pieces[to_x][to_y][to_z] = 0
    
    state['turn'] += 1
def minimax(state, depth, current_player, line_made=False):
    if depth == 0 or is_end(state):
        return evaluate(state, current_player), None

    best_eval = -float('inf') if current_player == WHITE else float('inf')
    best_move = None

    for move in get_moves(state, current_player, line_made):
        if isMoveValid(move, state):
            apply_move(state, move)
            eval, _ = minimax(state, depth - 1, -current_player, is_making_line(state, move))
            undo_move(state, move)

            if current_player == WHITE and eval > best_eval:
                best_eval = eval
                best_move = move
            elif current_player == BLACK and eval < best_eval:
                best_eval = eval
                best_move = move

    return best_eval, best_move

def apply_temporary_move(state: State, move: Move, current_player: int) -> int:
    if not isMoveValid(move, state):
        return -float('inf') if move[1] == current_player else float('inf')

    apply_move(state, move)
    score = evaluate(state, move[1], last_move=move)
    undo_move(state, move)
    return score

def alphabeta(state: State, depth: int, alpha: int, beta: int, player: int, line_made: bool = False) -> tuple[int, Move | None]:
    if depth == 0 or is_end(state):
        return evaluate(state, player), None  # Include the current player in the evaluation

    next_player = -player
    best_move = None

    if player == WHITE:
        best_value = -float('inf')
        for move in get_moves(state, player, line_made):
            if isMoveValid(move, state):
                apply_move(state, move)
                value, _ = alphabeta(state, depth - 1, alpha, beta, next_player, line_made)
                undo_move(state, move)

                if value > best_value:
                    best_value = value
                    best_move = move
                alpha = max(alpha, value)

                if beta <= alpha:
                    break
    else:  
        best_value = float('inf')
        for move in get_moves(state, player, line_made):
            if isMoveValid(move, state):
                apply_move(state, move)
                value, _ = alphabeta(state, depth - 1, alpha, beta, next_player, line_made)
                undo_move(state, move)

                if value < best_value:
                    best_value = value
                    best_move = move
                beta = min(beta, value)

                if beta <= alpha:
                    break

    return best_value, best_move
