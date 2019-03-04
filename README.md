# 1RL

[Download on itch.io!](https://pfgimenez.itch.io/1rl)

Create your first roguelike!

You have 7 days to create your roguelike by completing its features. But unstable features generate bugs that cost you time… Will you finish your game in time?

## Context

This is my first participation to a game jam, namely 7DRL 2019. So this is kind of autobiographical.

## Core mechanics

- You have no hit points but 7 days to make your game. Try not to lose too much time!
- You can control the spawn rate of the bugs by choosing how many unstable features you equip at the same time.
- Weapons and features have ego: find the combinations that work best!
- Depending on the feature that generated them, bugs have special skills. Mapgen bugs can phase, RNG bugs rarely fail their attack.

## Manual compilation (Unix)

You will need sdl2-dev package.

First, install tcod and pyinstaller:

    $ python3 -m pip install tcod
    $ python3 -m pip install pyinstaller

Then clone the repository:

    $ git clone https://github.com/PFGimenez/1rl
    $ cd 1rl

Then package it:

    $ python3 -m PyInstaller 1rl.py --additional-hooks-dir=. -F --add-data "font.png:font.png" --add-data "splash.png:splash.png"

The binary is in `dist`.

## Acknowledgement

This game is based on the [python-tcod](https://github.com/libtcod/python-tcod) library. Splash art by [Master484](http://m484games.ucoz.com/)
