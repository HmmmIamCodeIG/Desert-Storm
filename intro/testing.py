import unittest
import pygame
import math
from mainfile import GameObject, Player, Projectile, Enemy, spawn_explosion_at_object

# Mock Pygame init for headless testing
pygame.init()
screen = pygame.display.set_mode((320, 480))
mock_sprite = pygame.Surface((10, 10))

class TestGameObject(unittest.TestCase):
    def test_position_set_and_get(self): # checking if the class correctly stores and returns its position
        obj = GameObject(screen, mock_sprite, 100, 150, 5)
        self.assertEqual(obj.getXPos(), 100)
        self.assertEqual(obj.getYPos(), 150)
        self.assertEqual(obj.getPos(), (100, 150))

    def test_get_rect(self):  # if the rectangle matches expected coordinates
        obj = GameObject(screen, mock_sprite, 50, 60, 0)
        rect = obj.get_rect()
        self.assertEqual(rect.topleft, (50, 60))
        self.assertEqual(rect.width, 10)
        self.assertEqual(rect.height, 10)

# verify movement logic
class TestProjectile(unittest.TestCase):
    def test_projectile_movement_up(self): 
        proj = Projectile(screen, mock_sprite, 100, 100, direction="up")
        proj.Movement()
        self.assertEqual(proj.getYPos(), 90)

    def test_projectile_movement_down(self):
        proj = Projectile(screen, mock_sprite, 100, 100, direction="down")
        proj.Movement()
        self.assertEqual(proj.getYPos(), 110)

# Checks if player position is kept within screen bounds and health and respawn system works
class TestPlayer(unittest.TestCase):
    def setUp(self):
        self.player = Player(
            screen,
            mock_sprite, mock_sprite, mock_sprite,
            100, 400
        )

    def test_movement_bounds(self):
        screen_width, screen_height = screen.get_size()
        self.player._xPos = -50
        self.player._yPos = -50
        self.player.Movement({})
        self.assertGreaterEqual(self.player.getXPos(), 0)
        self.assertGreaterEqual(self.player.getYPos(), 0)

    def test_update_health_death_and_respawn(self):
        self.player.health = 1
        self.player.lives = 2
        explosions = []
        mock_sound = pygame.mixer.Sound(buffer=b"\x00\x00")  # Silent sound
        spawn_explosion_at_object(self.player, mock_sprite, explosions, 30, mock_sound)
        self.player.update_health(-2, explosions, mock_sprite, 30, mock_sound)
        self.assertEqual(self.player.lives, 1)
        self.assertEqual(self.player.health, 3)

class TestEnemy(unittest.TestCase):
    def setUp(self): # check enemy positions and 
        self.enemy = Enemy(screen, mock_sprite, 100, 100)
        self.enemy2 = Enemy(screen, mock_sprite, 120, 100)
        self.bullets = []
        self.missiles = []
        self.enemies = [self.enemy, self.enemy2]
        self.enemyBullets = []
        self.explosions = []
        self.mock_sound = pygame.mixer.Sound(buffer=b"\x00\x00")
        self.score_ref = [0]

    def test_collision_with_missile(self): # check collision with the missiles
        missile = Projectile(screen, mock_sprite, 100, 100)
        self.missiles.append(missile)
        self.enemy.handle_collisions(self.enemies, self.missiles, self.bullets, mock_sprite, self.explosions, 30, self.mock_sound, self.score_ref)
        self.assertEqual(len(self.enemies), 1)
        self.assertEqual(self.score_ref[0], 1)

    def test_shooting_probability(self): # check collision with the bullet
        count = 0
        for _ in range(1000):
            e = Enemy(screen, mock_sprite, 100, 0)
            e.move_and_shoot(self.enemyBullets, mock_sprite, 5, 10)
            count += len(self.enemyBullets)
            self.enemyBullets.clear()
        self.assertTrue(10 <= count <= 30)  

### Grey Box: Test Missile Homing Logic ###
class TestMissileHoming(unittest.TestCase):
    def test_missile_homing_accuracy(self):
        missile = Projectile(screen, mock_sprite, 100, 200)
        enemy = Enemy(screen, mock_sprite, 110, 100)
        missile_homing_speed = 8

        # Horizontal movement toward enemy
        dx = (enemy.getXPos() + mock_sprite.get_width() // 2) - (missile.getXPos() + mock_sprite.get_width() // 2)
        dx_capped = max(-missile_homing_speed, min(missile_homing_speed, dx))
        missile._xPos += dx_capped
        self.assertTrue(abs(missile.getXPos() - enemy.getXPos()) <= missile_homing_speed)


if __name__ == '__main__':
    unittest.main()

