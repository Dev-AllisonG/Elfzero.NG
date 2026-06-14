import pyautogui as pg
import time
import keyboard

REGION_BATTLE = (1745, 487, 160, 51)
REGION_LOOT = (767,366,211,214)

POSITION_MANA_FULL = (878, 32)
COLOR_MANA = (0, 63, 140)

POSITION_LIFE = (17, 35)
COLOR_GREEN_LIFE = (100, 145, 4)

def check_battle():
    return pg.locateOnScreen('./imgs/region_battle.png', region=REGION_BATTLE)

while True:
    is_battle = check_battle()

    if is_battle == None:
        print("Deu certo")
        pg.press('space')

        while pg.locateOnScreen(
            './imgs/red_target.png',
            confidence=0.7,
            region=REGION_BATTLE
        ) != None:
            print("esperando o monstro morrer!")
            print("procurando outro monstro")

    print(is_battle)

def get_loot():
    loot = pg.locateAllOnScreen(
        './imgs/monsterdead.png',
        confidence=0.9,
        region=REGION_LOOT
    )

    for box in loot:
        x, y = pg.center(box)
        pg.moveTo(x, y)
        pg.click(button='right')

    print('loot>>>>', loot)

def check_status(name, delay, x, y, rgb, button_name):
    print(f'checando {name}...')
    time.sleep(delay)

    if pg.pixelMatchesColor(x, y, rgb):
        pg.press(button_name)

keyboard.wait('h')
check_status('mana', 5, 878, 32, (0, 63, 140), 'F3')

keyboard.wait('h')
check_status('life', 1, *POSITION_LIFE, COLOR_GREEN_LIFE, 'F5')
