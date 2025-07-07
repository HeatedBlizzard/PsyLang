### Config ###
GRID_SIZE   = 16
CELL_SIZE   = 32
WIN_SIZE    = GRID_SIZE * CELL_SIZE
FPS         = 30

### Colour IDs 0‑8 ###
COLOURS = [
    (0,   0,   0),     # 0 Black
    (255, 255, 255),   # 1 White
    (255, 0,   0),     # 2 Red
    (255, 128, 0),     # 3 Orange
    (255, 255, 0),     # 4 Yellow
    (0,   255, 0),     # 5 Green
    (0,   128, 255),   # 6 Blue
    (128, 0,   255),   # 7 Purple
    (255, 0,   255)    # 8 Pink
]

### Cell object ###
class Cell:
    __slots__ = ("val", "alpha")
    def __init__(self):
        self.val   = 0       # colour 0‑8
        self.alpha = 256     # opacity 0‑256

### Helpers ###
def clamp_colour(v:int)->int:
    return 0 if v < 0 else 8 if v > 8 else v

def clamp_alpha(a:int)->int:
    return 0 if a < 0 else 256 if a > 256 else a

### Grid & state ###
grid = [[Cell() for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
pointer_x = 0
pointer_y = 0
show_values = False
show_cell_border = False
keybindings = {}

### Scheduled tasks for $ ###
class Task:
    __slots__ = ("interval","code","next_time")
    def __init__(self, interval:float, code:str):
        self.interval  = interval
        self.code      = code
        self.next_time = time.time() + interval

tasks = []       # list[Task]

### Pygame init ###
pygame.init()
screen = pygame.display.set_mode((WIN_SIZE, WIN_SIZE))
pygame.display.set_caption("PsyLang Interpreter v3")
font = pygame.font.SysFont("Consolas", 14)

def draw_grid():
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            c = grid[y][x]
            base = COLOURS[c.val]
            alpha = 255 if c.alpha >= 256 else c.alpha
            surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            surf.fill((*base, alpha))
            screen.blit(surf, (x*CELL_SIZE, y*CELL_SIZE))
            if show_values:
                txt = font.render(str(c.val), True, (128,128,128))
                screen.blit(txt, (x*CELL_SIZE+4, y*CELL_SIZE+4))
            if show_cell_border and x == pointer_x and y == pointer_y:
                pygame.draw.rect(screen, (255,0,0), (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE), 2)

### Utility for nested braces ###
def find_matching_brace(s:str, start:int)->int:
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

### EXECUTE ###
def execute(code:str, start:int=0):
    """Executes code string from index start. 
    Returns new index after finishing (len or position where paused)."""
    global pointer_x, pointer_y
    i = start
    ln = len(code)
    while i < ln:
        ch = code[i]

        # Movement
        if ch == '>':
            pointer_x = (pointer_x + 1) % GRID_SIZE
        elif ch == '<':
            pointer_x = (pointer_x - 1) % GRID_SIZE
        elif ch == ',':
            pointer_y = (pointer_y - 1) % GRID_SIZE
        elif ch == '.':
            pointer_y = (pointer_y + 1) % GRID_SIZE

        # Inc / Dec
        elif ch == '+':
            c = grid[pointer_y][pointer_x]
            c.val = clamp_colour(c.val + 1)
        elif ch == '-':
            c = grid[pointer_y][pointer_x]
            c.val = clamp_colour(c.val - 1)

        # Opacity
        elif ch == 'O' and code.startswith("Op[", i):
            j = code.find(']', i+3)
            if j != -1:
                try:
                    val = int(code[i+3:j])
                except ValueError:
                    val = 0
                grid[pointer_y][pointer_x].alpha = clamp_alpha(val)
                i = j

        # Random %[x/y] -> inline number
        elif ch == '%' and code.startswith("%[", i):
            j = code.find(']', i+2)
            if j != -1 and '/' in code[i+2:j]:
                lo_str, hi_str = code[i+2:j].split('/')
                try:
                    lo, hi = int(lo_str), int(hi_str)
                except ValueError:
                    lo, hi = 0, 0
                rnd = random.randint(lo, hi)
                num_str = str(rnd)
                # Replace the %[x/y] with its numeric string in code
                code = code[:i] + num_str + code[j+1:]
                ln = len(code)
                # don't advance i so that the new digits are processed
                continue   # restart loop with same i

        # Loop n{ ... }
        elif ch.isdigit():
            m = re.match(r'(\d+)\{', code[i:])
            if m:
                n = int(m.group(1))
                block_start = i + len(m.group(0))
                block_end = find_matching_brace(code, block_start)
                if block_end != -1:
                    block = code[block_start:block_end]
                    for _ in range(n):
                        execute(block)
                    i = block_end

        i += 1
    return len(code)

### PARSE SOURCE ###
def parse_source(path:str):
    global show_values, show_cell_border, keybindings, tasks
    with open(path, 'r', encoding='utf-8') as f:
        src = f.read()

    # Special toggles
    show_values = "showVal()" in src
    show_cell_border = "showCell()" in src

    # Parse tasks $[t][code]
    tasks = []
    def task_repl(match):
        interval_s = float(match.group(1))
        code_str   = match.group(2)
        tasks.append(Task(interval_s, code_str))
        return ''  # strip from main script
    src = re.sub(r'\$\[(.*?)\]\[(.*?)\]', task_repl, src, flags=re.DOTALL)

    # Keybindings
    keybindings = {k.upper():v for k,v in re.findall(r'(\w)\[(.*?)\]', src, flags=re.DOTALL)}

    # Remove keybinding blocks and toggles from main script
    stripped = re.sub(r'\w\[.*?\]', '', src, flags=re.DOTALL)
    stripped = stripped.replace("showVal()", "").replace("showCell()", "")
    return stripped

### MAIN ###
def main():
    if len(sys.argv) < 2:
        print("Usage: python psylang.py program.psy")
        sys.exit(0)

    main_code = parse_source(sys.argv[1])
    exec_pos  = 0

    clock = pygame.time.Clock()
    running = True
    while running:
        now = time.time()

        # Pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                k = pygame.key.name(event.key).upper()
                block = keybindings.get(k)
                if block:
                    execute(block)

        # Run scheduled tasks
        for t in tasks:
            if now >= t.next_time:
                execute(t.code)
                t.next_time += t.interval

        # Run main code once (non-looping script)
        if exec_pos < len(main_code):
            exec_pos = execute(main_code, exec_pos)

        # Draw
        screen.fill((0,0,0))
        draw_grid()
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
