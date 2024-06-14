import pygame
from pygame import mixer
import sys
import os
import random
import csv
import button

mixer.init()
pygame.init()
mixer.set_num_channels(16)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH*0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Shooter')

# set framerate
clock = pygame.time.Clock()
FPS = 60

# defind fame variables
GRAVITY = 0.75
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT// ROWS
TILE_TYPES = 21
MAX_LEVELS = 3
screen_scroll = 0
bg_scroll = 0
level = 1

# Define player actions variables
moving_left = False
moving_right = False
shoot = False
grenade = False     
grenade_thrown = True

# load music and sounds
pygame.mixer.music.load('audio/background_music.mp3')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000)
jump_fx = pygame.mixer.Sound('audio/land-81509.mp3')
jump_fx.set_volume(0.3)
shot_fx = pygame.mixer.Sound('audio/m1-garand-rifle-80192.mp3')
shot_fx.set_volume(0.05)
grenade_fx = pygame.mixer.Sound('audio/grenade-explosion-14-190266.mp3')
grenade_fx.set_volume(0.5)
death_fx = pygame.mixer.Sound('audio/man-death-scream-186763.mp3')
death_fx.set_volume(0.5)
# playerdeath_fx = pygame.mixer.Sound('audio/howie-scream-105591.mp3')
# playerdeath_fx.set_volume(0.5)


# load images
# button_images
start_img = pygame.image.load('img/start_btn.png').convert_alpha()
exit_img = pygame.image.load('img/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('img/restart_btn.png').convert_alpha()
win_img = pygame.image.load('img/win_btn.png').convert_alpha()
#background
pine1_img = pygame.image.load('img/Background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('img/Background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('img/Background/mountain.png').convert_alpha()
sky_img = pygame.image.load('img/Background/sky_cloud.png').convert_alpha()
# bullet
bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()
# grenade
grenade_img = pygame.image.load('img/icons/grenade.png').convert_alpha()
# pick up boxes
health_box_img = pygame.image.load('img/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('img/icons/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load('img/icons/grenade_box.png').convert_alpha()
item_boxes = {
	'Health'	: health_box_img,
	'Ammo'		: ammo_box_img,
	'Grenade'	: grenade_box_img
}

# get tile images
img_list = []
for i in range(21):
    img = pygame.image.load(f'img/tile/{i}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

#define colours
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

#define font
font = pygame.font.SysFont('dejavuserif', 30)

def draw_text(text, font, text_col, x, y):
    """
    Draw text on the screen.

    Args:
        text (str): The text to render.
        font (pygame.font.Font): The font to use.
        text_col (tuple): The color of the text.
        x (int): The x-coordinate of the text.
        y (int): The y-coordinate of the text.
    """
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))
     
def draw_bg():
    """
    Draw the background on the screen.
    """
    screen.fill(BG)
    for i in range(5):
        screen.blit(sky_img, (i*sky_img.get_width()+bg_scroll*0.5,0))
        screen.blit(mountain_img, (i*sky_img.get_width()+bg_scroll*0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300))
        screen.blit(pine1_img, (i*sky_img.get_width()+bg_scroll*0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
        screen.blit(pine2_img, (i*sky_img.get_width()+bg_scroll*0.8, SCREEN_HEIGHT - pine2_img.get_height()))

# function to reset level
def reset_level():
    """
    Reset the current game level by clearing all groups.
    """
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decorration_group.empty()
    water_group.empty()
    exit_group.empty()

    

class Soldier(pygame.sprite.Sprite):
    """
    A class representing a soldier in the game.

    Attributes:
        char_type (str): The type of the character (player or enemy).
        x (int): The x-coordinate of the soldier.
        y (int): The y-coordinate of the soldier.
        scale (float): The scale of the soldier sprite.
        speed (int): The speed of the soldier.
        ammo (int): The amount of ammo the soldier has.
        grenades (int): The number of grenades the soldier has.
        alive (bool): The status of the soldier's life.
        y_vel (int): The vertical velocity of the soldier.
        in_air (bool): Whether the soldier is in the air.
        start_ammo (int): The initial amount of ammo the soldier has.
        shoot_cooldown (int): The cooldown period between shots.
        health (int): The current health of the soldier.
        max_health (int): The maximum health of the soldier.
        direction (int): The direction the soldier is facing (1 for right, -1 for left).
        jump (bool): Whether the soldier is in a jump state.
        flip (bool): Whether the soldier's image is flipped horizontally.
        action (int): The current action being performed by the soldier.
        animation_list (list): A list of lists containing animation frames for different actions.
        frame_index (int): The current frame index of the animation.
        update_time (int): The time when the animation frame was last updated.
        move_counter (int): A counter to manage AI movement.
        vision (pygame.Rect): The rectangular area representing the soldier's vision.
        idling (bool): Whether the soldier is idling.
        idling_counter (int): A counter to manage idling behavior.
        image (pygame.Surface): The current image of the soldier.
        rect (pygame.Rect): The rectangular area of the soldier.
        width (int): The width of the soldier's image.  
        height (int): The height of the soldier's image.
    """
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        """
        Initialize the soldier.

        Args:
            char_type (str): The type of the character (player or enemy).
            x (int): The x-coordinate of the soldier.
            y (int): The y-coordinate of the soldier.
            scale (float): The scale of the soldier sprite.
            speed (int): The speed of the soldier.
            ammo (int): The amount of ammo the soldier has.
            grenades (int): The number of grenades the soldier has.
        """
        pygame.sprite.Sprite.__init__(self)
        self.is_alive = True
        self.char_type = char_type
        self.y_vel = 0
        self.in_air = True
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.grenades = grenades
        self.shoot_cooldown = 0
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.jump = False
        self.flip = False
        self.action = 0
        self.animation_list = []
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.action = 0
        # ai specific variables
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)    
        self.idling = False
        self.idling_counter = 0

		#load all images for the players
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            tmp_list = []
            num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                tmp_list.append(img)
            self.animation_list.append(tmp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        """
        Update the soldier's state.
        """
        self.check_alive()
        self.update_animation()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        """
        Move the soldier.

        Args:
            moving_left (bool): Whether the soldier is moving left.
            moving_right (bool): Whether the soldier is moving right.

        Returns:
            tuple: The screen scroll and whether the level is complete.
        """
        
        # reset moving variable
        screen_scroll = 0
        dx = 0
        dy = 0 

        if moving_left:
            self.flip = True
            self.direction = -1
            dx -= self.speed
        if moving_right:
            self.flip = False
            self.direction = 1
            dx += self.speed
        # jump
        if self.jump and self.in_air == False:
            self.y_vel = -12
            self.jump = False
            self.in_air = True

        # apply gravity    
        self.y_vel += GRAVITY
        if self.y_vel >= 10:
            self.y_vel = 10
        dy += self.y_vel        

        # check collision
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                if self.char_type == 'enemy':
                    self.direction *= -1
                    self.move_counter = 0
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # check if falling
                if self.y_vel >= 0:
                    dy = tile[1].top - self.rect.bottom
                    self.in_air = False
                    self.y_vel = 0
                # check if hitting head
                else:
                    dy = tile[1].bottom - self.rect.top
                    self.y_vel = 0


        # check for collision with water
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0

        # check for collision with exit
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True

        # check if fallen off the map
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0

        # check if going off edges of the screen
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dy > SCREEN_WIDTH:
                dx = 0

        # update rectangle position
        self.rect.x += dx
        self.rect.y += dy   

        # scroll based on player position
        if self.char_type == 'player':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and -bg_scroll < world.level_length*TILE_SIZE-SCREEN_WIDTH) \
                or (self.rect.left < SCROLL_THRESH and bg_scroll < 0):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll, level_complete

    def shoot(self):
        """
        Make the soldier shoot a bullet.
        """
        if self.shoot_cooldown == 0 and self.ammo:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + 0.75 * self.rect.size[0] * self.direction, self.rect.centery, self.direction)
            bullet_group.add(bullet)
            # reduce ammo
            self.ammo -= 1
            shot_fx.play()

    def ai(self):
        """
        Define the AI behavior for the enemy soldier.
        """
        if self.is_alive and player.is_alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0)#0: idle
                self.idling = True
                self.idling_counter = 50
            #check if the ai in near the player
            elif self.vision.colliderect(player.rect):
                # head the enemy to the player
                if player.rect.x < self.rect.x:
                    self.flip = True
                else:
                    self.flip = False
                # stay still
                self.update_action(0)
                # shoot the player
                self.shoot()
    
            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)#1: run
                    self.move_counter += 1
                    #update ai vision as the enemy moves
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)
                    # pygame.draw.rect(screen, RED, self.vision)
                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False
        #scroll bot
        self.rect.x += screen_scroll 

    def update_animation(self):
        """
        Update the animation state of the soldier.
        """
        # update animation
        ANIMATION_COOLDOWN = 100
        # update image depending on current frame
        # print(self.action, self.frame_index)
        self.image = self.animation_list[self.action][self.frame_index]
        # check if time has passed
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        """
        Update the action state of the soldier.

        Args:
            new_action (int): The new action state.
        """

        # check if new action if different from the current one
        if self.action != new_action:
            self.action = new_action
            # update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        """
        Check if the soldier is still alive.
        """
        if self.health <= 0:
            if self.is_alive == True:
                death_fx.play()
            self.is_alive = False
            self.speed = 0
            self.action = 3
            self.update_action(3)

    def draw(self):
        """
        Draw the soldier on the screen.
        """
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

class World:
    """
    A class representing the game world.

    Attributes:
        level_length (int): The length of the level.
        obstacle_list (list): The list of obstacles in the world.
    """
    def __init__(self):
        """
        Initialize the world.
        """
        self.obstacle_list = [] # list of tuple (img, rect)

    def process_data(self, data):
        """
        Process the level data to create the world.

        Args:
            data (list): The level data.
        """
        self.level_length = len(data[0])
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                tile = int(tile)
                if tile == -1:
                    continue
                img = img_list[tile]
                img_rect = img.get_rect()
                img_rect.x = x * TILE_SIZE
                img_rect.y = y * TILE_SIZE
                # img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
                # obstacle
                if 0 <= tile <= 8:
                    self.obstacle_list.append((img, img_rect))
                # water
                if 9 <= tile <= 10:
                    water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                    water_group.add(water)
                # decoration
                if 11 <= tile <= 14:
                    decorration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                    decorration_group.add(decorration)
                # player
                if tile == 15:
                    player = Soldier('player', x * TILE_SIZE, y * TILE_SIZE, 1.65, 5, 20, 5)
                    health_bar = HealthBar(10, 10, player.health, player.max_health)
                # enemy
                if tile == 16:
                    enemy = Soldier('enemy', x * TILE_SIZE, y * TILE_SIZE, 1.65, 2, 200, 5)
                    enemy_group.add(enemy)  
                # ammo
                if tile == 17:
                    item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
                    item_box_group.add(item_box)
                # grenade
                if tile == 18:
                    item_box = ItemBox('Grenade', x * TILE_SIZE, y * TILE_SIZE)
                    item_box_group.add(item_box)
                # health
                if tile == 19:
                    item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
                    item_box_group.add(item_box)
                # finish 
                if tile == 20:
                    finish = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                    exit_group.add(finish)

        return player, health_bar
    
    def draw(self):
        """
        Draw the world on the screen.
        """
        for tile in self.obstacle_list:
            tile[1].x += screen_scroll
            screen.blit(tile[0], tile[1])

class ExtraObject(pygame.sprite.Sprite):
    """
    A class representing an extra object in the game.

    Attributes:
        image (pygame.Surface): The image of the object.
        rect (pygame.Rect): The rectangular area of the object.
    """
    def __init__(self, img, x, y):
        """
        Initialize the extra object.

        Args:
            img (pygame.Surface): The image of the object.
            x (int): The x-coordinate of the object.
            y (int): The y-coordinate of the object.
        """
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = img.get_rect()
        self.rect.midtop = (x + TILE_SIZE//2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        """
        Update the state of the object.
        """
        self.rect.x += screen_scroll

class Decoration(ExtraObject):
    """
    A class representing a decoration object in the game.
    """
    def __init__(self, img, x, y):
        """
        Initialize the decoration object.

        Args:
            img (pygame.Surface): The image of the decoration.
            x (int): The x-coordinate of the decoration.
            y (int): The y-coordinate of the decoration.
        """
        super().__init__(img, x, y)

class Water(ExtraObject):
    """
    A class representing a water object in the game.
    """
    def __init__(self, img, x, y):
        """
        Initialize the water object.

        Args:
            img (pygame.Surface): The image of the water.
            x (int): The x-coordinate of the water.
            y (int): The y-coordinate of the water.
        """
        super().__init__(img, x, y)

class Exit(ExtraObject):
    """
    A class representing an exit object in the game.
    """
    def __init__(self, img, x, y):
        """
        Initialize the exit object.

        Args:
            img (pygame.Surface): The image of the exit.
            x (int): The x-coordinate of the exit.
            y (int): The y-coordinate of the exit.
        """
        super().__init__(img, x, y)

class ItemBox(pygame.sprite.Sprite):
    """
    A class representing an item box in the game.

    Attributes:
        item_type (str): The type of the item.
        image (pygame.Surface): The image of the item box.
        rect (pygame.Rect): The rectangular area of the item box.
    """
    def __init__(self, item_type, x, y):
        """
        Initialize the item box.

        Args:
            item_type (str): The type of the item.
            x (int): The x-coordinate of the item box.
            y (int): The y-coordinate of the item box.
        """
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        """
        Update the state of the item box.
        """
        self.rect.x += screen_scroll
        # check if the player has picked up the box
        if pygame.sprite.collide_rect(self, player):
            #check what kind of box it was
            if self.item_type == 'Health':
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'Ammo':
                player.ammo += 15
            elif self.item_type == 'Grenade':
                player.grenades += 3
            #delete the item box
            self.kill()


class HealthBar():
    """
    A class representing the health bar of the player.

    Attributes:
        x (int): The x-coordinate of the health bar.
        y (int): The y-coordinate of the health bar.
        health (int): The current health of the player.
        max_health (int): The maximum health of the player.
    """
    def __init__(self, x, y, health, max_health):
        """
        Initialize the health bar.

        Args:
            x (int): The x-coordinate of the health bar.
            y (int): The y-coordinate of the health bar.
            health (int): The current health of the player.
            max_health (int): The maximum health of the player.
        """
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        """
        Draw the health bar on the screen.

        Args:
            health (int): The current health of the player.
        """
        #update with new health
        self.health = health
        #calculate health ratio
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 804, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 800, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 800 * ratio, 20))


class Bullet(pygame.sprite.Sprite):
    """
    A class representing a bullet in the game.

    Attributes:
        image (pygame.Surface): The image of the bullet.
        rect (pygame.Rect): The rectangular area of the bullet.
        speed (int): The speed of the bullet.
        direction (int): The direction of the bullet.
    """
    def __init__(self, x, y, direction):
        """
        Initialize the bullet.

        Args:
            x (int): The x-coordinate of the bullet.
            y (int): The y-coordinate of the bullet.
            direction (int): The direction of the bullet.
        """
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.speed = 10
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        """
        Update the state of the bullet.
        """
        # move bullet
        self.rect.x += self.direction*self.speed + screen_scroll
        # delete bullet if reached screen border
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
        # check collision with level
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()
        # check colision with characters
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.is_alive:
                player.health -= 5
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.is_alive:
                    enemy.health -= 25
                    self.kill()

class Grenade(pygame.sprite.Sprite):
    """
    A class representing a grenade in the game.

    Attributes:
        timer (int): The timer for the grenade explosion.
        vel_y (float): The vertical velocity of the grenade.
        speed (int): The speed of the grenade.
        image (pygame.Surface): The image of the grenade.
        rect (pygame.Rect): The rectangular area of the grenade.
        direction (int): The direction of the grenade.
        width (int): The width of the grenade.
        height (int): The height of the grenade.
    """
    def __init__(self, x, y, direction):
        """
        Initialize the grenade.

        Args:
            x (int): The x-coordinate of the grenade.
            y (int): The y-coordinate of the grenade.
            direction (int): The direction of the grenade.
        """
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        """
        Update the state of the grenade.
        """
        self.vel_y += GRAVITY
        dx = self.speed * self.direction
        dy = self.vel_y
        # # check collsion with walls
        # if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
        #     self.direction *= -1
        #     dx = self.speed * self.direction
    
        # check if landed on ground
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x+dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.speed * self.direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # check if hit bottom
                if self.vel_y >= 0:
                    dy = tile[1].top - self.rect.bottom
                    self.speed = 0
                    self.vel_y = 0
                # check if hit top
                else:
                    self.vel_y = 0
                    dy =  tile[1].bottom - self.rect.top

        self.rect.x += dx + screen_scroll
        self.rect.y += dy


		#countdown timer
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            grenade_fx.play()
            explosion = Explosion(self.rect.x, self.rect.y, 0.5)
            explosion_group.add(explosion)
            #do damage to anyone that is nearby
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
                abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                player.health -= 50
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                    abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                    enemy.health -= 50

class Explosion(pygame.sprite.Sprite):
    """
        Initialize the explosion.

        Args:
            x (int): The x-coordinate of the explosion.
            y (int): The y-coordinate of the explosion.
            scale (float): The scale of the explosion.
    """
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f'img/explosion/exp{num}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0


    def update(self):
        #scroll
        self.rect.x += screen_scroll

        EXPLOSION_SPEED = 4
        #update explosion amimation
        self.counter += 1

        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            #if the animation is complete then delete the explosion
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]


# create button
start_button = button.Button(SCREEN_WIDTH//2-130, SCREEN_HEIGHT//2-150, start_img, 1)
exit_button = button.Button(SCREEN_WIDTH//2-110, SCREEN_HEIGHT//2+50, exit_img, 1)
restart_button = button.Button(SCREEN_WIDTH//2-100, SCREEN_HEIGHT//2-50, restart_img, 2)
win_button = button.Button(SCREEN_WIDTH//2-180, SCREEN_HEIGHT//2-50, win_img, 8)

bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decorration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()


if __name__ == '__main__':
    with open(f'map/level{level}_data.csv', mode='r') as file:
        reader = csv.reader(file)
        # Convert the reader object to a list of rows
        world_data = list(reader)

    world = World()
    player, health_bar = world.process_data(world_data)

    run = True
    start_game = False
    pygame.mixer.music.play(-1, 0.0, 5000)
    while run:
        clock.tick(FPS)
        if start_game == False:
            # draw menu
            screen.fill(BG)
            # add buttons
            if exit_button.draw(screen):
                run = False
            if start_button.draw(screen):
                start_game = True
            

        else:
            # update background
            draw_bg()
            # draw world map
            world.draw()
            #show player health
            health_bar.draw(player.health)
            #show ammo
            draw_text('AMMO: ', font, WHITE, 10, 35)
            for x in range(player.ammo):
                screen.blit(bullet_img, (120 + (x * 10), 45))
            #show grenades
            draw_text('GRENADES: ', font, WHITE, 10, 60)
            for x in range(player.grenades):
                screen.blit(grenade_img, (185 + (x * 15), 70))
            
            for enemy in enemy_group:
                
                enemy.update()
                enemy.draw()
                enemy.ai()
            
            
            # update and draw bullets

            bullet_group.update()
            grenade_group.update()
            explosion_group.update()
            item_box_group.update()
            decorration_group.update()
            water_group.update()
            exit_group.update()

            bullet_group.draw(screen)
            grenade_group.draw(screen)
            explosion_group.draw(screen)
            item_box_group.draw(screen)
            decorration_group.draw(screen)
            water_group.draw(screen)
            exit_group.draw(screen)

            

            player.update()
            player.draw()

            # update player actions
            if player.is_alive:
                if shoot:
                    player.shoot()
                if grenade and grenade_thrown == False and player.grenades:
                    grenade_group.add(Grenade(player.rect.centerx + 0.5 * player.rect.size[0] * player.direction,\
                                            player.rect.top, player.direction))
                    grenade_thrown = True
                    player.grenades -= 1
                if player.in_air:
                    player.update_action(2) # jump
                elif moving_left or moving_right:
                    player.update_action(1) # run
                else:
                    player.update_action(0) # idle

                # update player movement
                screen_scroll, level_complete = player.move(moving_left, moving_right)
                bg_scroll += screen_scroll
                if level_complete:
                    level += 1
                    
                    if level <= MAX_LEVELS:
                        bg_scroll = 0
                        reset_level()
                        with open(f'map/level{level}_data.csv', mode='r') as file:
                            reader = csv.reader(file)
                            # Convert the reader object to a list of rows
                            world_data = list(reader)
                        world = World()
                        player, health_bar = world.process_data(world_data)
                    else:
                        if win_button.draw(screen):
                            start_game = False
                            level = 0

            else:
                screen_scroll = 0
                if restart_button.draw(screen):
                    bg_scroll = 0
                    reset_level()
                    with open(f'map/level{level}_data.csv', mode='r') as file:
                        reader = csv.reader(file)
                        # Convert the reader object to a list of rows
                        world_data = list(reader)

                    world = World()
                    player, health_bar = world.process_data(world_data)
        for event in pygame.event.get():
            # quit game
            if event.type == pygame.QUIT:
                run = False

            # Keyboard pressed
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    moving_left = True
                if event.key == pygame.K_d:
                    moving_right = True
                if event.key == pygame.K_SPACE:
                    shoot = True
                if event.key == pygame.K_q:
                    grenade = True
                    grenade_thrown = False
                if event.key == pygame.K_w and player.is_alive and player.in_air == False:
                    player.jump = True # ở đây thay đổi giá trị trong player nên cần check player.alive
                    jump_fx.play()
                if event.key == pygame.K_ESCAPE:
                    run = False
            # Keyboard released
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    moving_left = False
                if event.key == pygame.K_d:
                    moving_right = False
                if event.key == pygame.K_SPACE:
                    shoot = False
                if event.key == pygame.K_q:
                    grenade = False
                    grenade_thrown = True

        pygame.display.update()
    pygame.quit()
