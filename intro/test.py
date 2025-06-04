import pygame
import random
import math

# --- GameObject Classes ---

class GameObject:
    def __init__(self, surface, sprite, xPos, yPos, speed):
        self._surface = surface
        self._sprite = sprite
        self._xPos = xPos
        self._yPos = yPos
        self._speed = speed

    def getXPos(self): return self._xPos
    def getYPos(self): return self._yPos
    def getPos(self): return (self._xPos, self._yPos)
    def drawSprite(self): self._surface.blit(self._sprite, (self._xPos, self._yPos))
    def get_rect(self):
        return pygame.Rect(self._xPos, self._yPos, self._sprite.get_width(), self._sprite.get_height())

class Player(GameObject):
    def __init__(self, surface, moving_forward_sprite, moving_left_sprite, moving_right_sprite, xPos, yPos):
        super().__init__(surface, moving_forward_sprite, xPos, yPos, 5)
        self._default_sprite = moving_forward_sprite
        self._moving_left_sprite = moving_left_sprite
        self._moving_right_sprite = moving_right_sprite
            
    def Movement(self, keysPressed):
        moved_left = moved_right = False
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

        # boundary checks
        self._xPos = max(0, min(self._xPos, self._surface.get_width() - self._sprite.get_width()))
        self._yPos = max(0, min(self._yPos, self._surface.get_height() - self._sprite.get_height()))

        # sprite direction
        if moved_left:
            self._sprite = self._moving_left_sprite
        elif moved_right:
            self._sprite = self._moving_right_sprite
        else:
            self._sprite = self._default_sprite

class PlayerBullet(GameObject):
    def __init__(self, surface, sprite, xPos, yPos):
        super().__init__(surface, sprite, xPos, yPos, 10)
    def Movement(self): self._yPos -= self._speed

class Enemy(GameObject):
    def __init__(self, surface, sprite, xPos, yPos):
        super().__init__(surface, sprite, xPos, yPos, 3)
    def Movement(self): self._yPos += self._speed

class EnemyBullet(GameObject):
    def __init__(self, surface, sprite, xPos, yPos):
        super().__init__(surface, sprite, xPos, yPos, 7)
    def Movement(self): self._yPos += self._speed

class PlayerMissile(GameObject):
    def __init__(self, surface, sprite, xPos, yPos):
        super().__init__(surface, sprite, xPos, yPos, 14)
    def Movement(self): self._yPos -= self._speed

# --- Initialisation ---

def load_sprites_and_sounds():
    sprites = {
        'BG': pygame.transform.scale(
            pygame.image.load("Intro/libraryofimages/water.jpg").convert(),
            (screenWidth, screenHeight)
        ),
        'playerForward': pygame.image.load("Intro/libraryofimages/FA-18moving.png").convert_alpha(),
        'playerLeft': pygame.image.load("Intro/libraryofimages/FA-18movingleft.png").convert_alpha(),
        'playerRight': pygame.image.load("Intro/libraryofimages/FA-18movingright.png").convert_alpha(),
        'enemy': pygame.image.load("Intro/libraryofimages/enemyF-4.png").convert_alpha(),
        'explosion': pygame.transform.scale(
            pygame.image.load("Intro/libraryofimages/explosion_Boom_2.png").convert_alpha(), (32, 32)
        ),
    }
    bullet_width, bullet_height = 4, 6
    sprites['playerBullet'] = pygame.Surface((bullet_width, bullet_height), pygame.SRCALPHA)
    sprites['playerBullet'].fill((255, 255, 0))
    missile_width, missile_height = 6, 12
    sprites['playerMissile'] = pygame.Surface((missile_width, missile_height), pygame.SRCALPHA)
    sprites['playerMissile'].fill((255, 0, 0))
    enemyBullet_width, enemyBullet_height = 4, 6
    sprites['enemyBullet'] = pygame.Surface((enemyBullet_width, enemyBullet_height), pygame.SRCALPHA)
    sprites['enemyBullet'].fill((0, 255, 255))

    sounds = {
        'gunshot': pygame.mixer.Sound("Intro/fx/gunshot-fx-zap.wav"),
        'missile': pygame.mixer.Sound("Intro/fx/launching-missile-313226.mp3"),
        'explosion': pygame.mixer.Sound("Intro/fx/dry-explosion-fx.wav"),
    }
    sounds['tracks'] = {
        i: pygame.mixer.Sound(f"Intro/soundtrack/soundtrack{i}.mp3") for i in range(1, 8)
    }
    return sprites, sounds

def set_volumes(sounds, chosen_track):
    for i, track in sounds['tracks'].items():
        track.set_volume(0.70)
        if i == chosen_track:
            print(f"Current soundtrack: Soundtrack {i}")
    sounds['explosion'].set_volume(0.3)
    sounds['gunshot'].set_volume(0.1)
    sounds['missile'].set_volume(0.5)

def draw(surface, BG, bg_offset, sprites, player, bullets, missiles, enemies, enemyBullets, explosions, font, player_lives, player_health, score):
    BG_height = BG.get_height()
    surface.blit(BG, (0, int(bg_offset) - BG_height))
    surface.blit(BG, (0, int(bg_offset)))
    for obj_list in (bullets, missiles, enemies, enemyBullets):
        for obj in obj_list: obj.drawSprite()
    for exp in explosions:
        surface.blit(sprites['explosion'], (exp[0], exp[1]))
    player.drawSprite()
    y = 5
    for label, value in [("Lives", player_lives), ("Health", player_health), ("Score", score)]:
        text = font.render(f"{label}: {value}", True, (255, 255, 255))
        surface.blit(text, (5, y))
        y += text.get_height() + 5

def spawn_enemy(surface, sprites, screenWidth):
    enemy_x = random.randint(0, screenWidth - sprites['enemy'].get_width())
    return Enemy(surface, sprites['enemy'], enemy_x, 0)

# --- Main Game Loop ---

def main():
    global screenWidth, screenHeight
    pygame.init()
    screenWidth, screenHeight = 320, 480
    surface = pygame.display.set_mode((screenWidth, screenHeight))
    pygame.display.set_caption("gametest")
    clock = pygame.time.Clock()
    cSpeed = 60

    sprites, sounds = load_sprites_and_sounds()
    bullet_width, bullet_height = sprites['playerBullet'].get_width(), sprites['playerBullet'].get_height()
    missile_width, missile_height = sprites['playerMissile'].get_width(), sprites['playerMissile'].get_height()
    enemyBullet_width, enemyBullet_height = sprites['enemyBullet'].get_width(), sprites['enemyBullet'].get_height()

    soundtrack_choice = random.randint(1, 7)
    current_soundtrack = sounds['tracks'][soundtrack_choice]
    current_soundtrack.play(-1)
    set_volumes(sounds, soundtrack_choice)

    player = Player(
        surface,
        sprites['playerForward'],
        sprites['playerLeft'],
        sprites['playerRight'],
        (screenWidth - sprites['playerForward'].get_width()) // 2,
        screenHeight - sprites['playerForward'].get_height()
    )

    bullets, missiles, enemies, enemyBullets, explosions = [], [], [], [], []
    score, explosion_time, missile_homing_speed = 0, 30, 8
    shoot_timer, shoot_delay = 0, 8
    missile_cooldown, missile_delay = 0, 480
    enemy_spawn_timer, enemy_spawn_delay = 0, 40
    enemy_shoot_delay = 30
    player_health, player_max_health, player_lives = 3, 3, 3
    font = pygame.font.SysFont(None, 28)
    bg_offset, running = 0, True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        player.Movement(keys)

        # Scrolling Background
        bg_offset = (bg_offset + 1) % sprites['BG'].get_height()

        # Player Shooting
        shoot_timer += 1
        if shoot_timer >= shoot_delay:
            bullet_x = player.getXPos() + sprites['playerForward'].get_width() // 2 - bullet_width // 2
            bullet_y = player.getYPos()
            bullets.append(PlayerBullet(surface, sprites['playerBullet'], bullet_x, bullet_y))
            shoot_timer = 0
            sounds['gunshot'].play()

        # Player Missile
        missile_cooldown = max(0, missile_cooldown - 1)
        if keys[pygame.K_SPACE] and missile_cooldown == 0:
            missile_x = player.getXPos() + sprites['playerForward'].get_width() // 2 - missile_width // 2
            missile_y = player.getYPos()
            missiles.append(PlayerMissile(surface, sprites['playerMissile'], missile_x, missile_y))
            missile_cooldown = missile_delay
            sounds['missile'].play()

        # Move Bullets
        bullets[:] = [b for b in bullets if b.Movement() or b.getYPos() >= -bullet_height]
        missiles[:] = [m for m in missiles if m.Movement() or m.getYPos() >= -missile_height]

        # Missile homing logic
        for missile in missiles:
            if enemies:
                closest_enemy = min(
                    enemies,
                    key=lambda e: math.hypot(
                        e.getXPos() + sprites['enemy'].get_width() // 2 - (missile.getXPos() + missile_width // 2),
                        e.getYPos() + sprites['enemy'].get_height() // 2 - (missile.getYPos() + missile_height // 2)
                    )
                )
                missile_center_x = missile.getXPos() + missile_width // 2
                enemy_center_x = closest_enemy.getXPos() + sprites['enemy'].get_width() // 2
                dx = enemy_center_x - missile_center_x
                if closest_enemy.getYPos() < missile.getYPos():
                    dx = max(-missile_homing_speed, min(dx, missile_homing_speed))
                    missile._xPos += dx

        # Spawn Enemies
        enemy_spawn_timer += 1.3
        if enemy_spawn_timer >= enemy_spawn_delay:
            enemies.append(spawn_enemy(surface, sprites, screenWidth))
            enemy_spawn_timer = 0

        # Enemy logic & shooting
        for enemy in enemies[:]:
            enemy.Movement()
            if random.randint(0, enemy_shoot_delay-1) == 0:
                ebullet_x = enemy.getXPos() + sprites['enemy'].get_width() // 2 - enemyBullet_width // 2
                ebullet_y = enemy.getYPos() + sprites['enemy'].get_height()
                enemyBullets.append(EnemyBullet(surface, sprites['enemyBullet'], ebullet_x, ebullet_y))
            if enemy.getYPos() > screenHeight:
                enemies.remove(enemy)

        # Enemy Bullets
        enemyBullets[:] = [eb for eb in enemyBullets if eb.Movement() or eb.getYPos() <= screenHeight]

        # Bullet-enemy collisions
        for bullet in bullets[:]:
            bullet_rect = bullet.get_rect()
            for enemy in enemies[:]:
                if bullet_rect.colliderect(enemy.get_rect()):
                    if bullet in bullets: bullets.remove(bullet)
                    if enemy in enemies:
                        explosion_x = enemy.getXPos() + sprites['enemy'].get_width() // 2 - sprites['explosion'].get_width() // 2
                        explosion_y = enemy.getYPos() + sprites['enemy'].get_height() // 2 - sprites['explosion'].get_height() // 2
                        explosions.append([explosion_x, explosion_y, explosion_time])
                        sounds['explosion'].play()
                        enemies.remove(enemy)
                        score += 1

        # Missile-enemy collisions
        for missile in missiles[:]:
            missile_rect = missile.get_rect()
            for enemy in enemies[:]:
                if missile_rect.colliderect(enemy.get_rect()):
                    if missile in missiles: missiles.remove(missile)
                    if enemy in enemies:
                        explosion_x = enemy.getXPos() + sprites['enemy'].get_width() // 2 - sprites['explosion'].get_width() // 2
                        explosion_y = enemy.getYPos() + sprites['enemy'].get_height() // 2 - sprites['explosion'].get_height() // 2
                        explosions.append([explosion_x, explosion_y, explosion_time])
                        sounds['explosion'].play()
                        enemies.remove(enemy)
                        score += 1
                    break

        # Enemy bullet-player collisions
        for ebullet in enemyBullets[:]:
            if ebullet.get_rect().colliderect(player.get_rect()):
                player_health -= 1
                enemyBullets.remove(ebullet)
                if player_health <= 0:
                    player_lives -= 1
                    explosion_x = player.getXPos() + sprites['playerForward'].get_width() // 2 - sprites['explosion'].get_width() // 2
                    explosion_y = player.getYPos() + sprites['playerForward'].get_height() // 2 - sprites['explosion'].get_height() // 2
                    explosions.append([explosion_x, explosion_y, explosion_time])
                    sounds['explosion'].play()
                    pygame.display.update()
                    if player_lives <= 0:
                        draw(surface, sprites['BG'], bg_offset, sprites, player, bullets, missiles, enemies, enemyBullets, explosions, font, player_lives, player_health, score)
                        pygame.display.update()
                        pygame.time.delay(500)
                        running = False
                    else:
                        player_health = player_max_health
                        player._xPos = (screenWidth - sprites['playerForward'].get_width()) // 2
                        player._yPos = screenHeight - sprites['playerForward'].get_height()
                break
        
        # Enemy plane-player collisions
        for enemy in enemies[:]:
            if enemy.get_rect().colliderect(player.get_rect()):
                player_health -= 3
                enemies.remove(enemy)
                explosion_x = enemy.getXPos() + sprites['enemy'].get_width() // 2 - sprites['explosion'].get_width() // 2
                explosion_y = enemy.getYPos() + sprites['enemy'].get_height() // 2 - sprites['explosion'].get_height() // 2
                explosions.append([explosion_x, explosion_y, explosion_time])
                sounds['explosion'].play()
                pygame.display.update()
                if player_health <= 0:
                    player_lives -= 1
                    if player_lives <= 0:
                        running = False
                    else:
                        player_health = player_max_health
                        player._xPos = (screenWidth - sprites['playerForward'].get_width()) // 2
                        player._yPos = screenHeight - sprites['playerForward'].get_height()
                break

        # Update and remove finished explosions
        for exp in explosions[:]:
            exp[2] -= 1
            if exp[2] <= 0:
                explosions.remove(exp)

        draw(surface, sprites['BG'], bg_offset, sprites, player, bullets, missiles, enemies, enemyBullets, explosions, font, player_lives, player_health, score)
        pygame.display.update()
        clock.tick(cSpeed)
    pygame.quit()

if __name__ == "__main__":
    main()