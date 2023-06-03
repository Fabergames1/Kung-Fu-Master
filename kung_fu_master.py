import pygame,sys,random
from pygame.locals import *
import enemies


BLACK=pygame.color.THECOLORS["black"]
WHITE=pygame.color.THECOLORS["white"]
RED=pygame.color.THECOLORS["red"]
GREEN=pygame.color.THECOLORS["green"]
BLUE=pygame.color.THECOLORS["blue"]
YELLOW=pygame.color.THECOLORS["yellow"]
SCREEN_WIDTH=640
SCREEN_HEIGHT=480
DISPLAY_SURFACE_WIDTH = 320
DISPLAY_SURFACE_HEIGHT = 240
CENTER_X= int(DISPLAY_SURFACE_WIDTH/2)


def load_sprite_data(sprite_file):
    sprites = {'rect':[], 'axis_shift':[], 'offense_box':[], 'defense_box':[]}
    with open(sprite_file, 'r') as file:
         data=file.read()
         data=data.split(';')
         del(data[-1])
         for i in range(len(data)):
             data[i] = data[i].split(",")
             for j in range(len(data[i])):
                 data[i][j] = data[i][j].split(" ")
                 for k in range(len(data[i][j])):
                     data[i][j][k] = int(data[i][j][k])
             sprites['rect'].append(data[i][0])
             sprites['axis_shift'].append(data[i][1])
             sprites['offense_box'].append(data[i][2])
             sprites['defense_box'].append(data[i][3])
    return sprites

def load_animation_data(animation_file):
    animations = None
    with open(animation_file, 'r') as file:
         data=file.read()
         data=data.split(',')
         del(data[-1])
         for i in range(len(data)):
             data[i] = data[i].split(" ")
             if data[i][0] == "-1":
                del(data[i][0])
             else:
                data[i].append(-1)
             for j in range(len(data[i])):
                 data[i][j] = int(data[i][j])
         animations = data
    return animations

def collisions(player, enemy):
    if player.attack_type != None:
       if enemy.current_state not in ('hurt', 'death') \
       and player.current_sprite['offense_box']!= [0, 0, 0, 0]:
          offense_box = player.current_sprite['offense_box']
          offense_box = [player.image_pos[0] + offense_box[0],
                         player.image_pos[1] + offense_box[1],
                         offense_box[2], offense_box[3]]
          defense_box = enemy.current_sprite['defense_box']
          defense_box = [enemy.image_pos[0] + defense_box[0],
                         enemy.image_pos[1] + defense_box[1],
                         defense_box[2], defense_box[3]]        
          if offense_box[0] < defense_box[0] + defense_box[2] \
          and offense_box[0] + offense_box[2] > defense_box[0] \
          and offense_box[1] < defense_box[1] + defense_box[3] \
          and offense_box[1] + offense_box[3] > defense_box[1]:
              enemy.hit_points -= 1
              enemy.direction *= -1
              enemy.xvel = 2 * enemy.direction
              enemy.axis_pos[0] += enemy.xvel
              enemy.current_state = 'hurt'
              enemy.change_animation(enemy.hit_reactions[player.attack_type])
    if enemy.attack_type != None:
       if player.current_state not in ('hurt', 'death') \
       and enemy.current_sprite['offense_box'] != [0, 0, 0, 0]:
          offense_box = enemy.current_sprite['offense_box']
          offense_box = [enemy.image_pos[0] + offense_box[0],
                         enemy.image_pos[1] + offense_box[1],
                         offense_box[2], offense_box[3]]          
          defense_box = player.current_sprite['defense_box']
          defense_box = [player.image_pos[0] + defense_box[0],
                         player.image_pos[1] + defense_box[1],
                         defense_box[2], defense_box[3]]                    
          if offense_box[0] < defense_box[0] + defense_box[2] \
          and offense_box[0] + offense_box[2] > defense_box[0] \
          and offense_box[1] < defense_box[1] + defense_box[3] \
          and offense_box[1] + offense_box[3] > defense_box[1]:
              player.hit_points -= 1
              player.current_state = 'hurt'
              player.change_animation(player.hit_reactions[enemy.attack_type])
              

class Player():
    def __init__(self, image, sprite_file, animation_file, axis_pos):
        self.left_side_sprites = self.get_sprites(image, sprite_file)
        self.right_side_sprites = self.get_right_side_sprites(self.left_side_sprites)
        self.sprites = self.right_side_sprites
        self.animations = self.get_animations(animation_file)
        self.axis_pos = axis_pos
        self.current_animation =  self.animations['idle']
        self.animation_frame = 0
        self.current_sprite = self.sprites[self.current_animation[self.animation_frame]]
        self.image = self.current_sprite['image']
        self.image_pos=[
        self.axis_pos[0] + self.current_sprite['axis_shift'][0],
        self.axis_pos[1] + self.current_sprite['axis_shift'][1]]
        self.anim_time = 0
        self.max_anim_time = 3
        self.xvel = 0
        self.yvel = 0
        self.hit_points = 10
        self.attack_type = None
        self.grabbing_enemies = []
        self.grab_count = 3
        self.grab_escape_timer = 0
        self.current_state = 'idle'
        self.states = {'idle':self.idle, 'walk':self.walk, 'crouch':self.crouch,
                       'jump_start':self.jump_start, 'jump':self.jump, 'fall':self.fall,
                       'attack':self.attack, 'air_attack':self.air_attack,
                       'ground_attack':self.ground_attack, 'climb_stairs':self.climb_stairs,
                       'grabbed':self.grabbed}
        self.hit_reactions = {'hight':'hurt1', 'middle':'hurt2', 'low':'hurt2'}
        
    def get_sprites(self, image, player_sprite_file):
        sprites = []
        sprites_data = load_sprite_data(player_sprite_file)
        for i in range(len(sprites_data['rect'])):
            sprites.append({'image':image.subsurface(sprites_data['rect'][i]),
                            'axis_shift':sprites_data['axis_shift'][i],
                            'offense_box':sprites_data['offense_box'][i],
                            'defense_box':sprites_data['defense_box'][i]})
        return sprites
                            
    def get_animations(self, player_animation_file):
        animations = {}            
        animations_data = load_animation_data(player_animation_file)
        animations['idle'] = animations_data[14]
        animations['walk'] = animations_data[2]
        animations['crouch'] = animations_data[18]
        animations['jump_start'] = animations_data[15]
        animations['jump'] = animations_data[5]
        animations['fall'] = animations_data[16]
        animations['fight_stance'] = animations_data[13]
        animations['punch1'] = animations_data[0]
        animations['punch2'] = animations_data[17]
        animations['kick'] = animations_data[1]
        animations['air_punch'] = animations_data[6]
        animations['air_kick'] = animations_data[7]
        animations['ground_punch1'] = animations_data[3]
        animations['ground_punch2'] = animations_data[19]
        animations['ground_kick'] = animations_data[4]
        animations['climb_stairs'] = animations_data[11]
        return animations
                            
    def get_right_side_sprites(self, sprites):
        left_side_sprites=[]
        for sprite in sprites:
            image_width, image_height = sprite['image'].get_size()             
            left_side_sprite={
            'image':pygame.transform.flip(sprite['image'], True, False),    
            'axis_shift':[-(image_width + sprite['axis_shift'][0]), sprite['axis_shift'][1]],
            'offense_box':sprite['offense_box'],
            'defense_box':sprite['offense_box']}
            if sprite['offense_box'] != [0,0,0,0]:
               offense_box = sprite['offense_box']
               left_side_offense_box = [image_width - (offense_box[0] + offense_box[2]),
                                        offense_box[1], offense_box[2], offense_box[3]]
               left_side_sprite['offense_box'] = left_side_offense_box
            if sprite['defense_box'] != [0,0,0,0]:
               defense_box = sprite['defense_box']
               left_side_defense_box = [image_width - (defense_box[0] + defense_box[2]),
                                        defense_box[1], defense_box[2], defense_box[3]]
               left_side_sprite['defense_box'] = left_side_defense_box
            left_side_sprites.append(left_side_sprite)            
        return left_side_sprites

    def change_animation(self, animation):
        self.current_animation =  self.animations[animation]
        self.anim_time = 0
        self.animation_frame = 0
        self.current_sprite = self.sprites[self.current_animation[self.animation_frame]]
        self.image = self.current_sprite['image']
        self.image_pos[0] = self.axis_pos[0] + self.current_sprite['axis_shift'][0]
        self.image_pos[1] = self.axis_pos[1] + self.current_sprite['axis_shift'][1]
        
    def scroll_background(self):
        if self.axis_pos[0] < CENTER_X or self.axis_pos[0] > CENTER_X:
           dx = CENTER_X - self.axis_pos[0]
           background_pos[0] += dx
           if background_pos[0] > 0:
              background_pos[0] = 0
              if self.axis_pos[0] < 135:
                 self.axis_pos[0] = 135
                 self.current_state = 'climb_stairs'
                 self.change_animation('climb_stairs')
           elif background_pos[0] < -1472:
              background_pos[0] = -1472
              if self.axis_pos[0] > 280:
                 self.axis_pos[0] = 280
           else:
              self.axis_pos[0] += dx
              for enemy in enemies_group:
                  enemy.axis_pos[0] += dx
                  if enemy.axis_pos[0] < -100 or enemy.axis_pos[0] > 420:
                     enemy.kill()
        
    def idle(self):
        global punch, kick
        if left:
           self.current_state = 'walk'
           self.sprites = self.right_side_sprites
           self.current_animation =  self.animations['walk']
           self.anim_time = 0
           self.xvel = -walk_speed
        elif right:
           self.current_state = 'walk'
           self.sprites = self.left_side_sprites
           self.current_animation =  self.animations['walk']
           self.anim_time = 0
           self.xvel = walk_speed
        if jump:
           self.yvel = jump_speed
           if left:
              self.xvel = -2
           elif right:
              self.xvel = 2
           self.current_state = 'jump_start'
           self.change_animation('jump_start')
        elif crouch:
           self.current_state = 'crouch'
           self.change_animation('crouch')
        elif punch:
           punch = False
           self.current_state = 'attack'
           self.attack_type = 'hight'
           self.change_animation('punch1')
        elif kick:
           kick = False
           self.attack_type = 'hight'
           self.current_state = 'attack'
           self.change_animation('kick')
           
    def walk(self):
        global punch, kick
        self.anim_time += 1
        if self.anim_time  >= self.max_anim_time:
           self.anim_time = 0
           self.current_sprite = self.sprites[self.current_animation[self.animation_frame]]
           self.image = self.current_sprite['image']
           self.image_pos[0] = self.axis_pos[0] + self.current_sprite['axis_shift'][0]
           self.image_pos[1] = self.axis_pos[1] + self.current_sprite['axis_shift'][1]           
           self.animation_frame += 1
           if self.current_animation[self.animation_frame] == -1:
              self.animation_frame = 0
           self.axis_pos[0] += self.xvel
           if not (left or right):
              self.current_state = 'idle'
              self.xvel = 0
           if jump:
              self.yvel = jump_speed
              if left:
                 self.xvel = -2
              elif right:
                 self.xvel = 2
              self.current_state = 'jump_start'
              self.change_animation('jump_start')
           elif crouch:
              self.current_state = 'crouch'
              self.change_animation('crouch')
           elif punch:
              punch = False
              self.current_state = 'attack'
              self.change_animation('punch1')
           elif kick:
              kick = False
              self.current_state = 'attack'
              self.change_animation('kick')
           self.scroll_background()
           
    def crouch(self):
        global punch, kick
        if crouch:
           if left:
              self.sprites = self.right_side_sprites
              self.current_sprite = self.sprites[self.current_animation[self.animation_frame]]
              self.image = self.current_sprite['image']
              self.image_pos[0] = self.axis_pos[0] + self.current_sprite['axis_shift'][0]   
              self.image_pos[1] = self.axis_pos[1] + self.current_sprite['axis_shift'][1]
           elif right:
              self.sprites = self.left_side_sprites
              self.current_sprite = self.sprites[self.current_animation[self.animation_frame]]
              self.image = self.current_sprite['image']
              self.image_pos[0] = self.axis_pos[0] + self.current_sprite['axis_shift'][0]   
              self.image_pos[1] = self.axis_pos[1] + self.current_sprite['axis_shift'][1]
           elif punch:
              punch = False
              self.current_state = 'ground_attack'
              self.change_animation('ground_punch1')              
           elif kick:
              kick = False
              self.current_state = 'ground_attack'
              self.change_animation('ground_kick')
        else:    
           self.current_state = 'idle'
           self.change_animation('idle')
           
    def jump_start(self):
        self.anim_time += 1
        if self.anim_time  >= self.max_anim_time:
           self.anim_time = 0
           self.current_sprite = self.sprites[self.current_animation[self.animation_frame]]
           self.image = self.current_sprite['image']                               
           if self.current_animation[self.animation_frame] == -1:
              self.animation_frame = 0
              if self.yvel > 0:
                 self.current_state = 'jump'
                 self.current_animation = self.animations['jump']
              else:
                 self.current_state = 'idle'
                 self.current_animation = self.animations['fight_stance']
                 global punch, kick
                 punch = False
                 kick = False
              self.current_sprite = self.sprites[self.current_animation[self.animation_frame]]
              self.image = self.current_sprite['image']
              self.image_pos[0] = self.axis_pos[0] + self.current_sprite['axis_shift'][0]   
              self.image_pos[1] = self.axis_pos[1] + self.current_sprite['axis_shift'][1]
           self.animation_frame += 1 
              
    def jump(self):
        global punch, kick
        self.axis_pos[0] += self.xvel
        self.axis_pos[1] -= self.yvel
        self.yvel -= gravity
        self.scroll_background()
        self.anim_time += 1
        if self.anim_time  >= self.max_anim_time:
           self.anim_time = 0
           if self.current_animation[self.animation_frame] != -1:
              self.current_sprite = self.sprites[self.current_animation[self.animation_frame]]
              self.image = self.current_sprite['image']
              self.animation_frame += 1
        self.image_pos[0] = self.axis_pos[0] + self.current_sprite['axis_shift'][0]  
        self.image_pos[1] = self.axis_pos[1] + self.current_sprite['axis_shift'][1]
        if punch:
           punch = False
           self.current_state = 'air_attack'
           self.change_animation('air_punch')
        elif kick:
           kick = False
           self.current_state = 'air_attack'
           self.change_animation('air_kick')
        if self.yvel < 0:
           self.current_state = 'fall'
           self.change_animation('fall')
           
    def fall(self):
        self.axis_pos[0] += self.xvel
        self.axis_pos[1] -= self.yvel
        self.yvel -= gravity
        self.scroll_background()
        self.anim_time += 1
        if self.anim_time  >= self.max_anim_time:
           self.anim_time = 0
           if self.current_animation[self.animation_frame] != -1:
              self.current_sprite = self.sprites[self.current_animation[self.animation_frame]]
              self.image = self.current_sprite['image']
              self.animation_frame += 1
        self.image_pos[0] = self.axis_pos[0] + self.current_sprite['axis_shift'][0] 
        self.image_pos[1] = self.axis_pos[1] + self.current_sprite['axis_shift'][1]              
        if self.axis_pos[1] >= ground_y_pos:
           self.axis_pos[1] = ground_y_pos
           global jump
           jump = False
           self.xvel = 0
           self.yvel = 0
           self.current_state = 'jump_start'
           self.change_animation('jump_start')
        
    def attack(self):    
        self.anim_time += 1
        if self.anim_time  >= self.max_anim_time:
           self.anim_time = 0
           self.current_sprite = self.sprites[self.current_animation[self.animation_frame]]
           self.image = self.current_sprite['image']
           if self.current_animation[self.animation_frame] == -1:
              self.animation_frame = 0 
              global punch, kick
              if punch and self.current_animation == self.animations['punch1']:
                 self.current_animation = self.animations['punch2']
              elif punch and self.current_animation == self.animations['punch2']:
                 self.current_animation = self.animations['punch1']
              elif kick and self.current_animation == self.animations['kick']:
                 self.animation_frame = 1
                 self.current_animation = self.animations['kick']
              else:
                 self.attack_type = None 
                 self.current_state = 'idle'
                 self.current_animation =  self.animations['fight_stance']
              punch = False
              kick = False
           self.current_sprite = self.sprites[self.current_animation[self.animation_frame]]
           self.image = self.current_sprite['image']
           self.image_pos[0] = self.axis_pos[0] + self.current_sprite['axis_shift'][0]   
           self.image_pos[1] = self.axis_pos[1] + self.current_sprite['axis_shift'][1]
           self.animation_frame += 1
                      
    def air_attack(self):
        self.axis_pos[0] += self.xvel
        self.axis_pos[1] -= self.yvel
        self.yvel -= gravity
        self.scroll_background()
        self.anim_time += 1
        if self.anim_time  >= self.max_anim_time:
           self.anim_time = 0
           if self.current_animation[self.animation_frame] == -1:
              if self.yvel > 0:
                 self.current_state = 'jump'
                 self.current_animation = self.animations['jump']
              elif self.yvel < 0:
                 self.current_state = 'fall'
                 self.current_animation = self.animations['fall']
              self.animation_frame = len(self.current_animation) - 2
           self.current_sprite = self.sprites[self.current_animation[self.animation_frame]]
           self.image = self.current_sprite['image']
           self.animation_frame += 1
        self.image_pos[0] = self.axis_pos[0] + self.current_sprite['axis_shift'][0]
        self.image_pos[1] = self.axis_pos[1] + self.current_sprite['axis_shift'][1]
        if self.axis_pos[1] >= ground_y_pos:
           self.axis_pos[1] = ground_y_pos
           global jump
           jump = False
           self.xvel = 0
           self.yvel = 0
           self.current_state = 'jump_start'
           self.change_animation('jump_start')
           
    def ground_attack(self):
        self.anim_time += 1
        if self.anim_time  >= self.max_anim_time:
           self.anim_time = 0
           if self.current_animation[self.animation_frame] == -1:
              self.animation_frame = 0
              global punch, kick
              if punch and self.current_animation == self.animations['ground_punch1']:
                 self.current_animation = self.animations['ground_punch2']
              elif punch and self.current_animation == self.animations['ground_punch2']:
                 self.current_animation = self.animations['ground_punch1']
              elif kick and self.current_animation == self.animations['ground_kick']:
                 self.current_animation = self.animations['ground_kick']
              else:
                 self.current_state = 'crouch'
                 self.current_animation = self.animations['crouch']
              punch = False
              kick = False
           self.current_sprite = self.sprites[self.current_animation[self.animation_frame]]
           self.image = self.current_sprite['image']
           self.image_pos[0] = self.axis_pos[0] + self.current_sprite['axis_shift'][0]   
           self.image_pos[1] = self.axis_pos[1] + self.current_sprite['axis_shift'][1]
           self.animation_frame += 1
           
    def climb_stairs(self):
        self.anim_time += 1
        if self.anim_time  >= self.max_anim_time:
           self.anim_time = 0           
           if self.current_animation[self.animation_frame] == -1:
              self.animation_frame = 0
           self.axis_pos[0] -= 4
           self.axis_pos[1] -= 6
           if self.axis_pos[1] < 100:
              background_pos[0] = -1472
              background_pos[1] = 40
              self.axis_pos[0] = 190
              self.axis_pos[1] = 202
              self.current_state = 'idle'
              self.change_animation('idle')
           self.current_sprite = self.sprites[self.current_animation[self.animation_frame]]
           self.image = self.current_sprite['image']
           self.image_pos[0] = self.axis_pos[0] + self.current_sprite['axis_shift'][0]  
           self.image_pos[1] = self.axis_pos[1] + self.current_sprite['axis_shift'][1]
           self.animation_frame += 1
           
    def grabbed(self):
        global jump, left, right, crouch
        if jump and self.axis_pos[1] != ground_y_pos:
           self.axis_pos[1] -= self.yvel
           self.yvel -= gravity
           if self.axis_pos[1] >= ground_y_pos:
              self.axis_pos[1] = ground_y_pos
              jump = False
              self.xvel = 0
              self.yvel = 0
              self.change_animation('idle')
           self.image_pos[0] = self.axis_pos[0] + self.current_sprite['axis_shift'][0]  
           self.image_pos[1] = self.axis_pos[1] + self.current_sprite['axis_shift'][1]
        else:
           if left:
              left = False
              self.sprites = self.right_side_sprites
              self.change_animation('walk')
              self.grab_count -= 1
              self.grab_escape_timer = 10
           elif right:
              right = False 
              self.sprites = self.left_side_sprites
              self.change_animation('walk')
              self.grab_count -= 1
              self.grab_escape_timer = 10
           elif jump:
              jump = False 
              self.grab_count -= 1
              self.grab_escape_timer = 10               
           elif crouch:
              crouch = False 
              self.change_animation('crouch')
              self.grab_count -= 1
              self.grab_escape_timer = 10              
           if self.grab_escape_timer > 0:
              self.grab_escape_timer -= 1
              if self.grab_escape_timer <= 0:
                 self.grab_escape_timer = 0
                 self.grab_count = 3
              if self.grab_count <= 0:
                 self.grab_escape_timer = 0
                 self.grab_count = 3
                 self.current_state = 'idle'
                 self.change_animation('idle')
                 global punch, kick
                 punch = False
                 kick = False
                 for i in range(len(self.grabbing_enemies)-1, -1, -1):
                     enemy = self.grabbing_enemies[i]
                     enemy.hit_points = 0
                     enemy.direction *= -1
                     enemy.xvel = 2 * enemy.direction
                     enemy.axis_pos[0] += enemy.xvel
                     enemy.current_state = 'death'
                     enemy.change_animation('death')
                     self.grabbing_enemies.remove(enemy)
                 
    
def main():
    
    pygame.init()

    #Open Pygame window
    screen = pygame.display.set_mode((640, 480),) #add RESIZABLE or FULLSCREEN
    display_surface = pygame.Surface((320, 240)).convert()
    scaled_display_surface = pygame.transform.scale(display_surface,(640,480))
    #Title
    pygame.display.set_caption("Kung-Fu Master")
    #font
    font=pygame.font.SysFont('Arial', 30)

    #images
    image = pygame.image.load('data\\Characters.png').convert()
    background = pygame.image.load('data\\kungfum_1_floor.png').convert()
    foreground = background.subsurface((16, 232, 1792, 170))
    background = background.subsurface((16, 16, 1792, 200))
    image.set_colorkey(image.get_at((0,0)))
    foreground.set_colorkey(foreground.get_at((0,50)))
    #variables
    global left, right, crouch, jump, punch, kick, walk_speed, jump_speed, gravity
    global ground_y_pos, background_pos, enemies_group
    left = False
    right = False
    crouch = False
    jump = False
    punch = False
    kick = False
    walk_speed = 5
    jump_speed = 4
    gravity = 0.25
    ground_y_pos = 202
    player = Player(image, 'data\\hero_sprite_info.spr', 'data\\hero_animation_info.anm', [190, ground_y_pos])
    enemies.enemies_load_data(image)
    #enemy = enemies.Enemy1([20, ground_y_pos], 1, player)
    enemies_group = enemies.Enemy.group
    enemy_spawn_timer = 100
    background_width, background_height = background.get_size()
    background_pos = [-1472, 40]
    
    #pygame.key.set_repeat(400, 30)

    while True:
        #loop speed limitation
        #30 frames per second is enought
        pygame.time.Clock().tick(30)
        
        for event in pygame.event.get():    #wait for events
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                
            #keyboard movement commands    
            if event.type == KEYDOWN:
                if event.key == K_LEFT:
                   left = True
                   right = False
                   if player.current_state == 'walk':
                      player.sprites = player.right_side_sprites
                      player.xvel = -walk_speed
                elif event.key == K_RIGHT:
                   right = True
                   left = False                   
                   if player.current_state == 'walk':
                      player.sprites = player.left_side_sprites
                      player.xvel = walk_speed
                if event.key == K_a:
                   punch = True
                elif event.key == K_s:
                   kick = True
                if event.key == K_UP:
                   jump = True
                if event.key == K_DOWN:
                   crouch = True
            if event.type == KEYUP:
                if event.key == K_LEFT:
                   left=False
                elif event.key == K_RIGHT:
                   right=False
                if event.key == K_DOWN: 
                   crouch = False

        player.states[player.current_state]()#;print(player.current_state)
        for enemy in enemies_group:
            enemy.states[enemy.current_state]()
            if enemy.projectile and enemy.projectile['active']:
               enemy.update_projectile()
            collisions(player, enemy)
            
        enemy_spawn_timer -= 1
        if enemy_spawn_timer <= 0:
           enemy_spawn_timer = random.randint(100, 200)
           if len(enemies_group) < 4:
              direction = random.choice((-1, 1))
              if direction == 1:
                 if background_pos[0] < -150:
                    enemies.Enemy1([-20, ground_y_pos], 1, player)
                 else:
                    enemies.Enemy1([340, ground_y_pos], -1, player)
              elif direction == -1:
                 if background_pos[0] > -1420:
                    enemies.Enemy1([340, ground_y_pos], -1, player)
                 else:
                    enemies.Enemy1([-20, ground_y_pos], 1, player)
        
        #draw everything
        display_surface.fill(BLUE)
        display_surface.blit(background, background_pos)
        display_surface.blit(player.image, player.image_pos)
        for enemy in enemies_group:
            display_surface.blit(enemy.image, enemy.image_pos)
            if enemy.projectile and enemy.projectile['active']:
               display_surface.blit(enemy.projectile['image'], enemy.projectile['image_pos'])  
        display_surface.blit(foreground, background_pos)
        scaled_display_surface = pygame.transform.scale(display_surface,(640,480))
        screen.blit(scaled_display_surface, (0,0))
        pygame.display.flip()

if __name__ == "__main__":
    main()
