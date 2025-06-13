import pygame
import random
import math

### Global variables ###
class GameObject:
    # base class for all game objects
    def __init__(self, surface, sprite, xPos, yPos, speed):
        self._surface = surface
        self._sprite = sprite
        self._xPos = xPos
        self._yPos = yPos
        self._speed = speed

    def getXPos(self):
        # return the x position of the object
        return self._xPos

    def getYPos(self):
        # return the y position of the object
        return self._yPos

    def getPos(self):
        # return the position of the object as a tuple
        return (self._xPos, self._yPos)

    def drawSprite(self):
        # draw a sprite on the surface at the object's position
        self._surface.blit(self._sprite, (self._xPos, self._yPos))

    def get_rect(self):
        # get the rectangle for collision detection
        return pygame.Rect(self._xPos, self._yPos, self._sprite.get_width(), self._sprite.get_height()) 
    
    # Draw function for rendering all game objects and UI
    def Draw(surface):
        # draw all game objects on the surface 
        global bg_offset  
        # draw the bg image 
        bg_offset_int = int(bg_offset)
        BG_height = BG.get_height()
        # draw background image at the offset minus its heigh to create scrolling effect
        surface.blit(BG, (0, bg_offset_int - BG_height))
        # draw background image at the current offset
        surface.blit(BG, (0, bg_offset_int)) 
    
        for bullet in bullets:
            bullet.drawSprite()
        for missile in missiles:
            missile.drawSprite()
        for enemy in enemies:
            enemy.drawSprite()
        for ebullet in enemyBullets:
            ebullet.drawSprite()
        for exp in explosions:
            surface.blit(explosionSprite, (exp[0], exp[1]))
        player.drawSprite()
        # Draw lives 
        lives_text = font.render(f"Lives: {player_lives}", True, (255, 255, 255)) # render lives text
        surface.blit(lives_text, (5, 5)) # position lives text at the top left corner
        # Draw health 
        health_text = font.render(f"Health: {player_health}", True, (255, 255, 255)) # render health text
        surface.blit(health_text, (5, 5 + lives_text.get_height() + 5)) # position health text below lives text
        # Draw score 
        score_text = font.render(f"Score: {score}", True, (255, 255, 255)) # render score text
        surface.blit(score_text, (5, 5 + lives_text.get_height() + health_text.get_height() + 10)) # position score text below health text

class Player(GameObject):
    def __init__(self, surface, moving_forward_sprite, moving_left_sprite, moving_right_sprite, xPos, yPos):
        super().__init__(surface, moving_forward_sprite, xPos, yPos, 5) # inherit from GameObject
        self._default_sprite = moving_forward_sprite
        self._moving_left_sprite = moving_left_sprite
        self._moving_right_sprite = moving_right_sprite
            
    def Movement(self, keysPressed): # Handle player movement based on key presses
        moved_left = False
        moved_right = False
        if keysPressed[pygame.K_UP] or keysPressed[pygame.K_w]: # W or up arrow key pressed
            self._yPos -= self._speed # move up y position (movement)
        if keysPressed[pygame.K_DOWN] or keysPressed[pygame.K_s]:
            self._yPos += self._speed # move down y position (movement)
        if keysPressed[pygame.K_RIGHT] or keysPressed[pygame.K_d]:
            self._xPos += self._speed # move right x position (movement)
            moved_right = True 
        elif keysPressed[pygame.K_LEFT] or keysPressed[pygame.K_a]:
            self._xPos -= self._speed # move left x position (movement)
            moved_left = True

         # Keep player within screen bounds
        self._xPos = max(0, min(self._xPos, self._surface.get_width() - self._sprite.get_width()))
        self._yPos = max(0, min(self._yPos, self._surface.get_height() - self._sprite.get_height()))

        # update sprite based on movement
        if moved_left:
            self._sprite = self._moving_left_sprite
        elif moved_right:
            self._sprite = self._moving_right_sprite
        else:
            self._sprite = self._default_sprite

# projectile class inheriting from GameObject
class Projectile(GameObject):
    def __init__(self, surface, sprite, xPos, yPos, direction="up"): 
        super().__init__(surface, sprite, xPos, yPos, 10) # inherit from GameObject
        self.direction = direction # Set direction of the projectile

    def Movement(self): # Move projectile based on its direction
        if self.direction == "up": 
            self._yPos -= self._speed # move up y position (movement)
            if self._yPos < -self._sprite.get_height(): # if the projectile goes off screen
                self._yPos = -self._sprite.get_height() # reset position
        elif self.direction == "down":  
            self._yPos += self._speed # move down y position (movement)

    def get_rect(self): # Get the rectangle for collision detection
        return pygame.Rect(self._xPos, self._yPos, self._sprite.get_width(), self._sprite.get_height())

    def PlayerBullet(self): # Move the player bullet upwards
        self._yPos -= self._speed 
    
    def EnemyBullet(self): # Move the enemy bullet downwards
        self._yPos += self._speed 
    
    def PlayerMissile(self): # Move the player missile upwards
        self._yPos -= self._speed
        if self._yPos < -self._sprite.get_height():
            self._yPos = -self._sprite.get_height()

## Enemy class inheriting from GameObject
class Enemy(GameObject):
    def __init__(self, surface, sprite, xPos, yPos): # Constructor for Enemy
        super().__init__(surface, sprite, xPos, yPos, 3) # super calls the parent class constructor

    def Movement(self): # Move the enemy downwards
        self._yPos += self._speed

# Function to spawn an explosion at the position of an object
def spawn_explosion_at_object(obj, explosionSprite, explosions, explosion_time, explosionSound): 
    explosion_x = obj.getXPos() + obj._sprite.get_width() // 2 - explosionSprite.get_width() // 2 # Center explosion on object
    explosion_y = obj.getYPos() + obj._sprite.get_height() // 2 - explosionSprite.get_height() // 2
    explosions.append([explosion_x, explosion_y, explosion_time])
    explosionSound.play() # Play explosion sound


### Initialisation ###
pygame.init()

# Set up the display
screenWidth = 320
screenHeight = 480
surface = pygame.display.set_mode((screenWidth, screenHeight))

# background image
BG = pygame.image.load("Intro/libraryofimages/water.jpg").convert() 
BG = pygame.transform.scale(BG, (screenWidth, screenHeight))  

# fps
clock = pygame.time.Clock()
cSpeed = 60

title = "gametest"
pygame.display.set_caption(title)

# Load sprites and sounds for player, bullets, missiles, enemies, and enemy bullets
# Bullet and missile dimensions
bullet_width, bullet_height = 4, 8
missile_width, missile_height = 6, 12
enemyBullet_width, enemyBullet_height = 4, 8

# player settings
playerMovingForwardSprite = pygame.image.load("Intro/libraryofimages/FA-18moving.png").convert_alpha()
playerMovingLeftSprite = pygame.image.load("Intro/libraryofimages/FA-18movingleft.png").convert_alpha()
playerMovingRightSprite = pygame.image.load("Intro/libraryofimages/FA-18movingright.png").convert_alpha()

# Player bullet settings
playerBulletSprite = pygame.Surface((bullet_width, bullet_height), pygame.SRCALPHA)
playerBulletSprite.fill((255, 255, 0))
gunshotSound = pygame.mixer.Sound("Intro/fx/gunshot-fx-zap.wav")

# Player missile settings
playerMissileSprite = pygame.Surface((missile_width, missile_height), pygame.SRCALPHA)
playerMissileSprite.fill((255, 0, 0))
missileSound = pygame.mixer.Sound("Intro/fx/launching-missile-313226.mp3")

# Enemy settings
enemySprite = pygame.image.load("Intro/libraryofimages/enemyF-4.png").convert_alpha()
enemyBulletSprite = pygame.Surface((enemyBullet_width, enemyBullet_height), pygame.SRCALPHA)
enemyBulletSprite.fill((0, 255, 255))

# Explosion settings
explosionSprite = pygame.image.load("Intro/libraryofimages/explosion_Boom_2.png").convert_alpha()
explosionSprite = pygame.transform.scale(explosionSprite, (32, 32))  
explosionSound = pygame.mixer.Sound("Intro/fx/dry-explosion-fx.wav")

# Create player object, starting at the bottom center of the screen
player = Player(surface, playerMovingForwardSprite, playerMovingLeftSprite, playerMovingRightSprite, (screenWidth - playerMovingForwardSprite.get_width()) // 2, screenHeight - playerMovingForwardSprite.get_height())

# Lists to hold bullets, missiles, enemies, enemy bullets, explosions and audio paths
bullets = []
missiles = []
enemies = []
enemyBullets = []
explosions = []  
audiopath = {
    1: pygame.mixer.Sound("Intro/soundtrack/soundtrack1.mp3"),
    2: pygame.mixer.Sound("Intro/soundtrack/soundtrack2.mp3"),
    3: pygame.mixer.Sound("Intro/soundtrack/soundtrack3.mp3"),
    4: pygame.mixer.Sound("Intro/soundtrack/soundtrack4.mp3"),
    5: pygame.mixer.Sound("Intro/soundtrack/soundtrack5.mp3"),
    6: pygame.mixer.Sound("Intro/soundtrack/soundtrack6.mp3"),
    7: pygame.mixer.Sound("Intro/soundtrack/soundtrack7.mp3")
}

# Randomly select a soundtrack to play
soundtrack_choice = random.randint(1, 7) # randomly choose a soundtrack from 1 to 7
current_soundtrack = audiopath[soundtrack_choice]
current_soundtrack.play(-1)

# Set volume for all soundtracks
for i in range(1, 7): # in the range from 1 to 6
    audiopath[i].set_volume(0.90)
    if i == soundtrack_choice: # if the current soundtrack is the one chosen
        print(f"Current soundtrack: Soundtrack {i}")

# Fx volume
explosionSound.set_volume(0.3) 
gunshotSound.set_volume(0.1) 
missileSound.set_volume(0.5)

# Timers for shooting and spawning
score = 0
explosion_time = 30 
missile_homing_speed = 8
shoot_timer = 0
shoot_delay = 8
missile_cooldown = 0
missile_delay = 480
enemy_spawn_timer = 0
enemy_spawn_delay = 40
enemy_shoot_delay = 30
player_health = 3
player_max_health = 3
player_lives = 3
font = pygame.font.SysFont(None, 28) # Font for displaying lives, health, and score
bg_offset = 0

### Main game loop ###
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: # if the quit event is triggered 
            running = False # quit the game

    keys = pygame.key.get_pressed() # Get the state of all keys
    player.Movement(keys) # Move player based on key presses

    # Scrolling Background
    bg_offset += 1 # background increases by 1 pixel each frame
    if bg_offset >= BG.get_height(): # if the background exceeds the height of background image
        bg_offset = 0 # reset offset to 0

    # Player Shooting
    shoot_timer += 1
    if shoot_timer >= shoot_delay: 
        bullet_x = player.getXPos() + playerMovingForwardSprite.get_width() // 2 - bullet_width // 2 # center bullet on player
        bullet_y = player.getYPos() # position bullet at player's y position 
        bullets.append(Projectile(surface, playerBulletSprite, bullet_x, bullet_y)) # create a new bullet
        shoot_timer = 0 
        gunshotSound.play() # gunshot sound

    # Player Missile Shooting 
    if missile_cooldown > 0: # if cooldown timer is active 
        missile_cooldown -= 1 # Decrease cooldown timer
    if keys[pygame.K_SPACE] and missile_cooldown == 0: 
        missile_x = player.getXPos() + playerMovingForwardSprite.get_width() // 2 - missile_width // 2 # center missile on player
        missile_y = player.getYPos() # position missile at player's y position
        missiles.append(Projectile(surface, playerMissileSprite, missile_x, missile_y))
        missile_cooldown = missile_delay # reset cooldown timer
        missileSound.play()

    # Move Player Bullets
    for bullet in bullets[:]:
        bullet.Movement() 
        if bullet.getYPos() < -bullet_height: # if bullet goes off screen
            bullets.remove(bullet) # remove the list

    # Missiles homing
    for missile in missiles[:]:
        missile.Movement()
        if missile.getYPos() < -missile_height:
            missiles.remove(missile)
            continue 
        if enemies:
            # find the closest enemy to the missile
            closest_enemy = min(enemies, key=lambda e: math.hypot(
                e.getXPos() + enemySprite.get_width() // 2 - (missile.getXPos() + missile_width // 2), # distance calculation
                e.getYPos() + enemySprite.get_height() // 2 - (missile.getYPos() + missile_height // 2) 
            ))
            missile_center_x = missile.getXPos() + missile_width // 2 # center of the missile
            enemy_center_x = closest_enemy.getXPos() + enemySprite.get_width() // 2 # center of the enemy
            dx = enemy_center_x - missile_center_x # calculate the difference in x position
            if closest_enemy.getYPos() < missile.getYPos(): # if the enemy is above the missile
                if abs(dx) > missile_homing_speed: # if the distance is greater than the homing speed
                    dx = missile_homing_speed if dx > 0 else -missile_homing_speed # limit the movement to homing speed
                missile._xPos += dx # move the missile towards the enemy

    # Enemy Spawning
    enemy_spawn_timer += 1.3 
    if enemy_spawn_timer >= enemy_spawn_delay:
        enemy_x = random.randint(0, screenWidth - enemySprite.get_width()) # random x position for enemy spawn
        enemies.append(Enemy(surface, enemySprite, enemy_x, 0)) # create new enemy at the top of the screen
        enemy_spawn_timer = 0 # reset enemy spawn timer
    
    # Enemy Bullets
    for ebullet in enemyBullets[:]:
        ebullet.Movement()
        if ebullet.getYPos() > screenHeight: # if enemy bullet goes off screen
            enemyBullets.remove(ebullet) 

    # Enemies and Enemy Shooting
    for enemy in enemies[:]:
        enemy.Movement()
        if random.randint(0, enemy_shoot_delay-1) == 0:
            ebullet_x = enemy.getXPos() + enemySprite.get_width() // 2 - enemyBullet_width // 2 # center enemy bullet on enemy
            ebullet_y = enemy.getYPos() + enemySprite.get_height() 
            enemyBullets.append(Projectile(surface, enemyBulletSprite, ebullet_x, ebullet_y, direction="down")) # create a new enemy bullet
        if enemy.getYPos() > screenHeight: # if the enemy goes off screen
            enemies.remove(enemy) 

    # collisions with player
    player_rect = player.get_rect()
    for enemy in enemies[:]:
        enemy_rect = enemy.get_rect() # get the rectangle for collision detection
        if player_rect.colliderect(enemy_rect):
            enemies.remove(enemy) # delete enemy from the list
            player_health -= 3 # reduce player health by 3
            spawn_explosion_at_object(enemy, explosionSprite, explosions, explosion_time, explosionSound)
    for ebullet in enemyBullets[:]:
        ebullet_rect = ebullet.get_rect() 
        if player_rect.colliderect(ebullet_rect): # check for collision between player and enemy bullet
            enemyBullets.remove(ebullet) # remove the ebullet from the list
            player_health -= 1 # reduce by 1

    # collisions with enemies
    for missile in missiles[:]:
        missile_rect = missile.get_rect() # get the rectangle for collision detection
        for enemy in enemies[:]:
            enemy_rect = enemy.get_rect() # get the rectangle for collision detection
            if missile_rect.colliderect(enemy_rect):
                if missile in missiles:
                    missiles.remove(missile) # remove the missile from the list
                if enemy in enemies:
                    spawn_explosion_at_object(enemy, explosionSprite, explosions, explosion_time, explosionSound) 
                    # spawn explosion at enemy position
                    enemies.remove(enemy)
                    score += 1 # increase score
    for bullet in bullets[:]:
        bullet_rect = bullet.get_rect() # get the rectangle for collision detection
        for enemy in enemies[:]:
            enemy_rect = enemy.get_rect() 
            if bullet_rect.colliderect(enemy_rect): # check for collision between bullet and enemy
                if bullet in bullets: # remove the bullet from the list
                    bullets.remove(bullet)
                if enemy in enemies:
                    spawn_explosion_at_object(enemy, explosionSprite, explosions, explosion_time, explosionSound)
                    # spawn explosion at enemy position
                    enemies.remove(enemy)
                    score += 1

    # player health
    if player_health <= 0:
        spawn_explosion_at_object(player, explosionSprite, explosions, explosion_time, explosionSound) # spawn explosion at player position
        player._xPos = (screenWidth - playerMovingForwardSprite.get_width()) // 2 # reset player position to center
        player._yPos = screenHeight - playerMovingForwardSprite.get_height()
        player_lives -= 1 # reduce player lives
        player_health = player_max_health # reset player health
        if player_lives <= 0: # if player has no lives left
            print("Game Over")
            running = False

    # Update and remove finished explosions
    for exp in explosions[:]:
        exp[2] -= 1
        if exp[2] <= 0:
            explosions.remove(exp)
    GameObject.Draw(surface)
    pygame.display.update()
    clock.tick(cSpeed)

pygame.quit()