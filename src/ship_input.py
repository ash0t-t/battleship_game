import os
import csv
from src.utils import coord_to_index, in_bounds, neighbors8, index_to_coord

SHIP_SIZES = [4,3,3,2,2,2,1,1,1,1]


def parse_coords(s: str):
    parts = s.strip().upper().split()
    res = []
    for p in parts:
        r,c = coord_to_index(p)
        res.append((r,c))
    return res


def is_contiguous_and_straight(cells):
    if len(cells) == 1:
        return True
    rows = [r for r,c in cells]
    cols = [c for r,c in cells]
    if all(r == rows[0] for r in rows):
        cols_sorted = sorted(cols)
        for i in range(1,len(cols_sorted)):
            if cols_sorted[i] != cols_sorted[i-1]+1:
                return False
        return True
    if all(c == cols[0] for c in cols):
        rows_sorted = sorted(rows)
        for i in range(1,len(rows_sorted)):
            if rows_sorted[i] != rows_sorted[i-1]+1:
                return False
        return True
    return False


def cells_touching_any(cells, other_ships):
    forbidden = set()
    for ship in other_ships:
        for r,c in ship:
            forbidden.add((r,c))
            for n in neighbors8(r,c):
                forbidden.add(n)
    for cell in cells:
        if cell in forbidden:
            return True
    return False


def ensure_player_ships():
    os.makedirs('data', exist_ok=True)
    path = os.path.join('data','player_ships.csv')
    if os.path.exists(path):
        return
    ships = []
    ship_id = 1
    for size in SHIP_SIZES:
        while True:
            print(f'Enter cells for ship size {size} (example: A1 A2 ...):')
            s = input().strip()
            try:
                cells = parse_coords(s)
            except Exception:
                print('Bad coordinates format')
                continue
            if len(cells) != size:
                print('Wrong number of cells')
                continue
            ok = True
            for r,c in cells:
                if not in_bounds(r,c):
                    ok = False
                    break
            if not ok:
                print('Cell out of bounds')
                continue
            if len(set(cells)) != len(cells):
                print('Duplicate cells')
                continue
            if not is_contiguous_and_straight(cells):
                print('Cells must form a straight contiguous line')
                continue
            if cells_touching_any(cells, ships):
                print('Ships cannot touch existing ships')
                continue
            ships.append(cells)
            ship_id += 1
            break
    with open(path,'w',newline='') as f:
        w = csv.writer(f)
        w.writerow(['ship_id','size','cells'])
        sid = 1
        for ship in ships:
            cells_str = ';'.join(index_to_coord(r,c) for r,c in ship)
            w.writerow([sid,len(ship),cells_str])
            sid += 1