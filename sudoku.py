#!/usr/bin/env python3

import os
import random
from time import sleep

blue = "\033[1;34;40m"
green = "\033[1;32;40m"
yellow = "\033[1;33;40m"
red = "\033[1;31;40m"
white = "\033[1;37;40m"


blue_lines = "   " + blue + ("+---" * 9) + '+'
green_lines = "   " + (blue + ("+") + green + "---" + ("+---" * 2)) * 3 + blue + '+'



class Box:

    def __init__(self, value, color):
        self.value = value
        self.color = color

    def __str__(self):
        return "{}{}{}".format(self.color, self.value, green)

    def __retr__(self):
        return "{}{}{}".format(self.color, self.value, green)
    
    def __eq__(self, other):
        return self.value == other.value


def check_row(value, row, lst):
    return value in lst[row]


def check_column(value, col, lst):
    for row in lst:
        if row[col] == value:
            return True
    return False

def ramp(value):
    if value < 3:
        return 0
    if value < 6:
        return 1
    return 2

def check_block(value, block, lst):
    for x in range(3):
        for y in range(3):
            if value == lst[x + (3 * ramp(block))][y + 3 * (block % 3)]:
                return True
    return False

def blockify(lst):
    ret = []
    for z in range(9):
        block = []
        for x in range(3):
            for y in range(3):
                block.append(lst[x + (3 * ramp(z))][y + 3 * (z % 3)])
        ret.append(block)
    return ret



def translate(x, y):
    return ramp(x) + 3 * ramp(y)


def check_valid(value, x, y, lst):
    if check_column(value, x, lst):
        return False
    if check_row(value, y, lst):
        return False
    if check_block(value, translate(x, y), lst):
        return False
    return True


def get_row(row, lst):
    ret = ''
    for x in range(len(lst)):
        if x % 3 == 0:
            ret += '{}|{} {} '.format(blue, green, str(lst[row][x]))
        else:
            ret += '| {} '.format(str(lst[row][x]))
    ret += blue + '|' + green
    return ret


def shift(lst, n):
    n = n % len(lst)
    return lst[n:] + lst[:n]

def flatten(lst):
    return [val for row in lst for val in row]

def chunky(lst, n):
    return [lst[i * n:(i + 1) * n] for i in range(len(lst) + (n - 1) // n)]

def get_columns(lst):
    cols = []
    for x in range(9):
        col = []
        for y in range(9):
            col.append(lst[y][x])
        cols.append(col)

    cols = chunky(cols, 3)[:3]
    for chunk in cols:
        random.shuffle(chunk)
        random.shuffle(chunk)
        random.shuffle(chunk)
    random.shuffle(cols)
    return flatten(cols)

def shuffle_set(lst):
    rows = chunky(lst, 3)
    for row in rows:
        random.shuffle(row)
        random.shuffle(row)
        random.shuffle(row)
    cols = get_columns(flatten(rows))
    return cols


def generate_random_set():
    lst = [Box(x, white) for x in range(1, 10)]
    random.shuffle(lst)
    ret = [[]] * 9
    ret[0] = lst
    for x in range(8):
        if (x + 1) % 3 == 0 and x != 0:
            ret[x + 1] = shift(ret[x], 1)
        else:
            ret[x + 1] = shift(ret[x], 3)
    return shuffle_set(ret)


def remove_evenly(blocks, init_pass, tot):
    #Removes n numbers from every block, where n is equal to init_pass (initial passes)
    for x in range(init_pass):
        for y in range(9):
            spot = random.randint(0, 8)
            while blocks[y][spot].value == ' ':
                spot = random.randint(0, 8)
            blocks[y][spot] = Box(' ', white)

    while tot > 0:
        x = random.randint(0, 8)
        y = random.randint(0, 8)
        if blocks[x][y].value != ' ':
            blocks[x][y] = Box(' ', white)
            tot -= 1
    return blocks

def pre_process(blocks):
    chunks = []
    for block in blocks:
        chunks.append([block[i:i + 3] for i in range(0, 9, 3)])
    return chunks


def reconstitute(blocks, board):
    chunks = pre_process(blocks)
    rows = []
    for z in range(3):
        for x in range(3):
            row = []
            for y in range(3):
                row.append(chunks[y + (3 * z)][x])
            rows.append(flatten(row))
    for x in range(9):
        for y in range(9):
            board[x][y] = rows[x][y]

def remove_pieces(diff, board):
    blocks = blockify(board)
    if diff == 1:
        blocks = remove_evenly(blocks, 2, 39 - 18) #39 total num blocks removed - 18 (9 * 2) for even removal
        reconstitute(blocks, board)
    elif diff == 2:
        blocks = remove_evenly(blocks, 3, 46 - 27)
        reconstitute(blocks, board)
    elif diff == 3:
        blocks = remove_evenly(blocks, 3, 50 - 27)
        reconstitute(blocks, board)
    elif diff == 4:
        blocks = remove_evenly(blocks, 4, 55 - 36)
        reconstitute(blocks, board)
    elif diff == 5:
        for row in range(9):
            for col in range(9):
                if board[row][col].value != 6 and board[row][col].value != 9:
                    board[row][col] = Box(' ', white)


def make_move(move, board):
    code = x = y = value = None
    if 'g' in move or 'e' in move:
        code = move[0]
        x = int(move[2])
        y = int(move[1])
        if 'g' in move:
            value = int(move[3])
    else:
        x = int(move[1])
        y = int(move[0])
        value = int(move[2])

    if board[x][y].color == white:
            if board[x][y].value != ' ':
                print("Cannot Delete Clues!")
                sleep(2)
                return 0
    if code == 'g':
        board[x][y] = Box(value, yellow)
        return 0
    
    elif code == 'e':
        ret = -1
        if board[x][y].color == yellow:
            ret = 0
        board[x][y] = Box(' ', white)
        return ret
    else:
        if not check_valid(Box(value, green), y, x, board) and board[x][y].color != yellow:
            board[x][y] = Box(value, red)
            return 0
        else:
            board[x][y] = Box(value, green)
            return 1



def play_game():
    board = generate_random_set()
    name = input("What Is Your Name? ")
    valid = False
    while not valid:
        try:
            difficulty = int(input("Hello {} What Difficulty Level Would You Like To Play At? \n\n1.\tEASY\n2.\tMEDIUM\n3.\tHARD\n4.\tEXPERT\n5.\tSEXPERT\n (Please Select A Number)\n".format(name)))
            if difficulty < 1 or difficulty > 5:
                print("Please Enter a Number [1, 5]\n\n")
            else:
                valid = True
        except:
            print("You May Only Enter a Number [1, 5]\n\n")
    moves = [39, 46, 50, 55, 69]
    print_board(board) 
    remove_pieces(difficulty, board) 
    game_over = False
    moves = moves[difficulty - 1]
    while not game_over:
        print_board(board)
        move = input("\nMove: ").split(" ")
        if len(move) != 0 and len(move) <= 4:
            moves += make_move(move, board)
        game_over = moves == 64

def print_board(lst):
    os.system("clear")
    print("Regular Move - X Y Number")
    print("Erase Spot - e X Y")
    print("Guess Spot - g X Y Number\n")
    top = green + "   "
    for x in range(9):
        top += "  {} ".format(x)
    print(top)
    for x in range(len(lst)):
        if x % 3 == 0:
            print(blue_lines)
        else:
            print(green_lines)
        print("{}{}  {}".format(green, x, get_row(x, lst)))
    print(blue_lines + green)


play_game()
