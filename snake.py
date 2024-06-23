

import pygame as pg
import sys
import random
from enum import Enum

#INiCIACIÓN DE PYGAME
pg.init()

#CONSTANTE GLOBALES DE SISTEMA
FPS = 30
DT_TIME = 1000 #milisegundos, que tanto se tarda en llegar el proximo frame en tiempo real

SCREEN_CAPTION = "Snake Game"
CELL_SIZE = 24
NUMBER_OF_CELLS = 25
FRAME_OFFSET = 75
SCREEN_WIDTH = NUMBER_OF_CELLS*CELL_SIZE # 750px
SCREEN_HEIGHT = NUMBER_OF_CELLS*CELL_SIZE #750px
GREEN = (173,204,96)
DARK_GREEN = (43,51,24)
class GAME_STATES(Enum):
    STOPPED = 0
    RUNNING = 1


SNAKE_UPDATE = pg.USEREVENT
pg.time.set_timer(SNAKE_UPDATE, 200)

#CONFIGURACIONES DE SISTEMA
screen = pg.display.set_mode(size=(2*FRAME_OFFSET + SCREEN_WIDTH,2*FRAME_OFFSET + SCREEN_HEIGHT))
pg.display.set_caption(SCREEN_CAPTION)
game_clock = pg.time.Clock()
is_running = True

#CARGANDO RECURSOS
font = pg.font.SysFont("Verdana" , 12 , bold = True)
food_surface = pg.image.load("graphics/fruit.png")
snake_eat_food_sound  = pg.mixer.Sound("sounds/eat.mp3")
snake_wall_sound  = pg.mixer.Sound("sounds/wall.mp3")

#DEFINICIÓN DE CLASES
## CLASE COMIDA
class Food:
    def __init__(self, snake_body):
        self.position = self.generate_random_pos(snake_body)
    def draw(self):
        food_rect = pg.Rect(FRAME_OFFSET+self.position.x*CELL_SIZE,FRAME_OFFSET+ self.position.y*CELL_SIZE, CELL_SIZE,CELL_SIZE)
        #pg.draw.rect(screen, DARK_GREEN, food_rect)
        screen.blit(food_surface, food_rect)
    def generate_random_cell(self):
        new_x_pos = random.randint(0,NUMBER_OF_CELLS - 1)
        new_y_pos = random.randint(0,NUMBER_OF_CELLS - 1)
        return pg.Vector2(new_x_pos, new_y_pos)
    def generate_random_pos(self, snake_body):
        position = self.generate_random_cell()
        while position in snake_body:
            position = self.generate_random_cell()
        return position
## CLASE SNAKE
class Snake:
    def __init__(self):
        self.body = [pg.Vector2(7,8), pg.Vector2(7,9),pg.Vector2(7,10)]
        self.direction = pg.Vector2(1,0)
        self.dir_val = 0
    def draw(self):
        for segment in self.body:
            segment_rect = pg.Rect(FRAME_OFFSET+segment.x*CELL_SIZE,FRAME_OFFSET+segment.y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pg.draw.rect(screen,DARK_GREEN, segment_rect,0,7)
    def update(self):
        self.body = self.body[:-1]
        self.body.insert(0, self.body[0] + self.direction)

    def reset(self):
        self.body = [pg.Vector2(7,8), pg.Vector2(7,9),pg.Vector2(7,10)]
        self.direction = pg.Vector2(1,0)
    def increase_size(self):
        self.body.insert(len(self.body) - 1,self.body[len(self.body) - 1])
    def move_to(self,dir):
        if dir == 0: #derecha
            self.direction = pg.Vector2(1,0)
            self.dir_val=0
        elif dir == 1: #abajo
            self.direction = pg.Vector2(0,1)
            self.dir_val=1
        elif dir == 2:#izquierda
            self.direction = pg.Vector2(-1,0)
            self.dir_val=2
        elif dir == 3:#arriba
            self.direction = pg.Vector2(0,-1)
            self.dir_val=3
    def get_dir(self):
        return self.dir_val

class Game:
    def __init__(self):
        self.snake = Snake()
        self.food = Food(self.snake.body)
        self.game_state = GAME_STATES.STOPPED
        self.points = 0
    def draw(self):
        if self.game_state == GAME_STATES.RUNNING:
            self.snake.draw()
            self.food.draw()
            self.show_points_ui()
        if self.game_state == GAME_STATES.STOPPED:
            start_ui_message()
    def start_new_game(self):
        self.reset_game()
        self.game_state = GAME_STATES.RUNNING
    def update(self):
        if self.game_state == GAME_STATES.RUNNING:
            self.snake.update()
            self.check_snake_collision_with_food()
            self.check_snake_collision_with_borders()
            self.check_snake_collision_with_tail()
    def check_snake_collision_with_food(self):
        if self.snake.body[0] == self.food.position:
            self.food.position = self.food.generate_random_pos(self.snake.body)
            snake_eat_food_sound.play() 
            self.add_point()
            self.snake.increase_size()
    def check_snake_collision_with_borders(self):
        if self.snake.body[0].x >= NUMBER_OF_CELLS or self.snake.body[0].x <= -1:
            self.game_over() 
            snake_wall_sound.play()
        if self.snake.body[0].y >= NUMBER_OF_CELLS or self.snake.body[0].y <= -1:
            self.game_over()
            snake_wall_sound.play()
        
    def check_snake_collision_with_tail(self):
        if self.snake.body[0] in self.snake.body[1:]:
            self.game_over()
    def add_point(self):
        self.points+=1
    def reset_game(self):
        self.snake.reset()
        self.food.position = self.food.generate_random_pos(self.snake.body)
        self.points = 0
    
    def game_over(self):
        self.game_state = GAME_STATES.STOPPED
    def show_points_ui(self):
        points_str = "Puntos: "+str(self.points)
        points_ui_render = font.render(points_str , True, pg.Color("black"))
        screen.blit(points_ui_render,[SCREEN_WIDTH+FRAME_OFFSET-30,FRAME_OFFSET+SCREEN_HEIGHT+30])




#FUNCION QUE MANEJA EL CONTADOR DE FPS EN PANTALLA
def fps_counter():
    fps = "fps: "+str(int(game_clock.get_fps()))
    fps_t = font.render(fps , True, pg.Color("black"))
    screen.blit(fps_t,[30,10])

def start_ui_message():
    text = "Dale click en el espacio para empezar un nuevo juego"
    start_t = font.render(text, True, pg.Color("black"))
    screen.blit(start_t,[SCREEN_WIDTH/2-FRAME_OFFSET-40, SCREEN_HEIGHT/2])


#DEFINIR OBJETOS
game = Game()

#GAME LOOP
while is_running:
    frame_time = game_clock.tick(FPS)
    dt = frame_time / DT_TIME
    #MANEJAR EVENTOS DE SISTEMA
    for event in pg.event.get():
        if event.type == SNAKE_UPDATE:
            game.update()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_RIGHT and game.snake.get_dir() != 2:
                game.snake.move_to(0)
            elif event.key == pg.K_DOWN and game.snake.get_dir() != 3:
                game.snake.move_to(1)
            elif event.key == pg.K_LEFT and game.snake.get_dir() != 0:
                game.snake.move_to(2)
            elif event.key == pg.K_UP and game.snake.get_dir() != 1:
                game.snake.move_to(3)
            if event.key == pg.K_SPACE and game.game_state == GAME_STATES.STOPPED:
                game.start_new_game()
        
        if event.type == pg.QUIT:
            is_running = False
    
    #MANEJAR ACTUALIZACIONES VISUALES
    screen.fill(GREEN)
    pg.draw.rect(screen, DARK_GREEN, (FRAME_OFFSET-5,FRAME_OFFSET-5, SCREEN_WIDTH+10, SCREEN_HEIGHT+10 ),5)
    ## DIBUJADO DE OBJETOS
    game.draw()
    ## DIBUJADO DE UI
    fps_counter()
    ##
    pg.display.update()
   
    if not is_running:
        pg.quit()
        sys.exit()



