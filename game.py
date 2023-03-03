import math
import random
import time
import tkinter as tk

frames = 0
score = 0
canvas = None
app = None


BUFFER_W = 320
BUFFER_H = 240

DISP_SCALE = 2
DISP_W = BUFFER_W * DISP_SCALE
DISP_H = BUFFER_H * DISP_SCALE

SHIP_W = 12 * DISP_SCALE
SHIP_H = 13 * DISP_SCALE

SHIP_SHOT_W = 2 * DISP_SCALE
SHIP_SHOT_H = 9 * DISP_SCALE

LIFE_W = 6 * DISP_SCALE
LIFE_H = 6 * DISP_SCALE

ALIEN_W = [14 * DISP_SCALE, 13 * DISP_SCALE, 45 * DISP_SCALE]
ALIEN_H = [9 * DISP_SCALE, 10 * DISP_SCALE, 27 * DISP_SCALE]

ALIEN_BUG_W      = ALIEN_W[0]
ALIEN_BUG_H      = ALIEN_H[0]
ALIEN_ARROW_W    = ALIEN_W[1]
ALIEN_ARROW_H    = ALIEN_H[1]
ALIEN_THICCBOI_W = ALIEN_W[2]
ALIEN_THICCBOI_H = ALIEN_H[2]

ALIEN_SHOT_W = 4 * DISP_SCALE
ALIEN_SHOT_H = 4 * DISP_SCALE

EXPLOSION_FRAMES = 4
SPARKS_FRAMES    = 3

KEY_SEEN = 1
KEY_RELEASED = 2

KEY_Left = 65361
KEY_Right = 65363
KEY_Up = 65362
KEY_Down = 65364
KEY_Space = 32
KEY_Escape = 65307
key = {
  KEY_Left: 0,
  KEY_Right: 0,
  KEY_Up: 0,
  KEY_Down: 0,
  KEY_Space: 0
}

keyrelease = {
  KEY_Left: -1,
  KEY_Right: -1,
  KEY_Up: -1,
  KEY_Down: -1,
  KEY_Space: -1
}


def collide(ax1, ay1, ax2, ay2, bx1, by1, bx2, by2):
    if ax1 > bx2: 
        return False
    if ax2 < bx1:
        return False
    if ay1 > by2:
        return False
    if ay2 < by1:
        return False

    return True

#--- sprites ---
sprites = {  
    "ship_shot": [0, 1],
    "life": 0,
  
    "alien": [0, 1, 2],
    "alien_shot": 0,
  
    "explosion": [0, 1, 2, 3],
    "sparks": [0, 1, 2],
  
    "star": 0,
}

def sprite_new(sprite_name):
    img = tk.PhotoImage(file="sprites/" + sprite_name + ".png")
    return img.zoom(DISP_SCALE, DISP_SCALE)

def sprites_init():
    global sprites

    sprites["life"] = sprite_new("life")

    sprites["ship"] = sprite_new("ship")
    sprites["ship_shot"][0] = sprite_new("shipshot0")
    sprites["ship_shot"][1] = sprite_new("shipshot1")

    sprites["alien"][0] = sprite_new("alienbug")
    sprites["alien"][1] = sprite_new("alienarrow")
    sprites["alien"][2] = sprite_new("alienthiccboi")

    sprites["alien_shot"] = sprite_new("alienshot")

    sprites["explosion"][0] = sprite_new("explosion0")
    sprites["explosion"][1] = sprite_new("explosion1")
    sprites["explosion"][2] = sprite_new("explosion2")
    sprites["explosion"][3] = sprite_new("explosion3")

    sprites["sparks"][0] = sprite_new("sparks0")
    sprites["sparks"][1] = sprite_new("sparks1")
    sprites["sparks"][2] = sprite_new("sparks2")
  
    sprites["star"] = tk.PhotoImage(file="sprites/star.png")

#--- fx ---
FX_N = 128
fx = []

def fx_init():
    global FX_N, fx, canvas
    for i in range(FX_N):
        a_fx = {
          "used": False,
          "picture": canvas.create_image(0, 0, image=sprites["sparks"][0], anchor=tk.NW),
        }
        canvas.itemconfigure(a_fx["picture"], state=tk.HIDDEN)
        fx.append(a_fx)

def fx_add(spark, x, y):
    global FX_N, fx, canvas
    for i in range(FX_N):
        a_fx = fx[i]
        if not a_fx["used"]:
          a_fx["x"] = x
          a_fx["y"] = y
          a_fx["frame"] = 0
          a_fx["spark"] = spark
          a_fx["used"] = True
          canvas.itemconfigure(a_fx["picture"], state=tk.NORMAL)
          return

def fx_update():
    global FX_N, fx, canvas, EXPLOSION_FRAMES, SPARKS_FRAMES
    for i in range(FX_N):
        a_fx = fx[i]
        if a_fx["used"]:
            a_fx["frame"] = a_fx["frame"] + 1

            if ((not a_fx["spark"] and a_fx["frame"] == EXPLOSION_FRAMES * 2) or
                (a_fx["spark"] and a_fx["frame"] == SPARKS_FRAMES * 2)):
                a_fx["used"] = False
                canvas.itemconfigure(a_fx["picture"], state=tk.HIDDEN)


def fx_draw():
    global FX_N, fx, sprites, canvas, DISP_SCALE
    for i in range(FX_N):
        a_fx = fx[i]
        if a_fx["used"]:
            frame_display = math.floor(a_fx["frame"] / 2)
            bmp = sprites["sparks"][frame_display] if a_fx["spark"] else sprites["explosion"][frame_display]
      
            width = bmp.width()
            height = bmp.height()
            x = a_fx["x"] - math.floor(width / 2)
            y = a_fx["y"] - math.floor(height / 2)
      
            picture = a_fx["picture"]
            canvas.itemconfigure(picture, image=bmp)
            canvas.coords(picture, x, y)

#--- shots ---
SHOTS_N = 128
shots = []

def shots_init():
    global SHOTS_N, shots, canvas, sprites
    for i in range(SHOTS_N):
        shot = {
          "used": False,
          "picture": canvas.create_image(0, 0, image=sprites["alien_shot"], anchor=tk.NW),
        }
        shots.append(shot)
        canvas.itemconfigure(shot["picture"], state=tk.HIDDEN)

def shots_add(ship, straight, x, y):
    global SHOTS_N, shots, SHIP_SHOT_W, ALIEN_SHOT_W, ALIEN_SHOT_H, canvas
    for i in range(SHOTS_N):
        shot = shots[i]
        if not shot["used"]:
            shot["ship"] = ship

            if ship:
                shot["x"] = x - math.floor(SHIP_SHOT_W / 2)
                shot["y"] = y
            else: # alien
                shot["x"] = x - math.floor(ALIEN_SHOT_W / 2)
                shot["y"] = y - math.floor(ALIEN_SHOT_H / 2)

                if straight:
                    shot["dx"] = 0
                    shot["dy"] = 4
                else:
                    shot["dx"] = random.randint(-4, 4) 
                    shot["dy"] = random.randint(-4, 4) 

                # if the shot has no speed, don't bother
                if shot["dx"] == 0 and shot["dy"] == 0:
                    return True
                
                shot["frame"] = 0

            shot["frame"] = 0
            shot["used"] = True
            canvas.itemconfigure(shot["picture"], state=tk.NORMAL)
            return True
    
    return False

def shots_update():
    global SHOTS_N, shots, ALIEN_SHOT_W, DISP_W, ALIEN_SHOT_H, DISP_H, SHIP_SHOT_H

    for i in range(SHOTS_N):
        shot = shots[i]
        if not shot["used"]:
            continue
        
        picture = shot["picture"]
          
        if shot["ship"]:
            shot["y"] = shot["y"] - 10

            if shot["y"] < -SHIP_SHOT_H:
                shot["used"] = False
                canvas.itemconfigure(shot["picture"], state=tk.HIDDEN)
                continue
        else: # alien
            shot["x"] = shot["x"] + shot["dx"]
            shot["y"] = shot["y"] + shot["dy"]

            if (shot["x"] < -ALIEN_SHOT_W or
              shot["x"] > DISP_W or
              shot["y"] < -ALIEN_SHOT_H or
              shot["y"] > DISP_H):
            
                shot["used"] = False
                canvas.itemconfigure(shot["picture"], state=tk.HIDDEN)
                continue

        shot["frame"] = shot["frame"] + 1

def shots_collide(ship, x, y, w, h):
    global SHOTS_N, shots, ALIEN_SHOT_W, ALIEN_SHOT_H, SHIP_SHOT_W, SHIP_SHOT_H

    for i in range(SHOTS_N):
        shot = shots[i]
        if not shot["used"]:
            continue

        # don't collide with one's own shots
        if shot["ship"] == ship:
            continue

        sw = 0 
        sh = 0
        if ship:
            sw = ALIEN_SHOT_W
            sh = ALIEN_SHOT_H
        else:
            sw = SHIP_SHOT_W
            sh = SHIP_SHOT_H

        if collide(x, y, x+w, y+h, shot["x"], shot["y"], shot["x"]+sw, shot["y"]+sh):
            fx_add(True, shot["x"] + math.floor(sw / 2), shot["y"] + math.floor(sh / 2))
            shot["used"] = False
            canvas.itemconfigure(shot["picture"], state=tk.HIDDEN)
            return True

    return False

def shots_draw():
    global SHOTS_N, shots, SHIP_SHOT_W, SHIP_SHOT_H, ALIEN_SHOT_W, ALIEN_SHOT_H, sprites, canvas

    for i in range(SHOTS_N):
        shot = shots[i]
        if shot["used"]:
            frame_display = math.floor(shot["frame"] / 2) % 2
            picture = shot["picture"]
            if shot["ship"]:
                canvas.itemconfigure(shot["picture"], image=sprites["ship_shot"][frame_display])
                canvas.coords(shot["picture"], shot["x"], shot["y"])
            else:# alien
                canvas.itemconfigure(shot["picture"], image=sprites["alien_shot"])
                canvas.coords(shot["picture"], shot["x"], shot["y"])


#--- ship ---
SHIP_SPEED = 3 * DISP_SCALE
SHIP_MAX_X = DISP_W - SHIP_W
SHIP_MAX_Y = DISP_H - SHIP_H

ship = {}

def ship_init():
    global ship, SHIP_W, SHIP_H, DISP_W, DISP_H, canvas, sprites
    
    ship["x"] = math.floor(DISP_W / 2) - math.floor(SHIP_W / 2)
    ship["y"] = math.floor(DISP_H / 2) - math.floor(SHIP_H / 2)
    ship["picture"] = canvas.create_image(ship["x"], ship["y"], image=sprites["ship"], anchor=tk.NW)
    
    ship["shot_timer"] = 0
    ship["lives"] = 3
    ship["respawn_timer"] = 0
    ship["invincible_timer"] = 120

def ship_update():
    global ship, key, SHIP_SPEED, SHIP_MAX_X, SHIP_MAX_Y, SHIP_W, SHIP_H, KEY_Left, KEY_Right, KEY_Up, KEY_Down, KEY_Space
    if ship["lives"] < 0:
        return

    if ship["respawn_timer"] > 0:
        ship["respawn_timer"] = ship["respawn_timer"] - 1
        return

    if key[KEY_Left] > 0:
        ship["x"] = ship["x"] - SHIP_SPEED
    
    if key[KEY_Right] > 0:
        ship["x"] = ship["x"] + SHIP_SPEED
   
    if key[KEY_Up] > 0:
        ship["y"] = ship["y"] - SHIP_SPEED
   
    if key[KEY_Down] > 0:
        ship["y"] = ship["y"] + SHIP_SPEED

    if ship["x"] < 0:
        ship["x"] = 0
   
    if ship["y"] < 0:
        ship["y"] = 0
  
    if ship["x"] > SHIP_MAX_X:
        ship["x"] = SHIP_MAX_X
    
    if ship["y"] > SHIP_MAX_Y:
        ship["y"] = SHIP_MAX_Y

    if ship["invincible_timer"] > 0:
        ship["invincible_timer"] = ship["invincible_timer"] - 1
    else:
        if shots_collide(True, ship["x"], ship["y"], SHIP_W, SHIP_H):
            x = ship["x"] + math.floor(SHIP_W / 2)
            y = ship["y"] + math.floor(SHIP_H / 2)
            fx_add(False, x, y)
            fx_add(False, x+8, y+4)
            fx_add(False, x-4, y-8)
            fx_add(False, x+2, y-10)

            ship["lives"] = ship["lives"] - 1
            ship["respawn_timer"] = 90
            ship["invincible_timer"] = 180

    if ship["shot_timer"] > 0:
        ship["shot_timer"] = ship["shot_timer"] - 1
    elif key[KEY_Space] > 0:
        x = ship["x"] + math.floor(SHIP_W / 2)
        if shots_add(True, False, x, ship["y"]):
            ship["shot_timer"] = 5


def ship_draw():
    global ship, canvas

    if ship["lives"] < 0:
        canvas.itemconfigure(ship["picture"], state=tk.HIDDEN)
        return

    if ship["respawn_timer"] > 0:
        canvas.itemconfigure(ship["picture"], state=tk.HIDDEN)
        return
   
    if (math.floor(ship["invincible_timer"] / 2) % 3) == 1:
        canvas.itemconfigure(ship["picture"], state=tk.HIDDEN)
        return
    
    canvas.coords(ship["picture"], ship["x"], ship["y"])
    canvas.itemconfigure(ship["picture"], state=tk.NORMAL)


#--- aliens ---
ALIEN_TYPE_BUG = 0
ALIEN_TYPE_ARROW = 1
ALIEN_TYPE_THICCBOI = 2
ALIEN_TYPE_N = 3

ALIENS_N = 16
aliens = []

def aliens_init():
    global aliens, ALIENS_N, canvas
    for i in range(ALIENS_N):
        alien = {
          "used": False,
          "picture": canvas.create_image(0, 0, image=sprites["alien"][0], anchor=tk.NW),
        }
        canvas.itemconfigure(alien["picture"], state=tk.HIDDEN)
        aliens.append(alien)

def aliens_update():
    global frames, aliens, score, canvas, ALIENS_N, DISP_W, DISP_H, ALIEN_TYPE_N, ALIEN_TYPE_BUG, ALIEN_TYPE_ARROW, ALIEN_TYPE_THICCBOI, ALIEN_W, ALIEN_H

    new_quota = 0 if (frames % 120) > 0 else random.randint(2, 4)
    new_x = random.randint(20, DISP_W-100)

    for i in range(ALIENS_N):
        alien = aliens[i]
        if not alien["used"]:
            # if this alien is unused, should it spawn?
            if new_quota > 0:
                new_x = new_x + random.randint(80, 160)
                if new_x > (DISP_W - 120):
                    new_x = new_x - (DISP_W - 120)

                alien["x"] = new_x

                alien["y"] = random.randint(-80, -60)
                alien["type"] = random.randrange(ALIEN_TYPE_N)
                alien["shot_timer"] = random.randint(1, 99)
                alien["blink"] = 0
                alien["used"] = True
                canvas.itemconfigure(alien["picture"], state=tk.NORMAL)

                if alien["type"] == ALIEN_TYPE_BUG:
                    alien["life"] = 4
                elif alien["type"] == ALIEN_TYPE_ARROW:
                    alien["life"] = 2
                elif alien["type"] == ALIEN_TYPE_THICCBOI:
                    alien["life"] = 12

                new_quota = new_quota - 1
              
            continue

        if alien["type"] == ALIEN_TYPE_BUG:
            if (frames % 2) > 0:
                alien["y"] = alien["y"] + 2

        elif alien["type"] == ALIEN_TYPE_ARROW:
            alien["y"] = alien["y"] + 2

        elif alien["type"] == ALIEN_TYPE_THICCBOI:
            if (frames % 4) == 0:
              alien["y"] = alien["y"] + 2

        if alien["y"] >= DISP_H:
            alien["used"] = False
            canvas.itemconfigure(alien["picture"], state=tk.HIDDEN)
            continue

        if alien["blink"] > 0:
          alien["blink"] = alien["blink"] - 1
            

        if shots_collide(False, alien["x"], alien["y"], ALIEN_W[alien["type"]], ALIEN_H[alien["type"]]):
            alien["life"] = alien["life"] - 1
            alien["blink"] = 4

        cx = alien["x"] + math.floor(ALIEN_W[alien["type"]] / 2)
        cy = alien["y"] + math.floor(ALIEN_H[alien["type"]] / 2)

        if alien["life"] <= 0:
            fx_add(False, cx, cy)

            if alien["type"] == ALIEN_TYPE_BUG:
                score = score + 200
            elif alien["type"] == ALIEN_TYPE_ARROW:
                score = score + 150
            elif alien["type"] == ALIEN_TYPE_THICCBOI:
                score = score + 800
                fx_add(False, cx-20, cy-8)
                fx_add(False, cx+8, cy+20)
                fx_add(False, cx+16, cy+16)

            alien["used"] = False
            canvas.itemconfigure(alien["picture"], state=tk.HIDDEN)
            continue

        alien["shot_timer"] = alien["shot_timer"] - 1
        if alien["shot_timer"] == 0:
            if alien["type"] == ALIEN_TYPE_BUG:
                shots_add(False, False, cx, cy)
                alien["shot_timer"] = 150
            elif alien["type"] == ALIEN_TYPE_ARROW:
                shots_add(False, True, cx, alien["y"])
                alien["shot_timer"] = 80
            elif alien["type"] == ALIEN_TYPE_THICCBOI:
                shots_add(False, True, cx-10, cy)
                shots_add(False, True, cx+10, cy)
                shots_add(False, True, cx-10, cy + 16)
                shots_add(False, True, cx+10, cy + 16)
                alien["shot_timer"] = 200

def aliens_draw():
    global aliens, ALIENS_N, ALIEN_W, ALIEN_H, canvas, sprites

    for i in range(ALIENS_N):
        alien = aliens[i]
        picture = alien["picture"]
        
        if not alien["used"]:
            canvas.itemconfigure(picture, state=tk.HIDDEN)
            continue

        if alien["blink"] > 2:
            canvas.itemconfigure(picture, state=tk.HIDDEN)
            continue
        
        canvas.itemconfigure(picture, image=sprites["alien"][alien["type"]], state=tk.NORMAL)
        canvas.coords(picture, alien["x"], alien["y"])


#--- HUD ---
score_display = 0
score_display_changed = False
score_label = None

gameover_label = None
lives_pictures = []

def hud_init():
    global score_label, gameover_label, score_display, canvas, LIFE_W, LIFE_H, DISP_W, DISP_H

    x = math.floor(DISP_W / 2)
    y = math.floor(DISP_H / 2)
    gameover_label = canvas.create_text(x, y, text='G A M E  O V E R', fill="white", state=tk.HIDDEN)

    score_label = canvas.create_text(2, 2, text='{:06d}'.format(score_display), fill="white", anchor=tk.NW)
    
    spacing = LIFE_W + 2
    for i in range(3):
        picture = canvas.create_image(2 + (i * spacing), 20, image=sprites["life"], anchor=tk.NW)
        lives_pictures.append(picture)

def hud_update():
    global frames, score_display, score_display_changed, score

    if (frames % 2) > 0:
        return
    
    for i in range(5, 0, -1):
        diff = 1 << i
        if score_display <= (score - diff):
            score_display = score_display + diff
            score_display_changed = True


def hud_draw():
    global score_display_changed, score_label, score_display, ship, lives_pictures, canvas, gameover_label

    if score_display_changed:
        canvas.itemconfigure(score_label, text='{:06d}'.format(score_display))
        score_display_changed = False
    
    start_i = ship["lives"]
    if start_i < 0:
        start_i = 0
    for i in range(start_i, 3):
        canvas.itemconfigure(lives_pictures[i], state=tk.HIDDEN)

    if ship["lives"] < 0:
        canvas.itemconfigure(gameover_label, state=tk.NORMAL)


#--- stars ---
STARS_N = math.floor(BUFFER_W / 2) - 1
stars = []

def stars_init():
    global stars, STARS_N, sprites, canvas

    for i in range (STARS_N):
        star = {
            "y": random.uniform(0, DISP_H), 
            "speed": random.uniform(0.2, 2),
            "picture": canvas.create_image(-4, -4, image=sprites["star"], anchor=tk.NW),
        }
        stars.append(star)

def stars_update():
    global stars, STARS_N

    for i in range(STARS_N):
        star = stars[i]
        star["y"] = star["y"] + star["speed"]
        if star["y"] >= DISP_H:
            star["y"] = 0
            star["speed"] = random.uniform(0.2, 2)

def stars_draw():
    global stars, STARS_N, canvas

    star_x = 1.5
    for i in range(STARS_N):
        star = stars[i]
        canvas.coords(star["picture"], star_x, star["y"])
        star_x = star_x + 4

#--- game loop ---
fps = 60
fps_timeout = math.floor(1000/fps)

def game_loop():
    global frames, key, KEY_SEEN, keyrelease, KEY_RELEASED

    stars_update()
    fx_update()
    shots_update()
    ship_update()
    aliens_update()
    hud_update()

    frames = frames + 1
    current_time = time.time()
    for k, v in key.items():
        key[k] = key[k] & KEY_SEEN
        if keyrelease[k] > 0:
            if (current_time - keyrelease[k]) > .2:
                key[k] = key[k] & KEY_RELEASED
                keyrelease[k] = -1
  
    stars_draw()
    aliens_draw()
    shots_draw()
    fx_draw()
    ship_draw()
    hud_draw()
    
    canvas.after(fps_timeout, game_loop)


#--- keyboard ---

def on_close():
    global app
    app.destroy()


def on_keypressed(event):
    global key, KEY_SEEN, KEY_RELEASED, app, KEY_Escape, keyrelease
    if event.keysym_num in key:
        key[event.keysym_num] = KEY_SEEN + KEY_RELEASED
        keyrelease[event.keysym_num] = -1
    
    if event.keysym_num == KEY_Escape:
        on_close()


def on_keyreleased(event):
    global key, KEY_RELEASED
    if event.keysym_num in key:
        keyrelease[event.keysym_num] = time.time()


app = tk.Tk()
app.title("Tkinter 2d action game")
canvas = tk.Canvas(app, width=DISP_W, height=DISP_H)
canvas.configure(bg="Black")
canvas.pack()
canvas.bind("<KeyPress>", on_keypressed)
canvas.bind("<KeyRelease>", on_keyreleased)
canvas.focus_set()
canvas.after(fps_timeout, game_loop)
app.resizable(width=False, height=False)
app.protocol("WM_DELETE_WINDOW",on_close)

#--- Game Main ---
sprites_init()

stars_init()
aliens_init()
shots_init()
fx_init()
ship_init()
hud_init()

app.mainloop()

