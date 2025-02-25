import pygame
from pygame.locals import *

pygame.init()

clock = pygame.time.Clock()
fps = 60

# Параметры экрана
scr_width, scr_height = 900, 900
screen = pygame.display.set_mode((scr_width, scr_height))
pygame.display.set_caption('Game')

# Параметры текстур и др.
black = (0, 0, 0)
cub_size = 50
level = 0
max_levels = 2
game_over = 0
score = 0
col = 0
main_menu = True
font_score = pygame.font.SysFont('Bauhaus 93', 30)
font = pygame.font.SysFont('Bauhaus 93', 30)

# Загрузка иконок
start = pygame.image.load('btn_start.png')
end = pygame.image.load('end_button.png')
main = pygame.image.load('start_image.png')
logo_start = pygame.image.load('name.png')
logo_end = pygame.image.load('name1.png')


# Если игрок прошёл уровень
def reset_level(level):
    player.reset(100, scr_height - 130)
    exit_group.empty()
    coin_group.empty()
    world = World(world_data[level])
    return world


# Написание текста
def text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


# Создание мира
class World():
    def __init__(self, data):
        self.list = []

        # Загрузка изображений
        dirt_img = pygame.image.load('stone.jpg')
        grass_img = pygame.image.load('stone1.jpg')

        # Отрисовка мира
        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (cub_size, cub_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * cub_size
                    img_rect.y = row_count * cub_size
                    tile = (img, img_rect)
                    self.list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(grass_img, (cub_size, cub_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * cub_size
                    img_rect.y = row_count * cub_size
                    tile = (img, img_rect)
                    self.list.append(tile)
                if tile == 3:
                    coin = Coin(col_count * cub_size + (cub_size // 2), row_count * cub_size + (cub_size // 2))
                    coin_group.add(coin)
                if tile == 4:
                    exit = Exit(col_count * cub_size, row_count * cub_size - (cub_size // 2))
                    exit_group.add(exit)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.list:
            screen.blit(tile[0], tile[1])
            pygame.draw.rect(screen, (0, 0, 0), tile[1], 1)

# Создание игрока
class Player():
    def __init__(self, x, y):
        self.reset(x, y)

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 5):
            img_right = pygame.image.load(f'guy{num}.png')
            img_right = pygame.transform.scale(img_right, (40, 80))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0

    def download(self, game_over):
        dx = 0
        dy = 0
        walk_cooldown = 5

        if game_over == 0:
            # Кнопки клавиатуры
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
                self.vel_y = -15
                self.jumped = True
            if key[pygame.K_SPACE] == False:
                self.jumped = False
            if key[pygame.K_LEFT]:
                dx -= 5
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx += 5
                self.counter += 1
                self.direction = 1
            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # Анимация
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # Гравитация
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            # Столкновение
            self.in_air = True
            for tile in world.list:
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False

            # Столкновение с выходом
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1

            self.rect.x += dx
            self.rect.y += dy

            # Изображение героя
            if level != 2:
                screen.blit(self.image, self.rect)

            return game_over


# Изображение выхода
class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('exit.png')
        self.image = pygame.transform.scale(img, (cub_size, int(cub_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


# Изображение монет
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('coin.png')
        self.image = pygame.transform.scale(img, (cub_size // 2, cub_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


exit_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()

score_coin = Coin(cub_size // 2, cub_size // 2)
coin_group.add(score_coin)


# Отображение кнопок
class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False

        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # Рисование кнопки
        screen.blit(self.image, self.rect)

        return action


start_button = Button(300, 400, start)
end_button = Button(300, 400, end)

player = Player(100, scr_height - 130)

world_data = [[
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[1, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 4],
[1, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 3, 0, 0, 1, 2, 1, 2],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 3, 0, 5, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 2, 2, 0, 0, 0, 2],
[1, 3, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 3, 0, 0, 2],
[1, 0, 2, 0, 0, 3, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 3, 0, 0, 1],
[1, 0, 0, 0, 0, 2, 2, 2, 0, 2, 2, 2, 2, 2, 2, 0, 0, 2],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 3, 0, 0, 0, 1, 2],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 2],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 0, 2, 2, 2, 2],
[1, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
[1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]],
[[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 4, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 1, 2, 2, 1, 2, 0, 0, 0, 0, 0, 3, 0, 3, 2, 2, 0, 2],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 3, 0, 1, 1, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
[1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 3, 0, 0, 1],
[1, 0, 2, 0, 0, 3, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
[1, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 3, 0, 0, 1],
[1, 0, 0, 0, 0, 2, 2, 2, 0, 2, 2, 2, 2, 2, 2, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 3, 0, 2, 2, 2, 2],
[1, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1],
[1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]],
[[0]]]

world = World(world_data[level])

run = True
while run:
    clock.tick(fps)

    screen.blit(main, (0, 0))

    if main_menu == True:
        screen.blit(logo_start, (250, 250))
        if start_button.draw():
            main_menu = False
    else:
        world.draw()
        game_over = player.download(game_over)

        exit_group.draw(screen)
        coin_group.draw(screen)
        if game_over == 0 and level != 2:
            if pygame.sprite.spritecollide(player, coin_group, True):
                score += 1
            text('X' + str(score), font_score, black, cub_size - 10, 10)
        if level == 2:
            screen.blit(logo_end, (250, 250))
            if end_button.draw():
                run = False
        if game_over == 1:
            level += 1
            if level <= max_levels:
                world = reset_level(level)
                game_over = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()