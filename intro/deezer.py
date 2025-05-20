import pygame

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
        # Vertical movement
        if keysPressed[pygame.K_UP] or keysPressed[pygame.K_w]:
            self.__yPos -= self.__speed
        elif keysPressed[pygame.K_DOWN] or keysPressed[pygame.K_s]:
            self.__yPos += self.__speed
        # Horizontal movement
        if keysPressed[pygame.K_RIGHT] or keysPressed[pygame.K_d]:
            self.__xPos += self.__speed
            moved_right = True
        elif keysPressed[pygame.K_LEFT] or keysPressed[pygame.K_a]:
            self.__xPos -= self.__speed
            moved_left = True

        # Clamp position to screen boundaries
        self.__xPos = max(0, min(self.__xPos, self.__surface.get_width() - self.__sprite.get_width()))
        self.__yPos = max(0, min(self.__yPos, self.__surface.get_height() - self.__sprite.get_height()))

        # Switch sprite based on movement
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
        self.__speed = 5

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

class PlayerMissile():
    def __init__(self, surface, sprite, xPos, yPos):
        self.__surface = surface
        self.__sprite = sprite
        self.__xPos = xPos
        self.__yPos = yPos
        self.__speed = 5

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

# initializing all imported pygame modules
(numpass, numfail) = pygame.init()

print("number of modules initialized successfully:", numpass)

screenWidth = 320
screenHeight = 480
surface = pygame.display.set_mode((screenWidth, screenHeight))

BGcolor = (14, 0, 84)

clock = pygame.time.Clock()
cSpeed = 60

title = "gametest"
pygame.display.set_caption(title)

# Load both sprites
playerMovingForwardSprite = pygame.image.load("Intro/libraryofimages/FA-18moving.png").convert_alpha()
playerMovingLeftSprite = pygame.image.load("Intro/libraryofimages/FA-18movingleft.png").convert_alpha()
playerMovingRightSprite = pygame.image.load("Intro/libraryofimages/FA-18movingright.png").convert_alpha()
bullet_width = 2
bullet_height = 6
playerBulletSprite = pygame.Surface((bullet_width, bullet_height), pygame.SRCALPHA)
playerBulletSprite.fill((199, 146, 0))
playerEnemySprite = pygame.image.load("Intro/libraryofimages/enemy.png").convert_alpha()

player = Player(surface, playerMovingForwardSprite, playerMovingLeftSprite, playerMovingRightSprite, screenWidth/2, screenHeight/2)
bullets = []
shoot_timer = 0
shoot_delay = 8 # frames between shots

def Draw():
    surface.fill(BGcolor)
    for bullet in bullets:
        bullet.drawSprite()
    player.drawSprite()

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Check for shooting
    shoot_timer += 1
    if shoot_timer >= shoot_delay:
        bullet_x = player.getXPos() + playerMovingForwardSprite.get_width() // 2 - bullet_width // 2 # Center bullet on player
        bullet_y = player.getYPos()
        bullets.append(PlayerBullet(surface, playerBulletSprite, bullet_x, bullet_y)) # Create a new bullet
        shoot_timer = 0 # Reset shoot timer 

    # Update bullets
    for bullet in bullets[:]:
        bullet.Movement()
        if bullet.getYPos() < -bullet_height: 
            bullets.remove(bullet) # Remove bullet if it goes off screen


    keys = pygame.key.get_pressed()
    player.Movement(keys)
    Draw()
    pygame.display.update()
    clock.tick(cSpeed)

pygame.quit()