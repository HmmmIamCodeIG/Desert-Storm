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


# initializing all imported pygame modules
(numpass, numfail) = pygame.init()

print("number of modules initialized successfully:", numpass)

screenWidth = 320
screenHeight = 480
surface = pygame.display.set_mode((screenWidth, screenHeight))

BGcolor = (0, 0, 185)

clock = pygame.time.Clock()
cSpeed = 60

title = "gametest"
pygame.display.set_caption(title)

# Load both sprites
playerMovingForwardSprite = pygame.image.load("Intro/libraryofimages/FA-18moving.png").convert_alpha()
playerMovingLeftSprite = pygame.image.load("Intro/libraryofimages/FA-18movingleft.png").convert_alpha()
playerMovingRightSprite = pygame.image.load("Intro/libraryofimages/Arcade - Strikers 1945 3 Strikers 1999 - FA-18 Super Hornet(1)(1).png").convert_alpha()


player = Player(surface, playerMovingForwardSprite, playerMovingLeftSprite, playerMovingRightSprite, screenWidth/2, screenHeight/2)

def Draw():
    surface.fill(BGcolor)
    player.drawSprite()

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


    keys = pygame.key.get_pressed()
    player.Movement(keys)
    Draw()
    pygame.display.update()
    clock.tick(cSpeed)
