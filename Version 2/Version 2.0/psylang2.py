import pygame, sys, re, random, time

GRID_SIZE   = 16
CELL_SIZE   = 32
WIN_SIZE    = GRID_SIZE * CELL_SIZE
FPS         = 30

COLOURS = [
    (0,   0,   0),
    (255, 255, 255),
    (255, 0,   0),
    (255, 128, 0),
    (255, 255, 0),
    (0,   255, 0),
    (0,   128, 255),
    (128, 0,   255),
    (255, 0,   255)
]

class Cell:
    __slots__ = ("val", "alpha")
    def __init__(self):
        self.val   = 0
        self.alpha = 256

def clamp_colour(v):
    return 0 if v < 0 else 8 if v > 8 else v

def clamp_alpha(a):
    return 0 if a < 0 else 256 if a > 256 else a

grid = [[Cell() for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
pointer_x = 0
pointer_y = 0
show_values = False
show_cell_border = False
keybindings = {}

pygame.init()
screen = pygame.display.set_mode((WIN_SIZE, WIN_SIZE))
pygame.display.set_caption("PsyLang Interpreter v2")
font = pygame.font.SysFont("Consolas", 14)

def draw_grid():
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            cell = grid[y][x]
            base  = COLOURS[cell.val]
            alpha = 255 if cell.alpha >= 256 else cell.alpha
            surf  = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            surf.fill((*base, alpha))
            screen.blit(surf, (x*CELL_SIZE, y*CELL_SIZE))
            if show_values:
                txt = font.render(str(cell.val), True, (128,128,128))
                screen.blit(txt, (x*CELL_SIZE+4, y*CELL_SIZE+4))
            if show_cell_border and x == pointer_x and y == pointer_y:
                pygame.draw.rect(screen, (255, 0, 0), (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE), 2)

def find_matching_brace(s, start):
    depth = 1
    i = start
    while i < len(s):
        if s[i] == '{':
            depth += 1
        elif s[i] == '}':
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1

def execute(code, start=0):
    global pointer_x, pointer_y
    i = start
    ln = len(code)
    while i < ln:
        ch = code[i]

        if ch == '>':
            pointer_x = (pointer_x + 1) % GRID_SIZE
        elif ch == '<':
            pointer_x = (pointer_x - 1) % GRID_SIZE
        elif ch == ',':
            pointer_y = (pointer_y - 1) % GRID_SIZE
        elif ch == '.':
            pointer_y = (pointer_y + 1) % GRID_SIZE
        elif ch == '+':
            c = grid[pointer_y][pointer_x]
            c.val = clamp_colour(c.val + 1)
        elif ch == '-':
            c = grid[pointer_y][pointer_x]
            c.val = clamp_colour(c.val - 1)

        elif ch == 'O' and code.startswith("Op[", i):
            j = code.find(']', i+3)
            if j != -1:
                try:
                    val = int(code[i+3:j])
                except ValueError:
                    val = 0
                grid[pointer_y][pointer_x].alpha = clamp_alpha(val)
                i = j

        elif ch.isdigit():
            num_match = re.match(r'(\d+)\{', code[i:])
            if num_match:
                n = int(num_match.group(1))
                start_block = i + len(num_match.group(0))
                end_block = find_matching_brace(code, start_block)
                if end_block != -1:
                    block = code[start_block:end_block]
                    for _ in range(n):
                        execute(block)
                    i = end_block

        i += 1
    return len(code), 0  # done, no delay

def parse_source(fname):
    global show_values, keybindings, show_cell_border
    with open(fname, 'r', encoding='utf-8') as f:
        src = f.read()

    show_cell_border = "showCell()" in src
    show_values = "showVal()" in src

    keybindings = {}
    for key, block in re.findall(r'(\w)\[(.*?)\]', src, flags=re.DOTALL):
        keybindings[key.upper()] = block

    stripped = re.sub(r'\w\[.*?\]', '', src, flags=re.DOTALL)
    stripped = stripped.replace("showVal()", "")
    stripped = stripped.replace("showCell()", "")
    return stripped

def main():
    if len(sys.argv) < 2:
        print("Usage: python psylang.py <program.psy>")
        sys.exit(0)

    code = parse_source(sys.argv[1])
    exec_pos = 0

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                key_name = pygame.key.name(event.key).upper()
                if key_name in keybindings:
                    execute(keybindings[key_name])

        if exec_pos < len(code):
            exec_pos, _ = execute(code, exec_pos)

        screen.fill((0, 0, 0))
        draw_grid()
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
