# tkinter_2d_action_game

This is the python tkinter version of the [Proof of Concept for a Gtk4 2D action game written in c](https://github.com/lavalfils/poc_gtk4_2D_action_game) using the tkinter canvas widget.

## How to play

* Arrow keys to move ship
* Space bar to shoot

![Screenshot](screenshot.png)

## Issues

* No sound fx
* No tint effects when alien ships get hit. (Could created tinted sprite versions and swap them to create the tint effect)

## Solved issues

* No longer use the fix os.system('xset r off') to bypass the key repeat problem on linux.

## Requirements

* Latest Python 3 and tkinter. Also works on Windows with latest python3 installed.

## run
```
python3 game.py
```
