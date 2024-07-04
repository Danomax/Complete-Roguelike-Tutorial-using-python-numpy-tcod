#!/usr/bin/env python3
import tcod
import numpy as np

WINDOW_WIDTH, WINDOW_HEIGHT = 720, 480  # Window pixel resolution (when not maximized.)
FLAGS = tcod.context.SDL_WINDOW_RESIZABLE
WIDTH, HEIGHT = 40,30

colors = {
    'dark_wall': np.array([0, 0, 100,255]),
    'dark_ground': np.array([50, 50, 150,255]),
    'dark_pass': np.array([0,150,50,255]),
    'white': np.array([255,255,255,255]),
    'black': np.array([0,0,0,255]),
    'yellow': np.array([200,200,0,255])
}

def main() -> None:
    """Script entry point."""
    
    # Load the font, a 16 by 16 tile font with CP437 layout.
    tileset = tcod.tileset.load_tilesheet(
        "rKRKz.png", 16, 16, tcod.tileset.CHARMAP_CP437,
    )

    game_map = tcod.map.Map(WIDTH,HEIGHT,order="F")
    
    console = tcod.console.Console(WIDTH,HEIGHT,order="F")
    player_pos = [int(WIDTH / 2), int(HEIGHT / 2)]
    #console.ch[player_pos[0],player_pos[1]]=ord('@')
    
    game_map.transparent[:] = False
    game_map.walkable[:] = False
    console.rgba[:]['bg'] = colors['dark_wall']
    game_map.transparent[1:-1,1:-1] = True
    game_map.walkable[1:-1,1:-1] = True
    console.rgba[1:-1,1:-1]['bg']=colors['dark_ground']
    
    #game_map.compute_fov(player_pos[0],player_pos[1])
    
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
            #game_map.compute_fov(player_pos[0],player_pos[1])         
            context.present(console, integer_scaling=True)            
                   
if __name__ == "__main__":
    main()
