import pgzrun
import random

#Configurações do Jogo
WIDTH = 1280
HEIGHT = 720

FONTE = 'alagard.ttf'

# Classe do jogador
class Player(Actor):
    def __init__(self):
        super().__init__('peao1', (WIDTH//2, HEIGHT//2))
        self.idle_frames_left = ['peao1', 'peao2']
        self.walk_frames_left = ['peao1', 'peao2', 'peao3', 'peao4', 'peao5']
        self.idle_frames_right = ['peao_right1', 'peao_right2']
        self.walk_frames_right = ['peao_right1', 'peao_right2', 'peao_right3', 'peao_right4', 'peao_right5']
        self.current_frame = 0
        self.is_moving = False
        self.is_moving_left = True
        self.timer = 0
        self.speed = 2  
        self.is_hurt = False  
        self.hurt_timer = 0  

    def handle_input(self):
        self.is_moving = False
        if keyboard.w: 
            self.y -= self.speed
            self.is_moving = True
        if keyboard.a: 
            self.x -= self.speed
            self.is_moving = True
            self.is_moving_left = True
        if keyboard.s: 
            self.y += self.speed
            self.is_moving = True
        if keyboard.d: 
            self.x += self.speed
            self.is_moving = True
            self.is_moving_left = False
            

    def keep_in_bounds(self):
        if self.x < 249: self.x = 249
        if self.x > 1030: self.x = 1030
        if self.y < 16: self.y = 16
        if self.y > HEIGHT - 16: self.y = HEIGHT - 16

    def take_damage(self):
        global lives, game_state
        lives -= 1
        self.is_hurt = True
        self.hurt_timer = 1
        self.image = "hit_left" if self.is_moving_left else "hit_right"
        
        if lives <= 0:
            game_state = 'game_over'
            enemies.clear()
            if music_enabled:
                sounds.death.play()

#Função para animar os atores
def animate(obj, dt):
    obj.timer += dt
    if obj.is_moving:
        frames = obj.walk_frames_left if obj.is_moving_left else obj.walk_frames_right
    else:
        frames = obj.idle_frames_left if obj.is_moving_left else obj.idle_frames_right

    if frames and obj.timer >= 0.1:
        obj.timer = 0
        obj.current_frame = (obj.current_frame + 1) % len(frames)
        obj.image = frames[obj.current_frame]

#Função que determina qual música tocará a depender da tela do jogo
def play_music_for_state():
    if game_state == 'playing':
        music.fadeout(0.5)
        music.play('chess_ruins')
        music.set_volume(0.5)
    elif game_state == 'menu':
        music.fadeout(0.5)
        music.play('menu')
        music.set_volume(0.5)
    else:
        music.fadeout(0.5)

player = Player()
sword = Actor('espada')
background = Actor('arena')
menu = Actor('menu')
frame = Actor('frame', (95,145))

enemies = []

lives = 3

game_state = 'menu'

play_music_for_state()
music_enabled = True

attack_direction = None

def update(dt):
    global attack_direction, lives, game_state
    
    #Define se o jogo rodará
    if game_state != 'playing':
        return

    #Movimentação, animação e barreiras
    player.handle_input()
    animate(player, dt)
    player.keep_in_bounds()
    
    #Sistema de ataque
    attack_direction = None
    if keyboard.up: attack_direction = 'up'
    if keyboard.down: attack_direction = 'down'
    if keyboard.left: attack_direction = 'left'
    if keyboard.right: attack_direction = 'right'
    
    if attack_direction:
        if attack_direction == 'up':
            sword.pos = (player.x, player.y - 35)
            sword.angle = 0
        elif attack_direction == 'down':
            sword.pos = (player.x, player.y + 35)
            sword.angle = 180
        elif attack_direction == 'left':
            sword.pos = (player.x - 30, player.y)
            sword.angle = 90
        elif attack_direction == 'right':
            sword.pos = (player.x + 30, player.y)
            sword.angle = 270
    
    #Verifica se o player está machucado
    if player.is_hurt:
        player.hurt_timer -= dt
        if player.hurt_timer <= 0:
            player.is_hurt = False
            player.image = "peao1"
    
    #Spawn de inimigos
    if random.randint(0, 100) < 5 and len(enemies) < 5:
        pos = random.choice([(270, 690), (1009, 690), (1009, 27), (270, 27)])
        enemy = Actor('dama1', pos)
        enemy.walk_frames_right = ['dama1','dama2','dama3', 'dama4', 'dama5']
        enemy.walk_frames_left = ['dama1','dama2','dama3_left', 'dama4_left', 'dama5_left']
        enemy.current_frame = 0
        enemy.timer = 0
        enemy.is_moving = True
        enemy.is_moving_left = True
        enemies.append(enemy)
    
    for enemy in enemies[:]:
        proximity_zone = Rect((player.x - 25, player.y - 25), (50, 50))

        enemy_rect = Rect((enemy.x - enemy.width // 2, enemy.y - enemy.height // 2), (enemy.width, enemy.height))
        
        if proximity_zone.colliderect(enemy_rect) and player.is_hurt:
            if enemy.x < player.x: 
                enemy.x -= 2 
            elif enemy.x > player.x:
                enemy.x += 2

            if enemy.y < player.y: 
                enemy.y -= 2
            elif enemy.y > player.y:
                enemy.y += 2
        else:
            if enemy.x < player.x: 
                enemy.x += 2
                enemy.is_moving_left = False
            if enemy.y < player.y: enemy.y += 2
            if enemy.x > player.x: 
                enemy.x -= 2 
                enemy.is_moving_left = True
            if enemy.y > player.y: enemy.y -= 2

        animate(enemy, dt)
        
        #Verificação de colisão do inimigo com a espada
        if attack_direction and sword.colliderect(enemy):
            if enemy in enemies:  
                enemies.remove(enemy)
                if music_enabled:
                    sounds.enemy_death.play()
            continue
        
        #Verificação de colisão do inimigo com o player
        if player.colliderect(enemy) and not player.is_hurt:
            if enemy in enemies:  
                enemies.remove(enemy)
                player.take_damage()
                if music_enabled:
                    sounds.hit.play()
        
        #Barreiras para o inimigo
        if enemy.x < 249: enemy.x = 249
        if enemy.x > 1030: enemy.x = 1030
        if enemy.y < 16: enemy.y = 16
        if enemy.y > HEIGHT - 16: enemy.y = HEIGHT - 16

def draw():
    screen.clear()
    
    #Tela de menu
    if game_state == 'menu': 
        menu.draw()
        screen.draw.text("Killer's Queen",center=(WIDTH//2, HEIGHT//2 - 50),fontname=FONTE,color='red',fontsize=100)
        screen.draw.text('Start',center=(WIDTH//2, HEIGHT//2 + 30),fontname=FONTE,color='white',fontsize=30)
        music_text = "Music & Sounds: ON" if music_enabled else "Music & Sounds: OFF"
        screen.draw.text(music_text,center=(WIDTH//2, HEIGHT//2 + 80),fontname=FONTE,color='white')
        screen.draw.text('Quit',center=(WIDTH//2, HEIGHT//2 + 130),fontname=FONTE,color='white')

    #Tela de GameOver
    if game_state == 'game_over':
        music.stop()
        screen.draw.text('Game Over',center=(WIDTH//2, HEIGHT//2 - 50),fontname=FONTE,color='red',fontsize=100)
        screen.draw.text('Press SPACE to restart',center=(WIDTH//2, HEIGHT//2 + 50),fontname=FONTE,color='white')
        screen.draw.text('Press ESC to main menu',center=(WIDTH//2, HEIGHT//2 + 100),fontname=FONTE,color='red')

    #Tela do Jogo
    elif game_state == 'playing':
        background.draw()
        frame.draw()
        player.draw()
        for enemy in enemies:
            enemy.draw()
        if attack_direction:
            sword.draw()
        
        screen.draw.text(f'Lives: {lives}',(15, 103),fontname=FONTE,color='red')
        screen.draw.text('Use WASD to move',(15, 138),fontname=FONTE,fontsize=15,color='white')
        screen.draw.text('Arrows to attack',(15, 168),fontname=FONTE,fontsize=15,color='white')

menu_buttons = {
    'Start': (WIDTH//2, HEIGHT//2 + 30),
    'Music ON/OFF': (WIDTH//2, HEIGHT//2 + 80),
    'Quit': (WIDTH//2, HEIGHT//2 + 130),
}
def on_mouse_down(pos):
    global game_state,music_enabled
    
    for text, (x, y) in menu_buttons.items():
        text_box = Rect((x - 100, y - 20), (200, 40))
        if text_box.collidepoint(pos):
            if text == 'Start':
                game_state = 'playing'
                if music_enabled:
                    play_music_for_state()
            elif text == 'Music ON/OFF':
                music_enabled = not music_enabled
                if music_enabled:
                    play_music_for_state()
                else:
                    music.fadeout(0.5)
            elif text == 'Quit':
                exit()

def on_key_down(key):
    global game_state,lives,enemies,music_enabled
    if key == keys.SPACE and game_state == 'game_over':
        game_state = 'playing'
        lives = 3
        enemies = []
        player.pos = (WIDTH//2, HEIGHT//2)
        if music_enabled:
            sounds.death.stop()
            play_music_for_state()
            
    elif game_state == 'menu':
        game_state = 'playing'
        if music_enabled:
            play_music_for_state()
    
    if key == keys.ESCAPE:
        if game_state == 'playing':
            game_state = 'menu'
            if music_enabled:
                play_music_for_state()
        elif game_state == 'game_over':
            game_state = 'menu'
            if music_enabled:
                sounds.death.stop()
                play_music_for_state()
            lives = 3
            enemies = []

pgzrun.go()