import glob
from random import randint

from BaseGame import *
g = GameMode()
title_font = font.Font('geonms-font.ttf', 72)
menu_font = font.Font('geonms-font.ttf', 32)
background = transform.smoothscale(image.load('nmsplanet.jpg').convert(), (1280,800))
def AAfilledRoundedRect(surface,rect,color,radius=0.4): #Source: from Stack Overflow

    """
    AAfilledRoundedRect(surface,rect,color,radius=0.4)

    surface : destination
    rect    : rectangle
    color   : rgb or rgba
    radius  : 0 <= radius <= 1
    """

    rect         = Rect(rect)
    color        = Color(*color)
    alpha        = color.a
    color.a      = 0
    pos          = rect.topleft
    rect.topleft = 0,0
    rectangle    = Surface(rect.size,SRCALPHA)

    circle       = Surface([min(rect.size)*3]*2,SRCALPHA)
    draw.ellipse(circle,(0,0,0),circle.get_rect(),0)
    circle       = transform.smoothscale(circle,[int(min(rect.size)*radius)]*2)

    radius              = rectangle.blit(circle,(0,0))
    radius.bottomright  = rect.bottomright
    rectangle.blit(circle,radius)
    radius.topright     = rect.topright
    rectangle.blit(circle,radius)
    radius.bottomleft   = rect.bottomleft
    rectangle.blit(circle,radius)

    rectangle.fill((0,0,0),rect.inflate(-radius.w,0))
    rectangle.fill((0,0,0),rect.inflate(0,-radius.h))

    rectangle.fill(color,special_flags=BLEND_RGBA_MAX)
    rectangle.fill((255,255,255,alpha),special_flags=BLEND_RGBA_MIN)

    return surface.blit(rectangle,pos)
def loading_screen(percent, background):
    'Blits a loading sceen with "background" image and "percent" amount of bar filled'
    for e in event.get(): #Check for user quit
        if e.type == QUIT:
            quit()
    screen = g.screen#Alias for shorter typing
    title = title_font.render('outcast: the game', True, (255,255,255))
    msg = menu_font.render('loading', True, (255,255,255))
    width = 500#Width of progress bar
    height = 25#Height of progress bar
    main_status_rect = (screen.get_width()//2-width//2, #Rect tuple of bar underneath progress bar
                        600,
                        width,
                        height)
    progress_rect = (main_status_rect[0], #Rect tuple of progress bar
                     main_status_rect[1], int(percent*width), height)
##        screen.fill(0)
    screen.blit(background, (0,0))
    screen.blit(title, (screen.get_width()//2-title.get_width()//2, 100))
    screen.blit(msg, (screen.get_width()//2-msg.get_width()//2, 550))
##  Draw in rounded rectangle for base bar and progress bar
    AAfilledRoundedRect(screen, main_status_rect, (255,255,255), 0.4)
    AAfilledRoundedRect(screen, progress_rect, (53,121,169), 0.4)
    display.flip()
    
def main(menu_obj):
    'Main game function: takes in menu object'
    conn, username = (menu_obj.client.s, menu_obj.client.name) #Needed for maintaining socket connection
    global g
    g = GameMode() #Reset GameMode variable each time function is run to create a fresh instance
    inventory = Inventory(g.guns)
    dronebuttonlist = [image.load("Background/dronebutton.png"),image.load("Background/dronebuttondark.png")]
    openbuilding = image.load('Background/openbuilding.png')
    collision = image.load('Background/rocks+hole.png').convert_alpha()
    image_counter = [0] #Nested functions don't allow globalling, list allows usage of memory pointers
                        #to achieve similar effect

    #Shotgun bullet range
    #Gun reload time
    #Storm show up on minimap


    inventory = Inventory(g.guns) #Inventory object
    dronebuttonlist = [image.load("Background/dronebutton.png"),
                       image.load("Background/dronebuttondark.png")] #Drone buttons for Ready and Timeout stages

    #collision = image.load('Background/rocks+hole.png').convert_alpha()
    #buildingcollision = image.load('Background/buildings.png').convert_alpha()

    def scale_and_load(path, factor):
        'Takes an image path, scales and converts by factor'
        img = image.load(path).convert_alpha()

        x, y = img.get_size()
        
        image_counter[0] += 1#Used for loading screen
        loading_screen(image_counter[0]//44, background)#44 comes from pre-calculated total
        return transform.smoothscale(img, (int(x/factor), int(y/factor)))#Return transformed image
    def get_fps(old_time):
        'Returns FPS based on delta time'
        return int(1/(t.time()-old_time))

    newSprites = [[scale_and_load(file, 3) for file in glob.glob('Sprites/Idle/*.png')],
                  [scale_and_load(file, 3) for file in glob.glob('Sprites/Shoot/*.png')],
                  [scale_and_load(file, 3) for file in glob.glob('Sprites/ShootIdle/*.png')]]

    droneSprite = [[scale_and_load(file, 2) for file in glob.glob('newSprites/drone/*.png')]]
    droneB = False#Drone on/off boolean
    p = Player(g, username, (1200, 1200), 10, 'player')#Main player instance
    p.ammo =[100 for i in range(len(g.guns))]#Fill existing guns to the brim
    client = Client(p,0,g, conn, newSprites)#Networking object to communicate with server
    threading.Thread(target=client.get_data).start()#Connect to server
    drone_start = 31 #Drone can be used first (30 seconds)
    fps_font = font.SysFont('Arial',18)
    g.current_actor = p
    myClock = time.Clock()
    last_fire = 0 #Last time user fired for cooldowns
    #Mouse Cursor
##    reticle = (               #sized 24x24
##      "        ........        ",
##      "      ..   ..   ..      ",
##      "     ..    ..    ..     ",
##      "    ..     ..     ..    ",
##      "   ..      ..      ..   ",
##      "  ..      oooo      ..  ",
##      " ..        ..        .. ",
##      "..         ..         ..",
##      "..         ..         ..",
##      "..         ..         ..",
##      "..   o    X..X    o   ..",
##      ".....o.....XX.....o.....",
##      ".....o.....XX.....o.....",
##      "..   o    X..X    o   ..",
##      "..         ..         ..",
##      "..         ..         ..",
##      "..         ..         ..",
##      " ..        ..        .. ",
##      "  ..      oooo      ..  ",
##      "   ..      ..      ..   ",
##      "    ..     ..     ..    ",
##      "     ..    ..    ..     ",
##      "      ..   ..   ..      ",
##      "        ........        ")#Took me 2 hours
##    datatuple,masktuple=cursors.compile(reticle,black='.',white='X',xor='o')#Compile the code
##    mouse.set_cursor((24,24),(12,12),datatuple,masktuple)
    while g.running:
        m = mouse.get_pressed()
        mx, my = mouse.get_pos()
        myClock.tick(144)#My monitor is 144hz, no need to go faster
        FPS = myClock.get_fps()
        if inventory.inventoryP[inventory.state].rate > 0 and m[0] == 1:
            left_click = True
        else:
            left_click = False
        for e in event.get():
            if e.type == QUIT:
                g.running = False
            if e.type == MOUSEBUTTONDOWN:
                if g.droneB == False:
                    if e.button == 1:
                        left_click = True
                    elif e.button == 5: #scroll to move right
                        inventory.switch("RIGHT")
                    elif e.button == 4:#scroll to move left
                        inventory.switch("LEFT")
            elif e.type == KEYDOWN:
                keys = key.get_pressed()
                if keys[K_z]:
                    g.drone_click(g,p,client) #Activate drone
                if keys[K_e] and g.current_actor.type == 'player':
                    #g.weapon_pickup(p,inventory)
                    client.weapon_pickup(inventory) #Pickup weapon
                if keys[K_f] and g.current_actor.type == 'player':
                    g.open_door(p) #Enter buildings
                if keys[K_g] and g.current_actor.type == 'player':
                    inventory.remove_item(p) #Drop items
                    
                #open door
                elif e.key == K_ESCAPE:
                    running = False #Alternative 'exit' key

        keys = key.get_pressed()
        old_time = t.time()
        g.current_actor.rotation = int(degrees(atan2((g.screen.get_width()//2-mx),(g.screen.get_height()//2-my))))
        px, py = g.current_actor.get_pos()
        #SPRINT only for player
        if keys[K_LSHIFT] and m[0] == 1:
            p.speed = 6
            
        elif keys[K_LSHIFT]:
            p.speed = 14
            
            
        else:
            p.speed = 10
            
## ----------Move character, while making sure character doesn't go off-screen. Sends in masks for collision checking -----
        #UP
        if keys[K_w] and g.screen.get_height()//2<py-g.current_actor.speed:
            g.current_actor.move('UP', g.background, g.collisionmap,g.buildingmap,g.openbuilding, FPS,g.building)
        #DOWN
        if keys[K_s] and py+g.current_actor.speed<g.background.get_height()-g.screen.get_height()//2:
            g.current_actor.move('DOWN', g.background, g.collisionmap,g.buildingmap,g.openbuilding, FPS,g.building)
        #LEFT
        if keys[K_a] and g.screen.get_width()//2<px-g.current_actor.speed:
            g.current_actor.move('LEFT', g.background, g.collisionmap,g.buildingmap,g.openbuilding, FPS,g.building)
        #RIGHT
        if keys[K_d] and px+g.current_actor.speed<g.background.get_width()-g.screen.get_width()//2:
            g.current_actor.move('RIGHT', g.background, g.collisionmap,g.buildingmap,g.openbuilding, FPS,g.building)
##-------------------------------------------------------------------------------------------------------------------------
        if g.current_actor.type == 'player' and left_click and (t.time() - last_fire > 0.3 or (inventory.inventoryP[inventory.state].rate >0 and t.time() - last_fire > inventory.inventoryP[inventory.state].rate)):
            last_fire = t.time()
            p.fire(inventory, FPS)
            
        if m[0] == 1 or m[2] ==1:
            p.state = 1
        else:
            p.player_state(inventory)
            


        g.draw_screen(g.current_actor)
        if g.current_actor.type == 'player': #Player object specific functions
            p.update_gif(newSprites) #Update player GIFS
            p.render_player(newSprites, g) #Draw player
            client.render_other_players() #Render other players from player perspective
            client.update_player(p) #Update networking system with latest client info
        else: #Drone object specific functions
            client.render_other_players(newSprites) #Tells function to render other players from drone perspective
            client.update_drone(g.drone) #Update networking system with latest drone info
            g.drone.update_gif(droneSprite) #Update drone GIF
            g.drone.render_player(droneSprite, g) #Draw the drone
            #----------If time runs out ------
            if t.time()-g.drone_start >10:
                client.drone = 0
                g.current_actor = p
                g.drone_start = t.time()
                g.droneB = False
            #---------------------------------
        #g.draw_weapons(g.screen,g.current_actor.pos)
        client.draw_weapons(g.screen,g.current_actor.pos) #Draw weapons on the ground
        render_bullets(g, p, client, FPS) #Draw in player bullets
        client.render_enemy_bullets(inventory.inventoryP[inventory.state],g.screen) #Draw in enemy bullets
        inventory.draw_inventory(g.screen,p.ammo) #Draw in inventory
        Drone.draw_drone(g.screen,g.droneB,dronebuttonlist,(t.time()-g.drone_start)) #Draw in drone button
        fps = fps_font.render(str(int(FPS)), True, (0,0,0)) 
        g.screen.blit(fps, (1200,10)) #Draw in FPS
        if not check_health(p): #Check if player is dead
            client.s.send(pickle.dumps("leaving"))
            p.die(g.screen) #drawing in dead screen
            g.running = False
            time.wait(500)
            client.done = True
        display.flip()
    client.s.close()
    while not client.done: #Wait for client object to display victory page
        pass
    return 'menu', p.name

#testing branch merge
if __name__ == '__main__':
    main(socket.socket(),'james')

