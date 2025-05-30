import random

WIN_WIDTH = 1920
WIN_HEIGHT = 1080
TILESIZE = 60
FPS = 60

ENEMY_LAYER = 1
PLAYER_LAYER = 3
BLOCK_LAYER = 2
GROUND_LAYER =  1
PLAYER_SPEED = 2.5

RED = (255, 0, 0)
BLACK = (0, 0, 0)
CYAN = (0, 255, 255)

tilemap = [
    'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB',
    'B............WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW........B',
    'B............W..........................................................W.......................B',
    'B............W..TTT.....D........T........D.....TTT........D......T.....W..WWWWWWWWWWWWWWWWWW..B',
    'B............W..T.....................T..................T..............W......................W.B',
    'B............W..D.............T.............D.................D.......W..TTTTT.....D...........B',
    'B............W.....T................................T..................W.............T..........B',
    'B............W.............D..........T..........................D....W..WWWWWWWWWWWWWWWWWWWW..B',
    'B............W........................................................W.........................B',
    'B............WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW..W..WWWWWWWWWWWWWWWWWWW..B',
    'B....................................................................W..W......................W.B',
    'B..WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW..W..W..TTT.....D...........B',
    'B..W................................................................W..W........................B',
    'B..W..TTT.....D........T........D.....TTT........D......T...........W..WWWWWWWWWWWWWWWWWWWWWW..B',
    'B..W........................................T..................T....W............................B',
    'B..W.............T.............D.................D.......D........W..WWWWWWWWWWWWWWWWWWWWWWWW..B',
    'B..W.....T................................T..................T....W..W.......................E..B',
    'B..W.............D..........T..........................D...........W..W..TTT.....D..............B',
    'B..W...............................................................W..W.........................B',
    'B..WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW..W..WWWWWWWWWWWWWWWWWWWWW..B',
    'B....................................................................W..........................B',
    'B..WWWWWWWWWWWWWWWWWWW.WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW..W..TTT.....D...........B',
    'B..W...............................................................E..W.........................B',
    'B..W..TTT.....D........T........D.....TTT........D......T...........W..WWWWWWWWWWWWWWWWWWWWWW..B',
    'B..W........................................T..................T....W..W......................W.B',
    'B..W........W....WWWWW.........D.................D.......D........W..W..TTT.....D..............B',
    'B..W.....T..W....W...WWWWWWWW.............T..................T....W..W..........................B',
    'B..W........WWWWWW...W......W..........................D...........W..WWWWWWWWWWWWWWWWWWWWWWWW..B',
    'B..W...............................................................W.............................B',
    'B..WWWWWWWWWWWWWWWWWWW.WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW..W..WWWWWWWWWWWWWWWWWWWWW..B',
    'B....................................................................W..W.......................B',
    'B..WWWWWWWWWWWWWWWWW...WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW....WWWWWWWW..W..TTT.....D........E..B',
    'B..W...............................................................E..W.........................B',
    'B..W..TTT.....D........T........D.....TTT........D......T...EEEEE.....W..WWWWWWWWWWWWWWWWWWWWWW..B',
    'B..W........................................T.............Y...T....W..W......................W.B',
    'B..W.............T.............D.................D.......X....P....W..W..TTT.....D..............B',
    'B..W.....T................................T...............ZZZZZ..T....W..W..........................B',
    'B..W.............D..........T..........................D...........W..WWWWWWWWWWWWWWWWWWWWWWWW..B',
    'B..W...............................................................W.............................B',
    'B..WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW..B',
    'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'
]

# Tambahkan 5 musuh tambahan untuk memenuhi 20
tilemap[3] = 'B............W..TTT.....D........T........D.....TTT........D......T.....W..WWWWWWWWWWWWWWWWWW..B'
tilemap[11] = 'B..WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW..W..W..TTT.....D........E..B'
tilemap[21] = 'B..WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW..W..TTT.....D...........B'
tilemap[31] = 'B..WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW..W..TTT.....D........E..B'
tilemap[35] = 'B..W.............T.............D.................D.......D....P....W..W..TTT.....D..............B'

