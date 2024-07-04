#!/usr/bin/env python3
import tcod
import numpy as np

WINDOW_WIDTH, WINDOW_HEIGHT = 720, 480  # Window pixel resolution (when not maximized.)
FLAGS = tcod.context.SDL_WINDOW_RESIZABLE
WIDTH, HEIGHT = 60,30


colors = {
    'dark_wall': np.array([0, 0, 100,255]),
    'dark_ground': np.array([50, 50, 150,255]),
    'dark_pass': np.array([0,150,50,255]),
    'white': np.array([255,255,255,255]),
    'black': np.array([0,0,0,255]),
    'yellow': np.array([200,200,0,255])
}

class BspDungeon(tcod.bsp.BSP):
    def __init__(self,x=0,y=0,width=1,height=1):
        super(BspDungeon, self).__init__(x,y,width,height)

    def create_room(self,node,console,game_map,wall_thick): 
        x_ini = node.x+wall_thick
        x_end = node.x+node.width-wall_thick  
        y_ini = node.y+wall_thick   
        y_end = node.y+node.height-wall_thick        
        console.rgba[x_ini:x_end,y_ini:y_end]['bg']=colors["dark_ground"]       
        game_map.walkable[x_ini:x_end,y_ini:y_end] = True
        game_map.transparent[x_ini:x_end,y_ini:y_end] = True

    def connect_rooms(self,node,console,game_map,wall_thick):
        if node.children:
            node1,node2=node.children
            node1_x = np.random.randint(node1.x+wall_thick,node1.x + node1.width-wall_thick)
            node1_y = np.random.randint(node1.y+wall_thick,node1.y + node1.height-wall_thick)
            node2_x = np.random.randint(node2.x+wall_thick,node2.x + node2.width-wall_thick)
            node2_y = np.random.randint(node2.y+wall_thick,node2.y + node2.height-wall_thick)
            x_ini = node1_x
            x_end = node1_x 
            y_ini = node2_y
            y_end = node2_y
            if node.horizontal:
                y_ini = node1_y
                y_end = node2_y
                if node1_x <= node2_x:
                    x_ini = node1_x
                    x_end = node2_x
                else:
                    x_ini = node2_x
                    x_end = node1_x  
                #print('horizontal: xini'+str(x_ini)+'xend'+str(x_end)+'yini'+str(y_ini)+'yend'+str(y_end))                  
                console.rgba[x_ini,y_ini:node.position]['bg']=colors["dark_ground"]       
                game_map.walkable[x_ini,y_ini:node.position] = True
                game_map.transparent[x_ini,y_ini:node.position] = True

                console.rgba[x_ini:x_end+1,node.position]['bg']=colors["dark_ground"]       
                game_map.walkable[x_ini:x_end+1,node.position] = True
                game_map.transparent[x_ini:x_end+1,node.position] = True

                console.rgba[x_end,node.position:y_end]['bg']=colors["dark_ground"]       
                game_map.walkable[x_end,node.position:y_end] = True
                game_map.transparent[x_end,node.position:y_end] = True
            else:
                x_ini = node1_x
                x_end = node2_x
                if node1_y <= node2_y:
                    y_ini = node1_y
                    y_end = node2_y
                else:
                    y_ini = node2_y
                    y_end = node1_y                                
                #print('vertical: xini'+str(x_ini)+'xend'+str(x_end)+'yini'+str(y_ini)+'yend'+str(y_end))                    
                console.rgba[x_ini:node.position,y_ini]['bg']=colors["dark_ground"]       
                game_map.walkable[x_ini:node.position,y_ini] = True
                game_map.transparent[x_ini:node.position,y_ini] = True

                console.rgba[node.position,y_ini:y_end+1]['bg']=colors["dark_ground"]       
                game_map.walkable[node.position,y_ini:y_end+1] = True
                game_map.transparent[node.position,y_ini:y_end+1] = True
             
                console.rgba[node.position:x_end,y_end]['bg']=colors["dark_ground"]       
                game_map.walkable[node.position:x_end,y_end] = True
                game_map.transparent[node.position:x_end,y_end] = True

def main() -> None:
    """Script entry point."""
    
    # Load the font, a 16 by 16 tile font with CP437 layout.
    tileset = tcod.tileset.load_tilesheet(
        "rKRKz.png", 16, 16, tcod.tileset.CHARMAP_CP437,
    )

    game_map = tcod.map.Map(WIDTH,HEIGHT,order="F")
    
    console = tcod.console.Console(WIDTH,HEIGHT,order="F")
    console.rgba[:]['bg']=colors["dark_wall"]
    
    dungeon_bsp = BspDungeon(0,0,WIDTH,HEIGHT)
    
    dungeon_bsp.split_recursive(
        depth=5,
        min_width=10,
        min_height=8,
        max_horizontal_ratio=3.0,
        max_vertical_ratio=1.5
    )

    wall_thick = np.random.randint(2,4)
    
    for node in dungeon_bsp.pre_order():
        if node.children:
            #nodo tiene hijos
            dungeon_bsp.connect_rooms(node,console,game_map,wall_thick)
        else:
            #nodo tipo hoja, crear habitacion
            dungeon_bsp.create_room(node,console,game_map,wall_thick)
            #pass
    
    x_start = np.random.randint(0,WIDTH)
    y_start = np.random.randint(0,HEIGHT)
    start_node = dungeon_bsp.find_node(x_start,y_start)
    x_start = np.random.randint(start_node.x + wall_thick, start_node.x+start_node.width-wall_thick)
    y_start = np.random.randint(start_node.y + wall_thick, start_node.y+start_node.height-wall_thick)
    
    player_pos = [x_start, y_start]

    
    # New window with pixel resolution of width×height.   
    with tcod.context.new(  
        width=WINDOW_WIDTH, height=WINDOW_HEIGHT, sdl_window_flags=FLAGS,
        console=console
    ) as context:
        while True:
            dx,dy=0,0           
            # Console size based on window resolution and tile size.
            
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
                context.convert_event(event)  # Sets tile coordinates for mouse events.
                #print(event)  # Print event names and attributes.
                if isinstance(event, tcod.event.Quit):
                    raise SystemExit()
                elif isinstance(event, tcod.event.WindowResized) and event.type == "WINDOWRESIZED":
                    pass  # The next call to context.new_console may return a different size.
            console.put_char(player_pos[0],player_pos[1],ord('@'))             
            context.present(console, integer_scaling=True)            
                   
if __name__ == "__main__":
    main()
