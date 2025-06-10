import pygame
import random
import math

# --- Asset Manager ---
class AssetManager:
    def __init__(self, screen_width, screen_height):
        # Load and scale background image
        self.bg = pygame.transform.scale(
            pygame.image.load("Intro/libraryofimages/water.jpg").convert(), (screen_width, screen_height))

        # Load player sprites for different directions
        self.player_sprites = {
            "forward": pygame.image.load("Intro/libraryofimages/FA-18moving.png").convert_alpha(),
            "left": pygame.image.load("Intro/libraryofimages/FA-18movingleft.png").convert_alpha(),
            "right": pygame.image.load("Intro/libraryofimages/FA-18movingright.png").convert_alpha(),
        }

        # Load enemy sprite
        self.enemy_sprite = pygame.image.load("Intro/libraryofimages/enemyF-4.png").convert_alpha()

        # Make bullet/missile/enemy bullet sprites as simple colored rectangles
        self.player_bullet = pygame.Surface((4, 6), pygame.SRCALPHA)
        self.player_bullet.fill((255, 255, 0))
        self.player_missile = pygame.Surface((6, 12), pygame.SRCALPHA)
        self.player_missile.fill((255, 0, 0))
        self.enemy_bullet = pygame.Surface((4, 6), pygame.SRCALPHA)
        self.enemy_bullet.fill((0, 255, 255))

        # Load and scale explosion sprite
        self.explosion = pygame.transform.scale(
            pygame.image.load("Intro/libraryofimages/explosion_Boom_2.png").convert_alpha(), (32, 32))

        # Load all sounds (fx and soundtracks)
        self.sounds = {
            "gunshot": pygame.mixer.Sound("Intro/fx/gunshot-fx-zap.wav"),
            "missile": pygame.mixer.Sound("Intro/fx/launching-missile-313226.mp3"),
            "explosion": pygame.mixer.Sound("Intro/fx/dry-explosion-fx.wav"),
            "soundtracks": [pygame.mixer.Sound(f"Intro/soundtrack/soundtrack{i}.mp3") for i in range(1, 8)]
        }

        # Load font
        self.font = pygame.font.SysFont(None, 28)

# --- Game Entities ---
class GameObject:
    def __init__(self, surface, sprite, x, y, speed):
        self.surface = surface
        self.sprite = sprite
        self.x = x
        self.y = y
        self.speed = speed

    def draw(self):
        self.surface.blit(self.sprite, (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.sprite.get_width(), self.sprite.get_height())

class Player(GameObject):

    def __init__(self, surface, sprites, x, y):
        super().__init__(surface, sprites["forward"], x, y, 5)
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

        # Prevent moving out of the screen bounds
        self.x = max(0, min(self.x, self.surface.get_width() - self.sprite.get_width()))
        self.y = max(0, min(self.y, self.surface.get_height() - self.sprite.get_height()))

        # Change sprite based on direction
        if moved_left:
            self.sprite = self.sprites["left"]
        elif moved_right:
            self.sprite = self.sprites["right"]
        else:
            self.sprite = self.sprites["forward"]

class Bullet(GameObject):
    def __init__(self, surface, sprite, x, y, speed, direction):
        super().__init__(surface, sprite, x, y, speed)
        self.direction = direction  # -1 for up (player), 1 for down (enemy)

    def move(self):
        self.y += self.speed * self.direction

class Missile(GameObject):
    def __init__(self, surface, sprite, x, y):
        super().__init__(surface, sprite, x, y, 14)

    def move(self):
        self.y -= self.speed

    def home_to(self, enemy, missile_homing_speed=8):
        if enemy:
            missile_center_x = self.x + self.sprite.get_width() // 2
            enemy_center_x = enemy.x + enemy.sprite.get_width() // 2
            dx = enemy_center_x - missile_center_x
            if enemy.y < self.y:
                if abs(dx) > missile_homing_speed:
                    dx = missile_homing_speed if dx > 0 else -missile_homing_speed
                self.x += dx

class Enemy(GameObject):
    def __init__(self, surface, sprite, x, y):
        super().__init__(surface, sprite, x, y, 3)

    def move(self):
        self.y += self.speed

class Explosion:
    def __init__(self, x, y, sprite, time=30):
        self.x = x
        self.y = y
        self.sprite = sprite
        self.time = time  # Countdown timer

    def draw(self, surface):
        surface.blit(self.sprite, (self.x, self.y))

    def update(self):
        self.time -= 1
        return self.time > 0

# --- The Game Class ---
class Game:
    def __init__(self):
        # Initialise pygame and window
        pygame.init()
        self.screen_width, self.screen_height = 320, 480
        self.surface = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("gametest")
        self.clock = pygame.time.Clock()
        self.assets = AssetManager(self.screen_width, self.screen_height)
        self.bg_offset = 0  # For scrolling background

        # Entities and state
        self.player = Player(self.surface, self.assets.player_sprites,
                             (self.screen_width - self.assets.player_sprites["forward"].get_width()) // 2,
                             self.screen_height - self.assets.player_sprites["forward"].get_height())
        self.bullets = []
        self.missiles = []
        self.enemies = []
        self.enemy_bullets = []
        self.explosions = []
        self.score = 0
        self.player_health = 3
        self.player_lives = 3

        # Timers
        self.shoot_timer = 0
        self.shoot_delay = 8
        self.missile_cooldown = 0
        self.missile_delay = 480
        self.enemy_spawn_timer = 0
        self.enemy_spawn_delay = 40
        self.enemy_shoot_delay = 30

        # Audio: play a random soundtrack, set volumes for sfx
        self.current_soundtrack = random.choice(self.assets.sounds["soundtracks"])
        self.current_soundtrack.play(-1)
        self.assets.sounds["explosion, missile, gunshot"].set_volume(0.3)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.player.move(keys)
        # Player shooting (auto-fire)
        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_delay:
            px = self.player.x + self.player.sprite.get_width() // 2 - self.assets.player_bullet.get_width() // 2
            py = self.player.y
            self.bullets.append(Bullet(self.surface, self.assets.player_bullet, px, py, 10, -1))
            self.shoot_timer = 0
            self.assets.sounds["gunshot"].play()
        # Player missile (spacebar)
        if self.missile_cooldown > 0:
            self.missile_cooldown -= 1
        if keys[pygame.K_SPACE] and self.missile_cooldown == 0:
            mx = self.player.x + self.player.sprite.get_width() // 2 - self.assets.player_missile.get_width() // 2
            my = self.player.y
            self.missiles.append(Missile(self.surface, self.assets.player_missile, mx, my))
            self.missile_cooldown = self.missile_delay
            self.assets.sounds["missile"].play()

    def update(self):
        # Scroll background
        self.bg_offset += 1
        if self.bg_offset >= self.assets.bg.get_height():
            self.bg_offset = 0

        # Move player bullets and remove if off-screen
        self.bullets[:] = [b for b in self.bullets if b.y > -b.sprite.get_height() and not b.move()]

        # Move missiles and make them home in on closest enemy
        for missile in self.missiles[:]:
            missile.move()
            if missile.y < -missile.sprite.get_height():
                self.missiles.remove(missile)
                continue
            if self.enemies:
                closest_enemy = min(self.enemies, key=lambda e: math.hypot(
                    e.x + e.sprite.get_width() // 2 - (missile.x + missile.sprite.get_width() // 2),
                    e.y + e.sprite.get_height() // 2 - (missile.y + missile.sprite.get_height() // 2)
                ))
                missile.home_to(closest_enemy)

        # Spawn new enemies at intervals
        self.enemy_spawn_timer += 1.3
        if self.enemy_spawn_timer >= self.enemy_spawn_delay:
            ex = random.randint(0, self.screen_width - self.assets.enemy_sprite.get_width())
            self.enemies.append(Enemy(self.surface, self.assets.enemy_sprite, ex, 0))
            self.enemy_spawn_timer = 0
        # Move enemies and fire enemy bullets randomly
        for enemy in self.enemies[:]:
            enemy.move()
            if random.randint(0, self.enemy_shoot_delay-1) == 0:
                ex = enemy.x + enemy.sprite.get_width() // 2 - self.assets.enemy_bullet.get_width() // 2
                ey = enemy.y + enemy.sprite.get_height()
                self.enemy_bullets.append(Bullet(self.surface, self.assets.enemy_bullet, ex, ey, 7, 1))
            if enemy.y > self.screen_height:
                self.enemies.remove(enemy)

        # Move enemy bullets and remove if off-screen
        self.enemy_bullets[:] = [b for b in self.enemy_bullets if b.y < self.screen_height and not b.move()]

        # Handle all collisions
        self.handle_collisions()

        # Update explosions and remove finished ones
        self.explosions[:] = [exp for exp in self.explosions if exp.update()]

    def handle_collisions(self):
        # Player bullet-enemy collisions
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if bullet.get_rect().colliderect(enemy.get_rect()):
                    self.bullets.remove(bullet)
                    self.explosions.append(Explosion(
                        enemy.x + enemy.sprite.get_width() // 2 - self.assets.explosion.get_width() // 2,
                        enemy.y + enemy.sprite.get_height() // 2 - self.assets.explosion.get_height() // 2,
                        self.assets.explosion))
                    self.assets.sounds["explosion"].play()
                    self.enemies.remove(enemy)
                    self.score += 1
                    break
        # Missile-enemy collisions
        for missile in self.missiles[:]:
            for enemy in self.enemies[:]:
                if missile.get_rect().colliderect(enemy.get_rect()):
                    self.missiles.remove(missile)
                    self.explosions.append(Explosion(
                        enemy.x + enemy.sprite.get_width() // 2 - self.assets.explosion.get_width() // 2,
                        enemy.y + enemy.sprite.get_height() // 2 - self.assets.explosion.get_height() // 2,
                        self.assets.explosion))
                    self.assets.sounds["explosion"].play()
                    self.enemies.remove(enemy)
                    self.score += 1
                    break
        # Enemy bullet-player collisions
        for ebullet in self.enemy_bullets[:]:
            if ebullet.get_rect().colliderect(self.player.get_rect()):
                self.player_health -= 1
                self.enemy_bullets.remove(ebullet)
                if self.player_health <= 0:
                    self.player_lives -= 1
                    self.explosions.append(Explosion(
                        self.player.x + self.player.sprite.get_width() // 2 - self.assets.explosion.get_width() // 2,
                        self.player.y + self.player.sprite.get_height() // 2 - self.assets.explosion.get_height() // 2,
                        self.assets.explosion))
                    self.assets.sounds["explosion"].play()
                    pygame.display.update()
                    pygame.time.delay(500)
                    if self.player_lives <= 0:
                        self.running = False
                    else:
                        # Reset player position and health
                        self.player_health = 3
                        self.player.x = (self.screen_width - self.player.sprite.get_width()) // 2
                        self.player.y = self.screen_height - self.player.sprite.get_height()
                break
        # Enemy-player collisions
        for enemy in self.enemies[:]:
            if enemy.get_rect().colliderect(self.player.get_rect()):
                self.player_health -= 3
                self.enemies.remove(enemy)
                self.explosions.append(Explosion(
                    enemy.x + enemy.sprite.get_width() // 2 - self.assets.explosion.get_width() // 2,
                    enemy.y + enemy.sprite.get_height() // 2 - self.assets.explosion.get_height() // 2,
                    self.assets.explosion))
                self.assets.sounds["explosion"].play()
                pygame.display.update()
                if self.player_health <= 0:
                    self.player_lives -= 1
                    if self.player_lives <= 0:
                        self.running = False
                    else:
                        self.player_health = 3
                        self.player.x = (self.screen_width - self.player.sprite.get_width()) // 2
                        self.player.y = self.screen_height - self.player.sprite.get_height()
                break

    def draw(self):
        # Draw scrolling background
        bg_height = self.assets.bg.get_height()
        offset = int(self.bg_offset)
        self.surface.blit(self.assets.bg, (0, offset - bg_height))
        self.surface.blit(self.assets.bg, (0, offset))

        # Draw all game objects and explosions
        for obj_list in [self.bullets, self.missiles, self.enemies, self.enemy_bullets]:
            for obj in obj_list:
                obj.draw()
        for exp in self.explosions:
            exp.draw(self.surface)
        self.player.draw()

        # Draw HUD
        y = 5
        lives_text = self.assets.font.render(f"Lives: {self.player_lives}", True, (255,255,255))
        self.surface.blit(lives_text, (5, y))
        y += lives_text.get_height() + 5
        health_text = self.assets.font.render(f"Health: {self.player_health}", True, (255,255,255))
        self.surface.blit(health_text, (5, y))
        y += health_text.get_height() + 5
        score_text = self.assets.font.render(f"Score: {self.score}", True, (255,255,255))
        self.surface.blit(score_text, (5, y))

    def run(self):
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            self.handle_input()
            self.update()
            self.draw()
            pygame.display.update()
            self.clock.tick(60)
        pygame.quit()

if __name__ == "__main__":
    Game().run()