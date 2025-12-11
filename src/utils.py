from typing import Tuple, List, Set

ROWS = [chr(ord('A') + i) for i in range(10)]
COLS = [str(i + 1) for i in range(10)]


def coord_to_index(coord: str) -> Tuple[int, int]:
    coord = coord.strip().upper()
    if len(coord) < 2:
        raise ValueError('bad')
    row = coord[0]
    col = coord[1:]
    r = ord(row) - ord('A')
    c = int(col) - 1
    return r, c


def index_to_coord(r: int, c: int) -> str:
    return f"{chr(ord('A')+r)}{c+1}"


def in_bounds(r: int, c: int) -> bool:
    return 0 <= r < 10 and 0 <= c < 10


def neighbors8(r: int, c: int) -> List[Tuple[int, int]]:
    res = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr = r + dr
            nc = c + dc
            if in_bounds(nr, nc):
                res.append((nr, nc))
    return res


def neighbors4(r: int, c: int) -> List[Tuple[int, int]]:
    res = []
    for dr, dc in ((-1,0),(1,0),(0,-1),(0,1)):
        nr = r+dr
        nc = c+dc
        if in_bounds(nr, nc):
            res.append((nr, nc))
    return res


def flatten_board(board: List[List[str]]) -> str:
    return ''.join(''.join(row) for row in board)


def board_from_flat(s: str) -> List[List[str]]:
    return [list(s[i*10:(i+1)*10]) for i in range(10)]