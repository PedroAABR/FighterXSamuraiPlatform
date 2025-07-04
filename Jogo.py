import math
import random
import pgzrun
from pygame import Rect
from pgzero.actor import Actor

# --- Game Constants ---
WIDTH = 800
HEIGHT = 600
GRAVITY = 0.5
PLAYER_JUMP_VELOCITY = -12
PLAYER_WALK_SPEED = 3
PLAYER_RUN_SPEED = 6
ENEMY_WALK_SPEED = 1.5
ENEMY_RUN_SPEED = 4
MAX_FALL_SPEED = 10
ENEMY_SIGHT_RANGE = 200
ENEMY_ATTACK_COOLDOWN = 1.5
ENEMY_EDGE_DETECTION_OFFSET = 5
PROJECTILE_SPEED = 8
ATTACK_COOLDOWN = 0.5

# --- Game States ---
GAME_STATE_MENU = 0
GAME_STATE_PLAYING = 1
GAME_STATE_GAME_OVER = 2
GAME_STATE_VICTORY = 3
current_game_state = GAME_STATE_MENU

# --- Global Objects ---
player = None
platforms = []
enemies = []
projectiles = []
score = 0
coin = None
is_coin_collected = False
enemies_defeated = 0
music_on = True

# --- Classes ---
class GameObject:
    def __init__(self, x, y, width, height):
        self.rect = Rect(x, y, width, height)
        self.animation_frames_names = []
        self.current_frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 0.1

    def set_animation_frames(self, frame_names):
        if self.animation_frames_names != frame_names:
            self.animation_frames_names = frame_names
            self.current_frame_index = 0
            self.animation_timer = 0

    def animate(self, dt):
        if not self.animation_frames_names or len(self.animation_frames_names) <= 1:
            self.current_frame_index = 0
            return
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame_index = (self.current_frame_index + 1) % len(self.animation_frames_names)

    def draw(self):
        if not self.animation_frames_names:
            screen.draw.rect(self.rect, (255, 0, 0))
            return
        current_image_name = self.animation_frames_names[self.current_frame_index]
        try:
            actor_to_draw = Actor(current_image_name)
            actor_to_draw.pos = self.rect.center
            if hasattr(self, 'invincibility_timer') and self.invincibility_timer > 0:
                if int(self.invincibility_timer * 10) % 2 == 0:
                    actor_to_draw.draw()
            else:
                actor_to_draw.draw()
        except Exception as e:
            print(f"Erro de criar Actor do '{current_image_name}': {e}.")
            screen.draw.rect(self.rect, (255, 0, 0))

class Player(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 40, 60)
        self.vx, self.vy = 0, 0
        self.on_ground = False
        self.is_moving = False
        self.is_running = False
        self.facing_right = True
        self.attack_cooldown = 0
        self.is_attacking = False
        self.attack_animation_timer = 0
        
        self.health = 5
        self.max_health = 5
        self.invincibility_timer = 0.0

        self.attack_right_frames = ["hero_attack_right_0", "hero_attack_right_1"]
        self.attack_left_frames = ["hero_attack_left_0", "hero_attack_left_1"]
        self.idle_right_frames = ["hero_idle_right_0", "hero_idle_right_1"]
        self.idle_left_frames = ["hero_idle_left_0", "hero_idle_left_1"]
        self.walk_right_frames = ["hero_walk_right_0", "hero_walk_right_1"]
        self.walk_left_frames = ["hero_walk_left_0", "hero_walk_left_1"]
        self.run_right_frames = ["hero_run_right_0", "hero_run_right_1"]
        self.run_left_frames = ["hero_run_left_0", "hero_run_left_1"]
        self.set_animation_frames(self.idle_right_frames)

    def update(self, dt, platforms):
        if self.attack_cooldown > 0: self.attack_cooldown -= dt
        if self.attack_animation_timer > 0:
            self.attack_animation_timer -= dt
            if self.attack_animation_timer <= 0: self.is_attacking = False
        if self.invincibility_timer > 0: self.invincibility_timer -= dt
        
        if not self.is_attacking:
            current_speed = PLAYER_RUN_SPEED if self.is_running else PLAYER_WALK_SPEED
            if keyboard.left: self.vx, self.facing_right, self.is_moving = -current_speed, False, True
            elif keyboard.right: self.vx, self.facing_right, self.is_moving = current_speed, True, True
            else: self.vx, self.is_moving = 0, False
        else:
             self.vx, self.is_moving = 0, False

        self.vy += GRAVITY
        if self.vy > MAX_FALL_SPEED: self.vy = MAX_FALL_SPEED
        self.rect.y += self.vy

        self.on_ground = False
        for p in platforms:
            if self.rect.colliderect(p.rect) and self.vy > 0:
                self.rect.bottom = p.rect.top
                self.vy, self.on_ground = 0, True

        self.rect.x += self.vx
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vx > 0: self.rect.right = p.rect.left
                elif self.vx < 0: self.rect.left = p.rect.right

        if self.is_attacking:
            self.set_animation_frames(self.attack_right_frames if self.facing_right else self.attack_left_frames)
        elif self.is_moving:
            if self.is_running: self.set_animation_frames(self.run_right_frames if self.facing_right else self.run_left_frames)
            else: self.set_animation_frames(self.walk_right_frames if self.facing_right else self.walk_left_frames)
        else:
            self.set_animation_frames(self.idle_right_frames if self.facing_right else self.idle_left_frames)
            
        self.animate(dt)

    def take_damage(self, amount):
        if self.invincibility_timer <= 0:
            self.health -= amount
            self.invincibility_timer = 1.5
            if music_on:
                try: sounds.player_hit.play()
                except Exception: pass

    def jump(self):
        if self.on_ground and not self.is_attacking and music_on:
            self.vy = PLAYER_JUMP_VELOCITY
            try: sounds.jump_sound.play()
            except Exception as e: print(f"Não pode tocar o som de pulo: {e}")

    def shoot(self):
        if self.attack_cooldown <= 0:
            self.attack_cooldown = ATTACK_COOLDOWN
            self.is_attacking = True
            self.attack_animation_timer = 0.3
            if music_on:
                try: sounds.shoot_sound.play()
                except Exception as e: print(f"Não pode tocar o som de tiro: {e}")
            projectiles.append(Projectile(self.rect.centerx, self.rect.centery, self.facing_right))

    def on_key_down(self, key):
        if key == keys.SPACE: self.jump()
        if key == keys.LSHIFT or key == keys.RSHIFT: self.is_running = True
        if key == keys.Z: self.shoot()

    def on_key_up(self, key):
        if key == keys.LSHIFT or key == keys.RSHIFT: self.is_running = False

class Enemy(GameObject):
    def __init__(self, x, y, patrol_start_x, patrol_end_x):
        super().__init__(x, y, 40, 60)
        self.vx, self.vy = 0, 0
        self.on_ground = False
        self.cooldown_timer = 0.0
        self.patrol_start_x, self.patrol_end_x = patrol_start_x, patrol_end_x
        self.facing_right = True
        self.health = 3
        self.is_aggro = False
        
        self.DEAGGRO_TIME = 5.0
        self.deaggro_timer = 0.0
        
        self.STATE_PATROLLING, self.STATE_WAITING, self.STATE_ATTACKING = 'patrolling', 'waiting', 'attacking'
        self.state = self.STATE_PATROLLING
        self.patrol_timer = random.uniform(3.0, 6.0)
        self.wait_timer = 0.0

        self.attack_right_frames = ["enemy_attack_right_0", "enemy_attack_right_1"]
        self.attack_left_frames = ["enemy_attack_left_0", "enemy_attack_left_1"]
        self.idle_right_frames = ["enemy_idle_right_0", "enemy_idle_right_1"]
        self.idle_left_frames = ["enemy_idle_left_0", "enemy_idle_left_1"]
        self.walk_right_frames = ["enemy_walk_right_0", "enemy_walk_right_1"]
        self.walk_left_frames = ["enemy_walk_left_0", "enemy_walk_left_1"]
        self.run_right_frames = ["enemy_run_right_0", "enemy_run_right_1"]
        self.run_left_frames = ["enemy_run_left_0", "enemy_run_left_1"]
        self.set_animation_frames(self.walk_right_frames)

    def on_hit(self):
        if self.health > 0:
            self.health -= 1
            self.is_aggro = True
            self.deaggro_timer = self.DEAGGRO_TIME

    def update(self, dt, player, platforms):
        if self.cooldown_timer > 0: self.cooldown_timer -= dt

        if self.state == self.STATE_ATTACKING and self.current_frame_index == len(self.animation_frames_names) - 1:
            self.state = self.STATE_PATROLLING

        self.vy += GRAVITY
        if self.vy > MAX_FALL_SPEED: self.vy = MAX_FALL_SPEED
        self.rect.y += self.vy

        self.on_ground = False
        for p in platforms:
            if self.rect.colliderect(p.rect) and self.vy >= 0:
                self.rect.bottom = p.rect.top
                self.vy, self.on_ground = 0, True

        distance_to_player = math.hypot(self.rect.centerx - player.rect.centerx, self.rect.centery - player.rect.centery)
        in_sight = distance_to_player < ENEMY_SIGHT_RANGE and abs(self.rect.y - player.rect.y) < 50
        
        if self.is_aggro:
            if in_sight:
                self.deaggro_timer = self.DEAGGRO_TIME
            else:
                self.deaggro_timer -= dt
                if self.deaggro_timer <= 0:
                    self.is_aggro = False
        
        is_pursuing = in_sight or self.is_aggro
        
        if self.rect.colliderect(player.rect) and self.cooldown_timer <= 0:
            self.state = self.STATE_ATTACKING
            self.cooldown_timer = ENEMY_ATTACK_COOLDOWN
            player.take_damage(1)
        
        target_vx = 0
        current_frames = self.animation_frames_names

        if self.state == self.STATE_ATTACKING:
            target_vx = 0
            current_frames = self.attack_right_frames if self.facing_right else self.attack_left_frames
        elif is_pursuing:
            self.state = self.STATE_PATROLLING
            if self.rect.centerx < player.rect.centerx:
                target_vx, self.facing_right, current_frames = ENEMY_RUN_SPEED, True, self.run_right_frames
            else:
                target_vx, self.facing_right, current_frames = -ENEMY_RUN_SPEED, False, self.run_left_frames
        else:
            if self.state == self.STATE_PATROLLING:
                target_vx = ENEMY_WALK_SPEED if self.facing_right else -ENEMY_WALK_SPEED
                current_frames = self.walk_right_frames if self.facing_right else self.walk_left_frames
                self.patrol_timer -= dt
                if self.patrol_timer <= 0: self.state, self.wait_timer = self.STATE_WAITING, random.uniform(2.0, 4.0)
            elif self.state == self.STATE_WAITING:
                target_vx = 0
                current_frames = self.idle_right_frames if self.facing_right else self.idle_left_frames
                self.wait_timer -= dt
                if self.wait_timer <= 0: self.state, self.patrol_timer = self.STATE_PATROLLING, random.uniform(3.0, 6.0)
        
        should_reverse = False
        if target_vx != 0:
            check_x = self.rect.right + ENEMY_EDGE_DETECTION_OFFSET if target_vx > 0 else self.rect.left - ENEMY_EDGE_DETECTION_OFFSET
            check_rect = Rect(check_x, self.rect.bottom + 5, 1, 1)
            on_ground_ahead = any(check_rect.colliderect(p.rect) for p in platforms)
            if not on_ground_ahead and self.on_ground: should_reverse = True
        
        if not is_pursuing and self.state != self.STATE_ATTACKING:
            if (target_vx > 0 and self.rect.right >= self.patrol_end_x) or \
               (target_vx < 0 and self.rect.left <= self.patrol_start_x):
                should_reverse = True

        if should_reverse and self.state == self.STATE_PATROLLING: self.facing_right = not self.facing_right

        self.vx = target_vx
        self.rect.x += self.vx
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vx > 0: self.rect.right = p.rect.left
                elif self.vx < 0: self.rect.left = p.rect.right

        self.set_animation_frames(current_frames)
        self.animate(dt)

class Projectile:
    def __init__(self, x, y, is_facing_right):
        self.rect = Rect(x - 5, y - 5, 10, 10)
        self.direction = 1 if is_facing_right else -1
    def update(self): self.rect.x += PROJECTILE_SPEED * self.direction
    def draw(self): screen.draw.filled_circle(self.rect.center, 5, 'orange')

class Platform:
    def __init__(self, x, y, width, height):
        self.rect = Rect(x, y, width, height)
        self.image_asset = getattr(images, 'platform', None)
        if not self.image_asset: print("Erro: Imagem plataforma 'platform.png' não foi encontrado.")
    def draw(self):
        if self.image_asset: screen.blit(self.image_asset, self.rect)
        else: screen.draw.filled_rect(self.rect, (100, 100, 100))

class Coin(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 24, 24)
        num_frames = 30 
        self.animation_frames_names = [f"coin_{i}" for i in range(num_frames)]
        
        self.set_animation_frames(self.animation_frames_names)
        self.animation_speed = 0.1

    def draw(self):
        if not self.animation_frames_names:
            screen.draw.rect(self.rect, (255, 0, 0))
            return
        current_image_name = self.animation_frames_names[self.current_frame_index]
        
        try:
            actor_to_draw = Actor(current_image_name)
            actor_to_draw.scale = 0.1
            actor_to_draw.pos = self.rect.center
            actor_to_draw.draw()
        except Exception as e:
            print(f"Erro de criar Actor do '{current_image_name}': {e}.")
            screen.draw.rect(self.rect, (255, 0, 0))

# --- Game Functions ---
def setup_level():
    global player, platforms, enemies, projectiles, score, coin, is_coin_collected, enemies_defeated
    score = 0
    is_coin_collected = False
    enemies_defeated = 0
    player = Player(100, 400)
    platforms = [
        Platform(0, 500, 800, 50), Platform(150, 400, 200, 30),
        Platform(450, 350, 150, 30), Platform(600, 250, 100, 30)
    ]
    top_platform = platforms[-1]
    coin_x = top_platform.rect.centerx
    coin_y = top_platform.rect.top - 16
    coin = Coin(coin_x, coin_y)
    
    enemies = [ Enemy(160, 340, 150, 350), Enemy(460, 290, 450, 600) ]
    projectiles = []
    player.rect.topleft = (100, 400)

def draw_player_health():
    for i in range(player.max_health):
        heart_image = 'heart_full' if i < player.health else 'heart_empty'
        try:
            screen.blit(heart_image, (10 + i * 35, 10))
        except Exception:
            color = "red" if i < player.health else (50, 50, 50)
            screen.draw.filled_rect(Rect(10 + i * 35, 10, 30, 30), color)

def draw_menu():
    screen.clear()
    screen.fill((0, 0, 50))
    screen.draw.text("Lutador Vs Samurai Plataforma", center=(WIDTH / 2, HEIGHT / 4), color="white", fontsize=60)
    start_button = Rect(WIDTH / 2 - 100, HEIGHT / 2 - 30, 200, 60)
    screen.draw.filled_rect(start_button, (0, 150, 0))
    screen.draw.text("Começar Jogo", center=start_button.center, color="white", fontsize=40)
    music_button = Rect(WIDTH / 2 - 100, HEIGHT / 2 + 50, 200, 60)
    music_text = "Música/Sons: ON" if music_on else "Música/Sons: OFF"
    screen.draw.filled_rect(music_button, (150, 0, 150))
    screen.draw.text(music_text, center=music_button.center, color="white", fontsize=30)
    exit_button = Rect(WIDTH / 2 - 100, HEIGHT / 2 + 130, 200, 60)
    screen.draw.filled_rect(exit_button, (150, 0, 0))
    screen.draw.text("Sair", center=exit_button.center, color="white", fontsize=40)

def draw_game_over():
    screen.clear()
    screen.fill((50, 0, 0))
    screen.draw.text("FIM DE JOGO", center=(WIDTH / 2, HEIGHT / 2 - 50), color="white", fontsize=80)
    screen.draw.text("Pressione qualquer tecla para voltar ao menu", center=(WIDTH / 2, HEIGHT / 2 + 50), color="white", fontsize=30)

def draw_victory_screen():
    screen.clear()
    screen.fill((20, 100, 20))
    screen.draw.text("VITÓRIA", center=(WIDTH / 2, HEIGHT / 2 - 50), color="yellow", fontsize=80)
    screen.draw.text(f"Pontuação Final: {score}", center=(WIDTH / 2, HEIGHT / 2 + 20), color="white", fontsize=40)
    screen.draw.text("Pressione qualquer tecla para voltar ao menu", center=(WIDTH / 2, HEIGHT / 2 + 70), color="white", fontsize=30)

def on_mouse_down(pos):
    global current_game_state, music_on
    if current_game_state == GAME_STATE_MENU:
        start_button = Rect(WIDTH / 2 - 100, HEIGHT / 2 - 30, 200, 60)
        music_button = Rect(WIDTH / 2 - 100, HEIGHT / 2 + 50, 200, 60)
        exit_button = Rect(WIDTH / 2 - 100, HEIGHT / 2 + 130, 200, 60)
        if start_button.collidepoint(pos):
            current_game_state = GAME_STATE_PLAYING
            setup_level()
            if music_on:
                try: music.play("background_music"); music.set_volume(0.5)
                except Exception as e: print(f"Não pode tocar a musica de background: {e}")
        elif music_button.collidepoint(pos):
            music_on = not music_on
            if music_on:
                try: music.play("background_music"); music.set_volume(0.5)
                except Exception as e: print(f"Não pode tocar a musica de background: {e}")
            else: music.stop()
        elif exit_button.collidepoint(pos): exit()

def on_key_down(key):
    global current_game_state
    if current_game_state == GAME_STATE_PLAYING: player.on_key_down(key)
    elif current_game_state == GAME_STATE_GAME_OVER or current_game_state == GAME_STATE_VICTORY:
        current_game_state = GAME_STATE_MENU
        if music_on:
             try: music.play("background_music")
             except Exception as e: print(f"Não pode tocar a musica de background no menu: {e}")

def on_key_up(key):
    if current_game_state == GAME_STATE_PLAYING: player.on_key_up(key)

def update(dt):
    global current_game_state, projectiles, enemies, score, is_coin_collected, enemies_defeated
    if current_game_state == GAME_STATE_PLAYING:
        player.update(dt, platforms)
        
        if not is_coin_collected:
            coin.animate(dt)
            if player.rect.colliderect(coin.rect):
                is_coin_collected = True
                score += 3
                if music_on:
                    try: sounds.coin_collect.play()
                    except Exception as e: print(f"Não pode tocar o som de coleta de moeda: {e}")
        
        projectiles_to_remove = []
        enemies_to_remove = []
        for p in projectiles:
            p.update()
            if not (0 < p.rect.x < WIDTH): projectiles_to_remove.append(p)
            for enemy in enemies:
                if p.rect.colliderect(enemy.rect):
                    enemy.on_hit()
                    if p not in projectiles_to_remove: projectiles_to_remove.append(p)
                    if enemy.health <= 0 and enemy not in enemies_to_remove:
                        score += 1
                        enemies_defeated += 1
                        enemies_to_remove.append(enemy)
        
        projectiles = [p for p in projectiles if p not in projectiles_to_remove]
        enemies = [e for e in enemies if e not in enemies_to_remove]

        for enemy in enemies: enemy.update(dt, player, platforms)
        
        if enemies_defeated >= 2 and is_coin_collected:
            current_game_state = GAME_STATE_VICTORY
            music.stop()
        elif player.health <= 0 or player.rect.y > HEIGHT + 50:
            current_game_state = GAME_STATE_GAME_OVER
            music.stop()

def draw():
    if current_game_state == GAME_STATE_MENU: draw_menu()
    elif current_game_state == GAME_STATE_PLAYING:
        screen.clear()
        if hasattr(images, 'background'): screen.blit(images.background, (0, 0))
        else: screen.fill((135, 206, 235))
        for p in platforms: p.draw()
        for e in enemies: e.draw()
        for proj in projectiles: proj.draw()
        
        if not is_coin_collected:
            coin.draw()
        
        player.draw()
        draw_player_health()
        screen.draw.text(f"Pontuação: {score}", center=(WIDTH / 2, 30), color="black", fontsize=40)
    elif current_game_state == GAME_STATE_GAME_OVER: draw_game_over()
    elif current_game_state == GAME_STATE_VICTORY: draw_victory_screen()

if music_on:
    try:
        music.play("background_music")
        music.set_volume(0.5)
    except Exception as e:
        print(f"Não pode tocar a musica de background no começo: {e}")

pgzrun.go()