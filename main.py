import sys
import os
import pygame


def load_level(filename):
    filename = "data/" + filename
    mapFile = open(filename, 'r')
    level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def terminate():
    pygame.quit()
    quit()


def load_image(path, colorkey=None):
    image = pygame.image.load(path).convert()
    if colorkey:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


FPS = 60
WIDTH = 1200
HEIGHT = 900

PLAYER_SPEED = 3

pygame.init()
size = (WIDTH, HEIGHT)
screen = pygame.display.set_mode(size)

TILE_WIDTH = 100
TILE_HEIGHT = 100
TILE_IMAGES = {"wall": pygame.transform.scale(load_image('data/box.png'), (TILE_WIDTH, TILE_HEIGHT)),
               "empty": pygame.transform.scale(load_image('data/grass.png'), (TILE_WIDTH, TILE_HEIGHT))}

player = None
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y, all_sprites, tiles_group)
            elif level[y][x] == '#':
                Tile('wall', x, y, all_sprites, tiles_group)
            elif level[y][x] == '@':
                Tile('empty', x, y, all_sprites, tiles_group)
                new_player = Player(x, y, all_sprites, player_group)
    return new_player, x, y


def start_screen():
    clock = pygame.time.Clock()
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]
    fon = pygame.transform.scale(load_image('data/background.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 40)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


class Player(pygame.sprite.Sprite):
    image = pygame.transform.scale(load_image("data/mar2.png", (255, 255, 255)), (TILE_WIDTH - 20, TILE_HEIGHT - 20))

    def __init__(self, pos_x, pos_y, *groups):
        super().__init__(groups)
        self.image = Player.image
        self.rect = self.image.get_rect()
        self.rect = self.image.get_rect().move(TILE_WIDTH * pos_x + 5, TILE_HEIGHT * pos_y + 5)
        self.prev_coords = None

    def move_left(self):
        self.prev_coords = self.rect.x, self.rect.y
        self.rect.x -= PLAYER_SPEED
        if check_collide(self):
            self.rect.x, self.rect.y = self.prev_coords

    def move_right(self):
        self.prev_coords = self.rect.x, self.rect.y
        self.rect.x += PLAYER_SPEED
        if check_collide(self):
            self.rect.x, self.rect.y = self.prev_coords

    def move_up(self):
        self.prev_coords = self.rect.x, self.rect.y
        self.rect.y -= PLAYER_SPEED
        if check_collide(self):
            self.rect.x, self.rect.y = self.prev_coords

    def move_down(self):
        self.prev_coords = self.rect.x, self.rect.y
        self.rect.y += PLAYER_SPEED
        if check_collide(self):
            self.rect.x, self.rect.y = self.prev_coords


class Tile(pygame.sprite.Sprite):
    def __init__(self, type, pos_x, pos_y, *groups):
        super().__init__(groups)
        self.image = TILE_IMAGES[type]
        self.rect = self.image.get_rect().move(TILE_WIDTH * pos_x, TILE_HEIGHT * pos_y)
        self.type = type


def check_collide(player):
    for obj in all_sprites:
        if id(player) == id(obj):
            continue
        if obj.type == "wall" and player.rect.colliderect(obj.rect):
            return True
    return False


if __name__ == "__main__":
    data = sys.argv
    pygame.display.iconify()
    if len(data) > 1:
        level = data[1]
    else:
        level = input("Enter the level number:   ")
    if level + ".dat" not in os.listdir("data"):
        print("There is no file with such name!")
        quit()
    screen = pygame.display.set_mode(size)
    print("Game has already been prepared for you. Check it below!")
    start_screen()
    running = True
    fon = pygame.transform.scale(load_image('data/background.png'), (WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    screen.blit(fon, (0, 0))
    player, level_x, level_y = generate_level(load_level(level + '.dat'))
    moving = False
    turn = None
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                moving = True
                if event.key == 276:
                    turn = player.move_left
                elif event.key == 275:
                    turn = player.move_right
                elif event.key == 273:
                    turn = player.move_up
                elif event.key == 274:
                    turn = player.move_down
            if event.type == pygame.KEYUP:
                moving = False
        if moving and turn:
            turn()
        tiles_group.draw(screen)
        player_group.draw(screen)
        pygame.display.flip()
        screen.blit(fon, (0, 0))
        clock.tick(FPS)
