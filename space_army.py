import pygame
import random
import math

# --- Developer Information ---
# Developer: Michał Matsalak
# Email: matsalakmichal@gmail.com
# GitHub: https://github.com/Michael21Official
# --- End of Developer Information ---

class SpaceShip(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("spaceship.png")
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.original_image = self.image
        self.rect = self.image.get_rect(center=(512, 384))
        self.speed = 3
        self.angle = 0
        self.max_bullets = 33
        self.current_bullets = self.max_bullets

    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.angle += 5
        if keys[pygame.K_RIGHT]:
            self.angle -= 5
        if keys[pygame.K_UP]:
            self.rect.x += self.speed * math.cos(math.radians(-self.angle))
            self.rect.y += self.speed * math.sin(math.radians(-self.angle))
        if keys[pygame.K_DOWN]:
            self.rect.x -= self.speed * math.cos(math.radians(-self.angle))
            self.rect.y -= self.speed * math.sin(math.radians(-self.angle))

        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.clamp_ip(pygame.Rect(0, 0, 1024, 768))

    def shoot(self):
        if self.current_bullets > 0:
            self.current_bullets -= 1
            return Bullet(self.rect.centerx, self.rect.centery, self.angle)
        return None


class Meteor(pygame.sprite.Sprite):
    def __init__(self, target):
        super().__init__()
        self.image = pygame.image.load("meteor.png")
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect(center=(random.choice([0, 1024]), random.randint(0, 768)))
        self.speed = random.uniform(1, 2)
        self.target = target

        dx, dy = self.target.rect.centerx - self.rect.centerx, self.target.rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)
        self.velocity = (dx / distance * self.speed, dy / distance * self.speed)

    def update(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

        if not pygame.Rect(0, 0, 1024, 768).colliderect(self.rect):
            self.kill()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.animation_frames = [
            "shoot1.png", "shoot2.png", "shoot3.png", "shoot4.png"
        ]
        self.animation_index = 0
        self.image = pygame.image.load(self.animation_frames[self.animation_index])
        self.original_width, self.original_height = self.image.get_size()
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10
        self.angle = angle
        self.dx = self.speed * math.cos(math.radians(-self.angle))
        self.dy = self.speed * math.sin(math.radians(-self.angle))
        self.animation_time = 0

        self.image = pygame.transform.scale(self.image, (self.original_width // 2, self.original_height // 2))

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

        self.animation_time += 1
        if self.animation_time % 5 == 0:
            self.animation_index += 1
            if self.animation_index >= len(self.animation_frames):
                self.animation_index = 0

        self.image = pygame.image.load(self.animation_frames[self.animation_index])
        self.image = pygame.transform.scale(self.image, (self.original_width // 2, self.original_height // 2))
        self.image = pygame.transform.rotate(self.image, self.angle)

        if not pygame.Rect(0, 0, 1024, 768).colliderect(self.rect):
            self.kill()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.animation_frames = [
            "explosion1.png", "explosion2.png", "explosion3.png",
            "explosion4.png", "explosion5.png", "explosion6.png"
        ]
        self.animation_index = 0
        self.image = pygame.image.load(self.animation_frames[self.animation_index])
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect(center=(x, y))
        self.last_update = pygame.time.get_ticks()

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update > 100:
            self.animation_index += 1
            self.last_update = current_time

        if self.animation_index >= len(self.animation_frames):
            self.kill()
        else:
            self.image = pygame.image.load(self.animation_frames[self.animation_index])
            self.image = pygame.transform.scale(self.image, (100, 100))


def main():
    pygame.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((1024, 768))
    pygame.display.set_caption("Kosmiczne Wojsko")
    clock = pygame.time.Clock()

    background = pygame.image.load("kosmos.png")
    background = pygame.transform.scale(background, (1024, 768))

    shoot_sound = pygame.mixer.Sound("shoot.mp3")
    explosion_sound = pygame.mixer.Sound("explosion.mp3")

    all_sprites = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    meteors = pygame.sprite.Group()
    explosions = pygame.sprite.Group()

    spaceship = SpaceShip()
    all_sprites.add(spaceship)

    running = True
    score = 0
    font = pygame.font.Font(None, 36)

    game_over = False
    game_over_font = pygame.font.Font(None, 72)

    while running:
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    bullet = spaceship.shoot()
                    if bullet:
                        all_sprites.add(bullet)
                        bullets.add(bullet)
                        shoot_sound.play()

        if len(meteors) < 6 and not game_over:
            meteor = Meteor(spaceship)
            all_sprites.add(meteor)
            meteors.add(meteor)

        if not game_over:
            spaceship.update(keys)

        bullets.update()
        meteors.update()
        explosions.update()

        hits = pygame.sprite.groupcollide(meteors, bullets, True, True)
        for hit in hits:
            score += 1
            explosion = Explosion(hit.rect.centerx, hit.rect.centery)
            all_sprites.add(explosion)
            explosions.add(explosion)
            explosion_sound.play()

        if pygame.sprite.spritecollideany(spaceship, meteors) and not game_over:
            explosion = Explosion(spaceship.rect.centerx, spaceship.rect.centery)
            all_sprites.add(explosion)
            explosions.add(explosion)
            explosion_sound.play()
            game_over = True

        screen.blit(background, (0, 0))
        all_sprites.draw(screen)

        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

        remaining_bullets_text = font.render(f"Pozostałe Strzały: {spaceship.current_bullets}", True, (255, 255, 255))
        screen.blit(remaining_bullets_text, (10, 50))

        if game_over:
            game_over_text = game_over_font.render("GAME OVER", True, (255, 0, 0))
            screen.blit(game_over_text, (300, 350))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()
