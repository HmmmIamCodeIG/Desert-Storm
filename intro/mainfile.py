import pygame
import random
import math

### Global variables and Classes ###

# Base class for all objects that appear in the game (player, enemy, projectile, etc.)
class GameObject:
    # Initialise the object with its drawing surface, image, position, and speed
    def __init__(self, surface, sprite, xPos, yPos, speed):
        self._surface = surface # pygame Surface to draw on
        self._sprite = sprite # pygame Surface for the sprite image
        self._xPos = xPos # X coordinate on screen
        self._yPos = yPos # Y coordinate on screen
        self._speed = speed # Speed to move player

    def getXPos(self):
        # Return the object's current X position
        return self._xPos

    def getYPos(self):
        # Return the object's current Y position
        return self._yPos

    def getPos(self):
        # Return the object's current (X, Y) position as a tuple
        return (self._xPos, self._yPos)

    def drawSprite(self):
        # Draw the object's sprite image at its current position on the given surface
        self._surface.blit(self._sprite, (self._xPos, self._yPos))

    def get_rect(self):
        # Get a pygame.Rect representing this object's screen area (used for collisions)
        return pygame.Rect(self._xPos, self._yPos, self._sprite.get_width(), self._sprite.get_height()) 

    @staticmethod
    def Draw(surface):
        # Draw all game elements, including background, bullets, enemies, explosions, and player HUD info
        global bg_offset, BG, bullets, missiles, enemies, enemyBullets, explosions, explosionSprite, player, font, score

        # Draw the scrolling background (twice for seamless vertical looping)
        bg_offset_int = int(bg_offset) 
        BG_height = BG.get_height()
        surface.blit(BG, (0, bg_offset_int - BG_height)) 
        surface.blit(BG, (0, bg_offset_int)) 

        # Draw all player bullets
        for bullet in bullets:
            bullet.drawSprite()
        # Draw all player missiles
        for missile in missiles:
            missile.drawSprite()
        # Draw all enemies
        for enemy in enemies:
            enemy.drawSprite()
        # Draw all enemy bullets
        for ebullet in enemyBullets:
            ebullet.drawSprite()
        # Draw all explosions
        for exp in explosions:
            surface.blit(explosionSprite, (exp[0], exp[1]))
        # Draw player sprite on top of everything
        player.drawSprite()
        
        # Draw player lives count on screen
        lives_text = font.render(f"Lives: {player._lives}", True, (255, 255, 255))
        surface.blit(lives_text, (5, 5))
        # Draw player health just under the lives text
        health_text = font.render(f"Health: {player._health}", True, (255, 255, 255))
        surface.blit(health_text, (5, 5 + lives_text.get_height() + 5))
        # Draw player score just under the health text
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        surface.blit(score_text, (5, 5 + lives_text.get_height() + health_text.get_height() + 10))

# Player class inherits from GameObject and represents the player aircraft
class Player(GameObject):
    def __init__(self, surface, moving_forward_sprite, moving_left_sprite, moving_right_sprite, xPos, yPos):
        # Initialise with sprites for each movement direction and basic player stats
        super().__init__(surface, moving_forward_sprite, xPos, yPos, 5)
        self._default_sprite = moving_forward_sprite # Sprite for forward movement
        self._moving_left_sprite = moving_left_sprite # Sprite for moving left
        self._moving_right_sprite = moving_right_sprite # Sprite for moving right
        self._health = 3 # Player starting health
        self._max_health = 3 # Max health
        self._lives = 3 # Player lives count
        self._shoot_timer = 0 # Timer for bullet fire rate
        self._shoot_delay = 8 # Delay (frames) between allowed shots
        self._missile_cooldown = 0 # Timer for missile fire rate
        self._missile_delay = 480 # Delay (frames) between allowed missile fires
        self._score = 0 # Player score
        self._last_shoot_key = False # State for continuous shooting

    def Movement(self, keysPressed):
        # Handle player movement and change the sprite depending on direction
        moved_left = False
        moved_right = False

        # Move up if up arrow or W pressed
        if keysPressed[pygame.K_UP] or keysPressed[pygame.K_w]:
            self._yPos -= self._speed
        # Move down if down arrow or S pressed
        elif keysPressed[pygame.K_DOWN] or keysPressed[pygame.K_s]:
            self._yPos += self._speed
        # Move right if right arrow or D pressed, and set sprite accordingly
        elif keysPressed[pygame.K_RIGHT] or keysPressed[pygame.K_d]:
            self._xPos += self._speed
            moved_right = True 
        # Move left if left arrow or A pressed, and set sprite accordingly
        elif keysPressed[pygame.K_LEFT] or keysPressed[pygame.K_a]:
            self._xPos -= self._speed
            moved_left = True

        # Clamp position so player stays within screen bounds
        self._xPos = max(0, min(self._xPos, self._surface.get_width() - self._sprite.get_width()))
        self._yPos = max(0, min(self._yPos, self._surface.get_height() - self._sprite.get_height()))

        # Select appropriate sprite based on movement direction
        if moved_left:
            self._sprite = self._moving_left_sprite 
        elif moved_right:
            self._sprite = self._moving_right_sprite
        else:
            self._sprite = self._default_sprite

    def update_health(self, delta, explosions, explosionSprite, explosion_time, explosionSound):
        # Change player's health by delta, handle losing lives and game over
        self._health += delta
        if self._health <= 0: 
            # Spawn an explosion at the player's position, play sound, and lose a life
            spawn_explosion_at_object(self, explosionSprite, explosions, explosion_time, explosionSound)
            playerLoseLifeSound.play()
            self._lives -= 1
            if self._lives > 0:
                # Respawn player: restore health and place at bottom center
                self._health = self._max_health
                self._xPos = (self._surface.get_width() - self._sprite.get_width()) // 2
                self._yPos = self._surface.get_height() - self._sprite.get_height()
            else:
                # Game over: show endcard, pause, and quit
                self._surface.blit(endcard, (0, 0))
                pygame.display.update()
                pygame.time.delay(5000)
                print("Game Over")
                pygame.event.post(pygame.event.Event(pygame.QUIT))

    def shoot(self, keys, bullets, bulletSprite, bullet_width, gunshotSound):
        # Handle shooting bullets
        if self._shoot_timer < self._shoot_delay:
            self._shoot_timer += 1
        if self._shoot_timer >= self._shoot_delay:
            bullet_x = self.getXPos() + self._sprite.get_width() // 2 - bullet_width // 2
            bullet_y = self.getYPos()
            bullets.append(Projectile(self._surface, bulletSprite, bullet_x, bullet_y))
            self._shoot_timer = 0
            gunshotSound.play()

    def shoot_missile(self, keys, missiles, missileSprite, missile_width, missile_height, missileSound):
        # Handle firing missiles
        if self._missile_cooldown > 0:
            self._missile_cooldown -= 1
        # press spacebar and missile will fire. missile has cooldown
        if keys[pygame.K_SPACE] and self._missile_cooldown == 0:
            missile_x = self.getXPos() + self._sprite.get_width() // 2 - missile_width // 2
            missile_y = self.getYPos()
            missiles.append(Projectile(self._surface, missileSprite, missile_x, missile_y))
            self._missile_cooldown = self._missile_delay
            missileSound.play()

    def handle_collisions(self, enemies, enemyBullets, explosions, explosionSprite, explosion_time, explosionSound):
        # Handle collisions between player and enemies/bullets
        player_rect = self.get_rect()
        # Check collision with enemies
        for enemy in enemies[:]:
            if player_rect.colliderect(enemy.get_rect()):
                enemies.remove(enemy)
                self.update_health(-3, explosions, explosionSprite, explosion_time, explosionSound)
        # Check collision with enemy bullets
        for ebullet in enemyBullets[:]:
            if player_rect.colliderect(ebullet.get_rect()):
                enemyBullets.remove(ebullet)
                self.update_health(-1, explosions, explosionSprite, explosion_time, explosionSound)

# Projectile class for all bullets and missiles (player and enemy)
class Projectile(GameObject):
    def __init__(self, surface, sprite, xPos, yPos, direction="up"): 
        # Direction is "up" for player, "down" for enemy projectiles
        super().__init__(surface, sprite, xPos, yPos, 10)
        self._direction = direction

    def Movement(self):
        # Move the projectile up (player) or down (enemy)
        if self._direction == "up": 
            self._yPos -= self._speed
            # Clamp position off screen if gone
            if self._yPos < -self._sprite.get_height():
                self._yPos = -self._sprite.get_height()
        elif self._direction == "down":  
            self._yPos += self._speed

    def get_rect(self):
        # Get the rect for collision detection
        return pygame.Rect(self._xPos, self._yPos, self._sprite.get_width(), self._sprite.get_height())

# Enemy class for enemy aircraft
class Enemy(GameObject):    
    def __init__(self, surface, sprite, xPos, yPos):
        # Initialise enemy at position, set downward speed
        super().__init__(surface, sprite, xPos, yPos, 3)

    def update(self, enemies, missiles, bullets, enemyBullets, enemyBulletSprite, enemyBullet_width, enemyBullet_height, explosionSprite, explosions, explosion_time, explosionSound, screenHeight, score_ref):
        # Update enemy position, shoot, and handle collisions
        self.move_and_shoot(enemyBullets, enemyBulletSprite, enemyBullet_width, enemyBullet_height)
        self.handle_collisions(enemies, missiles, bullets, explosionSprite, explosions, explosion_time, explosionSound, score_ref)
        # Remove enemy if it moves off the bottom of the screen
        if self.getYPos() > screenHeight and self in enemies:
            enemies.remove(self)

    def move_and_shoot(self, enemyBullets, enemyBulletSprite, enemyBullet_width, enemyBullet_height):
        # Move enemy downward
        self._yPos += self._speed
        # Enemy randomly shoots bullets downwards
        if random.random() < 0.02:
            bullet_x = self.getXPos() + self._sprite.get_width() // 2 - enemyBullet_width // 2
            bullet_y = self.getYPos() + self._sprite.get_height()
            enemyBullets.append(Projectile(self._surface, enemyBulletSprite, bullet_x, bullet_y, direction="down"))

    def handle_collisions(self, enemies, missiles, bullets, explosionSprite, explosions, explosion_time, explosionSound, score_ref):
        # Handle collision with missiles and bullets
        enemy_rect = self.get_rect()
        # Collision with missile
        for missile in missiles[:]:
            if missile.get_rect().colliderect(enemy_rect):
                if missile in missiles:
                    missiles.remove(missile)
                spawn_explosion_at_object(self, explosionSprite, explosions, explosion_time, explosionSound)
                if self in enemies:
                    enemies.remove(self)
                score_ref[0] += 1
                return
        # Collision with bullet
        for bullet in bullets[:]:
            if bullet.get_rect().colliderect(enemy_rect):
                if bullet in bullets:
                    bullets.remove(bullet)
                spawn_explosion_at_object(self, explosionSprite, explosions, explosion_time, explosionSound)
                if self in enemies:
                    enemies.remove(self)
                score_ref[0] += 1
                return

### Functions ###

def spawn_explosion_at_object(obj, explosionSprite, explosions, explosion_time, explosionSound): 
    # Spawn an explosion centered at the object's position and play the explosion sound
    explosion_x = obj.getXPos() + obj._sprite.get_width() // 2 - explosionSprite.get_width() // 2
    explosion_y = obj.getYPos() + obj._sprite.get_height() // 2 - explosionSprite.get_height() // 2
    explosions.append([explosion_x, explosion_y, explosion_time])
    explosionSound.play()

### Initialisation ###

pygame.init()  # Initialise all imported pygame modules

# Set up the display window (320x480 pixels)
screenWidth = 320
screenHeight = 480
surface = pygame.display.set_mode((screenWidth, screenHeight))

# Load and scale the background image for the game
BG = pygame.image.load("Intro/libraryofimages/water.jpg").convert() 
BG = pygame.transform.scale(BG, (screenWidth, screenHeight))  

# Set up the game clock for controlling frame rate (FPS)
clock = pygame.time.Clock()
cSpeed = 60  # Target frames per second

# Set the window title bar text
title = "gametest"
pygame.display.set_caption(title)

# Define bullet and missile sprite sizes
bullet_width, bullet_height = 4, 8
missile_width, missile_height = 6, 12
enemyBullet_width, enemyBullet_height = 4, 8

# Load player sprites (for forward, left, and right movement)
playerMovingForwardSprite = pygame.image.load("Intro/libraryofimages/FA-18moving.png").convert_alpha()
playerMovingLeftSprite = pygame.image.load("Intro/libraryofimages/FA-18movingleft.png").convert_alpha()
playerMovingRightSprite = pygame.image.load("Intro/libraryofimages/FA-18movingright.png").convert_alpha()
playerLoseLifeSound = pygame.mixer.Sound("Intro/fx/805693__edimar_ramide__death2.wav")

# Create a sprite for player bullets and load gunshot sound
playerBulletSprite = pygame.Surface((bullet_width, bullet_height), pygame.SRCALPHA)
playerBulletSprite.fill((255, 255, 0))
gunshotSound = pygame.mixer.Sound("Intro/fx/gunshot-fx-zap.wav")

# Create a sprite for player missiles and load missile launch sound
playerMissileSprite = pygame.Surface((missile_width, missile_height), pygame.SRCALPHA)
playerMissileSprite.fill((255, 0, 0))
missileSound = pygame.mixer.Sound("Intro/fx/launching-missile-313226.mp3")

# Load enemy sprite and create sprite for enemy bullets
enemySprite = pygame.image.load("Intro/libraryofimages/enemyF-4.png").convert_alpha()
enemyBulletSprite = pygame.Surface((enemyBullet_width, enemyBullet_height), pygame.SRCALPHA)
enemyBulletSprite.fill((0, 255, 255))

# Load explosion sprite, scale it, and load explosion sound
explosionSprite = pygame.image.load("Intro/libraryofimages/explosion_Boom_2.png").convert_alpha()
explosionSprite = pygame.transform.scale(explosionSprite, (32, 32))  
explosionSound = pygame.mixer.Sound("Intro/fx/dry-explosion-fx.wav")

# Load end screen image and scale to screen size
endcard = pygame.image.load("intro/libraryofimages/dead.png")
endcard = pygame.transform.scale(endcard, (screenWidth, screenHeight))

# Create the player object, positioned at the bottom center of the screen
player = Player(surface, playerMovingForwardSprite, playerMovingLeftSprite, playerMovingRightSprite, (screenWidth - playerMovingForwardSprite.get_width()) // 2, screenHeight - playerMovingForwardSprite.get_height())

# Lists to hold all in-game objects for easy management
bullets = [] # List of player bullets
missiles = [] # List of player missiles
enemies = [] # List of All enemy planes
enemyBullets = [] # List of All enemy bullets
explosions = [] #List of All explosions (active)

# Dictionary mapping soundtrack numbers to loaded pygame Sound objects
audiopath = {
    1: pygame.mixer.Sound("Intro/soundtrack/soundtrack1.mp3"),
    2: pygame.mixer.Sound("Intro/soundtrack/soundtrack2.mp3"),
    3: pygame.mixer.Sound("Intro/soundtrack/soundtrack3.mp3"),
    4: pygame.mixer.Sound("Intro/soundtrack/soundtrack4.mp3"),
    5: pygame.mixer.Sound("Intro/soundtrack/soundtrack5.mp3"),
    6: pygame.mixer.Sound("Intro/soundtrack/soundtrack6.mp3"),
    7: pygame.mixer.Sound("Intro/soundtrack/soundtrack7.mp3")
}

# Randomly choose one soundtrack and start playing it in a loop
soundtrack_choice = random.randint(1, 7)
current_soundtrack = audiopath[soundtrack_choice]
current_soundtrack.play(-1)  # -1 means loop forever

# Set all soundtrack volumes and print the currently playing one
for i in range(1, 8):
    audiopath[i].set_volume(0.60)
    if i == soundtrack_choice:
        print(f"Current soundtrack: Soundtrack {i}")

# Set volume for sound effects
explosionSound.set_volume(0.1) 
gunshotSound.set_volume(0.1) 
missileSound.set_volume(0.5)
playerLoseLifeSound.set_volume(1)

# Initialise game state variables
score = 0 # Player score
explosion_time = 30 # Frames an explosion lasts
missile_homing_speed = 8 # Max speed for missile homing
enemy_spawn_timer = 0 # Timer for next enemy spawn
enemy_spawn_delay = 40 # Frames between enemy spawns
font = pygame.font.SysFont(None, 28) # Font for HUD
bg_offset = 0 # Scrolling background offset

### Main game loop ###
running = True

while running:
    # Process all events (keyboard, window close, etc.)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False   # Exit loop if window is closed

    # Get state of all keys (pressed or not)
    keys = pygame.key.get_pressed()
    # Handle player movement
    player.Movement(keys)
    # Check for collisions with enemies/enemy bullets
    player.handle_collisions(enemies, enemyBullets, explosions, explosionSprite, explosion_time, explosionSound) 
    # Player auto-shoots bullets
    player.shoot(keys, bullets, playerBulletSprite, bullet_width, gunshotSound)
    # Player fires missile if space is pressed and not on cooldown
    player.shoot_missile(keys, missiles, playerMissileSprite, missile_width, missile_height, missileSound)

    # Scroll the background by incrementing offset, looping when past image height
    bg_offset += 1
    if bg_offset >= BG.get_height():
        bg_offset = 0

    # Move all player bullets and remove those that go off the top of the screen
    for bullet in bullets[:]:
        bullet.Movement()
        if bullet.getYPos() < -bullet_height:
            bullets.remove(bullet)

    # Move all missiles, handle homing and remove if off-screen
    for missile in missiles[:]:
        missile.Movement()
        if missile.getYPos() < -missile_height:
            missiles.remove(missile)
            continue 
        # If there are enemies, home in on the closest one
        if enemies:
            # Find the closest enemy by distance
            closest_enemy = min(enemies, key=lambda e: math.hypot( 
                e.getXPos() + enemySprite.get_width() // 2 - (missile.getXPos() + missile_width // 2), 
                e.getYPos() + enemySprite.get_height() // 2 - (missile.getYPos() + missile_height // 2) 
            ))
            # Calculate horizontal distance to closest enemy's center
            missile_center_x = missile.getXPos() + missile_width // 2
            enemy_center_x = closest_enemy.getXPos() + enemySprite.get_width() // 2
            dx = enemy_center_x - missile_center_x
            # Only home if enemy is above missile
            if closest_enemy.getYPos() < missile.getYPos():
                # Cap the homing adjustment speed per frame
                if abs(dx) > missile_homing_speed:
                    dx = missile_homing_speed if dx > 0 else -missile_homing_speed
                missile._xPos += dx

    # Handle enemy spawning based on timer
    enemy_spawn_timer += 1.3 
    if enemy_spawn_timer >= enemy_spawn_delay:
        enemy_x = random.randint(0, screenWidth - enemySprite.get_width())
        enemies.append(Enemy(surface, enemySprite, enemy_x, 0))
        enemy_spawn_timer = 0
    
    # Move all enemy bullets and remove those off bottom of screen
    for ebullet in enemyBullets[:]:
        ebullet.Movement()
        if ebullet.getYPos() > screenHeight:
            enemyBullets.remove(ebullet)

    # Update all enemies (move, shoot, handle collisions)
    score_ref = [score]  # Mutable list to allow score updates by reference
    for enemy in enemies[:]:
        enemy.update(
            enemies, missiles, bullets,
            enemyBullets, enemyBulletSprite, enemyBullet_width, enemyBullet_height,
            explosionSprite, explosions, explosion_time, explosionSound,
            screenHeight, score_ref
        )
    score = score_ref[0]

    # Update all explosions (reduce the timer and remove explosions)
    for exp in explosions[:]:
        exp[2] -= 1 
        if exp[2] <= 0:
            explosions.remove(exp)

    # Draw everything and update display
    GameObject.Draw(surface)
    pygame.display.update()
    clock.tick(cSpeed)  # T FPS

pygame.quit()  # Clean up and close the game window