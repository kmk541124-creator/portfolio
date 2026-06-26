import sys
import json
import os
import pygame
from datetime import datetime

pygame.init()

screen_width  = 900
screen_height = 620
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("d-day 캘린더")

DATA_FILE = "dday_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

dday_data = load_data()

def leap(year):
    return (year % 400 == 0) or (year % 4 == 0 and year % 100 != 0)

def month_days(month, year):
    dic = {1:31, 2:28, 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31}
    if month == 2 and leap(year):
        return 29
    return dic[month]

def valid(year, month, day):
    if not (1 <= month <= 12):
        return False
    if not (1 <= day <= month_days(month, year)):
        return False
    return True

now = datetime.now()

FONT_PATH = os.path.expanduser("~/Library/Fonts/온글잎 긍정.ttf")

mu_font    = pygame.font.Font(FONT_PATH, 38)
small_font = pygame.font.Font(FONT_PATH, 22)
tiny_font  = pygame.font.Font(FONT_PATH, 15)

Black = (0,   0,   0  )
Red   = (200, 0,   0  )
White = (255, 255, 255)
Gray  = (200, 200, 200)
LGray = (240, 240, 240)
DGray = (120, 120, 120)
Blue  = (50,  80,  210)
Green = (30,  160, 80 )
Accent= (70,  130, 230)
YellowBg = (255, 240, 100)
TodayBg  = (220, 235, 255)
HoverBg  = (230, 230, 230)

y = []
m = []
d = []

def ddays(year, month, day):
    total = 0
    for y_ in range(1, year):
        total += 366 if leap(y_) else 365
    for m_ in range(1, month):
        total += month_days(m_, year)
    total += day
    return total

def day(year, month, day):
    target = ddays(year, month, day)
    today  = ddays(now.year, now.month, now.day)
    return target - today

def first_weekday(year, month):
    if month < 3:
        month += 12
        year -= 1
    k = year % 100
    j = year // 100
    h = (1 + (13 * (month + 1)) // 5 + k + k // 4 + j // 4 + 5 * j) % 7
    return (h + 5) % 7

def date_key(year, month, day):
    return f"{year:04d}-{month:02d}-{day:02d}"

CAL_X   = 20
CAL_Y   = 110
CELL_W  = 100
CELL_H  = 72
PANEL_X = 720
PANEL_Y = 100
PANEL_W = 165
PANEL_H = 420

view_year  = now.year
view_month = now.month

showing_input  = False
input_error    = ""
label_mode     = False
label_text     = ""
selected_key   = None
hover_day      = None

def draw_rounded(surface, color, rect, radius=8, border=0, bcol=Black):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border:
        pygame.draw.rect(surface, bcol, rect, border, border_radius=radius)

def draw_calendar():
    screen.fill((245, 246, 250))

    title = mu_font.render(f"{view_year}년  {view_month}월", True, Black)
    screen.blit(title, (CAL_X + 42, 42))

    prev_rect = pygame.Rect(CAL_X, 42, 36, 36)
    next_rect = pygame.Rect(CAL_X + 46 + title.get_width(), 42, 36, 36)
    draw_rounded(screen, LGray, prev_rect, 6)
    draw_rounded(screen, LGray, next_rect, 6)
    screen.blit(small_font.render("◀", True, DGray), (prev_rect.x + 6, prev_rect.y + 7))
    screen.blit(small_font.render("▶", True, DGray), (next_rect.x + 6, next_rect.y + 7))

    days_kor = ["월", "화", "수", "목", "금", "토", "일"]
    for i, dn in enumerate(days_kor):
        col = Red if i == 6 else (Blue if i == 5 else DGray)
        hdr = small_font.render(dn, True, col)
        x = CAL_X + i * CELL_W + CELL_W // 2 - hdr.get_width() // 2
        screen.blit(hdr, (x, CAL_Y - 26))

    fd    = first_weekday(view_year, view_month)
    mdays = month_days(view_month, view_year)

    for d_ in range(1, mdays + 1):
        col_idx = (fd + d_ - 1) % 7
        row_idx = (fd + d_ - 1) // 7
        cx = CAL_X + col_idx * CELL_W
        cy = CAL_Y + row_idx * CELL_H
        cell = pygame.Rect(cx, cy, CELL_W - 2, CELL_H - 2)

        is_today = (view_year == now.year and view_month == now.month and d_ == now.day)
        key      = date_key(view_year, view_month, d_)
        has_dday = key in dday_data
        is_hover = (hover_day == d_)
        is_sel   = (selected_key == key)

        bg = White
        if is_today:  bg = TodayBg
        if has_dday:  bg = YellowBg
        if is_hover:  bg = HoverBg
        if is_sel:    bg = (180, 220, 255)

        bw  = 2 if (is_sel or is_today) else 1
        bcl = Accent if (is_sel or is_today) else Gray
        draw_rounded(screen, bg, cell, 6, bw, bcl)

        day_col = Red if col_idx == 6 else (Blue if col_idx == 5 else Black)
        screen.blit(small_font.render(str(d_), True, day_col), (cx + 6, cy + 5))

        if has_dday:
            diff = day(view_year, view_month, d_)
            if diff > 0:
                label = f"D-{diff}"
            elif diff < 0:
                label = f"D+{abs(diff)}"
            else:
                label = "D-Day!"
            screen.blit(tiny_font.render(label, True, (160, 80, 0)), (cx + 4, cy + 26))
            name = dday_data[key].get("name", "")
            if name:
                screen.blit(tiny_font.render(name[:6], True, DGray), (cx + 4, cy + 44))

    draw_rounded(screen, (248, 248, 252), pygame.Rect(PANEL_X, PANEL_Y, PANEL_W, PANEL_H), 10, 1, Gray)
    screen.blit(small_font.render("D-Day 목록", True, Black), (PANEL_X + 10, PANEL_Y + 10))

    py = PANEL_Y + 42
    for k in sorted(dday_data.keys()):
        if py > PANEL_Y + PANEL_H - 30:
            break
        ky, km, kd_ = int(k[:4]), int(k[5:7]), int(k[8:10])
        diff = day(ky, km, kd_)
        dl   = f"D-{diff}" if diff > 0 else (f"D+{abs(diff)}" if diff < 0 else "D-Day!")
        name = dday_data[k].get("name", "")
        screen.blit(tiny_font.render(f"{k}  {dl}", True, (100, 80, 0)), (PANEL_X + 10, py))
        screen.blit(tiny_font.render(name if name else "(이름없음)", True, DGray), (PANEL_X + 10, py + 16))
        del_rect = pygame.Rect(PANEL_X + PANEL_W - 24, py, 18, 18)
        draw_rounded(screen, (240, 180, 180), del_rect, 4)
        screen.blit(tiny_font.render("X", True, Red), (del_rect.x + 4, del_rect.y + 2))
        py += 38

    hint = tiny_font.render("Enter: 날짜이동  ←→: 월이동  클릭: D-Day등록", True, DGray)
    screen.blit(hint, (CAL_X, screen_height - 24))

    return prev_rect, next_rect

def draw_input():
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 140))
    screen.blit(overlay, (0, 0))

    box = pygame.Rect(250, 200, 400, 200)
    draw_rounded(screen, White, box, 12, 2, Accent)
    screen.blit(small_font.render("날짜 입력 (YYYY.MM.DD) 후 Enter", True, DGray), (box.x + 20, box.y + 18))

    year_str  = "".join(y).ljust(4, "_")
    month_str = "".join(m).ljust(2, "_")
    day_str   = "".join(d).ljust(2, "_")
    txt = mu_font.render(f"{year_str}.{month_str}.{day_str}", True, Black)
    screen.blit(txt, (box.x + 30, box.y + 60))

    if input_error:
        screen.blit(small_font.render(input_error, True, Red), (box.x + 20, box.y + 115))

    screen.blit(small_font.render("Enter: 이동   ESC: 취소", True, DGray), (box.x + 20, box.y + 158))

def draw_label():
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    screen.blit(overlay, (0, 0))

    box = pygame.Rect(270, 230, 360, 140)
    draw_rounded(screen, White, box, 12, 2, Green)
    screen.blit(small_font.render("이름 입력 후 Enter (선택사항)", True, DGray), (box.x + 14, box.y + 14))
    screen.blit(mu_font.render(label_text + "|", True, Black), (box.x + 14, box.y + 52))
    screen.blit(small_font.render("ESC: 이름 없이 저장", True, DGray), (box.x + 14, box.y + 100))

def get_day_at(mx, my):
    fd    = first_weekday(view_year, view_month)
    mdays = month_days(view_month, view_year)
    for d_ in range(1, mdays + 1):
        col_idx = (fd + d_ - 1) % 7
        row_idx = (fd + d_ - 1) // 7
        cx = CAL_X + col_idx * CELL_W
        cy = CAL_Y + row_idx * CELL_H
        if cx <= mx < cx + CELL_W - 2 and cy <= my < cy + CELL_H - 2:
            return d_
    return None


def get_del_at(mx, my):
    py = PANEL_Y + 42
    for k in sorted(dday_data.keys()):
        if py > PANEL_Y + PANEL_H - 30:
            break
        del_rect = pygame.Rect(PANEL_X + PANEL_W - 24, py, 18, 18)
        if del_rect.collidepoint(mx, my):
            return k
        py += 38
    return None

clock = pygame.time.Clock()

while True:
    mx, my = pygame.mouse.get_pos()
    hover_day = get_day_at(mx, my) if not showing_input and not label_mode else None

    prev_rect, next_rect = draw_calendar()
    if showing_input:
        draw_input()
    elif label_mode:
        draw_label()
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_data(dday_data)
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            key_name = pygame.key.name(event.key)

            if label_mode:
                if key_name == "return":
                    dday_data[selected_key] = {"name": label_text}
                    save_data(dday_data)
                    label_mode = False
                    label_text = ""
                elif key_name == "escape":
                    dday_data[selected_key] = {"name": ""}
                    save_data(dday_data)
                    label_mode = False
                    label_text = ""
                elif key_name == "backspace":
                    label_text = label_text[:-1]
                elif len(label_text) < 10:
                    label_text += event.unicode
                continue

            if showing_input:
                if key_name == "escape":
                    showing_input = False
                    y.clear(); m.clear(); d.clear()
                    input_error = ""
                    continue

                if '0' <= key_name <= '9':
                    if len(y) < 4:
                        y.append(key_name)
                    elif len(m) < 2:
                        if len(m) == 0 and key_name not in ('0', '1'):
                            pass
                        elif len(m) == 1:
                            candidate = int(m[0] + key_name)
                            if 1 <= candidate <= 12:
                                m.append(key_name)
                        else:
                            m.append(key_name)
                    elif len(d) < 2:
                        year_int  = int("".join(y)) if len(y) == 4 else 2000
                        month_int = int("".join(m)) if len(m) == 2 else 1
                        max_day   = month_days(month_int, year_int)
                        if len(d) == 0 and int(key_name) > 3:
                            pass
                        elif len(d) == 1:
                            candidate = int(d[0] + key_name)
                            if 1 <= candidate <= max_day:
                                d.append(key_name)
                        else:
                            d.append(key_name)

                elif key_name == "backspace":
                    if len(d) > 0:   d.pop()
                    elif len(m) > 0: m.pop()
                    elif len(y) > 0: y.pop()

                elif key_name == "return":
                    if len(y) == 4 and len(m) == 2 and len(d) == 2:
                        year_int  = int("".join(y))
                        month_int = int("".join(m))
                        day_int   = int("".join(d))
                        if not valid(year_int, month_int, day_int):
                            input_error = "잘못된 날짜입니다"
                        else:
                            view_year  = year_int
                            view_month = month_int
                            showing_input = False
                            input_error   = ""
                            y.clear(); m.clear(); d.clear()
                continue

            if key_name in ("return", "space"):
                showing_input = True
                y.clear(); m.clear(); d.clear()
                input_error = ""
            elif key_name == "left":
                view_month -= 1
                if view_month < 1:
                    view_month = 12
                    view_year -= 1
            elif key_name == "right":
                view_month += 1
                if view_month > 12:
                    view_month = 1
                    view_year += 1

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if showing_input or label_mode:
                continue
            if prev_rect.collidepoint(mx, my):
                view_month -= 1
                if view_month < 1:
                    view_month = 12; view_year -= 1
                continue
            if next_rect.collidepoint(mx, my):
                view_month += 1
                if view_month > 12:
                    view_month = 1; view_year += 1
                continue
            dk = get_del_at(mx, my)
            if dk:
                del dday_data[dk]
                save_data(dday_data)
                if selected_key == dk:
                    selected_key = None
                continue
            clicked = get_day_at(mx, my)
            if clicked:
                key = date_key(view_year, view_month, clicked)
                if key in dday_data:
                    del dday_data[key]
                    save_data(dday_data)
                    selected_key = None
                else:
                    selected_key = key
                    label_mode   = True
                    label_text   = ""

    clock.tick(60)