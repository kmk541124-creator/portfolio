import requests
import pygame
import threading
from io import BytesIO
import random
import math
import os
import json
import copy

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
GREEN = (60, 200, 120)
WHITE = (255, 255, 255)
GRAY = (140, 140, 160)
DARK_GRAY = (60, 60, 80)
GOLD = (255, 215, 0)
BLACK = (0, 0, 0)

BASE = "https://pokeapi.co/api/v2"

TYPE_COLORS = {
    "노말": (168, 168, 120), "불꽃": (240, 128, 48), "물": (104, 144, 240),
    "풀": (120, 200, 80), "전기": (248, 208, 48), "얼음": (152, 216, 216),
    "격투": (192, 48, 40), "독": (160, 64, 160), "땅": (224, 192, 104),
    "비행": (168, 144, 240), "에스퍼": (248, 88, 136), "벌레": (168, 184, 32),
    "바위": (184, 160, 56), "고스트": (112, 88, 152), "드래곤": (112, 56, 248),
    "악": (112, 88, 72), "강철": (184, 184, 208), "페어리": (238, 153, 172),
}

MAP_NODES = {
    "태초마을": {"conn": ["1번도로", "21번도로"], "type": "town"},
    "1번도로": {"conn": ["태초마을", "회색시티"], "type": "route"},
    "회색시티": {"conn": ["1번도로", "2번도로"], "type": "city"},
    "2번도로": {"conn": ["회색시티", "황토마을"], "type": "route"},
    "황토마을": {"conn": ["2번도로", "3번도로"], "type": "city"},
    "3번도로": {"conn": ["황토마을", "홍련마을"], "type": "route"},
    "홍련마을": {"conn": ["3번도로", "4번도로", "9번도로", "24번도로"], "type": "city"},
    "24번도로": {"conn": ["홍련마을"], "type": "route"},
    "4번도로": {"conn": ["홍련마을", "연분홍시티"], "type": "route"},
    "9번도로": {"conn": ["홍련마을", "라벤더마을"], "type": "route"},
    "연분홍시티": {"conn": ["4번도로", "5번도로", "6번도로"], "type": "city"},
    "5번도로": {"conn": ["연분홍시티", "셀라돈시티"], "type": "route"},
    "셀라돈시티": {"conn": ["5번도로", "16번도로"], "type": "city"},
    "6번도로": {"conn": ["연분홍시티", "주홍시티"], "type": "route"},
    "주홍시티": {"conn": ["6번도로", "11번도로"], "type": "city"},
    "11번도로": {"conn": ["주홍시티", "라벤더마을"], "type": "route"},
    "라벤더마을": {"conn": ["9번도로", "11번도로", "12번도로"], "type": "town"},
    "12번도로": {"conn": ["라벤더마을", "진홍시티"], "type": "route"},
    "16번도로": {"conn": ["셀라돈시티", "진홍시티"], "type": "route"},
    "진홍시티": {"conn": ["16번도로", "12번도로", "19번도로"], "type": "city"},
    "19번도로": {"conn": ["진홍시티", "21번도로"], "type": "route"},
    "21번도로": {"conn": ["19번도로", "태초마을"], "type": "route"},
}

NODE_POS = {
    "태초마을": (152, 856),
    "1번도로": (152, 756),
    "회색시티": (152, 572),
    "2번도로": (152, 388),
    "황토마을": (152, 180),
    "3번도로": (336, 180),
    "홍련마을": (490, 180),
    "24번도로": (490, 296),
    "4번도로": (602, 180),
    "9번도로": (638, 276),
    "연분홍시티": (490, 492),
    "5번도로": (362, 492),
    "셀라돈시티": (234, 492),
    "6번도로": (490, 636),
    "주홍시티": (596, 716),
    "11번도로": (632, 572),
    "라벤더마을": (724, 360),
    "12번도로": (666, 668),
    "16번도로": (234, 644),
    "진홍시티": (334, 756),
    "19번도로": (234, 848),
    "21번도로": (152, 892),
}

GYM_INIT = {
    "회색체육관": {"location": "회색시티", "leader": "웅", "cleared": False}
}

TRY_INIT = {
    "웅": {
        "pid": {
            74: {"lv": 12, "moves": ["tackle", "defense-curl", "rock-throw"]},
            95: {"lv": 14, "moves": ["tackle", "bind", "rock-throw", "screech"]},
        }
    }
}

GYM = copy.deepcopy(GYM_INIT)
TRY = copy.deepcopy(TRY_INIT)

ROUTE_POKEMON = {
    "1번도로": [16, 19],
}
item_li = []
ROUTE_TRAINER = {
    "1번도로": [],
    "2번도로": [],
}

ITEM_LIST = {
    "몬스터볼":{"money":1000, "desc":"야생 포켓몬에게 던져서 잡기 위한 볼. 캡슐식으로 되어 있다.", "use":False},
    "이상한 사탕":{"money":1000, "desc":"이상한 사탕이자 희귀한 사탕(영문판은 rare candy다 엄연히 오역이다) 포켓몬의 레벨 1올려준다", "use":True, "type":"level_up", "eff":1}
}

name_cache = {}
img_cache = {}
sil_cache = {}
back_img_cache = {}
evolution_cache = {}
growth_rate_cache = {}
base_exp_cache = {}
trainer_move_cache = {}
stats_cache = {}

MOVE_NAME_KO_TO_EN = {
    "몸통박치기": "tackle",
    "웅크리기": "defense-curl",
    "바위떨구기": "rock-throw",
    "조르기": "bind",
    "울음소리": "screech",
}
_loading_set = set()
_loading_lock = threading.Lock()

SPRITE_URL = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{}.png"
BACK_SPRITE_URL = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/back/{}.png"
TOTAL = 151
COL = 5
CARD_W, CARD_H = 180, 180
IMG_SIZE = 96
book_scroll = 0
scene_start = 0
choice_name = None
choice_desc = None
choice_types = None
tab_rects = []
map_selected = None
map_node_rects = {}
map_ok_r = None
map_no_r = None
bg_imgs = {}

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

def _bg_load(pid):
    if pid not in img_cache:
        try:
            data = requests.get(SPRITE_URL.format(pid), timeout=3).content
            img = pygame.image.load(BytesIO(data)).convert_alpha()
            img = pygame.transform.scale(img, (IMG_SIZE, IMG_SIZE))
            img_cache[pid] = img
        except:
            img_cache[pid] = None
    if pid not in name_cache:
        try:
            res = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{pid}", timeout=3)
            for n in res.json()["names"]:
                if n["language"]["name"] == "ko":
                    name_cache[pid] = n["name"]
                    break
        except:
            name_cache[pid] = str(pid)
    with _loading_lock:
        _loading_set.discard(pid)

def _bg_load_sync(pid):
    _bg_load(pid)
    return img_cache.get(pid)

def preload(pid):
    with _loading_lock:
        if pid not in img_cache and pid not in _loading_set:
            _loading_set.add(pid)
            threading.Thread(target=_bg_load, args=(pid,), daemon=True).start()

def get_img(pid):
    return img_cache.get(pid)

def load_back_img(pid):
    if pid in back_img_cache:
        return back_img_cache[pid]
    try:
        data = requests.get(BACK_SPRITE_URL.format(pid), timeout=3).content
        img = pygame.image.load(BytesIO(data)).convert_alpha()
        img = pygame.transform.scale_by(img, 4)
        back_img_cache[pid] = img
        return img
    except:
        back_img_cache[pid] = None
        return None

def get_korean_name(pid):
    return name_cache.get(pid, str(pid))

def get_silhouette(pid):
    if pid in sil_cache:
        return sil_cache[pid]
    img = img_cache.get(pid)
    if img is None:
        return None
    try:
        import numpy
        sil = img.copy()
        arr = pygame.surfarray.pixels3d(sil)
        arr[:, :, :] = 0
        del arr
        sil_cache[pid] = sil
        return sil
    except:
        sil_cache[pid] = None
        return None

def load_starter_img(pid):
    try:
        data = requests.get(SPRITE_URL.format(pid), timeout=3).content
        img = pygame.image.load(BytesIO(data)).convert_alpha()
        return pygame.transform.scale_by(img, 3)
    except:
        return None

def get_bg(location):
    if location not in bg_imgs:
        paths = {
            "태초마을": "images/firsttown.png",
            "회색시티": "images/graycity.webp",
            "황토마을": "images/wangtotown.jpeg",
            "홍련마을": "images/flowertown.webp",
            "연분홍시티": "images/pinkcity.webp",
            "셀라돈시티": "images/celldoncity.webp",
        }
        path = paths.get(location)
        if path and os.path.exists(path):
            img = pygame.image.load(path)
            bg_imgs[location] = pygame.transform.scale(img, (WIDTH, HEIGHT))
        else:
            s = pygame.Surface((WIDTH, HEIGHT))
            s.fill(BG)
            bg_imgs[location] = s
    return bg_imgs[location]

def get_types_ko(pid):
    res = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pid}")
    types = []
    for t in res.json()["types"]:
        type_res = requests.get(t["type"]["url"])
        for n in type_res.json()["names"]:
            if n["language"]["name"] == "ko":
                types.append(n["name"])
                break
    return types

def get_desc(pid):
    res = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{pid}")
    entries = res.json()["flavor_text_entries"]
    for e in entries:
        if e["language"]["name"] == "ko":
            return e["flavor_text"]
    for e in entries:
        if e["language"]["name"] == "en":
            return e["flavor_text"]
    return ""

def get_stats(pid):
    if pid in stats_cache:
        return stats_cache[pid]
    res = requests.get(f"{BASE}/pokemon/{pid}", timeout=5).json()
    stats_cache[pid] = {s["stat"]["name"]: s["base_stat"] for s in res["stats"]}
    return stats_cache[pid]

def fetch_move(url):
    mv = requests.get(url, timeout=5).json()
    name_ko = next((n["name"] for n in mv["names"] if n["language"]["name"] == "ko"), mv["name"])
    return {
        "name": name_ko,
        "power": mv["power"] or 0,
        "pp": mv["pp"],
        "max_pp": mv["pp"],
        "type": mv["type"]["name"],
        "damage_class": mv["damage_class"]["name"],
    }

def get_my_moves(pid, level):
    res = requests.get(f"{BASE}/pokemon/{pid}", timeout=5).json()
    moves = {}
    count = 0
    for m in res["moves"]:
        for vgd in m["version_group_details"]:
            if vgd["version_group"]["name"] == "red-blue" and vgd["move_learn_method"]["name"] == "level-up":
                if vgd["level_learned_at"] <= level:
                    moves[count] = fetch_move(m["move"]["url"])
                    count += 1
                    if count >= 4:
                        break
        if count >= 4:
            break
    return moves

def check_new_move(pid, old_level, new_level):
    res = requests.get(f"{BASE}/pokemon/{pid}", timeout=5).json()
    new_moves = []
    for m in res["moves"]:
        for vgd in m["version_group_details"]:
            if vgd["version_group"]["name"] == "red-blue" and vgd["move_learn_method"]["name"] == "level-up":
                lv = vgd["level_learned_at"]
                if old_level < lv <= new_level:
                    new_moves.append(fetch_move(m["move"]["url"]))
    return new_moves

def get_trainer_moves(move_names):
    moves = {}
    for i, name in enumerate(move_names[:4]):
        slug = MOVE_NAME_KO_TO_EN.get(name, name)
        if slug not in trainer_move_cache:
            trainer_move_cache[slug] = fetch_move(f"{BASE}/move/{slug}")
        moves[i] = dict(trainer_move_cache[slug])
    return moves

def preload_trainer_data(trainer_name):
    def _load():
        pool = TRY.get(trainer_name, {}).get("pid", {})
        for pid, info in pool.items():
            try:
                preload(pid)
                get_stats(pid)
                get_trainer_moves(info.get("moves", []))
                get_base_experience(pid)
            except Exception:
                pass
    threading.Thread(target=_load, daemon=True).start()

def calc_hp(base_hp, level, iv=15, ev=0):
    return int((base_hp * 2 + iv + ev // 4) * level // 100) + level + 10

def calc_stat(base_stat, level, iv=15, ev=0):
    return int((base_stat * 2 + iv + ev // 4) * level // 100) + 5

def calc_damage(level, attack, defense, power):
    if power == 0:
        return 0
    dmg = int(((2 * level / 5 + 2) * power * attack / max(1, defense)) / 50) + 2
    dmg = int(dmg * random.uniform(0.85, 1.0))
    return max(1, dmg)

def catch(pid):
    res = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{pid}", timeout=5).json()
    capture_rate = res["capture_rate"] 
    return capture_rate

def get_growth_rate(pid):
    if pid in growth_rate_cache:
        return growth_rate_cache[pid]
    species = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{pid}", timeout=5).json()
    rate = species["growth_rate"]["name"]
    growth_rate_cache[pid] = rate
    return rate

def get_base_experience(pid):
    if pid in base_exp_cache:
        return base_exp_cache[pid]
    res = requests.get(f"{BASE}/pokemon/{pid}", timeout=5).json()
    base_exp_cache[pid] = res["base_experience"]
    return base_exp_cache[pid]

def exp_for_level(growth_rate, level):
    n = level
    if growth_rate == "fast":
        return int(0.8 * n ** 3)
    elif growth_rate == "slow":
        return int(1.25 * n ** 3)
    elif growth_rate == "medium-slow":
        return int(1.2 * n ** 3 - 15 * n ** 2 + 100 * n - 140)
    elif growth_rate == "slow-then-very-fast":
        if n <= 50:
            return int(n ** 3 * (100 - n) / 50)
        elif n <= 68:
            return int(n ** 3 * (150 - n) / 100)
        elif n <= 98:
            return int(n ** 3 * ((1911 - 10 * n) // 3) / 500)
        else:
            return int(n ** 3 * (160 - n) / 100)
    elif growth_rate == "fast-then-very-slow":
        if n <= 15:
            return int(n ** 3 * (((n + 1) // 3) + 24) / 50)
        elif n <= 36:
            return int(n ** 3 * (n + 14) / 50)
        else:
            return int(n ** 3 * ((n // 2) + 32) / 50)
    else:
        return n ** 3

def calc_exp_gain(enemy_pid, enemy_level, is_trainer=False):
    base_exp = get_base_experience(enemy_pid)
    a = 1.5 if is_trainer else 1
    return int((base_exp * enemy_level * a) / 7)

def mark_gym_cleared(leader_name):
    for gym_name, info in GYM.items():
        if info.get("leader") == leader_name:
            info["cleared"] = True
            break

def trainer_move_attack(trainer_name):
    available = [i for i, mv in g.battle_moves.items() if mv["pp"] > 0]
    if not available:
        for mv in g.battle_moves.values():
            mv["pp"] = mv["max_pp"]
        available = list(g.battle_moves.keys())
    move_idx = random.choice(available)
    mv = g.battle_moves[move_idx]
    mv["pp"] -= 1
    dc = mv["damage_class"]
    atk = g.battle_sp_attack if dc == "special" else g.battle_attack
    def_ = g.my_sp_defense if dc == "special" else g.my_defense
    dmg = calc_damage(g.battle_level, atk, def_, mv["power"])
    g.my_hp = max(0, g.my_hp - dmg)
    lines = [f"{trainer_name}의 {get_korean_name(g.battle_pid)}이(가) {mv['name']}을(를) 사용했다!"]
    if mv["power"] > 0:
        lines.append(f"내 포켓몬에게 {dmg}의 데미지!")
    return lines

def do_player_turn(move_idx):
    mv = g.my_moves[move_idx]
    if mv["pp"] <= 0:
        g.battle_msgs = ["기술의 PP가 없습니다!"]
        g.battle_after = "command"
        g.battle_state = "msg"
        return

    g.my_moves[move_idx]["pp"] -= 1
    g.poket_list[g.my_pid]["moves"][move_idx]["pp"] -= 1

    msgs = []
    player_first = g.my_speed >= g.battle_speed

    def player_attack():
        dc = mv["damage_class"]
        atk = g.my_sp_attack if dc == "special" else g.my_attack
        def_ = g.battle_sp_defense if dc == "special" else g.battle_defense
        dmg = calc_damage(g.my_level, atk, def_, mv["power"])
        g.battle_hp = max(0, g.battle_hp - dmg)
        msgs.append(f"{get_korean_name(g.my_pid)}이(가) {mv['name']}을(를) 사용했다!")
        if mv["power"] > 0:
            msgs.append(f"상대에게 {dmg}의 데미지!")
        return g.battle_hp <= 0

    def enemy_attack():
        enemy_power = random.randint(35, 55)
        dmg = calc_damage(g.battle_level, g.battle_attack, g.my_defense, enemy_power)
        g.my_hp = max(0, g.my_hp - dmg)
        msgs.append(f"야생의 {g.battle_target}이(가) 공격했다!")
        msgs.append(f"내 포켓몬에게 {dmg}의 데미지!")
        return g.my_hp <= 0

    def give_exp():
        if g.battle_pid:
            is_trainer = g.battle_type == "trainer"
            exp_gain, leveled_up = g.gain_exp(g.my_pid, g.battle_pid, g.battle_level, is_trainer)
            msgs.append(f"{get_korean_name(g.my_pid)}이(가) {exp_gain}의 경험치를 얻었다!")
            for lv in leveled_up:
                msgs.append(f"{get_korean_name(g.my_pid)}이(가) Lv.{lv}(으)로 올랐다!")

    if player_first:
        if player_attack():
            msgs.append(f"야생의 {g.battle_target}이(가) 쓰러졌다!")
            give_exp()
            g.battle_msgs = msgs
            g.battle_after = "win"
            g.battle_state = "msg"
            return
        if enemy_attack():
            msgs.append(f"{get_korean_name(g.my_pid)}이(가) 쓰러졌다!")
            g.battle_msgs = msgs
            g.battle_after = "lose"
            g.battle_state = "msg"
            return
    else:
        if enemy_attack():
            msgs.append(f"{get_korean_name(g.my_pid)}이(가) 쓰러졌다!")
            g.battle_msgs = msgs
            g.battle_after = "lose"
            g.battle_state = "msg"
            return
        if player_attack():
            msgs.append(f"야생의 {g.battle_target}이(가) 쓰러졌다!")
            give_exp()
            g.battle_msgs = msgs
            g.battle_after = "win"
            g.battle_state = "msg"
            return

    g.battle_msgs = msgs
    g.battle_after = "command"
    g.battle_state = "msg"

def do_player_turn_try(move_idx):
    trainer_name = g.battle_target

    mv = g.my_moves[move_idx]
    if mv["pp"] <= 0:
        g.battle_msgs = ["기술의 PP가 없습니다!"]
        g.battle_after = "command"
        g.battle_state = "msg"
        return

    g.my_moves[move_idx]["pp"] -= 1
    g.poket_list[g.my_pid]["moves"][move_idx]["pp"] -= 1

    msgs = []
    player_first = g.my_speed >= g.battle_speed

    def player_attack():
        dc = mv["damage_class"]
        atk = g.my_sp_attack if dc == "special" else g.my_attack
        def_ = g.battle_sp_defense if dc == "special" else g.battle_defense
        dmg = calc_damage(g.my_level, atk, def_, mv["power"])
        g.battle_hp = max(0, g.battle_hp - dmg)
        msgs.append(f"{get_korean_name(g.my_pid)}이(가) {mv['name']}을(를) 사용했다!")
        if mv["power"] > 0:
            msgs.append(f"상대에게 {dmg}의 데미지!")
        return g.battle_hp <= 0

    def enemy_attack():
        lines = trainer_move_attack(trainer_name)
        msgs.extend(lines)
        return g.my_hp <= 0

    def give_exp():
        if g.battle_pid:
            is_trainer = g.battle_type == "trainer"
            exp_gain, leveled_up = g.gain_exp(g.my_pid, g.battle_pid, g.battle_level, is_trainer)
            msgs.append(f"{get_korean_name(g.my_pid)}이(가) {exp_gain}의 경험치를 얻었다!")
            for lv in leveled_up:
                msgs.append(f"{get_korean_name(g.my_pid)}이(가) Lv.{lv}(으)로 올랐다!")

    def handle_enemy_defeated():
        msgs.append(f"{trainer_name}의 {get_korean_name(g.battle_pid)}이(가) 쓰러졌다!")
        del TRY[trainer_name]["pid"][g.battle_pid]
        give_exp()
        remaining = TRY[trainer_name]["pid"]
        if len(remaining) > 0:
            pid, info = next(iter(remaining.items()))
            lv = info["lv"]
            g.battle_pid = pid
            _bg_load_sync(pid)
            g.battle_level = lv
            stats = get_stats(g.battle_pid)
            g.battle_max_hp = calc_hp(stats["hp"], lv)
            g.battle_hp = g.battle_max_hp
            g.battle_attack = calc_stat(stats["attack"], lv)
            g.battle_defense = calc_stat(stats["defense"], lv)
            g.battle_sp_attack = calc_stat(stats["special-attack"], lv)
            g.battle_sp_defense = calc_stat(stats["special-defense"], lv)
            g.battle_speed = calc_stat(stats["speed"], lv)
            g.battle_moves = get_trainer_moves(info.get("moves", []))
            msgs.append(f"{trainer_name}(이)가 다음 포켓몬을 보냈다!")
            g.battle_after = "next_poket"
        else:
            msgs.append(f"{trainer_name}(을)를 이겼다!")
            g.battle_after = "trainer_win"

    if player_first:
        if player_attack():
            handle_enemy_defeated()
            g.battle_msgs = msgs
            g.battle_state = "msg"
            return
        if enemy_attack():
            msgs.append(f"{get_korean_name(g.my_pid)}이(가) 쓰러졌다!")
            g.battle_msgs = msgs
            g.battle_after = "lose"
            g.battle_state = "msg"
            return
    else:
        if enemy_attack():
            msgs.append(f"{get_korean_name(g.my_pid)}이(가) 쓰러졌다!")
            g.battle_msgs = msgs
            g.battle_after = "lose"
            g.battle_state = "msg"
            return
        if player_attack():
            handle_enemy_defeated()
            g.battle_msgs = msgs
            g.battle_state = "msg"
            return

    g.battle_msgs = msgs
    g.battle_after = "command"
    g.battle_state = "msg"

class Game:
    def __init__(self):
        self.scene = "title"
        self.t = 0
        self.notification = None
        self.notif_timer = 0

    def start(self):
        global TRY, GYM
        TRY = copy.deepcopy(TRY_INIT)
        GYM = copy.deepcopy(GYM_INIT)
        for trainer_name in TRY:
            preload_trainer_data(trainer_name)

        self.poket = 0
        self.poket_list = {}
        self.discovered = set()
        self.team = {}
        self.pending_item = None
        self.move_learn_pid = None
        self.return_scene = "main"
        self.pending_evolution = None
        self.item = []
        self.money = 50000
        self.current_location = "태초마을"
        self.scene = "first"
        self.view = None
        self.battle_type = None
        self.battle_target = None
        self.battle_pid = None
        self.bag_list = []
        self.battle_level = 0
        self.battle_hp = 0
        self.battle_max_hp = 0
        self.battle_attack = 0
        self.battle_defense = 0
        self.battle_sp_attack = 0
        self.battle_sp_defense = 0
        self.battle_speed = 0
        self.battle_moves = {}
        self.my_pid = None
        self.my_level = 0
        self.my_hp = 0
        self.my_max_hp = 0
        self.my_attack = 0
        self.my_defense = 0
        self.my_sp_attack = 0
        self.my_sp_defense = 0
        self.my_speed = 0
        self.my_moves = {}
        self.pending_move = None
        self.battle_state = "command"
        self.battle_msgs = []
        self.battle_after = "command"

    def save(self):
        data = {
            "poket": self.poket,
            "poket_list": {
                str(pid): {
                    "lv": info["lv"],
                    "stat": info["stat"],
                    "hp": info["hp"],
                    "max_hp": info["max_hp"],
                    "moves": {str(k): v for k, v in info["moves"].items()},
                    "exp": info.get("exp", 0),
                    "growth_rate": info.get("growth_rate", ""),
                }
                for pid, info in self.poket_list.items()
            },
            "discovered": list(self.discovered),
            "team": list(self.team.keys()),
            "item": self.item,
            "money": self.money,
            "current_location": self.current_location,
        }
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.notify("저장 완료", GREEN)
    
    def load(self):
        if not os.path.exists(SAVE_FILE):
            self.notify("저장 파일이 없습니다", ACCENT)
            return False
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.poket = data["poket"]
        self.poket_list = {
            int(pid): {
                "lv": info["lv"],
                "stat": info["stat"],
                "hp": info["hp"],
                "max_hp": info["max_hp"],
                "moves": {int(k): v for k, v in info["moves"].items()},
                "exp": info.get("exp", 0),
                "growth_rate": info.get("growth_rate", ""),
            }
            for pid, info in data["poket_list"].items()
        }
        for pid, info in self.poket_list.items():
            if not info["growth_rate"]:
                gr = get_growth_rate(pid)
                info["growth_rate"] = gr
                info["exp"] = exp_for_level(gr, info["lv"])
        self.discovered = set(data["discovered"])
        self.team = {pid: self.poket_list[pid] for pid in data["team"] if pid in self.poket_list}
        self.item = data["item"]
        self.money = data["money"]
        self.current_location = data["current_location"]
        self.scene = "main"
        self.view = None
        self.battle_type = None
        self.battle_target = None
        self.battle_pid = None
        self.battle_level = 0
        self.battle_hp = 0
        self.battle_max_hp = 0
        self.battle_attack = 0
        self.battle_defense = 0
        self.pending_item = None
        self.move_learn_pid = None
        self.return_scene = "main"
        self.battle_sp_attack = 0
        self.battle_sp_defense = 0
        self.battle_speed = 0
        self.battle_moves = {}
        self.my_pid = None
        self.my_level = 0
        self.my_hp = 0
        self.my_max_hp = 0
        self.pending_evolution = None 
        self.my_attack = 0
        self.my_defense = 0
        self.my_sp_attack = 0
        self.my_sp_defense = 0
        self.my_speed = 0
        self.my_moves = {}
        self.pending_move = None
        self.battle_state = "command"
        self.battle_msgs = []
        self.battle_after = "command"
        self.notify("불러오기 완료", GREEN)
        for pid in self.poket_list:
            threading.Thread(target=_bg_load, args=(pid,), daemon=True).start()
        return True

    def notify(self, msg, color=WHITE):
        self.notification = (msg, color)
        self.notif_timer = 240

    def find_poket(self, location):
        if random.random() < 0.25:
            trainers = ROUTE_TRAINER.get(location, [])
            if trainers:
                return ("trainer", random.choice(trainers))
            return None
        else:
            pokemons = ROUTE_POKEMON.get(location, [])
            if pokemons:
                return ("pokemon", random.choice(pokemons))
            return None
    
    def buy_item(self, cname):
        self.item.append(cname)

    def get_evolution_by_pid(self, pid):
        if pid in evolution_cache:
            return evolution_cache[pid]
        species = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{pid}", timeout=5).json()
        chain_url = species["evolution_chain"]["url"]
        chain = requests.get(chain_url, timeout=5).json()["chain"]
        evolutions = []
        def parse(node):
            species_url = node["species"]["url"]
            from_pid = int(species_url.rstrip("/").split("/")[-1])
            for evo in node["evolves_to"]:
                to_url = evo["species"]["url"]
                to_pid = int(to_url.rstrip("/").split("/")[-1])
                detail = evo["evolution_details"][0]
                evolutions.append({
                    "from_pid": from_pid,
                    "to_pid": to_pid,
                    "level": detail.get("min_level"),
                    "trigger": detail["trigger"]["name"],
                })
                parse(evo)
        parse(chain)
        evolution_cache[pid] = evolutions
        return evolutions

    def level_up(self, pid):
        old_lv = self.poket_list[pid]["lv"]
        new_lv = old_lv + 1
        self.poket_list[pid]["lv"] = new_lv
        stats = self.poket_list[pid]["stat"]
        self.poket_list[pid]["max_hp"] = calc_hp(stats["hp"], new_lv)
        new_moves = check_new_move(pid, old_lv, new_lv)
        for mv in new_moves:
            cur = self.poket_list[pid]["moves"]
            if len(cur) < 4:
                cur[len(cur)] = mv
            else:
                self.pending_move = mv
                self.move_learn_pid = pid
                self.return_scene = self.scene
                self.scene = "move_learn"
        evos = self.get_evolution_by_pid(pid)
        for evo in evos:
            if evo["from_pid"] == pid and evo["trigger"] == "level-up" and evo["level"]:
                if new_lv >= evo["level"]:
                    self.pending_evolution = (pid, evo["to_pid"])
                    break

    def gain_exp(self, pid, enemy_pid, enemy_level, is_trainer=False):
        if "growth_rate" not in self.poket_list[pid] or not self.poket_list[pid]["growth_rate"]:
            self.poket_list[pid]["growth_rate"] = get_growth_rate(pid)
        if "exp" not in self.poket_list[pid]:
            self.poket_list[pid]["exp"] = exp_for_level(self.poket_list[pid]["growth_rate"], self.poket_list[pid]["lv"])
        growth_rate = self.poket_list[pid]["growth_rate"]
        exp_gain = calc_exp_gain(enemy_pid, enemy_level, is_trainer)
        self.poket_list[pid]["exp"] += exp_gain
        leveled_up = []
        while self.poket_list[pid]["lv"] < 100:
            need = exp_for_level(growth_rate, self.poket_list[pid]["lv"] + 1)
            if self.poket_list[pid]["exp"] >= need:
                self.level_up(pid)
                leveled_up.append(self.poket_list[pid]["lv"])
            else:
                break
        return exp_gain, leveled_up

    def use_monsterball(self, type):
        ball_bonus = 1
        if type == "super":
            ball_bonus = 1.5
        elif type == "hyper":
            ball_bonus = 2
        elif type == "master":
            return True

        a = (3 * g.battle_max_hp - 2 * g.battle_hp) * catch(g.battle_pid) * ball_bonus
        a /= 3 * g.battle_max_hp
        a = int(a)
        if a >= 255:
            return True
        return random.randint(0, 255) < a

    def use_item(self, cname):
        if cname == "몬스터볼":
            if g.use_monsterball("nomal"):
                g.item.remove("몬스터볼")
                g.discovered.add(g.battle_pid)
                stats = get_stats(g.battle_pid)
                lv = g.battle_level
                growth_rate = get_growth_rate(g.battle_pid)
                g.poket_list[g.battle_pid] = {
                    "lv": lv,
                    "stat": stats,
                    "hp": calc_hp(stats["hp"], lv),
                    "max_hp": calc_hp(stats["hp"], lv),
                    "moves": get_my_moves(g.battle_pid, lv),
                    "exp": exp_for_level(growth_rate, lv),
                    "growth_rate": growth_rate,
                }
                g.battle_msgs = ["포켓몬을 잡았다!"]
                g.battle_after = "win"
                g.battle_state = "msg"
            else:
                g.item.remove("몬스터볼")
                g.battle_msgs = ["아, 아깝다!"]
                g.battle_after = "command"
                g.battle_state = "msg"

    def use_item_in_bag(self, cname, pid):
        info = ITEM_LIST[cname]
        if info["type"] == "level_up":
            for _ in range(info["eff"]):
                self.level_up(pid)
            if pid in self.team:
                self.team[pid] = self.poket_list[pid]
            self.notify(f"{get_korean_name(pid)}의 레벨이 올랐다!", GREEN)

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
        _fire_img = load_starter_img(4)
    if _water_img is None:
        _water_img = load_starter_img(7)
    if _wrong_img is None:
        _wrong_img = load_starter_img(1)

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
        for pid, img, cx in [(4, _fire_img, 300), (7, _water_img, 500), (1, _wrong_img, 700)]:
            ball_rect = _pokeball.get_rect(center=(cx, HEIGHT // 2 + 20))
            hovered = ball_rect.collidepoint(mx, my)
            show = img if (hovered and img) else _pokeball
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
    pygame.draw.polygon(screen, WHITE, [(img_x - 10, by), (img_x + 10, by), (img_x, by - 15)])
    pygame.draw.lines(screen, BORDER, False, [(img_x - 10, by), (img_x, by - 15), (img_x + 10, by)], 2)
    screen.blit(ts, (bx + 20, by + 12))

def draw_main(bg_img):
    screen.blit(bg_img, (0, 0))
    mx, my = pygame.mouse.get_pos()
    txt(screen, "포켓몬스터", F18, BLACK, 460, 15)
    txt(screen, f"돈: {g.money}", F18, GOLD, 460, 40)
    tabs = [("야생", "wild"), ("체육관", "gym"), ("포켓몬 센터", "center"),
            ("상점", "shop"), ("가방", "bag"), ("지도", "map"), ("팀", "team"), ("도감", "book"),("저장","save")]
    tab_rects = []
    tab_w = (WIDTH - 20) // len(tabs)
    for i, (label, key) in enumerate(tabs):
        r = pygame.Rect(10 + i * tab_w, 66, tab_w - 4, 34)
        active = g.view == key
        bc = (40, 60, 130) if active else PANEL2
        panel(screen, r.x, r.y, r.w, r.h, bc, alpha=220, radius=6, border=ACCENT if active else DARK_GRAY)
        txt(screen, label, F12, WHITE if active else BLACK, r.centerx, r.centery, center=True)
        tab_rects.append((r, key))
    content_y = 108
    if g.view == "wild": draw_wild(content_y, mx, my)
    elif g.view == "gym": draw_gym(content_y, mx, my)
    elif g.view == "center": draw_center(content_y, mx, my)
    elif g.view == "shop": 
        global item_li
        item_li = draw_shop(content_y, mx, my)
    elif g.view == "bag": draw_bag(content_y, mx, my)
    elif g.view == "map": draw_map(content_y, mx, my)
    elif g.view == "team": draw_team(content_y, mx, my)
    elif g.view == "book": draw_book(content_y)
    return tab_rects

def draw_wild(cy, mx, my):
    panel(screen, 10, cy, WIDTH - 20, HEIGHT - cy - 62, GREEN, alpha=255, radius=10, border=PANEL2)
    b = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 48)
    btn(screen, b, "풀숲 뒤지기", F18, hover=b.collidepoint(mx, my))
    return b

def draw_gym(cy, mx, my):
    panel(screen, 10, cy, WIDTH - 20, HEIGHT - cy - 62, PANEL, alpha=180, radius=10, border=BORDER)
    txt(screen, "체육관", F18, ACCENT, WIDTH // 2, cy + 18, center=True)
    txt(screen, "체육관의 관장들에게 도전해 뱃지 얻으세요", F12, GRAY, WIDTH // 2, cy + 42, center=True)
    gym_list = []
    names = list(GYM.keys())
    for i, cname in enumerate(names):
        info = GYM[cname]
        if(info["location"] == g.current_location):
            cx2 = 30 + (i % 2) * 480
            cy2 = cy + 70 + (i // 2) * 160
            w, h = 450, 145
            panel(screen, cx2, cy2, w, h, (40, 60, 100), alpha=220, radius=12, border=True)
            txt(screen, cname, F18, BLACK, cx2 + 20, cy2 + 14)
            txt(screen, f"관장: {info['leader']}", F14, GOLD, cx2 + 20, cy2 + 100)
            r = pygame.Rect(cx2 + w - 110, cy2 + h - 42, 95, 30)
            if info.get("cleared"):
                txt(screen, "클리어 완료!", F14, GREEN, cx2 + 20, cy2 + 122)
                btn(screen, r, "클리어", F12, active=False)
            else:
                btn(screen, r, "도전하기", F12, hover=r.collidepoint(mx, my))
                gym_list.append((r, cname))
    return gym_list

def draw_center(cy, mx, my):
    panel(screen, 10, cy, WIDTH - 20, HEIGHT - cy - 62, PANEL, alpha=255, radius=10, border=PANEL2)

def draw_shop(cy, mx, my):
    panel(screen, 10, cy, WIDTH - 20, HEIGHT - cy - 62, PANEL, alpha=180, radius=10, border=BORDER)
    txt(screen, "상점", F18, ACCENT, WIDTH // 2, cy + 18, center=True)
    txt(screen, "상점에서 물건을 구매하고 모험을 계속하세요", F12, GRAY, WIDTH // 2, cy + 42, center=True)
    item_list = []
    names = list(ITEM_LIST.keys())
    for i, cname in enumerate(names):
        info = ITEM_LIST[cname]
        cx2 = 30 + (i % 2) * 480
        cy2 = cy + 70 + (i // 2) * 160
        w, h = 450, 145
        panel(screen, cx2, cy2, w, h, (40, 60, 100), alpha=220, radius=12, border=True)
        txt(screen, cname, F18, BLACK, cx2 + 20, cy2 + 14)
        txt(screen, info["desc"], F12, GRAY, cx2 + 20, cy2 + 46)
        txt(screen, f"가격: {info['money']}", F14, GOLD, cx2 + 20, cy2 + 100)
        count = g.item.count(cname)
        if count > 0:
            txt(screen, f"보유 x{count}", F12, GREEN, cx2 + w - 20, cy2 + 14, right=True)
        r = pygame.Rect(cx2 + w - 110, cy2 + h - 42, 95, 30)
        btn(screen, r, "구매하기", F12, hover=r.collidepoint(mx, my))
        item_list.append((r, cname))
    return item_list

def draw_bag(cy, mx, my):
    panel(screen, 10, cy, WIDTH - 20, HEIGHT - cy - 62, PANEL, alpha=180, radius=10, border=BORDER)
    txt(screen, "가방", F18, ACCENT, WIDTH // 2, cy + 18, center=True)
    txt(screen, "소지하고 있는 아이템 입니다", F12, GRAY, WIDTH // 2, cy + 42, center=True)
    bag_rect = []
    seen = []
    for cname in g.item:
        if cname not in seen:
            seen.append(cname)
    for i, cname in enumerate(seen):
        info = ITEM_LIST[cname]
        cx2 = 30 + (i % 2) * 480
        cy2 = cy + 70 + (i // 2) * 160
        w, h = 450, 145
        panel(screen, cx2, cy2, w, h, (40, 60, 100), alpha=220, radius=12, border=True)
        txt(screen, cname, F18, BLACK, cx2 + 20, cy2 + 14)
        count = g.item.count(cname)
        txt(screen, f"x{count}", F12, GREEN, cx2 + w - 20, cy2 + 14, right=True)
        txt(screen, info["desc"], F12, GRAY, cx2 + 20, cy2 + 46)
        r = pygame.Rect(cx2 + w - 110, cy2 + h - 42, 95, 30)
        if(info["use"]):
            btn(screen, r, "사용하기", F12, hover=r.collidepoint(mx, my))
            bag_rect.append((r, cname))
    return bag_rect

def draw_item_poket_select(cy, mx, my):
    screen.fill(BG)
    panel(screen, 10, cy, WIDTH - 20, HEIGHT - cy - 62, PANEL, alpha=255, radius=10, border=PANEL2)
    txt(screen, f"{g.pending_item} 사용", F18, ACCENT, WIDTH // 2, cy + 18, center=True)
    txt(screen, "어느 포켓몬에게 사용하시겠습니까?", F12, GRAY, WIDTH // 2, cy + 42, center=True)
    have_pids = sorted(g.poket_list.keys())
    poket_rects = []
    for i, pid in enumerate(have_pids):
        col = i % 6
        row = i // 6
        x = 20 + col * 158
        y = cy + 64 + row * 110
        r = pygame.Rect(x, y, 148, 96)
        panel(screen, x, y, 148, 96, PANEL2, alpha=220, radius=8, border=BORDER)
        img = get_img(pid)
        if img:
            screen.blit(img, (x + 26, y + 4))
        lv = g.poket_list[pid]["lv"]
        txt(screen, get_korean_name(pid), F12, BLACK, x + 74, y + 68, center=True)
        txt(screen, f"Lv.{lv}", F12, GRAY, x + 74, y + 82, center=True)
        if r.collidepoint(mx, my):
            pygame.draw.rect(screen, ACCENT, r, 2, border_radius=8)
        poket_rects.append((r, pid))
    if not have_pids:
        txt(screen, "포켓몬이 없습니다", F14, GRAY, WIDTH // 2, cy + 100, center=True)
    back_r = pygame.Rect(WIDTH - 130, HEIGHT - 48, 120, 38)
    btn(screen, back_r, "취소", F12, hover=back_r.collidepoint(mx, my))
    return poket_rects, back_r

def draw_team(cy, mx, my):
    panel(screen, 10, cy, WIDTH - 20, HEIGHT - cy - 10, PANEL, alpha=255, radius=10, border=PANEL2)
    txt(screen, "보유 포켓몬", F14, DARK_GRAY, 30, cy + 14)
    txt(screen, "팀 (최대 6)", F14, DARK_GRAY, WIDTH // 2 + 20, cy + 14)
    pygame.draw.line(screen, PANEL2, (WIDTH // 2, cy + 10), (WIDTH // 2, HEIGHT - 20), 2)

    have_pids = sorted(g.poket_list.keys())
    for i, pid in enumerate(have_pids):
        col = i % 3
        row = i // 3
        x = 30 + col * 150
        y = cy + 44 + row * 110
        is_in_team = pid in g.team
        bc = (200, 240, 200) if is_in_team else PANEL2
        r = pygame.Rect(x, y, 120, 96)
        panel(screen, x, y, 120, 96, bc, alpha=220, radius=8, border=BORDER)
        img = get_img(pid)
        if img:
            screen.blit(img, (x + 12, y + 4))
        lv = g.poket_list[pid]["lv"]
        txt(screen, get_korean_name(pid), F12, BLACK, x + 60, y + 68, center=True)
        txt(screen, f"Lv.{lv}", F12, GRAY, x + 60, y + 82, center=True)
        if r.collidepoint(mx, my):
            pygame.draw.rect(screen, ACCENT, r, 2, border_radius=8)

    team_rects = []
    team_keys = list(g.team.keys())
    for i in range(6):
        col = i % 2
        row = i // 2
        x = WIDTH // 2 + 30 + col * 210
        y = cy + 44 + row * 120
        r = pygame.Rect(x, y, 180, 100)
        if i < len(team_keys):
            pid = team_keys[i]
            panel(screen, x, y, 180, 100, (220, 240, 220), alpha=220, radius=8, border=BORDER)
            img = get_img(pid)
            if img:
                screen.blit(img, (x + 8, y + 4))
            txt(screen, get_korean_name(pid), F14, BLACK, x + 90, y + 70, center=True)
            txt(screen, "✕", F14, ACCENT, x + 156, y + 8)
        else:
            panel(screen, x, y, 180, 100, PANEL2, alpha=160, radius=8, border=GRAY)
            txt(screen, f"슬롯 {i + 1}", F12, GRAY, x + 90, y + 50, center=True)
        team_rects.append(r)

    return have_pids, team_rects

def draw_map(cy, mx, my):
    global map_node_rects, map_ok_r, map_no_r
    MX, MY = 15, cy + 5
    MW, MH = WIDTH - 30, HEIGHT - cy - 20

    FRAME_C = (168, 168, 184)
    FRAME_L = (208, 208, 224)
    FRAME_D = (136, 136, 152)
    ROUTE_C = (228, 196, 228)
    LAND_C = (112, 184, 88)
    WATER_C = (168, 212, 248)
    T_BG = (244, 248, 252)
    T_BD = (12, 12, 20)

    def sc(rx, ry):
        return int(MX + rx * MW / 1000), int(MY + ry * MH / 1000)

    def R(rx, ry, rw, rh, c):
        ax, ay = sc(rx, ry)
        bx2, by2 = sc(rx + rw, ry + rh)
        pygame.draw.rect(screen, c, (ax, ay, max(1, bx2 - ax), max(1, by2 - ay)))

    pygame.draw.rect(screen, FRAME_C, (MX, MY, MW, MH), border_radius=4)
    fm = max(4, int(14 * MW / 1000))
    IX, IY = MX + fm, MY + fm
    IW, IH = MW - fm * 2, MH - fm * 2
    pygame.draw.rect(screen, ROUTE_C, (IX, IY, IW, IH))

    for lx, ly, lw, lh in [
        (16, 16, 968, 215),
        (16, 16, 215, 968),
        (231, 231, 175, 535),
        (231, 231, 375, 195),
        (641, 16, 195, 420),
        (841, 16, 143, 968),
        (491, 601, 353, 383),
    ]:
        R(lx, ly, lw, lh, LAND_C)

    for wx, wy, ww, wh in [
        (16, 776, 215, 208),
        (641, 441, 200, 543),
        (406, 426, 235, 250),
        (686, 16, 155, 215),
        (231, 776, 260, 208),
    ]:
        R(wx, wy, ww, wh, WATER_C)

    RW = 68
    for rx2, ry2, rw2, rh2 in [
        (118, 776, RW, 208),
        (118, 231, RW, 296),
        (183, 148, 308, RW),
        (461, 148, RW, 83),
        (461, 231, RW, 195),
        (529, 148, 162, RW),
        (661, 148, RW, 293),
        (231, 426, 230, RW),
        (231, 494, RW, 282),
        (299, 701, 362, RW),
        (593, 494, RW, 282),
        (461, 426, 200, RW),
    ]:
        R(rx2, ry2, rw2, rh2, ROUTE_C)

    fw = max(3, int(8 * MW / 1000))
    pygame.draw.rect(screen, FRAME_D, (IX, IY, IW, IH), fw)

    for jx, jy in [(16, 16), (500, 16), (984, 16), (16, 500), (984, 500), (16, 984), (500, 984), (984, 984)]:
        jsx, jsy = sc(jx, jy)
        jr = max(4, int(17 * MW / 1000))
        pygame.draw.circle(screen, FRAME_L, (jsx, jsy), jr)
        pygame.draw.circle(screen, FRAME_D, (jsx, jsy), jr, 2)

    current = g.current_location
    reachable = set(MAP_NODES[current]["conn"])
    node_rects = {}

    for name in MAP_NODES:
        if name not in NODE_POS:
            continue
        nx, ny = NODE_POS[name]
        sx, sy = sc(nx, ny)
        ntype = MAP_NODES[name]["type"]
        is_current = (name == current)
        is_reachable = (name in reachable)
        is_route = (ntype == "route")

        if is_route:
            rc = max(5, int(11 * MW / 1000))
            if is_reachable:
                pygame.draw.circle(screen, (210, 248, 210), (sx, sy), rc)
                pygame.draw.circle(screen, (30, 150, 30), (sx, sy), rc, 2)
            else:
                pygame.draw.circle(screen, ROUTE_C, (sx, sy), rc)
                pygame.draw.circle(screen, T_BD, (sx, sy), rc, 1)
            node_rects[name] = pygame.Rect(sx - rc - 4, sy - rc - 4, rc * 2 + 8, rc * 2 + 8)
        else:
            sq = max(10, int(22 * MW / 1000))
            sqr = pygame.Rect(sx - sq, sy - sq, sq * 2, sq * 2)
            if is_current:
                pygame.draw.rect(screen, T_BG, sqr)
                pygame.draw.rect(screen, T_BD, sqr, 1)
                outer_sq = sq + max(4, int(7 * MW / 1000))
                outer = pygame.Rect(sx - outer_sq, sy - outer_sq, outer_sq * 2, outer_sq * 2)
                pygame.draw.rect(screen, T_BD, outer, max(3, int(5 * MW / 1000)))
            elif is_reachable:
                pygame.draw.rect(screen, (210, 248, 210), sqr)
                pygame.draw.rect(screen, (30, 150, 30), sqr, 2)
            else:
                pygame.draw.rect(screen, T_BG, sqr)
                pygame.draw.rect(screen, T_BD, sqr, 1)
            ns = F12.render(name, True, T_BD)
            screen.blit(ns, (sqr.right + 3, sqr.centery - ns.get_height() // 2))
            node_rects[name] = pygame.Rect(sqr.x, sqr.y, sqr.w + ns.get_width() + 10, sqr.h)

    loc_surf = F14.render(current, True, T_BD)
    bg_r = pygame.Rect(MX + 8, MY + 8, loc_surf.get_width() + 12, loc_surf.get_height() + 8)
    pygame.draw.rect(screen, T_BG, bg_r)
    screen.blit(loc_surf, (MX + 14, MY + 12))

    map_node_rects = node_rects

    if map_selected and map_selected in MAP_NODES:
        ppx, ppy = WIDTH // 2 - 180, HEIGHT // 2 - 70
        pygame.draw.rect(screen, WHITE, (ppx, ppy, 360, 140), border_radius=12)
        pygame.draw.rect(screen, BORDER, (ppx, ppy, 360, 140), 2, border_radius=12)
        txt(screen, f"{map_selected}(으)로 이동하시겠습니까?", F14, BLACK, WIDTH // 2, ppy + 36, center=True)
        ok_r = pygame.Rect(ppx + 20, ppy + 82, 140, 38)
        no_r = pygame.Rect(ppx + 200, ppy + 82, 140, 38)
        btn(screen, ok_r, "이동하기", F14, hover=ok_r.collidepoint(mx, my))
        btn(screen, no_r, "취소", F14, hover=no_r.collidepoint(mx, my))
        map_ok_r = ok_r
        map_no_r = no_r
    else:
        map_ok_r = None
        map_no_r = None

evo_from_pid = None
evo_to_pid = None
evo_start = 0

def draw_evolution():
    global evo_from_pid, evo_to_pid
    elapsed = pygame.time.get_ticks() - evo_start
    screen.fill(BLACK)

    if elapsed < 2000:
        img = get_img(evo_from_pid)
        if img:
            big = pygame.transform.scale(img, (200, 200))
            screen.blit(big, (WIDTH // 2 - 100, HEIGHT // 2 - 140))
        txt(screen, f"오잉? {get_korean_name(evo_from_pid)}의 상태가...", F18, WHITE, WIDTH // 2, HEIGHT // 2 + 80, center=True)

    elif elapsed < 4000:
        blink = (elapsed // 200) % 2 == 0
        pid = evo_from_pid if blink else evo_to_pid
        img = get_img(pid)
        if img:
            big = pygame.transform.scale(img, (200, 200))
            s = pygame.Surface((200, 200), pygame.SRCALPHA)
            s.blit(big, (0, 0))
            arr = pygame.surfarray.pixels3d(s)
            arr[:, :, :] = 255
            del arr
            screen.blit(s, (WIDTH // 2 - 100, HEIGHT // 2 - 140))
        txt(screen, "진화", F18, WHITE, WIDTH // 2, HEIGHT // 2 + 80, center=True)

    else:
        img = get_img(evo_to_pid)
        if img:
            big = pygame.transform.scale(img, (200, 200))
            screen.blit(big, (WIDTH // 2 - 100, HEIGHT // 2 - 140))
        txt(screen, f"{get_korean_name(evo_from_pid)}이(가) {get_korean_name(evo_to_pid)}(으)로 진화했다!", F18, GOLD, WIDTH // 2, HEIGHT // 2 + 80, center=True)
        txt(screen, "클릭하여 계속", F12, GRAY, WIDTH // 2, HEIGHT // 2 + 120, center=True)


def draw_battle_choice(cy, mx, my):
    screen.fill(BG)
    panel(screen, WIDTH // 2 - 300, HEIGHT // 2 - 180, 600, 360, PANEL2, alpha=235, radius=16, border=True)
    if g.battle_type == "trainer":
        txt(screen, f"{g.battle_target}(이)가 도전장을 내민다!", F18, BLACK, WIDTH // 2, HEIGHT // 2 - 148, center=True)
    else:
        txt(screen, f"야생의 {g.battle_target}이 나타났다!", F18, BLACK, WIDTH // 2, HEIGHT // 2 - 148, center=True)
    pygame.draw.line(screen, BORDER, (WIDTH // 2 - 270, HEIGHT // 2 - 122), (WIDTH // 2 + 270, HEIGHT // 2 - 122), 1)
    ok_r = pygame.Rect(WIDTH // 2 - 160, HEIGHT // 2 + 120, 140, 40)
    no_r = pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2 + 120, 140, 40)
    btn(screen, ok_r, "싸운다", F14, hover=ok_r.collidepoint(mx, my))
    if g.battle_type == "pokemon":
        btn(screen, no_r, "도망간다", F14, hover=no_r.collidepoint(mx, my))
    else:
        btn(screen, no_r, "포기한다", F14, hover=no_r.collidepoint(mx,my))
    return ok_r, no_r

def draw_battle_moves(mx, my):
    pygame.draw.rect(screen, WHITE, (0, HEIGHT - 160, WIDTH, 160))
    pygame.draw.rect(screen, BLACK, (0, HEIGHT - 160, WIDTH, 160), 3)
    move_rects = []
    for i in range(4):
        col = i % 2
        row = i // 2
        x = col * (WIDTH // 2)
        y = HEIGHT - 160 + row * 80
        r = pygame.Rect(x, y, WIDTH // 2, 80)
        pygame.draw.rect(screen, BLACK, r, 1)
        if i < len(g.my_moves):
            mv = g.my_moves[i]
            tc = TYPE_COLORS.get(mv["type"], GRAY)
            s = pygame.Surface((WIDTH // 2, 80), pygame.SRCALPHA)
            pygame.draw.rect(s, (*tc, 60), (0, 0, WIDTH // 2, 80))
            screen.blit(s, (x, y))
            txt(screen, mv["name"], F18, BLACK, x + 20, y + 10)
            txt(screen, f"PP {mv['pp']}/{mv['max_pp']}", F12, GRAY, x + 20, y + 46)
            txt(screen, mv["type"], F12, tc, x + WIDTH // 2 - 20, y + 10, right=True)
            txt(screen, f"위력 {mv['power']}", F12, GRAY, x + WIDTH // 2 - 20, y + 46, right=True)
        else:
            txt(screen, "-", F18, GRAY, x + WIDTH // 4, y + 30, center=True)
        move_rects.append(r)
    back_r = pygame.Rect(WIDTH - 130, HEIGHT - 48, 120, 38)
    btn(screen, back_r, "돌아가기", F12, hover=back_r.collidepoint(mx, my))
    return move_rects, back_r

def draw_battle_items(mx, my):
    pygame.draw.rect(screen, WHITE, (0, HEIGHT - 160, WIDTH, 160))
    pygame.draw.rect(screen, BLACK, (0, HEIGHT - 160, WIDTH, 160), 3)
    seen = []
    for cname in g.item:
        if cname not in seen:
            seen.append(cname)
    item_rects = []
    for i, cname in enumerate(seen):
        count = g.item.count(cname)
        x = WIDTH // 2 + (i % 2) * 240 + 20
        y = HEIGHT - 150 + (i // 2) * 60 + 10
        r = pygame.Rect(x, y, 200, 48)
        btn(screen, r, f"{cname} x{count}", F14, hover=r.collidepoint(mx, my))
        item_rects.append((r, cname))
    if not seen:
        txt(screen, "아이템이 없습니다", F14, GRAY, WIDTH // 2 + 230, HEIGHT - 80, center=True)
    back_r = pygame.Rect(WIDTH // 2 + 20, HEIGHT - 48, 110, 36)
    btn(screen, back_r, "돌아가기", F12, hover=back_r.collidepoint(mx, my))
    return item_rects, back_r

def draw_battle_poket_change(mx, my):
    pygame.draw.rect(screen, WHITE, (0, HEIGHT - 160, WIDTH, 160))
    pygame.draw.rect(screen, BLACK, (0, HEIGHT - 160, WIDTH, 160), 3)
    txt(screen, "어느 포켓몬과 교체하시겠습니까?", F14, BLACK, 20, HEIGHT - 148)
    team_keys = list(g.team.keys())
    poket_rects = []
    for i, pid in enumerate(team_keys):
        x = WIDTH // 2 + (i % 3) * 160 + 10
        y = HEIGHT - 148 + (i // 3) * 70
        r = pygame.Rect(x, y, 150, 60)
        is_current = pid == g.my_pid
        bc = (100, 100, 100) if is_current else (40, 60, 130)
        panel(screen, x, y, 150, 60, bc, alpha=220, radius=8, border=BORDER)
        img = get_img(pid)
        if img:
            small = pygame.transform.scale(img, (48, 48))
            screen.blit(small, (x + 4, y + 6))
        txt(screen, get_korean_name(pid), F12, WHITE, x + 56, y + 10)
        hp = g.team[pid]["hp"]
        max_hp = g.team[pid]["max_hp"]
        txt(screen, f"HP {hp}/{max_hp}", F12, GRAY, x + 56, y + 30)
        if is_current:
            txt(screen, "출전중", F12, GOLD, x + 56, y + 44)
        poket_rects.append((r, pid))
    back_r = pygame.Rect(WIDTH // 2 - 110, HEIGHT - 48, 100, 36)
    btn(screen, back_r, "돌아가기", F12, hover=back_r.collidepoint(mx, my))
    return poket_rects, back_r

def draw_move_learn(mx, my):
    screen.fill(BG)
    panel(screen, WIDTH // 2 - 320, 60, 640, 560, PANEL2, alpha=235, radius=16, border=True)
    moves = g.poket_list[g.move_learn_pid]["moves"]
    if g.pending_move:
        txt(screen, f"{get_korean_name(g.move_learn_pid)}이(가) {g.pending_move['name']}을(를) 배우려 합니다!", F14, BLACK, WIDTH // 2, 100, center=True)
    txt(screen, "교체할 기술을 선택하세요 (또는 포기)", F12, GRAY, WIDTH // 2, 130, center=True)
    slot_rects = []
    for i in range(4):
        x = WIDTH // 2 - 280
        y = 160 + i * 90
        r = pygame.Rect(x, y, 560, 76)
        if i < len(moves):
            mv = moves[i]
            tc = TYPE_COLORS.get(mv["type"], GRAY)
            panel(screen, x, y, 560, 76, (240, 240, 248), alpha=220, radius=8, border=BORDER)
            txt(screen, mv["name"], F18, BLACK, x + 20, y + 12)
            txt(screen, f"PP {mv['pp']}/{mv['max_pp']}", F12, GRAY, x + 20, y + 46)
            txt(screen, mv["type"], F12, tc, x + 540, y + 12, right=True)
            txt(screen, f"위력 {mv['power']}", F12, GRAY, x + 540, y + 46, right=True)
        slot_rects.append(r)
    skip_r = pygame.Rect(WIDTH // 2 - 100, 540, 200, 44)
    btn(screen, skip_r, "포기", F14, hover=skip_r.collidepoint(mx, my))
    return slot_rects, skip_r

def draw_battle(mx, my):
    screen.fill((120, 180, 100))
    pygame.draw.rect(screen, (88, 140, 72), (0, 0, WIDTH, HEIGHT // 2))
    pygame.draw.rect(screen, (200, 180, 120), (0, HEIGHT // 2, WIDTH, HEIGHT // 2))

    pygame.draw.ellipse(screen, (80, 120, 60), (540, 210, 200, 40))

    if g.battle_pid:
        img = get_img(g.battle_pid)
        if img:
            big = pygame.transform.scale_by(img, 4)
            screen.blit(big, (470, 0))

    pygame.draw.rect(screen, WHITE, (30, 30, 280, 90), border_radius=8)
    pygame.draw.rect(screen, BLACK, (30, 30, 280, 90), 2, border_radius=8)
    txt(screen, g.battle_target, F18, BLACK, 50, 45)
    txt(screen, f"Lv.{g.battle_level}", F14, GRAY, 260, 45, right=True)
    ratio = g.battle_hp / g.battle_max_hp if g.battle_max_hp > 0 else 0
    bar_w = int(200 * ratio)
    bar_c = (80, 220, 80) if ratio > 0.5 else (220, 220, 80) if ratio > 0.25 else (220, 80, 80)
    pygame.draw.rect(screen, (200, 200, 200), (50, 85, 200, 12), border_radius=6)
    pygame.draw.rect(screen, bar_c, (50, 85, bar_w, 12), border_radius=6)
    txt(screen, f"{g.battle_hp}/{g.battle_max_hp}", F12, BLACK, 260, 70, right=True)

    pygame.draw.ellipse(screen, (160, 140, 90), (160, 330, 220, 50))

    if g.my_pid:
        back_img = load_back_img(g.my_pid)
        if back_img:
            screen.blit(back_img, (0, 150))

    pygame.draw.rect(screen, WHITE, (580, 270, 280, 90), border_radius=8)
    pygame.draw.rect(screen, BLACK, (580, 270, 280, 90), 2, border_radius=8)
    if g.my_pid:
        txt(screen, get_korean_name(g.my_pid), F18, BLACK, 600, 285)
        txt(screen, f"Lv.{g.my_level}", F14, GRAY, 840, 285, right=True)
    my_ratio = g.my_hp / g.my_max_hp if g.my_max_hp > 0 else 0
    my_bar_w = int(200 * my_ratio)
    my_bar_c = (80, 220, 80) if my_ratio > 0.5 else (220, 220, 80) if my_ratio > 0.25 else (220, 80, 80)
    pygame.draw.rect(screen, (200, 200, 200), (600, 325, 200, 12), border_radius=6)
    pygame.draw.rect(screen, my_bar_c, (600, 325, my_bar_w, 12), border_radius=6)
    txt(screen, "HP", F12, BLACK, 600, 310)
    txt(screen, f"{g.my_hp}/{g.my_max_hp}", F12, BLACK, 840, 310, right=True)

    if g.battle_state == "command":
        pygame.draw.rect(screen, WHITE, (0, HEIGHT - 160, WIDTH, 160))
        pygame.draw.rect(screen, BLACK, (0, HEIGHT - 160, WIDTH, 160), 3)
        pygame.draw.rect(screen, WHITE, (0, HEIGHT - 160, WIDTH // 2, 160))
        pygame.draw.rect(screen, BLACK, (0, HEIGHT - 160, WIDTH // 2, 160), 2)
        txt(screen, f"야생의 {g.battle_target}이 나타났다!", F14, BLACK, 20, HEIGHT - 130)
        cmds = ["싸운다", "가방", "포켓몬", "도망간다"]
        cmd_rects = []
        for i, cmd in enumerate(cmds):
            cx = WIDTH // 2 + (i % 2) * 240 + 20
            cy = HEIGHT - 150 + (i // 2) * 60 + 10
            r = pygame.Rect(cx, cy, 200, 48)
            btn(screen, r, cmd, F18, hover=r.collidepoint(mx, my))
            cmd_rects.append(r)
        return cmd_rects, None, None
    elif g.battle_state == "move":
        move_rects, back_r = draw_battle_moves(mx, my)
        return None, move_rects, back_r
    elif g.battle_state == "bag":
        item_rects, back_r = draw_battle_items(mx, my)
        return None, item_rects, back_r
    elif g.battle_state == "change":
        poket_rects, back_r = draw_battle_poket_change(mx ,my)
        return None, poket_rects, back_r
    else:
        pygame.draw.rect(screen, WHITE, (0, HEIGHT - 160, WIDTH, 160))
        pygame.draw.rect(screen, BLACK, (0, HEIGHT - 160, WIDTH, 160), 3)
        if g.battle_msgs:
            txt(screen, g.battle_msgs[0], F18, BLACK, 20, HEIGHT - 120)
        txt(screen, "▼", F12, GRAY, WIDTH - 20, HEIGHT - 20, right=True)
        return None, None, None


def draw_battle_trianer(mx, my):
    screen.fill((120, 180, 100))
    pygame.draw.rect(screen, (88, 140, 72), (0, 0, WIDTH, HEIGHT // 2))
    pygame.draw.rect(screen, (200, 180, 120), (0, HEIGHT // 2, WIDTH, HEIGHT // 2))

    pygame.draw.ellipse(screen, (80, 120, 60), (540, 210, 200, 40))

    if g.battle_pid:
        img = get_img(g.battle_pid)
        if img:
            big = pygame.transform.scale_by(img, 4)
            screen.blit(big, (470, 0))

    pygame.draw.rect(screen, WHITE, (30, 30, 280, 90), border_radius=8)
    pygame.draw.rect(screen, BLACK, (30, 30, 280, 90), 2, border_radius=8)
    txt(screen, get_korean_name(g.battle_pid), F18, BLACK, 50, 45)
    txt(screen, f"Lv.{g.battle_level}", F14, GRAY, 260, 45, right=True)
    ratio = g.battle_hp / g.battle_max_hp if g.battle_max_hp > 0 else 0
    bar_w = int(200 * ratio)
    bar_c = (80, 220, 80) if ratio > 0.5 else (220, 220, 80) if ratio > 0.25 else (220, 80, 80)
    pygame.draw.rect(screen, (200, 200, 200), (50, 85, 200, 12), border_radius=6)
    pygame.draw.rect(screen, bar_c, (50, 85, bar_w, 12), border_radius=6)
    txt(screen, f"{g.battle_hp}/{g.battle_max_hp}", F12, BLACK, 260, 70, right=True)

    pygame.draw.ellipse(screen, (160, 140, 90), (160, 330, 220, 50))

    if g.my_pid:
        back_img = load_back_img(g.my_pid)
        if back_img:
            screen.blit(back_img, (0, 150))

    pygame.draw.rect(screen, WHITE, (580, 270, 280, 90), border_radius=8)
    pygame.draw.rect(screen, BLACK, (580, 270, 280, 90), 2, border_radius=8)
    if g.my_pid:
        txt(screen, get_korean_name(g.my_pid), F18, BLACK, 600, 285)
        txt(screen, f"Lv.{g.my_level}", F14, GRAY, 840, 285, right=True)
    my_ratio = g.my_hp / g.my_max_hp if g.my_max_hp > 0 else 0
    my_bar_w = int(200 * my_ratio)
    my_bar_c = (80, 220, 80) if my_ratio > 0.5 else (220, 220, 80) if my_ratio > 0.25 else (220, 80, 80)
    pygame.draw.rect(screen, (200, 200, 200), (600, 325, 200, 12), border_radius=6)
    pygame.draw.rect(screen, my_bar_c, (600, 325, my_bar_w, 12), border_radius=6)
    txt(screen, "HP", F12, BLACK, 600, 310)
    txt(screen, f"{g.my_hp}/{g.my_max_hp}", F12, BLACK, 840, 310, right=True)

    if g.battle_state == "command":
        pygame.draw.rect(screen, WHITE, (0, HEIGHT - 160, WIDTH, 160))
        pygame.draw.rect(screen, BLACK, (0, HEIGHT - 160, WIDTH, 160), 3)
        pygame.draw.rect(screen, WHITE, (0, HEIGHT - 160, WIDTH // 2, 160))
        pygame.draw.rect(screen, BLACK, (0, HEIGHT - 160, WIDTH // 2, 160), 2)
        txt(screen, f"{g.battle_target}이 싸움을 걸어왔다(숙명적인 싸움 이곳에 발을 들인 어쩌구저쩌구 희망을 어쩌구 저쩌구)", F14, BLACK, 20, HEIGHT - 130)
        cmds = ["싸운다", "가방", "포켓몬", "도망간다"]
        cmd_rects = []
        for i, cmd in enumerate(cmds):
            cx = WIDTH // 2 + (i % 2) * 240 + 20
            cy = HEIGHT - 150 + (i // 2) * 60 + 10
            r = pygame.Rect(cx, cy, 200, 48)
            btn(screen, r, cmd, F18, hover=r.collidepoint(mx, my))
            cmd_rects.append(r)
        return cmd_rects, None, None
    elif g.battle_state == "move":
        move_rects, back_r = draw_battle_moves(mx, my)
        return None, move_rects, back_r
    elif g.battle_state == "bag":
        item_rects, back_r = draw_battle_items(mx, my)
        return None, item_rects, back_r
    elif g.battle_state == "change":
        poket_rects, back_r = draw_battle_poket_change(mx ,my)
        return None, poket_rects, back_r
    else:
        pygame.draw.rect(screen, WHITE, (0, HEIGHT - 160, WIDTH, 160))
        pygame.draw.rect(screen, BLACK, (0, HEIGHT - 160, WIDTH, 160), 3)
        if g.battle_msgs:
            txt(screen, g.battle_msgs[0], F18, BLACK, 20, HEIGHT - 120)
        txt(screen, "▼", F12, GRAY, WIDTH - 20, HEIGHT - 20, right=True)
        return None, None, None

def draw_choice(cname, desc, types, cy, mx, my):
    screen.fill(BG)
    panel(screen, WIDTH // 2 - 300, HEIGHT // 2 - 180, 600, 360, PANEL2, alpha=235, radius=16, border=True)
    txt(screen, f"{cname}으로 선택하시겠습니까?", F18, BLACK, WIDTH // 2, HEIGHT // 2 - 148, center=True)
    pygame.draw.line(screen, BORDER, (WIDTH // 2 - 270, HEIGHT // 2 - 122), (WIDTH // 2 + 270, HEIGHT // 2 - 122), 1)
    if desc:
        for i, line in enumerate(desc.split("\n")):
            txt(screen, line, F14, BLACK, WIDTH // 2, HEIGHT // 2 - 95 + i * 26, center=True)
    if types:
        for i, t in enumerate(types):
            txt(screen, t, F14, TYPE_COLORS.get(t, GRAY), WIDTH // 2, HEIGHT // 2 + 60 + i * 26, center=True)
    mx, my = pygame.mouse.get_pos()
    ok_r = pygame.Rect(WIDTH // 2 - 160, HEIGHT // 2 + 120, 140, 40)
    no_r = pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2 + 120, 140, 40)
    btn(screen, ok_r, "선택하기", F14, hover=ok_r.collidepoint(mx, my))
    btn(screen, no_r, "조금 더 고민하기", F14, hover=no_r.collidepoint(mx, my))
    return ok_r, no_r

def draw_book(cy):
    panel(screen, 10, cy, WIDTH - 20, HEIGHT - cy - 62, PANEL, alpha=180, radius=10, border=BORDER)
    txt(screen, f"관동 도감  {len(g.discovered)}/{TOTAL}", F18, ACCENT, WIDTH // 2, cy + 18, center=True)
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
        found = pid in g.discovered
        panel(screen, x, y, CARD_W, CARD_H, (40, 60, 100) if found else (28, 28, 36), alpha=220, radius=10, border=BORDER)
        txt(screen, f"#{pid}", F12, GRAY if found else (50, 50, 60), x + 10, y + 8)
        img_x = x + CARD_W // 2 - IMG_SIZE // 2
        img_y = y + 30
        if found:
            preload(pid)
            img = get_img(pid)
            if img:
                screen.blit(img, (img_x, img_y))
            txt(screen, get_korean_name(pid), F12, WHITE, x + CARD_W // 2, y + CARD_H - 22, center=True)
        else:
            preload(pid)
            sil = get_silhouette(pid)
            if sil:
                screen.blit(sil, (img_x, img_y))
            else:
                pygame.draw.rect(screen, (40, 40, 50), (img_x, img_y, IMG_SIZE, IMG_SIZE), border_radius=6)
                txt(screen, "?", F24, DARK_GRAY, img_x + IMG_SIZE // 2, img_y + IMG_SIZE // 2, center=True)
            txt(screen, "???", F12, DARK_GRAY, x + CARD_W // 2, y + CARD_H - 22, center=True)
    screen.set_clip(None)

running = True
while running:
    mx, my = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEWHEEL:
            if g.view == "book":
                book_scroll = max(0, book_scroll - event.y * 30)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if g.scene == "title":
                bs, bl, bq = draw_title()
                if bs.collidepoint(mx, my):
                    g.start()
                    scene_start = pygame.time.get_ticks()
                if bl.collidepoint(mx,my):
                    g.start()
                    g.load()
                    for pid in g.poket_list:
                        threading.Thread(target=_bg_load, args=(pid,), daemon=True).start()
            elif g.scene == "first":
                for pid, cx in [(4, 300), (7, 500), (1, 700)]:
                    ball_rect = _pokeball.get_rect(center=(cx, HEIGHT // 2 + 20))
                    if ball_rect.collidepoint(mx, my):
                        g.poket = pid
                        _bg_load_sync(pid)
                        choice_name = name_cache.get(pid, str(pid))
                        choice_desc = get_desc(pid)
                        choice_types = get_types_ko(pid)
                        g.scene = "choice"
            elif g.scene == "choice":
                ok_r, no_r = draw_choice(choice_name, choice_desc, choice_types, 108, mx, my)
                if ok_r.collidepoint(mx, my):
                    g.discovered.add(g.poket)
                    stats = get_stats(g.poket)
                    lv = 5
                    moves = get_my_moves(g.poket, lv)
                    growth_rate = get_growth_rate(g.poket)
                    g.poket_list[g.poket] = {
                        "lv": lv,
                        "stat": stats,
                        "hp": calc_hp(stats["hp"], lv),
                        "max_hp": calc_hp(stats["hp"], lv),
                        "moves": moves,
                        "exp": exp_for_level(growth_rate, lv),
                        "growth_rate": growth_rate,
                    }
                    g.scene = "main"
                if no_r.collidepoint(mx, my):
                    g.scene = "first"
            elif g.scene == "main":
                for r, key in tab_rects:
                    if r.collidepoint(mx, my):
                        g.view = None if g.view == key else key
                        map_selected = None
                        if g.view == "gym":
                            for trainer_name in TRY:
                                preload_trainer_data(trainer_name)
                if g.view == "map":
                    if map_ok_r and map_ok_r.collidepoint(mx, my):
                        g.current_location = map_selected
                        map_selected = None
                        if(g.current_location == "3번도로"):
                            info = GYM["회색체육관"]
                            if not info.get("cleared"):
                                g.notify("웅이 먼저 이기고 오세요", BLACK)
                                g.current_location = "황토마을"
                    elif map_no_r and map_no_r.collidepoint(mx, my):
                        map_selected = None
                    else:
                        reachable = set(MAP_NODES[g.current_location]["conn"])
                        for name, r in map_node_rects.items():
                            if r.collidepoint(mx, my) and name in reachable:
                                map_selected = name
                                break
                if g.view == "shop":
                    for r, cname in item_li:
                        if r.collidepoint(mx, my):
                            if ITEM_LIST[cname]["money"] <= g.money:
                                g.buy_item(cname)
                                g.money -= ITEM_LIST[cname]["money"]
                                print("샀다!")
                if g.view == "wild":
                    b = draw_wild(108, mx, my)
                    if b.collidepoint(mx, my):
                        result = g.find_poket(g.current_location)
                        if result:
                            kind, value = result
                            g.battle_type = kind
                            if kind == "pokemon":
                                _bg_load_sync(value)
                                g.battle_pid = value
                                g.battle_target = name_cache.get(value, str(value))
                            else:
                                g.battle_pid = None
                                g.battle_target = value
                            g.scene = "battle_choice"
                if g.view == "team":
                    have_pids, team_rects = draw_team(108, mx, my)
                    for i, pid in enumerate(have_pids):
                        col = i % 3
                        row = i // 3
                        r = pygame.Rect(30 + col * 150, 108 + 44 + row * 110, 120, 96)
                        if r.collidepoint(mx, my):
                            if pid in g.team:
                                g.team.pop(pid)
                            elif len(g.team) < 6:
                                g.team[pid] = g.poket_list[pid]
                    team_keys = list(g.team.keys())
                    for i, r in enumerate(team_rects):
                        if r.collidepoint(mx, my) and i < len(team_keys):
                            g.team.pop(team_keys[i])
                if g.view == "save":
                    g.save()
                    g.view = None
                if g.view == "bag":
                    bag_rect = draw_bag(108, mx,my)
                    for r, cname in bag_rect:
                        if r.collidepoint(mx,my):
                            g.pending_item = cname
                            g.scene = "item_select"
                if g.view == "gym":
                    gym_rect = draw_gym(108,mx, my)
                    for r,cname in gym_rect:
                        if r.collidepoint(mx,my):
                            info = GYM[cname]
                            g.battle_type = "trainer"
                            g.battle_target = info["leader"]
                            g.scene = "battle_choice"
            elif g.scene == "item_select":
                poket_rects, back_r = draw_item_poket_select(108, mx, my)
                if back_r.collidepoint(mx, my):
                    g.pending_item = None
                    g.scene = "main"
                else:
                    for r, pid in poket_rects:
                        if r.collidepoint(mx, my):
                            item_used = g.pending_item
                            g.pending_item = None
                            g.scene = "main"
                            g.use_item_in_bag(item_used, pid)
                            g.item.remove(item_used)
                            if g.scene == "main" and g.pending_evolution:
                                from_pid, to_pid = g.pending_evolution
                                g.pending_evolution = None
                                evo_from_pid = from_pid
                                evo_to_pid = to_pid
                                evo_start = pygame.time.get_ticks()
                                _bg_load_sync(to_pid)
                                g.scene = "evolution"
                            break
            elif g.scene == "battle_choice":
                ok_r, no_r = draw_battle_choice(108, mx, my)
                if ok_r.collidepoint(mx, my):
                    if(g.battle_type == "pokemon"):
                        if len(g.team) > 0:
                            lv = random.randint(2, 4)
                            g.battle_level = lv
                            stats = get_stats(g.battle_pid)
                            g.battle_max_hp = calc_hp(stats["hp"], lv)
                            g.battle_hp = g.battle_max_hp
                            g.battle_attack = calc_stat(stats["attack"], lv)
                            g.battle_defense = calc_stat(stats["defense"], lv)
                            g.battle_sp_attack = calc_stat(stats["special-attack"], lv)
                            g.battle_sp_defense = calc_stat(stats["special-defense"], lv)
                            g.battle_speed = calc_stat(stats["speed"], lv)
                            g.my_pid = list(g.team.keys())[0]
                            my_lv = g.team[g.my_pid]["lv"]
                            my_stats = g.team[g.my_pid]["stat"]
                            g.my_level = my_lv
                            g.my_max_hp = calc_hp(my_stats["hp"], my_lv)
                            g.my_hp = g.team[g.my_pid]["hp"]
                            g.my_attack = calc_stat(my_stats["attack"], my_lv)
                            g.my_defense = calc_stat(my_stats["defense"], my_lv)
                            g.my_sp_attack = calc_stat(my_stats["special-attack"], my_lv)
                            g.my_sp_defense = calc_stat(my_stats["special-defense"], my_lv)
                            g.my_speed = calc_stat(my_stats["speed"], my_lv)
                            g.my_moves = g.poket_list[g.my_pid]["moves"]
                            g.battle_state = "command"
                            g.battle_msgs = []
                            g.scene = "battle_poket"
                    else:
                        if len(g.team) > 0:
                            trainer_pool = TRY.get(g.battle_target, {}).get("pid", {})
                            if not trainer_pool:
                                g.notify(f"{g.battle_target}은(는) 이미 쓰러뜨렸습니다.", GRAY)
                                g.scene = "main"
                            else:
                                pid, info = next(iter(trainer_pool.items()))
                                lv = info["lv"]
                                g.battle_pid = pid
                                _bg_load_sync(pid)
                                g.battle_level = lv
                                stats = get_stats(g.battle_pid)
                                g.battle_max_hp = calc_hp(stats["hp"], lv)
                                g.battle_hp = g.battle_max_hp
                                g.battle_attack = calc_stat(stats["attack"], lv)
                                g.battle_defense = calc_stat(stats["defense"], lv)
                                g.battle_sp_attack = calc_stat(stats["special-attack"], lv)
                                g.battle_sp_defense = calc_stat(stats["special-defense"], lv)
                                g.battle_speed = calc_stat(stats["speed"], lv)
                                g.battle_moves = get_trainer_moves(info.get("moves", []))
                                g.my_pid = list(g.team.keys())[0]
                                my_lv = g.team[g.my_pid]["lv"]
                                my_stats = g.team[g.my_pid]["stat"]
                                g.my_level = my_lv
                                g.my_max_hp = calc_hp(my_stats["hp"], my_lv)
                                g.my_hp = g.team[g.my_pid]["hp"]
                                g.my_attack = calc_stat(my_stats["attack"], my_lv)
                                g.my_defense = calc_stat(my_stats["defense"], my_lv)
                                g.my_sp_attack = calc_stat(my_stats["special-attack"], my_lv)
                                g.my_sp_defense = calc_stat(my_stats["special-defense"], my_lv)
                                g.my_speed = calc_stat(my_stats["speed"], my_lv)
                                g.my_moves = g.poket_list[g.my_pid]["moves"]
                                g.battle_state = "command"
                                g.battle_msgs = []
                                g.scene = "battle_try"
                if no_r and no_r.collidepoint(mx, my):
                    g.scene = "main"
            elif g.scene == "battle_poket":
                cmd_rects, move_rects, back_r = draw_battle(mx, my)
                if g.battle_state == "command" and cmd_rects:
                    if cmd_rects[0].collidepoint(mx, my):
                        g.battle_state = "move"
                    if cmd_rects[1].collidepoint(mx,my):
                        g.battle_state = "bag"
                    if cmd_rects[2].collidepoint(mx, my):
                        g.battle_state = "change"
                    if cmd_rects[3].collidepoint(mx, my):
                        g.poket_list[g.my_pid]["hp"] = g.my_hp
                        g.scene = "main"
                elif g.battle_state == "move" and move_rects:
                    if back_r and back_r.collidepoint(mx, my):
                        g.battle_state = "command"
                    for i, r in enumerate(move_rects):
                        if r.collidepoint(mx, my) and i < len(g.my_moves):
                            do_player_turn(i)
                elif g.battle_state == "bag":
                    item_rects, back_r = draw_battle_items(mx, my)
                    if back_r and back_r.collidepoint(mx, my):
                        g.battle_state = "command"
                    for r, cname in item_rects:
                        if r.collidepoint(mx,my):
                            g.use_item(cname)
                elif g.battle_state == "msg":
                    if g.battle_msgs:
                        g.battle_msgs.pop(0)
                    if not g.battle_msgs:
                        if g.battle_after == "win":
                            g.poket_list[g.my_pid]["hp"] = g.my_hp
                            g.battle_state = "command"
                            if g.pending_evolution:
                                from_pid, to_pid = g.pending_evolution
                                g.pending_evolution = None
                                evo_from_pid = from_pid
                                evo_to_pid = to_pid
                                evo_start = pygame.time.get_ticks()
                                _bg_load_sync(to_pid)
                                g.scene = "evolution"
                            else:
                                g.scene = "main"
                        elif g.battle_after == "lose":
                            g.poket_list[g.my_pid]["hp"] = 0
                            g.battle_state = "command"
                            g.scene = "main"
                        else:
                            g.battle_state = g.battle_after
                elif g.battle_state == "change":
                    poket_rects, back_r = draw_battle_poket_change(mx, my)
                    if back_r and back_r.collidepoint(mx,my):
                        g.battle_state = "command"
                    for r, cname in poket_rects:
                        if r.collidepoint(mx, my) and cname != g.my_pid:
                            g.poket_list[g.my_pid]["hp"] = g.my_hp
                            g.my_pid = cname
                            my_lv = g.team[cname]["lv"]
                            my_stats = g.team[cname]["stat"]
                            g.my_level = my_lv
                            g.my_max_hp = calc_hp(my_stats["hp"], my_lv)
                            g.my_hp = g.team[cname]["hp"]
                            g.my_attack = calc_stat(my_stats["attack"], my_lv)
                            g.my_defense = calc_stat(my_stats["defense"], my_lv)
                            g.my_sp_attack = calc_stat(my_stats["special-attack"], my_lv)
                            g.my_sp_defense = calc_stat(my_stats["special-defense"], my_lv)
                            g.my_speed = calc_stat(my_stats["speed"], my_lv)
                            g.my_moves = g.poket_list[cname]["moves"]

                            msgs = []
                            enemy_power = random.randint(35, 55)
                            dmg = calc_damage(g.battle_level, g.battle_attack, g.my_defense, enemy_power)
                            g.my_hp = max(0, g.my_hp - dmg)
                            msgs.append(f"{get_korean_name(g.my_pid)}(으)로 교체했다!")
                            msgs.append(f"야생의 {g.battle_target}이(가) 공격했다!")
                            msgs.append(f"내 포켓몬에게 {dmg}의 데미지!")
                            if g.my_hp <= 0:
                                msgs.append(f"{get_korean_name(g.my_pid)}이(가) 쓰러졌다!")
                                g.battle_after = "lose"
                            else:
                                g.battle_after = "command"
                            g.battle_msgs = msgs
                            g.battle_state = "msg"
            elif g.scene == "battle_try":
                cmd_rects, move_rects, back_r = draw_battle_trianer(mx ,my)
                if g.battle_state == "command" and cmd_rects:
                    if cmd_rects[0].collidepoint(mx,my):
                        g.battle_state = "move"
                    if (cmd_rects[1]).collidepoint(mx,my):
                        g.battle_state = "bag"
                    if cmd_rects[2].collidepoint(mx, my):
                        g.battle_state = "change"
                    if cmd_rects[3].collidepoint(mx, my):
                        g.poket_list[g.my_pid]["hp"] = g.my_hp
                        g.scene = "main"
                elif g.battle_state == "move" and move_rects:
                    if back_r and back_r.collidepoint(mx,my):
                        g.battle_state = "command"
                    for i, r in enumerate(move_rects):
                        if r.collidepoint(mx, my) and i < len(g.my_moves):
                            do_player_turn_try(i)
                elif g.battle_state == "bag":
                    item_rects, back_r = draw_battle_items(mx, my)
                    if back_r and back_r.collidepoint(mx, my):
                        g.battle_state = "command"
                    for r, cname in item_rects:
                        if r.collidepoint(mx,my):
                            g.use_item(cname)
                elif g.battle_state == "msg":
                    if g.battle_msgs:
                        g.battle_msgs.pop(0)
                    if not g.battle_msgs:
                        if g.battle_after == "next_poket":
                            g.battle_state = "command"
                        elif g.battle_after == "trainer_win":
                            g.poket_list[g.my_pid]["hp"] = g.my_hp
                            mark_gym_cleared(g.battle_target)
                            g.battle_state = "command"
                            if g.pending_evolution:
                                from_pid, to_pid = g.pending_evolution
                                g.pending_evolution = None
                                evo_from_pid = from_pid
                                evo_to_pid = to_pid
                                evo_start = pygame.time.get_ticks()
                                _bg_load_sync(to_pid)
                                g.scene = "evolution"
                            else:
                                g.scene = "main"
                        elif g.battle_after == "lose":
                            g.poket_list[g.my_pid]["hp"] = 0
                            g.battle_state = "command"
                            g.scene = "main"
                        else:
                            g.battle_state = g.battle_after
                elif g.battle_state == "change":
                    poket_rects, back_r = draw_battle_poket_change(mx, my)
                    if back_r and back_r.collidepoint(mx,my):
                        g.battle_state = "command"
                    for r, cname in poket_rects:
                        if r.collidepoint(mx, my) and cname != g.my_pid:
                            g.poket_list[g.my_pid]["hp"] = g.my_hp
                            g.my_pid = cname
                            my_lv = g.team[cname]["lv"]
                            my_stats = g.team[cname]["stat"]
                            g.my_level = my_lv
                            g.my_max_hp = calc_hp(my_stats["hp"], my_lv)
                            g.my_hp = g.team[cname]["hp"]
                            g.my_attack = calc_stat(my_stats["attack"], my_lv)
                            g.my_defense = calc_stat(my_stats["defense"], my_lv)
                            g.my_sp_attack = calc_stat(my_stats["special-attack"], my_lv)
                            g.my_sp_defense = calc_stat(my_stats["special-defense"], my_lv)
                            g.my_speed = calc_stat(my_stats["speed"], my_lv)
                            g.my_moves = g.poket_list[cname]["moves"]

                            msgs = []
                            msgs.append(f"{get_korean_name(g.my_pid)}(으)로 교체했다!")
                            msgs.extend(trainer_move_attack(g.battle_target))
                            if g.my_hp <= 0:
                                msgs.append(f"{get_korean_name(g.my_pid)}이(가) 쓰러졌다!")
                                g.battle_after = "lose"
                            else:
                                g.battle_after = "command"
                            g.battle_msgs = msgs
                            g.battle_state = "msg"
            elif g.scene == "move_learn":
                slot_rects, skip_r = draw_move_learn(mx, my)
                if skip_r.collidepoint(mx, my):
                    g.pending_move = None
                    g.move_learn_pid = None
                    g.scene = g.return_scene
                for i, r in enumerate(slot_rects):
                    if r.collidepoint(mx, my) and i < len(g.poket_list[g.move_learn_pid]["moves"]):
                        g.poket_list[g.move_learn_pid]["moves"][i] = g.pending_move
                        g.pending_move = None
                        g.move_learn_pid = None
                        g.scene = g.return_scene
            elif g.scene == "evolution":
                elapsed = pygame.time.get_ticks() - evo_start
                if elapsed >= 4000:
                    old_info = g.poket_list.pop(evo_from_pid)
                    new_stats = get_stats(evo_to_pid)
                    old_info["stat"] = new_stats
                    old_info["max_hp"] = calc_hp(new_stats["hp"], old_info["lv"])
                    g.discovered.add(evo_to_pid)
                    g.poket_list[evo_to_pid] = old_info
                    if evo_from_pid in g.team:
                        g.team[evo_to_pid] = g.team.pop(evo_from_pid)
                    if g.my_pid == evo_from_pid:
                        g.my_pid = evo_to_pid
                        g.my_max_hp = old_info["max_hp"]
                        g.my_attack = calc_stat(new_stats["attack"], old_info["lv"])
                        g.my_defense = calc_stat(new_stats["defense"], old_info["lv"])
                        g.my_sp_attack = calc_stat(new_stats["special-attack"], old_info["lv"])
                        g.my_sp_defense = calc_stat(new_stats["special-defense"], old_info["lv"])
                        g.my_speed = calc_stat(new_stats["speed"], old_info["lv"])
                    g.scene = "main"
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if g.scene == "choice":
                g.scene = "first"
            elif g.scene == "main" and map_selected:
                map_selected = None
            elif g.scene == "battle_choice":
                g.scene = "main"
            elif g.scene == "battle_poket":
                g.scene = "main"
            elif g.scene == "item_select":
                g.pending_item = None
                g.scene = "main"

    if g.scene == "title":
        draw_title()
    elif g.scene == "first":
        draw_fist(108, mx, my)
    elif g.scene == "choice":
        draw_choice(choice_name, choice_desc, choice_types, 108, mx, my)
    elif g.scene == "main":
        tab_rects = draw_main(get_bg(g.current_location))
    elif g.scene == "item_select":
        draw_item_poket_select(108, mx, my)
    elif g.scene == "battle_choice":
        draw_battle_choice(108, mx, my)
    elif g.scene == "battle_poket":
        draw_battle(mx, my)
    elif g.scene == "move_learn":
        draw_move_learn(mx, my)
    elif g.scene == "evolution":
        draw_evolution()

    if g.notification and g.notif_timer >0:
        msg, color = g.notification
        ns = F18.render(msg, True, WHITE)
        nw = ns.get_width() + 24
        nx = WIDTH // 2 - nw // 2
        ny = HEIGHT - 60
        alpha = min(255, g.notif_timer * 4)
        s = pygame.Surface((nw, 40), pygame.SRCALPHA)
        pygame.draw.rect(s, (*color, alpha), (0, 0, nw, 40), border_radius=8)
        screen.blit(s, (nx, ny))
        screen.blit(ns, (nx + 12, ny + 8))
        g.notif_timer -= 1
        if g.notif_timer == 0:
            g.notification = None

    pygame.display.flip()
    clock.tick(60)

pygame.quit()