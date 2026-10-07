import pygame
import random
import sys

COLS = 10
ROWS = 20
CELL_SIZE = 32

FIELD_WIDTH = COLS * CELL_SIZE
FIELD_HEIGHT = ROWS * CELL_SIZE

UI_WIDTH = 220
SCREEN_WIDTH = FIELD_WIDTH + UI_WIDTH
SCREEN_HEIGHT = FIELD_HEIGHT
FPS = 60   #frames per seconds  кадров в секунду

# 4 цвета для квадратиков
BLOCK_COLORS = [
    (231, 76, 60),   # Красный
    (46, 204, 113),  # Зеленый
    (241, 196, 15),   # синий
    (52, 152, 219),  # Синий
    (240, 136, 213), 
    (166, 210, 222)    
]

# Цвета
BLACK = (20, 20, 20)
WHITE = (255, 255, 255)
GRAY = (125, 125, 125)
GRID_COLOR = (140, 140, 140)
BG_COLOR = (60, 60, 60)

# Фигуры тетриса (координаты относительно центра)
# Каждая фигура - список из 4 кортежей (x, y)
SHAPES = {
    'I': [
        [(0, -1), (0, 0), (0, 1), (0, 2)],  # Вертикальная
        [(-1, 0), (0, 0), (1, 0), (2, 0)]   # Горизонтальная
    ],
    'L': [
        [(0, -1), (0, 0), (0, 1), (1, 1)],  # Поворот 0°
        [(-1, 0), (0, 0), (1, 0), (-1, 1)], # Поворот 90°
        [(-1, -1), (0, -1), (0, 0), (0, 1)],# Поворот 180°
        [(1, -1), (-1, 0), (0, 0), (1, 0)]  # Поворот 270°
    ],
    'T': [
        [(0, -1), (-1, 0), (0, 0), (1, 0)], # Поворот 0°
        [(0, -1), (0, 0), (1, 0), (0, 1)],  # Поворот 90°
        [(-1, 0), (0, 0), (1, 0), (0, 1)],  # Поворот 180°
        [(0, -1), (-1, 0), (0, 0), (0, 1)]  # Поворот 270°
    ]
}

# Цвета для каждой фигуры
SHAPE_COLORS = {
    'I': (46, 204, 113),   # Зеленый
    'L': (231, 76, 60),    # Красный
    'T': (52, 152, 219)    # Синий
}

# --- ИНИЦИАЛИЗАЦИЯ PYGAME ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Мини-Tetris (1x1)")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 20, bold=True)
small_font = pygame.font.SysFont("arial", 16)

# --- СОСТОЯНИЕ ИГРЫ ---
# Сетка 16 строк на 8 колонок. 0 - пусто, иначе - кортеж цвета.
grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]

current_piece = {
    'shape': 'I',
    'rotation': 0,
    'x': 0,
    'y': 0,
    'color': (0, 0, 0)
}


fall_timer = 0          # Таймер падения (в миллисекундах)
base_fall_speed = 600   # Базовая скорость (мс между падениями)
current_fall_speed = base_fall_speed
game_over = False
score = 0


def spawn_new_piece():
    """Создает новую фигуру в середине верхней части поля."""
    global current_piece, game_over
    
    shape_name = random.choice(list(SHAPES.keys()))
    current_piece['shape'] = shape_name
    current_piece['rotation'] = 0
    current_piece['x'] = COLS // 2  # Середина поля
    current_piece['y'] = 2  # Начинаем чуть ниже верха
    current_piece['color'] = random.choice(BLOCK_COLORS)
    
    # Проверка на Game Over
    if check_piece_collision(current_piece['x'], current_piece['y'], current_piece['rotation']):
        game_over = True

def get_piece_cells(x, y, rotation):
    """Возвращает абсолютные координаты всех клеток фигуры."""
    shape_name = current_piece['shape']
    relative_cells = SHAPES[shape_name][rotation]
    return [(x + dx, y + dy) for dx, dy in relative_cells]

def check_piece_collision(x, y, rotation):
    """Проверяет, можно ли разместить фигуру в позиции (x, y) с поворотом rotation."""
    cells = get_piece_cells(x, y, rotation)
    
    for cell_x, cell_y in cells:
        # Проверка границ
        if cell_x < 0 or cell_x >= COLS or cell_y >= ROWS:
            return True
        # Проверка столкновения с другими блоками
        if cell_y >= 0 and grid[cell_y][cell_x] != 0:
            return True
    
    return False


def lock_piece():
    """Закрепляет фигуру на сетке и очищает заполненные линии."""
    global score
    
    cells = get_piece_cells(current_piece['x'], current_piece['y'], current_piece['rotation'])
    
    for cell_x, cell_y in cells:
        if cell_y >= 0:
            grid[cell_y][cell_x] = current_piece['color']
    
    # Проверка и очистка заполненных линий
    lines_cleared = 0
    for r in range(ROWS - 1, -1, -1):
        if all(cell != 0 for cell in grid[r]):
            grid.pop(r)
            grid.insert(0, [0 for _ in range(COLS)])
            lines_cleared += 1
            # Не увеличиваем r, так как строки сдвинулись
    
    # Очки за линии
    if lines_cleared > 0:
        score += lines_cleared * 100


def rotate_piece():
    """Поворачивает фигуру по часовой стрелке."""
    shape_name = current_piece['shape']
    new_rotation = (current_piece['rotation'] + 1) % len(SHAPES[shape_name])
    
    # Проверяем, можно ли повернуть
    if not check_piece_collision(current_piece['x'], current_piece['y'], new_rotation):
        current_piece['rotation'] = new_rotation

def draw_block(x, y, color, is_current=False):
    """Рисует один квадратик с 3D эффектом."""
    rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, color, rect)
    
    # Блик и тень
    highlight = tuple(min(255, c + 40) for c in color)
    shadow = tuple(max(0, c - 40) for c in color)
    
    pygame.draw.line(screen, highlight, rect.topleft, rect.topright, 3)
    pygame.draw.line(screen, highlight, rect.topleft, rect.bottomleft, 3)
    pygame.draw.line(screen, shadow, rect.bottomleft, rect.bottomright, 3)
    pygame.draw.line(screen, shadow, rect.topright, rect.bottomright, 3)
    
    if is_current:
        pygame.draw.rect(screen, WHITE, rect, 2)


def draw_grid():
    """Рисует фоновую сетку."""
    for x in range(COLS):
        for y in range(ROWS):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, GRID_COLOR, rect, 1)


def draw_ui():
    """Рисует боковую панель с информацией и управлением."""
    ui_x = FIELD_WIDTH + 15
    
    # Заголовок
    title = font.render("TETRIS 1x1", True, WHITE)
    screen.blit(title, (ui_x, 20))
    
    # Счет
    score_text = font.render(f"Счет: {score}", True, WHITE)
    screen.blit(score_text, (ui_x, 70))
    
    # Скорость
    speed_text = small_font.render(f"Скорость: {current_fall_speed} мс", True, (200, 200, 200))
    screen.blit(speed_text, (ui_x, 110))
    
    # Статус
    if game_over:
        go_text = font.render("GAME OVER", True, (231, 76, 60))
        screen.blit(go_text, (ui_x, 150))
        restart_text = small_font.render("Нажмите R", True, WHITE)
        screen.blit(restart_text, (ui_x, 180))

    # Управление
    controls = [
        "Управление:",
        "< > : Движение",
        " v  : Ускорить",
        " +  : Быстрее",
        " -  : Медленнее",
        " R  : Рестарт"
    ]
    
    y_offset = 250
    for line in controls:
        text = small_font.render(line, True, (150, 150, 150))
        screen.blit(text, (ui_x, y_offset))
        y_offset += 25


def reset_game():
    """Сбрасывает состояние игры."""
    global grid, score, game_over, current_fall_speed, base_fall_speed, fall_timer
    grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    score = 0
    game_over = False
    current_fall_speed = base_fall_speed
    fall_timer = 0
    spawn_new_piece()


# --- ГЛАВНЫЙ ЦИКЛ ---
spawn_new_piece()
running = True

while running:
    dt = clock.tick(FPS)
    print(str(dt))
    # 1. Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reset_game()
                
            if not game_over:
                if event.key == pygame.K_LEFT:
                    if not check_piece_collision(current_piece['x'] - 1, current_piece['y'], current_piece['rotation']):
                        current_piece['x'] -= 1
                elif event.key == pygame.K_RIGHT:
                    if not check_piece_collision(current_piece['x'] + 1, current_piece['y'], current_piece['rotation']):
                        current_piece['x'] += 1
                elif event.key == pygame.K_DOWN:
                    if not check_piece_collision(current_piece['x'], current_piece['y'] + 1, current_piece['rotation']):
                        current_piece['y'] += 1
                        fall_timer = 0
                elif event.key == pygame.K_UP:
                        rotate_piece()
                elif event.key in (pygame.K_EQUALS, pygame.K_PLUS):
                        current_fall_speed = max(50, current_fall_speed - 50)
                elif event.key == pygame.K_MINUS:
                        current_fall_speed = min(1500, current_fall_speed + 50)


    # 2. Обновление логики (если не пауза и не game over)
    if not game_over:
        fall_timer += dt
        # Проверка удержания клавиши "Вниз" для плавного ускорения
        keys = pygame.key.get_pressed()
        effective_speed = current_fall_speed
        if keys[pygame.K_DOWN]:
            effective_speed = 50  # Очень быстрое падение при удержании

        if fall_timer >= effective_speed:
            fall_timer = 0
            if not check_piece_collision(current_piece['x'], current_piece['y'] + 1, current_piece['rotation']):
                current_piece['y'] += 1
            else:
                lock_piece()
                spawn_new_piece()

    # 3. Отрисовка
    screen.fill(BG_COLOR)
    
    # Рисуем игровое поле
    draw_grid()
    
    # Рисуем закрепленные блоки
    for y in range(ROWS):
        for x in range(COLS):
            if grid[y][x] != 0:
                draw_block(x, y, grid[y][x])
                
    # Рисуем текущую фигуру
    if not game_over:
        cells = get_piece_cells(current_piece['x'], current_piece['y'], current_piece['rotation'])
        for cell_x, cell_y in cells:
            if cell_y >= 0:  # Рисуем только видимые части
                draw_block(cell_x, cell_y, current_piece['color'], is_current=True)

        
    # Разделитель и UI
    pygame.draw.line(screen, GRAY, (FIELD_WIDTH, 0), (FIELD_WIDTH, SCREEN_HEIGHT), 2)
    draw_ui()
    
    pygame.display.flip() 

pygame.quit()
sys.exit()
