# A million thanks to Keith Galli at https://youtu.be/MMLtza3CZFM
import numpy as np
import random

COL_COUNT = 7
ROW_COUNT = 6
HUMAN = 1
AI = 2
WINDOW_SIZE = 4 # the number of connections in a row we're looking for to win
EMPTY_SPOT = 0 # the value that represents an empty, available location

def display_welcome():
    print(' _____                             _       ___ ')
    print('/  __ \\                           | |     /   |')
    print('| /  \\/ ___  _ __  _ __   ___  ___| |_   / /| |')
    print('| |    / _ \\| \'_ \\| \'_ \\ / _ \\/ __| __| / /_| |')
    print('| \\__/\\ (_) | | | | | | |  __/ (__| |_  \\___  |')
    print(' \\____/\\___/|_| |_|_| |_|\\___|\\___|\\__|     |_/\n')
    print('Welcome to Connect 4!')
    print('When it\'s your turn, please type a column number (1-', COL_COUNT,
          ')', sep = '', end = '')
    print(' to drop a piece there.\n')
    print('Here\'s the board - your pieces appear as the number', end = '')
    print(' 1 and the AI\'s as number 2,')
    print('while available spaces are represented as 0:\n')

def create_board():
    # Create a 7x6 matrix filled with zeros
    board = np.zeros((ROW_COUNT, COL_COUNT))
    return board

def drop_piece(board, col, row, piece):
    # Drop the piece in the first unoccupied row at the column selected
    board[row][col] = piece

def is_valid_location(board, col):
    # Is the top row in the column selected 0, or empty? If so, it can be played
    return board[ROW_COUNT - 1][col] == 0

def get_next_open_row(board, col):
    # Return the first empty row in the selected column
    for row in range(ROW_COUNT):
        if board[row][col] == 0:
            return row

    return None

def get_player_column(player_num, board):
    player_num = str(player_num)

    is_valid_input = False

    while not is_valid_input:
        try:
            # The player enters a column as a 1-based index, which we then
            # convert to a 0-based index to use internally
            col_num = input('Player ' + player_num + ', select a column: ')
            col_num = int(col_num) - 1 # convert to a zero-based index

            # Check bounds and availability of the location
            if col_num >= 0 and col_num < COL_COUNT \
               and is_valid_location(board, col_num):
                is_valid_input = True
            else:
                print('\nSorry, valid columns are between 1 and ', COL_COUNT,
                       ' and are not full. Please try again.', sep = '')
        except ValueError:
            print('\nSorry, only numbers are accepted. Please try again.')

    print() # blank space
    return col_num

def display_board(board):
    print(np.flip(board, 0))
    print() # blank space

def is_winning_move(board, piece):
    # Check all the horizontal locations
    # Not the most efficient check, but it works
    # Eventually, this function needs to be made to work with any number of rows
    # and columns
    for col in range(COL_COUNT - 3): # can't start a win at the last 3 columns
        for row in range(ROW_COUNT):
            if board[row][col] == piece \
               and board[row][col + 1] == piece \
               and board[row][col + 2] == piece \
               and board[row][col + 3] == piece:
                return True

    # Check the vertical locations
    for col in range(COL_COUNT):
        for row in range(ROW_COUNT - 3):
            if board[row][col] == piece \
               and board[row + 1][col] == piece \
               and board[row + 2][col] == piece \
               and board[row + 3][col] == piece:
                return True

    # Check the positively sloped diagonals
    for col in range(COL_COUNT - 3):
        for row in range(ROW_COUNT - 3):
            if board[row][col] == piece \
               and board[row + 1][col + 1] == piece \
               and board[row + 2][col + 2] == piece \
               and board[row + 3][col + 3] == piece:
                return True

    # Check the negatively sloped diagonals
    for col in range(COL_COUNT - 3):
        for row in range(3, ROW_COUNT):
            if board[row][col] == piece \
               and board[row - 1][col + 1] == piece \
               and board[row - 2][col + 2] == piece \
               and board[row - 3][col + 3] == piece:
                return True

def get_window_eval_score(window, piece):
    opponent_piece = HUMAN

    if piece == HUMAN:
        opponent_piece = AI

    score = 0

     # Found 4 in a row
    if window.count(piece) == WINDOW_SIZE:
        score += 100
    # Found 3 in a row
    elif window.count(piece) == 3 and window.count(EMPTY_SPOT) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY_SPOT) == 2:
        score += 2

    # The opponent has 3 in a row
    if window.count(opponent_piece) == 3 and window.count(EMPTY_SPOT) == 1:
        score -= 4

    return score
    
def get_position_score(board, piece):
    score = 0

    # Score the center column higher
    center_array = [int(i) for i in list(board[:, COL_COUNT // 2])]
    center_count = center_array.count(piece)
    score += center_count * 6

    # Score the horizontal locations with 100 if it's a win
    for row in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[row, :])]

        for col in range(COL_COUNT - 3):
            window = row_array[col:col + WINDOW_SIZE]
            get_window_eval_score(window, piece)

    # Score the vertical locations
    for col in range(COL_COUNT):
        col_array = [int(i) for i in list(board[:, col])]

        for row in range(ROW_COUNT - 3):
            window = col_array[row:row + WINDOW_SIZE]
            get_window_eval_score(window, piece)

    # Score the positively sloped diagonals
    for row in range(ROW_COUNT - 3):
        for col in range(COL_COUNT - 3):
            window = [board[row + i][col + i] for i in range(WINDOW_SIZE)]
            get_window_eval_score(window, piece)

    # Score the negatively sloped diagonals
    for row in range(ROW_COUNT - 3):
        for col in range(COL_COUNT - 3):
            window = [board[row + 3 - i][col + i] for i in range(WINDOW_SIZE)]
            get_window_eval_score(window, piece)

    return score

def is_terminal_node(board):
    return is_winning_move(board, HUMAN) or is_winning_move(board, AI) \
           or len(get_valid_locations(board)) == 0

# The star of the show
# Uses alpha-beta pruning to speed up the process, skipping useless branches
def minimax(board, depth, alpha, beta, is_maximizing_player):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)

    if depth == 0 or is_terminal:
        if is_terminal:
            if is_winning_move(board, AI):
                return None, 1000000000000
            elif is_winning_move(board, HUMAN):
                return None, -1000000000000
            else: # game over, no more valid moves
                return None, 0
        else: # depth is 0
            return None, get_position_score(board, AI)

    # The AI is the maximizing player
    if is_maximizing_player:
        value = float('-Inf')
        column = random.choice(valid_locations)

        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, col, row, AI)
            new_score = minimax(temp_board, depth - 1, alpha, beta, False)[1]

            if new_score > value:
                value = new_score
                column = col

            alpha = max(alpha, value)

            if alpha >= beta:
                break

        return column, value

    # If we're here, we're the minimizing player
    value = float('Inf')
    column = random.choice(valid_locations)

    for col in valid_locations:
        row = get_next_open_row(board, col)
        temp_board = board.copy()
        drop_piece(temp_board, col, row, HUMAN)
        new_score = minimax(temp_board, depth - 1, alpha, beta, True)[1]

        if new_score < value:
                value = new_score
                column = col

        beta = min(beta, value)

        if alpha >= beta:
            break

    return column, value

def get_valid_locations(board):
    valid_locations = []

    for col in range(COL_COUNT):
        if is_valid_location(board, col):
            valid_locations.append(col)

    return valid_locations


if __name__ == '__main__':
    display_welcome()

    # Initialize the game
    board = create_board()
    turn_count = 0
    turn_count_mod = random.randint(0, 1) # randomize who gets to play first
    is_game_over = False

    # Game loop
    while not is_game_over:
        display_board(board)

        # Ask for human player input if it's an even turn count
        if turn_count % 2 == turn_count_mod:
            player = HUMAN

            # Ask the player which column she wants to play
            column_played = get_player_column(player, board)
        else:
            # Let the AI decide on a move
            player = AI
            print('AI thinking...\n')
            column_played = minimax(board, 6, float('-Inf'),
                                    float('Inf'), True)[0]

        # Drop the piece in the appropriate location
        row = get_next_open_row(board, column_played)
        drop_piece(board, column_played, row, player)

        # Check for victory
        if is_winning_move(board, player):
            display_board(board)

            if player == HUMAN:
                win_message = 'YOU WIN! You beat the AI. Congratulations!'
            else:
                 win_message = 'The AI is victorious. Long live the machines!'

            print(win_message, '\n')
            is_game_over = True

        turn_count += 1
