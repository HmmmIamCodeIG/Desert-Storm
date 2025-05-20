import pygame
import random

# Classes 

class Player():
    def __init__(self, surface, moving_forward_sprite, moving_left_sprite, moving_right_sprite, xPos, yPos):
        self.__surface = surface
        self.__sprite = moving_forward_sprite 
        self.__default_sprite = moving_forward_sprite
        self.__moving_left_sprite = moving_left_sprite
        self.__moving_right_sprite = moving_right_sprite
        self.__xPos = xPos
        self.__yPos = yPos
        self.__speed = 5

    def Movement(self, keysPressed):
        moved_left = False
        moved_right = False
        if keysPressed[pygame.K_RIGHT] or keysPressed[pygame.K_d]:
            self.__xPos += self.__speed
            moved_right = True
        elif keysPressed[pygame.K_LEFT] or keysPressed[pygame.K_a]:
            self.__xPos -= self.__speed
            moved_left = True

        self.__xPos = max(0, min(self.__xPos, self.__surface.get_width() - self.__sprite.get_width()))
        self.__yPos = self.__surface.get_height() - self.__sprite.get_height()

        if moved_left:
            self.__sprite = self.__moving_left_sprite
        elif moved_right:
            self.__sprite = self.__moving_right_sprite
        else:
            self.__sprite = self.__default_sprite  

    def getXPos(self):
        return self.__xPos

    def getYPos(self):
        return self.__yPos

    def getPos(self):
        return (self.__xPos, self.__yPos)

    def drawSprite(self):
        self.__surface.blit(self.__sprite, (self.__xPos, self.__yPos))

class PlayerBullet():
    def __init__(self, surface, sprite, xPos, yPos):
        self.__surface = surface
        self.__sprite = sprite
        self.__xPos = xPos
        self.__yPos = yPos
        self.__speed = 10

    def Movement(self):
        self.__yPos -= self.__speed

    def getXPos(self):
        return self.__xPos

    def getYPos(self):
        return self.__yPos

    def getPos(self):
        return (self.__xPos, self.__yPos)

    def drawSprite(self):
        self.__surface.blit(self.__sprite, (self.__xPos, self.__yPos))

class Enemy():
    def __init__(self, surface, sprite, xPos, yPos):
        self.__surface = surface
        self.__sprite = sprite
        self.__xPos = xPos
        self.__yPos = yPos
        self.__speed = 3

    def Movement(self):
        self.__yPos += self.__speed

    def getXPos(self):
        return self.__xPos

    def getYPos(self):
        return self.__yPos

    def getPos(self):
        return (self.__xPos, self.__yPos)
    
    def drawSprite(self):
        self.__surface.blit(self.__sprite, (self.__xPos, self.__yPos))

class EnemyBullet():
    def __init__(self, surface, sprite, xPos, yPos):
        self.__surface = surface
        self.__sprite = sprite
        self.__xPos = xPos
        self.__yPos = yPos
        self.__speed = 7

    def Movement(self):
        self.__yPos += self.__speed

    def getXPos(self):
        return self.__xPos

    def getYPos(self):
        return self.__yPos

    def drawSprite(self):
        self.__surface.blit(self.__sprite, (self.__xPos, self.__yPos))

class PlayerMissile():
    def __init__(self, surface, sprite, xPos, yPos):
        self.__surface = surface
        self.__sprite = sprite
        self.__xPos = xPos
        self.__yPos = yPos
        self.__speed = 14

    def Movement(self):
        self.__yPos -= self.__speed

    def getXPos(self):
        return self.__xPos

    def getYPos(self):
        return self.__yPos

    def drawSprite(self):
        self.__surface.blit(self.__sprite, (self.__xPos, self.__yPos))

# Initialisation 

pygame.init()

screenWidth = 320
screenHeight = 480
surface = pygame.display.set_mode((screenWidth, screenHeight))

BGcolor = (14, 0, 84)

clock = pygame.time.Clock()
cSpeed = 60

title = "gametest"
pygame.display.set_caption(title)

# Load sprites for player, bullets, missiles, enemies, and enemy bullets
playerMovingForwardSprite = pygame.image.load("Intro/libraryofimages/FA-18moving.png").convert_alpha()
playerMovingLeftSprite = pygame.image.load("Intro/libraryofimages/FA-18movingleft.png").convert_alpha()
playerMovingRightSprite = pygame.image.load("Intro/libraryofimages/FA-18movingright.png").convert_alpha()
bullet_width, bullet_height = 2, 6
playerBulletSprite = pygame.Surface((bullet_width, bullet_height), pygame.SRCALPHA)
playerBulletSprite.fill((199, 146, 0))
missile_width, missile_height = 4, 16
playerMissileSprite = pygame.Surface((missile_width, missile_height), pygame.SRCALPHA)
playerMissileSprite.fill((255, 80, 0))
enemySprite = pygame.image.load("Intro/libraryofimages/enemy.png").convert_alpha()
enemyBullet_width, enemyBullet_height = 3, 8
enemyBulletSprite = pygame.Surface((enemyBullet_width, enemyBullet_height), pygame.SRCALPHA)
enemyBulletSprite.fill((40, 255, 255))

# Create player object, starting at the bottom center of the screen
player = Player(surface, playerMovingForwardSprite, playerMovingLeftSprite, playerMovingRightSprite,
                screenWidth // 2, screenHeight - playerMovingForwardSprite.get_height())

# Lists to hold bullets, missiles, enemies, and enemy bullets
bullets = []
missiles = []
enemies = []
enemyBullets = []

# Timers for shooting and spawning
shoot_timer = 0
shoot_delay = 8               # How many frames between player shots
missile_cooldown = 0
missile_delay = 30            # Cooldown for missile (frames)
enemy_spawn_timer = 0
enemy_spawn_delay = 40        # How often to spawn an enemy (frames)
enemy_shoot_delay = 50        # How often enemies shoot (random chance)

def Draw():
    # Draw the background, then all sprites in this order: player bullets, missiles, enemies, enemy bullets, player
    surface.fill(BGcolor)
    for bullet in bullets:
        bullet.drawSprite()
    for missile in missiles:
        missile.drawSprite()
    for enemy in enemies:
        enemy.drawSprite()
    for ebullet in enemyBullets:
        ebullet.drawSprite()
    player.drawSprite()

# Main loop
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    player.Movement(keys)

    # Player Shooting (automatic) 
    shoot_timer += 1
    if shoot_timer >= shoot_delay:
        bullet_x = player.getXPos() + playerMovingForwardSprite.get_width() // 2 - bullet_width // 2
        bullet_y = player.getYPos()
        bullets.append(PlayerBullet(surface, playerBulletSprite, bullet_x, bullet_y))
        shoot_timer = 0

    # Player Missile Shooting (space bar) 
    if missile_cooldown > 0:
        missile_cooldown -= 1
    if keys[pygame.K_SPACE] and missile_cooldown == 0:
        missile_x = player.getXPos() + playerMovingForwardSprite.get_width() // 2 - missile_width // 2
        missile_y = player.getYPos()
        missiles.append(PlayerMissile(surface, playerMissileSprite, missile_x, missile_y))
        missile_cooldown = missile_delay

    # Enemy Spawning
    enemy_spawn_timer += 1
    if enemy_spawn_timer >= enemy_spawn_delay:
        # Spawn an enemy at random X position at the top
        enemy_x = random.randint(0, screenWidth - enemySprite.get_width())
        enemies.append(Enemy(surface, enemySprite, enemy_x, 0))
        enemy_spawn_timer = 0

    # Move Player Bullets
    for bullet in bullets[:]:
        bullet.Movement()
        if bullet.getYPos() < -bullet_height:
            bullets.remove(bullet) # Remove bullet if it goes off screen

    # Missiles 
    for missile in missiles[:]:
        missile.Movement()
        if missile.getYPos() < -missile_height:
            missiles.remove(missile) # Remove missile if it goes off screen

    # Enemies and Enemy Shooting 
    for enemy in enemies[:]:
        enemy.Movement()
        # Randomly allow enemy to shoot
        if random.randint(0, enemy_shoot_delay-1) == 0:
            ebullet_x = enemy.getXPos() + enemySprite.get_width() // 2 - enemyBullet_width // 2
            ebullet_y = enemy.getYPos() + enemySprite.get_height()
            enemyBullets.append(EnemyBullet(surface, enemyBulletSprite, ebullet_x, ebullet_y))
        # Remove enemy if it moves off the bottom of the screen
        if enemy.getYPos() > screenHeight:
            enemies.remove(enemy)

    # Enemy Bullets 
    for ebullet in enemyBullets[:]:
        ebullet.Movement()
        if ebullet.getYPos() > screenHeight:
            enemyBullets.remove(ebullet) # Remove enemy bullet if it goes off screen


    Draw()
    pygame.display.update()
    clock.tick(cSpeed)

pygame.quit()