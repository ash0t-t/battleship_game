import random
import os
import csv
from src.utils import in_bounds, neighbors8, index_to_coord

SHIP_SIZES = [4,3,3,2,2,2,1,1,1,1]


def try_place_all():
    occupied = set()
    forbidden = set()
    ships = []
    for size in SHIP_SIZES:
        placed = False
        attempts = 0
        while not placed and attempts < 500:
            attempts += 1
            orientation = random.choice(['H','V'])
            if orientation == 'H':
                r = random.randrange(0,10)
                c = random.randrange(0, 11-size)
                cells = [(r, c+i) for i in range(size)]
            else:
                r = random.randrange(0, 11-size)
                c = random.randrange(0,10)
                cells = [(r+i, c) for i in range(size)]
            bad = False
            for cell in cells:
                if cell in forbidden or cell in occupied:
                    bad = True
                    break
            if bad:
                continue
            ships.append(cells)
            for cell in cells:
                occupied.add(cell)
                forbidden.add(cell)
                for n in neighbors8(cell[0], cell[1]):
                    forbidden.add(n)
            placed = True
        if not placed:
            return None
    return ships


def ensure_bot_ships():
    os.makedirs('data', exist_ok=True)
    path = os.path.join('data','bot_ships.csv')
    if os.path.exists(path):
        return
    while True:
        ships = try_place_all()
        if ships is not None:
            break
    with open(path,'w',newline='') as f:
        w = csv.writer(f)
        w.writerow(['ship_id','size','cells'])
        sid = 1
        for ship in ships:
            cells_str = ';'.join(index_to_coord(r,c) for r,c in ship)
            w.writerow([sid,len(ship),cells_str])
            sid += 1