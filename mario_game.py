import pygame
import sys
import random

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE = 40
FPS = 60

GRAVITY = 0.8
PLAYER_SPEED = 5
JUMP_POWER = 15

SKY = (107, 140, 255)
GROUND = (139, 69, 19)
GRASS = (34, 139, 34)
BRICK = (180, 80, 40)
COIN = (255, 215, 0)
RED = (220, 40, 40)
BLUE = (40, 80, 220)
SKIN = (255, 200, 150)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (30, 170, 50)
FLAG_COLOR = (230, 30, 30)
PIPE = (20, 160, 60)
CLOUD = (245, 245, 255)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Super Plumber Bros")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 22, bold=True)
big_font = pygame.font.SysFont("arial", 48, bold=True)


LEVEL = [
    "                                                                                                                                        ",
    "                                                                                                                                        ",
    "      c                                                                                                                                 ",
    "                              c c c                                                                                                     ",
    "          BBCBB                                                                                                                         ",
    "                       BBB                     BCB                                                                                      ",
    "              c c                                                                                                                       ",
    "                                                                                              c c c                                     ",
    "                                        P                                                                                               ",
    "         BCBB            BB                        BBBB               BBBBB                                                             ",
    "                                                                                                                                        ",
    "                                 e              e                                       e                    e       F                  ",
    "GGGGGGGGGGGGGGGGGGGGGGGGG     GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG   GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
    "GGGGGGGGGGGGGGGGGGGGGGGGG     GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG   GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
]


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 30, 40)
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.facing = 1
        self.alive = True
        self.won = False
        self.anim = 0

    def update(self, solids, enemies, coins, flag, powerups):
        keys = pygame.key.get_pressed()
        self.vx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -PLAYER_SPEED
            self.facing = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = PLAYER_SPEED
            self.facing = 1
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vy = -JUMP_POWER
            self.on_ground = False

        self.vy += GRAVITY
        if self.vy > 18:
            self.vy = 18

        self.rect.x += int(self.vx)
        self._resolve(solids, axis="x")
        self.rect.y += int(self.vy)
        self.on_ground = False
        self._resolve(solids, axis="y")

        if self.vx != 0 and self.on_ground:
            self.anim = (self.anim + 1) % 20

        for e in enemies[:]:
            if not e.alive:
                continue
            if self.rect.colliderect(e.rect):
                if self.vy > 0 and self.rect.bottom - e.rect.top < 20:
                    e.alive = False
                    self.vy = -10
                    return "stomp"
                else:
                    self.alive = False
                    return "die"

        for c in coins[:]:
            if self.rect.colliderect(c):
                coins.remove(c)
                return "coin"

        if flag and self.rect.colliderect(flag):
            self.won = True
            return "win"

        if self.rect.top > SCREEN_HEIGHT + 200:
            self.alive = False
            return "die"

        return None

    def _resolve(self, solids, axis):
        for s in solids:
            if self.rect.colliderect(s):
                if axis == "x":
                    if self.vx > 0:
                        self.rect.right = s.left
                    elif self.vx < 0:
                        self.rect.left = s.right
                else:
                    if self.vy > 0:
                        self.rect.bottom = s.top
                        self.vy = 0
                        self.on_ground = True
                    elif self.vy < 0:
                        self.rect.top = s.bottom
                        self.vy = 0

    def draw(self, surf, cam):
        r = self.rect.move(-cam, 0)
        pygame.draw.rect(surf, RED, (r.x, r.y, r.width, 20))
        pygame.draw.rect(surf, BLUE, (r.x, r.y + 20, r.width, 20))
        pygame.draw.rect(surf, SKIN, (r.x + 6, r.y + 4, 18, 12))
        hat_x = r.x - 2 if self.facing == -1 else r.x + 14
        pygame.draw.rect(surf, RED, (hat_x, r.y - 4, 18, 8))
        eye_x = r.x + 8 if self.facing == -1 else r.x + 18
        pygame.draw.rect(surf, BLACK, (eye_x, r.y + 7, 3, 4))
        leg_offset = 0
        if self.on_ground and self.vx != 0:
            leg_offset = 3 if (self.anim // 5) % 2 == 0 else -3
        pygame.draw.rect(surf, BLACK, (r.x + 4, r.y + 36, 8, 4 + leg_offset))
        pygame.draw.rect(surf, BLACK, (r.x + 18, r.y + 36, 8, 4 - leg_offset))


class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.vx = -1.5
        self.vy = 0
        self.alive = True
        self.anim = 0

    def update(self, solids):
        if not self.alive:
            return
        self.vy += GRAVITY
        if self.vy > 18:
            self.vy = 18

        self.rect.x += int(self.vx)
        for s in solids:
            if self.rect.colliderect(s):
                if self.vx > 0:
                    self.rect.right = s.left
                else:
                    self.rect.left = s.right
                self.vx = -self.vx

        self.rect.y += int(self.vy)
        on_ground = False
        for s in solids:
            if self.rect.colliderect(s):
                if self.vy > 0:
                    self.rect.bottom = s.top
                    self.vy = 0
                    on_ground = True
                elif self.vy < 0:
                    self.rect.top = s.bottom
                    self.vy = 0

        if on_ground:
            probe = self.rect.move(int(self.vx * 8), 5)
            if not any(probe.colliderect(s) for s in solids):
                self.vx = -self.vx

        self.anim += 1

    def draw(self, surf, cam):
        if not self.alive:
            return
        r = self.rect.move(-cam, 0)
        pygame.draw.ellipse(surf, (120, 60, 20), (r.x, r.y + 4, r.width, r.height - 4))
        pygame.draw.rect(surf, (90, 45, 15), (r.x + 2, r.y + r.height - 8, 10, 6))
        pygame.draw.rect(surf, (90, 45, 15), (r.x + r.width - 12, r.y + r.height - 8, 10, 6))
        pygame.draw.circle(surf, WHITE, (r.x + 10, r.y + 14), 4)
        pygame.draw.circle(surf, WHITE, (r.x + r.width - 10, r.y + 14), 4)
        pygame.draw.circle(surf, BLACK, (r.x + 10, r.y + 14), 2)
        pygame.draw.circle(surf, BLACK, (r.x + r.width - 10, r.y + 14), 2)


def build_level():
    solids = []
    coins = []
    enemies = []
    flag = None
    player_start = (100, 400)
    for row, line in enumerate(LEVEL):
        for col, ch in enumerate(line):
            x, y = col * TILE, row * TILE
            if ch == "G":
                solids.append(pygame.Rect(x, y, TILE, TILE))
            elif ch == "B":
                solids.append(pygame.Rect(x, y, TILE, TILE))
            elif ch == "C":
                solids.append(pygame.Rect(x, y, TILE, TILE))
                coins.append(pygame.Rect(x + 10, y - TILE, 20, 20))
            elif ch == "c":
                coins.append(pygame.Rect(x + 10, y + 10, 20, 20))
            elif ch == "e":
                enemies.append(Enemy(x, y))
            elif ch == "F":
                flag = pygame.Rect(x + 15, y - TILE * 3, 10, TILE * 4)
            elif ch == "P":
                player_start = (x, y)
    return solids, coins, enemies, flag, player_start


def tile_type(row, col):
    if 0 <= row < len(LEVEL) and 0 <= col < len(LEVEL[row]):
        return LEVEL[row][col]
    return " "


def draw_level(surf, solids, cam):
    for row, line in enumerate(LEVEL):
        for col, ch in enumerate(line):
            x = col * TILE - cam
            y = row * TILE
            if x < -TILE or x > SCREEN_WIDTH:
                continue
            if ch == "G":
                pygame.draw.rect(surf, GROUND, (x, y, TILE, TILE))
                if row == 0 or tile_type(row - 1, col) != "G":
                    pygame.draw.rect(surf, GRASS, (x, y, TILE, 8))
                pygame.draw.line(surf, (90, 50, 10), (x, y), (x + TILE, y), 1)
            elif ch == "B" or ch == "C":
                pygame.draw.rect(surf, BRICK, (x, y, TILE, TILE))
                pygame.draw.rect(surf, (120, 50, 20), (x, y, TILE, TILE), 2)
                pygame.draw.line(surf, (120, 50, 20), (x, y + TILE // 2), (x + TILE, y + TILE // 2), 2)
                pygame.draw.line(surf, (120, 50, 20), (x + TILE // 2, y), (x + TILE // 2, y + TILE // 2), 2)
                pygame.draw.line(surf, (120, 50, 20), (x + TILE // 4, y + TILE // 2), (x + TILE // 4, y + TILE), 2)


def draw_coins(surf, coins, cam, frame):
    for c in coins:
        x = c.x - cam
        if -30 < x < SCREEN_WIDTH:
            phase = (frame // 6) % 4
            w = [20, 14, 6, 14][phase]
            cx = x + 10
            pygame.draw.ellipse(surf, COIN, (cx - w // 2, c.y, w, 20))
            pygame.draw.ellipse(surf, (200, 150, 0), (cx - w // 2, c.y, w, 20), 2)


def draw_flag(surf, flag, cam):
    if not flag:
        return
    x = flag.x - cam
    pygame.draw.rect(surf, (100, 100, 100), (x, flag.y, flag.width, flag.height))
    pygame.draw.polygon(surf, FLAG_COLOR, [(x + flag.width, flag.y + 10), (x + flag.width + 40, flag.y + 25), (x + flag.width, flag.y + 40)])


def draw_clouds(surf, cam, clouds):
    for cx, cy, size in clouds:
        x = cx - cam * 0.3
        x = x % (SCREEN_WIDTH + 200) - 100
        pygame.draw.ellipse(surf, CLOUD, (x, cy, size, size // 2))
        pygame.draw.ellipse(surf, CLOUD, (x + size // 3, cy - 10, size // 2, size // 2))
        pygame.draw.ellipse(surf, CLOUD, (x + size // 2, cy, size // 2, size // 2))


def draw_hud(surf, score, coins_got, lives, time_left):
    surf.blit(font.render(f"SCORE {score:06d}", True, WHITE), (20, 10))
    surf.blit(font.render(f"COINS {coins_got:02d}", True, WHITE), (220, 10))
    surf.blit(font.render(f"LIVES {lives}", True, WHITE), (400, 10))
    surf.blit(font.render(f"TIME {int(time_left)}", True, WHITE), (560, 10))


def center_text(surf, text, y, f=big_font, color=WHITE):
    img = f.render(text, True, color)
    surf.blit(img, (SCREEN_WIDTH // 2 - img.get_width() // 2, y))


def main():
    level_width = len(LEVEL[0]) * TILE
    clouds = [(random.randint(0, level_width), random.randint(20, 150), random.randint(60, 120)) for _ in range(20)]

    lives = 3
    score = 0
    coins_got = 0

    while lives > 0:
        solids, coins, enemies, flag, start = build_level()
        player = Player(*start)
        cam = 0
        frame = 0
        time_left = 300.0
        state = "playing"
        retry = False
        full_reset = False

        while not retry:
            dt = clock.tick(FPS) / 1000.0
            frame += 1
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_r and state != "playing":
                    retry = True
                    if state == "won":
                        full_reset = True

            if state == "playing":
                time_left -= dt
                if time_left <= 0:
                    state = "dead"

                result = player.update(solids, enemies, coins, flag, [])
                if result == "coin":
                    coins_got += 1
                    score += 100
                    if coins_got >= 100:
                        coins_got = 0
                        lives += 1
                elif result == "stomp":
                    score += 200
                elif result == "die":
                    state = "dead"
                elif result == "win":
                    state = "won"
                    score += int(time_left) * 10

                for e in enemies:
                    e.update(solids)

                target_cam = player.rect.centerx - SCREEN_WIDTH // 2
                cam += (target_cam - cam) * 0.12
                cam = max(0, min(cam, level_width - SCREEN_WIDTH))

            screen.fill(SKY)
            draw_clouds(screen, cam, clouds)
            draw_level(screen, solids, int(cam))
            draw_flag(screen, flag, int(cam))
            draw_coins(screen, coins, int(cam), frame)
            for e in enemies:
                e.draw(screen, int(cam))
            player.draw(screen, int(cam))
            draw_hud(screen, score, coins_got, lives, time_left)

            if state == "dead":
                center_text(screen, "GAME OVER" if lives <= 1 else "YOU DIED", 220)
                center_text(screen, "Press R to retry", 290, font)
            elif state == "won":
                center_text(screen, "LEVEL CLEAR!", 220, big_font, COIN)
                center_text(screen, f"Final score: {score}", 280, font)
                center_text(screen, "Press R to play again", 320, font)

            pygame.display.flip()

        if full_reset:
            score = 0
            coins_got = 0
            lives = 3
        elif state == "dead":
            lives -= 1

    screen.fill(BLACK)
    center_text(screen, "GAME OVER", 240)
    center_text(screen, f"Final score: {score}", 300, font)
    pygame.display.flip()
    pygame.time.wait(2500)
    pygame.quit()


if __name__ == "__main__":
    main()
