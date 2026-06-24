import pygame
import sys
import random
import math
import ollama
import threading
import json
import os

pygame.init()
WIDTH, HEIGHT = 1000, 680
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("개발자 메이커")
clock = pygame.time.Clock()

def load_font(size):
    return pygame.font.Font("/System/Library/Fonts/AppleSDGothicNeo.ttc", size)

F32 = load_font(32)
F24 = load_font(24)
F18 = load_font(18)
F14 = load_font(14)
F12 = load_font(12)

BG = (10, 14, 26)
PANEL = (20, 26, 50)
PANEL2 = (28, 34, 62)
BORDER = (60, 80, 160)
ACCENT = (80, 160, 255)
GREEN = (60, 200, 120)
RED = (220, 70, 70)
YELLOW = (220, 190, 60)
ORANGE = (220, 130, 50)
PURPLE = (160, 80, 220)
WHITE = (230, 235, 255)
GRAY = (120, 130, 160)
DARK_GRAY = (50, 55, 80)
CYAN = (60, 210, 210)
PINK = (220, 100, 160)
GOLD = (255, 215, 0)
BLUE = (0, 233, 255)

SAVE_FILE = "savegame.json"
PROMPT_FILE = "friend_prompt.json"

def load_friend_prompt():
    if os.path.exists(PROMPT_FILE):
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

def txt(surface, text, font, color, x, y, center=False, right=False):
    s = font.render(str(text), True, color)
    r = s.get_rect()
    if center: r.center = (x, y)
    elif right: r.right = x; r.top = y
    else: r.topleft = (x, y)
    surface.blit(s, r)
    return r

def panel(surface, x, y, w, h, color=None, alpha=210, radius=10, border=None):
    color = color or PANEL
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(s, (*color, alpha), (0, 0, w, h), border_radius=radius)
    surface.blit(s, (x, y))
    if border:
        pygame.draw.rect(surface, border, (x, y, w, h), 1, border_radius=radius)

def bar(surface, x, y, w, h, val, mx, col, bg=(30, 35, 60)):
    pygame.draw.rect(surface, bg, (x, y, w, h), border_radius=3)
    if mx > 0:
        fw = max(0, int(w * min(val, mx) / mx))
        if fw:
            pygame.draw.rect(surface, col, (x, y, fw, h), border_radius=3)
    pygame.draw.rect(surface, BORDER, (x, y, w, h), 1, border_radius=3)

def btn(surface, rect, label, font, active=True, hover=False):
    bc = PANEL2 if not active else ((50, 90, 180) if not hover else (70, 120, 220))
    fc = GRAY if not active else WHITE
    panel(surface, rect.x, rect.y, rect.w, rect.h, bc, alpha=230, radius=8, border=ACCENT if active else DARK_GRAY)
    txt(surface, label, font, fc, rect.centerx, rect.centery, center=True)

STATS = ["코딩", "수학", "영어", "체력", "멘탈", "사교성"]
STAT_COLOR = {
    "코딩": ACCENT, "수학": CYAN, "영어": GREEN,
    "체력": RED, "멘탈": PURPLE, "사교성": PINK,
}
MAJORS = {
    "프론트엔드": {"주력": ["코딩", "사교성"], "색": (255, 160, 60)},
    "백엔드": {"주력": ["코딩", "수학"], "색": (60, 160, 255)},
    "게임": {"주력": ["코딩", "멘탈"], "색": (160, 80, 220)},
    "앱": {"주력": ["코딩", "사교성"], "색": (60, 200, 160)},
}

SHOP_LIST = {
    "에너지 드링크" : {"desc":"피로도를 줄일 수 있습니다", "money": 20000, "stats":"피로도", "eff": -25, "색":GOLD, "buy":False},
    "수학 문제집" : {"desc":"수학 문제집을 사서 수학 능력치를 올릴 수 있습니다", "money": 30000, "stats": "수학", "eff": 25, "색":GOLD, "buy":False},
    "스프링부트 책" : {"desc":"스프링 부트 공부로 코딩 능력을 올릴 수 있습니다", "money": 25000, "stats": "코딩", "eff": 25, "색":GOLD, "buy":False},
    "비타 500" : {"desc":"비타민 섭취로 인해 체력이 상승합니다", "money": 20000, "stats": "체력", "eff": 20, "색":GOLD, "buy":False},
    "클로드" : {"desc":"클로드 요금제 결제로 코딩이 상승하빈다", "money": 50000, "stats": "코딩", "eff": 50, "색":GOLD, "buy":False},
    "김영한의 강의" : {"desc":"김영한 강의를 봐서 코딩능력치가 대폭 상승하빈다", "money": 600000, "stats": "코딩", "eff": 200, "색":GOLD, "buy":False},
}

CLUBS = {
    "프로세스": {"desc": "개발 동아리", "효과": {"코딩": 3, "수학": 2}, "색": ACCENT},
    "모디": {"desc": "자격증 동아리", "효과": {"수학": 3, "코딩": 2}, "색": PINK},
    "두카미": {"desc": "봉사 동아리", "효과": {"코딩": 2, "사교성": 10}, "색": CYAN},
    "바인드": {"desc": "도담도담 동아리", "효과": {"코딩": 3, "수학": 5, "사교성": 5}, "색": CYAN},
    "잉클리스 바이브": {"desc": "영어 동아리", "효과": {"영어": 10, "사교성": 5}, "색": (255, 215, 0)},
    "삼디": {"desc": "3D 그래픽 게임 제작 동아리", "효과": {"코딩": 2, "멘탈": 2, "체력": 1}, "색": ORANGE},
}
ACTIVITIES_BASE = [
    ("알고리즘 공부", "학습", 2, 18, {"코딩": 9, "수학": 4, "체력": -6}, "공부", 0),
    ("영어 자습", "학습", 1, 10, {"영어": 7, "체력": -3}, "토익 문제집 풀기", 0),
    ("수학 심화 공부", "학습", 2, 14, {"수학": 10, "멘탈": -3, "체력": -6}, "수학 공부", 0),
    ("전공 교과 선행", "학습", 2, 16, {"코딩": 7, "수학": 5, "체력": -5}, "전공 교과", 0),
    ("해커톤 참가", "프로젝트", 1, 26, {"코딩": 10, "사교성": 9, "멘탈": -6, "체력": -12}, "팀플+포트폴리오", 0),
    ("친구랑 공부하기", "프로젝트", 2, 12, {"코딩": 6, "사교성": 10, "체력": -4}, "친구랑 공부하기", 0),
    ("개인 프로젝트", "프로젝트", 2, 15, {"코딩": 11, "멘탈": -4, "체력": -8}, "포트폴리오 한 줄 추가", 0),
    ("봉사 활동", "봉사", 1, 15, {"사교성": 10, "체력": -3}, "봉사활동을 한다", -10),
    ("운동장 달리기", "휴식", 1, 0, {"체력": 13, "멘탈": 4}, "조깅", 0),
    ("독서", "휴식", 1, 4, {"멘탈": 7, "영어": 2}, "도서관에서 책 읽기", 0),
    ("휴식", "휴식", 1, -18, {"체력": 16, "멘탈": 14}, "피로 빠르게 회복", 0),
    ("친구랑 게임", "휴식", 1, 5, {"멘탈": 10, "사교성": 6}, "기숙사에서", 0),
]
PENALTY_ACTIVITIES = [
    ("교내 봉사", "생활", 1, 8, {"사교성": 2, "체력": -3}, "벌점 정리", -10),
]
NARSYA_ACTIVITIES = [
    ("나르샤: 기획서 작성", "나르샤", 1, 10, {"코딩": 4, "사교성": 8, "멘탈": -2, "체력": -4}, "팀 프로젝트 기획", 0),
    ("나르샤: 프로토타입 개발", "나르샤", 2, 20, {"코딩": 12, "사교성": 6, "멘탈": -5, "체력": -10}, "구현", 0),
    ("나르샤: 발표 준비", "나르샤", 1, 8, {"영어": 4, "사교성": 10, "멘탈": -3, "체력": -5}, "팀 발표 자료 제작", 0),
    ("나르샤: 팀 회의", "나르샤", 1, 5, {"사교성": 8, "코딩": 3, "체력": -3}, "방향성 논의", 0),
    ("나르샤: 디버깅 & 리뷰", "나르샤", 2, 16, {"코딩": 10, "수학": 3, "멘탈": -4, "체력": -8}, "코드 품질 향상", 0),
]
SV_ACTIVITIES = [
    ("실리콘밸리: 업무 적응", "실리콘밸리", 1, 30, {"코딩": 8, "영어": 10, "멘탈": -8, "체력": -10}, "첫 주 온보딩", 0),
    ("실리콘밸리: 코드 기여", "실리콘밸리", 2, 25, {"코딩": 15, "영어": 6, "멘탈": -6, "체력": -14}, "실제 프로덕션 작업", 0),
    ("실리콘밸리: 1대1 미팅", "실리콘밸리", 1, 10, {"영어": 8, "사교성": 10, "멘탈": 3, "체력": -2}, "멘토 개발자와 대화", 0),
    ("실리콘밸리: 현지 탐방", "실리콘밸리", 1, -18, {"멘탈": 12, "영어": 5, "체력": -4}, "쉬면서 문화 체험", 0),
]
RANDOM_EVENTS = [
    ("친구의 버그 해결을 도와줬다", {"코딩": 5, "사교성": 3}, 0, {"decs":"친구가 버그 해결을 요구한다", "yes":"수락한다","no":"거절한다"} ),
    ("심자2의 연속으로 몸 안좋아졌다", {"체력": -8, "멘탈": -5}, 0, {"decs":"심자 2를 신청할까?", "yes":"신청한다","no":"신청하지 않는다"}),
    ("선생님께 칭찬을 받았다", {"멘탈": 10}, 0, {"decs":"선생님이 부탁하신다", "yes":"도와준다","no":"바쁘다고한다"}),
    ("대회에서 입상했다", {"코딩": 10, "멘탈": 8}, 0, {"decs":"대회에 나갈까?", "yes":"나간다","no":"나가지 않는다"}),
    ("감기에 걸렸다", {"체력": -10, "멘탈": -3}, 0, {"decs":"에어컨 틀고잘까?", "yes":"튼다","no":"예약 맞추고 잔다"}),
    ("좋은 강의를 봤다", {"코딩": 6}, 0, {"decs":"강의가 필요할것 같디", "yes":"찾아본다","no":"그딴거 필요없다"}),
    ("팀 프로젝트가 성공했다", {"사교성": 8, "코딩": 5}, 0, {"decs":"친구들이 프로젝트를 하잔다", "yes":"같이 한다","no":"필요 없다"}),
    ("슬럼프가 왔다", {"멘탈": -12, "코딩": -3}, 0, {"decs":"슬럼프가 올 것같다 (선택지를 어떻게 할지 모르겠다)", "yes":"슬럼프가 온다","no":"오지 않는다"}),
    ("소마고 선배와 멘토링을 했다", {"코딩": 7, "멘탈": 6}, 0, {"decs":"멘토링을 할까?", "yes":"한다","no":"하지 않는다"}),
    ("실수로 만들던 프로젝트를 날렸다", {"멘탈": -8, "코딩": 3}, 0, {"decs":"프로젝트 저장을 할까?", "yes":"저장한다","no":"하지 않는다"}),
    ("수업 중 졸다가 걸렸다", {"멘탈": -3}, 5, {"decs":"수업시간에 너무 잠이 온다 잘까?", "yes":"잔다","no":"자지 않는다"}),
    ("기숙사 청소 불량 받았다", {"멘탈": -2}, 1, {"decs":"기숙사 청소를 할까?", "yes":"하지 않는다","no":"한다"}),
    ("복도에서 뛰다가 적발됐다", {}, 5, {"decs":"내 친구가 나 때리고 튀었다", "yes":"쫓아간다","no":"쫓아가지 않는다"}),
    ("배달음식 먹다가 걸렸다", {"멘탈": -5}, 15, {"decs":"급식이 맛이 없다", "yes":"배달음식을 시킨다","no":"시키지 않는다"}),
    ("실습실 및 기숙사 장비를 파손했다", {"멘탈": -8}, 20, {"decs":"친구랑 장난을 칠까?", "yes":"장난친다","no":"장난치지 않는다"}),
    ("기숙사 청소 상점을 받았다", {"멘탈": +9}, -1, {"decs":"기숙사 청소를 열심히 할까?", "yes":"열심히 한다","no":"열심히 하지 않는다"}),
    ("친구와 심한 다툼이 생겼다", {"사교성": -5, "멘탈": -5}, 10,{"decs":"친구랑 의견이 안맞아 말싸움이 겪해진다", "yes":"나도 덩달아 언성을 높힌다","no":"언성을 높히지 마라"}),
    ("제출 기한을 어겼다", {"코딩": -3}, 0, {"decs":"제출시간이 생각나지 않는다", "yes":"제출기간이 생각났다!","no":"생각나지 않는다..."}),
    ("선생님께 반항했다가 벌점을 받았다", {"멘탈": -5}, 15, {"decs":"선생님의 의견이 마음에 안든다", "yes":"반박한다","no":"그냥 받아들인다"}),
]

PENALTY_EXPEL = 50
EXAM_MONTHS = {5, 7, 17, 19, 29, 31}

ENDINGS = [
    ("실리콘밸리 입사", lambda s, sv, p: sv and s["코딩"] >= 400 and s["영어"] >= 400 and s["사교성"] >= 400,
    "실리콘밸리 인턴 경험으로 인해 실리콘밸리의 회사에 입사했습니다", GOLD),
    ("대기업 취업", lambda s, sv, p: s["코딩"] >= 300 and s["영어"] >= 200 and s["사교성"] >= 300,
    "대기업에 취업했습니다", ACCENT),
    ("스타트업 취업", lambda s, sv, p: s["코딩"] >= 200 and s["사교성"] >= 200,
    "스타트업에 취업했습니다", YELLOW),
    ("대학 진학", lambda s, sv, p: s["수학"] >= 400 and s["영어"] >= 400 and s["코딩"] <= 200,
    "취업을 하지 않고 수능을 봐서 대학에 진학했습니다", PURPLE),
    ("미취업", lambda s, sv, p: True,
    "취업에 실패했습니다(열심히 하세요)", GRAY),
]

NARSYA_MONTHS = {8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24}
ENGLISH = {4, 16, 28}
SV_APPLY_MONTH = 28
SV_INTERN_START = 31
SV_INTERN_END = 33
NARSYA_END_MONTH = 25

prompt_data = load_friend_prompt()
FRIEND_NAME = prompt_data.get("friend_name", "김시영")

chat_lock = threading.Lock()

def build_friend_system(g):
    p = load_friend_prompt()
    stat_lines = "\n".join([f"  {k}: {v}/500" for k, v in g.stats.items()])
    year = g.current_year()
    month = (g.month - 1) % 12 + 1
    system = p["system"].format(
        friend_name=p.get("friend_name", "김시영"),
        year=year,
        month=month,
        major=g.major or "미정",
        club=g.club or "없음",
        narsya="진행 중" if g.is_narsya_period() else "해당 없음",
        sv="인턴 중" if g.is_sv_intern_period() else ("경험 있음" if g.sv_intern else "없음"),
        penalty=g.penalty,
        stats=stat_lines
    )
    return system, p

class FriendChat:
    def __init__(self):
        self.log = []
        self.history = []
        self.streaming_buf = ""
        self.is_thinking = False
        self.input_text = ""
        self.scroll_offset = 0

    def to_dict(self):
        return {"log": self.log, "history": self.history}

    def from_dict(self, d):
        self.log = d.get("log", [])
        self.history = d.get("history", [])

    def send(self, text, g):
        if not text.strip() or self.is_thinking:
            return
        self.log.append({"role": "user", "text": text})
        self.history.append({"role": "user", "content": text})
        self.is_thinking = True
        threading.Thread(target=self._ask, args=(text, g), daemon=True).start()

    def _ask(self, user_input, g):
        system_text, p = build_friend_system(g)
        msgs = [{"role": "system", "content": system_text}]
        for fs in p.get("few_shot", []):
            msgs.append({"role": fs["role"], "content": fs["content"]})
        for m in self.history[:-1]:
            msgs.append(m)
        msgs.append({"role": "user", "content": user_input})
        reply = ""
        try:
            model = p.get("model", "gemma3:12b")
            for chunk in ollama.chat(model=model, messages=msgs, stream=True):
                token = chunk["message"]["content"]
                reply += token
                with chat_lock:
                    self.streaming_buf = reply
        except Exception as e:
            reply = f"(연결 오류: {e})"
        self.history.append({"role": "assistant", "content": reply})
        with chat_lock:
            self.log.append({"role": "ai", "text": reply})
            self.streaming_buf = ""
            self.is_thinking = False

friend_chat = FriendChat()

def wrap_text(text, font, max_width):
    lines = []
    cur = ""
    for ch in text:
        test = cur + ch
        if font.size(test)[0] > max_width:
            lines.append(cur)
            cur = ch
        else:
            cur = test
    if cur:
        lines.append(cur)
    return lines

class Game:
    TOTAL_MONTHS = 36

    def __init__(self):
        self.scene = "title"
        self.t = 0
        self.notification = None
        self.notif_timer = 0

    def start(self):
        self.month = 1
        self.fatigue = 0
        self.stats = {s: 20 for s in STATS}
        self.stats["체력"] = 300
        self.stats["멘탈"] = 300
        self.history = []
        self.money = 0
        self.pending_event = None
        self.schedule = []
        self.item_list = []
        self.bag_list = []
        self.weeks_used = 0
        self.scene = "main"
        self.selected_act = None
        self.view = "schedule"
        self.club = None
        self.club_year = 0
        self.gamgi_stats = 5
        self.en_year = 0
        self.penalty = 0
        self._expel = False
        self.sv_applied = False
        self.en_applied = False
        self.gamgi = False
        self.heal_count = 0
        self.en_ing = False
        self.en_notiy = 0
        self.sv_intern = False
        self.narsya_notified = False
        self.sv_apply_notified = False
        self.narsya_result_done = False
        self.exam_done = set()
        self.major = None
        self.selected_ending = None
        self.act_scroll = 0
        friend_chat.__init__()
        self.notify("소마고에 입학했습니다! 3년 후 개발자가 되세요", GREEN)

    def save(self):
        data = {
            "month": self.month,
            "fatigue": self.fatigue,
            "stats": self.stats,
            "history": self.history,
            "club": self.club,
            "club_year": self.club_year,
            "money": self.money,
            "en_year": self.en_year,
            "penalty": self.penalty,
            "en_ing": self.en_ing,
            "gamgi_stats" : self.gamgi_stats,
            "item_list" : self.item_list,
            "heal_count": self.heal_count,
            "bag_list": self.bag_list,
            "gamgi": self.gamgi,
            "en_applied": self.en_applied,
            "en_notiy": self.en_notiy,
            "sv_applied": self.sv_applied,
            "sv_intern": self.sv_intern,
            "narsya_notified": self.narsya_notified,
            "sv_apply_notified": self.sv_apply_notified,
            "narsya_result_done": self.narsya_result_done,
            "exam_done": list(self.exam_done),
            "major": self.major,
            "friend_chat": friend_chat.to_dict(),
        }
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.notify("저장 완료", GREEN)

    def load(self):
        if not os.path.exists(SAVE_FILE):
            self.notify("저장 파일이 없습니다", RED)
            return False
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.month = data["month"]
        self.fatigue = data["fatigue"]
        self.stats = data["stats"]
        self.history = data["history"]
        self.club = data.get("club")
        self.club_year = data.get("club_year", 0)
        self.en_year = data.get("en_year", 0)
        self.money = data.get("money", 0)
        self.penalty = data.get("penalty", 0)
        self.gamgi_stats = data.get("gamgi_stats", 5)
        self.sv_applied = data.get("sv_applied", False)
        self.en_ing = data.get("en_ing", False)
        self.en_applied = data.get("en_applied", False)
        self.sv_intern = data.get("sv_intern", False)
        self.heal_count = data.get("heal_count", 0)
        self.gamgi = data.get("gamgi", False)
        self.narsya_notified = data.get("narsya_notified", False)
        self.sv_apply_notified = data.get("sv_apply_notified", False)
        self.narsya_result_done = data.get("narsya_result_done", False)
        self.exam_done = set(data.get("exam_done", []))
        self.en_notiy = data.get("en_notiy", 0)
        self.item_list = data.get("item_list", [])
        self.bag_list = data.get("bag_list",[])
        self.major = data.get("major")
        self.pending_event = None
        self.schedule = []
        self.weeks_used = 0
        self.selected_act = None
        self.view = "schedule"
        self._expel = False
        self.t = 0
        self.selected_ending = None
        self.act_scroll = 0
        if "friend_chat" in data:
            friend_chat.from_dict(data["friend_chat"])
        self.scene = "main"
        self.notify("불러오기 완료!", CYAN)
        return True

    def notify(self, msg, color=WHITE):
        self.notification = (msg, color)
        self.notif_timer = 240

    def clamp_stats(self):
        for k in self.stats:
            self.stats[k] = max(0, min(500, self.stats[k]))

    def current_year(self):
        return (self.month - 1) // 12 + 1

    def resolve_random_event(self, accept):
        ev = self.pending_event
        if accept:
            for stat, val in ev["eff"].items():
                self.stats[stat] = self.stats.get(stat, 0) + val
            self.clamp_stats()
            self.penalty += ev["penalty"]
            ev["revealed"] = True

    def can_change_club(self):
        return self.club is None or self.current_year() > self.club_year

    def can_change_en(self):
        return self.en_ing == False or self.current_year() > self.en_year

    def try_heal(self):
        if self.stats["체력"] >= 250:
            self.notify("감기가 나았습니다!", GREEN)
            self.gamgi = False
            self.heal_count = 0
            return False
        else:
            self.heal_count += 1
            return True

    def join_club(self, cname):
        self.club = cname
        self.club_year = self.current_year()

    def buy_item(self, cname):
        self.bag_list.append(cname)
        SHOP_LIST[cname]['buy'] = True
        print(self.bag_list)

    def use_item(self, cname):
        use = SHOP_LIST[cname]['stats']
        self.stats[use] += SHOP_LIST[cname]['eff']
        self.bag_list.remove(cname)
        SHOP_LIST[cname]['buy'] = False
        self.clamp_stats()

    def join_major(self, cname):
        self.major = cname

    def current_activities(self):
        acts = list(ACTIVITIES_BASE)
        if self.month in NARSYA_MONTHS:
            acts += NARSYA_ACTIVITIES
        if self.sv_intern and SV_INTERN_START <= self.month <= SV_INTERN_END:
            acts = SV_ACTIVITIES
        if self.penalty > 0:
            acts += PENALTY_ACTIVITIES
        return acts

    def apply_activity(self, act):
        name, cat, weeks, fat, effects, desc = act[:6]
        if self.weeks_used + weeks > 4:
            self.notify("이번 달 일정이 꽉 찼습니다", RED)
            return False
        if self.fatigue + fat > 100:
            self.notify("힘드니까 하지 마세요", RED)
            return False
        if self.en_ing and self.weeks_used + weeks > 3:
            self.notify("영어 회화로 인해 1주일은 사용할 수 없습니다", RED)
            return False
        self.schedule.append(act)
        self.weeks_used += weeks
        return True

    def remove_activity(self, act):
        if act in self.schedule:
            self.schedule.remove(act)
            self.weeks_used -= act[2]

    def end_month(self):
        total_fatigue = self.fatigue
        self.money += 30000
        for act in self.schedule:
            name, cat, weeks, fat, effects, desc = act[:6]
            total_fatigue += fat
            point = act[6] if len(act) == 7 else 0
            self.penalty += point
            if self.club:
                club_eff = CLUBS[self.club]["효과"]
                for stat, val in club_eff.items():
                    self.stats[stat] = self.stats.get(stat, 0) + val
            for stat, val in effects.items():
                self.stats[stat] = self.stats.get(stat, 0) + val
            self.history.append((self.month, name))
        self.fatigue = max(0, min(100, total_fatigue))
        if self.fatigue >= 80:
            self.stats["체력"] -= 10
            self.stats["멘탈"] -= 8
            self.notify("과로로 힘드니까 쉬세요", RED)
        elif self.fatigue >= 60:
            self.stats["체력"] -= 4
            self.notify("위험합니다", ORANGE)
        if self.gamgi:
            if self.try_heal():
                if self.stats["체력"] < 250:
                    self.gamgi_stats = 5
                if self.stats["체력"] < 150:
                    self.gamgi_stats = 10
                if self.stats["체력"] < 80:
                    self.gamgi_stats = 20
                self.notify(f"감기 때문에 체력과 멘탈이 {self.gamgi_stats}씩 감소합니다", RED)
                self.stats["체력"] -= self.gamgi_stats
                self.stats["멘탈"] -= self.gamgi_stats
        elif not self.gamgi and self.stats["체력"] <= 80:
            self.notify("감기에 걸리셨습니다 운동좀 하세요", RED)
            self.gamgi = True

        self.clamp_stats()
        if self.en_ing:
            self.stats["영어"] += 10
        if self.stats["멘탈"] < 50:
            ratio = self.stats["멘탈"] / 100.0
            for stat in ["코딩", "수학", "영어"]:
                penalty = int(self.stats[stat] * (1 - ratio) * 0.1)
                self.stats[stat] = max(0, self.stats[stat] - penalty)
        if random.random() < 0.25 and not (self.sv_intern and SV_INTERN_START <= self.month <= SV_INTERN_END):
            ev_name, ev_eff, ev_pen, ev_choice = random.choice(RANDOM_EVENTS)
            self.pending_event = {"type": "random", "name": ev_name, "eff": ev_eff, "penalty": ev_pen, "ch": ev_choice}
        self.month += 1
        self.schedule = []
        self.weeks_used = 0
        self.act_scroll = 0
        if self.penalty >= PENALTY_EXPEL:
            self.scene = "ending"
            self._expel = True
            return
        if self.month > self.TOTAL_MONTHS:
            self.scene = "ending_list"
            return
        self._check_special_events()
        if self.pending_event:
            self.scene = "event"
            return

    def _check_special_events(self):
        m = self.month
        if m in NARSYA_MONTHS and not self.narsya_notified:
            self.narsya_notified = True
            self.pending_event = {
                "type": "narsya_start",
                "name": "나르샤 프로젝트 시작",
                "eff": {},
                "desc": "1학년 2학기부터 나르샤 프로젝트가 시작됩니다.\n팀원들과 함께 나르샤 프로젝트를 실시 하세요\n활동 목록에 나르샤 관련 할일이 추가됩니다.",
            }
            self.scene = "event"
        elif m == NARSYA_END_MONTH and not self.narsya_result_done:
            self.narsya_result_done = True
            count = sum(1 for _, name in self.history if "나르샤" in name)
            if count >= 8:
                eff = {"코딩": 30, "사교성": 20, "멘탈": 10}
                desc = "나르샤를 열심히 했습니다! 스텟이 크게 올랐습니다"
            elif count >= 4:
                eff = {"코딩": 10, "사교성": 5}
                desc = "나르샤를 적당히 했습니다"
            else:
                eff = {"코딩": -30, "사교성": -20, "멘탈": -25}
                desc = "나르샤에 거의 참여하지 않았습니다. 스텟이 크게 깎였습니다"
            for stat, val in eff.items():
                self.stats[stat] = self.stats.get(stat, 0) + val
            self.clamp_stats()
            self.pending_event = {
                "type": "narsya_result",
                "name": "나르샤 프로젝트 결과",
                "eff": eff,
                "desc": desc,
            }
            self.scene = "event"
        elif m == SV_APPLY_MONTH and not self.sv_apply_notified:
            self.sv_apply_notified = True
            self.pending_event = {
                "type": "sv_apply",
                "name": "실리콘밸리 인턴 지원서 도착",
                "eff": {},
                "desc": "3학년 4월, 실리콘밸리 인턴십 지원 공고가 왔습니다.\n영어와 코딩 실력, 사교성을 쌓았다면 도전하세요\n여름방학(7~9월) 동안 실리콘밸리에서 인턴으로 일하게 됩니다.",
                "choice": True,
            }
            self.scene = "event"
        elif m in EXAM_MONTHS and m not in self.exam_done:
            self.exam_done.add(m)
            eng = self.stats.get("영어", 0)
            math_ = self.stats.get("수학", 0)
            eff = {}
            bad = False
            if eng < 100:
                eff["영어"] = -15
                eff["멘탈"] = eff.get("멘탈", 0) - 20
                bad = True
            if math_ < 100:
                eff["수학"] = -15
                eff["멘탈"] = eff.get("멘탈", 0) - 20
                bad = True
            if not bad:
                eff["멘탈"] = 15
                desc = "중간/기말 시험을 잘 봤습니다! 멘탈이 올랐습니다"
            else:
                desc = "중간/기말 성적이 안 좋습니다. 멘탈과 스텟이 깎였습니다"
            for stat, val in eff.items():
                self.stats[stat] = self.stats.get(stat, 0) + val
            self.clamp_stats()
            self.pending_event = {
                "type": "exam",
                "name": "중간/기말 시험 결과",
                "eff": eff,
                "desc": desc,
            }
            self.scene = "event"
        elif m in ENGLISH and self.current_year() > self.en_notiy:
            self.en_notiy = self.current_year()
            self.pending_event = {
                "type": "english",
                "name": "영어 회화 신청서 도착",
                "eff": {},
                "desc": "영어회화를 신청하여 영어 실력을 키워 보세요 영어 스텟이 매달 상승합니다.",
                "choice": True,
            }
            self.scene = "event"
        else:
            self.notify(f"{self.year_label()} 시작", ACCENT)

    def accept_sv(self):
        self.sv_applied = True
        if self.stats["코딩"] >= 350 and self.stats["영어"] >= 350 and self.stats["사교성"] >= 300:
            self.sv_intern = True
            self.notify("실리콘밸리 인턴십에 합격했습니다", GOLD)
        else:
            self.sv_intern = False
            self.notify("아쉽게도 불합격 하셨습니다", RED)

    def accept_en(self):
        self.en_applied = True
        self.en_ing = True
        self.en_year = self.current_year()
        self.notify("영어 회화를 시작하셨습니다", GOLD)

    def decline_sv(self):
        self.sv_applied = False
        self.notify("인턴십을 포기했습니다. 국내에서 실력을 쌓아요.", GRAY)

    def get_ending(self):
        if getattr(self, "_expel", False):
            return ("퇴학", "벌점이 50점을 넘어 퇴학 처리됐습니다", RED)
        if self.selected_ending is not None:
            title, cond, desc, color = ENDINGS[self.selected_ending]
            return title, desc, color
        sv = self.sv_intern
        p = self.penalty
        for title, cond, desc, color in ENDINGS:
            if cond(self.stats, sv, p):
                return title, desc, color
        return ENDINGS[-1][0], ENDINGS[-1][2], ENDINGS[-1][3]

    def year_label(self):
        y = (self.month - 1) // 12 + 1
        m = (self.month - 1) % 12 + 1
        return f"고{y} {m}월"

    def is_narsya_period(self):
        return self.month in NARSYA_MONTHS

    def is_sv_intern_period(self):
        return self.sv_intern and SV_INTERN_START <= self.month <= SV_INTERN_END

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
    txt(screen, "개발자 메이커", F32, ACCENT, WIDTH // 2, 120, center=True)
    txt(screen, "소마고 육성 시뮬레이션", F18, GRAY, WIDTH // 2, 165, center=True)
    panel(screen, WIDTH // 2 - 90, 200, 180, 180, PANEL2, alpha=200, radius=16, border=BORDER)
    txt(screen, "< 나 >", F14, GRAY, WIDTH // 2, 310, center=True)
    txt(screen, "소프트웨어마이스터고", F14, CYAN, WIDTH // 2, 340, center=True)
    txt(screen, "1학년 입학", F14, GRAY, WIDTH // 2, 360, center=True)
    mx, my = pygame.mouse.get_pos()
    btn_start = pygame.Rect(WIDTH // 2 - 100, 415, 200, 48)
    btn_load = pygame.Rect(WIDTH // 2 - 100, 473, 200, 48)
    btn_quit = pygame.Rect(WIDTH // 2 - 100, 531, 200, 48)
    btn(screen, btn_start, "새 게임", F18, hover=btn_start.collidepoint(mx, my))
    has_save = os.path.exists(SAVE_FILE)
    btn(screen, btn_load, "이어하기", F18, active=has_save, hover=has_save and btn_load.collidepoint(mx, my))
    btn(screen, btn_quit, "종료", F18, hover=btn_quit.collidepoint(mx, my))
    txt(screen, "개발자가 되기 위해 소마고에서 3년을 보내세요", F12, DARK_GRAY, WIDTH // 2, 593, center=True)
    return btn_start, btn_load, btn_quit

def draw_main():
    screen.fill(BG)
    g.t += 1
    mx, my = pygame.mouse.get_pos()
    panel(screen, 0, 0, WIDTH, 52, PANEL, alpha=240, radius=0)
    pygame.draw.line(screen, BORDER, (0, 52), (WIDTH, 52), 1)
    txt(screen, "개발자 메이커", F18, ACCENT, 18, 15)
    txt(screen, f"돈: {g.money}", F14, GOLD, 150, 17)
    if g.gamgi:
        txt(screen, f"감기에 걸리셨습니다 매달 체력 {g.gamgi_stats}씩 감소합니다", F14, RED, 200, 17)
    txt(screen, g.year_label(), F18, WHITE, WIDTH // 2, 26, center=True)
    m_color = MAJORS.get(g.major, {}).get("색", WHITE) if g.major and g.major != "풀스택" else WHITE
    if g.major:
        txt(screen, g.major, F14, m_color, WIDTH - 20, 10, right=True)
    if g.club:
        txt(screen, f"동아리: {g.club}", F12, CLUBS[g.club]["색"], WIDTH - 20, 32, right=True)
    if g.is_narsya_period():
        panel(screen, WIDTH // 2 + 60, 8, 130, 22, (80, 40, 10), alpha=200, radius=6, border=ORANGE)
        txt(screen, "나르샤 진행중", F12, ORANGE, WIDTH // 2 + 125, 19, center=True)
    if g.is_sv_intern_period():
        panel(screen, WIDTH // 2 + 60, 8, 150, 22, (10, 60, 30), alpha=200, radius=6, border=GOLD)
        txt(screen, "실리콘밸리 인턴중", F12, GOLD, WIDTH // 2 + 135, 19, center=True)
    prog = (g.month - 1) / g.TOTAL_MONTHS
    bar(screen, 0, 52, WIDTH, 6, prog, 1.0, ACCENT, bg=(20, 25, 50))
    tabs = [("스케줄", "schedule"), ("스탯", "status"), ("동아리", "club"),
            ("기록", "history"), ("전공", "major"), (f"💬{FRIEND_NAME}", "friend"), ("상점", "shop"), ("가방","bag")]
    tab_rects = []
    tab_w = (WIDTH - 20) // len(tabs)
    for i, (label, key) in enumerate(tabs):
        r = pygame.Rect(10 + i * tab_w, 66, tab_w - 4, 34)
        active = g.view == key
        bc = PANEL2 if not active else (40, 60, 130)
        border_c = PINK if key == "friend" and active else (ACCENT if active else DARK_GRAY)
        panel(screen, r.x, r.y, r.w, r.h, bc, alpha=220, radius=6, border=border_c)
        label_col = PINK if key == "friend" else (WHITE if active else GRAY)
        txt(screen, label, F12, label_col, r.centerx, r.centery, center=True)
        tab_rects.append((r, key))
    content_y = 108
    if g.view == "schedule":
        draw_schedule(content_y, mx, my)
    elif g.view == "status":
        draw_status(content_y)
    elif g.view == "club":
        draw_club(content_y, mx, my)
    elif g.view == "history":
        draw_history(content_y)
    elif g.view == "major":
        draw_major(content_y, mx, my)
    elif g.view == "friend":
        draw_friend_chat(content_y, mx, my)
    elif g.view == "shop":
        draw_shop(content_y, mx, my)
    elif g.view == "bag":
        draw_bag(content_y, mx, my)
    elif g.view == "event":
        draw_event_choice(content_y, mx, my)
    panel(screen, 0, HEIGHT - 52, WIDTH, 52, PANEL, alpha=220, radius=0)
    pygame.draw.line(screen, BORDER, (0, HEIGHT - 52), (WIDTH, HEIGHT - 52), 1)
    txt(screen, f"피로도: {g.fatigue}/100", F14,
        RED if g.fatigue >= 70 else ORANGE if g.fatigue >= 40 else GREEN, 20, HEIGHT - 36)
    bar(screen, 110, HEIGHT - 38, 120, 12, g.fatigue, 100,
        RED if g.fatigue >= 70 else ORANGE if g.fatigue >= 40 else GREEN)
    txt(screen, f"이번 달 여유: {4 - g.weeks_used}주", F14, CYAN, 260, HEIGHT - 36)
    pen_col = RED if g.penalty >= 40 else ORANGE if g.penalty >= 20 else GRAY
    if g.penalty >= 0:
        txt(screen, f"벌점: {g.penalty}/{PENALTY_EXPEL}", F14, pen_col, 430, HEIGHT - 36)
    else:
        txt(screen, f"상점: {g.penalty * -1}/{PENALTY_EXPEL}", F14, pen_col, 430, HEIGHT - 36)
    bar(screen, 510, HEIGHT - 38, 80, 12, g.penalty, PENALTY_EXPEL, pen_col)
    save_r = pygame.Rect(WIDTH - 310, HEIGHT - 46, 80, 38)
    btn(screen, save_r, "저장", F14, hover=save_r.collidepoint(mx, my))
    btn_end = pygame.Rect(WIDTH - 220, HEIGHT - 46, 205, 38)
    btn(screen, btn_end, "한 달 보내기 ▶", F14, active=True, hover=btn_end.collidepoint(mx, my))
    return tab_rects, btn_end, save_r

def draw_notification():
    if g.notif_timer > 0:
        g.notif_timer -= 1
        alpha = min(255, g.notif_timer * 4)
        msg, col = g.notification
        ns = pygame.Surface((WIDTH - 40, 34), pygame.SRCALPHA)
        pygame.draw.rect(ns, (*PANEL2, alpha), (0, 0, WIDTH - 40, 34), border_radius=8)
        screen.blit(ns, (20, HEIGHT - 95))
        s = F14.render(msg, True, col)
        s.set_alpha(alpha)
        screen.blit(s, (WIDTH // 2 - s.get_width() // 2, HEIGHT - 90))

def draw_ending_list():
    screen.fill(BG)
    g.t += 1
    random.seed(g.t // 6)
    for _ in range(20):
        px = random.randint(0, WIDTH)
        py = random.randint(0, HEIGHT)
        r = random.randint(1, 2)
        c = random.choice([ACCENT, CYAN, PURPLE, GRAY])
        pygame.draw.circle(screen, c, (px, py), r)
    txt(screen, "3년이 지났습니다", F32, WHITE, WIDTH // 2, 40, center=True)
    txt(screen, "달성한 엔딩을 선택해서 결말을 확인하세요", F14, GRAY, WIDTH // 2, 80, center=True)
    mx, my = pygame.mouse.get_pos()
    sv = g.sv_intern
    p = g.penalty
    btn_rects = []
    card_w = 880
    card_h = 80
    start_y = 110
    gap = 10
    for i, (title, cond, desc, color) in enumerate(ENDINGS):
        unlocked = cond(g.stats, sv, p)
        cy2 = start_y + i * (card_h + gap)
        hov = pygame.Rect(WIDTH // 2 - card_w // 2, cy2, card_w, card_h).collidepoint(mx, my) and unlocked
        bc = (40, 55, 90) if unlocked else (20, 22, 38)
        bdr = color if unlocked else DARK_GRAY
        panel(screen, WIDTH // 2 - card_w // 2, cy2, card_w, card_h, bc, alpha=220, radius=10, border=bdr)
        if unlocked:
            txt(screen, title, F18, color, WIDTH // 2 - card_w // 2 + 20, cy2 + 14)
            txt(screen, desc, F12, GRAY, WIDTH // 2 - card_w // 2 + 20, cy2 + 44)
        else:
            txt(screen, "???", F18, DARK_GRAY, WIDTH // 2 - card_w // 2 + 20, cy2 + 14)
            txt(screen, "조건 미달성", F12, DARK_GRAY, WIDTH // 2 - card_w // 2 + 20, cy2 + 44)
        btn_r = pygame.Rect(WIDTH // 2 + card_w // 2 - 120, cy2 + card_h // 2 - 18, 110, 36)
        btn(screen, btn_r, "선택하기", F14, active=unlocked, hover=hov)
        btn_rects.append((btn_r, i, unlocked))
    return btn_rects

def draw_friend_chat(cy, mx, my):
    CW = WIDTH - 20
    CH = HEIGHT - cy - 62
    panel(screen, 10, cy, CW, CH, PANEL, alpha=180, radius=10, border=PINK)
    header_h = 42
    panel(screen, 10, cy, CW, header_h, (40, 20, 50), alpha=220, radius=10, border=PINK)
    pygame.draw.circle(screen, PINK, (36, cy + 21), 12)
    txt(screen, FRIEND_NAME[0], F12, WHITE, 36, cy + 21, center=True)
    txt(screen, f"💬 {FRIEND_NAME} · 대구소마고 동기", F14, PINK, 56, cy + 14)
    if friend_chat.is_thinking:
        dots = "." * ((pygame.time.get_ticks() // 400) % 4)
        txt(screen, f"입력 중{dots}", F12, GRAY, 56, cy + 28)
    LOG_TOP = cy + header_h + 4
    INPUT_H = 44
    INPUT_Y = cy + CH - INPUT_H - 6
    LOG_H = INPUT_Y - LOG_TOP - 4
    pygame.draw.rect(screen, (15, 12, 25), (12, LOG_TOP, CW - 4, LOG_H), border_radius=6)
    with chat_lock:
        buf = friend_chat.streaming_buf
        log = list(friend_chat.log)
    items = list(log)
    if buf:
        items.append({"role": "ai", "text": buf})
    LINE_H = 20
    BUBBLE_PAD = 8
    MSG_W = CW - 80
    all_rendered = []
    for item in items:
        is_user = item["role"] == "user"
        color = (180, 220, 255) if is_user else (255, 200, 230)
        bc = (30, 60, 100) if is_user else (60, 25, 50)
        lines = wrap_text(item["text"], F12, MSG_W - BUBBLE_PAD * 2)
        if not lines:
            lines = [""]
        bh = len(lines) * LINE_H + BUBBLE_PAD * 2
        all_rendered.append((is_user, color, bc, lines, bh))
    total_h = sum(r[4] + 10 for r in all_rendered)
    max_scroll = max(0, total_h - LOG_H)
    friend_chat.scroll_offset = min(friend_chat.scroll_offset, max_scroll)
    clip_surf = pygame.Surface((CW - 4, LOG_H), pygame.SRCALPHA)
    draw_y = -friend_chat.scroll_offset
    for (is_user, color, bc, lines, bh) in all_rendered:
        if draw_y + bh > 0 and draw_y < LOG_H:
            bx = CW - 4 - (MSG_W - 20) - 10 if is_user else 10
            pygame.draw.rect(clip_surf, (*bc, 210), (bx, int(draw_y), MSG_W - 20, bh), border_radius=8)
            pygame.draw.rect(clip_surf, (*color, 80), (bx, int(draw_y), MSG_W - 20, bh), 1, border_radius=8)
            for li, line in enumerate(lines):
                ls = F12.render(line, True, color)
                clip_surf.blit(ls, (bx + BUBBLE_PAD, int(draw_y) + BUBBLE_PAD + li * LINE_H))
        draw_y += bh + 10
    screen.blit(clip_surf, (12, LOG_TOP))
    pygame.draw.rect(screen, (20, 15, 35), (12, INPUT_Y, CW - 4, INPUT_H), border_radius=8)
    pygame.draw.rect(screen, PINK, (12, INPUT_Y, CW - 4, INPUT_H), 2, border_radius=8)
    display_text = friend_chat.input_text + "|"
    ts = F14.render(display_text, True, WHITE)
    max_tw = CW - 140
    if ts.get_width() > max_tw:
        clip_r = pygame.Rect(ts.get_width() - max_tw, 0, max_tw, ts.get_height())
        screen.blit(ts, (22, INPUT_Y + (INPUT_H - ts.get_height()) // 2), area=clip_r)
    else:
        screen.blit(ts, (22, INPUT_Y + (INPUT_H - ts.get_height()) // 2))
    send_r = pygame.Rect(CW - 70, INPUT_Y + 7, 60, INPUT_H - 14)
    btn(screen, send_r, "전송", F12, hover=send_r.collidepoint(mx, my))
    if max_scroll > 0:
        scroll_ratio = friend_chat.scroll_offset / max_scroll if max_scroll else 0
        sb_h = max(30, int(LOG_H * LOG_H / total_h))
        sb_y = LOG_TOP + int((LOG_H - sb_h) * scroll_ratio)
        pygame.draw.rect(screen, DARK_GRAY, (WIDTH - 22, LOG_TOP, 6, LOG_H), border_radius=3)
        pygame.draw.rect(screen, GRAY, (WIDTH - 22, sb_y, 6, sb_h), border_radius=3)
    return send_r

def draw_schedule(cy, mx, my):
    acts = g.current_activities()
    panel(screen, 10, cy, 440, HEIGHT - cy - 62, PANEL, alpha=180, radius=10, border=BORDER)
    txt(screen, "활동 선택", F14, GRAY, 20, cy + 10)
    if g.is_sv_intern_period():
        txt(screen, "실리콘밸리 인턴 활동만 가능", F12, GOLD, 100, cy + 12)
    elif g.is_narsya_period():
        txt(screen, "나르샤 활동 추가됨", F12, ORANGE, 100, cy + 12)

    ROW_H = 34
    visible_top = cy + 35
    visible_bot = HEIGHT - 64
    visible_h = visible_bot - visible_top
    max_scroll = max(0, len(acts) * ROW_H - visible_h)
    g.act_scroll = min(g.act_scroll, max_scroll)

    act_rects = []
    clip_surf = pygame.Surface((432, visible_h), pygame.SRCALPHA)
    for i, act in enumerate(acts):
        name, cat, weeks, fat, effects, desc = act[:6]
        ry = i * ROW_H - g.act_scroll
        if ry + ROW_H < 0 or ry > visible_h:
            act_rects.append(None)
            continue
        r_screen = pygame.Rect(14, visible_top + ry, 432, 30)
        hov = r_screen.collidepoint(mx, my)
        sel = g.selected_act == i
        bc = (50, 70, 130) if sel else ((35, 45, 80) if hov else PANEL2)
        cat_colors = {"학습": CYAN, "프로젝트": GREEN, "나르샤": ORANGE, "실리콘밸리": GOLD, "휴식": PURPLE}
        pygame.draw.rect(clip_surf, bc, (0, ry, 432, 30), border_radius=6)
        border_c = ACCENT if sel else (cat_colors.get(cat, BORDER) if hov else DARK_GRAY)
        pygame.draw.rect(clip_surf, border_c, (0, ry, 432, 30), 1, border_radius=6)
        cat_color = cat_colors.get(cat, WHITE)
        cs = F12.render(f"[{cat}]", True, cat_color)
        clip_surf.blit(cs, (6, ry + 9))
        ns = F14.render(name, True, WHITE)
        clip_surf.blit(ns, (72, ry + 7))
        ws = F12.render(f"{weeks}주", True, GRAY)
        clip_surf.blit(ws, (270, ry + 9))
        fc = RED if fat > 0 else GREEN
        fs2 = F12.render(f"피로{fat:+}", True, fc)
        clip_surf.blit(fs2, (310, ry + 9))
        sc = F12.render(f"상점{act[6] * -1:+}", True, BLUE)
        clip_surf.blit(sc, (370, ry + 9))
        act_rects.append(r_screen)
    screen.blit(clip_surf, (14, visible_top))

    if max_scroll > 0:
        sb_ratio = g.act_scroll / max_scroll
        sb_h = max(30, int(visible_h * visible_h / (len(acts) * ROW_H)))
        sb_y = visible_top + int((visible_h - sb_h) * sb_ratio)
        pygame.draw.rect(screen, DARK_GRAY, (448, visible_top, 6, visible_h), border_radius=3)
        pygame.draw.rect(screen, GRAY, (448, sb_y, 6, sb_h), border_radius=3)

    rx = 460
    panel(screen, rx, cy, WIDTH - rx - 10, HEIGHT - cy - 62, PANEL, alpha=180, radius=10, border=BORDER)
    txt(screen, "이번 달 스케줄", F14, GRAY, rx + 10, cy + 10)
    txt(screen, f"({g.weeks_used}/4주)", F12, CYAN, rx + 130, cy + 12)
    for wi in range(4):
        bx = rx + 10 + wi * 125
        used = wi < g.weeks_used
        bc = (40, 60, 110) if used else (25, 30, 55)
        panel(screen, bx, cy + 34, 118, 20, bc, alpha=200, radius=4, border=ACCENT if used else DARK_GRAY)
        label = f"{wi + 1}주차" + (" v" if used else "")
        txt(screen, label, F12, WHITE if used else DARK_GRAY, bx + 59, cy + 44, center=True)
    sy = cy + 64
    if g.schedule:
        for idx, act in enumerate(g.schedule):
            name, cat, weeks, fat, effects, desc = act[:6]
            if sy + 52 > HEIGHT - 64:
                break
            panel(screen, rx + 8, sy, WIDTH - rx - 26, 50, PANEL2, alpha=220, radius=8, border=GREEN)
            txt(screen, name, F14, WHITE, rx + 14, sy + 5)
            txt(screen, desc, F12, GRAY, rx + 14, sy + 24)
            eff_x = rx + 14
            for stat, val in effects.items():
                col = GREEN if val > 0 else RED
                txt(screen, f"{stat}{val:+}", F12, col, eff_x, sy + 38)
                eff_x += 62
            del_r = pygame.Rect(WIDTH - rx - 36, sy + 14, 20, 20)
            panel(screen, del_r.x, del_r.y, del_r.w, del_r.h, (100, 30, 30), alpha=200, radius=4)
            txt(screen, "X", F12, WHITE, del_r.centerx, del_r.centery, center=True)
            sy += 56
    else:
        txt(screen, "왼쪽에서 활동을 선택하세요", F14, DARK_GRAY, rx + 10, sy + 8)
        txt(screen, "한 달에 최대 4주 분량을 배정할 수 있습니다", F12, DARK_GRAY, rx + 10, sy + 30)
    if g.selected_act is not None and g.selected_act < len(acts):
        act = acts[g.selected_act]
        name, cat, weeks, fat, effects, desc = act[:6]
        dy = sy + 10
        if dy + 95 < HEIGHT - 64:
            panel(screen, rx + 8, dy, WIDTH - rx - 26, 95, (30, 25, 60), alpha=200, radius=8, border=ACCENT)
            txt(screen, name, F14, ACCENT, rx + 14, dy + 7)
            txt(screen, desc, F12, GRAY, rx + 14, dy + 26)
            txt(screen, f"기간 {weeks}주  피로 {fat:+}", F12, CYAN, rx + 14, dy + 44)
            ef_x = rx + 14
            for stat, val in effects.items():
                col = GREEN if val > 0 else RED
                txt(screen, f"{stat} {val:+}", F14, col, ef_x, dy + 62)
                ef_x += 78
            add_r = pygame.Rect(WIDTH - rx - 98, dy + 58, 80, 26)
            btn(screen, add_r, "추가하기", F12, hover=add_r.collidepoint(mx, my))
            return act_rects, add_r
    return act_rects, None

def draw_status(cy):
    panel(screen, 10, cy, WIDTH - 20, HEIGHT - cy - 62, PANEL, alpha=180, radius=10, border=BORDER)
    txt(screen, "스탯 현황", F18, ACCENT, WIDTH // 2, cy + 18, center=True)
    for i, stat in enumerate(STATS):
        val = g.stats[stat]
        col = STAT_COLOR[stat]
        bx = 40 if i < 3 else WIDTH // 2 + 20
        by = cy + 55 + (i % 3) * 80
        txt(screen, stat, F14, col, bx, by)
        txt(screen, str(val), F18, col, bx + 55, by - 4)
        grade = "S" if val >= 400 else "A" if val >= 300 else "B" if val >= 200 else "C" if val >= 100 else "D"
        grade_col = GOLD if grade == "S" else YELLOW if grade == "A" else WHITE if grade == "B" else GRAY if grade == "C" else RED
        txt(screen, grade, F14, grade_col, bx + 100, by)
        bar(screen, bx, by + 22, 360, 14, val, 500, col)
        txt(screen, f"{val}/500", F12, GRAY, bx + 368, by + 24)
    total = sum(g.stats.values())
    txt(screen, f"종합 점수: {total}/3000", F14, YELLOW, WIDTH // 2, cy + 305, center=True)
    m_color = MAJORS.get(g.major, {}).get("색", WHITE) if g.major else WHITE
    txt(screen, f"현재 전공 방향: {g.major or '미정'}", F14, m_color, WIDTH // 2, cy + 330, center=True)
    hints = []
    if g.stats["코딩"] >= 400: hints.append(("대기업 개발자 가능성", GREEN))
    if g.stats["영어"] >= 400: hints.append(("해외 취업 가능성", CYAN))
    if g.stats["사교성"] >= 300: hints.append(("스타트업 취업 가능성", YELLOW))
    if g.stats["수학"] >= 500: hints.append(("대학 진학 가능성", PURPLE))
    if g.stats["멘탈"] < 30: hints.append(("번아웃 위험", RED))
    if g.stats["체력"] < 30: hints.append(("건강 적신호", RED))
    if g.sv_intern: hints.append(("실리콘밸리 인턴 경험 보유", GOLD))
    if hints:
        txt(screen, "경로 분석:", F14, GRAY, WIDTH // 2, cy + 358, center=True)
        for j, (h, c) in enumerate(hints[:3]):
            txt(screen, h, F12, c, WIDTH // 2, cy + 378 + j * 20, center=True)

def draw_club(cy, mx, my):
    panel(screen, 10, cy, WIDTH - 20, HEIGHT - cy - 62, PANEL, alpha=180, radius=10, border=BORDER)
    txt(screen, "동아리 선택", F18, ACCENT, WIDTH // 2, cy + 18, center=True)
    txt(screen, "동아리에 가입하면 매달 스탯 보너스가 붙습니다. 학년이 올라가야 변경 가능.", F12, GRAY, WIDTH // 2, cy + 42, center=True)
    club_rects = []
    names = list(CLUBS.keys())
    for i, cname in enumerate(names):
        info = CLUBS[cname]
        cx2 = 30 + (i % 2) * 480
        cy2 = cy + 70 + (i // 2) * 160
        w, h = 450, 145
        selected = g.club == cname
        hov = pygame.Rect(cx2, cy2, w, h).collidepoint(mx, my)
        bc = (40, 60, 100) if selected else ((30, 40, 75) if hov else PANEL2)
        bdr = info["색"] if selected else (BORDER if hov else DARK_GRAY)
        panel(screen, cx2, cy2, w, h, bc, alpha=220, radius=12, border=bdr)
        txt(screen, cname, F18, info["색"], cx2 + 20, cy2 + 14)
        if selected:
            txt(screen, "가입중", F12, GREEN, cx2 + w - 80, cy2 + 16)
        txt(screen, info["desc"], F12, GRAY, cx2 + 20, cy2 + 46)
        txt(screen, "매달 보너스:", F12, GRAY, cx2 + 20, cy2 + 72)
        ex = cx2 + 110
        for stat, val in info["효과"].items():
            txt(screen, f"{stat} +{val}", F14, STAT_COLOR.get(stat, WHITE), ex, cy2 + 70)
            ex += 90
        r = pygame.Rect(cx2 + w - 110, cy2 + h - 42, 95, 30)
        if selected:
            can = g.can_change_club()
            btn(screen, r, "다음학년변경" if not can else "탈퇴불가", F12, active=False)
        else:
            can = g.can_change_club()
            btn(screen, r, "가입하기", F12, active=can, hover=can and hov)
        club_rects.append((r, cname, selected))
    return club_rects

def draw_bag(cy,mx,my):
    panel(screen, 10, cy, WIDTH - 20, HEIGHT - cy - 62, PANEL, alpha=180, radius=10, border=BORDER)
    txt(screen, "가방", F18, ACCENT, WIDTH // 2, cy + 18, center=True)
    txt(screen, "소지하고 있는 아이템 입니다", F12, GRAY, WIDTH // 2, cy + 42, center=True)
    names = g.bag_list
    bag_rect = []
    for  i, cname in enumerate(names):
        info = SHOP_LIST[cname]
        cx2 = 30 + (i % 2) * 480
        cy2 = cy + 70 + (i // 2) * 160
        w, h = 450, 145
        hov = pygame.Rect(cx2, cy2, w, h).collidepoint(mx, my)
        bc = (40, 60, 100)
        bdr = info["색"]
        panel(screen, cx2, cy2, w, h, bc, alpha=220, radius=12, border=bdr)
        txt(screen, cname, F18, info["색"], cx2 + 20, cy2 + 14)

        txt(screen, info["desc"], F12, GRAY, cx2 + 20, cy2 + 46)
        txt(screen, "사용시: ", F12, GRAY, cx2 + 20, cy2 + 72)
        ex = cx2 + 110

        txt(screen, f"{info['stats']} : {info['eff']}", F14, STAT_COLOR.get(info['stats'], WHITE), ex, cy2 + 70)
        ex += 90
        r = pygame.Rect(cx2 + w - 110, cy2 + h - 42, 95, 30)
        btn(screen, r, "사용하기", F12, active=True, hover=True and hov)
        bag_rect.append((r, cname))
    return bag_rect

def draw_history(cy):
    panel(screen, 10, cy, WIDTH - 20, HEIGHT - cy - 62, PANEL, alpha=180, radius=10, border=BORDER)
    txt(screen, "활동 기록", F18, ACCENT, WIDTH // 2, cy + 18, center=True)
    if not g.history:
        txt(screen, "아직 기록이 없습니다.", F14, DARK_GRAY, WIDTH // 2, cy + 80, center=True)
        return
    for i, (month, name) in enumerate(reversed(g.history[-20:])):
        y = (month - 1) // 12 + 1
        m = (month - 1) % 12 + 1
        hy = cy + 48 + i * 24
        if hy > HEIGHT - 70:
            break
        col = ACCENT if i == 0 else (WHITE if i < 3 else GRAY)
        txt(screen, f"고{y} {m:2}월", F12, CYAN, 25, hy)
        txt(screen, name, F14, col, 100, hy - 2)

def draw_major(cy, mx, my):
    panel(screen, 10, cy, WIDTH - 20, HEIGHT - cy - 62, PANEL, alpha=180, radius=10, border=BORDER)
    txt(screen, "전공 선택", F18, ACCENT, WIDTH // 2, cy + 18, center=True)
    major_list = []
    names = list(MAJORS.keys())
    for i, cname in enumerate(names):
        info = MAJORS[cname]
        cx2 = 30 + (i % 2) * 480
        cy2 = cy + 70 + (i // 2) * 160
        w, h = 450, 145
        selected = g.major == cname
        hov = pygame.Rect(cx2, cy2, w, h).collidepoint(mx, my)
        bc = (40, 60, 100) if selected else ((30, 40, 75) if hov else PANEL2)
        bdr = info["색"] if selected else (BORDER if hov else DARK_GRAY)
        panel(screen, cx2, cy2, w, h, bc, alpha=220, radius=12, border=bdr)
        txt(screen, cname, F18, info["색"], cx2 + 20, cy2 + 14)
        if selected:
            txt(screen, "선택중", F12, GREEN, cx2 + w - 80, cy2 + 16)
        txt(screen, "주력 전공:", F12, GRAY, cx2 + 20, cy2 + 72)
        ex = cx2 + 110
        for stat in info["주력"]:
            txt(screen, f"{stat}", F14, STAT_COLOR.get(stat, WHITE), ex, cy2 + 70)
            ex += 90
        r = pygame.Rect(cx2 + w - 110, cy2 + h - 42, 95, 30)
        if selected:
            btn(screen, r, "선택됨", F12, active=False)
        else:
            btn(screen, r, "선택하기", F12, active=True, hover=hov)
        major_list.append((r, cname, selected))
    return major_list

def draw_shop(cy, mx, my):
    panel(screen, 10, cy, WIDTH - 20, HEIGHT - cy - 62, PANEL, alpha=180, radius=10, border=BORDER)
    txt(screen, "상점", F18, ACCENT, WIDTH // 2, cy + 18, center=True)
    txt(screen, "상점에서 아이템을 구매하고 다양한 능력치를 올려보세요 아이템은 매달마다 갱신됩니다", F12, GRAY, WIDTH // 2, cy + 42, center=True)
    item_list = []
    names = list(SHOP_LIST.keys())
    for i, cname in enumerate(names):
        info = SHOP_LIST[cname]
        cx2 = 30 + (i % 2) * 480
        cy2 = cy + 70 + (i // 2) * 160
        w, h = 450, 145
        hov = pygame.Rect(cx2, cy2, w, h).collidepoint(mx, my)
        bc = (40, 60, 100) if not info['buy'] else ((30, 40, 75) if hov else PANEL2)
        bdr = info["색"]
        panel(screen, cx2, cy2, w, h, bc, alpha=220, radius=12, border=bdr)
        txt(screen, cname, F18, info["색"], cx2 + 20, cy2 + 14)

        txt(screen, info["desc"], F12, GRAY, cx2 + 20, cy2 + 46)
        txt(screen, "획득 스탯:", F12, GRAY, cx2 + 20, cy2 + 72)
        ex = cx2 + 110
        txt(screen, f"{info['stats']} : {info['eff']}", F14, STAT_COLOR.get(info['stats'], WHITE), ex, cy2 + 70)
        txt(screen, f"가격: {info['money']}", F14, GOLD, ex-100, cy2 + 100)
        r = pygame.Rect(cx2 + w - 110, cy2 + h - 42, 95, 30)
        can = info['buy']
        btn(screen, r, "구매하기" if not can else "구매완료", F12, active=not info['buy'])
        item_list.append((r, cname, info["buy"]))
    return item_list

def draw_event():
    screen.fill(BG)
    ev = g.pending_event
    ev_type = ev.get("type", "random")
    border_col = ORANGE if ev_type == "narsya_start" else GOLD if ev_type == "sv_apply" else ACCENT
    title_col = ORANGE if ev_type == "narsya_start" else GOLD if ev_type == "sv_apply" else YELLOW
    panel(screen, WIDTH // 2 - 300, HEIGHT // 2 - 180, 600, 360, PANEL2, alpha=235, radius=16, border=border_col)
    txt(screen, ev["name"], F18, title_col, WIDTH // 2, HEIGHT // 2 - 148, center=True)
    pygame.draw.line(screen, BORDER, (WIDTH // 2 - 270, HEIGHT // 2 - 122), (WIDTH // 2 + 270, HEIGHT // 2 - 122), 1)
    desc = ev.get("desc", "")
    if desc:
        for i, line in enumerate(desc.split("\n")):
            txt(screen, line, F14, WHITE, WIDTH // 2, HEIGHT // 2 - 95 + i * 26, center=True)
    eff = ev.get("eff", {})
    eff_y = HEIGHT // 2 - 95 + len(desc.split("\n")) * 26 + 10 if desc else HEIGHT // 2 - 60
    for stat, val in eff.items():
        col = GREEN if val > 0 else RED
        txt(screen, f"{stat} {val:+}", F18, col, WIDTH // 2, eff_y, center=True)
        eff_y += 32
    pen = ev.get("penalty", 0)
    if pen > 0:
        txt(screen, f"벌점 +{pen}점  (누적 {g.penalty}/{PENALTY_EXPEL})", F14, RED, WIDTH // 2, eff_y + 4, center=True)
    mx, my = pygame.mouse.get_pos()
    if ev_type == "sv_apply":
        ok_r = pygame.Rect(WIDTH // 2 - 160, HEIGHT // 2 + 120, 140, 40)
        no_r = pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2 + 120, 140, 40)
        btn(screen, ok_r, "지원하기", F14, hover=ok_r.collidepoint(mx, my))
        btn(screen, no_r, "포기하기", F14, hover=no_r.collidepoint(mx, my))
        return ok_r, no_r
    else:
        ok_r = pygame.Rect(WIDTH // 2 - 70, HEIGHT // 2 + 130, 140, 40)
        btn(screen, ok_r, "확인", F18, hover=ok_r.collidepoint(mx, my))
        return ok_r, None


def draw_event_choice(cy,mx,my):
    screen.fill(BG)
    ev = g.pending_event
    ev_type = ev.get("type", "random")
    ch = ev.get("ch")
    border_col = ORANGE if ev_type == "narsya_start" else GOLD if ev_type == "sv_apply" else ACCENT
    title_col = ORANGE if ev_type == "narsya_start" else GOLD if ev_type == "sv_apply" else YELLOW
    panel(screen, WIDTH // 2 - 300, HEIGHT // 2 - 180, 600, 360, PANEL2, alpha=235, radius=16, border=border_col)
    mx, my = pygame.mouse.get_pos()
    if ev_type == "random" and ch and not ev.get("revealed"):
        txt(screen, "선택", F18, title_col, WIDTH // 2, HEIGHT // 2 - 148, center=True)
        pygame.draw.line(screen, BORDER, (WIDTH // 2 - 270, HEIGHT // 2 - 122), (WIDTH // 2 + 270, HEIGHT // 2 - 122), 1)
        txt(screen, ch["decs"], F14, WHITE, WIDTH // 2, HEIGHT // 2 - 70, center=True)
        ok_r = pygame.Rect(WIDTH // 2 - 160, HEIGHT // 2 + 40, 140, 40)
        no_r = pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2 + 40, 140, 40)
        btn(screen, ok_r, ch["yes"], F14, hover=ok_r.collidepoint(mx, my))
        btn(screen, no_r, ch["no"], F14, hover=no_r.collidepoint(mx, my))
        return ok_r, no_r
    txt(screen, ev["name"], F18, title_col, WIDTH // 2, HEIGHT // 2 - 148, center=True)
    pygame.draw.line(screen, BORDER, (WIDTH // 2 - 270, HEIGHT // 2 - 122), (WIDTH // 2 + 270, HEIGHT // 2 - 122), 1)
    desc = ev.get("desc", "")
    if desc:
        for i, line in enumerate(desc.split("\n")):
            txt(screen, line, F14, WHITE, WIDTH // 2, HEIGHT // 2 - 95 + i * 26, center=True)
    eff = ev.get("eff", {})
    eff_y = HEIGHT // 2 - 95 + len(desc.split("\n")) * 26 + 10 if desc else HEIGHT // 2 - 60
    for stat, val in eff.items():
        col = GREEN if val > 0 else RED
        txt(screen, f"{stat} {val:+}", F18, col, WIDTH // 2, eff_y, center=True)
        eff_y += 32
    pen = ev.get("penalty", 0)
    if pen > 0:
        txt(screen, f"벌점 +{pen}점  (누적 {g.penalty}/{PENALTY_EXPEL})", F14, RED, WIDTH // 2, eff_y + 4, center=True)
    if ev_type == "sv_apply":
        ok_r = pygame.Rect(WIDTH // 2 - 160, HEIGHT // 2 + 120, 140, 40)
        no_r = pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2 + 120, 140, 40)
        btn(screen, ok_r, "지원하기", F14, hover=ok_r.collidepoint(mx, my))
        btn(screen, no_r, "포기하기", F14, hover=no_r.collidepoint(mx, my))
        return ok_r, no_r
    if ev_type == "english":
        ok_r = pygame.Rect(WIDTH // 2 - 160, HEIGHT // 2 + 120, 140, 40)
        no_r = pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2 + 120, 140, 40)
        btn(screen, ok_r, "신청하기", F14, hover=ok_r.collidepoint(mx, my))
        btn(screen, no_r, "신청하지 않기", F14, hover=no_r.collidepoint(mx, my))
        return ok_r, no_r
    else:
        ok_r = pygame.Rect(WIDTH // 2 - 70, HEIGHT // 2 + 130, 140, 40)
        btn(screen, ok_r, "확인", F18, hover=ok_r.collidepoint(mx, my))
        return ok_r, None

def draw_ending():
    screen.fill(BG)
    g.t += 1
    title, desc, color = g.get_ending()
    m_color = MAJORS.get(g.major, {}).get("색", WHITE) if g.major else WHITE
    random.seed(g.t // 3)
    for _ in range(30):
        px = random.randint(0, WIDTH)
        py = random.randint(0, HEIGHT)
        r = random.randint(1, 3)
        c = random.choice([ACCENT, YELLOW, GREEN, CYAN, PINK, GOLD])
        pygame.draw.circle(screen, c, (px, py), r)
    panel(screen, WIDTH // 2 - 340, HEIGHT // 2 - 220, 680, 440, PANEL2, alpha=235, radius=20, border=color)
    txt(screen, "3년이 지났습니다!", F18, GRAY, WIDTH // 2, HEIGHT // 2 - 200, center=True)
    txt(screen, title, F32, color, WIDTH // 2, HEIGHT // 2 - 155, center=True)
    pygame.draw.line(screen, BORDER, (WIDTH // 2 - 300, HEIGHT // 2 - 120), (WIDTH // 2 + 300, HEIGHT // 2 - 120), 1)
    txt(screen, desc, F14, WHITE, WIDTH // 2, HEIGHT // 2 - 88, center=True)
    txt(screen, f"전공: {g.major or '미정'}", F14, m_color, WIDTH // 2, HEIGHT // 2 - 60, center=True)
    if g.club:
        txt(screen, f"동아리: {g.club}", F12, CLUBS[g.club]["색"], WIDTH // 2, HEIGHT // 2 - 38, center=True)
    if g.sv_intern:
        txt(screen, "실리콘밸리 인턴 경험 보유", F12, GOLD, WIDTH // 2, HEIGHT // 2 - 18, center=True)
    pygame.draw.line(screen, BORDER, (WIDTH // 2 - 300, HEIGHT // 2), (WIDTH // 2 + 300, HEIGHT // 2), 1)
    txt(screen, "최종 스탯", F14, GRAY, WIDTH // 2, HEIGHT // 2 + 16, center=True)
    sx = WIDTH // 2 - 300
    for i, stat in enumerate(STATS):
        val = g.stats[stat]
        col = STAT_COLOR[stat]
        bx = sx + i * 100
        txt(screen, stat, F12, col, bx + 50, HEIGHT // 2 + 36, center=True)
        bar(screen, bx + 5, HEIGHT // 2 + 54, 90, 12, val, 100, col)
        txt(screen, str(val), F12, col, bx + 50, HEIGHT // 2 + 70, center=True)
    mx, my = pygame.mouse.get_pos()
    back_r = pygame.Rect(WIDTH // 2 - 260, HEIGHT // 2 + 155, 160, 44)
    retry_r = pygame.Rect(WIDTH // 2 + 100, HEIGHT // 2 + 155, 160, 44)
    btn(screen, back_r, "엔딩 목록", F18, hover=back_r.collidepoint(mx, my))
    btn(screen, retry_r, "다시 시작", F18, hover=retry_r.collidepoint(mx, my))
    return back_r, retry_r

act_rects = []
add_rect = None
tab_rects = []
btn_end = None
item_list = []
bag_rect = []
save_r = None
club_rects = []
majors = []
friend_send_r = None
ending_list_btns = []
running = True

while running:
    mx, my = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if g.scene == "main":
                g.scene = "title"
            elif g.scene == "ending":
                g.scene = "ending_list"
            else:
                running = False
        if event.type == pygame.MOUSEWHEEL:
            if g.scene == "main" and g.view == "friend":
                friend_chat.scroll_offset = max(0, friend_chat.scroll_offset - event.y * 30)
            if g.scene == "main" and g.view == "schedule":
                g.act_scroll = max(0, g.act_scroll - event.y * 30)
        if event.type == pygame.KEYDOWN:
            if g.scene == "main" and g.view == "friend":
                if event.key == pygame.K_RETURN:
                    text = friend_chat.input_text.strip()
                    if text:
                        friend_chat.send(text, g)
                        friend_chat.input_text = ""
                        friend_chat.scroll_offset = 999999
                elif event.key == pygame.K_BACKSPACE:
                    friend_chat.input_text = friend_chat.input_text[:-1]
                else:
                    friend_chat.input_text += event.unicode
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if g.scene == "title":
                bs, bl, bq = draw_title()
                if bs.collidepoint(mx, my):
                    g.start()
                if bl.collidepoint(mx, my) and os.path.exists(SAVE_FILE):
                    g.load()
                if bq.collidepoint(mx, my):
                    running = False
            elif g.scene == "main":
                if save_r and save_r.collidepoint(mx, my):
                    g.save()
                for r, key in tab_rects:
                    if r.collidepoint(mx, my):
                        g.view = key
                        g.selected_act = None
                if btn_end and btn_end.collidepoint(mx, my):
                    g.end_month()
                if g.view == "schedule":
                    acts = g.current_activities()
                    for i, r in enumerate(act_rects):
                        if r and r.collidepoint(mx, my):
                            g.selected_act = i
                    if add_rect and add_rect.collidepoint(mx, my):
                        if g.selected_act is not None and g.selected_act < len(acts):
                            g.apply_activity(acts[g.selected_act])
                            g.selected_act = None
                    rx2 = 460
                    scy = 108 + 64
                    for idx, act in enumerate(g.schedule):
                        del_r = pygame.Rect(WIDTH - rx2 - 36, scy + idx * 56 + 14, 20, 20)
                        if del_r.collidepoint(mx, my):
                            g.remove_activity(act)
                            break
                elif g.view == "club":
                    for r, cname, selected in club_rects:
                        if r.collidepoint(mx, my):
                            if selected:
                                g.notify("학년이 올라가야 동아리를 바꿀 수 있습니다.", RED)
                            elif g.can_change_club():
                                g.join_club(cname)
                                g.notify(f"{cname} 동아리에 가입했습니다!", CLUBS[cname]["색"])
                            else:
                                g.notify("학년이 올라가야 동아리를 바꿀 수 있습니다.", RED)
                elif g.view == "shop":
                    for r, cname, selected in item_list:
                        if r.collidepoint(mx, my):
                            if selected:
                                g.notify("이미 구매하신 물품입니다", RED)
                            elif SHOP_LIST[cname]["money"] <= g.money:
                                g.notify("아이템을 구매하셨습니다.", GREEN)
                                g.buy_item(cname)
                                g.money -= SHOP_LIST[cname]["money"]
                            else:
                                g.notify("돈이 부족합니다!", RED)
                elif g.view == "bag":
                    for r,cname in bag_rect:
                        if r.collidepoint(mx,my):
                            if SHOP_LIST[cname]['stats'] == "피로도":
                                g.fatigue += SHOP_LIST[cname]['eff']
                                g.bag_list.remove(cname)
                                g.notify(f"{cname} 사용", GREEN)
                                if g.fatigue < 0 :
                                    g.fatigue = 0
                            else:
                                g.use_item(cname)
                                g.notify(f"{cname} 사용", GREEN)
                            break
                elif g.view == "major":
                    for r, cname, selected in majors:
                        if r.collidepoint(mx, my):
                            g.join_major(cname)
                            g.notify(f"{cname}으로 전공을 선택했습니다.", MAJORS[cname]["색"])
                elif g.view == "friend":
                    if friend_send_r and friend_send_r.collidepoint(mx, my):
                        text = friend_chat.input_text.strip()
                        if text:
                            friend_chat.send(text, g)
                            friend_chat.input_text = "" 
                            friend_chat.scroll_offset = 999999
            elif g.scene == "event":
                ok_r, no_r = draw_event_choice(108, mx, my)
                ev_type = g.pending_event.get("type", "random")
                ch = g.pending_event.get("ch")
                revealed = g.pending_event.get("revealed")
                if ev_type == "random" and ch and not revealed:
                    if ok_r and ok_r.collidepoint(mx, my):
                        g.resolve_random_event(True)
                    elif no_r and no_r.collidepoint(mx, my):
                        g.pending_event = None
                        g.scene = "main"
                        g.notify(f"{g.year_label()} 시작!", ACCENT)
                else:
                    if ok_r and ok_r.collidepoint(mx, my):
                        if ev_type == "sv_apply":
                            g.accept_sv()
                        elif ev_type == "english":
                            g.accept_en()
                        g.pending_event = None
                        g.scene = "main"
                        if ev_type not in ("sv_apply",):
                            g.notify(f"{g.year_label()} 시작!", ACCENT)
                    if no_r and no_r.collidepoint(mx, my):
                        if ev_type == "sv_apply":
                            g.decline_sv()
                        g.pending_event = None
                        g.scene = "main"
                        g.notify(f"{g.year_label()} 시작!", ACCENT)
            elif g.scene == "ending_list":
                for btn_r, idx, unlocked in ending_list_btns:
                    if btn_r.collidepoint(mx, my) and unlocked:
                        g.selected_ending = idx
                        g.scene = "ending"
            elif g.scene == "ending":
                back_r, retry_r = draw_ending()
                if back_r.collidepoint(mx, my):
                    g.scene = "ending_list"
                if retry_r.collidepoint(mx, my):
                    g.start()

    if g.scene == "title":
        draw_title()
    elif g.scene == "main":
        tab_rects, btn_end, save_r = draw_main()
        if g.view == "schedule":
            result = draw_schedule(108, mx, my)
            act_rects, add_rect = result if result else ([], None)
        elif g.view == "club":
            club_rects = draw_club(108, mx, my)
        elif g.view == "major":
            majors = draw_major(108, mx, my)
        elif g.view == "friend":
            friend_send_r = draw_friend_chat(108, mx, my)
        elif g.view == "shop":
            item_list = draw_shop(108, mx, my)
        elif g.view == "bag":
            bag_rect = draw_bag(108,mx,my)
        draw_notification()
    elif g.scene == "event":
        draw_event_choice(108,mx,my)
    elif g.scene == "ending_list":
        ending_list_btns = draw_ending_list()
    elif g.scene == "ending":
        draw_ending()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()