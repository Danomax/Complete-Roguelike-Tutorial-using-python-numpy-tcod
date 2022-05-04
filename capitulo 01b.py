#!/usr/bin/env python3
import tcod

WINDOW_WIDTH, WINDOW_HEIGHT = 720, 480  # Window pixel resolution (when not maximized.)
FLAGS = tcod.context.SDL_WINDOW_RESIZABLE
WIDTH, HEIGHT = 40,30

def main() -> None:
    """Script entry point."""
    
    # Load the font, a 16 by 16 tile font with CP437 layout.
    tileset = tcod.tileset.load_tilesheet(
        "rKRKz.png", 16, 16, tcod.tileset.CHARMAP_CP437,
    )
    
    player_pos = [int(WIDTH / 2), int(HEIGHT / 2)]
       
    with tcod.context.new(  # New window with pixel resolution of width×height.
        width=WINDOW_WIDTH, height=WINDOW_HEIGHT, sdl_window_flags=FLAGS
    ) as context:
        while True:
            
            dx,dy=0,0
           
            # Console size based on window resolution and tile size.
            con = context.new_console(min_columns=5,min_rows=5,order="F")
            
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
                    player_pos[0] += dx
                    player_pos[1] += dy                     
                context.convert_event(event)  # Sets tile coordinates for mouse events.
                print(event)  # Print event names and attributes.
                if isinstance(event, tcod.event.Quit):
                    raise SystemExit()
                elif isinstance(event, tcod.event.WindowResized) and event.type == "WINDOWRESIZED":
                    pass  # The next call to context.new_console may return a different size.
            
            con.put_char(player_pos[0],player_pos[1],ord('@'))               
            context.present(con, integer_scaling=True)            
            

            
if __name__ == "__main__":
    main()
