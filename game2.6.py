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
GRAY = (128, 128, 128)  # Серый цвет для недоступных кнопок

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
NUM_OBSTACLES = 10  # Количество препятствий

# Загрузка изображений
def load_image(path, width, height):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Файл {path} не найден!") 
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
def load_background():
    return load_image(os.path.join("Sprites", "background.jpg"), WIDTH, HEIGHT)

# Титульный экран
def title_screen():
    run = True
    clock = pygame.time.Clock()

    # Загрузка фона
    background = load_background()

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
        text = font.render("Карта 1", True, BLACK)
        WIN.blit(text, (WIDTH // 2 - text.get_width() // 2, 210))

        # Кнопка карты 2 (недоступна)
        map2_button = pygame.Rect(WIDTH // 2 - 100, 300, 200, 50)
        pygame.draw.rect(WIN, GRAY, map2_button)
        text = font.render("Скоро", True, BLACK)
        WIN.blit(text, (WIDTH // 2 - text.get_width() // 2, 310))

        # Кнопка карты 3 (недоступна)
        map3_button = pygame.Rect(WIDTH // 2 - 100, 400, 200, 50)
        pygame.draw.rect(WIN, GRAY, map3_button)
        text = font.render("Скоро", True, BLACK)
        WIN.blit(text, (WIDTH // 2 - text.get_width() // 2, 410))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if map1_button.collidepoint(event.pos):
                    return "map1"  # Возвращаем выбранную карту

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

    def move(self, dx, dy):
        # Сохраняем направление движения
        self.dx = dx
        self.dy = dy

        # Проверка границ окна
        new_x = self.x + dx * TANK_SPEED
        new_y = self.y + dy * TANK_SPEED

        if 0 <= new_x <= WIDTH - TANK_WIDTH:
            self.x = new_x
        if 0 <= new_y <= HEIGHT - TANK_HEIGHT:
            self.y = new_y

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
        return pygame.Rect(self.x, self.y, TANK_WIDTH, TANK_HEIGHT)

# Класс пули
class Bullet:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.radius = 5
        self.color = YELLOW
        self.direction = direction

    def draw(self, win):
        pygame.draw.circle(win, self.color, (self.x, self.y), self.radius)

    def move(self):
        if self.direction == "up":
            self.y -= BULLET_SPEED
        elif self.direction == "down":
            self.y += BULLET_SPEED
        elif self.direction == "left":
            self.x -= BULLET_SPEED
        elif self.direction == "right":
            self.x += BULLET_SPEED

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

# Класс бонуса
class Bonus:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = random.choice(BONUS_TYPES)
        self.color = GREEN if self.type == "shield" else BLUE if self.type == "invulnerability" else RED

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, BONUS_SIZE, BONUS_SIZE))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, BONUS_SIZE, BONUS_SIZE)

# Класс препятствия
class Obstacle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = OBSTACLE_WIDTH
        self.height = OBSTACLE_HEIGHT

    def draw(self, win):
        pygame.draw.rect(win, CANYON, (self.x, self.y, self.width, self.height))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

# Класс противника
class EnemyTank(Tank):
    def __init__(self, x, y, target, image):
        super().__init__(x, y)
        self.target = target
        self.move_timer = pygame.time.get_ticks()
        self.shoot_timer = pygame.time.get_ticks()
        self.image = image

    def update(self):
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
            self.move(dx, dy)

        # Стрельба в цель
        if current_time - self.shoot_timer > 2000:
            self.shoot_timer = current_time
            return self.shoot()
        return None

# Функция для отображения результатов
def show_results(win, time_elapsed, bonuses_collected, victory):
    font = pygame.font.SysFont("Arial", 40)
    win.fill(WHITE)

    # Отображение результатов
    result_text = "Победа!" if victory else "Поражение!"
    time_text = f"Время: {time_elapsed:.2f} сек"
    bonuses_text = f"Бонусов собрано: {bonuses_collected}"

    # Отрисовка текста
    win.blit(font.render(result_text, True, BLACK), (WIDTH // 2 - 100, 100))
    win.blit(font.render(time_text, True, BLACK), (WIDTH // 2 - 100, 200))
    win.blit(font.render(bonuses_text, True, BLACK), (WIDTH // 2 - 100, 300))

    # Кнопка "Вернуться в меню"
    return_button = pygame.Rect(WIDTH // 2 - 100, 400, 200, 50)
    pygame.draw.rect(win, GREEN, return_button)
    win.blit(font.render("Вернуться в меню", True, BLACK), (WIDTH // 2 - 90, 410))

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
    # Титульный экран
    selected_map = title_screen()
    if not selected_map:
        return

    run = True
    clock = pygame.time.Clock()

    # Загрузка изображений
    enemy_images = load_enemy_images()
    background = load_background()

    # Создание танков
    tank1 = Tank(100, 100)
    enemies = [
        EnemyTank(random.randint(0, WIDTH - TANK_WIDTH), random.randint(0, HEIGHT - TANK_HEIGHT), tank1, enemy_images[i])
        for i in range(3)
    ]

    bullets = []
    enemy_bullets = []
    bonuses = []

    # Создание бонусов
    for _ in range(5):
        bonuses.append(Bonus(random.randint(0, WIDTH - BONUS_SIZE), random.randint(0, HEIGHT - BONUS_SIZE)))

    # Создание препятствий
    obstacles = []
    for _ in range(NUM_OBSTACLES):
        x = random.randint(0, WIDTH - OBSTACLE_WIDTH)
        y = random.randint(0, HEIGHT - OBSTACLE_HEIGHT)
        obstacles.append(Obstacle(x, y))

    # Время начала игры
    start_time = time.time()
    bonuses_collected = 0

    while run:
        clock.tick(60)
        WIN.blit(background, (0, 0))  # Отрисовка фона

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # Управление танком игрока
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            tank1.move(0, -1)
        if keys[pygame.K_s]:
            tank1.move(0, 1)
        if keys[pygame.K_a]:
            tank1.move(-1, 0)
        if keys[pygame.K_d]:
            tank1.move(1, 0)
        if keys[pygame.K_SPACE]:
            bullet = tank1.shoot()
            if bullet:
                bullets.append(bullet)

        # Обновление противников
        for enemy in enemies:
            enemy_bullet = enemy.update()
            if enemy_bullet:
                enemy_bullets.append(enemy_bullet)

        # Обновление пуль игрока
        for bullet in bullets[:]:
            bullet.move()
            bullet.draw(WIN)
            for enemy in enemies[:]:
                if bullet.get_rect().colliderect(enemy.get_rect()):
                    enemy.take_damage(1)
                    if enemy.hp <= 0:
                        enemies.remove(enemy)
                    if bullet in bullets:
                        bullets.remove(bullet)
                    break

        # Обновление пуль противников
        for bullet in enemy_bullets[:]:
            bullet.move()
            bullet.draw(WIN)
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

        # Обновление препятствий
        for obstacle in obstacles:
            obstacle.draw(WIN)

        # Проверка столкновений танка с препятствиями
        tank_rect = tank1.get_rect()
        for obstacle in obstacles:
            if tank_rect.colliderect(obstacle.get_rect()):
                # Возвращаем танк на предыдущую позицию
                tank1.x -= tank1.dx * TANK_SPEED
                tank1.y -= tank1.dy * TANK_SPEED

        # Обновление неуязвимости
        tank1.update_invulnerability()

        # Перезарядка пуль
        tank1.recharge()

        # Проверка завершения игры
        if not enemies:
            time_elapsed = time.time() - start_time
            show_results(WIN, time_elapsed, bonuses_collected, victory=True)
            run = False
        elif tank1.hp <= 0:
            time_elapsed = time.time() - start_time
            show_results(WIN, time_elapsed, bonuses_collected, victory=False)
            run = False

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
