import pygame
import random
import math

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
    def __init__(self, surface, moving_forward_sprite, moving_left_sprite, moving_right_sprite, xPos, yPos, speed=5):
        super().__init__(surface, moving_forward_sprite, xPos, yPos, speed)
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

    def update(self):
        self._yPos -= self._speed

class Enemy(GameObject):
    def __init__(self, surface, sprite, xPos, yPos):
        super().__init__(surface, sprite, xPos, yPos, 3)

    def update(self):
        self._yPos += self._speed

class EnemyBullet(GameObject):
    def __init__(self, surface, sprite, xPos, yPos):
        super().__init__(surface, sprite, xPos, yPos, 7)

    def update(self):
        self._yPos += self._speed

class PlayerMissile(GameObject):
    def __init__(self, surface, sprite, xPos, yPos):
        super().__init__(surface, sprite, xPos, yPos, 14)

    def update(self):
        self._yPos -= self._speed

class Explosion:
    def __init__(self, x, y, duration):
        self.x = x
        self.y = y
        self.timer = duration

    def update(self):
        self.timer -= 1

class Game:
    def __init__(self):
        pygame.init()
        self.__screenWidth = 320
        self.__screenHeight = 480
        self.__surface = pygame.display.set_mode((self.screenWidth, self.screenHeight))
        pygame.display.set_caption("gametest")

        self.__clock = pygame.time.Clock()
        self.__cSpeed = 60

        self.__font = pygame.font.SysFont(None, 28)
        # Game state
        self.score = 0
        self.player_health = 3
        self.player_max_health = 3
        self.player_lives = 3
        self.bg_offset = 0

        # Timers
        self.shoot_delay = 8
        self.shoot_timer = 0
        self.missile_delay = 400
        self.missile_cooldown = 0
        self.enemy_spawn_delay = 40
        self.enemy_spawn_timer = 0
        self.enemy_shoot_delay = 30
        self.explosion_time = 30
        self.missile_homing_speed = 8

        # Load resources
        self.load_resources()

        # Create player
        self.player = Player(
            self.surface,
            self.playerMovingForwardSprite,
            self.playerMovingLeftSprite,
            self.playerMovingRightSprite,
            (self.screenWidth - self.playerMovingForwardSprite.get_width()) // 2,
            self.screenHeight - self.playerMovingForwardSprite.get_height()
        )

        # Lists of objects
        self.bullets = []
        self.missiles = []
        self.enemies = []
        self.enemyBullets = []
        self.explosions = []

        # Play soundtrack
        self.play_soundtrack()

    def load_resources(self):
        self.BG = pygame.image.load("Intro/libraryofimages/water.jpg").convert()
        self.BG = pygame.transform.scale(self.BG, (self.screenWidth, self.screenHeight))
        self.playerMovingForwardSprite = pygame.image.load("Intro/libraryofimages/FA-18moving.png").convert_alpha()
        self.playerMovingLeftSprite = pygame.image.load("Intro/libraryofimages/FA-18movingleft.png").convert_alpha()
        self.playerMovingRightSprite = pygame.image.load("Intro/libraryofimages/FA-18movingright.png").convert_alpha()
        bullet_width, bullet_height = 4, 6
        self.playerBulletSprite = pygame.Surface((bullet_width, bullet_height), pygame.SRCALPHA)
        self.playerBulletSprite.fill((255, 255, 0))
        self.bullet_width = bullet_width
        self.bullet_height = bullet_height
        self.gunshotSound = pygame.mixer.Sound("Intro/fx/gunshot-fx-zap.wav")
        missile_width, missile_height = 6, 12
        self.playerMissileSprite = pygame.Surface((missile_width, missile_height), pygame.SRCALPHA)
        self.playerMissileSprite.fill((255, 0, 0))
        self.missile_width = missile_width
        self.missile_height = missile_height
        self.missileSound = pygame.mixer.Sound("Intro/fx/launching-missile-313226.mp3")
        self.enemySprite = pygame.image.load("Intro/libraryofimages/enemyF-4.png").convert_alpha()
        enemyBullet_width, enemyBullet_height = 4, 6
        self.enemyBulletSprite = pygame.Surface((enemyBullet_width, enemyBullet_height), pygame.SRCALPHA)
        self.enemyBulletSprite.fill((0, 255, 255))
        self.enemyBullet_width = enemyBullet_width
        self.enemyBullet_height = enemyBullet_height
        self.explosionSprite = pygame.image.load("Intro/libraryofimages/explosion_Boom_2.png").convert_alpha()
        self.explosionSprite = pygame.transform.scale(self.explosionSprite, (32, 32))
        self.explosionSound = pygame.mixer.Sound("Intro/fx/dry-explosion-fx.wav")
        self.audiopath = {
            i: pygame.mixer.Sound(f"Intro/soundtrack/soundtrack{i}.mp3")
            for i in range(1, 8)
        }
        for snd in self.audiopath.values():
            snd.set_volume(0.70)
        self.explosionSound.set_volume(0.3)
        self.gunshotSound.set_volume(0.1)
        self.missileSound.set_volume(0.5)

    def play_soundtrack(self):
        self.soundtrack_choice = random.randint(1, 7)
        self.current_soundtrack = self.audiopath[self.soundtrack_choice]
        self.current_soundtrack.play(-1)
        print(f"Current soundtrack: Soundtrack {self.soundtrack_choice}")

    def draw(self):
        bg_offset_int = int(self.bg_offset)
        BG_height = self.BG.get_height()
        self.surface.blit(self.BG, (0, bg_offset_int - BG_height))
        self.surface.blit(self.BG, (0, bg_offset_int))

        for bullet in self.bullets:
            bullet.drawSprite()
        for missile in self.missiles:
            missile.drawSprite()
        for enemy in self.enemies:
            enemy.drawSprite()
        for ebullet in self.enemyBullets:
            ebullet.drawSprite()
        for exp in self.explosions:
            self.surface.blit(self.explosionSprite, (exp.x, exp.y))
        self.player.drawSprite()
        # Draw lives, health, score
        lives_text = self.font.render(f"Lives: {self.player_lives}", True, (255, 255, 255))
        self.surface.blit(lives_text, (5, 5))
        health_text = self.font.render(f"Health: {self.player_health}", True, (255, 255, 255))
        self.surface.blit(health_text, (5, 5 + lives_text.get_height() + 5))
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.surface.blit(score_text, (5, 5 + lives_text.get_height() + health_text.get_height() + 10))

    def spawn_enemy(self):
        enemy_x = random.randint(0, self.screenWidth - self.enemySprite.get_width())
        self.enemies.append(Enemy(self.surface, self.enemySprite, enemy_x, 0))

    def update(self):
        keys = pygame.key.get_pressed()
        self.player.Movement(keys)

        # Scrolling background
        self.bg_offset += 1
        if self.bg_offset >= self.BG.get_height():
            self.bg_offset = 0

        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_delay:
            bullet_x = self.player.getXPos() + self.playerMovingForwardSprite.get_width() // 2 - self.bullet_width // 2
            bullet_y = self.player.getYPos()
            self.bullets.append(PlayerBullet(self.surface, self.playerBulletSprite, bullet_x, bullet_y))
            self.shoot_timer = 0
            self.gunshotSound.play()

        # Missile
        if self.missile_cooldown > 0:
            self.missile_cooldown -= 1
        if keys[pygame.K_SPACE] and self.missile_cooldown == 0:
            missile_x = self.player.getXPos() + self.playerMovingForwardSprite.get_width() // 2 - self.missile_width // 2
            missile_y = self.player.getYPos()
            self.missiles.append(PlayerMissile(self.surface, self.playerMissileSprite, missile_x, missile_y))
            self.missile_cooldown = self.missile_delay
            self.missileSound.play()

        # Player bullets movement
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.getYPos() < -self.bullet_height:
                self.bullets.remove(bullet)

        # Missiles
        for missile in self.missiles[:]:
            missile.update()
            if missile.getYPos() < -self.missile_height:
                self.missiles.remove(missile)
                continue
            if self.enemies:
                closest_enemy = min(self.enemies, key=lambda e: math.hypot(
                    e.getXPos() + self.enemySprite.get_width() // 2 - (missile.getXPos() + self.missile_width // 2),
                    e.getYPos() + self.enemySprite.get_height() // 2 - (missile.getYPos() + self.missile_height // 2)
                ))
                missile_center_x = missile.getXPos() + self.missile_width // 2
                enemy_center_x = closest_enemy.getXPos() + self.enemySprite.get_width() // 2
                dx = enemy_center_x - missile_center_x
                if closest_enemy.getYPos() < missile.getYPos():
                    if abs(dx) > self.missile_homing_speed:
                        dx = self.missile_homing_speed if dx > 0 else -self.missile_homing_speed
                    missile._xPos += dx

        # Enemy Spawning
        self.enemy_spawn_timer += 1.3
        if self.enemy_spawn_timer >= self.enemy_spawn_delay:
            self.spawn_enemy()
            self.enemy_spawn_timer = 0

        # Enemies and Enemy shooting
        for enemy in self.enemies[:]:
            enemy.update()
            if random.randint(0, self.enemy_shoot_delay - 1) == 0:
                ebullet_x = enemy.getXPos() + self.enemySprite.get_width() // 2 - self.enemyBullet_width // 2
                ebullet_y = enemy.getYPos() + self.enemySprite.get_height()
                self.enemyBullets.append(EnemyBullet(self.surface, self.enemyBulletSprite, ebullet_x, ebullet_y))
            if enemy.getYPos() > self.screenHeight:
                self.enemies.remove(enemy)

        # Enemy Bullets
        for ebullet in self.enemyBullets[:]:
            ebullet.update()
            if ebullet.getYPos() > self.screenHeight:
                self.enemyBullets.remove(ebullet)

        # Bullet-enemy collisions
        for bullet in self.bullets[:]:
            bullet_rect = bullet.get_rect()
            for enemy in self.enemies[:]:
                enemy_rect = enemy.get_rect()
                if bullet_rect.colliderect(enemy_rect):
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    if enemy in self.enemies:
                        explosion_x = enemy.getXPos() + self.enemySprite.get_width() // 2 - self.explosionSprite.get_width() // 2
                        explosion_y = enemy.getYPos() + self.enemySprite.get_height() // 2 - self.explosionSprite.get_height() // 2
                        self.explosions.append(Explosion(explosion_x, explosion_y, self.explosion_time))
                        self.explosionSound.play()
                        self.enemies.remove(enemy)
                        self.score += 1

        # Missile-enemy collisions
        for missile in self.missiles[:]:
            missile_rect = missile.get_rect()
            for enemy in self.enemies[:]:
                if missile_rect.colliderect(enemy.get_rect()):
                    if missile in self.missiles:
                        self.missiles.remove(missile)
                    if enemy in self.enemies:
                        explosion_x = enemy.getXPos() + self.enemySprite.get_width() // 2 - self.explosionSprite.get_width() // 2
                        explosion_y = enemy.getYPos() + self.enemySprite.get_height() // 2 - self.explosionSprite.get_height() // 2
                        self.explosions.append(Explosion(explosion_x, explosion_y, self.explosion_time))
                        self.explosionSound.play()
                        self.enemies.remove(enemy)
                        self.score += 1
                    break

        # Enemy bullet-player collisions
        for ebullet in self.enemyBullets[:]:
            if ebullet.get_rect().colliderect(self.player.get_rect()):
                self.player_health -= 1
                self.enemyBullets.remove(ebullet)
                if self.player_health <= 0:
                    self.player_lives -= 1
                    explosion_x = self.player.getXPos() + self.playerMovingForwardSprite.get_width() // 2 - self.explosionSprite.get_width() // 2
                    explosion_y = self.player.getYPos() + self.playerMovingForwardSprite.get_height() // 2 - self.explosionSprite.get_height() // 2
                    self.explosions.append(Explosion(explosion_x, explosion_y, self.explosion_time))
                    self.explosionSound.play()
                    pygame.display.update()
                    pygame.time.delay(500)
                    if self.player_lives <= 0:
                        return False
                    else:
                        self.player_health = self.player_max_health
                        self.player._xPos = (self.screenWidth - self.playerMovingForwardSprite.get_width()) // 2
                        self.player._yPos = self.screenHeight - self.playerMovingForwardSprite.get_height()
                break

        # Enemy plane-player collisions
        for enemy in self.enemies[:]:
            if enemy.get_rect().colliderect(self.player.get_rect()):
                self.player_health -= 3
                self.enemies.remove(enemy)
                explosion_x = enemy.getXPos() + self.enemySprite.get_width() // 2 - self.explosionSprite.get_width() // 2
                explosion_y = enemy.getYPos() + self.enemySprite.get_height() // 2 - self.explosionSprite.get_height() // 2
                self.explosions.append(Explosion(explosion_x, explosion_y, self.explosion_time))
                self.explosionSound.play()
                pygame.display.update()
                pygame.time.delay(500)
                if self.player_health <= 0:
                    self.player_lives -= 1
                    if self.player_lives <= 0:
                        return False
                    else:
                        self.player_health = self.player_max_health
                        self.player._xPos = (self.screenWidth - self.playerMovingForwardSprite.get_width()) // 2
                        self.player._yPos = self.screenHeight - self.playerMovingForwardSprite.get_height()
                break

        # Update and remove finished explosions
        for exp in self.explosions[:]:
            exp.update()
            if exp.timer <= 0:
                self.explosions.remove(exp)

        return True

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            running = self.update()
            self.draw()
            pygame.display.update()
            self.clock.tick(self.cSpeed)

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()