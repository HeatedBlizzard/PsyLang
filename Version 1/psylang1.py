import pygame, sys, re

GRID_SIZE = 16
CELL_SIZE = 32
WINDOW_SIZE = GRID_SIZE * CELL_SIZE
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
FONT_SIZE = 16

pygame.init()
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("PsyLang")
font = pygame.font.SysFont("Arial", FONT_SIZE)

#Memory Grid and Pointer
grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
pointer_x = 0
pointer_y = 0
show_values = False
keybindings = {}

def draw_grid():
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            val = grid[y][x]
            color = WHITE if val > 0 else BLACK
            pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            if show_values:
                text = font.render(str(val), True, GRAY)
                screen.blit(text, (x * CELL_SIZE + 4, y * CELL_SIZE + 4))

def execute(code):
    global pointer_x, pointer_y
    for char in code:
        if char == '>':
            pointer_x = (pointer_x + 1) % GRID_SIZE
        elif char == '<':
            pointer_x = (pointer_x - 1) % GRID_SIZE
        elif char == '+':
            grid[pointer_y][pointer_x] += 1
        elif char == '-':
            grid[pointer_y][pointer_x] = max(0, grid[pointer_y][pointer_x] - 1)
        elif char == ',':
            pointer_y = (pointer_y - 1) % GRID_SIZE
        elif char == '.':
            pointer_y = (pointer_y + 1) % GRID_SIZE

def parse_source(filename):
    global show_values
    with open(filename, 'r') as f:
        source = f.read()

    if 'showVal()' in source:
        show_values = True

    #Parse keybindings
    matches = re.findall(r'(\w)\[(.*?)\]', source)
    for key, code in matches:
        keybindings[key.upper()] = code

    #Execute global (non-bound) code
    stripped = re.sub(r'\w\[.*?\]', '', source)
    execute(stripped.replace('showVal()', '').strip())

def main():
    global pointer_x, pointer_y

    if len(sys.argv) < 2:
        print("Usage: python psylang.py program.psy")
        return

    parse_source(sys.argv[1])

    clock = pygame.time.Clock()
    running = True

    while running:
        screen.fill((0, 0, 0))
        draw_grid()
        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                key = pygame.key.name(event.key).upper()
                if key in keybindings:
                    execute(keybindings[key])

    pygame.quit()

if __name__ == "__main__":
    main()
