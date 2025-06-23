import pygame
import random
import math

### Global variables and Classes ###

# Base class for all game objects in the game (player, enemy, projectile, etc.)
class GameObject:
    # Initialize with surface to draw on, sprite image, position, and speed
    def __init__(self, surface, sprite, xPos, yPos, speed):
        self._surface = surface
        self._sprite = sprite
        self._xPos = xPos
        self._yPos = yPos
        self._speed = speed

    def getXPos(self):
        return self._xPos

    def getYPos(self):
        return self._yPos

    def getPos(self):
        return (self._xPos, self._yPos)

    # Draw the object's sprite at its current position
    def drawSprite(self):
        self._surface.blit(self._sprite, (self._xPos, self._yPos))

    # Get the rectangle representing the object's position and size (for collision)
    def get_rect(self):
        return pygame.Rect(self._xPos, self._yPos, self._sprite.get_width(), self._sprite.get_height()) 

    # Static method to draw everything on the screen
    @staticmethod
    def Draw(surface):
        # Use global variables for drawing all game elements
        global bg_offset, BG, bullets, missiles, enemies, enemyBullets, explosions, explosionSprite, player, font, score
        # Draw the scrolling background, twice for seamless looping
        bg_offset_int = int(bg_offset) 
        BG_height = BG.get_height()
        surface.blit(BG, (0, bg_offset_int - BG_height)) 
        surface.blit(BG, (0, bg_offset_int)) 

        # Draw all bullets, missiles, enemies, enemy bullets, and explosions
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
        # Draw player sprite
        player.drawSprite()
        # Draw player lives
        lives_text = font.render(f"Lives: {player.lives}", True, (255, 255, 255))
        surface.blit(lives_text, (5, 5))
        # Draw player health
        health_text = font.render(f"Health: {player.health}", True, (255, 255, 255))
        surface.blit(health_text, (5, 5 + lives_text.get_height() + 5))
        # Draw player score
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        surface.blit(score_text, (5, 5 + lives_text.get_height() + health_text.get_height() + 10))

# Player class inherits from GameObject
class Player(GameObject):
    def __init__(self, surface, moving_forward_sprite, moving_left_sprite, moving_right_sprite, xPos, yPos):
        # Initialize player with sprites for different movement directions
        super().__init__(surface, moving_forward_sprite, xPos, yPos, 5)
        self._default_sprite = moving_forward_sprite
        self._moving_left_sprite = moving_left_sprite
        self._moving_right_sprite = moving_right_sprite
        self.health = 3
        self.max_health = 3
        self.lives = 3
        self.shoot_timer = 0
        self.shoot_delay = 8  # Ticks between allowed shots
        self.missile_cooldown = 0
        self.missile_delay = 480  # Delay between missile fires
        self.score = 0
        self.last_shoot_key = False  # Track the last shoot key 

    # Handle player movement and sprite selection based on keys pressed
    def Movement(self, keysPressed):
        moved_left = False
        moved_right = False
        # Move player up
        if keysPressed[pygame.K_UP] or keysPressed[pygame.K_w]:
            self._yPos -= self._speed
        # Move player down
        elif keysPressed[pygame.K_DOWN] or keysPressed[pygame.K_s]:
            self._yPos += self._speed
        # Move player right
        elif keysPressed[pygame.K_RIGHT] or keysPressed[pygame.K_d]:
            self._xPos += self._speed
            moved_right = True 
        # Move player left
        elif keysPressed[pygame.K_LEFT] or keysPressed[pygame.K_a]:
            self._xPos -= self._speed
            moved_left = True

        # Keep player within screen bounds
        self._xPos = max(0, min(self._xPos, self._surface.get_width() - self._sprite.get_width()))
        self._yPos = max(0, min(self._yPos, self._surface.get_height() - self._sprite.get_height()))

        # Update sprite based on movement direction
        if moved_left:
            self._sprite = self._moving_left_sprite
        elif moved_right:
            self._sprite = self._moving_right_sprite
        else:
            self._sprite = self._default_sprite

    # Update health, handle death and respawn, and spawn explosion
    def update_health(self, delta, explosions, explosionSprite, explosion_time, explosionSound):
        self.health += delta
        if self.health <= 0:
            spawn_explosion_at_object(self, explosionSprite, explosions, explosion_time, explosionSound)
            self.lives -= 1
            if self.lives > 0:
                # Respawn with full health, reposition to bottom center
                self.health = self.max_health
                self._xPos = (self._surface.get_width() - self._sprite.get_width()) // 2
                self._yPos = self._surface.get_height() - self._sprite.get_height()
            else:
                # Game Over: post QUIT event to exit main loop
                print("Game Over")
                pygame.event.post(pygame.event.Event(pygame.QUIT))

    # Handle shooting regular bullets
    def shoot(self, keys, bullets, bulletSprite, bullet_width, gunshotSound, auto_shoot=True):
        # Only shoot if enough time has passed since last shot
        if self.shoot_timer < self.shoot_delay:
            self.shoot_timer += 1
        # Shoot if auto_shoot is True or Z key pressed
        if (auto_shoot) and self.shoot_timer >= self.shoot_delay:
            bullet_x = self.getXPos() + self._sprite.get_width() // 2 - bullet_width // 2
            bullet_y = self.getYPos()
            bullets.append(Projectile(self._surface, bulletSprite, bullet_x, bullet_y))
            self.shoot_timer = 0
            gunshotSound.play()

    # Handle firing missiles (spacebar)
    def shoot_missile(self, keys, missiles, missileSprite, missile_width, missile_height, missileSound):
        # Missile cooldown logic
        if self.missile_cooldown > 0:
            self.missile_cooldown -= 1
        # Shoot missile if space pressed and not on cooldown
        if keys[pygame.K_SPACE] and self.missile_cooldown == 0:
            missile_x = self.getXPos() + self._sprite.get_width() // 2 - missile_width // 2
            missile_y = self.getYPos()
            missiles.append(Projectile(self._surface, missileSprite, missile_x, missile_y))
            self.missile_cooldown = self.missile_delay
            missileSound.play()

    # Handle collisions with enemies and enemy bullets
    def handle_collisions(self, enemies, enemyBullets, explosions, explosionSprite, explosion_time, explosionSound):
        player_rect = self.get_rect()
        # Collide with enemies
        for enemy in enemies[:]:
            if player_rect.colliderect(enemy.get_rect()):
                enemies.remove(enemy)
                self.update_health(-3, explosions, explosionSprite, explosion_time, explosionSound)
                spawn_explosion_at_object(enemy, explosionSprite, explosions, explosion_time, explosionSound)
        # Collide with enemy bullets
        for ebullet in enemyBullets[:]:
            if player_rect.colliderect(ebullet.get_rect()):
                enemyBullets.remove(ebullet)
                self.update_health(-1, explosions, explosionSprite, explosion_time, explosionSound)

# Projectile class for player and enemy bullets and missiles
class Projectile(GameObject):
    def __init__(self, surface, sprite, xPos, yPos, direction="up"): 
        super().__init__(surface, sprite, xPos, yPos, 10)
        self.direction = direction

    # Move projectile up (player) or down (enemy)
    def Movement(self):
        if self.direction == "up": 
            self._yPos -= self._speed
            if self._yPos < -self._sprite.get_height():
                self._yPos = -self._sprite.get_height()
        elif self.direction == "down":  
            self._yPos += self._speed

    def get_rect(self):
        return pygame.Rect(self._xPos, self._yPos, self._sprite.get_width(), self._sprite.get_height())

# Enemy class for enemy aircraftclass Enemy(GameObject):
class Enemy(GameObject):    
    def __init__(self, surface, sprite, xPos, yPos):
        super().__init__(surface, sprite, xPos, yPos, 3)

    def update(self, enemies, missiles, bullets, enemyBullets, enemyBulletSprite, enemyBullet_width, enemyBullet_height,
               explosionSprite, explosions, explosion_time, explosionSound, screenHeight, score_ref):
        self.move_and_shoot(enemyBullets, enemyBulletSprite, enemyBullet_width, enemyBullet_height)
        self.handle_collisions(enemies, missiles, bullets, explosionSprite, explosions, explosion_time, explosionSound, score_ref)
        if self.getYPos() > screenHeight and self in enemies:
            enemies.remove(self)

    def move_and_shoot(self, enemyBullets, enemyBulletSprite, enemyBullet_width, enemyBullet_height):
        self._yPos += self._speed
        if random.random() < 0.02:
            bullet_x = self.getXPos() + self._sprite.get_width() // 2 - enemyBullet_width // 2
            bullet_y = self.getYPos() + self._sprite.get_height()
            enemyBullets.append(Projectile(self._surface, enemyBulletSprite, bullet_x, bullet_y, direction="down"))

    def handle_collisions(self, enemies, missiles, bullets, explosionSprite, explosions, explosion_time, explosionSound, score_ref):
        enemy_rect = self.get_rect()
        for missile in missiles[:]:
            if missile.get_rect().colliderect(enemy_rect):
                if missile in missiles:
                    missiles.remove(missile)
                spawn_explosion_at_object(self, explosionSprite, explosions, explosion_time, explosionSound)
                if self in enemies:
                    enemies.remove(self)
                score_ref[0] += 1
                return
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

# Spawn explosion at an object's position and play sound
def spawn_explosion_at_object(obj, explosionSprite, explosions, explosion_time, explosionSound): 
    explosion_x = obj.getXPos() + obj._sprite.get_width() // 2 - explosionSprite.get_width() // 2
    explosion_y = obj.getYPos() + obj._sprite.get_height() // 2 - explosionSprite.get_height() // 2
    explosions.append([explosion_x, explosion_y, explosion_time])
    explosionSound.play()

### Initialisation ###

pygame.init()

# Set up the display window
screenWidth = 320
screenHeight = 480
surface = pygame.display.set_mode((screenWidth, screenHeight))

# Load and scale the background image
BG = pygame.image.load("Intro/libraryofimages/water.jpg").convert() 
BG = pygame.transform.scale(BG, (screenWidth, screenHeight))  

# Set up the game clock and frames per second
clock = pygame.time.Clock()
cSpeed = 60

# Set the window title
title = "gametest"
pygame.display.set_caption(title)

# Load sprites and sounds for player, bullets, missiles, enemies, and enemy bullets
bullet_width, bullet_height = 4, 8
missile_width, missile_height = 6, 12
enemyBullet_width, enemyBullet_height = 4, 8

# Player sprites for different movement states
playerMovingForwardSprite = pygame.image.load("Intro/libraryofimages/FA-18moving.png").convert_alpha()
playerMovingLeftSprite = pygame.image.load("Intro/libraryofimages/FA-18movingleft.png").convert_alpha()
playerMovingRightSprite = pygame.image.load("Intro/libraryofimages/FA-18movingright.png").convert_alpha()

# Player bullet and sound
playerBulletSprite = pygame.Surface((bullet_width, bullet_height), pygame.SRCALPHA)
playerBulletSprite.fill((255, 255, 0))
gunshotSound = pygame.mixer.Sound("Intro/fx/gunshot-fx-zap.wav")

# Player missile and sound
playerMissileSprite = pygame.Surface((missile_width, missile_height), pygame.SRCALPHA)
playerMissileSprite.fill((255, 0, 0))
missileSound = pygame.mixer.Sound("Intro/fx/launching-missile-313226.mp3")

# Enemy sprite and enemy bullet
enemySprite = pygame.image.load("Intro/libraryofimages/enemyF-4.png").convert_alpha()
enemyBulletSprite = pygame.Surface((enemyBullet_width, enemyBullet_height), pygame.SRCALPHA)
enemyBulletSprite.fill((0, 255, 255))

# Explosion sprite and sound
explosionSprite = pygame.image.load("Intro/libraryofimages/explosion_Boom_2.png").convert_alpha()
explosionSprite = pygame.transform.scale(explosionSprite, (32, 32))  
explosionSound = pygame.mixer.Sound("Intro/fx/dry-explosion-fx.wav")

# Instantiate the player object at bottom center
player = Player(surface, playerMovingForwardSprite, playerMovingLeftSprite, playerMovingRightSprite, (screenWidth - playerMovingForwardSprite.get_width()) // 2, screenHeight - playerMovingForwardSprite.get_height())

# Create empty lists for bullets, missiles, enemies, enemy bullets, and explosions
bullets = []
missiles = []
enemies = []
enemyBullets = []
explosions = []  

# Dictionary to hold different background music tracks
audiopath = {
    1: pygame.mixer.Sound("Intro/soundtrack/soundtrack1.mp3"),
    2: pygame.mixer.Sound("Intro/soundtrack/soundtrack2.mp3"),
    3: pygame.mixer.Sound("Intro/soundtrack/soundtrack3.mp3"),
    4: pygame.mixer.Sound("Intro/soundtrack/soundtrack4.mp3"),
    5: pygame.mixer.Sound("Intro/soundtrack/soundtrack5.mp3"),
    6: pygame.mixer.Sound("Intro/soundtrack/soundtrack6.mp3"),
    7: pygame.mixer.Sound("Intro/soundtrack/soundtrack7.mp3")
}

# Randomly select and play a soundtrack
soundtrack_choice = random.randint(1, 7)
current_soundtrack = audiopath[soundtrack_choice]
current_soundtrack.play(-1)  # Loop indefinitely

# Set volume for each soundtrack and print which one is playing
for i in range(1, 8):
    audiopath[i].set_volume(0.60)
    if i == soundtrack_choice:
        print(f"Current soundtrack: Soundtrack {i}")

# Set volumes for sound effects
explosionSound.set_volume(0.3) 
gunshotSound.set_volume(0.1) 
missileSound.set_volume(0.5)

# Initialize score, explosion duration, missile homing speed, enemy spawn timings, and font
score = 0
explosion_time = 30 
missile_homing_speed = 8
enemy_spawn_timer = 0
enemy_spawn_delay = 40
enemy_shoot_delay = 30
font = pygame.font.SysFont(None, 28)
bg_offset = 0

### Main game loop ###
running = True

while running:
    # Handle all game events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Get the current state of all keyboard keys
    keys = pygame.key.get_pressed()
    # Handle player input and movement
    player.Movement(keys)
    player.handle_collisions(enemies, enemyBullets, explosions, explosionSprite, explosion_time, explosionSound) 
    player.shoot(keys, bullets, playerBulletSprite, bullet_width, gunshotSound, auto_shoot=True)
    player.shoot_missile(keys, missiles, playerMissileSprite, missile_width, missile_height, missileSound)

    # Scroll the background
    bg_offset += 1
    if bg_offset >= BG.get_height():
        bg_offset = 0

    # Move player bullets and remove if off-screen
    for bullet in bullets[:]:
        bullet.Movement()
        if bullet.getYPos() < -bullet_height:
            bullets.remove(bullet)

    # Move and home missiles toward closest enemy, remove if off-screen
    for missile in missiles[:]:
        missile.Movement()
        if missile.getYPos() < -missile_height:
            missiles.remove(missile)
            continue 
        # Homing logic: steer missile horizontally toward closest enemy if any exist
        if enemies:
            # calculate euclidean distance between missile and each enemy and find the closest enemy
            closest_enemy = min(enemies, key=lambda e: math.hypot( 
                e.getXPos() + enemySprite.get_width() // 2 - (missile.getXPos() + missile_width // 2), 
                e.getYPos() + enemySprite.get_height() // 2 - (missile.getYPos() + missile_height // 2) 
            ))
            # Calculate the horizontal distance to the closest enemy and adjust the missile's x position to home in on it
            missile_center_x = missile.getXPos() + missile_width // 2
            enemy_center_x = closest_enemy.getXPos() + enemySprite.get_width() // 2
            dx = enemy_center_x - missile_center_x
            # Only home if enemy is above missile
            if closest_enemy.getYPos() < missile.getYPos():
                # Cap the homing change per frame
                if abs(dx) > missile_homing_speed: # if the distance is greater than the homing speed, cap it
                    dx = missile_homing_speed if dx > 0 else -missile_homing_speed # cap the change to the homing speed
                missile._xPos += dx # apply the horizontal change to the missile position

    enemy_spawn_timer += 1.3 
    if enemy_spawn_timer >= enemy_spawn_delay:
        enemy_x = random.randint(0, screenWidth - enemySprite.get_width())
        enemies.append(Enemy(surface, enemySprite, enemy_x, 0))
        enemy_spawn_timer = 0

    for ebullet in enemyBullets[:]:
        ebullet.Movement()
        if ebullet.getYPos() > screenHeight:
            enemyBullets.remove(ebullet)

    # Enemy update and collision logic handled inside class now
    score_ref = [score]  # mutable reference for score
    for enemy in enemies[:]:
        enemy.update(
            enemies, missiles, bullets,
            enemyBullets, enemyBulletSprite, enemyBullet_width, enemyBullet_height,
            explosionSprite, explosions, explosion_time, explosionSound,
            screenHeight, score_ref
        )
    score = score_ref[0]

# Handle enemy bullet collisions with player
    for exp in explosions[:]:
        exp[2] -= 1
        if exp[2] <= 0:
            explosions.remove(exp)

    # Draw all game objects and update display
    GameObject.Draw(surface)
    pygame.display.update()
    clock.tick(cSpeed)  # Maintain target FPS

pygame.quit()