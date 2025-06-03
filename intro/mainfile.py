import pygame
import random
import math

class VisualDebugger:
    def __init__(self, surface):
        self._surface = surface
        self._debug_lines = []

    def add_line(self, start_pos, end_pos, color=(255, 0, 0)):
        self._debug_lines.append((start_pos, end_pos, color))

    def draw(self):
        for start_pos, end_pos, color in self._debug_lines:
            pygame.draw.line(self._surface, color, start_pos, end_pos)
        self._debug_lines.clear()

class GameObject:
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

    def drawSprite(self):
        self._surface.blit(self._sprite, (self._xPos, self._yPos))

    def get_rect(self):
        return pygame.Rect(self._xPos, self._yPos, self._sprite.get_width(), self._sprite.get_height())

class Player(GameObject):
    def __init__(self, surface, moving_forward_sprite, moving_left_sprite, moving_right_sprite, xPos, yPos):
        super().__init__(surface, moving_forward_sprite, xPos, yPos, 5)
        self._default_sprite = moving_forward_sprite
        self._moving_left_sprite = moving_left_sprite
        self._moving_right_sprite = moving_right_sprite
            
    def Movement(self, keysPressed):
        moved_left = False
        moved_right = False
        if keysPressed[pygame.K_UP] or keysPressed[pygame.K_w]:
            self._yPos -= self._speed
        if keysPressed[pygame.K_DOWN] or keysPressed[pygame.K_s]:
            self._yPos += self._speed
        if keysPressed[pygame.K_RIGHT] or keysPressed[pygame.K_d]:
            self._xPos += self._speed
            moved_right = True
        elif keysPressed[pygame.K_LEFT] or keysPressed[pygame.K_a]:
            self._xPos -= self._speed
            moved_left = True

        self._xPos = max(0, min(self._xPos, self._surface.get_width() - self._sprite.get_width()))
        self._yPos = max(0, min(self._yPos, self._surface.get_height() - self._sprite.get_height()))

        if moved_left:
            self._sprite = self._moving_left_sprite
        elif moved_right:
            self._sprite = self._moving_right_sprite
        else:
            self._sprite = self._default_sprite

class PlayerBullet(GameObject):
    def __init__(self, surface, sprite, xPos, yPos):
        super().__init__(surface, sprite, xPos, yPos, 10)

    def Movement(self):
        self._yPos -= self._speed

class Enemy(GameObject):
    def __init__(self, surface, sprite, xPos, yPos):
        super().__init__(surface, sprite, xPos, yPos, 3)

    def Movement(self):
        self._yPos += self._speed

class EnemyBullet(GameObject):
    def __init__(self, surface, sprite, xPos, yPos):
        super().__init__(surface, sprite, xPos, yPos, 7)

    def Movement(self):
        self._yPos += self._speed

class PlayerMissile(GameObject):
    def __init__(self, surface, sprite, xPos, yPos):
        super().__init__(surface, sprite, xPos, yPos, 14)

    def Movement(self):
        self._yPos -= self._speed

# Initialisation 

pygame.init()

screenWidth = 320
screenHeight = 480
surface = pygame.display.set_mode((screenWidth, screenHeight))

BG = pygame.image.load("Intro/libraryofimages/water.jpg").convert() 
BG = pygame.transform.scale(BG, (screenWidth, screenHeight))  

clock = pygame.time.Clock()
cSpeed = 60

title = "gametest"
pygame.display.set_caption(title)

# Load sprites and sounds for player, bullets, missiles, enemies, and enemy bullets
playerMovingForwardSprite = pygame.image.load("Intro/libraryofimages/FA-18moving.png").convert_alpha()
playerMovingLeftSprite = pygame.image.load("Intro/libraryofimages/FA-18movingleft.png").convert_alpha()
playerMovingRightSprite = pygame.image.load("Intro/libraryofimages/FA-18movingright.png").convert_alpha()
bullet_width, bullet_height = 4, 6
playerBulletSprite = pygame.Surface((bullet_width, bullet_height), pygame.SRCALPHA)
playerBulletSprite.fill((255, 255, 0))
gunshotSound = pygame.mixer.Sound("Intro/fx/gunshot-fx-zap.wav")
missile_width, missile_height = 6, 12
playerMissileSprite = pygame.Surface((missile_width, missile_height), pygame.SRCALPHA)
playerMissileSprite.fill((255, 0, 0))
missileSound = pygame.mixer.Sound("Intro/fx/launching-missile-313226.mp3")
enemySprite = pygame.image.load("Intro/libraryofimages/enemyF-4.png").convert_alpha()
enemyBullet_width, enemyBullet_height = 4, 6
enemyBulletSprite = pygame.Surface((enemyBullet_width, enemyBullet_height), pygame.SRCALPHA)
enemyBulletSprite.fill((0, 255, 255))
explosionSprite = pygame.image.load("Intro/libraryofimages/explosion_Boom_2.png").convert_alpha()
explosionSprite = pygame.transform.scale(explosionSprite, (32, 32))  
explosionSound = pygame.mixer.Sound("Intro/fx/dry-explosion-fx.wav")

# Create player object, starting at the bottom center of the screen
player = Player(surface, playerMovingForwardSprite, playerMovingLeftSprite, playerMovingRightSprite, (screenWidth - playerMovingForwardSprite.get_width()) // 2, screenHeight - playerMovingForwardSprite.get_height())

# Lists to hold bullets, missiles, enemies, and enemy bullets
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
    5: pygame.mixer.Sound("Intro/soundtrack/soundtrack5.mp3")
}

for i in range(1, 6):
    audiopath[i].set_volume(0.50)

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
missile_delay = 200
enemy_spawn_timer = 0
enemy_spawn_delay = 40
enemy_shoot_delay = 30
player_health = 3
player_max_health = 3
player_lives = 3
font = pygame.font.SysFont(None, 28)
bg_offset = 0

# Draw function to render the game state
def Draw():
    global bg_offset  
    bg_offset_int = int(bg_offset)
    BG_height = BG.get_height()
    surface.blit(BG, (0, bg_offset_int - BG_height))
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
    lives_text = font.render(f"Lives: {player_lives}", True, (255, 255, 255))
    surface.blit(lives_text, (5, 5))
    # Draw health 
    health_text = font.render(f"Health: {player_health}", True, (255, 255, 255))
    surface.blit(health_text, (5, 5 + lives_text.get_height() + 5))
    # Draw score 
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    surface.blit(score_text, (5, 5 + lives_text.get_height() + health_text.get_height() + 10))

soundtrack_choice = random.randint(1, 5)
current_soundtrack = audiopath[soundtrack_choice]
current_soundtrack.play(-1)

# Main loop
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    player.Movement(keys)

    # Visual Debugger
    debugger = VisualDebugger(surface)
    debugger.add_line(player.getPos(), (player.getXPos() + playerMovingForwardSprite.get_width() // 2, player.getYPos() + playerMovingForwardSprite.get_height()), (0, 255, 0))  # Player position line
    for bullet in bullets:
        debugger.add_line(bullet.getPos(), (bullet.getXPos() + bullet_width // 2, bullet.getYPos() + bullet_height), (255, 255, 0))
    for missile in missiles:
        debugger.add_line(missile.getPos(), (missile.getXPos() + missile_width // 2, missile.getYPos() + missile_height), (255, 0, 0))
    for enemy in enemies:
        debugger.add_line(enemy.getPos(), (enemy.getXPos() + enemySprite.get_width() // 2, enemy.getYPos() + enemySprite.get_height()), (255, 0, 255))
    for ebullet in enemyBullets:
        debugger.add_line(ebullet.getPos(), (ebullet.getXPos() + enemyBullet_width // 2, ebullet.getYPos() + enemyBullet_height), (0, 0, 255))
    debugger.draw()

    # Scrolling Background
    bg_offset += 1
    if bg_offset >= BG.get_height():
        bg_offset = 0

    # Player Shooting
    shoot_timer += 1
    if shoot_timer >= shoot_delay: 
        bullet_x = player.getXPos() + playerMovingForwardSprite.get_width() // 2 - bullet_width // 2
        bullet_y = player.getYPos()
        bullets.append(PlayerBullet(surface, playerBulletSprite, bullet_x, bullet_y))
        shoot_timer = 0
        gunshotSound.play()

    # Player Missile Shooting 
    if missile_cooldown > 0:
        missile_cooldown -= 1
    if keys[pygame.K_SPACE] and missile_cooldown == 0: 
        missile_x = player.getXPos() + playerMovingForwardSprite.get_width() // 2 - missile_width // 2
        missile_y = player.getYPos()
        missiles.append(PlayerMissile(surface, playerMissileSprite, missile_x, missile_y))
        missile_cooldown = missile_delay
        missileSound.play()

    # Move Player Bullets
    for bullet in bullets[:]:
        bullet.Movement() 
        if bullet.getYPos() < -bullet_height:
            bullets.remove(bullet)

    # Missiles
    for missile in missiles[:]:
        missile.Movement()
        if missile.getYPos() < -missile_height:
            missiles.remove(missile)
            continue 
        if enemies:
            closest_enemy = min(enemies, key=lambda e: math.hypot(
                e.getXPos() + enemySprite.get_width() // 2 - (missile.getXPos() + missile_width // 2),
                e.getYPos() + enemySprite.get_height() // 2 - (missile.getYPos() + missile_height // 2)
            ))
            missile_center_x = missile.getXPos() + missile_width // 2
            enemy_center_x = closest_enemy.getXPos() + enemySprite.get_width() // 2
            dx = enemy_center_x - missile_center_x
            if closest_enemy.getYPos() < missile.getYPos():
                if abs(dx) > missile_homing_speed:
                    dx = missile_homing_speed if dx > 0 else -missile_homing_speed
                missile._xPos += dx

    # Enemy Spawning
    enemy_spawn_timer += 1.3
    if enemy_spawn_timer >= enemy_spawn_delay:
        enemy_x = random.randint(0, screenWidth - enemySprite.get_width())
        enemies.append(Enemy(surface, enemySprite, enemy_x, 0))
        enemy_spawn_timer = 0

    # Enemies and Enemy Shooting
    for enemy in enemies[:]:
        enemy.Movement()
        if random.randint(0, enemy_shoot_delay-1) == 0:
            ebullet_x = enemy.getXPos() + enemySprite.get_width() // 2 - enemyBullet_width // 2
            ebullet_y = enemy.getYPos() + enemySprite.get_height()
            enemyBullets.append(EnemyBullet(surface, enemyBulletSprite, ebullet_x, ebullet_y))
        if enemy.getYPos() > screenHeight:
            enemies.remove(enemy)

    # Enemy Bullets
    for ebullet in enemyBullets[:]:
        ebullet.Movement()
        if ebullet.getYPos() > screenHeight:
            enemyBullets.remove(ebullet)

    # Bullet-enemy collisions
    for bullet in bullets[:]:
        bullet_rect = bullet.get_rect()
        for enemy in enemies[:]:
            enemy_rect = enemy.get_rect()
            if bullet_rect.colliderect(enemy_rect):
                if bullet in bullets:
                    bullets.remove(bullet)
                if enemy in enemies:
                    explosion_x = enemy.getXPos() + enemySprite.get_width() // 2 - explosionSprite.get_width() // 2
                    explosion_y = enemy.getYPos() + enemySprite.get_height() // 2 - explosionSprite.get_height() // 2
                    explosions.append([explosion_x, explosion_y, explosion_time])
                    explosionSound.play()
                    enemies.remove(enemy)
                    score += 1

    # Missile-enemy collisions
    for missile in missiles[:]:
        missile_rect = missile.get_rect()
        for enemy in enemies[:]:
            if missile_rect.colliderect(enemy.get_rect()): 
                if missile in missiles:
                    missiles.remove(missile)
                if enemy in enemies:
                    explosion_x = enemy.getXPos() + enemySprite.get_width() // 2 - explosionSprite.get_width() // 2
                    explosion_y = enemy.getYPos() + enemySprite.get_height() // 2 - explosionSprite.get_height() // 2
                    explosions.append([explosion_x, explosion_y, explosion_time])
                    explosionSound.play()
                    enemies.remove(enemy)
                    score += 1
                break

    # Enemy bullet-player collisions (lives & health system)
    for ebullet in enemyBullets[:]:
        if ebullet.get_rect().colliderect(player.get_rect()):
            player_health -= 1
            enemyBullets.remove(ebullet)
            if player_health <= 0:
                player_lives -= 1
                explosion_x = player.getXPos() + playerMovingForwardSprite.get_width() // 2 - explosionSprite.get_width() // 2
                explosion_y = player.getYPos() + playerMovingForwardSprite.get_height() // 2 - explosionSprite.get_height() // 2
                explosions.append([explosion_x, explosion_y, explosion_time])
                explosionSound.play()
                pygame.display.update()
                if player_lives <= 0:
                    Draw()
                    pygame.display.update()
                    pygame.time.delay(500)
                    running = False
                else:
                    player_health = player_max_health
                    player._xPos = (screenWidth - playerMovingForwardSprite.get_width()) // 2
                    player._yPos = screenHeight - playerMovingForwardSprite.get_height()
                break
        
    # Enemy plane-player collisions
    for enemy in enemies[:]:
        if enemy.get_rect().colliderect(player.get_rect()):
            player_health -= 3
            enemies.remove(enemy)
            explosion_x = enemy.getXPos() + enemySprite.get_width() // 2 - explosionSprite.get_width() // 2
            explosion_y = enemy.getYPos() + enemySprite.get_height() // 2 - explosionSprite.get_height() // 2
            explosions.append([explosion_x, explosion_y, explosion_time])
            explosionSound.play()
            pygame.display.update()
            if player_health <= 0:
                player_lives -= 1
                if player_lives <= 0:
                    running = False
                else:
                    player_health = player_max_health
                    player._xPos = (screenWidth - playerMovingForwardSprite.get_width()) // 2
                    player._yPos = screenHeight - playerMovingForwardSprite.get_height()
            break

    # Update and remove finished explosions
    for exp in explosions[:]:
        exp[2] -= 1
        if exp[2] <= 0:
            explosions.remove(exp)

    Draw()
    pygame.display.update()
    clock.tick(cSpeed)

pygame.quit()