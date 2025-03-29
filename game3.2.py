import pygame
import os
import random
import math
import time

# Инициализация Pygame
pygame.init()

# Настройки окна
WIDTH, HEIGHT = 1280, 720
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("World of Tanks Nintendo Switch edition")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CANYON = (139, 69, 19)  # Коричневый цвет для препятствий
DARK_GRAY = (50, 50, 50)  # Темно-серый для Underground_Storage
LIGHT_GRAY = (180, 180, 180)  # Светло-серый для Castle_Lawn
FOUNTAIN_COLOR = (200, 200, 200)  # Цвет фонтана/статуи

# Настройки танка
TANK_WIDTH, TANK_HEIGHT = 40, 40
TANK_SPEED = 2
BULLET_SPEED = 5
BULLET_COOLDOWN = 2000

# Настройки бонусов
BONUS_SIZE = 20
BONUS_TYPES = ["explosive_bullet", "shield", "invulnerability"]

# Настройки препятствий
OBSTACLE_WIDTH, OBSTACLE_HEIGHT = 80, 80

# Загрузка изображений
def load_image(path, width, height):
    if not os.path.exists(path):
        # Если файл не найден, создаем заглушку
        surf = pygame.Surface((width, height))
        surf.fill(RED)
        return surf
    image = pygame.image.load(path)
    image = pygame.transform.scale(image, (width, height))
    return image

# Загрузка изображения танка
def load_tank_image():
    return load_image(os.path.join("Sprites", "tank.png"), TANK_WIDTH, TANK_HEIGHT)

# Загрузка изображений врагов
def load_enemy_images():
    return [load_image(os.path.join("Sprites", f"bot.png"), TANK_WIDTH, TANK_HEIGHT) for i in range(1, 4)]

# Загрузка фонового изображения
def load_background(map_name):
    if map_name == "map1":
        return load_image(os.path.join("Sprites", "Underground_Storage.jpg"), WIDTH, HEIGHT)
    elif map_name == "map2":
        return load_image(os.path.join("Sprites", "Castle_Lawn.jpg"), WIDTH, HEIGHT)
    elif map_name == "map3":
        return load_image(os.path.join("Sprites", "Besieged_City.jpg"), WIDTH, HEIGHT)
    else:
        return load_image(os.path.join("Sprites", "background.jpg"), WIDTH, HEIGHT)

# Функция для ввода имени игрока
def get_player_name():
    pygame.display.set_caption("Введите ваше имя")
    name = ""
    font = pygame.font.SysFont("Arial", 40)
    input_active = True
    
    while input_active:
        WIN.fill(WHITE)
        text_surface = font.render("Введите ваше имя:", True, BLACK)
        name_surface = font.render(name, True, BLACK)
        
        WIN.blit(text_surface, (WIDTH//2 - text_surface.get_width()//2, HEIGHT//2 - 50))
        WIN.blit(name_surface, (WIDTH//2 - name_surface.get_width()//2, HEIGHT//2 + 10))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    name += event.unicode
    
    pygame.display.set_caption("World of Tanks Nintendo Switch edition")
    return name if name else "Игрок"

# Титульный экран
def title_screen():
    run = True
    clock = pygame.time.Clock()

    # Загрузка фона
    background = load_background(None)

    while run:
        clock.tick(60)
        WIN.blit(background, (0, 0))

        # Отрисовка кнопок
        font = pygame.font.SysFont("Arial", 40)
        text = font.render("Выберите карту", True, WHITE)
        WIN.blit(text, (WIDTH // 2 - text.get_width() // 2, 100))

        # Кнопка карты 1
        map1_button = pygame.Rect(WIDTH // 2 - 100, 200, 200, 50)
        pygame.draw.rect(WIN, GREEN, map1_button)
        text = font.render("Подземелье", True, BLACK)
        WIN.blit(text, (WIDTH // 2 - text.get_width() // 2, 210))

        # Кнопка карты 2
        map2_button = pygame.Rect(WIDTH // 2 - 100, 300, 200, 50)
        pygame.draw.rect(WIN, GREEN, map2_button)
        text = font.render("Замок", True, BLACK)
        WIN.blit(text, (WIDTH // 2 - text.get_width() // 2, 310))

        # Кнопка карты 3
        map3_button = pygame.Rect(WIDTH // 2 - 100, 400, 200, 50)
        pygame.draw.rect(WIN, GREEN, map3_button)
        text = font.render("Город", True, BLACK)
        WIN.blit(text, (WIDTH // 2 - text.get_width() // 2, 410))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if map1_button.collidepoint(event.pos):
                    return "map1"
                elif map2_button.collidepoint(event.pos):
                    return "map2"
                elif map3_button.collidepoint(event.pos):
                    return "map3"

        pygame.display.update()

# Класс танка
class Tank:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 15
        self.bullets = 5
        self.last_shot = pygame.time.get_ticks()
        self.shield = False
        self.invulnerable = False
        self.invulnerable_start_time = 0
        self.image = load_tank_image()
        self.direction = "up"  # Направление танка
        self.dx = 0  # Направление по оси X
        self.dy = 0  # Направление по оси Y
        self.rect = pygame.Rect(x, y, TANK_WIDTH, TANK_HEIGHT)

    def draw(self, win):
        # Поворачиваем изображение в зависимости от направления
        if self.direction == "up":
            rotated_image = self.image
        elif self.direction == "down":
            rotated_image = pygame.transform.rotate(self.image, 180)
        elif self.direction == "left":
            rotated_image = pygame.transform.rotate(self.image, 90)
        elif self.direction == "right":
            rotated_image = pygame.transform.rotate(self.image, -90)
        win.blit(rotated_image, (self.x, self.y))

    def move(self, dx, dy, obstacles, tanks):
        # Сохраняем направление движения
        self.dx = dx
        self.dy = dy

        # Проверка границ окна
        new_x = self.x + dx * TANK_SPEED
        new_y = self.y + dy * TANK_SPEED

        # Обновляем rect для проверки столкновений
        new_rect = pygame.Rect(new_x, new_y, TANK_WIDTH, TANK_HEIGHT)

        # Проверка столкновений с препятствиями
        collision = False
        for obstacle in obstacles:
            if new_rect.colliderect(obstacle.rect):
                collision = True
                break

        # Проверка столкновений с другими танками
        for tank in tanks:
            if tank != self and new_rect.colliderect(tank.rect):
                collision = True
                break

        if not collision:
            if 0 <= new_x <= WIDTH - TANK_WIDTH:
                self.x = new_x
            if 0 <= new_y <= HEIGHT - TANK_HEIGHT:
                self.y = new_y
            self.rect.x = self.x
            self.rect.y = self.y

        # Обновляем направление
        if dx > 0:
            self.direction = "right"
        elif dx < 0:
            self.direction = "left"
        if dy > 0:
            self.direction = "down"
        elif dy < 0:
            self.direction = "up"

    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > BULLET_COOLDOWN and self.bullets > 0:
            self.bullets -= 1
            self.last_shot = current_time
            return Bullet(self.x + TANK_WIDTH // 2, self.y + TANK_HEIGHT // 2, self.direction)
        return None

    def recharge(self):
        current_time = pygame.time.get_ticks()
        if self.bullets < 5 and current_time - self.last_shot > BULLET_COOLDOWN:
            self.bullets += 1
            self.last_shot = current_time

    def take_damage(self, damage):
        if not self.invulnerable:
            if self.shield:
                self.shield = False
            else:
                self.hp -= damage

    def activate_shield(self):
        self.shield = True

    def activate_invulnerability(self):
        self.invulnerable = True
        self.invulnerable_start_time = pygame.time.get_ticks()

    def update_invulnerability(self):
        if self.invulnerable and pygame.time.get_ticks() - self.invulnerable_start_time > 10000:
            self.invulnerable = False

    def get_rect(self):
        return self.rect

# Класс пули
class Bullet:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.radius = 5
        self.color = YELLOW
        self.direction = direction
        self.rect = pygame.Rect(x - self.radius, y - self.radius, self.radius * 2, self.radius * 2)

    def draw(self, win):
        pygame.draw.circle(win, self.color, (self.x, self.y), self.radius)

    def move(self, obstacles):
        if self.direction == "up":
            self.y -= BULLET_SPEED
        elif self.direction == "down":
            self.y += BULLET_SPEED
        elif self.direction == "left":
            self.x -= BULLET_SPEED
        elif self.direction == "right":
            self.x += BULLET_SPEED
        
        # Обновляем rect
        self.rect.x = self.x - self.radius
        self.rect.y = self.y - self.radius

        # Проверка столкновения с препятствиями
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle.rect):
                return True  # Пуля должна быть уничтожена
        return False

    def get_rect(self):
        return self.rect

# Класс бонуса
class Bonus:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = random.choice(BONUS_TYPES)
        self.color = GREEN if self.type == "shield" else BLUE if self.type == "invulnerability" else RED
        self.rect = pygame.Rect(x, y, BONUS_SIZE, BONUS_SIZE)

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, BONUS_SIZE, BONUS_SIZE))

    def get_rect(self):
        return self.rect

# Класс препятствия
class Obstacle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.width = OBSTACLE_WIDTH
        self.height = OBSTACLE_HEIGHT
        self.color = color
        self.rect = pygame.Rect(x, y, self.width, self.height)

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))

    def get_rect(self):
        return self.rect

# Класс противника
class EnemyTank(Tank):
    def __init__(self, x, y, target, image):
        super().__init__(x, y)
        self.target = target
        self.move_timer = pygame.time.get_ticks()
        self.shoot_timer = pygame.time.get_ticks()
        self.image = image

    def update(self, obstacles, tanks):
        # Движение к цели
        current_time = pygame.time.get_ticks()
        if current_time - self.move_timer > 1000:
            self.move_timer = current_time
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            distance = math.hypot(dx, dy)
            if distance != 0:
                dx /= distance
                dy /= distance
            self.move(dx, dy, obstacles, tanks)

        # Стрельба в цель
        if current_time - self.shoot_timer > 2000:
            self.shoot_timer = current_time
            return self.shoot()
        return None

# Функция для проверки, находится ли точка в препятствии
def is_position_valid(x, y, obstacles, tank_size=TANK_WIDTH):
    temp_rect = pygame.Rect(x, y, tank_size, tank_size)
    for obstacle in obstacles:
        if temp_rect.colliderect(obstacle.rect):
            return False
    return True

# Функция для создания препятствий для карты
def create_obstacles(map_name):
    obstacles = []
    
    if map_name == "map1":  # Underground_Storage
        color = DARK_GRAY
        # Создаем сетку препятствий
        for x in range(200, WIDTH - 200, 200):
            for y in range(150, HEIGHT - 150, 150):
                if random.random() < 0.6:  # 60% chance to place obstacle
                    obstacles.append(Obstacle(x, y, color))
    
    elif map_name == "map2":  # Castle_Lawn
        color = LIGHT_GRAY
        # 8 хаотично расположенных препятствий
        for _ in range(8):
            valid_position = False
            while not valid_position:
                x = random.randint(50, WIDTH - 50 - OBSTACLE_WIDTH)
                y = random.randint(50, HEIGHT - 50 - OBSTACLE_HEIGHT)
                # Проверяем, чтобы препятствие не было слишком близко к центру
                if (abs(x - WIDTH//2) > 150 or abs(y - HEIGHT//2) > 150):
                    valid_position = True
            obstacles.append(Obstacle(x, y, color))
    
    elif map_name == "map3":  # Besieged_City
        color = CANYON
        # Создаем "улицы" с препятствиями
        for x in range(50, WIDTH - 50, 250):
            for y in range(50, HEIGHT - 50, 200):
                if x % 500 == 50 or y % 400 == 50:
                    obstacles.append(Obstacle(x, y, color))
        
        # Добавляем фонтан/статую в центре
        fountain = Obstacle(WIDTH//2 - OBSTACLE_WIDTH, HEIGHT//2 - OBSTACLE_HEIGHT, FOUNTAIN_COLOR)
        obstacles.append(fountain)
    
    return obstacles

# Функция для получения позиций спавна игрока и врагов
def get_spawn_positions(map_name, obstacles, num_enemies):
    player_spawn = None
    enemy_spawns = []
    
    if map_name == "map1":  # Underground_Storage
        # Игрок в левом верхнем углу
        player_spawn = (100, 100)
        # Враги в правом нижнем углу
        for i in range(3):
            enemy_spawns.append((WIDTH - 150 - i*100, HEIGHT - 150 - i*100))
    
    elif map_name == "map2":  # Castle_Lawn
        # Игрок в центре левой стороны
        player_spawn = (100, HEIGHT//2)
        # Враги по углам и сторонам (4 врага)
        enemy_spawns = [
            (WIDTH - 150, 100),  # правый верх
            (WIDTH - 150, HEIGHT - 150),  # правый низ
            (WIDTH//2, 100),  # верх центр
            (WIDTH//2, HEIGHT - 150)  # низ центр
        ]
    
    elif map_name == "map3":  # Besieged_City
        # Игрок в левом нижнем углу
        player_spawn = (100, HEIGHT - 100)
        # Враги распределены по карте (6 врагов)
        enemy_spawns = [
            (WIDTH - 150, 100),  # правый верх
            (WIDTH - 150, HEIGHT//2),  # правый центр
            (WIDTH - 150, HEIGHT - 150),  # правый низ
            (WIDTH//2, 100),  # верх центр
            (WIDTH//4, 100),  # верх слева
            (WIDTH//2, HEIGHT - 150)  # низ центр
        ]
    
    # Проверяем, что позиции не в препятствиях
    if not is_position_valid(player_spawn[0], player_spawn[1], obstacles):
        # Если позиция игрока в препятствии, ищем ближайшую свободную
        for offset in range(0, 300, 50):
            for x in range(player_spawn[0] - offset, player_spawn[0] + offset + 1, 50):
                for y in range(player_spawn[1] - offset, player_spawn[1] + offset + 1, 50):
                    if 0 <= x <= WIDTH - TANK_WIDTH and 0 <= y <= HEIGHT - TANK_HEIGHT:
                        if is_position_valid(x, y, obstacles):
                            player_spawn = (x, y)
                            break
                else:
                    continue
                break
            else:
                continue
            break
    
    # Проверяем позиции врагов
    valid_enemy_spawns = []
    for spawn in enemy_spawns:
        if is_position_valid(spawn[0], spawn[1], obstacles):
            valid_enemy_spawns.append(spawn)
        else:
            # Ищем ближайшую свободную позицию
            for offset in range(0, 300, 50):
                for x in range(spawn[0] - offset, spawn[0] + offset + 1, 50):
                    for y in range(spawn[1] - offset, spawn[1] + offset + 1, 50):
                        if 0 <= x <= WIDTH - TANK_WIDTH and 0 <= y <= HEIGHT - TANK_HEIGHT:
                            if is_position_valid(x, y, obstacles):
                                valid_enemy_spawns.append((x, y))
                                break
                    else:
                        continue
                    break
                else:
                    continue
                break
    
    # Ограничиваем количество врагов
    enemy_spawns = valid_enemy_spawns[:num_enemies]
    
    return player_spawn, enemy_spawns

# Функция для отображения результатов
def show_results(win, time_elapsed, bonuses_collected, score, victory, player_name):
    font = pygame.font.SysFont("Arial", 40)
    win.fill(WHITE)

    # Отображение результатов
    result_text = f"{player_name}, Победа!" if victory else f"{player_name}, Поражение!"
    time_text = f"Время: {time_elapsed:.2f} сек"
    bonuses_text = f"Бонусов собрано: {bonuses_collected}"
    score_text = f"Счёт: {score}"

    # Отрисовка текста
    win.blit(font.render(result_text, True, BLACK), (WIDTH // 2 - 150, 100))
    win.blit(font.render(time_text, True, BLACK), (WIDTH // 2 - 100, 180))
    win.blit(font.render(bonuses_text, True, BLACK), (WIDTH // 2 - 100, 260))
    win.blit(font.render(score_text, True, BLACK), (WIDTH // 2 - 100, 340))

    # Кнопка "Вернуться в меню"
    return_button = pygame.Rect(WIDTH // 2 - 100, 420, 200, 50)
    pygame.draw.rect(win, GREEN, return_button)
    win.blit(font.render("Вернуться в меню", True, BLACK), (WIDTH // 2 - 90, 430))

    pygame.display.update()

    # Ожидание нажатия кнопки
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if return_button.collidepoint(event.pos):
                    return

# Основная функция игры
def main():
    # Получаем имя игрока
    player_name = get_player_name()
    if not player_name:
        return

    # Титульный экран
    selected_map = title_screen()
    if not selected_map:
        return

    run = True
    clock = pygame.time.Clock()

    # Загрузка изображений
    enemy_images = load_enemy_images()
    background = load_background(selected_map)

    # Создание препятствий для выбранной карты
    obstacles = create_obstacles(selected_map)

    # Определяем количество врагов в зависимости от карты
    if selected_map == "map1":
        num_enemies = 3
    elif selected_map == "map2":
        num_enemies = 4
    elif selected_map == "map3":
        num_enemies = 6

    # Получаем позиции спавна
    player_spawn, enemy_spawns = get_spawn_positions(selected_map, obstacles, num_enemies)

    # Создание танков
    tank1 = Tank(*player_spawn)
    enemies = [
        EnemyTank(*enemy_spawns[i], tank1, enemy_images[i % len(enemy_images)])
        for i in range(num_enemies)
    ]

    bullets = []
    enemy_bullets = []
    bonuses = []

    # Создание бонусов
    for _ in range(5):
        valid_position = False
        while not valid_position:
            x = random.randint(0, WIDTH - BONUS_SIZE)
            y = random.randint(0, HEIGHT - BONUS_SIZE)
            if is_position_valid(x, y, obstacles, BONUS_SIZE):
                valid_position = True
        bonuses.append(Bonus(x, y))

    # Время начала игры
    start_time = time.time()
    bonuses_collected = 0
    score = 0

    while run:
        clock.tick(60)
        WIN.blit(background, (0, 0))  # Отрисовка фона

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # Управление танком игрока
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            tank1.move(0, -1, obstacles, [tank1] + enemies)
        if keys[pygame.K_s]:
            tank1.move(0, 1, obstacles, [tank1] + enemies)
        if keys[pygame.K_a]:
            tank1.move(-1, 0, obstacles, [tank1] + enemies)
        if keys[pygame.K_d]:
            tank1.move(1, 0, obstacles, [tank1] + enemies)
        if keys[pygame.K_SPACE]:
            bullet = tank1.shoot()
            if bullet:
                bullets.append(bullet)

        # Обновление противников
        for enemy in enemies:
            enemy_bullet = enemy.update(obstacles, [tank1] + enemies)
            if enemy_bullet:
                enemy_bullets.append(enemy_bullet)

        # Обновление пуль игрока
        for bullet in bullets[:]:
            should_remove = bullet.move(obstacles)
            bullet.draw(WIN)
            
            if should_remove and bullet in bullets:
                bullets.remove(bullet)
                continue
                
            for enemy in enemies[:]:
                if bullet.get_rect().colliderect(enemy.get_rect()):
                    enemy.take_damage(1)
                    if enemy.hp <= 0:
                        enemies.remove(enemy)
                        score += 1000  # 1000 очков за убийство танка
                    if bullet in bullets:
                        bullets.remove(bullet)
                    break

        # Обновление пуль противников
        for bullet in enemy_bullets[:]:
            should_remove = bullet.move(obstacles)
            bullet.draw(WIN)
            
            if should_remove and bullet in enemy_bullets:
                enemy_bullets.remove(bullet)
                continue
                
            if bullet.get_rect().colliderect(tank1.get_rect()):
                tank1.take_damage(1)
                if bullet in enemy_bullets:
                    enemy_bullets.remove(bullet)

        # Обновление танков
        tank1.draw(WIN)
        for enemy in enemies:
            enemy.draw(WIN)

        # Обновление бонусов
        for bonus in bonuses[:]:
            bonus.draw(WIN)
            if tank1.get_rect().colliderect(bonus.get_rect()):
                if bonus.type == "shield":
                    tank1.activate_shield()
                elif bonus.type == "invulnerability":
                    tank1.activate_invulnerability()
                bonuses.remove(bonus)
                bonuses_collected += 1
                score += 100  # 100 очков за бонус

        # Обновление препятствий
        for obstacle in obstacles:
            obstacle.draw(WIN)

        # Обновление неуязвимости
        tank1.update_invulnerability()

        # Перезарядка пуль
        tank1.recharge()

        # Отображение информации
        font = pygame.font.SysFont("Arial", 30)
        # Имя игрока
        name_text = font.render(f"Игрок: {player_name}", True, WHITE)
        WIN.blit(name_text, (10, 10))
        # Счет
        score_text = font.render(f"Счёт: {score}", True, WHITE)
        WIN.blit(score_text, (10, 50))
        # Здоровье
        hp_text = font.render(f"HP: {tank1.hp}", True, WHITE)
        WIN.blit(hp_text, (10, 90))

        # Проверка завершения игры
        if not enemies:
            time_elapsed = time.time() - start_time
            show_results(WIN, time_elapsed, bonuses_collected, score, victory=True, player_name=player_name)
            run = False
        elif tank1.hp <= 0:
            time_elapsed = time.time() - start_time
            show_results(WIN, time_elapsed, bonuses_collected, score, victory=False, player_name=player_name)
            run = False

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()