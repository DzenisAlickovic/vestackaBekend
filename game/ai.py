import copy
from typing import Union, List, Dict

State = Dict[str, Union[int, List[List[List[int]]]]]


from typing import Union, Tuple

Move = Union[Tuple[str, int, int, int, int], Tuple[str, int, int, int, int, int, int, int]]

SET_PIECE= 'set'
MOVE_PIECE= 'move'
REMOVE_PIECE= 'remove'

WHITE = 1
BLACK = -1

# potez izgleda ovako (MOVE_TYPE, MOVE_COLOR, MOVE_X, MOVE_Y, MOVE_Z)
# ove konstante su indeksi u tuple koji predstavlja potez
# npr: ako indeksiramo potez sa MOVE_TYPE (nulom), dobicemo tip poteza
MOVE_TYPE = 0
MOVE_COLOR = 1
MOVE_X = 2
MOVE_Y = 3
MOVE_Z = 4


def is_end(state):
    # Ako nema preostalih figura za postavljanje i broj figura na tabli je 2 ili manje, igra je završena
    if state['white_remaining'] == 0 and state['black_remaining'] == 0:
        if state['white_count'] <= 2 or state['black_count'] <= 2:
            return True
        # Proverava da li igrač na potezu ima mogućih poteza
        current_player = WHITE if state['turn'] % 2 == 0 else BLACK
        if not can_move(state, current_player):
            return True
    return False


# pieces[square][line][spot]
# [
#       0  1  2 
#       ^--^--^--- polja unutar linije      
#    
#     [[0, 0, 0],   kvadrat 0   linija 0
#      [0, X, 0],               linija 1
#      [0, 0, 0]],              linija 2
#
#     [[0, 0, 0],   kvadrat 1   linija 0
#      [0, X, 0],               linija 1
#      [0, 0, 0]],              linija 2
#
#     [[0, 0, 0],   kvadrat 2   linija 0
#      [0, X, 0],               linija 1
#      [0, 0, 0]],              linija 2
# ]

def can_move(state, player):
    # Ova funkcija bi trebala da proverava da li igrač može da napravi bilo kakav potez
    # Za svaku figuru igrača proverite da li postoje slobodna susedna mesta na koja se može pomeriti
    for s, square in enumerate(state['pieces']):
        for i, row in enumerate(square):
            for j, spot in enumerate(row):
                if spot == player:
                    # Ako postoji barem jedan validan potez, vrati True
                    for x, y, z in get_neighboaring_empty_spots(state, s, i, j):
                        return True
    return False
WINNING_SCORE = 100000
LINE_VALUE = 8000
mill_potential_value = 3500
mill_forming_potential_value = 9000
potential_line_value = 1000

def evaluate(state):
    value = 0
    pieces = state['pieces']
    player = WHITE if state['turn'] % 2 == 0 else BLACK  # Određujemo igrača na potezu
    block_mill_value = 10000 if state['white_remaining'] > 0 or state['black_remaining'] > 0 else 4000

    # Proveravamo za svaki kvadrat i svaku liniju
    for square in range(3):
        for line in range(3):
            line_pieces = pieces[square][line]
            col_pieces = [pieces[square][i][line] for i in range(3)]  

            # Postojeće evaluacije
            line_sum = sum(line_pieces)
            col_sum = sum(col_pieces)
            if abs(line_sum) == 3:
                value += LINE_VALUE if line_sum > 0 else -LINE_VALUE
            if abs(col_sum) == 3:
                value += LINE_VALUE if col_sum > 0 else -LINE_VALUE

            # Evaluacija potencijalnih linija
            if line_pieces.count(1) == 2 and line_pieces.count(0) == 1 or col_pieces.count(1) == 2 and col_pieces.count(0) == 1:
                value += mill_potential_value
            if line_pieces.count(-1) == 2 and line_pieces.count(0) == 1 or col_pieces.count(-1) == 2 and col_pieces.count(0) == 1:
                value -= mill_potential_value
                
                 # Provera da li igrač može blokirati mlin protivnika
            if line_pieces.count(-1) == 2 and line_pieces.count(0) == 1:
                value += block_mill_value
            if col_pieces.count(-1) == 2 and col_pieces.count(0) == 1:
                value += block_mill_value
            
            # Dodavanje potencijalne vrednosti za linije koje još nisu formirane
            if line_pieces.count(1) == 2 and line_pieces.count(0) == 1 or col_pieces.count(1) == 2 and col_pieces.count(0) == 1:
                value += potential_line_value if line_pieces.count(1) > line_pieces.count(-1) else -potential_line_value

    # Uslov pobede
    if state['black_count'] <= 2 or not can_move(state, -1):
        return WINNING_SCORE if state['turn'] % 2 == 0 else -WINNING_SCORE
    if state['white_count'] <= 2 or not can_move(state, 1):
        return WINNING_SCORE if state['turn'] % 2 != 0 else -WINNING_SCORE

    # Broj komada kao dodatni faktor
    value += (state['white_count'] - state['black_count']) * 5000
    # Dodajemo dodatne poene ako AI ima mogućnost da formira mlin
    for x in range(3):
        for y in range(3):
            for z in range(3):
                if pieces[x][y][z] == player and can_break_and_reform_mill(state, player, x, y, z):
                    value += mill_forming_potential_value

    return value
def easy_evaluate(state):
    value = 0
    pieces = state['pieces']
    block_mill_value = 100000 if state['white_remaining'] > 0 or state['black_remaining'] > 0 else 6000 
     # Proveravamo za svaki kvadrat i svaku liniju
    for square in range(3):
        for line in range(3):
            line_pieces = pieces[square][line]
            col_pieces = [pieces[square][i][line] for i in range(3)]  

            # Postojeće evaluacije
            line_sum = sum(line_pieces)
            col_sum = sum(col_pieces)
            if abs(line_sum) == 3:
                value += LINE_VALUE if line_sum > 0 else -LINE_VALUE
            if abs(col_sum) == 3:
                value += LINE_VALUE if col_sum > 0 else -LINE_VALUE
                
                 # Provera da li igrač može blokirati mlin protivnika
            if line_pieces.count(-1) == 2 and line_pieces.count(0) == 1:
                value += block_mill_value
            if col_pieces.count(-1) == 2 and col_pieces.count(0) == 1:
                value += block_mill_value
                
            

    # Uslov pobede
    if state['black_count'] <= 2 or not can_move(state, -1):
        return WINNING_SCORE if state['turn'] % 2 == 0 else -WINNING_SCORE
    if state['white_count'] <= 2 or not can_move(state, 1):
        return WINNING_SCORE if state['turn'] % 2 != 0 else -WINNING_SCORE
     # Broj komada kao dodatni faktor
    value += (state['white_count'] - state['black_count']) * 5000
    return value
def medium_evaluate(state):
    value = 0
    pieces = state['pieces']
    block_mill_value = 20000 if state['white_remaining'] > 0 or state['black_remaining'] > 0 else 6000 
     # Proveravamo za svaki kvadrat i svaku liniju
    for square in range(3):
        for line in range(3):
            line_pieces = pieces[square][line]
            col_pieces = [pieces[square][i][line] for i in range(3)]  

            # Postojeće evaluacije
            line_sum = sum(line_pieces)
            col_sum = sum(col_pieces)
            if abs(line_sum) == 3:
                value += LINE_VALUE if line_sum > 0 else -LINE_VALUE
            if abs(col_sum) == 3:
                value += LINE_VALUE if col_sum > 0 else -LINE_VALUE

            # Evaluacija potencijalnih linija
            if line_pieces.count(1) == 2 and line_pieces.count(0) == 1 or col_pieces.count(1) == 2 and col_pieces.count(0) == 1:
                value += mill_potential_value
            if line_pieces.count(-1) == 2 and line_pieces.count(0) == 1 or col_pieces.count(-1) == 2 and col_pieces.count(0) == 1:
                value -= mill_potential_value
                
                 # Provera da li igrač može blokirati mlin protivnika
            if line_pieces.count(-1) == 2 and line_pieces.count(0) == 1:
                value += block_mill_value
            if col_pieces.count(-1) == 2 and col_pieces.count(0) == 1:
                value += block_mill_value
                 # Dodavanje potencijalne vrednosti za linije koje još nisu formirane
            if line_pieces.count(1) == 2 and line_pieces.count(0) == 1 or col_pieces.count(1) == 2 and col_pieces.count(0) == 1:
                value += potential_line_value if line_pieces.count(1) > line_pieces.count(-1) else -potential_line_value
            
    # Uslov pobede
    if state['black_count'] <= 2 or not can_move(state, -1):
        return WINNING_SCORE if state['turn'] % 2 == 0 else -WINNING_SCORE
    if state['white_count'] <= 2 or not can_move(state, 1):
        return WINNING_SCORE if state['turn'] % 2 != 0 else -WINNING_SCORE
     # Broj komada kao dodatni faktor
    value += (state['white_count'] - state['black_count']) * 5000
    return value

def can_break_and_reform_mill(state, player, from_x, from_y, from_z):
    # Pretpostavljamo da se figura može pomeriti samo na susedna prazna mesta
    original_piece = state['pieces'][from_x][from_y][from_z]
    state['pieces'][from_x][from_y][from_z] = 0  # Privremeno uklanjamo figuru

    # Proveravamo sve susedne pozicije
    for (to_x, to_y, to_z) in get_neighboaring_empty_spots(state, from_x, from_y, from_z):
        state['pieces'][to_x][to_y][to_z] = player  # Simuliramo pomeranje na susedno mesto
        if is_making_line(state, ('move', player, to_x, to_y, to_z, from_x, from_y, from_z)):
            # Ako formiramo mlin, proveravamo možemo li ponovno formirati mlin pomeranjem nazad
            state['pieces'][to_x][to_y][to_z] = 0  # Vraćamo na prazno mesto
            state['pieces'][from_x][from_y][from_z] = original_piece  # Vraćamo originalnu figuru
            if is_making_line(state, ('move', player, from_x, from_y, from_z, to_x, to_y, to_z)):
                return True  # Možemo formirati mlin ponovnim pomeranjem
        state['pieces'][to_x][to_y][to_z] = 0  # Vraćamo na prazno mesto

    state['pieces'][from_x][from_y][from_z] = original_piece  # Vraćamo originalnu figuru
    return False


# prazna polja koja su susedna nekom kamenu.
# x, y, z su koordinata datog kamena
def get_neighboaring_empty_spots(state, x, y, z):
    pieces = state['pieces']

    # gde imaju sloboda mesta na levoj strani gde da stavi kamen
    if y != 1 and z - 1 >= 0 and pieces[x][y][z - 1] == 0:
        yield x, y, z - 1

    # gde imaju sloboda mesta na desnoj strani
    if y != 1 and z + 1 <= 2 and pieces[x][y][z + 1] == 0:
        yield x, y, z + 1

    # gore
    if z != 1 and y - 1 >= 0 and pieces[x][y - 1][z] == 0:
        yield x, y - 1, z

    # dole
    if z != 1 and y + 1 <= 2 and pieces[x][y + 1][z] == 0:
        yield x, y + 1, z

    # proverava ima li prazno polje po liniji koa spaja kvadrate
    # gleda ka spoljnjem kvadratu (kvadratu koji je oko trenutnog)
    if (y == 1 or z == 1) and x - 1 >= 0 and pieces[x - 1][y][z] == 0:
        yield x - 1, y, z

    # proverava ima li prazno polje po liniji koa spaja kvadrate
    # gleda ka unutrasnjem kvadratu (kvadratu koji je unutar trenutnog)
    if (y == 1 or z == 1) and x + 1 <= 2 and pieces[x + 1][y][z] == 0:
        yield x + 1, y, z


def get_non_mill_pieces(state: State, opponent: int) -> list[Move]:
    non_mill_pieces = []
    mill_pieces = get_mill_pieces(state, opponent)  # Get mill pieces to check if all pieces are in mills
    for s, square in enumerate(state['pieces']):
        for i, row in enumerate(square):
            for j, piece in enumerate(row):
                if piece == opponent:
                    if not is_making_line(state, ('check', opponent, s, i, j)) or not mill_pieces:
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

def get_moves(state, player, line_made):
    moves = []
    # Provera da li je napravljena linija, ako jeste uklanjaju se protivničke figure koje nisu deo mill-a
    if line_made:
        non_mill_opponents = get_non_mill_pieces(state, -player)
        if non_mill_opponents:
            moves.extend(non_mill_opponents)
        else:
            mill_opponents = get_mill_pieces(state, -player)
            moves.extend(mill_opponents)
        return moves

    # Logika za postavljanje figura na tablu
    current_player_remaining = 'white_remaining' if player == WHITE else 'black_remaining'
    if state[current_player_remaining] > 0:
        for s, square in enumerate(state['pieces']):
            for i, row in enumerate(square):
                for j, element in enumerate(row):
                    if i == 1 and j == 1:  # Preskakanje centra
                        continue
                    if element == 0:  # Prazno polje
                        moves.append((SET_PIECE, player, s, i, j))
    else:
        # Logika za pomeranje figura na tabli
        for s, square in enumerate(state['pieces']):
            for i, row in enumerate(square):
                for j, element in enumerate(row):
                    if element == player:
                        for x, y, z in get_neighboaring_empty_spots(state, s, i, j):
                            moves.append((MOVE_PIECE, player, x, y, z, s, i, j))

    return moves

def is_making_line(state, move):
    pieces = state['pieces']
    _, _, x, y, z, *_ = move

    # Provera horizontalnu liniju
    if abs(sum(pieces[x][y])) == 3:
        return True

    # Provera vertikalnu liniju
    if abs(sum(pieces[x][i][z] for i in range(3))) == 3:
        return True

    # Provera linija(sredisnja) koje spajaju kvadrate
    if y == 0 or y == 2:
        # gornja sredisnja linija
        if abs(sum(pieces[x][0][1] for x in range(3))) == 3:
            return True
        # donja
        if abs(sum(pieces[x][2][1] for x in range(3))) == 3:
            return True
    if z == 0 or z == 2:
        # leva
        if abs(sum(pieces[x][1][0] for x in range(3))) == 3:
            return True
        # desna
        if abs(sum(pieces[x][1][2] for x in range(3))) == 3:
            return True

    return False


# ovde prati trenutno stanje
def apply_move(state, move):
    pieces = state['pieces']
    if move[MOVE_TYPE] == SET_PIECE:  # koji je potez na redu u ovom slucaju je postavljanje
        _, color, x, y, z = move  # uzimamo koordinate tog kamena i njegovu boju
        # na tim koordinatama postavljamo kamen odgovarajuce boje
        pieces[x][y][z] = color
        # kada postavi kamen smanjuje za jedan od onih koje ima
        state['white_remaining' if color == WHITE else 'black_remaining'] -= 1
        # povecava broj kamena na tabli
        state['white_count' if color == WHITE else 'black_count'] += 1
    elif move[MOVE_TYPE] == REMOVE_PIECE:  # sada ako je na redu uklanjanje
        _, color, x, y, z = move  # isto proverava koordinate kamena koji uklanjamo
        # kada pojedemo kamen tu stavljamo stanje 0, znaci da na toj koordinati nema vise kamena na tabli
        pieces[x][y][z] = 0
        # gleda se koja je boja, i uklanja se taj kamen
        state['white_count' if color == WHITE else 'black_count'] -= 1
    elif move[MOVE_TYPE] == MOVE_PIECE:  # pomeranje kamena
        # sada uzimamo koordinate oba kamena gde treba da postavi i gde da makne
        # sa koordinata koje pocinju sa 'from' se uklanja kamen
        # a na koordinate koje pocinju sa 'to' se postavlja kamen
        _, color, to_x, to_y, to_z, from_x, from_y, from_z = move
        # na to mesto gde se makao kamen restartuje vrednost na 0
        pieces[from_x][from_y][from_z] = 0
        # na toj novoj poziciji gde se postavio kamen se stavlja odgovarajuca boja odnosno vrednost
        pieces[to_x][to_y][to_z] = color

    state['turn'] += 1


def minimax(state, depth, player, line_made=False):
    if depth == 0 or is_end(state):
        return easy_evaluate(state), None

    next_player = player * -1
    if player == WHITE:
        max_eval = float('-inf')
        best_move = None
        for move in get_moves(state, player, line_made):
            state_copy = copy.deepcopy(state)
            apply_move(state_copy, move)
            move_made_line = is_making_line(state_copy, move)
            eval, _ = minimax(state_copy, depth - 1, next_player, move_made_line)
            if eval > max_eval or best_move is None:
                max_eval = eval
                best_move = move
        return max_eval, best_move
    else:
        min_eval = float('inf')
        best_move = None
        for move in get_moves(state, player, line_made):
            state_copy = copy.deepcopy(state)
            apply_move(state_copy, move)
            move_made_line = is_making_line(state_copy, move)
            eval, _ = minimax(state_copy, depth - 1, next_player, move_made_line)
            if eval < min_eval or best_move is None:
                min_eval = eval
                best_move = move
        return min_eval, best_move


def alphabeta(state, depth, alpha, beta, player, line_made=False):
    if depth == 0 or is_end(state):
        return evaluate(state), None

    next_player = player * -1
    if player == WHITE:
        value = float('-inf')
        best_move = None
        for move in get_moves(state, player, line_made):
            state_copy = copy.deepcopy(state)
            apply_move(state_copy, move)
            move_made_line = is_making_line(state_copy, move)
            eval, _ = alphabeta(state_copy, depth - 1, alpha, beta, next_player, move_made_line)
            if eval > value:
                value = eval
                best_move = move
            alpha = max(alpha, value)
            if beta <= alpha:
                break
        return value, best_move
    else:
        value = float('inf')
        best_move = None
        for move in get_moves(state, player, line_made):
            state_copy = copy.deepcopy(state)
            apply_move(state_copy, move)
            move_made_line = is_making_line(state_copy, move)
            eval, _ = alphabeta(state_copy, depth - 1, alpha, beta, next_player, move_made_line)
            if eval < value:
                value = eval
                best_move = move
            beta = min(beta, value)
            if beta <= alpha:
                break
        return value, best_move

def alphabeta(state, depth, alpha, beta, player, line_made=False):
    if depth == 0 or is_end(state):
        return medium_evaluate(state), None

    next_player = player * -1
    if player == WHITE:
        value = float('-inf')
        best_move = None
        for move in get_moves(state, player, line_made):
            state_copy = copy.deepcopy(state)
            apply_move(state_copy, move)
            move_made_line = is_making_line(state_copy, move)
            eval, _ = alphabeta(state_copy, depth - 1, alpha, beta, next_player, move_made_line)
            if eval > value:
                value = eval
                best_move = move
            alpha = max(alpha, value)
            if beta <= alpha:
                break
        return value, best_move
    else:
        value = float('inf')
        best_move = None
        for move in get_moves(state, player, line_made):
            state_copy = copy.deepcopy(state)
            apply_move(state_copy, move)
            move_made_line = is_making_line(state_copy, move)
            eval, _ = alphabeta(state_copy, depth - 1, alpha, beta, next_player, move_made_line)
            if eval < value:
                value = eval
                best_move = move
            beta = min(beta, value)
            if beta <= alpha:
                break
        return value, best_move


            

            
