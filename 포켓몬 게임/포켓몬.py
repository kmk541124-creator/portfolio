import requests
import pygame
from io import BytesIO
import random
import math
import os
pygame.init()
WIDTH, HEIGHT = 1000, 680
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("포켓몬 게임")
clock = pygame.time.Clock()

def load_font(size):
    return pygame.font.Font("/System/Library/Fonts/AppleSDGothicNeo.ttc", size)

F32 = load_font(32)
F24 = load_font(24)
F18 = load_font(18)
F14 = load_font(14)
F12 = load_font(12)

SAVE_FILE = "savegame.json"

BG = (132, 180, 228)
PANEL = (255, 255, 255)
PANEL2 = (210, 230, 248)
BORDER = (32, 48, 120)
ACCENT = (220, 30, 30)
WHITE = (255, 255, 255)
GRAY = (140, 140, 160)
DARK_GRAY = (60, 60, 80)
BLACK = (0,0,0)

name_cache = {}
img_cache = {}
SPRITE_URL = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{}.png"
TOTAL = 1025
COL = 5
CARD_W, CARD_H = 180, 180
book_scroll = 0

def txt(surface, text, font, color, x, y, center=False, right=False):
    s = font.render(str(text), True, color)
    r = s.get_rect()
    if center: r.center = (x, y)
    elif right: r.right = x; r.top = y
    else: r.topleft = (x, y)
    surface.blit(s, r)
    return r

def panel(surface, x, y, w, h, color=None, alpha=255, radius=10, border=None):
    color = color or PANEL
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(s, (*color, alpha), (0, 0, w, h), border_radius=radius)
    surface.blit(s, (x, y))
    if border:
        pygame.draw.rect(surface, border, (x, y, w, h), 2, border_radius=radius)

def btn(surface, rect, label, font, active=True, hover=False):
    bc = PANEL2 if not active else ((50, 90, 180) if not hover else (70, 120, 220))
    fc = GRAY if not active else WHITE
    panel(surface, rect.x, rect.y, rect.w, rect.h, bc, alpha=230, radius=8, border=ACCENT if active else DARK_GRAY)
    txt(surface, label, font, fc, rect.centerx, rect.centery, center=True)
    
def get_img_2x(pid):
    try:
        data = requests.get(SPRITE_URL.format(pid), timeout=3).content
        img = pygame.image.load(BytesIO(data)).convert_alpha()
        img = pygame.transform.scale_by(img, 2)
        return img
    except:
        return None

def get_korean_name(pid):
    if pid in name_cache:
        return name_cache[pid]
    try:
        res = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{pid}", timeout=3)
        for n in res.json()["names"]:
            if n["language"]["name"] == "ko":
                name_cache[pid] = n["name"]
                return name_cache[pid]
    except:
        pass
    name_cache[pid] = str(pid)
    return name_cache[pid]

def get_desc(pid):
    res = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{pid}")
    for e in res.json()["flavor_text_entries"]:
        if e["language"]["name"] == "ko":
            return e["flavor_text"]
        elif e["language"]["name"] == "en":
            return e["flavor_text"]


class Game:
    def __init__(self):
        self.scene = "title"
        self.t = 0
        self.notification = None
        self.notif_timer = 0

    def start(self):
        self.starting = ""
        self.poket = []
        self.scene = "first"
        self.view = None

g = Game()

def draw_title():
    screen.fill(BG)
    g.t += 1
    t = g.t
    random.seed(42)
    for _ in range(80):
        sx = random.randint(0, WIDTH)
        sy = random.randint(0, HEIGHT)
        alpha = int(100 + 80 * math.sin(t * 0.02 + sx))
        r = random.randint(1, 2)
        s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (200, 210, 255, alpha), (r, r), r)
        screen.blit(s, (sx - r, sy - r))
    for i in range(3):
        a = int(40 + 20 * math.sin(t * 0.015 + i))
        pygame.draw.line(screen, (*ACCENT, a), (0, 150 + i * 2), (WIDTH, 150 + i * 2), 1)
    txt(screen, "포켓몬스터 게임", F32, ACCENT, WIDTH // 2, 120, center=True)
    txt(screen, "포켓몬 마스터가 되어라", F18, GRAY, WIDTH // 2, 165, center=True)
    panel(screen, WIDTH // 2 - 90, 200, 180, 180, PANEL2, alpha=200, radius=16, border=BORDER)
    txt(screen, "< 나 >", F14, GRAY, WIDTH // 2, 310, center=True)
    txt(screen, "포켓몬", F14, DARK_GRAY, WIDTH // 2, 340, center=True)
    txt(screen, "포켓몬스터?", F14, GRAY, WIDTH // 2, 360, center=True)
    mx, my = pygame.mouse.get_pos()
    btn_start = pygame.Rect(WIDTH // 2 - 100, 415, 200, 48)
    btn_load = pygame.Rect(WIDTH // 2 - 100, 473, 200, 48)
    btn_quit = pygame.Rect(WIDTH // 2 - 100, 531, 200, 48)
    btn(screen, btn_start, "새 게임", F18, hover=btn_start.collidepoint(mx, my))
    has_save = os.path.exists(SAVE_FILE)
    btn(screen, btn_load, "이어하기", F18, active=has_save, hover=has_save and btn_load.collidepoint(mx, my))
    btn(screen, btn_quit, "종료", F18, hover=btn_quit.collidepoint(mx, my))
    txt(screen, "포켓몬 마스터가 되세요", F12, DARK_GRAY, WIDTH // 2, 593, center=True)
    return btn_start, btn_load, btn_quit

_fist_img = None
_pokeball = None
_fire_img = None
_water_img = None
_wrong_img = None

def draw_fist(cy, mx, my):
    global _fist_img, _pokeball, _fire_img, _water_img, _wrong_img
    if _fist_img is None:
        _fist_img = pygame.image.load('images/fivedoctor.jpeg')
    if _pokeball is None:
        _pokeball = pygame.image.load('images/poketball.webp')
    if _fire_img is None:
        _fire_img = get_img_2x(4)
    if _water_img is None:
        _water_img = get_img_2x(7)
    if _wrong_img is None:
        _wrong_img = get_img_2x(1)

    elapsed = pygame.time.get_ticks() - scene_start
    screen.fill(WHITE)
    finish = elapsed > 7000

    if elapsed > 6000:
        progress = min(1.0, (elapsed - 6000) / 1000)
        ease = progress * progress
        img_x = int(WIDTH // 2 - 300 * ease)
    else:
        img_x = WIDTH // 2

    img_rect = _fist_img.get_rect(center=(img_x, HEIGHT // 2 - 80))
    screen.blit(_fist_img, img_rect)

    if finish:
        for pid, img, cx in [
            (4, _fire_img, 300),
            (7, _water_img, 500),
            (1, _wrong_img, 700),
        ]:
            ball_rect = _pokeball.get_rect(center=(cx, HEIGHT // 2 + 20))
            hovered = ball_rect.collidepoint(mx, my)
            if hovered:
                show = img
            else:
                show = _pokeball
            r = show.get_rect(center=(cx, HEIGHT // 2 + 20))
            screen.blit(show, r)    
                

    if elapsed < 3000:
        msg = "포켓몬 세상에 어서오렴!"
        font = F24
    elif elapsed < 6000:
        msg = "너는 포켓몬도 없는 그지새끼구나 밖은 ㅈㄴ게 위험하니 얘네들을 데리고 가렴"
        font = F18
    else:
        msg = "빨리 고르고 꺼지렴"
        font = F24

    ts = font.render(msg, True, BLACK)
    tw, th = ts.get_size()
    bx = img_x - tw // 2 - 20
    by = img_rect.bottom + 20
    bw = tw + 40
    bh = th + 24
    pygame.draw.rect(screen, WHITE, (bx, by, bw, bh), border_radius=10)
    pygame.draw.rect(screen, BORDER, (bx, by, bw, bh), 2, border_radius=10)
    pygame.draw.polygon(screen, WHITE, [
        (img_x - 10, by),
        (img_x + 10, by),
        (img_x, by - 15)
    ])
    pygame.draw.lines(screen, BORDER, False, [
        (img_x - 10, by),
        (img_x, by - 15),
        (img_x + 10, by)
    ], 2)
    screen.blit(ts, (bx + 20, by + 12))

def draw_main_bg():
    # 하늘
    screen.fill((120, 192, 240))

    # 구름
    for cx, cy in [(150, 60), (400, 40), (700, 70), (900, 50)]:
        pygame.draw.rect(screen, WHITE, (cx - 40, cy, 80, 20))
        pygame.draw.rect(screen, WHITE, (cx - 56, cy + 8, 112, 20))
        pygame.draw.rect(screen, WHITE, (cx - 24, cy - 12, 48, 16))

    # 태양
    pygame.draw.rect(screen, (255, 224, 32), (880, 30, 56, 56))
    pygame.draw.rect(screen, (255, 224, 32), (872, 42, 72, 32))

    # 잔디 레이어
    pygame.draw.rect(screen, (120, 200, 64), (0, 340, WIDTH, HEIGHT))
    pygame.draw.rect(screen, (96, 168, 48), (0, 360, WIDTH, HEIGHT))
    pygame.draw.rect(screen, (80, 144, 40), (0, 380, WIDTH, HEIGHT))

    # 풀숲 (어두운 잔디 타일)
    for gx in range(0, 380, 32):
        pygame.draw.rect(screen, (64, 128, 32), (gx, 340, 16, 16))
    for gx in range(420, WIDTH, 32):
        pygame.draw.rect(screen, (64, 128, 32), (gx, 340, 16, 16))

    # 꽃
    for fx, fy, fc in [(100, 350, (255, 80, 80)), (180, 370, (255, 200, 80)),
                        (560, 355, (255, 80, 80)), (640, 375, (255, 200, 80)),
                        (780, 360, (200, 80, 255)), (850, 380, (255, 80, 80))]:
        pygame.draw.rect(screen, fc, (fx, fy, 8, 8))
        pygame.draw.rect(screen, (80, 160, 48), (fx + 2, fy + 6, 4, 8))

    # 경로
    pygame.draw.rect(screen, (208, 184, 120), (380, 340, 200, HEIGHT))
    pygame.draw.rect(screen, (184, 160, 96), (388, 340, 8, HEIGHT))
    pygame.draw.rect(screen, (184, 160, 96), (572, 340, 8, HEIGHT))

    # 나무 (1세대 스타일 - 동그란 상단)
    for tx in [40, 160, 680, 820, 950]:
        # 기둥
        pygame.draw.rect(screen, (112, 72, 40), (tx + 8, 270, 16, 80))
        # 잎 (3단)
        pygame.draw.rect(screen, (32, 96, 24), (tx - 16, 230, 64, 52))
        pygame.draw.rect(screen, (48, 128, 32), (tx - 8, 208, 48, 32))
        pygame.draw.rect(screen, (72, 160, 48), (tx, 192, 32, 24))
        # 하이라이트
        pygame.draw.rect(screen, (96, 192, 64), (tx + 4, 196, 12, 8))

    # 건물 (포켓몬 센터 느낌)
    pygame.draw.rect(screen, (248, 240, 216), (420, 180, 200, 168))
    # 지붕
    pygame.draw.rect(screen, (216, 64, 64), (412, 164, 216, 24))
    pygame.draw.rect(screen, (240, 80, 80), (420, 156, 200, 16))
    # 지붕 테두리
    pygame.draw.rect(screen, (160, 48, 48), (412, 180, 216, 4))
    # 문
    pygame.draw.rect(screen, (168, 216, 248), (488, 280, 64, 68))
    pygame.draw.rect(screen, (136, 184, 216), (488, 280, 32, 68))
    # 창문
    pygame.draw.rect(screen, (168, 216, 248), (432, 210, 48, 36))
    pygame.draw.rect(screen, (136, 184, 216), (432, 210, 24, 36))
    pygame.draw.rect(screen, (168, 216, 248), (556, 210, 48, 36))
    pygame.draw.rect(screen, (136, 184, 216), (556, 210, 24, 36))
    # 건물 이름
    pygame.draw.rect(screen, (240, 80, 80), (444, 248, 152, 20))

    # 표지판
    pygame.draw.rect(screen, (112, 72, 40), (310, 280, 8, 64))
    pygame.draw.rect(screen, (248, 232, 160), (286, 252, 56, 32))
    pygame.draw.rect(screen, (200, 160, 80), (286, 252, 56, 32), 2)

    # 울타리
    for fx in range(620, 860, 32):
        pygame.draw.rect(screen, (216, 192, 144), (fx, 330, 8, 24))
        pygame.draw.rect(screen, (216, 192, 144), (fx, 316, 32, 8))

    # 연못
    pygame.draw.rect(screen, (96, 168, 232), (80, 390, 120, 64))
    pygame.draw.rect(screen, (120, 192, 248), (88, 398, 104, 12))
    pygame.draw.rect(screen, (64, 128, 48), (76, 386, 128, 8))

    # 하단 풀 디테일
    for gx in range(0, WIDTH, 16):
        if gx < 376 or gx > 584:
            h = random.randint(4, 10)
            pygame.draw.rect(screen, (80, 144, 40), (gx + 4, 340 - h, 4, h))
    
def draw_main(cy, mx, my):
    draw_main_bg()


def draw_choice(cname, desc, cy, mx, my):
    screen.fill(BG)
    panel(screen, WIDTH // 2 - 300, HEIGHT // 2 - 180, 600, 360, PANEL2, alpha=235, radius=16, border=True)
    txt(screen, f"{cname}으로 선택하시겠습니까?", F18, BLACK, WIDTH // 2, HEIGHT // 2 - 148, center=True)
    pygame.draw.line(screen, BORDER, (WIDTH // 2 - 270, HEIGHT // 2 - 122), (WIDTH // 2 + 270, HEIGHT // 2 - 122), 1)
    if desc:
        for i, line in enumerate(desc.split("\n")):
            txt(screen, line, F14, BLACK, WIDTH // 2, HEIGHT // 2 - 95 + i * 26, center=True)
    mx, my = pygame.mouse.get_pos()

    ok_r = pygame.Rect(WIDTH // 2 - 160, HEIGHT // 2 + 120, 140, 40)
    no_r = pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2 + 120, 140, 40)
    btn(screen, ok_r, "선택하기", F14, hover=ok_r.collidepoint(mx, my))
    btn(screen, no_r, "조금 더 고민하기", F14, hover=no_r.collidepoint(mx, my))
    return ok_r, no_r


def draw_book(cy):
    panel(screen, 10, cy, WIDTH - 20, HEIGHT - cy - 62, PANEL, alpha=180, radius=10, border=BORDER)
    txt(screen, "도감", F18, ACCENT, WIDTH // 2, cy + 18, center=True)

    content_y = cy + 50
    panel_bottom = HEIGHT - 62
    screen.set_clip(pygame.Rect(10, content_y, WIDTH - 20, panel_bottom - content_y))

    for pid in range(1, TOTAL + 1):
        col = (pid - 1) % COL
        row = (pid - 1) // COL
        x = 20 + col * (CARD_W + 10)
        y = content_y + row * (CARD_H + 10) - book_scroll

        if y + CARD_H < content_y or y > panel_bottom:
            continue

        panel(screen, x, y, CARD_W, CARD_H, (40, 60, 100), alpha=220, radius=10, border=BORDER)
        txt(screen, f"#{pid}", F12, GRAY, x + 10, y + 8)

        img = get_img_2x(pid)
        if img:
            screen.blit(img, (x + CARD_W // 2 - 48, y + 20))

        name = get_korean_name(pid)
        txt(screen, name, F12, WHITE, x + CARD_W // 2, y + CARD_H - 25, center=True)

    screen.set_clip(None)

choice = None
running = True
while running:
    mx, my = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEWHEEL:
            if(g.scene == "book"):
                book_scroll = max(0, book_scroll - event.y * 30)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if g.scene == "title":
                bs, bl, bq = draw_title()
                if bs.collidepoint(mx, my):
                    g.start()
                    scene_start = pygame.time.get_ticks()
            elif g.scene == "first":
                for pid, cx in [(4, 300), (7, 500), (1, 700)]:
                    ball_rect = _pokeball.get_rect(center=(cx, HEIGHT // 2 + 20))
                    if ball_rect.collidepoint(mx, my):
                        g.poket = pid
                        print(pid)
                        g.scene = "choice"
            elif g.scene == "choice":
                ok_r, no_r = draw_choice(get_korean_name(g.poket), get_desc(g.poket), 108, mx, my)
                if ok_r.collidepoint(mx, my):
                    g.scene = "main" 
                if no_r.collidepoint(mx, my):
                    g.scene = "first"
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if g.scene == "choice":
                g.scene = "first"
    if g.scene == "title":
        draw_title()
    elif g.scene == "first":
        draw_fist(108, mx, my)
    elif g.scene == "choice":
        draw_choice(get_korean_name(g.poket), get_desc(g.poket) , 108, mx, my)
    elif g.scene == "main":
        draw_main(108,mx,my)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()