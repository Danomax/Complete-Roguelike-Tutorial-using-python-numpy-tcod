#!/usr/bin/env python3
import tcod
import numpy as np

WINDOW_WIDTH, WINDOW_HEIGHT = 720, 480  # Window pixel resolution (when not maximized.)
FLAGS = tcod.context.SDL_WINDOW_RESIZABLE
WIDTH, HEIGHT = 60,25

FOV_RADIUS = 10
FOV_ALGORYTHM = tcod.FOV_RESTRICTIVE

colors = {
    'dark_wall': np.array([0, 0, 100,255],dtype='uint8'),
    'dark_ground': np.array([50, 50, 150,255],dtype='uint8'),
    'dark_pass': np.array([0,150,50,255],dtype='uint8'),
    'white': np.array([255,255,255,255],dtype='uint8'),
    'black': np.array([0,0,0,255],dtype='uint8'),
    'yellow': np.array([200,200,0,255],dtype='uint8'),
    'lights': np.array([100,100,-100,255],dtype='uint8')
}

def AddAtPos(A,B,pos):
    '''
    suma de matrices de distinta forma y con posicion de offset
    '''
    v_range1 = slice(max(0, pos[1]), max(min(pos[1] + B.shape[0], A.shape[0]), 0))
    h_range1 = slice(max(0, pos[0]), max(min(pos[0] + B.shape[1], A.shape[1]), 0))

    v_range2 = slice(max(0, -pos[1]), min(-pos[1] + A.shape[0], B.shape[0]))
    h_range2 = slice(max(0, -pos[0]), min(-pos[0] + A.shape[1], B.shape[1]))    
    
    A_ = A.copy()
    A_[v_range1,h_range1] += B[v_range2,h_range2]
    
    return A_

def Normalize(A):
    A_ = (A-np.min(A))
    A_ = A_ / np.max(A_)
    
    return A_

class BspDungeon(tcod.bsp.BSP):
    def __init__(self,x=0,y=0,width=1,height=1):
        super(BspDungeon, self).__init__(x,y,width,height)
        self.explored = np.zeros(shape=(WIDTH, HEIGHT),order='F',dtype=bool)
        self.map_buffer = np.zeros(shape=(WIDTH, HEIGHT),dtype=tcod.console.Console.DTYPE,order="F")
        self.map_buffer['ch'][:] = ord(' ')
        self.map_buffer['fg'][:] = colors["white"]
        self.map_buffer['bg'][:] = colors["black"]

    def carve_rect(self,game_map,x_ini,x_end,y_ini,y_end):
        self.map_buffer['bg'][x_ini:x_end,y_ini:y_end]=colors["dark_ground"]     
        game_map.walkable[x_ini:x_end,y_ini:y_end] = True
        game_map.transparent[x_ini:x_end,y_ini:y_end] = True        

    def carve_horiz(self,game_map,x,y_ini,y_end):
        self.map_buffer['bg'][x,y_ini:y_end]=colors["dark_ground"]     
        game_map.walkable[x,y_ini:y_end] = True
        game_map.transparent[x,y_ini:y_end] = True        
    
    def carve_vert(self,game_map,x_ini,x_end,y):
        self.map_buffer['bg'][x_ini:x_end,y]=colors["dark_ground"]     
        game_map.walkable[x_ini:x_end,y] = True
        game_map.transparent[x_ini:x_end,y] = True

    def create_room(self,node,game_map,wall_thick): 
        x_ini = node.x+wall_thick
        x_end = node.x+node.width-wall_thick  
        y_ini = node.y+wall_thick   
        y_end = node.y+node.height-wall_thick        
        self.carve_rect(game_map,x_ini,x_end,y_ini,y_end)

    def connect_rooms(self,node,game_map,wall_thick):
        if node.children:
            node1,node2=node.children
            node1_x = np.random.randint(node1.x+wall_thick,node1.x + node1.width-wall_thick)
            node1_y = np.random.randint(node1.y+wall_thick,node1.y + node1.height-wall_thick)
            node2_x = np.random.randint(node2.x+wall_thick,node2.x + node2.width-wall_thick)
            node2_y = np.random.randint(node2.y+wall_thick,node2.y + node2.height-wall_thick)
            if node.horizontal: 
                y_ini = node1_y
                y_end = node2_y
                if node1_x <= node2_x:
                    x_ini = node1_x
                    x_end = node2_x
                else:
                    x_ini = node2_x
                    x_end = node1_x  
                self.carve_horiz(game_map,x_ini,y_ini,node.position)
                self.carve_vert(game_map,x_ini,x_end+1,node.position)
                self.carve_horiz(game_map,x_end,node.position,y_end)
            else:
                x_ini = node1_x
                x_end = node2_x
                if node1_y <= node2_y:
                    y_ini = node1_y
                    y_end = node2_y
                else:
                    y_ini = node2_y
                    y_end = node1_y                                
                self.carve_vert(game_map,x_ini,node.position,y_ini)
                self.carve_horiz(game_map,node.position,y_ini,y_end+1)
                self.carve_vert(game_map,node.position,x_end,y_end)

def main() -> None:
    """Script entry point."""
    
    # Load the font, a 16 by 16 tile font with CP437 layout.
    tileset = tcod.tileset.load_tilesheet(
        "rKRKz.png", 16, 16, tcod.tileset.CHARMAP_CP437,
    )

    game_map = tcod.map.Map(WIDTH,HEIGHT,order="F")
    
    console = tcod.console.Console(WIDTH,HEIGHT,order="F")
    
    dungeon_bsp = BspDungeon(0,0,WIDTH,HEIGHT)
    dungeon_bsp.map_buffer['bg'][:]=colors["dark_wall"]
    
    dungeon_bsp.split_recursive(
        depth=4,
        min_width=12,
        min_height=8,
        max_horizontal_ratio=3.0,
        max_vertical_ratio=1.5
    )

    wall_thick = np.random.randint(2,4)

    for node in dungeon_bsp.pre_order():
        if node.children:
            #nodo tiene hijos
            dungeon_bsp.connect_rooms(node,game_map, wall_thick)
        else:
            #nodo tipo hoja, crear habitacion
            dungeon_bsp.create_room(node,game_map,wall_thick)
    
    x_start = np.random.randint(0,WIDTH)
    y_start = np.random.randint(0,HEIGHT)
    start_node = dungeon_bsp.find_node(x_start,y_start)
    x_start = np.random.randint(start_node.x + wall_thick, start_node.x+start_node.width-wall_thick)
    y_start = np.random.randint(start_node.y + wall_thick, start_node.y+start_node.height-wall_thick)
    
    player_pos = [x_start, y_start]

    fov_recompute = False
    game_map.compute_fov(player_pos[0],player_pos[1],FOV_RADIUS,light_walls=True,algorithm=FOV_ALGORYTHM)
    dungeon_bsp.explored |= game_map.fov
    bg_fov = np.ndarray(shape=(WIDTH,HEIGHT,3),order='F',dtype='uint8')
    
    fov_torch = True
    torch_noise = tcod.noise.Noise(
                    dimensions=3,
                    algorithm=tcod.noise.Algorithm.SIMPLEX,
                    seed=None
    )
    x=np.linspace(-1,1,FOV_RADIUS)
    xx,yy=np.meshgrid(x,x)
    zz=np.sqrt(xx**2 + yy**2)/np.sqrt(2)
    zz = Normalize(zz)
    dz=0
    
    # New window with pixel resolution of width×height.   
    with tcod.context.new(  
        width=WINDOW_WIDTH, height=WINDOW_HEIGHT, sdl_window_flags=FLAGS,
        console=console
    ) as context:
        while True:
            dx,dy=0,0           
            # Console size based on window resolution and tile size.
            console.clear()
            console.bg[:] = dungeon_bsp.map_buffer['bg'][:,:,0:3]
            for event in tcod.event.wait():
                if event.type == "KEYDOWN":
                    if event.sym == tcod.event.K_UP:
                        (dx,dy) = (0,-1)
                    if event.sym == tcod.event.K_RIGHT:
                        (dx,dy) = (1,0)                
                    if event.sym == tcod.event.K_DOWN:
                        (dx,dy) = (0,1) 
                    if event.sym == tcod.event.K_LEFT:
                        (dx,dy) = (-1,0)
                    if game_map.walkable[player_pos[0]+dx,player_pos[1]+dy]:                   
                        console.put_char(player_pos[0],player_pos[1],ord(' ')) 
                        player_pos[0] += dx
                        player_pos[1] += dy
                        fov_recompute = True                        
                context.convert_event(event)  # Sets tile coordinates for mouse events.
                #print(event)  # Print event names and attributes.
                if isinstance(event, tcod.event.Quit):
                    raise SystemExit()
                elif isinstance(event, tcod.event.WindowResized) and event.type == "WINDOWRESIZED":
                    pass  # The next call to context.new_console may return a different size.
            console.put_char(player_pos[0],player_pos[1],ord('@')) 

            if fov_recompute:
                game_map.compute_fov(player_pos[0],player_pos[1],FOV_RADIUS,light_walls=True,algorithm=FOV_ALGORYTHM)
                dungeon_bsp.explored |= game_map.fov
                fov_recompute = False
            
            console.bg[:] *= np.repeat(dungeon_bsp.explored,3).reshape(WIDTH, HEIGHT,3)
            if fov_torch:
                dz += 0.1
                grid = torch_noise[tcod.noise.grid(shape=(FOV_RADIUS,FOV_RADIUS,1),scale=1.,origin=(0,0,dz))]
                grid = np.squeeze(grid)
                #grid = Normalize(grid)
                gridzz = (zz*255).astype('uint8')           
                bg_fov[:][:][0] = AddAtPos(bg_fov[:][:][0],gridzz,player_pos)
                bg_fov[:][:][1] = AddAtPos(bg_fov[:][:][1],gridzz,player_pos)
                bg_fov[:][:][2] = AddAtPos(bg_fov[:][:][2],gridzz,player_pos)                       
            else:
                bg_fov[:] = colors['lights'][0:3]
                
            bg_fov *= game_map.fov.repeat(3).reshape(WIDTH, HEIGHT,3)
                
            console.bg[:] += bg_fov
            
            
            
            
            context.present(console, integer_scaling=True)            
                   
if __name__ == "__main__":
    main()
