import pygame
import heapq
import sys
import random

CELL_SIZE = 40
GRID_WIDTH = 20
GRID_HEIGHT = 15
WIDTH = GRID_WIDTH * CELL_SIZE
HEIGHT = GRID_HEIGHT * CELL_SIZE
INFO_HEIGHT = 30
SCREEN_HEIGHT = HEIGHT + INFO_HEIGHT
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
GRAY = (200, 200, 200)
LIGHT_GRAY = (220, 220, 220)

EMPTY = 0
OBSTACLE = 1
START = 2
GOAL = 3

def heuristic(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

def get_neighbors(pos, grid):
    r, c = pos
    neighbors = []
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if 0 <= nr < GRID_HEIGHT and 0 <= nc < GRID_WIDTH:
                # Nếu là bước chéo (dr và dc đều khác 0)
                if dr != 0 and dc != 0:
                    # Kiểm tra hai ô kề cạnh (dr,0) và (0,dc) không được là vật cản
                    if grid[r + dr][c] == OBSTACLE or grid[r][c + dc] == OBSTACLE:
                        continue
                neighbors.append((nr, nc))
    return neighbors

def reconstruct_path(parent, start, goal):
    path = []
    cur = goal
    while cur != start:
        path.append(cur)
        cur = parent.get(cur)
        if cur is None:
            return []
    path.append(start)
    path.reverse()
    return path

def greedy_step(open_heap, closed_set, parent, grid, goal):
    if not open_heap:
        return "fail"
    _, current = heapq.heappop(open_heap)
    if current == goal:
        return "found"
    closed_set.add(current)
    for nb in get_neighbors(current, grid):
        r, c = nb
        if grid[r][c] != OBSTACLE and nb not in closed_set:
            already = any(nb == item[1] for item in open_heap)
            if not already:
                parent[nb] = current
                heapq.heappush(open_heap, (heuristic(nb, goal), nb))
    return "continue"

def draw_grid(screen, grid, start, goal, open_set, closed_set, path):
    for row in range(GRID_HEIGHT):
        for col in range(GRID_WIDTH):
            x = col * CELL_SIZE
            y = row * CELL_SIZE + INFO_HEIGHT
            rect = (x, y, CELL_SIZE, CELL_SIZE)
            color = WHITE
            val = grid[row][col]
            if val == OBSTACLE:
                color = BLACK
            elif (row, col) == start:
                color = GREEN
            elif (row, col) == goal:
                color = RED
            elif path and (row, col) in path:
                color = PURPLE
            elif (row, col) in closed_set:
                color = BLUE
            elif (row, col) in open_set:
                color = YELLOW
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, GRAY, rect, 1)

def draw_info_panel(screen):
    panel_rect = (0, 0, WIDTH, INFO_HEIGHT)
    pygame.draw.rect(screen, LIGHT_GRAY, panel_rect)
    pygame.draw.line(screen, BLACK, (0, INFO_HEIGHT), (WIDTH, INFO_HEIGHT), 2)
    font = pygame.font.SysFont("Arial", 16)
    instr = font.render("S:Start G:Goal O:Obs R:Reset M:Random SPACE:Step Q:Quit (Greedy 8-dir no corner cut)", True, BLACK)
    screen.blit(instr, (10, (INFO_HEIGHT - font.get_height()) // 2))

def random_map(grid, start, goal):
    for r in range(GRID_HEIGHT):
        for c in range(GRID_WIDTH):
            if (r,c) == start or (r,c) == goal:
                continue
            if random.random() < 0.3:
                grid[r][c] = OBSTACLE
            else:
                grid[r][c] = EMPTY
    if start:
        grid[start[0]][start[1]] = START
    if goal:
        grid[goal[0]][goal[1]] = GOAL

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Greedy Best First Search - 8 dir, no corner cut")
    clock = pygame.time.Clock()

    grid = [[EMPTY for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    start = None
    goal = None
    mode = "start"

    open_heap = []
    closed_set = set()
    parent = {}
    path = []
    search_active = False
    finished = False

    drawing = False
    erasing = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_r:
                    grid = [[EMPTY for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
                    start = None
                    goal = None
                    mode = "start"
                    open_heap.clear()
                    closed_set.clear()
                    parent.clear()
                    path.clear()
                    search_active = False
                    finished = False
                elif event.key == pygame.K_s:
                    mode = "start"
                elif event.key == pygame.K_g:
                    mode = "goal"
                elif event.key == pygame.K_o:
                    mode = "obstacle"
                elif event.key == pygame.K_m:
                    if start and goal:
                        random_map(grid, start, goal)
                        open_heap.clear()
                        closed_set.clear()
                        parent.clear()
                        path.clear()
                        search_active = False
                        finished = False
                elif event.key == pygame.K_SPACE:
                    if start is None or goal is None:
                        continue
                    if not search_active or finished:
                        open_heap.clear()
                        closed_set.clear()
                        parent.clear()
                        heapq.heappush(open_heap, (heuristic(start, goal), start))
                        search_active = True
                        finished = False
                        path.clear()
                    if search_active and not finished:
                        res = greedy_step(open_heap, closed_set, parent, grid, goal)
                        if res == "found":
                            finished = True
                            search_active = False
                            path = reconstruct_path(parent, start, goal)
                        elif res == "fail":
                            finished = True
                            search_active = False
                            path.clear()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if search_active:
                    continue
                x, y = event.pos
                if y < INFO_HEIGHT:
                    continue
                col = x // CELL_SIZE
                row = (y - INFO_HEIGHT) // CELL_SIZE
                if 0 <= row < GRID_HEIGHT and 0 <= col < GRID_WIDTH:
                    if event.button == 1:
                        drawing = True
                    elif event.button == 3:
                        erasing = True
                    if mode == "obstacle":
                        if event.button == 1:
                            if grid[row][col] != OBSTACLE and (row,col) != start and (row,col) != goal:
                                grid[row][col] = OBSTACLE
                        elif event.button == 3:
                            if grid[row][col] == OBSTACLE:
                                grid[row][col] = EMPTY
                    else:
                        if mode == "start":
                            if start:
                                grid[start[0]][start[1]] = EMPTY
                            start = (row, col)
                            grid[row][col] = START
                        elif mode == "goal":
                            if goal:
                                grid[goal[0]][goal[1]] = EMPTY
                            goal = (row, col)
                            grid[row][col] = GOAL
                        open_heap.clear()
                        closed_set.clear()
                        parent.clear()
                        path.clear()
                        search_active = False
                        finished = False
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    drawing = False
                elif event.button == 3:
                    erasing = False
            elif event.type == pygame.MOUSEMOTION:
                if (drawing or erasing) and mode == "obstacle":
                    x, y = event.pos
                    if y < INFO_HEIGHT:
                        continue
                    col = x // CELL_SIZE
                    row = (y - INFO_HEIGHT) // CELL_SIZE
                    if 0 <= row < GRID_HEIGHT and 0 <= col < GRID_WIDTH:
                        if drawing and grid[row][col] != OBSTACLE and (row,col) != start and (row,col) != goal:
                            grid[row][col] = OBSTACLE
                        elif erasing and grid[row][col] == OBSTACLE:
                            grid[row][col] = EMPTY
                        open_heap.clear()
                        closed_set.clear()
                        parent.clear()
                        path.clear()
                        search_active = False
                        finished = False

        open_positions = {pos for _, pos in open_heap}
        draw_grid(screen, grid, start, goal, open_positions, closed_set, path)
        draw_info_panel(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
