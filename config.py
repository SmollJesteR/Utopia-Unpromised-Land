import random

WIN_WIDTH = 1920
WIN_HEIGHT = 1080
TILESIZE = 60
FPS = 60

ENEMY_LAYER = 1
PLAYER_LAYER = 3
BLOCK_LAYER = 2
GROUND_LAYER =  1
PLAYER_SPEED = 9

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
    'B......E.....W.............D..........T..........................D....W..WWWWWWWWWWWWWWWWWWWW..B',
    'B............W........................................................W.........................B',
    'B......E.....WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW..W..WWWWWWWWWWWWWWWWWWW..B',
    'B....................E...........E...................E...............W..W......................W.B',
    'B..WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW..W..W..TTT.....D...........B',
    'B..W...........................................................E....W..W........................B',
    'B..W..TTT.....D.....E..T...E....D.....TTT........D......T...........W..WWWWWWWWWWWWWWWWWWWWWW..B',
    'B..W........................................T.......E..........T..E.W............................B',
    'B..W.............T.............D....P............D.......D...........WWWWWWWWWWWWWWWWWWWWWWWW..B',
    'B..W.....T..............E.................T..................T.......W.......................E..B',
    'B..W.............D..........T..........E..........E....D...E..........W..TTT.....D..............B',
    'B..W....E.......................E...........E...................................................B',
    'B...WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW....W..WWWWWWWWWWWWWWWWWWWWW..B',
    'B.......................E.......E......E.......E.....................W..........................B',
    'B...WWWWWWWWWWWWWWWWWW....WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW.....TTT.....D...........B',
    'B..W............................................................................................B',
    'B..W..TTT.....D........T........D.....TTT........D......T...........W..WWWWWWWWWWWWWWWWWWWWWW..B',
    'B..W........................................T..................T....W..W......................W.B',
    'B..W........W....WWWWW.........D.................D.......D........W..W..TTT.....D..............B',
    'B..W.....T..W....W...WWWWWWWW.............T..................T....W..W..........................B',
    'B..W........WWWWWW...W......W......E...................D...........W..WWWWWWWWWWWWWWWWWWWWWWWW..B',
    'B..W...............................................................W.............................B',
    'B...WWWWWWWWWWWWWWWWWW.WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW..W..WWWWWWWWWWWWWWWWWWWWW..B',
    'B....................................................................W..W.......................B',
    'B...WWWWWWWWWWWWWWWW...WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW....WWWWWWWW..W..TTT.....D........E..B',
    'B..W...............................................................E..W.........................B',
    'B..W..TTT.....D........T........D.....TTT........D......T...E.........W..WWWWWWWWWWWWWWWWWWWWWW..B',
    'B..W........................................T.............Y...T....W..W......................W.B',
    'B................T.............D.................D.......X.........W..W..TTT.....D..............B',
    'B........T................................T...............ZZZZZ..T....W..W..........................B',
    'B..W.............D..........T..........................D...........W..WWWWWWWWWWWWWWWWWWWWWWWW..B',
    'B..W...............................................................W.............................B',
    'B..WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW..B',
    'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'
]