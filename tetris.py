import pygame
import random
import sys

COLS = 8
ROWS = 16
CELL_SIZE = 40

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
current_block = {'x': 0, 'y': 0, 'color': (0, 0, 0)}

fall_timer = 0          # Таймер падения (в миллисекундах)
base_fall_speed = 600   # Базовая скорость (мс между падениями)
current_fall_speed = base_fall_speed
game_over = False
score = 0


def spawn_new_block():
    """Создает новый одиночный квадратик в верхней части поля."""
    global current_block, game_over
    current_block['x'] = random.randint(0, COLS - 1)
    current_block['y'] = 0
    current_block['color'] = random.choice(BLOCK_COLORS)
    
    # Проверка на Game Over (если верхняя клетка уже занята)
    if grid[current_block['y']][current_block['x']] != 0:
        game_over = True


def check_collision(x, y):
    """Проверяет, можно ли переместить блок в координаты (x, y) СТОЛКНОВЕНИЕ."""
    if x < 0 or x >= COLS or y >= ROWS:
        return True
    if y >= 0 and grid[y][x] != 0: # квадратик хотел попасть туда, где в этой клетке уже есть квадратик
        return True
    return False # столкновения нет


def lock_block(): # закрепляет квадратик
    """Закрепляет блок на сетке, проверяет и очищает заполненные линии."""
    global score
    x, y, color = current_block['x'], current_block['y'], current_block['color']
    
    if y >= 0:
        grid[y][x] = color
        
    # Проверка заполненных линий
    lines_cleared = 0
    for r in range(ROWS - 1, -1, -1): # от 15-го ряда до )-го включительно с обратным шагом 
        if all(cell != 0 for cell in grid[r]):
            # Удаляем заполненную строку
            grid.pop(r)
            # Добавляем пустую строку сверху
            grid.insert(0, [0 for _ in range(COLS)])
            lines_cleared += 1
            
    if lines_cleared > 0:
        score += lines_cleared * 100


def draw_block(x, y, color, is_current=False):
    """Рисует один квадратик"""
    rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, color, rect)

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
    spawn_new_block()


# --- ГЛАВНЫЙ ЦИКЛ ---
spawn_new_block()
running = True

while running:
    dt = clock.tick(FPS)

    # 1. Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reset_game()
                
            if not game_over:
                if event.key == pygame.K_LEFT:
                    if not check_collision(current_block['x'] - 1, current_block['y']):
                        current_block['x'] -= 1
                elif event.key == pygame.K_RIGHT:
                    if not check_collision(current_block['x'] + 1, current_block['y']):
                        current_block['x'] += 1
                elif event.key == pygame.K_DOWN:
                    # Мгновенное падение на 1 клетку при нажатии
                    if not check_collision(current_block['x'], current_block['y'] + 1):
                        current_block['y'] += 1
                        fall_timer = 0  # Сброс таймера
                            
                # Изменение базовой скорости (Таймер)
                elif event.key in (pygame.K_EQUALS, pygame.K_PLUS): # Клавиши '+' и '='
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
            # Пытаемся сдвинуть блок вниз
            if not check_collision(current_block['x'], current_block['y'] + 1):
                current_block['y'] += 1
            else:
            # Если не можем - закрепляем и создаем новый
                lock_block()
                spawn_new_block()

    # 3. Отрисовка
    screen.fill(BG_COLOR)
    
    # Рисуем игровое поле
    draw_grid()
    
    # Рисуем закрепленные блоки
    for y in range(ROWS):
        for x in range(COLS):
            if grid[y][x] != 0:
                draw_block(x, y, grid[y][x])
                
    # Рисуем текущий падающий блок
    if not game_over:
        draw_block(current_block['x'], current_block['y'], current_block['color'], is_current=True)
        
    # Разделитель и UI
    pygame.draw.line(screen, GRAY, (FIELD_WIDTH, 0), (FIELD_WIDTH, SCREEN_HEIGHT), 2)
    draw_ui()
    
    pygame.display.flip() 

pygame.quit()
sys.exit()
