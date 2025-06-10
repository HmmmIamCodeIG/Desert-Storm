import pygame
import random
import math

# contriants
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 480
PLAYER_SPEED = 5
PLAYER_BULLET_SPEED = 10
PLAYER_MISSILE_SPEED = 14
ENEMY_SPEED = 3
ENEMY_BULLET_SPEED = 7
MISSILE_HOMING_SPEED = 8

BULLET_SIZE = (4, 6)
MISSILE_SIZE = (6, 12)
ENEMY_BULLET_SIZE = (4, 6)
EXPLOSION_SIZE = (32, 32)

SHOOT_DELAY = 8
MISSILE_DELAY = 480
ENEMY_SPAWN_DELAY = 40
ENEMY_SHOOT_DELAY = 30
EXPLOSION_TIME = 30
PLAYER_MAX_HEALTH = 3
PLAYER_LIVES = 3

FONT_SIZE = 28
BG_SCROLL_SPEED = 1
FX_VOLUME = {'explosion': 0.3, 'gunshot': 0.1, 'missile': 0.5}
SFX_PATHS = {
    'gunshot': "Intro/fx/gunshot-fx-zap.wav",
    'missile': "Intro/fx/launching-missile-313226.mp3",
    'explosion': "Intro/fx/dry-explosion-fx.wav"
}
SOUNDTRACKS = [f"Intro/soundtrack/soundtrack{i}.mp3" for i in range(1, 8)]

# classes

class GameAssets:
    """Central storage for all images, sounds, and fonts."""
    def __init__(self):
        # Sprites
        self.bg = load_and_scale_img("Intro/libraryofimages/water.jpg", (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.player_sprites = {
            'forward': load_and_scale_img("Intro/libraryofimages/FA-18moving.png"),
            'left': load_and_scale_img("Intro/libraryofimages/FA-18movingleft.png"),
            'right': load_and_scale_img("Intro/libraryofimages/FA-18movingright.png"),
        }
        self.enemy_sprite = load_and_scale_img("Intro/libraryofimages/enemyF-4.png")
        self.player_bullet_sprite = pygame.Surface(BULLET_SIZE, pygame.SRCALPHA)
        self.player_bullet_sprite.fill((255, 255, 0))
        self.player_missile_sprite = pygame.Surface(MISSILE_SIZE, pygame.SRCALPHA)
        self.player_missile_sprite.fill((255, 0, 0))
        self.enemy_bullet_sprite = pygame.Surface(ENEMY_BULLET_SIZE, pygame.SRCALPHA)
        self.enemy_bullet_sprite.fill((0, 255, 255))
        self.explosion_sprite = load_and_scale_img("Intro/libraryofimages/explosion_Boom_2.png", EXPLOSION_SIZE)

        # Sounds
        self.sounds = {
            'gunshot': load_sound(SFX_PATHS['gunshot'], FX_VOLUME['gunshot']),
            'missile': load_sound(SFX_PATHS['missile'], FX_VOLUME['missile']),
            'explosion': load_sound(SFX_PATHS['explosion'], FX_VOLUME['explosion']),
            'soundtracks': [load_sound(path, 0.7) for path in SOUNDTRACKS]
        }

        # Font
        self.font = pygame.font.SysFont(None, FONT_SIZE)

assets = None  # Will be initialized after pygame.init()

# ---- GAME OBJECT CLASSES ----

class GameObject:
    def __init__(self, surface, sprite, x, y, speed):
        self.surface = surface
        self.sprite = sprite
        self.x = x
        self.y = y
        self.speed = speed

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.sprite.get_width(), self.sprite.get_height())

    def draw(self):
        self.surface.blit(self.sprite, (self.x, self.y))


class Player(GameObject):
    def __init__(self, surface, sprites, x, y):
        super().__init__(surface, sprites['forward'], x, y, PLAYER_SPEED)
        self.sprites = sprites

    def move(self, keys):
        moved_left = moved_right = False
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
            moved_right = True
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
            moved_left = True

        self.x = max(0, min(self.x, self.surface.get_width() - self.sprite.get_width()))
        self.y = max(0, min(self.y, self.surface.get_height() - self.sprite.get_height()))

        if moved_left:
            self.sprite = self.sprites['left']
        elif moved_right:
            self.sprite = self.sprites['right']
        else:
            self.sprite = self.sprites['forward']


class Bullet(GameObject):
    def __init__(self, surface, sprite, x, y, speed, direction):
        super().__init__(surface, sprite, x, y, speed)
        self.direction = direction  # -1 for up, 1 for down

    def move(self):
        self.y += self.speed * self.direction


class Enemy(GameObject):
    def __init__(self, surface, sprite, x, y):
        super().__init__(surface, sprite, x, y, ENEMY_SPEED)

    def move(self):
        self.y += self.speed


class Explosion:
    def __init__(self, x, y, sprite, time):
        self.x = x
        self.y = y
        self.sprite = sprite
        self.time = time

    def draw(self, surface):
        surface.blit(self.sprite, (self.x, self.y))

    def update(self):
        self.time -= 1
        return self.time > 0

class Missile(GameObject):
    def __init__(self, surface, sprite, x, y):
        super().__init__(surface, sprite, x, y, PLAYER_MISSILE_SPEED)

    def move(self):
        self.y -= self.speed  # Always move up

    def home_to(self, enemy):
        if enemy:
            missile_center_x = self.x + self.sprite.get_width() // 2
            enemy_center_x = enemy.x + enemy.sprite.get_width() // 2
            dx = enemy_center_x - missile_center_x
            if enemy.y < self.y:
                if abs(dx) > MISSILE_HOMING_SPEED:
                    dx = MISSILE_HOMING_SPEED if dx > 0 else -MISSILE_HOMING_SPEED
                self.x += dx

def load_and_scale_img(path, size=None):
    img = pygame.image.load(path).convert_alpha()
    if size:
        img = pygame.transform.scale(img, size)
    return img

def load_sound(path, volume=1.0):
    sound = pygame.mixer.Sound(path)
    sound.set_volume(volume)
    return sound

# Game state management

class GameState:
    def __init__(self, surface):
        self.surface = surface
        self.player = Player(
            surface, assets.player_sprites,
            (SCREEN_WIDTH - assets.player_sprites['forward'].get_width()) // 2,
            SCREEN_HEIGHT - assets.player_sprites['forward'].get_height()
        )
        self.bullets = []
        self.missiles = []
        self.enemies = []
        self.enemy_bullets = []
        self.explosions = []

        self.score = 0
        self.player_health = PLAYER_MAX_HEALTH
        self.player_lives = PLAYER_LIVES

        self.shoot_timer = 0
        self.missile_cooldown = 0
        self.enemy_spawn_timer = 0
        self.bg_offset = 0

    def restart_player(self):
        self.player_health = PLAYER_MAX_HEALTH
        self.player.x = (SCREEN_WIDTH - self.player.sprite.get_width()) // 2
        self.player.y = SCREEN_HEIGHT - self.player.sprite.get_height()

    def draw_hud(self):
        font = assets.font
        surface = self.surface
        # Lives
        y_offset = 5
        lives_text = font.render(f"Lives: {self.player_lives}", True, (255, 255, 255))
        surface.blit(lives_text, (5, y_offset))
        # Health
        y_offset += lives_text.get_height() + 5
        health_text = font.render(f"Health: {self.player_health}", True, (255, 255, 255))
        surface.blit(health_text, (5, y_offset))
        # Score
        y_offset += health_text.get_height() + 5
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        surface.blit(score_text, (5, y_offset))

    def draw(self):
        bg = assets.bg
        bg_height = bg.get_height()
        bg_offset_int = int(self.bg_offset)
        self.surface.blit(bg, (0, bg_offset_int - bg_height))
        self.surface.blit(bg, (0, bg_offset_int))

        # Draw all objects
        for obj_list in [self.bullets, self.missiles, self.enemies, self.enemy_bullets]:
            for obj in obj_list:
                obj.draw()
        for exp in self.explosions:
            exp.draw(self.surface)
        self.player.draw()
        self.draw_hud()


# ---- MAIN GAME LOOP ----

def main():
    global assets
    pygame.init()
    surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("gametest")
    clock = pygame.time.Clock()
    assets = GameAssets()

    # Soundtrack
    soundtrack_idx = random.randint(0, len(assets.sounds['soundtracks']) - 1)
    soundtrack = assets.sounds['soundtracks'][soundtrack_idx]
    soundtrack.play(-1)

    state = GameState(surface)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        state.player.move(keys)

        # Background scroll
        state.bg_offset += BG_SCROLL_SPEED
        if state.bg_offset >= assets.bg.get_height():
            state.bg_offset = 0

        # Player shooting
        state.shoot_timer += 1
        if state.shoot_timer >= SHOOT_DELAY:
            px = state.player.x + state.player.sprite.get_width() // 2 - BULLET_SIZE[0] // 2
            py = state.player.y
            state.bullets.append(Bullet(surface, assets.player_bullet_sprite, px, py, PLAYER_BULLET_SPEED, -1))
            state.shoot_timer = 0
            assets.sounds['gunshot'].play()

        # Player missile
        if state.missile_cooldown > 0:
            state.missile_cooldown -= 1
        if keys[pygame.K_SPACE] and state.missile_cooldown == 0:
            mx = state.player.x + state.player.sprite.get_width() // 2 - MISSILE_SIZE[0] // 2
            my = state.player.y
            state.missiles.append(Missile(surface, assets.player_missile_sprite, mx, my))
            state.missile_cooldown = MISSILE_DELAY
            assets.sounds['missile'].play()

        # Move bullets
        state.bullets[:] = [b for b in state.bullets if b.y > -BULLET_SIZE[1] and b.move() is None]
        # Move missiles (with homing)
        for missile in state.missiles[:]:
            missile.move()
            if missile.y < -MISSILE_SIZE[1]:
                state.missiles.remove(missile)
                continue
            if state.enemies:
                closest_enemy = min(state.enemies, key=lambda e: math.hypot(
                    e.x + e.sprite.get_width() // 2 - (missile.x + MISSILE_SIZE[0] // 2),
                    e.y + e.sprite.get_height() // 2 - (missile.y + MISSILE_SIZE[1] // 2)
                ))
                missile.home_to(closest_enemy)

        # Enemy spawning
        state.enemy_spawn_timer += 1.3
        if state.enemy_spawn_timer >= ENEMY_SPAWN_DELAY:
            ex = random.randint(0, SCREEN_WIDTH - assets.enemy_sprite.get_width())
            state.enemies.append(Enemy(surface, assets.enemy_sprite, ex, 0))
            state.enemy_spawn_timer = 0

        # Enemies and enemy shooting
        for enemy in state.enemies[:]:
            enemy.move()
            if random.randint(0, ENEMY_SHOOT_DELAY - 1) == 0:
                ex = enemy.x + enemy.sprite.get_width() // 2 - ENEMY_BULLET_SIZE[0] // 2
                ey = enemy.y + enemy.sprite.get_height()
                state.enemy_bullets.append(Bullet(surface, assets.enemy_bullet_sprite, ex, ey, ENEMY_BULLET_SPEED, 1))
            if enemy.y > SCREEN_HEIGHT:
                state.enemies.remove(enemy)

        # Enemy bullets
        state.enemy_bullets[:] = [b for b in state.enemy_bullets if b.y < SCREEN_HEIGHT and b.move() is None]

        # Bullet-enemy collisions
        for bullet in state.bullets[:]:
            for enemy in state.enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    state.bullets.remove(bullet)
                    explosion_x = enemy.x + enemy.sprite.get_width() // 2 - EXPLOSION_SIZE[0] // 2
                    explosion_y = enemy.y + enemy.sprite.get_height() // 2 - EXPLOSION_SIZE[1] // 2
                    state.explosions.append(Explosion(explosion_x, explosion_y, assets.explosion_sprite, EXPLOSION_TIME))
                    assets.sounds['explosion'].play()
                    state.enemies.remove(enemy)
                    state.score += 1
                    break

        # Missile-enemy collisions
        for missile in state.missiles[:]:
            for enemy in state.enemies[:]:
                if missile.rect.colliderect(enemy.rect):
                    state.missiles.remove(missile)
                    explosion_x = enemy.x + enemy.sprite.get_width() // 2 - EXPLOSION_SIZE[0] // 2
                    explosion_y = enemy.y + enemy.sprite.get_height() // 2 - EXPLOSION_SIZE[1] // 2
                    state.explosions.append(Explosion(explosion_x, explosion_y, assets.explosion_sprite, EXPLOSION_TIME))
                    assets.sounds['explosion'].play()
                    state.enemies.remove(enemy)
                    state.score += 1
                    break

        # Enemy bullet-player collisions
        for bullet in state.enemy_bullets[:]:
            if bullet.rect.colliderect(state.player.rect):
                state.player_health -= 1
                state.enemy_bullets.remove(bullet)
                if state.player_health <= 0:
                    state.player_lives -= 1
                    explosion_x = state.player.x + state.player.sprite.get_width() // 2 - EXPLOSION_SIZE[0] // 2
                    explosion_y = state.player.y + state.player.sprite.get_height() // 2 - EXPLOSION_SIZE[1] // 2
                    state.explosions.append(Explosion(explosion_x, explosion_y, assets.explosion_sprite, EXPLOSION_TIME))
                    assets.sounds['explosion'].play()
                    pygame.display.update()
                    pygame.time.delay(500)
                    if state.player_lives <= 0:
                        running = False
                    else:
                        state.restart_player()
                break

        # Enemy-player collision
        for enemy in state.enemies[:]:
            if enemy.rect.colliderect(state.player.rect):
                state.player_health -= 3
                state.enemies.remove(enemy)
                explosion_x = enemy.x + enemy.sprite.get_width() // 2 - EXPLOSION_SIZE[0] // 2
                explosion_y = enemy.y + enemy.sprite.get_height() // 2 - EXPLOSION_SIZE[1] // 2
                state.explosions.append(Explosion(explosion_x, explosion_y, assets.explosion_sprite, EXPLOSION_TIME))
                assets.sounds['explosion'].play()
                pygame.display.update()
                if state.player_health <= 0:
                    state.player_lives -= 1
                    if state.player_lives <= 0:
                        running = False
                    else:
                        state.restart_player()
                break

        # Update and remove finished explosions
        state.explosions[:] = [exp for exp in state.explosions if exp.update()]

        # Draw everything
        state.draw()
        pygame.display.update()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()