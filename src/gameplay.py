import csv
import os
import random
from src.utils import coord_to_index, index_to_coord, neighbors8, neighbors4, flatten_board, board_from_flat, in_bounds


def read_ships(path):
    ships = []
    with open(path,'r',newline='') as f:
        r = csv.DictReader(f)
        for row in r:
            cells = [coord_to_index(p) for p in row['cells'].split(';')]
            ships.append({'id':int(row['ship_id']),'size':int(row['size']),'cells':cells,'hits':set()})
    return ships


def apply_shot(ships, board, target):
    r,c = target
    for ship in ships:
        if (r,c) in ship['cells']:
            ship['hits'].add((r,c))
            board[r][c] = 'H'
            sunk = len(ship['hits']) == len(ship['cells'])
            return True, sunk, ship
    board[r][c] = 'M'
    return False, False, None


def mark_surrounding_miss(board, ship):
    for cell in ship['cells']:
        for n in neighbors8(cell[0], cell[1]):
            if board[n[0]][n[1]] == '.':
                board[n[0]][n[1]] = 'M'


def render(board, show_ships=False, ships=None):
    header = '   ' + ' '.join(str(i+1).rjust(2) for i in range(10))
    lines = [header]
    for i in range(10):
        row = []
        for j in range(10):
            ch = board[i][j]
            if show_ships and ch == '.' and ships is not None:
                for ship in ships:
                    if (i,j) in ship['cells']:
                        ch = 'S'
                        break
            row.append(ch.rjust(2))
        lines.append(f"{chr(ord('A')+i)} " + ' '.join(row))
    return '\n'.join(lines)


def board_init():
    return [['.' for _ in range(10)] for _ in range(10)]


def flat_board_str(board):
    return flatten_board(board)


class BotAI:
    def __init__(self):
        self.tried = set()
        self.mode = 'random'
        self.target_hits = []
        self.candidates = []

    def pick(self, player_board, player_ships):
        if self.mode == 'random':
            choices = [(r,c) for r in range(10) for c in range(10) if (r,c) not in self.tried and player_board[r][c] == '.']
            choice = random.choice(choices)
            return choice
        else:
            while self.candidates:
                cand = self.candidates.pop(0)
                if cand in self.tried or player_board[cand[0]][cand[1]] != '.':
                    continue
                return cand
            choices = [(r,c) for r in range(10) for c in range(10) if (r,c) not in self.tried and player_board[r][c] == '.']
            return random.choice(choices)

    def feedback(self, coord, hit, sunk, ship_size):
        self.tried.add(coord)
        if hit and not sunk and ship_size > 1:
            if self.mode == 'random':
                self.mode = 'targeting'
                self.target_hits = [coord]
                self.candidates = []
                for n in neighbors4(coord[0],coord[1]):
                    if n not in self.tried:
                        self.candidates.append(n)
                random.shuffle(self.candidates)
            else:
                self.target_hits.append(coord)
                if len(self.target_hits) >= 2:
                    a = self.target_hits[0]
                    b = self.target_hits[1]
                    if a[0] == b[0]:
                        r = a[0]
                        minc = min(p[1] for p in self.target_hits)-1
                        maxc = max(p[1] for p in self.target_hits)+1
                        self.candidates = []
                        if minc >= 0:
                            self.candidates.append((r,minc))
                        if maxc < 10:
                            self.candidates.append((r,maxc))
                    else:
                        c = a[1]
                        minr = min(p[0] for p in self.target_hits)-1
                        maxr = max(p[0] for p in self.target_hits)+1
                        self.candidates = []
                        if minr >= 0:
                            self.candidates.append((minr,c))
                        if maxr < 10:
                            self.candidates.append((maxr,c))
        if sunk:
            self.mode = 'random'
            self.target_hits = []
            self.candidates = []


class Game:
    def __init__(self):
        self.player_ships = read_ships(os.path.join('data','player_ships.csv'))
        self.bot_ships = read_ships(os.path.join('data','bot_ships.csv'))
        self.player_board = board_init()
        self.bot_board = board_init()
        self.turn = 1
        self.bot_ai = BotAI()
        self.game_state_path = os.path.join('data','game_state.csv')
        if not os.path.exists(self.game_state_path):
            with open(self.game_state_path,'w',newline='') as f:
                w = csv.writer(f)
                w.writerow(['turn','player_move','bot_move','player_board','bot_board'])

    def all_sunk(self, ships):
        for s in ships:
            if len(s['hits']) != len(s['cells']):
                return False
        return True

    def player_attack(self, coord):
        r,c = coord
        if self.bot_board[r][c] != '.':
            return False, 'Already'
        hit, sunk, ship = apply_shot(self.bot_ships, self.bot_board, coord)
        if sunk:
            mark_surrounding_miss(self.bot_board, ship)
        return True, (hit, sunk, ship)

    def bot_attack(self):
        coord = self.bot_ai.pick(self.player_board, self.player_ships)
        hit, sunk, ship = apply_shot(self.player_ships, self.player_board, coord)
        if sunk:
            mark_surrounding_miss(self.player_board, ship)
        ship_size = ship['size'] if ship is not None else 0
        self.bot_ai.feedback(coord, hit, sunk, ship_size)
        return coord, hit, sunk, ship

    def save_turn(self, player_move_str, bot_move_str):
        with open(self.game_state_path,'a',newline='') as f:
            w = csv.writer(f)
            w.writerow([self.turn, player_move_str, bot_move_str, flat_board_str(self.player_board), flat_board_str(self.bot_board)])

    def run(self):
        while True:
            print('\n' + '='*20 + f' TURN {self.turn} ' + '='*20)
            print('Player board:')
            print(render(self.player_board, show_ships=True, ships=self.player_ships))
            print('\nBot board (known):')
            print(render(self.bot_board, show_ships=False))
            while True:
                print('Enter your attack (e.g., A1):')
                s = input().strip().upper()
                try:
                    r,c = coord_to_index(s)
                except Exception:
                    print('Bad input')
                    continue
                if not in_bounds(r,c):
                    print('Out of bounds')
                    continue
                if self.bot_board[r][c] != '.':
                    print('Cell already targeted')
                    continue
                ok, res = self.player_attack((r,c))
                if not ok:
                    print('Bad move')
                    continue
                hit, sunk, ship = res
                break
            pm = f"{s}({'HIT' if hit else 'MISS'})"
            if sunk:
                print('You sunk a ship!')
            if self.all_sunk(self.bot_ships):
                print('You win!')
                self.save_turn(pm, '')
                break
            coord, bhit, bsunk, bship = self.bot_attack()
            bcoord = index_to_coord(coord[0], coord[1])
            bm = f"{bcoord}({'HIT' if bhit else 'MISS'})"
            print(f'Bot attacked {bcoord} -> {"HIT" if bhit else "MISS"}')
            if bsunk:
                print('Bot sunk one of your ships!')
            self.save_turn(pm, bm)
            if self.all_sunk(self.player_ships):
                print('Bot wins!')
                break
            self.turn += 1