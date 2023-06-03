import pygame,sys,random
from pygame.locals import *


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

def enemies_load_data(image):
    Enemy1.get_sprites(image)
    Enemy1.get_animations()
    Enemy2.get_sprites(image)
    Enemy2.get_animations()
    Enemy2.get_projectile()
    

class Enemy():
    group = []
    def __init__(self, axis_pos):
        Enemy.group.append(self)
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
        self.walk_speed = 5
        self.xvel = self.walk_speed
        self.yvel = 0
        self.direction = 1
        self.hit_points = 1
        self.attack_type = None
        self.projectile = None
        self.current_state = 'idle'
        self.states = {'idle':self.idle, 'walk':self.walk, 'hurt':self.hurt, 'death':self.death}
        
    def get_sprites(image, sprite_file):
        sprites = []
        sprites_data = load_sprite_data(sprite_file)
        for i in range(len(sprites_data['rect'])):
            sprites.append({'image':image.subsurface(sprites_data['rect'][i]),
                            'axis_shift':sprites_data['axis_shift'][i],
                            'offense_box':sprites_data['offense_box'][i],
                            'defense_box':sprites_data['defense_box'][i]})
        return sprites
                            
    def get_animations(animation_file):
        animations = {}            
        animations_data = load_animation_data(animation_file)
        animations['idle'] = animations_data[14]
        animations['walk'] = animations_data[2]
        return animations
                            
    def get_right_side_sprites(sprites):
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
           background_pos[0] += CENTER_X - self.axis_pos[0]
           if background_pos[0] > 0:
              background_pos[0] = 0
              if self.axis_pos[0] < 135:
                 self.axis_pos[0] = 135
                 self.sprites = self.left_side_sprites
                 self.xvel = self.walk_speed
                 self.direction = 1
           elif background_pos[0] < -1472:
              background_pos[0] = -1472
              if self.axis_pos[0] > 280:
                 self.axis_pos[0] = 280
                 self.sprites = self.right_side_sprites
                 self.xvel = -self.walk_speed
                 self.direction = -1
           else:
              self.axis_pos[0] += CENTER_X - self.axis_pos[0]
              if self.projectile and self.projectile['active']:
                 self.projectile['image_pos'][0] += CENTER_X - self.axis_pos[0]
                
    def idle(self):
        pass
           
    def peaceful_walk(self):
        self.anim_time += 1
        if self.anim_time  >= self.max_anim_time:
           self.anim_time = 0
           self.axis_pos[0] += self.xvel
           self.scroll_background()
           self.current_sprite = self.sprites[self.current_animation[self.animation_frame]]
           self.image = self.current_sprite['image']
           self.image_pos[0] = self.axis_pos[0] + self.current_sprite['axis_shift'][0]
           self.image_pos[1] = self.axis_pos[1] + self.current_sprite['axis_shift'][1]           
           self.animation_frame += 1
           if self.current_animation[self.animation_frame] == -1:
              self.animation_frame = 0
              
    def hurt(self):
        self.anim_time += 1
        if self.anim_time  >= self.max_anim_time:
           self.anim_time = 0
           self.current_sprite = self.sprites[self.current_animation[self.animation_frame]]
           self.image = self.current_sprite['image']
           self.image_pos[0] = self.axis_pos[0] + self.current_sprite['axis_shift'][0]
           self.image_pos[1] = self.axis_pos[1] + self.current_sprite['axis_shift'][1]
           self.animation_frame += 1
           if self.current_animation[self.animation_frame] == -1:
              self.yvel = 0
              self.current_state = 'death'
              self.change_animation('death')
           
    def death(self):
        self.yvel += 0.3
        self.axis_pos[0] += self.xvel
        self.axis_pos[1] += self.yvel
        if self.axis_pos[1] > 300:
           self.kill()
        self.anim_time += 1
        if self.anim_time  >= self.max_anim_time:
           self.anim_time = 0
           self.current_sprite = self.sprites[self.current_animation[self.animation_frame]]
           self.image = self.current_sprite['image']
           if self.current_animation[self.animation_frame] != -1:
              self.animation_frame += 1
        self.image_pos[0] = self.axis_pos[0] + self.current_sprite['axis_shift'][0]
        self.image_pos[1] = self.axis_pos[1] + self.current_sprite['axis_shift'][1]           
              
              
    def kill(self):
        Enemy.group.remove(self)  
        
    
class Enemy1(Enemy):
    def __init__(self, axis_pos, direction, opponent):
        self.left_side_sprites = Enemy1.left_side_sprites
        self.right_side_sprites = Enemy1.right_side_sprites
        self.sprites = self.left_side_sprites
        self.animations = Enemy1.animations
        self.opponent = opponent
        Enemy.__init__(self, axis_pos)
        self.states = {'idle':self.idle, 'walk':self.walk,'peaceful_walk':self.peaceful_walk,
                       'menacing_walk':self.menacing_walk, 'grab':self.grab,
                       'hurt':self.hurt, 'death':self.death}
        self.hit_reactions = {'hight':'hurt1', 'middle':'hurt2', 'low':'hurt3'}
        self.direction = direction
        if self.direction == 1:
           self.xvel = self.walk_speed 
           self.sprites = self.left_side_sprites
        if self.direction == -1:
           self.xvel = -self.walk_speed
           self.sprites = self.right_side_sprites        
        self.current_state = 'walk'
        self.change_animation('walk')
        
    def get_sprites(image):
        sprite_file = "data\\enemy1_sprite_info.spr"
        Enemy1.left_side_sprites = Enemy.get_sprites(image, sprite_file)
        Enemy1.right_side_sprites = Enemy.get_right_side_sprites(Enemy1.left_side_sprites)
        
    def get_animations():
        animation_file = "data\\enemy1_animation_info.anm"
        animations = {}            
        animations_data = load_animation_data(animation_file)
        animations['idle'] = animations_data[7]
        animations['walk'] = animations_data[0]
        animations['menacing_walk'] = animations_data[1]
        animations['grab'] = animations_data[2]
        animations['hurt1'] = animations_data[3]
        animations['hurt2'] = animations_data[4]
        animations['hurt3'] = animations_data[5]
        animations['death'] = animations_data[6]
        Enemy1.animations = animations
        
    def walk(self):
        self.anim_time += 1
        if self.anim_time  >= self.max_anim_time:
           self.anim_time = 0
           self.axis_pos[0] += self.xvel
           self.current_sprite = self.sprites[self.current_animation[self.animation_frame]]
           self.image = self.current_sprite['image']
           self.image_pos[0] = self.axis_pos[0] + self.current_sprite['axis_shift'][0]
           self.image_pos[1] = self.axis_pos[1] + self.current_sprite['axis_shift'][1]           
           self.animation_frame += 1
           if self.current_animation[self.animation_frame] == -1:
              self.animation_frame = 0
           if abs(self.axis_pos[0] - self.opponent.axis_pos[0]) <= 70:
              self.current_state = 'menacing_walk'
              self.change_animation('menacing_walk')
              
    def menacing_walk(self):
        self.anim_time += 1
        if self.anim_time  >= self.max_anim_time:
           self.anim_time = 0
           self.axis_pos[0] += self.xvel
           self.current_sprite = self.sprites[self.current_animation[self.animation_frame]]
           self.image = self.current_sprite['image']
           self.animation_frame += 1
           if self.current_animation[self.animation_frame] == -1:
              self.animation_frame = 0
           if len(self.opponent.grabbing_enemies) > 0:
              for i in range(len(self.opponent.grabbing_enemies)-1, -1, -1):
                  enemy = self.opponent.grabbing_enemies[i]
                  if enemy.direction == self.direction:
                     if abs(self.axis_pos[0] - enemy.axis_pos[0]) <= 10:
                        self.axis_pos[0] = enemy.axis_pos[0] - (10 * self.direction)
                        self.current_state = 'grab'
                        self.change_animation('grab')
                        self.opponent.current_state = 'grabbed'
                        self.opponent.grabbing_enemies.append(self)              
           if self.current_state != 'grab' and abs(self.axis_pos[0] - self.opponent.axis_pos[0]) <= 10:
              self.opponent.axis_pos[0] = self.axis_pos[0] + (10 * self.direction)
              self.current_state = 'grab'
              self.change_animation('grab')
              self.opponent.current_state = 'grabbed'
              self.opponent.grabbing_enemies.append(self)
           self.image_pos[0] = self.axis_pos[0] + self.current_sprite['axis_shift'][0]
           self.image_pos[1] = self.axis_pos[1] + self.current_sprite['axis_shift'][1]           
        
    def grab(self):
        pass

    
class Enemy2(Enemy):
    def __init__(self, axis_pos, direction, opponent):
        self.left_side_sprites = Enemy2.left_side_sprites
        self.right_side_sprites = Enemy2.right_side_sprites
        self.sprites = self.left_side_sprites
        self.animations = Enemy2.animations
        self.opponent = opponent
        Enemy.__init__(self, axis_pos)
        self.states = {'idle':self.idle, 'walk':self.walk, 'peaceful_walk':self.peaceful_walk,
                       'throw_knife':self.throw_knife,
                       'hurt':self.hurt, 'death':self.death}
        self.hit_reactions = {'hight':'hurt1', 'middle':'hurt2', 'low':'hurt2'}
        self.direction = direction
        self.projectile = Enemy2.projectile
        self.max_stalk_distance = 100
        self.min_stalk_distance = 20
        if self.direction == 1:
           self.xvel = self.walk_speed 
           self.sprites = self.left_side_sprites
        if self.direction == -1:
           self.xvel = -self.walk_speed
           self.sprites = self.right_side_sprites
        self.current_state = 'walk'
        self.change_animation('walk')
        
    def get_sprites(image):
        sprite_file = "data\\enemy2_sprite_info.spr"
        Enemy2.left_side_sprites = Enemy.get_sprites(image, sprite_file)
        Enemy2.right_side_sprites = Enemy.get_right_side_sprites(Enemy2.left_side_sprites)
        
    def get_animations():
        animation_file = "data\\enemy2_animation_info.anm"
        animations = {}            
        animations_data = load_animation_data(animation_file)
        animations['idle'] = animations_data[6]
        animations['walk'] = animations_data[0]
        animations['throw_knife1'] = animations_data[1]
        animations['throw_knife2'] = animations_data[2]
        animations['hurt1'] = animations_data[3]
        animations['hurt2'] = animations_data[4]
        animations['death'] = animations_data[5]
        animations['knife'] = animations_data[7]
        Enemy2.animations = animations
        
    def get_projectile():
        Enemy2.projectile = {'left_side_sprite':Enemy2.left_side_sprites[11],
                             'right_side_sprite':Enemy2.right_side_sprites[11],
                             'image':Enemy2.left_side_sprites[11]['image'],
                             'image_width':Enemy2.left_side_sprites[11]['image'].get_width(),
                             'image_pos':[0, 0],
                             'start_pos1':[25, 10],
                             'start_pos2':[30, 25],
                             'start_pos':[25, 10],
                             'offense_box':Enemy2.left_side_sprites[11]['offense_box'],
                             'xvel':5,
                             'launch_frame':6,
                             'active':False}
        
    def check_direction(self):
        if self.opponent.axis_pos[0] > self.axis_pos[0]:
           self.direction = 1
           self.sprites = self.left_side_sprites
        elif self.opponent.axis_pos[0] < self.axis_pos[0]:
           self.direction = -1
           self.sprites = self.right_side_sprites                 
        
    def idle(self):
        self.image_pos[0] = self.axis_pos[0] + self.current_sprite['axis_shift'][0]
        self.image_pos[1] = self.axis_pos[1] + self.current_sprite['axis_shift'][1]           
        distance = abs(self.axis_pos[0] - self.opponent.axis_pos[0])
        if distance > self.max_stalk_distance:
           self.xvel = self.walk_speed * self.direction
           self.current_state = 'walk'
           self.change_animation('walk')
        elif distance < self.min_stalk_distance:
           self.min_stalk_distance = 90
           self.direction *= -1
           if self.direction == 1:
              self.sprites = self.left_side_sprites
           elif self.direction == -1:
              self.sprites = self.right_side_sprites              
           self.xvel = self.walk_speed * self.direction
           self.current_state = 'walk'
           self.change_animation('walk')
        if not self.projectile['active']:   
           if random.randint(1, 10) == 10:
              self.check_direction()
              self.current_state = 'throw_knife' 
              start_pos = random.choice(('start_pos1', 'start_pos2'))
              self.projectile['start_pos'] = self.projectile[start_pos]
              if start_pos == 'start_pos1':
                 self.change_animation('throw_knife1')
              elif start_pos == 'start_pos2':
                 self.change_animation('throw_knife2')
           
    def walk(self):
        self.anim_time += 1
        if self.anim_time  >= self.max_anim_time:
           self.anim_time = 0
           self.axis_pos[0] += self.xvel
           """if background_pos[0] <= -1472 and self.axis_pos[0] > 280:
              self.axis_pos[0] = 280
           elif background_pos[0] >= 0 and self.axis_pos[0] < 135:
              self.axis_pos[0] = 135"""
           self.current_sprite = self.sprites[self.current_animation[self.animation_frame]]
           self.image = self.current_sprite['image']
           self.image_pos[0] = self.axis_pos[0] + self.current_sprite['axis_shift'][0]
           self.image_pos[1] = self.axis_pos[1] + self.current_sprite['axis_shift'][1]           
           self.animation_frame += 1
           if self.current_animation[self.animation_frame] == -1:
              self.animation_frame = 0
           if not self.projectile['active']:   
              if random.randint(1, 10) == 10:
                 self.check_direction()
                 self.current_state = 'throw_knife' 
                 start_pos = random.choice(('start_pos1', 'start_pos2'))
                 self.projectile['start_pos'] = self.projectile[start_pos]
                 if start_pos == 'start_pos1':
                    self.change_animation('throw_knife1')
                 elif start_pos == 'start_pos2':
                    self.change_animation('throw_knife2')
           distance = abs(self.axis_pos[0] - self.opponent.axis_pos[0])
           if self.min_stalk_distance < distance < self.max_stalk_distance:
              self.min_stalk_distance = 20
              self.check_direction()
              self.current_state = 'idle'
              self.change_animation('idle')
              
    def throw_knife(self):
        self.anim_time += 1
        if self.anim_time  >= self.max_anim_time:
           self.anim_time = 0
           if self.current_animation[self.animation_frame] != -1:
              self.current_sprite = self.sprites[self.current_animation[self.animation_frame]]
              self.image = self.current_sprite['image']
              self.image_pos[0] = self.axis_pos[0] + self.current_sprite['axis_shift'][0]
              self.image_pos[1] = self.axis_pos[1] + self.current_sprite['axis_shift'][1]
              self.animation_frame += 1
           if self.animation_frame >= self.projectile['launch_frame']:
              if not self.projectile['active']:
                 self.projectile['active'] = True
                 start_pos = self.projectile['start_pos']
                 if self.direction == 1:
                    self.projectile['image'] = self.projectile['left_side_sprite']['image']
                    self.projectile['offense_box'] = self.projectile['left_side_sprite']['offense_box']
                    self.projectile['image_pos'][0] =  self.image_pos[0] + start_pos[0]
                    self.projectile['image_pos'][1] =  self.image_pos[1] + start_pos[1]
                    self.projectile['xvel'] = 5
                 elif self.direction == -1:
                    self.projectile['image'] = self.projectile['right_side_sprite']['image']
                    self.projectile['offense_box'] = self.projectile['right_side_sprite']['offense_box']
                    start_pos_x = self.image.get_width() - start_pos[0] - self.projectile['image_width']
                    self.projectile['image_pos'][0] = self.image_pos[0] + start_pos_x
                    self.projectile['image_pos'][1] = self.image_pos[1] + start_pos[1]
                    self.projectile['xvel'] = -5
              elif self.current_animation[self.animation_frame] == -1:
                 self.check_direction()
                 self.current_state = 'idle'
                 self.change_animation('idle')
           
    def update_projectile(self):
        self.projectile['image_pos'][0] += self.projectile['xvel']
        projectile_x_pos = self.projectile['image_pos'][0]
        if projectile_x_pos > DISPLAY_SURFACE_WIDTH or projectile_x_pos + self.projectile['image_width'] < 0:
           self.projectile['active'] = False
           if self.current_state == 'throw_knife':
              self.current_state = 'idle'
              self.change_animation('idle')              
        if self.opponent.current_state not in ('hurt', 'death') \
        and self.projectile['offense_box'] != [0, 0, 0, 0]:
           offense_box = self.projectile['offense_box']
           offense_box = [self.projectile['image_pos'][0] + offense_box[0],
                          self.projectile['image_pos'][1] + offense_box[1],
                          offense_box[2], offense_box[3]]          
           defense_box = self.opponent.current_sprite['defense_box']
           defense_box = [self.opponent.image_pos[0] + defense_box[0],
                          self.opponent.image_pos[1] + defense_box[1],
                          defense_box[2], defense_box[3]]                    
           if offense_box[0] < defense_box[0] + defense_box[2] \
           and offense_box[0] + offense_box[2] > defense_box[0] \
           and offense_box[1] < defense_box[1] + defense_box[3] \
           and offense_box[1] + offense_box[3] > defense_box[1]:
               self.projectile['active'] = False
               if self.current_state == 'throw_knife':
                  self.current_state = 'idle'
                  self.change_animation('idle')               
        
def main():
    
    pygame.init()

    #Open Pygame window
    screen = pygame.display.set_mode((640, 480),) #add RESIZABLE or FULLSCREEN
    display_surface = pygame.Surface((320, 240)).convert()
    scaled_display_surface = pygame.transform.scale(display_surface,(640,480))
    #Title
    pygame.display.set_caption("kung-fu master")
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
    global gravity , ground_y_pos, background_pos
    gravity = 0.25
    ground_y_pos = 202
    enemies_load_data(image)
    enemy = Enemy2([190, ground_y_pos], 1, None)
    enemy.current_state = 'peaceful_walk'
    enemy.change_animation('walk')
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
            if event.type == KEYDOWN:
               if event.key == K_ESCAPE:    
                  pygame.quit()
                  sys.exit()

        enemy.states[enemy.current_state]()
        if enemy.projectile and enemy.projectile['active']:
           enemy.update_projectile()

        #draw everything
        display_surface.fill(BLUE)
        display_surface.blit(background, background_pos)
        display_surface.blit(enemy.image, enemy.image_pos)
        if enemy.projectile and enemy.projectile['active']:
           display_surface.blit(enemy.projectile['image'], enemy.projectile['image_pos'])
        display_surface.blit(foreground, background_pos)
        scaled_display_surface = pygame.transform.scale(display_surface,(640,480))
        screen.blit(scaled_display_surface, (0,0))
        pygame.display.flip()

if __name__ == "__main__":
    main()
