import pyautogui as pg
from PIL import Image
import numpy as np
import time
import keyboard
import threading
import os

# ===================== CONFIGURAÇÕES =====================

# Battle list / ataque
REGION_BATTLE = (1745, 487, 160, 51)

VERMELHO_MIN = np.array([150, 0, 0])
VERMELHO_MAX = np.array([255, 80, 80])
LIMIAR_DIFF = 500
CAMINHO_BASE = "imgs/base_vazio.png"

# Loot
REGION_LOOT = (767, 366, 211, 214)

# Status (vida/mana) - posição de um pixel + cor esperada
POSITION_MANA = (878, 32)
COLOR_MANA = (0, 63, 140)
POSITION_LIFE = (17, 35)
COLOR_GREEN_LIFE = (100, 145, 4)

# Intervalos entre checagens (segundos)
INTERVALO_ATAQUE = 0.3
INTERVALO_LOOT = 1.0
INTERVALO_STATUS = 1.0

running = False

# ===================== AJUSTE DE OPACIDADE (OPCIONAL) =====================

try:
    print("Tentando ajustar a opacidade da janela...")
    import window
except (IndexError, ImportError):
    print("Aviso: Não foi possível aplicar a opacidade. A janela do Tibia está aberta com o título correto?")

# ===================== CARREGAR IMAGEM BASE =====================

if not os.path.exists(CAMINHO_BASE):
    print(f"ERRO: imagem base não encontrada em '{CAMINHO_BASE}'.")
    print("Rode primeiro o script 'capturar_base.py' com a battle list VAZIA.")
    IMG_BASE = None
else:
    IMG_BASE = np.array(Image.open(CAMINHO_BASE).convert('RGB'), dtype=int)

# ===================== ATAQUE =====================

def tem_mob():
    """Compara a battle list atual com a base vazia. Diferença grande = tem mob."""
    if IMG_BASE is None:
        return False
    img_atual = np.array(pg.screenshot(region=REGION_BATTLE).convert('RGB'), dtype=int)
    diff = np.abs(img_atual - IMG_BASE).sum()
    return diff > LIMIAR_DIFF

def esta_atacando():
    """Verifica se existe algum pixel vermelho (indicador de alvo selecionado)."""
    img = np.array(pg.screenshot(region=REGION_BATTLE).convert('RGB'))
    mask = (
        (img[:, :, 0] >= VERMELHO_MIN[0]) & (img[:, :, 0] <= VERMELHO_MAX[0]) &
        (img[:, :, 1] >= VERMELHO_MIN[1]) & (img[:, :, 1] <= VERMELHO_MAX[1]) &
        (img[:, :, 2] >= VERMELHO_MIN[2]) & (img[:, :, 2] <= VERMELHO_MAX[2])
    )
    return mask.any()

def attack_loop():
    global running
    print("Ataque automático ATIVADO")

    while running:
        if esta_atacando():
            print("Atacando, esperando o monstro morrer...")
        elif tem_mob():
            pg.press('space')
            print(">> Mob detectado, atacando...")
        else:
            print(">> Sem mob na battle list.")

        time.sleep(INTERVALO_ATAQUE)

    print("Ataque automático DESATIVADO")

# ===================== LOOT =====================

def loot_loop():
    global running
    print("Loot automático ATIVADO")

    while running:
        try:
            loot = pg.locateAllOnScreen(
                './imgs/monsterdead.png',
                confidence=0.9,
                region=REGION_LOOT
            )
            for box in loot:
                x, y = pg.center(box)
                pg.moveTo(x, y)
                pg.click(button='right')
                print(">> Loot coletado")
        except pg.ImageNotFoundException:
            pass

        time.sleep(INTERVALO_LOOT)

    print("Loot automático DESATIVADO")

# ===================== STATUS (VIDA/MANA) =====================

def status_loop():
    global running
    print("Checagem de vida/mana ATIVADA")

    while running:
        if pg.pixelMatchesColor(*POSITION_MANA, COLOR_MANA):
            pg.press('F3')
            print(">> Mana baixa, usando F3")

        if pg.pixelMatchesColor(*POSITION_LIFE, COLOR_GREEN_LIFE):
            pg.press('F5')
            print(">> Vida baixa, usando F5")

        time.sleep(INTERVALO_STATUS)

    print("Checagem de vida/mana DESATIVADA")

# ===================== CONTROLE (HOTKEYS) =====================

def start_attack():
    global running
    if not running:
        if IMG_BASE is None:
            print("Não é possível iniciar: imagem base não encontrada (veja o erro acima).")
            return
        running = True
        threading.Thread(target=attack_loop, daemon=True).start()
        threading.Thread(target=loot_loop, daemon=True).start()
        threading.Thread(target=status_loop, daemon=True).start()

def stop_attack():
    global running
    running = False

keyboard.add_hotkey('h', start_attack)
keyboard.add_hotkey('j', stop_attack)

print("Pressione H para iniciar (ataque + loot + vida/mana), J para parar.")
keyboard.wait()
