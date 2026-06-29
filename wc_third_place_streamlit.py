import streamlit as st
import math, random, copy, csv, os, asyncio, concurrent.futures
from datetime import date, timedelta
import numpy as np

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WC 2026 — Best Third Place Teams",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
:root {
  --bg:      #0f1117;
  --surf:    #1a1d27;
  --surf2:   #22263a;
  --border:  #2e3347;
  --text:    #e8ecf4;
  --muted:   #6b7494;
  --safe:    #22c55e;
  --likely:  #86efac;
  --bubble:  #f59e0b;
  --danger:  #ef4444;
  --accent:  #6366f1;
  --gold:    #fbbf24;
}
[data-testid="stAppViewContainer"] { background: var(--bg); }
[data-testid="stHeader"]           { background: transparent; }
section.main > div                 { padding-top: .5rem; }
[data-testid="stTabs"] button      { font-size: 13px; font-weight: 600; }

.hero-stat {
  background: var(--surf); border: 1px solid var(--border);
  border-radius: 10px; padding: 14px 18px; text-align: center;
}
.hero-stat .val { font-size: 26px; font-weight: 800; color: var(--gold); }
.hero-stat .lbl { font-size: 11px; color: var(--muted); text-transform: uppercase;
                  letter-spacing:.05em; margin-top:2px; }

/* ── best-thirds table ── */
.bt-table { width:100%; border-collapse:collapse; font-size:13px; }
.bt-table thead tr { background:var(--surf2); border-bottom:2px solid var(--border); }
.bt-table th { padding:8px 10px; color:var(--muted); font-weight:600; font-size:10px;
               text-transform:uppercase; letter-spacing:.06em; text-align:center;
               white-space:nowrap; }
.bt-table th.left { text-align:left; }
.bt-table td { padding:8px 10px; border-bottom:1px solid rgba(46,51,71,.5);
               text-align:center; vertical-align:middle; }
.bt-table td.left { text-align:left; }
.bt-table tr:hover td { background:rgba(99,102,241,.05); }
.bt-table tr.cutline td { border-bottom:3px solid var(--accent) !important; }

.rank-num { display:inline-flex; align-items:center; justify-content:center;
            width:24px; height:24px; border-radius:50%; font-size:11px; font-weight:700;
            background:var(--surf2); color:var(--muted); }
.rank-num.in  { background:rgba(34,197,94,.15);  color:#4ade80; }
.rank-num.cut { background:rgba(245,158,11,.15); color:#fbbf24; }
.rank-num.out { background:rgba(239,68,68,.1);   color:#f87171; }

.pill { display:inline-block; padding:3px 9px; border-radius:20px;
        font-size:12px; font-weight:800; min-width:52px; text-align:center; }
.p-safe   { background:rgba(34,197,94,.18);  color:#4ade80; }
.p-likely { background:rgba(134,239,172,.15);color:#86efac; }
.p-bubble { background:rgba(245,158,11,.18); color:#fbbf24; }
.p-danger { background:rgba(239,68,68,.15);  color:#f87171; }

.team-cell { display:flex; align-items:center; gap:8px; }
.team-flag { font-size:17px; line-height:1; }
.team-name { font-weight:600; color:var(--text); }
.team-grp  { font-size:10px; color:var(--muted); }

.bar-wrap { position:relative; height:6px; background:rgba(46,51,71,.6);
            border-radius:3px; width:100%; min-width:60px; }
.bar-fill { position:absolute; left:0; top:0; height:100%; border-radius:3px; }

/* ── group card ── */
.gc { background:var(--surf); border:1px solid var(--border);
      border-radius:8px; overflow:hidden; margin-bottom:12px; }
.gc-hdr { background:var(--surf2); padding:6px 11px;
          border-bottom:1px solid var(--border);
          display:flex; align-items:center; justify-content:space-between; }
.gc-hdr .gid { font-weight:800; color:var(--gold); font-size:12px; }
.gc-hdr .gct { font-size:10px; color:var(--muted); }
.gc-tbl { width:100%; border-collapse:collapse; font-size:11.5px; }
.gc-tbl th { padding:4px 7px; color:var(--muted); font-size:9px; text-transform:uppercase;
             background:var(--surf2); border-bottom:1px solid var(--border); text-align:center; }
.gc-tbl th:nth-child(2) { text-align:left; }
.gc-tbl td { padding:5px 7px; text-align:center; border-bottom:1px solid rgba(46,51,71,.35); }
.gc-tbl td:nth-child(2) { text-align:left; font-weight:500; }
.gc-tbl tr:last-child td { border-bottom:none; }
.gc-tbl tr.p3 td { background:rgba(245,158,11,.07); }
.pos1{color:#4ade80;font-weight:700;} .pos2{color:#86efac;font-weight:700;}
.pos3{color:#fbbf24;font-weight:700;} .pos4{color:#f87171;}
.gd-pos{color:#4ade80;} .gd-neg{color:#f87171;}

.res-row { font-size:11px; color:var(--muted); padding:3px 9px;
           border-top:1px solid rgba(46,51,71,.4); }
.res-score { font-weight:700; color:var(--text); font-family:monospace; }

/* ── placement prob table inside group card ── */
.plc-tbl { width:100%; border-collapse:collapse; font-size:11px; }
.plc-tbl th { padding:4px 6px; color:var(--muted); font-size:9px; text-transform:uppercase;
              background:rgba(34,39,58,.6); border-bottom:1px solid var(--border);
              text-align:center; }
.plc-tbl th:first-child { text-align:left; }
.plc-tbl td { padding:4px 6px; text-align:center; border-bottom:1px solid rgba(46,51,71,.3); }
.plc-tbl td:first-child { text-align:left; font-size:10.5px; }
.plc-tbl tr:last-child td { border-bottom:none; }
.plc-hdr { font-size:9px; font-weight:700; text-transform:uppercase; letter-spacing:.06em;
           color:var(--muted); padding:5px 9px 3px 9px; border-top:1px solid var(--border);
           background:rgba(34,39,58,.4); }

/* ── pts×GD matrix ── */
.matrix-wrap { background:var(--surf); border:1px solid var(--border); border-radius:10px;
               overflow:hidden; }
.matrix-hdr  { background:var(--surf2); padding:9px 14px; border-bottom:1px solid var(--border);
               font-weight:700; font-size:13px; color:var(--text); }
.mx-tbl { width:100%; border-collapse:collapse; font-size:11.5px; }
.mx-tbl th { padding:6px 8px; color:var(--muted); font-size:9px; text-transform:uppercase;
             background:var(--surf2); border-bottom:1px solid var(--border); text-align:center; }
.mx-tbl th.left { text-align:left; }
.mx-tbl td { padding:5px 7px; text-align:center; border-bottom:1px solid rgba(46,51,71,.3);
             border-right:1px solid rgba(46,51,71,.3); font-weight:600; font-size:11px; }
.mx-tbl td.pts-label { text-align:left; color:var(--gold); font-weight:700;
                        border-right:1px solid var(--border); background:var(--surf2); }
.mx-tbl tr:last-child td { border-bottom:none; }
.mx-tbl td.empty { color:var(--muted); font-weight:400; font-size:10px; }

/* ── historical ── */
.ht-wrap { background:var(--surf); border:1px solid var(--border);
           border-radius:8px; overflow:hidden; margin-bottom:18px; }
.ht-hdr  { background:var(--surf2); padding:9px 14px; border-bottom:1px solid var(--border);
           display:flex; align-items:center; gap:12px; }
.ht-yr   { font-size:22px; font-weight:800; color:var(--gold); }
.ht-meta { font-size:12px; color:var(--muted); }
.ht-badge{ background:rgba(251,191,36,.12); color:var(--gold);
           border:1px solid rgba(251,191,36,.3); padding:2px 9px;
           border-radius:20px; font-size:11px; font-weight:700; }
.ht-tbl  { width:100%; border-collapse:collapse; font-size:12.5px; }
.ht-tbl th { padding:6px 9px; color:var(--muted); font-size:9px; text-transform:uppercase;
             border-bottom:1px solid var(--border); background:var(--surf2); text-align:center; }
.ht-tbl th.left { text-align:left; }
.ht-tbl td { padding:6px 9px; border-bottom:1px solid rgba(46,51,71,.5); text-align:center; }
.ht-tbl td.left { text-align:left; font-weight:500; }
.ht-tbl tr:last-child td { border-bottom:none; }
.ht-tbl tr.adv  td { background:rgba(34,197,94,.06); }
.ht-tbl tr.elim td { background:rgba(239,68,68,.04); }
.ht-tbl tr.cutoff td { border-top:2px dashed var(--bubble) !important; }
.pts-conv { color:var(--gold); font-weight:700; }
.badge-adv  { display:inline-block; padding:2px 7px; border-radius:4px;
              background:rgba(34,197,94,.2); color:#4ade80; font-size:10px; font-weight:700; }
.badge-elim { display:inline-block; padding:2px 7px; border-radius:4px;
              background:rgba(239,68,68,.15); color:#f87171; font-size:10px; font-weight:700; }

.info-box  { background:var(--surf); border:1px solid var(--border);
             border-left:4px solid var(--accent); border-radius:6px;
             padding:12px 15px; line-height:1.75; margin-bottom:14px; font-size:13px; }
.thresh-box{ background:var(--surf); border:1px solid var(--border);
             border-left:4px solid var(--gold); border-radius:6px;
             padding:12px 15px; line-height:1.8; font-size:13px; }
.model-box { background:var(--surf); border:1px solid var(--border); border-radius:8px;
             padding:10px 14px; font-size:12px; color:var(--muted); margin-bottom:14px; }
.ctrl-label{ font-size:10px; color:var(--muted); text-transform:uppercase;
             letter-spacing:.05em; margin-bottom:3px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
GLOBAL_MEAN  = 1.35
TIME_DECAY   = 0.18   # per year; ~4 years ago = 50% weight
WC_REF_DATE      = date(2026, 6, 11)   # WC kick-off — decay anchor
WC2026_GROUP_END = date(2026, 7, 2)    # last group stage match day

FLAGS = {
    "Mexico":"🇲🇽","South Korea":"🇰🇷","Czechia":"🇨🇿","South Africa":"🇿🇦",
    "Switzerland":"🇨🇭","Canada":"🇨🇦","Qatar":"🇶🇦","Bosnia-Herz.":"🇧🇦",
    "Scotland":"🏴󠁧󠁢󠁳󠁣󠁴󠁿","Brazil":"🇧🇷","Morocco":"🇲🇦","Haiti":"🇭🇹",
    "USA":"🇺🇸","Australia":"🇦🇺","Türkiye":"🇹🇷","Paraguay":"🇵🇾",
    "Germany":"🇩🇪","Ivory Coast":"🇨🇮","Ecuador":"🇪🇨","Curaçao":"🇨🇼",
    "Sweden":"🇸🇪","Japan":"🇯🇵","Netherlands":"🇳🇱","Tunisia":"🇹🇳",
    "Belgium":"🇧🇪","Egypt":"🇪🇬","Iran":"🇮🇷","New Zealand":"🇳🇿",
    "Uruguay":"🇺🇾","Saudi Arabia":"🇸🇦","Spain":"🇪🇸","Cape Verde":"🇨🇻",
    "France":"🇫🇷","Iraq":"🇮🇶","Norway":"🇳🇴","Senegal":"🇸🇳",
    "Algeria":"🇩🇿","Argentina":"🇦🇷","Austria":"🇦🇹","Jordan":"🇯🇴",
    "Colombia":"🇨🇴","DR Congo":"🇨🇩","Portugal":"🇵🇹","Uzbekistan":"🇺🇿",
    "Croatia":"🇭🇷","England":"🏴󠁧󠁢󠁥󠁮󠁧󠁿","Ghana":"🇬🇭","Panama":"🇵🇦",
}

CSV_NAME = {
    "Czechia":      "Czech Republic",
    "USA":          "United States",
    "Türkiye":      "Turkey",
    "Bosnia-Herz.": "Bosnia and Herzegovina",
}

GD_BUCKETS = list(range(-6, 7))   # -6 … +6  (clamped at edges)
GD_LABELS  = ["≤−6", "−5", "−4", "−3", "−2", "−1", "0",
              "+1", "+2", "+3", "+4", "+5", "≥+6"]

# R32 bracket slot labels: match# → (slot-1 desc, slot-2 desc)
R32_SLOT_LABELS: dict = {
    73: ("2nd · Grp A",  "2nd · Grp B"),
    74: ("1st · Grp E",  "Best 3rd [E]"),
    75: ("1st · Grp F",  "2nd · Grp C"),
    76: ("1st · Grp C",  "2nd · Grp F"),
    77: ("1st · Grp I",  "Best 3rd [I]"),
    78: ("2nd · Grp E",  "2nd · Grp I"),
    79: ("1st · Grp A",  "Best 3rd [A]"),
    80: ("1st · Grp L",  "Best 3rd [L]"),
    81: ("1st · Grp D",  "Best 3rd [D]"),
    82: ("1st · Grp G",  "Best 3rd [G]"),
    83: ("2nd · Grp K",  "2nd · Grp L"),
    84: ("1st · Grp H",  "2nd · Grp J"),
    85: ("1st · Grp B",  "Best 3rd [B]"),
    86: ("1st · Grp J",  "2nd · Grp H"),
    87: ("1st · Grp K",  "Best 3rd [K]"),
    88: ("2nd · Grp D",  "2nd · Grp G"),
}

TOURNAMENT_WEIGHTS: dict[str, float] = {
    # World Cup
    "FIFA World Cup":                            5.0,
    "FIFA World Cup qualification":              3.5,
    # Continental championships
    "UEFA Euro":                                 3.8,
    "Copa América":                              3.6,
    "African Cup of Nations":                    2.5,
    "AFC Asian Cup":                             2.2,
    "Gold Cup":                                  2.6,
    "Oceania Nations Cup":                       2.2,
    "AFF Championship":                          2.2,
    "ASEAN Championship":                        2.0,
    "EAFF Championship":                         2.0,
    "SAFF Cup":                                  2.0,
    "Gulf Cup":                                  2.0,
    "COSAFA Cup":                                2.0,
    "CAFA Nations Cup":                          2.0,
    "Baltic Cup":                                2.0,
    "Arab Cup":                                  2.0,
    "UEFA Nations League":                       3.5,
    "CONCACAF Nations League":                   2.9,
    "FIFA Confederations Cup":                   2.0,
    "CONMEBOL–UEFA Cup of Champions":            2.0,
    "Intercontinental Cup":                      2.0,
    # Qualifiers
    "UEFA Euro qualification":                   3.3,
    "AFC Asian Cup qualification":               2.0,
    "African Cup of Nations qualification":      2.2,
    "Gold Cup qualification":                    2.6,
    "Oceania Nations Cup qualification":         2.0,
    "AFF Championship qualification":            2.0,
    "ASEAN Championship qualification":          2.0,
    "EAFF Championship qualification":           2.0,
    "Arab Cup qualification":                    2.0,
    "Copa América qualification":                3.2,
    # Friendlies / low-stakes
    "Friendly":                                  1.0,
    "FIFA Series":                               1.0,
    "Kirin Cup":                                 1.0,
    "Kirin Challenge Cup":                       1.0,
    "King's Cup":                                1.0,
    "Canadian Shield":                           1.0,
    "CONCACAF Series":                           1.0,
}

def _time_weight(game_date: date) -> float:
    """Exponential decay anchored to WC kick-off: 4 yrs ago ≈ 50% weight."""
    years_ago = (WC_REF_DATE - game_date).days / 365.25
    return math.exp(-TIME_DECAY * max(years_ago, 0))

# ─────────────────────────────────────────────────────────────────────────────
# LOAD TEAM STATS  (weighted by tournament importance + recency)
# ─────────────────────────────────────────────────────────────────────────────

SHRINK_K = 10.0
NB_DISPERSION = 10.0

@st.cache_data(show_spinner=False)
def load_team_stats(csv_path: str, cutoff_year: int = 2018) -> dict:
    """
    Returns {team: {avg_gf, avg_ga, eff_games, shrunk_gf, shrunk_ga},
             "_global_mean": float}

    Two-pass approach:
      Pass 1 — raw weighted averages per team.
      Pass 2 — opponent-quality-adjusted averages:
                adj_gf = actual_gf * global_mean / opponent_raw_ga
                adj_ga = actual_ga * global_mean / opponent_raw_gf
                This prevents OFC-inflated scorelines from distorting attack ratings.
    Shrinkage is then applied to the adjusted rates.
    """
    cutoff = date(cutoff_year, 1, 1)

    # ── Pass 1: collect matches + raw weighted totals ─────────────────────
    stored: list = []          # (home, away, hs, as_, w)
    raw: dict[str, list] = {}  # team -> [wgf, wga, w_sum]
    total_wgf = total_w = 0.0

    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                try:
                    d   = date.fromisoformat(row["date"])
                    if d < cutoff: continue
                    hs  = int(row["home_score"])
                    as_ = int(row["away_score"])
                except (ValueError, KeyError):
                    continue
                tw = TOURNAMENT_WEIGHTS.get(row.get("tournament", "Friendly"), 1.0)
                dw = _time_weight(d)
                w  = tw * dw
                ht, at = row["home_team"], row["away_team"]
                stored.append((ht, at, hs, as_, w))
                for team, gf, ga in [(ht, hs, as_), (at, as_, hs)]:
                    if team not in raw: raw[team] = [0.0, 0.0, 0.0]
                    raw[team][0] += gf * w
                    raw[team][1] += ga * w
                    raw[team][2] += w
                total_wgf += (hs + as_) * w
                total_w   += 2 * w
    except FileNotFoundError:
        return {}

    global_mean = (total_wgf / total_w) if total_w > 0 else GLOBAL_MEAN

    # Seed opponent-quality estimates from raw rates, then iterate
    cur_gf = {t: v[0] / v[2] for t, v in raw.items() if v[2] >= 3}
    cur_ga = {t: v[1] / v[2] for t, v in raw.items() if v[2] >= 3}

    # ── Iterated normalization (4 passes) ────────────────────────────────
    adj: dict[str, list] = {}
    for _iter in range(4):
        adj = {}
        for ht, at, hs, as_, w in stored:
            opp_ga_h = cur_ga.get(at, global_mean)
            opp_gf_h = cur_gf.get(at, global_mean)
            opp_ga_a = cur_ga.get(ht, global_mean)
            opp_gf_a = cur_gf.get(ht, global_mean)

            h_adj_gf = hs  * global_mean / opp_ga_h
            h_adj_ga = as_ * global_mean / opp_gf_h
            a_adj_gf = as_ * global_mean / opp_ga_a
            a_adj_ga = hs  * global_mean / opp_gf_a

            for team, agf, aga in [(ht, h_adj_gf, h_adj_ga), (at, a_adj_gf, a_adj_ga)]:
                if team not in adj: adj[team] = [0.0, 0.0, 0.0]
                adj[team][0] += agf * w
                adj[team][1] += aga * w
                adj[team][2] += w

        cur_gf = {t: v[0] / v[2] for t, v in adj.items() if v[2] >= 3}
        cur_ga = {t: v[1] / v[2] for t, v in adj.items() if v[2] >= 3}

    # ── Shrinkage on adjusted rates ───────────────────────────────────────
    result = {"_global_mean": global_mean}
    for t, v in adj.items():
        if v[2] < 3.0: continue
        eff = v[2]
        avg_gf = v[0] / eff
        avg_ga = v[1] / eff
        shrunk_gf = (eff * avg_gf + SHRINK_K * global_mean) / (eff + SHRINK_K)
        shrunk_ga = (eff * avg_ga + SHRINK_K * global_mean) / (eff + SHRINK_K)
        result[t] = {
            "avg_gf":    avg_gf,
            "avg_ga":    avg_ga,
            "shrunk_gf": shrunk_gf,
            "shrunk_ga": shrunk_ga,
            "eff_games": eff,
        }
    return result


@st.cache_data(show_spinner=False)
def load_ftable(csv_path: str) -> dict:
    """
    Parse third_place_combinations.csv → frozenset(group_letters) → bracket-slot dict.
    Key:   frozenset of 8 advancing group letters, e.g. frozenset({'A','B','C','D','E','F','G','H'})
    Value: {'1A':'3H', '1B':'3G', '1D':'3B', '1E':'3C', '1G':'3A', '1I':'3F', '1K':'3D', '1L':'3E'}
    """
    # CSV column index for each bracket slot
    scm = {"1A": 12, "1B": 13, "1D": 14, "1E": 15, "1G": 16, "1I": 17, "1K": 18, "1L": 19}
    ftable: dict = {}
    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            rows = list(csv.reader(f))
        for row in rows[2:]:                 # skip title row (0) + header row (1)
            row += [""] * max(0, 20 - len(row))
            key = frozenset(
                row[i].strip() for i in range(12)
                if row[i].strip() and row[i].strip().upper() not in ("NAN", "")
            )
            if len(key) == 8:
                ftable[key] = {s: row[c].strip() for s, c in scm.items()}
    except FileNotFoundError:
        pass
    return ftable


def get_stats(app_name: str, team_stats: dict) -> dict:
    csv_name = CSV_NAME.get(app_name, app_name)
    return team_stats.get(csv_name) or team_stats.get(app_name) or {}


def match_lambda(atk: str, def_: str, team_stats: dict) -> float:
    """Expected goals using shrunk attack/defense rates and calibrated global mean."""
    global_mean = team_stats.get("_global_mean", GLOBAL_MEAN)
    a = get_stats(atk,  team_stats)
    d = get_stats(def_, team_stats)
    atk_rate = a.get("shrunk_gf", global_mean)
    def_rate = d.get("shrunk_ga", global_mean)
    return max(0.1, atk_rate * def_rate / global_mean)

# ─────────────────────────────────────────────────────────────────────────────
# 2026 WC DATA
# ─────────────────────────────────────────────────────────────────────────────
GROUPS_CONFIG = [
    {"id":"A","teams":["Mexico","South Korea","Czechia","South Africa"]},
    {"id":"B","teams":["Switzerland","Canada","Qatar","Bosnia-Herz."]},
    {"id":"C","teams":["Scotland","Brazil","Morocco","Haiti"]},
    {"id":"D","teams":["USA","Australia","Türkiye","Paraguay"]},
    {"id":"E","teams":["Germany","Ivory Coast","Ecuador","Curaçao"]},
    {"id":"F","teams":["Sweden","Japan","Netherlands","Tunisia"]},
    {"id":"G","teams":["Belgium","Egypt","Iran","New Zealand"]},
    {"id":"H","teams":["Uruguay","Saudi Arabia","Spain","Cape Verde"]},
    {"id":"I","teams":["France","Iraq","Norway","Senegal"]},
    {"id":"J","teams":["Algeria","Argentina","Austria","Jordan"]},
    {"id":"K","teams":["Colombia","DR Congo","Portugal","Uzbekistan"]},
    {"id":"L","teams":["Croatia","England","Ghana","Panama"]},
]

ALL_PAIRS = [[0,1],[2,3],[0,2],[1,3],[0,3],[1,2]]

EMPTY_RESULTS = {g["id"]: [] for g in GROUPS_CONFIG}

HISTORY = [
    {"year":1986,"system":"2-1-0","advancing":4,"total":6,"host":"Mexico",
     "note":"2-1-0 system · Converted pts = orig + wins",
     "teams":[
         {"group":"A","team":"Bulgaria",  "w":0,"d":2,"l":1,"gf":2,"ga":4,"op":2,"adv":True},
         {"group":"B","team":"Belgium",   "w":1,"d":1,"l":1,"gf":5,"ga":5,"op":3,"adv":True},
         {"group":"C","team":"Hungary",   "w":1,"d":0,"l":2,"gf":2,"ga":9,"op":2,"adv":False},
         {"group":"D","team":"N. Ireland","w":0,"d":1,"l":2,"gf":2,"ga":6,"op":1,"adv":False},
         {"group":"E","team":"Uruguay",   "w":0,"d":2,"l":1,"gf":2,"ga":7,"op":2,"adv":True},
         {"group":"F","team":"Poland",    "w":1,"d":1,"l":1,"gf":1,"ga":3,"op":3,"adv":True},
     ]},
    {"year":1990,"system":"2-1-0","advancing":4,"total":6,"host":"Italy",
     "note":"2-1-0 system · Converted pts = orig + wins",
     "teams":[
         {"group":"A","team":"Austria",    "w":1,"d":0,"l":2,"gf":2,"ga":3,"op":2,"adv":False},
         {"group":"B","team":"Argentina",  "w":1,"d":1,"l":1,"gf":3,"ga":2,"op":3,"adv":True},
         {"group":"C","team":"Scotland",   "w":1,"d":0,"l":2,"gf":2,"ga":3,"op":2,"adv":False},
         {"group":"D","team":"Colombia",   "w":1,"d":1,"l":1,"gf":3,"ga":2,"op":3,"adv":True},
         {"group":"E","team":"Uruguay",    "w":1,"d":1,"l":1,"gf":2,"ga":3,"op":3,"adv":True},
         {"group":"F","team":"Netherlands","w":0,"d":3,"l":0,"gf":2,"ga":2,"op":3,"adv":True},
     ]},
    {"year":1994,"system":"3-1-0","advancing":4,"total":6,"host":"USA",
     "note":"First WC with 3-1-0 system · No conversion needed",
     "teams":[
         {"group":"A","team":"USA",      "w":1,"d":1,"l":1,"gf":3,"ga":3,"op":4,"adv":True},
         {"group":"B","team":"Russia",   "w":1,"d":0,"l":2,"gf":7,"ga":6,"op":3,"adv":False},
         {"group":"C","team":"S. Korea", "w":0,"d":2,"l":1,"gf":4,"ga":5,"op":2,"adv":False},
         {"group":"D","team":"Argentina","w":2,"d":0,"l":1,"gf":6,"ga":3,"op":6,"adv":True},
         {"group":"E","team":"Italy",    "w":1,"d":1,"l":1,"gf":4,"ga":3,"op":4,"adv":True},
         {"group":"F","team":"Belgium",  "w":2,"d":0,"l":1,"gf":2,"ga":1,"op":6,"adv":True},
     ]},
]

# ─────────────────────────────────────────────────────────────────────────────
# LIVE SCORE FETCHING  (FotMob)
# ─────────────────────────────────────────────────────────────────────────────

# FotMob name → app name for teams whose spelling differs
FOTMOB_NAME_MAP: dict[str, str] = {
    "United States":                    "USA",
    "Czech Republic":                   "Czechia",
    "Turkey":                           "Türkiye",
    "Turkiye":                          "Türkiye",
    "Bosnia & Herzegovina":             "Bosnia-Herz.",
    "Bosnia and Herzegovina":           "Bosnia-Herz.",
    "Côte d'Ivoire":                    "Ivory Coast",
    "Cote d'Ivoire":                    "Ivory Coast",
    "Curacao":                          "Curaçao",
    "Cape Verde Islands":               "Cape Verde",
    "Congo DR":                         "DR Congo",
    "Congo, DR":                        "DR Congo",
    "Democratic Republic of Congo":     "DR Congo",
    "Korea Republic":                   "South Korea",
    "Republic of Korea":                "South Korea",
}

# All 48 WC 2026 teams (app names) — used to filter FotMob matches
WC_TEAMS: set[str] = {t for g in GROUPS_CONFIG for t in g["teams"]}

# team name → (group_id, index_in_group)
_TEAM_TO_GROUP: dict[str, tuple[str, int]] = {
    t: (g["id"], i)
    for g in GROUPS_CONFIG
    for i, t in enumerate(g["teams"])
}

def _fotmob_name(raw: str) -> str:
    return FOTMOB_NAME_MAP.get(raw, raw)

def _run_async(coro):
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result(timeout=30)

def _process_wc_match(match: dict, results: dict) -> bool:
    """
    Parse one FotMob match dict and append to results if it is a
    finished WC 2026 group-stage game between two known teams.
    Returns True if a result was added.
    """
    try:
        status = match.get("status", {})
        if not status.get("finished"):
            return False

        h_name = _fotmob_name(match.get("home", {}).get("name", ""))
        a_name = _fotmob_name(match.get("away", {}).get("name", ""))

        if h_name not in WC_TEAMS or a_name not in WC_TEAMS:
            return False

        hs = match.get("home", {}).get("score")
        as_ = match.get("away", {}).get("score")
        if hs is None or as_ is None:
            score_str = status.get("scoreStr", "")
            if "-" in score_str:
                parts = score_str.split("-")
                hs, as_ = int(parts[0].strip()), int(parts[1].strip())
            else:
                return False

        hi = _TEAM_TO_GROUP.get(h_name)
        ai = _TEAM_TO_GROUP.get(a_name)
        if not hi or not ai or hi[0] != ai[0]:
            return False

        gid, t1, t2 = hi[0], hi[1], ai[1]

        if any((r["t1"] == t1 and r["t2"] == t2) or
               (r["t1"] == t2 and r["t2"] == t1) for r in results[gid]):
            return False

        results[gid].append({"t1": t1, "t2": t2, "s1": int(hs), "s2": int(as_)})
        return True
    except (TypeError, ValueError, KeyError):
        return False

async def _fotmob_fetch_wc():
    """Fetch all completed WC 2026 group stage results day-by-day in parallel."""
    from fotmob import FotMob

    today = date.today()
    end   = min(today, WC2026_GROUP_END)

    date_keys = []
    current = WC_REF_DATE
    while current <= end:
        date_keys.append(current.strftime("%Y%m%d"))
        current += timedelta(days=1)

    async with FotMob() as fm:
        responses = await asyncio.gather(
            *[fm.get_matches_by_date(dk) for dk in date_keys],
            return_exceptions=True,
        )

    results = {g["id"]: [] for g in GROUPS_CONFIG}
    found = 0
    for resp in responses:
        if isinstance(resp, Exception) or not isinstance(resp, dict):
            continue
        for league in resp.get("leagues", []):
            for match in league.get("matches", []):
                if _process_wc_match(match, results):
                    found += 1

    return results, found

@st.cache_data(ttl=270, show_spinner=False)
def fetch_live_wc_results() -> tuple:
    """Returns (results_dict, status_str). Cached 270 s so 5-min refresh always hits fresh data."""
    try:
        results, found = _run_async(_fotmob_fetch_wc())
    except Exception as e:
        empty = {g["id"]: [] for g in GROUPS_CONFIG}
        return empty, f"⚠ FotMob unavailable: {e}"

    now_str = date.today().strftime("%b %d")
    status  = (f"🟢 Live via FotMob · {found} results · {now_str}" if found
               else f"⚠ FotMob: 0 WC matches found · {now_str}")
    return results, status


async def _fotmob_fetch_inprogress():
    """Fetch today's in-progress WC matches with current score and minute."""
    from fotmob import FotMob
    today_key = date.today().strftime("%Y%m%d")
    async with FotMob() as fm:
        resp = await fm.get_matches_by_date(today_key)

    live: dict[str, list] = {g["id"]: [] for g in GROUPS_CONFIG}
    if not isinstance(resp, dict):
        return live

    for league in resp.get("leagues", []):
        for match in league.get("matches", []):
            try:
                status = match.get("status", {})
                # Only in-progress: started but not finished
                if not status.get("started") or status.get("finished"):
                    continue

                h_name = _fotmob_name(match.get("home", {}).get("name", ""))
                a_name = _fotmob_name(match.get("away", {}).get("name", ""))
                if h_name not in WC_TEAMS or a_name not in WC_TEAMS:
                    continue

                hs  = match.get("home", {}).get("score")
                as_ = match.get("away", {}).get("score")
                if hs is None or as_ is None:
                    score_str = status.get("scoreStr", "")
                    if "-" in score_str:
                        parts = score_str.split("-")
                        hs, as_ = int(parts[0].strip()), int(parts[1].strip())
                    else:
                        hs, as_ = 0, 0

                hi = _TEAM_TO_GROUP.get(h_name)
                ai = _TEAM_TO_GROUP.get(a_name)
                if not hi or not ai or hi[0] != ai[0]:
                    continue

                gid = hi[0]
                # Minute: FotMob puts it in status.liveTime.short or status.minutesStr
                live_time = status.get("liveTime", {})
                minute = (live_time.get("short")
                          or live_time.get("long")
                          or status.get("minutesStr", ""))

                live[gid].append({
                    "home": h_name,
                    "away": a_name,
                    "hs":   int(hs),
                    "as_":  int(as_),
                    "min":  minute,
                })
            except (TypeError, ValueError, KeyError):
                continue

    return live


@st.cache_data(ttl=30, show_spinner=False)
def fetch_live_inprogress() -> tuple:
    """Returns (live_dict, any_live: bool). Cached 30 s for near-real-time updates."""
    try:
        live = _run_async(_fotmob_fetch_inprogress())
    except Exception:
        return {g["id"]: [] for g in GROUPS_CONFIG}, False
    any_live = any(len(v) > 0 for v in live.values())
    return live, any_live


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
if "manual_mode" not in st.session_state:
    st.session_state.manual_mode = False

# On every load: if we're in the tournament window and not in manual mode, pull live data
if not st.session_state.manual_mode and WC_REF_DATE <= date.today() <= WC2026_GROUP_END:
    _live, _live_status = fetch_live_wc_results()
    _n_live = sum(len(v) for v in _live.values())
    if _n_live > 0:
        st.session_state.results  = _live
    elif "results" not in st.session_state:
        st.session_state.results  = copy.deepcopy(EMPTY_RESULTS)
    st.session_state.live_status = _live_status

    # In-progress live scores (separate from finished results — not fed to simulation)
    _inprogress, _any_live = fetch_live_inprogress()
    st.session_state.live_inprogress = _inprogress
    st.session_state.any_live        = _any_live
else:
    if "results" not in st.session_state:
        st.session_state.results = copy.deepcopy(EMPTY_RESULTS)
    st.session_state.live_status     = None
    st.session_state.live_inprogress = {g["id"]: [] for g in GROUPS_CONFIG}
    st.session_state.any_live        = False

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def get_group(gid): return next(g for g in GROUPS_CONFIG if g["id"] == gid)

def compute_standings(gid):
    g = get_group(gid)
    s = [{"name":t,"idx":i,"w":0,"d":0,"l":0,"gf":0,"ga":0,"pts":0}
         for i,t in enumerate(g["teams"])]
    for r in st.session_state.results[gid]:
        t1,t2,g1,g2 = r["t1"],r["t2"],r["s1"],r["s2"]
        s[t1]["gf"]+=g1; s[t1]["ga"]+=g2; s[t2]["gf"]+=g2; s[t2]["ga"]+=g1
        if   g1>g2: s[t1]["w"]+=1; s[t1]["pts"]+=3; s[t2]["l"]+=1
        elif g2>g1: s[t2]["w"]+=1; s[t2]["pts"]+=3; s[t1]["l"]+=1
        else: s[t1]["d"]+=1; s[t2]["d"]+=1; s[t1]["pts"]+=1; s[t2]["pts"]+=1
    for t in s: t["gd"] = t["gf"] - t["ga"]
    played = st.session_state.results[gid]
    return _sort_group(s, played, g["teams"])

def get_remaining(gid):
    played = st.session_state.results[gid]
    return [[a,b] for a,b in ALL_PAIRS
            if not any((r["t1"]==a and r["t2"]==b) or
                       (r["t1"]==b and r["t2"]==a) for r in played)]

def gd_fmt(gd): return f"+{gd}" if gd>0 else str(gd)
def gd_cls(gd): return "gd-pos" if gd>0 else ("gd-neg" if gd<0 else "")

def pill_cls(p):
    if p >= 75: return "p-safe"
    if p >= 50: return "p-likely"
    if p >= 25: return "p-bubble"
    return "p-danger"

def rank_cls(i):
    if i < 8:  return "in"
    if i < 10: return "cut"
    return "out"

def gd_bucket(gd):
    return max(-6, min(6, gd))

def _h2h_stats(team_name, opponents, h2h):
    """H2H points, GD, and GF for team_name against a list of opponents."""
    pts = gd = gf = 0
    for opp in opponents:
        if opp in h2h.get(team_name, {}):
            tgf, tga = h2h[team_name][opp]
            gf  += tgf
            gd  += tgf - tga
            if   tgf > tga: pts += 3
            elif tgf == tga: pts += 1
    return pts, gd, gf

def _sort_group(standings, all_matches, team_names):
    """
    Sort group standings by the correct FIFA tiebreaker order:
      overall pts → H2H pts → H2H GD → H2H GF → overall GD → overall GF → random
    H2H stats are computed only among teams tied on overall points.
    """
    h2h: dict = {}
    for m in all_matches:
        n1 = team_names[m["t1"]]
        n2 = team_names[m["t2"]]
        h2h.setdefault(n1, {})[n2] = (m["s1"], m["s2"])
        h2h.setdefault(n2, {})[n1] = (m["s2"], m["s1"])

    from collections import defaultdict
    buckets: dict = defaultdict(list)
    for t in standings:
        buckets[t["pts"]].append(t)

    result = []
    for pts in sorted(buckets.keys(), reverse=True):
        group = buckets[pts]
        if len(group) == 1:
            result.extend(group)
        else:
            names = [t["name"] for t in group]
            def sort_key(t, names=names):
                opps = [n for n in names if n != t["name"]]
                hp, hgd, hgf = _h2h_stats(t["name"], opps, h2h)
                return (-hp, -hgd, -hgf, -t["gd"], -t["gf"], random.random())
            result.extend(sorted(group, key=sort_key))
    return result

def cell_color(pct):
    if pct is None: return "rgba(46,51,71,.2)"
    if pct >= 90:   return "rgba(34,197,94,.35)"
    if pct >= 70:   return "rgba(34,197,94,.22)"
    if pct >= 50:   return "rgba(134,239,172,.18)"
    if pct >= 30:   return "rgba(245,158,11,.22)"
    if pct >= 10:   return "rgba(239,68,68,.18)"
    return "rgba(239,68,68,.10)"

def cell_text_color(pct):
    if pct is None: return "var(--muted)"
    if pct >= 70:   return "#4ade80"
    if pct >= 50:   return "#86efac"
    if pct >= 30:   return "#fbbf24"
    return "#f87171"

# ─────────────────────────────────────────────────────────────────────────────
# SIMULATION ENGINE
# ─────────────────────────────────────────────────────────────────────────────
def nb_rnd(lam: float) -> int:
    lam = max(lam, 0.01)
    r   = NB_DISPERSION
    p   = r / (r + lam)
    return int(np.random.negative_binomial(r, p))


def sim_group_final(gid: str, team_stats: dict, results_snap: dict):
    g = get_group(gid)
    s = [{"name":t,"idx":i,"w":0,"d":0,"l":0,"gf":0,"ga":0,"pts":0}
         for i,t in enumerate(g["teams"])]
    played    = results_snap[gid]
    remaining = [[a,b] for a,b in ALL_PAIRS
                 if not any((r["t1"]==a and r["t2"]==b) or
                            (r["t1"]==b and r["t2"]==a) for r in played)]
    all_m = list(played) + [
        {"t1":a,"t2":b,
         "s1":nb_rnd(match_lambda(g["teams"][a], g["teams"][b], team_stats)),
         "s2":nb_rnd(match_lambda(g["teams"][b], g["teams"][a], team_stats))}
        for a,b in remaining
    ]
    for r in all_m:
        t1,t2,g1,g2 = r["t1"],r["t2"],r["s1"],r["s2"]
        s[t1]["gf"]+=g1; s[t1]["ga"]+=g2; s[t2]["gf"]+=g2; s[t2]["ga"]+=g1
        if   g1>g2: s[t1]["w"]+=1; s[t1]["pts"]+=3; s[t2]["l"]+=1
        elif g2>g1: s[t2]["w"]+=1; s[t2]["pts"]+=3; s[t1]["l"]+=1
        else: s[t1]["d"]+=1; s[t2]["d"]+=1; s[t1]["pts"]+=1; s[t2]["pts"]+=1
    for t in s: t["gd"] = t["gf"] - t["ga"]
    return _sort_group(s, all_m, g["teams"])


def run_monte_carlo(n_sims: int, team_stats: dict, ftable: dict = None):
    snap      = copy.deepcopy(st.session_state.results)
    group_ids = [g["id"] for g in GROUPS_CONFIG]

    placement_counts = {
        gid: {t: [0,0,0,0] for t in get_group(gid)["teams"]}
        for gid in group_ids
    }
    third_total   = {gid: {t:0 for t in get_group(gid)["teams"]} for gid in group_ids}
    third_adv     = {gid: {t:0 for t in get_group(gid)["teams"]} for gid in group_ids}
    third_pts_sum = {gid: {t:0 for t in get_group(gid)["teams"]} for gid in group_ids}
    third_gd_sum  = {gid: {t:0 for t in get_group(gid)["teams"]} for gid in group_ids}

    pts_gd = {}
    pts_thresh = [0]*10

    # ── Bracket counters ──────────────────────────────────────────────────────
    r32_s1: dict = {mn: {} for mn in range(73, 89)}   # slot-1 occupancy
    r32_s2: dict = {mn: {} for mn in range(73, 89)}   # slot-2 occupancy
    r32_wc: dict = {mn: {} for mn in range(73, 89)}   # R32 win counts  (match-indexed)
    r32_mu: dict = {mn: {} for mn in range(73, 89)}   # matchup pair counts (t1, t2)
    r16_wc: dict = {}                                  # R16 wins flat  (team→count, for table)
    qf_wc:  dict = {}                                  # QF wins flat
    sf_wc:  dict = {}                                  # SF wins flat
    r16_wm: dict = {mn: {} for mn in [89,90,91,92,93,94,95,96]}  # R16 wins by match
    qf_wm:  dict = {mn: {} for mn in [97,98,99,100]}             # QF wins by match
    sf_wm:  dict = {mn: {} for mn in [101,102]}                  # SF wins by match
    final_c: dict = {}
    champ_c: dict = {}

    def _ko(t1: str, t2: str) -> str:
        """Simulate one knockout match (with penalties on draw); returns winner."""
        lam1 = match_lambda(t1, t2, team_stats)
        lam2 = match_lambda(t2, t1, team_stats)
        s1, s2 = nb_rnd(lam1), nb_rnd(lam2)
        if s1 > s2: return t1
        if s2 > s1: return t2
        # Penalty shootout — use xG ratio as tiebreak proxy
        return t1 if random.random() < lam1 / (lam1 + lam2 + 1e-9) else t2

    for _ in range(n_sims):
        thirds = []
        group_ranked: dict = {}
        for gid in group_ids:
            ranked = sim_group_final(gid, team_stats, snap)
            group_ranked[gid] = ranked
            for pos, t in enumerate(ranked):
                placement_counts[gid][t["name"]][pos] += 1
            third = ranked[2]
            third_total[gid][third["name"]] += 1
            third_pts_sum[gid][third["name"]] += third["pts"]
            third_gd_sum[gid][third["name"]]  += third["gd"]
            thirds.append({
                "gid": gid, "name": third["name"],
                "pts": third["pts"], "gd": third["gd"], "gf": third["gf"],
            })

        thirds.sort(key=lambda t:(-t["pts"],-t["gd"],-t["gf"],random.random()))

        for i, t in enumerate(thirds):
            key = (min(t["pts"], 9), gd_bucket(t["gd"]))
            if key not in pts_gd: pts_gd[key] = [0, 0]
            pts_gd[key][1] += 1
            if i < 8:
                third_adv[t["gid"]][t["name"]] += 1
                pts_gd[key][0] += 1

        pts_thresh[min(thirds[7]["pts"], 9)] += 1

        # ── Bracket simulation ─────────────────────────────────────────────────
        g1        = {gid: group_ranked[gid][0]["name"] for gid in group_ids}
        g2        = {gid: group_ranked[gid][1]["name"] for gid in group_ids}
        adv_key   = frozenset(t["gid"] for t in thirds[:8])
        third_lu  = {t["gid"]: t["name"] for t in thirds[:8]}
        tpm       = (ftable or {}).get(adv_key, {})

        def _res(label):
            if label.startswith("1"): return g1.get(label[1])
            if label.startswith("2"): return g2.get(label[1])
            if label.startswith("3"): return third_lu.get(label[1])
            return None

        # R32 — matches 73-88
        r32_tmpl = [
            (73,"2A","2B"),(74,"1E",tpm.get("1E","3D")),(75,"1F","2C"),(76,"1C","2F"),
            (77,"1I",tpm.get("1I","3F")),(78,"2E","2I"),(79,"1A",tpm.get("1A","3E")),
            (80,"1L",tpm.get("1L","3K")),(81,"1D",tpm.get("1D","3I")),
            (82,"1G",tpm.get("1G","3J")),(83,"2K","2L"),(84,"1H","2J"),
            (85,"1B",tpm.get("1B","3G")),(86,"1J","2H"),
            (87,"1K",tpm.get("1K","3L")),(88,"2D","2G"),
        ]
        r32_it: dict = {}
        for mn, l1, l2 in r32_tmpl:
            t1, t2 = _res(l1), _res(l2)
            if not t1 or not t2: continue
            r32_s1[mn][t1] = r32_s1[mn].get(t1, 0) + 1
            r32_s2[mn][t2] = r32_s2[mn].get(t2, 0) + 1
            r32_mu[mn][(t1, t2)] = r32_mu[mn].get((t1, t2), 0) + 1
            w = _ko(t1, t2)
            r32_wc[mn][w] = r32_wc[mn].get(w, 0) + 1
            r32_it[mn] = w

        # R16 — matches 89-96
        r16_it: dict = {}
        for mn, m1, m2 in [(89,74,77),(90,73,75),(91,76,78),(92,79,80),
                            (93,83,84),(94,81,82),(95,86,88),(96,85,87)]:
            t1, t2 = r32_it.get(m1), r32_it.get(m2)
            if not t1 or not t2: continue
            w = _ko(t1, t2)
            r16_wc[w] = r16_wc.get(w, 0) + 1
            r16_wm[mn][w] = r16_wm[mn].get(w, 0) + 1
            r16_it[mn] = w

        # QF — matches 97-100
        qf_it: dict = {}
        for mn, m1, m2 in [(97,89,90),(98,93,94),(99,91,92),(100,95,96)]:
            t1, t2 = r16_it.get(m1), r16_it.get(m2)
            if not t1 or not t2: continue
            w = _ko(t1, t2)
            qf_wc[w] = qf_wc.get(w, 0) + 1
            qf_wm[mn][w] = qf_wm[mn].get(w, 0) + 1
            qf_it[mn] = w

        # SF — matches 101-102
        sf_it: dict = {}
        for mn, m1, m2 in [(101,97,98),(102,99,100)]:
            t1, t2 = qf_it.get(m1), qf_it.get(m2)
            if not t1 or not t2: continue
            final_c[t1] = final_c.get(t1, 0) + 1
            final_c[t2] = final_c.get(t2, 0) + 1
            w = _ko(t1, t2)
            sf_wc[w] = sf_wc.get(w, 0) + 1
            sf_wm[mn][w] = sf_wm[mn].get(w, 0) + 1
            sf_it[mn] = w

        # Final
        f1, f2 = sf_it.get(101), sf_it.get(102)
        if f1 and f2:
            champ = _ko(f1, f2)
            champ_c[champ] = champ_c.get(champ, 0) + 1

    # ── build per-group summary ──────────────────────────────────────────────
    group_data = []
    for gid in group_ids:
        teams = get_group(gid)["teams"]
        n = n_sims

        likely_3rd = max(teams, key=lambda t: third_total[gid][t])
        t3c = third_total[gid][likely_3rd]

        p3rd        = t3c / n * 100
        exp_pts_3rd = third_pts_sum[gid][likely_3rd] / t3c if t3c else 0
        exp_gd_3rd  = third_gd_sum[gid][likely_3rd]  / t3c if t3c else 0
        adv_given   = third_adv[gid][likely_3rd] / t3c * 100 if t3c else 0
        p_advance   = third_adv[gid][likely_3rd] / n * 100

        all_teams = {}
        for t in teams:
            tc = third_total[gid][t]
            all_teams[t] = {
                "p1":  placement_counts[gid][t][0] / n * 100,
                "p2":  placement_counts[gid][t][1] / n * 100,
                "p3":  placement_counts[gid][t][2] / n * 100,
                "p4":  placement_counts[gid][t][3] / n * 100,
                "p3_adv": third_adv[gid][t] / n * 100,
            }

        group_data.append({
            "gid":        gid,
            "team":       likely_3rd,
            "flag":       FLAGS.get(likely_3rd, "🏳"),
            "p3rd":       p3rd,
            "exp_pts":    exp_pts_3rd,
            "exp_gd":     exp_gd_3rd,
            "adv_given":  adv_given,
            "p_advance":  p_advance,
            "all_teams":  all_teams,
        })

    group_data.sort(key=lambda x: -x["adv_given"])

    bracket_data = {
        "r32_s1": r32_s1,
        "r32_s2": r32_s2,
        "r32_w":  r32_wc,
        "r32_mu": r32_mu,
        "r16_w":  r16_wc,   # flat team→count (for tournament table)
        "qf_w":   qf_wc,
        "sf_w":   sf_wc,
        "r16_wm": r16_wm,   # match-indexed (for bracket view)
        "qf_wm":  qf_wm,
        "sf_wm":  sf_wm,
        "final":  final_c,
        "champ":  champ_c,
    }

    return group_data, pts_gd, pts_thresh, n_sims, bracket_data


# ─────────────────────────────────────────────────────────────────────────────
# HTML BUILDERS
# ─────────────────────────────────────────────────────────────────────────────

def bar_html(pct, color="#6366f1", max_w=80):
    w = max(0, min(pct, 100)) / 100 * max_w
    return (f'<div class="bar-wrap" style="width:{max_w}px">'
            f'<div class="bar-fill" style="width:{w:.1f}px;background:{color}"></div>'
            f'</div>')

def build_best_thirds_table(group_data, n_sims):
    rows = ""
    for i, g in enumerate(group_data):
        cut  = "cutline" if i == 7 else ""
        rc   = rank_cls(i)
        pill = pill_cls(g["p_advance"])
        gpc  = pill_cls(g["p3rd"])
        ag_c = pill_cls(g["adv_given"])
        gd_c = gd_cls(round(g["exp_gd"]))

        cnt_3rd = round(g["p3rd"]    * n_sims / 100)
        cnt_adv = round(g["p_advance"] * n_sims / 100)

        def count_sub(n):
            return f'<br><span style="font-size:9px;color:var(--muted);font-weight:400">{n:,}</span>'

        rows += f"""
<tr class="{cut}">
  <td><span class="rank-num {rc}">{i+1}</span></td>
  <td class="left">
    <div class="team-cell">
      <span class="team-flag">{g["flag"]}</span>
      <div>
        <div class="team-name">{g["team"]}</div>
        <div class="team-grp">Group {g["gid"]}</div>
      </div>
    </div>
  </td>
  <td><span class="pill {gpc}">{g["p3rd"]:.0f}%</span>{count_sub(cnt_3rd)}</td>
  <td style="font-family:monospace;font-weight:600">{g["exp_pts"]:.1f}</td>
  <td class="{gd_c}" style="font-family:monospace">{g["exp_gd"]:+.1f}</td>
  <td><span class="pill {ag_c}">{g["adv_given"]:.0f}%</span></td>
  <td><span class="pill {pill}">{g["p_advance"]:.1f}%</span>{count_sub(cnt_adv)}</td>
</tr>"""

    return f"""
<div style="background:var(--surf);border:1px solid var(--border);border-radius:10px;overflow:hidden">
  <div style="background:var(--surf2);padding:10px 14px;border-bottom:1px solid var(--border);
              display:flex;align-items:center;justify-content:space-between">
    <span style="font-weight:700;font-size:14px;color:var(--text)">
      Most Likely Third-Place Team — Per Group
    </span>
    <span style="font-size:11px;color:var(--muted)">{n_sims:,} simulations</span>
  </div>
  <table class="bt-table">
    <thead><tr>
      <th style="width:32px">#</th>
      <th class="left">Most Likely 3rd</th>
      <th>P(3rd)</th>
      <th>Exp&nbsp;Pts</th>
      <th>Exp&nbsp;GD</th>
      <th>P(adv&nbsp;|&nbsp;3rd)</th>
      <th>P(advance)</th>
    </tr></thead>
    <tbody>{rows}</tbody>
  </table>
  <div style="padding:7px 14px;font-size:11px;color:var(--muted);border-top:1px solid var(--border)">
    <b style="color:var(--text)">P(3rd)</b> = prob this team finishes 3rd in their group &nbsp;·&nbsp;
    <b style="color:var(--text)">P(adv | 3rd)</b> = if they finish 3rd, prob they crack top 8 &nbsp;·&nbsp;
    <b style="color:var(--text)">P(advance)</b> = P(3rd) × P(adv | 3rd) &nbsp;·&nbsp;
    &#x2014; line = 8th/9th cutoff
  </div>
</div>"""


def build_pts_gd_matrix(pts_gd, pts_thresh, n_sims):
    pts_range = range(9, -1, -1)

    header = '<th class="left" style="white-space:nowrap">Pts&nbsp;\\ GD</th>' + "".join(
        f'<th style="font-size:9px;padding:4px 5px">{lbl}</th>' for lbl in GD_LABELS
    )

    rows = ""
    for pts in pts_range:
        cells = ""
        any_data = False
        for b in GD_BUCKETS:
            key = (min(pts, 9), b)
            v   = pts_gd.get(key)
            if not v or v[1] == 0:
                cells += '<td class="empty" style="font-size:9px">—</td>'
            else:
                adv, total = v
                rate = adv / total * 100
                any_data = True
                bg = cell_color(rate)
                fc = cell_text_color(rate)
                cells += (
                    f'<td style="background:{bg};color:{fc};padding:4px 5px;vertical-align:middle">'
                    f'<div style="font-weight:700;font-size:11px">{rate:.0f}%</div>'
                    f'<div style="font-size:9px;color:var(--muted);font-weight:400;margin-top:1px">'
                    f'{adv:,}/{total:,}</div>'
                    f'</td>'
                )
        if any_data:
            freq = pts_thresh[pts] / n_sims * 100 if pts < 10 else 0
            freq_s = (f'<div style="font-size:9px;color:var(--muted);font-weight:400">'
                      f'{pts_thresh[pts]:,} sims ({freq:.0f}%)</div>') if freq > 0.1 else ""
            rows += f'<tr><td class="pts-label" style="vertical-align:middle;white-space:nowrap"><div style="font-size:12px">{pts}</div>{freq_s}</td>{cells}</tr>'

    return f"""
<div class="matrix-wrap">
  <div class="matrix-hdr">Advancement Rate by Points &amp; Goal Difference</div>
  <div style="overflow-x:auto">
  <table class="mx-tbl" style="min-width:700px">
    <thead><tr>{header}</tr></thead>
    <tbody>{rows}</tbody>
  </table>
  </div>
  <div style="padding:7px 14px;font-size:11px;color:var(--muted);border-top:1px solid var(--border)">
    <b style="color:var(--text)">Cell</b> = advancement rate (%) &nbsp;·&nbsp;
    <b style="color:var(--text)">adv/total</b> = simulations where team advanced / total with that Pts+GD &nbsp;·&nbsp;
    <b style="color:var(--text)">Pts column</b> = how often the cutline fell at that point total
  </div>
</div>"""


def build_group_card(gid, team_stats, all_teams_sim=None, n_sims=0, live_matches=None):
    g            = get_group(gid)
    standings    = compute_standings(gid)
    played       = len(st.session_state.results[gid])
    results      = st.session_state.results[gid]
    pos_cls      = ["pos1","pos2","pos3","pos4"]
    live_matches = live_matches or []

    rows = ""
    for i, t in enumerate(standings):
        flag   = FLAGS.get(t["name"],"🏳")
        p3_cls = " p3" if i==2 else ""
        rows += f"""<tr class="{p3_cls}">
          <td class="{pos_cls[i]}">{i+1}</td>
          <td>{flag} {t["name"]}</td>
          <td>{t["w"]}</td><td>{t["d"]}</td><td>{t["l"]}</td>
          <td class="{gd_cls(t["gd"])}">{gd_fmt(t["gd"])}</td>
          <td style="font-weight:700">{t["pts"]}</td>
        </tr>"""

    res_html = "".join(
        f'<div class="res-row">{g["teams"][r["t1"]]} '
        f'<span class="res-score">{r["s1"]}&ndash;{r["s2"]}</span> '
        f'{g["teams"][r["t2"]]}</div>'
        for r in results
    )

    # ── In-progress live scores (display only — not used in simulation) ──────
    live_html = ""
    for m in live_matches:
        h_flag  = FLAGS.get(m["home"], "🏳")
        a_flag  = FLAGS.get(m["away"], "🏳")
        min_txt = (f'<span style="color:#fbbf24;font-size:9px;margin-left:4px">{m["min"]}</span>'
                   if m["min"] else "")
        live_html += (
            f'<div class="res-row" style="background:rgba(239,68,68,.07);'
            f'border-left:3px solid #ef4444;padding-left:8px">'
            f'<span style="background:#ef4444;color:#fff;font-size:8px;font-weight:800;'
            f'padding:1px 5px;border-radius:3px;margin-right:6px;letter-spacing:.04em">LIVE</span>'
            f'{h_flag} {m["home"]} '
            f'<span class="res-score">{m["hs"]}&ndash;{m["as_"]}</span> '
            f'{a_flag} {m["away"]}{min_txt}'
            f'</div>'
        )

    plc_html = ""
    if all_teams_sim:
        plc_rows = ""
        for t in standings:
            nm  = t["name"]
            sim = all_teams_sim.get(nm, {})
            p1  = sim.get("p1", 0)
            p2  = sim.get("p2", 0)
            p3  = sim.get("p3", 0)
            p4  = sim.get("p4", 0)

            def pc(v, hi_col):
                c   = hi_col if v >= 40 else ("var(--muted)" if v < 10 else "#fbbf24")
                fw  = "700" if v >= 40 else "400"
                cnt = f"{round(v * n_sims / 100):,}" if n_sims else ""
                return (
                    f'<span style="color:{c};font-weight:{fw}">{v:.0f}%</span>'
                    + (f'<br><span style="color:var(--muted);font-size:9px;font-weight:400">{cnt}</span>' if cnt else "")
                )
            plc_rows += f"""<tr>
              <td>{FLAGS.get(nm,"🏳")} {nm}</td>
              <td>{pc(p1,"#4ade80")}</td>
              <td>{pc(p2,"#86efac")}</td>
              <td>{pc(p3,"#fbbf24")}</td>
              <td>{pc(p4,"#f87171")}</td>
            </tr>"""
        plc_html = f"""
<div class="plc-hdr">Simulated finish probability</div>
<table class="plc-tbl">
  <thead><tr><th>Team</th><th>1st</th><th>2nd</th><th>3rd</th><th>4th</th></tr></thead>
  <tbody>{plc_rows}</tbody>
</table>"""

    live_indicator = (
        ' <span style="background:#ef4444;color:#fff;font-size:8px;font-weight:800;'
        'padding:1px 5px;border-radius:3px;letter-spacing:.04em;vertical-align:middle">LIVE</span>'
        if live_matches else ""
    )

    return f"""
<div class="gc">
  <div class="gc-hdr">
    <span class="gid">Group {gid}{live_indicator}</span>
    <span class="gct">{played}/6 played</span>
  </div>
  <table class="gc-tbl">
    <thead><tr><th>#</th><th>Team</th><th>W</th><th>D</th><th>L</th><th>GD</th><th>Pts</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
  {live_html}{res_html}
  {plc_html}
</div>"""


def build_hist_table(yr):
    rows_sorted = sorted(
        yr["teams"],
        key=lambda t: (-(t["op"]+t["w"]), -(t["gf"]-t["ga"]), -t["gf"])
    )
    rows_html = ""
    for i, t in enumerate(rows_sorted):
        conv = t["op"] + t["w"]
        gd   = t["gf"] - t["ga"]
        cls  = "adv" if t["adv"] else "elim"
        cut  = " cutoff" if i == yr["advancing"] else ""
        pts_cells = (
            f'<td style="color:var(--muted)">{t["op"]}</td>'
            f'<td class="pts-conv">{conv}</td>'
            if yr["system"] != "3-1-0"
            else f'<td class="pts-conv">{t["op"]}</td>'
        )
        badge = ('<span class="badge-adv">&#x2713; ADV</span>' if t["adv"]
                 else '<span class="badge-elim">&#x2717; OUT</span>')
        rows_html += f"""<tr class="{cls}{cut}">
          <td style="color:var(--muted)">{t["group"]}</td>
          <td class="left">{t["team"]}</td>
          <td>{t["w"]}</td><td>{t["d"]}</td><td>{t["l"]}</td>
          <td>{t["gf"]}</td><td>{t["ga"]}</td>
          <td class="{gd_cls(gd)}">{gd_fmt(gd)}</td>
          {pts_cells}
          <td>{badge}</td>
        </tr>"""

    pts_heads = ('<th>Orig</th><th>Conv &#x25B2;</th>' if yr["system"] != "3-1-0"
                 else '<th>Pts</th>')
    return f"""
<div class="ht-wrap">
  <div class="ht-hdr">
    <span class="ht-yr">{yr["year"]}</span>
    <span class="ht-meta">{yr["host"]} &middot; {yr["note"]}</span>
    <span class="ht-badge">{yr["advancing"]}/{yr["total"]} advance</span>
  </div>
  <table class="ht-tbl">
    <thead><tr>
      <th>Grp</th><th class="left">Team</th>
      <th>W</th><th>D</th><th>L</th><th>GF</th><th>GA</th><th>GD</th>
      {pts_heads}<th>Result</th>
    </tr></thead>
    <tbody>{rows_html}</tbody>
  </table>
</div>"""


def build_r32_cards(bracket_data: dict, n_sims: int) -> str:
    """
    Full bracket tree (R32 → R16 → QF → SF → Final) with nested CSS connector
    lines. Only R32 match cards show matchup probabilities; R16/QF/SF/Final are
    empty bracket nodes — no future-round predictions.
    """
    r32_mu = bracket_data["r32_mu"]
    TOP_N  = 5
    BR     = "var(--border)"

    # ── R32 match card ───────────────────────────────────────────────────────
    def match_card(mn):
        lbl1, lbl2 = R32_SLOT_LABELS[mn]
        top_mu  = sorted(r32_mu[mn].items(), key=lambda x: -x[1])[:TOP_N]
        top_cnt = top_mu[0][1] if top_mu else 1
        rows = ""
        for (t1, t2), cnt in top_mu:
            f1 = FLAGS.get(t1, "");  f2 = FLAGS.get(t2, "")
            p  = cnt / n_sims * 100
            bw = cnt / top_cnt * 100
            pc = ("p-safe" if p >= 20 else "p-likely" if p >= 10
                  else "p-bubble" if p >= 4 else "p-danger")
            rows += (
                f'<div style="display:flex;align-items:center;gap:5px;margin-bottom:5px">'
                f'<span style="font-size:13px;line-height:1">{f1}</span>'
                f'<span style="font-size:10.5px;font-weight:600;color:var(--text);'
                f'white-space:nowrap">{t1}</span>'
                f'<span style="font-size:9px;color:var(--muted);margin:0 1px">vs</span>'
                f'<span style="font-size:13px;line-height:1">{f2}</span>'
                f'<span style="font-size:10.5px;font-weight:600;color:var(--text);'
                f'white-space:nowrap;flex:1;overflow:hidden;text-overflow:ellipsis">{t2}</span>'
                f'<span class="pill {pc}" style="font-size:9.5px;min-width:34px;padding:2px 4px;'
                f'flex-shrink:0">{p:.1f}%</span>'
                f'<div style="width:44px;height:7px;background:rgba(100,116,139,.18);'
                f'border-radius:2px;overflow:hidden;flex-shrink:0">'
                f'<div style="height:100%;width:{bw:.0f}%;background:var(--accent);'
                f'border-radius:2px"></div></div>'
                f'</div>'
            )
        return (
            f'<div style="background:var(--surf);border:1px solid {BR};border-radius:7px;'
            f'padding:9px 11px;width:320px;box-sizing:border-box;flex-shrink:0">'
            f'<div style="display:flex;justify-content:space-between;align-items:baseline;'
            f'margin-bottom:6px">'
            f'<span style="font-size:10.5px;font-weight:800;color:var(--gold)">Match {mn}</span>'
            f'<span style="font-size:8px;color:var(--muted)">{lbl1} · {lbl2}</span>'
            f'</div>'
            f'<div style="font-size:7.5px;font-weight:700;color:var(--muted);'
            f'text-transform:uppercase;letter-spacing:.06em;margin-bottom:5px">'
            f'Most Likely Matchup</div>'
            + rows +
            f'</div>'
        )

    # ── Empty bracket node (R16 / QF / SF) ──────────────────────────────────
    def node(label):
        return (
            f'<div style="display:flex;align-items:center;justify-content:center;'
            f'padding:5px 8px;font-size:8.5px;font-weight:700;color:var(--gold);'
            f'border:1px solid {BR};border-radius:5px;background:var(--surf2);'
            f'text-align:center;white-space:nowrap;line-height:1.35">{label}</div>'
        )

    # ── Bracket pair: stack two items, add connector + node on one side ──────
    def bpair(top, bottom, label, side, gap="8px"):
        nd = node(label)
        if side == "right":
            conn = (
                f'<div style="display:flex;flex-direction:column;width:80px;flex-shrink:0">'
                f'<div style="flex:1;border-right:2px solid {BR};border-bottom:2px solid {BR};'
                f'border-radius:0 0 5px 0;margin-left:36px"></div>'
                f'{nd}'
                f'<div style="flex:1;border-right:2px solid {BR};border-top:2px solid {BR};'
                f'border-radius:0 5px 0 0;margin-left:36px"></div>'
                f'</div>'
            )
            return (
                f'<div style="display:flex;align-items:stretch">'
                f'<div style="display:flex;flex-direction:column;gap:{gap}">'
                f'{top}{bottom}</div>'
                f'{conn}</div>'
            )
        else:
            conn = (
                f'<div style="display:flex;flex-direction:column;width:80px;flex-shrink:0">'
                f'<div style="flex:1;border-left:2px solid {BR};border-bottom:2px solid {BR};'
                f'border-radius:0 0 0 5px;margin-right:36px"></div>'
                f'{nd}'
                f'<div style="flex:1;border-left:2px solid {BR};border-top:2px solid {BR};'
                f'border-radius:5px 0 0 0;margin-right:36px"></div>'
                f'</div>'
            )
            return (
                f'<div style="display:flex;align-items:stretch">'
                f'{conn}'
                f'<div style="display:flex;flex-direction:column;gap:{gap}">'
                f'{top}{bottom}</div>'
                f'</div>'
            )

    # ── Left bracket  (R32 74–80, reads left → right) ───────────────────────
    r16_89 = bpair(match_card(74), match_card(77), "R16<br>M89", "right")
    r16_90 = bpair(match_card(73), match_card(75), "R16<br>M90", "right")
    r16_91 = bpair(match_card(76), match_card(78), "R16<br>M91", "right")
    r16_92 = bpair(match_card(79), match_card(80), "R16<br>M92", "right")

    qf_97  = bpair(r16_89, r16_90, "QF<br>M97",  "right", gap="14px")
    qf_99  = bpair(r16_91, r16_92, "QF<br>M99",  "right", gap="14px")

    sf_101 = bpair(qf_97,  qf_99,  "SF<br>M101", "right", gap="20px")

    # ── Right bracket (R32 81–88, reads right → left) ───────────────────────
    r16_93 = bpair(match_card(83), match_card(84), "R16<br>M93", "left")
    r16_94 = bpair(match_card(81), match_card(82), "R16<br>M94", "left")
    r16_95 = bpair(match_card(86), match_card(88), "R16<br>M95", "left")
    r16_96 = bpair(match_card(85), match_card(87), "R16<br>M96", "left")

    qf_98  = bpair(r16_93, r16_94, "QF<br>M98",  "left", gap="14px")
    qf_100 = bpair(r16_95, r16_96, "QF<br>M100", "left", gap="14px")

    sf_102 = bpair(qf_98,  qf_100, "SF<br>M102", "left", gap="20px")

    # ── Final center column ──────────────────────────────────────────────────
    final = (
        f'<div style="display:flex;flex-direction:column;align-items:center;'
        f'justify-content:center;padding:14px 12px;font-size:10px;font-weight:800;'
        f'color:var(--gold);border:2px solid var(--gold);border-radius:8px;'
        f'background:var(--surf2);flex-shrink:0;align-self:stretch;'
        f'writing-mode:vertical-lr;text-orientation:mixed;letter-spacing:.12em;'
        f'white-space:nowrap">\U0001f3c6 FINAL \U0001f3c6</div>'
    )

    return (
        f'<div style="background:var(--surf);border:1px solid {BR};'
        f'border-radius:10px;overflow:hidden">'
        f'<div style="background:var(--surf2);padding:9px 14px;'
        f'border-bottom:1px solid {BR};display:flex;justify-content:space-between;'
        f'align-items:center">'
        f'<span style="font-weight:700;font-size:14px;color:var(--text)">'
        f'Round of 32 — Matchup Probabilities</span>'
        f'<span style="font-size:11px;color:var(--muted)">{n_sims:,} simulations</span>'
        f'</div>'
        f'<div style="padding:14px;overflow-x:auto">'
        f'<div style="display:flex;align-items:stretch;min-width:max-content">'
        f'{sf_101}{final}{sf_102}'
        f'</div>'
        f'</div>'
        f'<div style="padding:6px 14px;font-size:11px;color:var(--muted);'
        f'border-top:1px solid {BR}">'
        f'% = P(that exact matchup is played) across all simulations. '
        f'R16 / QF / SF / Final show bracket path only — no predictions.'
        f'</div></div>'
    )


def build_bracket_view(bracket_data: dict, n_sims: int) -> str:
    """
    Predicted bracket (R32 → Final). Each match shows the two most likely
    opponents with head-to-head win odds (normalized between the top 2 teams
    projected to meet in that slot). Gold = predicted winner / higher odds.
    """
    r32_s1 = bracket_data["r32_s1"]
    r32_s2 = bracket_data["r32_s2"]
    r32_w  = bracket_data["r32_w"]
    r16_w  = bracket_data["r16_wm"]
    qf_w   = bracket_data["qf_wm"]
    sf_w   = bracket_data["sf_wm"]
    final  = bracket_data["final"]
    champ  = bracket_data["champ"]

    def top1(d):
        """Return (team, count) for the most frequent team in d."""
        if not d: return "TBD", 0
        return max(d.items(), key=lambda x: x[1])

    def win_odds(d):
        """
        Top 2 teams from dict d, with head-to-head win % normalized between them.
        Returns ((t1,p1), (t2,p2)) where p1+p2 = 100.
        """
        if not d: return ("TBD", 50.0), ("TBD", 50.0)
        ranked = sorted(d.items(), key=lambda x: -x[1])
        t1, c1 = ranked[0]
        t2, c2 = ranked[1] if len(ranked) > 1 else ("TBD", 0)
        total  = c1 + c2 or 1
        return (t1, c1 / total * 100), (t2, c2 / total * 100)

    def slot_html(team, pct, is_win=False, align="left"):
        flag = FLAGS.get(team, "")
        bg  = "rgba(251,191,36,.15)" if is_win else "rgba(22,26,40,.8)"
        bdr = "1px solid rgba(251,191,36,.5)" if is_win else "1px solid rgba(46,51,71,.6)"
        tc  = "#fbbf24" if is_win else "#9aa3be"
        pc  = "rgba(251,191,36,.9)" if is_win else "rgba(107,116,148,.8)"
        fw  = "700" if is_win else "500"
        ps  = f"{pct:.0f}%" if pct >= 0.5 else ""
        if align == "right":
            inner = (f'<span style="font-size:8px;color:{pc};flex-shrink:0;margin-right:5px">{ps}</span>'
                     f'<span>{team}&nbsp;{flag}</span>')
            jc = "flex-end"
        else:
            inner = (f'<span>{flag}&nbsp;{team}</span>'
                     f'<span style="font-size:8px;color:{pc};flex-shrink:0;margin-left:5px">{ps}</span>')
            jc = "flex-start"
        return (f'<div style="background:{bg};border:{bdr};border-radius:3px;padding:3px 7px;'
                f'font-size:0.71rem;font-weight:{fw};color:{tc};white-space:nowrap;overflow:hidden;'
                f'max-width:148px;min-width:108px;display:flex;justify-content:{jc};align-items:center;">'
                f'{inner}</div>')

    def mpair(t1, p1, t2, p2, winner, align="left"):
        return (f'<div style="display:flex;flex-direction:column;gap:2px;margin:4px 0;">'
                + slot_html(t1, p1, t1 == winner, align)
                + slot_html(t2, p2, t2 == winner, align)
                + '</div>')

    def col(html, label):
        return (f'<div style="display:flex;flex-direction:column;">'
                f'<div style="font-size:8.5px;font-weight:700;color:var(--muted);text-transform:uppercase;'
                f'letter-spacing:.07em;margin-bottom:6px;text-align:center">{label}</div>'
                f'<div style="display:flex;flex-direction:column;justify-content:space-around;flex:1;">'
                f'{html}</div></div>')

    # ── Round helpers ─────────────────────────────────────────────────────────
    def _norm(w1, w2):
        """Normalize two win counts to percentages summing to 100."""
        total = w1 + w2 or 1
        return w1/total*100, w2/total*100

    def mr32(mn, align="left"):
        # t1 = most likely group-winner slot; t2 = most likely best-3rd slot.
        t1, _ = top1(r32_s1[mn]);  t2, _ = top1(r32_s2[mn])
        w1 = r32_w[mn].get(t1, 0); w2 = r32_w[mn].get(t2, 0)
        p1, p2 = _norm(w1, w2)
        return mpair(t1, p1, t2, p2, t1 if w1 >= w2 else t2, align)

    def mr16(mn, f1, f2, align="left"):
        # t1/t2 = most likely winner of each R32 feeder match.
        t1, _ = top1(r32_w[f1]);  t2, _ = top1(r32_w[f2])
        w1 = r16_w[mn].get(t1, 0); w2 = r16_w[mn].get(t2, 0)
        p1, p2 = _norm(w1, w2)
        return mpair(t1, p1, t2, p2, t1 if w1 >= w2 else t2, align)

    def mqf(mn, f1, f2, align="left"):
        # t1/t2 = most likely winner of each R16 feeder match.
        t1, _ = top1(r16_w[f1]);  t2, _ = top1(r16_w[f2])
        w1 = qf_w[mn].get(t1, 0); w2 = qf_w[mn].get(t2, 0)
        p1, p2 = _norm(w1, w2)
        return mpair(t1, p1, t2, p2, t1 if w1 >= w2 else t2, align)

    def msf(mn, f1, f2, align="left"):
        # t1/t2 = most likely winner of each QF feeder match.
        t1, _ = top1(qf_w[f1]);  t2, _ = top1(qf_w[f2])
        w1 = sf_w[mn].get(t1, 0); w2 = sf_w[mn].get(t2, 0)
        p1, p2 = _norm(w1, w2)
        return mpair(t1, p1, t2, p2, t1 if w1 >= w2 else t2, align)

    # ── Build columns ─────────────────────────────────────────────────────────
    R = "right"

    l_r32 = col(mr32(74)+mr32(77)+mr32(73)+mr32(75)+mr32(76)+mr32(78)+mr32(79)+mr32(80), "R32")
    l_r16 = col(mr16(89,74,77)+mr16(90,73,75)+mr16(91,76,78)+mr16(92,79,80), "R16")
    l_qf  = col(mqf(97,89,90)+mqf(99,91,92), "QF")
    l_sf  = col(msf(101,97,98), "SF")

    r_r32 = col(mr32(83,R)+mr32(84,R)+mr32(81,R)+mr32(82,R)+mr32(86,R)+mr32(88,R)+mr32(85,R)+mr32(87,R), "R32")
    r_r16 = col(mr16(93,83,84,R)+mr16(94,81,82,R)+mr16(95,86,88,R)+mr16(96,85,87,R), "R16")
    r_qf  = col(mqf(98,93,94,R)+mqf(100,95,96,R), "QF")
    r_sf  = col(msf(102,99,100,R), "SF")

    # ── Final + Champion ──────────────────────────────────────────────────────
    # Finalists = most likely winners of each SF. Win odds from champ dict.
    f1, _ = top1(sf_w[101]);  f2, _ = top1(sf_w[102])
    fw1 = champ.get(f1, 0);   fw2 = champ.get(f2, 0)
    fp1, fp2 = _norm(fw1, fw2)
    ch, _   = top1(champ)
    chp     = champ.get(ch, 0) / n_sims * 100
    ch_flag = FLAGS.get(ch, "")

    final_col = (
        f'<div style="display:flex;flex-direction:column;align-items:center;'
        f'justify-content:center;gap:4px;padding:0 14px;flex-shrink:0;">'
        f'<div style="font-size:8.5px;font-weight:700;color:var(--muted);text-transform:uppercase;'
        f'letter-spacing:.07em;margin-bottom:4px">FINAL</div>'
        + slot_html(f1, fp1, f1 == ch)
        + slot_html(f2, fp2, f2 == ch)
        + f'<div style="margin-top:14px;text-align:center;padding:10px 12px;'
        f'background:rgba(251,191,36,.07);border:1px solid rgba(251,191,36,.25);border-radius:6px;">'
        f'<div style="font-size:8.5px;font-weight:700;color:var(--gold);text-transform:uppercase;'
        f'letter-spacing:.07em;margin-bottom:6px">Champion</div>'
        f'<div style="font-size:22px;line-height:1">{ch_flag}</div>'
        f'<div style="font-size:13px;font-weight:800;color:var(--gold);margin-top:4px">{ch}</div>'
        f'<div style="font-size:10px;color:var(--muted);margin-top:2px">{chp:.1f}% probability</div>'
        f'</div></div>'
    )

    bracket = (
        f'<div style="display:flex;align-items:stretch;gap:3px;min-width:max-content;padding:6px 0;">'
        + l_r32 + l_r16 + l_qf + l_sf
        + final_col
        + r_sf + r_qf + r_r16 + r_r32
        + f'</div>'
    )

    return (
        f'<div style="background:var(--surf);border:1px solid var(--border);border-radius:10px;overflow:hidden">'
        f'<div style="background:var(--surf2);padding:9px 14px;border-bottom:1px solid var(--border);'
        f'display:flex;justify-content:space-between;align-items:center">'
        f'<span style="font-weight:700;font-size:14px;color:var(--text)">Predicted Bracket</span>'
        f'<span style="font-size:11px;color:var(--muted)">{n_sims:,} simulations · '
        f'gold = predicted winner · % = P(win this match)</span>'
        f'</div>'
        f'<div style="overflow-x:auto;padding:12px 10px">{bracket}</div>'
        f'<div style="padding:6px 14px;font-size:11px;color:var(--muted);border-top:1px solid var(--border)">'
        f'Each match shows the two most likely opponents. '
        f'% = win probability normalized between those two teams. '
        f'Gold = predicted match winner who advances.'
        f'</div></div>'
    )


def build_tournament_table(bracket_data: dict, n_sims: int) -> str:
    """Full-tournament advancement probability table for all 48 teams."""
    r32_w  = bracket_data["r32_w"]
    r16_w  = bracket_data["r16_w"]
    qf_w   = bracket_data["qf_w"]
    sf_w   = bracket_data["sf_w"]
    final  = bracket_data["final"]
    champ  = bracket_data["champ"]

    # Aggregate R32 wins per team across all 16 matches
    r32_team: dict = {}
    for mn_data in r32_w.values():
        for team, cnt in mn_data.items():
            r32_team[team] = r32_team.get(team, 0) + cnt

    # Include all WC teams, sort by champion probability
    sorted_teams = sorted(
        WC_TEAMS,
        key=lambda t: (-champ.get(t, 0), -final.get(t, 0),
                       -sf_w.get(t, 0), -qf_w.get(t, 0), t)
    )

    def pct_td(raw_count: int, col_baseline: float) -> str:
        p = raw_count / n_sims * 100
        if p < 0.15:
            return '<td style="color:var(--muted);font-size:11px;text-align:center">—</td>'
        if p >= col_baseline:          c = "#4ade80"
        elif p >= col_baseline * 0.5:  c = "#86efac"
        elif p >= col_baseline * 0.2:  c = "#fbbf24"
        else:                          c = "#f87171"
        return (f'<td style="color:{c};font-weight:700;font-size:11px;'
                f'text-align:center">{p:.1f}%</td>')

    rows = ""
    for t in sorted_teams:
        flag = FLAGS.get(t, "🏳")
        grp  = next((g["id"] for g in GROUPS_CONFIG if t in g["teams"]), "?")
        rows += (
            f'<tr><td style="text-align:left;padding:5px 8px;white-space:nowrap;font-size:11.5px">'
            f'{flag} <b>{t}</b>'
            f'<span style="color:var(--muted);font-size:9px;margin-left:4px">Grp {grp}</span></td>'
            + pct_td(r32_team.get(t, 0), 50)
            + pct_td(r16_w.get(t, 0), 30)
            + pct_td(qf_w.get(t, 0), 18)
            + pct_td(sf_w.get(t, 0), 10)
            + pct_td(final.get(t, 0), 5)
            + pct_td(champ.get(t, 0), 2.5)
            + '</tr>'
        )

    th = ('<th style="padding:6px 8px;color:var(--muted);font-size:9px;text-transform:uppercase;'
          'letter-spacing:.06em;border-bottom:1px solid var(--border);text-align:center">')

    return f"""
<div style="background:var(--surf);border:1px solid var(--border);border-radius:10px;overflow:hidden">
  <div style="background:var(--surf2);padding:9px 14px;border-bottom:1px solid var(--border);
              display:flex;justify-content:space-between;align-items:center">
    <span style="font-weight:700;font-size:14px;color:var(--text)">Tournament Advancement Odds</span>
    <span style="font-size:11px;color:var(--muted)">{n_sims:,} simulations</span>
  </div>
  <div style="overflow-y:auto;max-height:560px">
    <table style="width:100%;border-collapse:collapse">
      <thead style="position:sticky;top:0;z-index:1">
        <tr style="background:var(--surf2)">
          <th style="text-align:left;padding:6px 8px;color:var(--muted);font-size:9px;
                     text-transform:uppercase;letter-spacing:.06em;
                     border-bottom:1px solid var(--border)">Team</th>
          {th}R32 Win</th>
          {th}R16</th>
          {th}QF</th>
          {th}SF</th>
          {th}Final</th>
          {th}Champion</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
  </div>
  <div style="padding:7px 14px;font-size:11px;color:var(--muted);border-top:1px solid var(--border)">
    Sorted by P(Champion). All 48 teams shown. Bracket paths from group-stage simulation.
  </div>
</div>"""


# ─────────────────────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────────────────────
CSV_PATH    = os.path.join(os.path.dirname(__file__), "all_international_soccer_results.csv")
CSV_FTABLE  = os.path.join(os.path.dirname(__file__), "third_place_combinations.csv")
team_stats  = load_team_stats(CSV_PATH, cutoff_year=2018)
ftable      = load_ftable(CSV_FTABLE)
data_loaded = bool(team_stats)

# ─────────────────────────────────────────────────────────────────────────────
# AUTO-REFRESH  (during group stage only)
# ─────────────────────────────────────────────────────────────────────────────
if WC_REF_DATE <= date.today() <= WC2026_GROUP_END:
    try:
        from streamlit_autorefresh import st_autorefresh
        # 60 s when a match is live, 5 min otherwise
        _refresh_ms = 60_000 if st.session_state.get("any_live") else 5 * 60 * 1000
        st_autorefresh(interval=_refresh_ms, key="wc_live_refresh")
    except ImportError:
        pass   # streamlit-autorefresh not installed — silent fallback

# ─────────────────────────────────────────────────────────────────────────────
# PAGE HEADER
# ─────────────────────────────────────────────────────────────────────────────
_live_badge = ""
if st.session_state.get("live_status"):
    _color = "#4ade80" if "🟢" in st.session_state.live_status else "#fbbf24"
    _live_badge = (f'<span style="background:rgba(34,197,94,.12);color:{_color};'
                   f'border:1px solid rgba(34,197,94,.3);padding:3px 10px;'
                   f'border-radius:20px;font-size:11px;font-weight:700">'
                   f'{st.session_state.live_status}</span>')

st.html(f"""
<div style="padding:4px 0 18px 0">
  <div style="display:flex;align-items:baseline;gap:12px;flex-wrap:wrap">
    <h1 style="color:#fbbf24;font-size:26px;font-weight:900;margin:0;letter-spacing:-.5px">
      &#x26BD; WC 2026 &mdash; Best Third Place Teams
    </h1>
    <span style="background:rgba(99,102,241,.2);color:#a5b4fc;
                 border:1px solid rgba(99,102,241,.35);padding:3px 10px;
                 border-radius:20px;font-size:12px;font-weight:700">
      8 of 12 advance
    </span>
    {_live_badge}
  </div>
  <p style="color:#6b7494;font-size:13px;margin:3px 0 0 0">
    Neg-binomial Monte Carlo &middot; Bayesian-shrunk ratings &middot; data from 2018&ndash;2026
  </p>
</div>
""")

# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
_sim_n_display = (
    f"{st.session_state.sim_results[3]:,} simulations"
    if "sim_results" in st.session_state else "no simulation run yet"
)
tab_bt, tab_groups, tab_r32, tab_hist = st.tabs([
    f"🏆 Best Third Place Teams · {_sim_n_display}",
    f"⚽ Groups & Results · {_sim_n_display}",
    f"🗓️ Predicted Bracket · {_sim_n_display}",
    "📊 Historical Reference",
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — BEST THIRDS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_bt:

    if data_loaded:
        cal_mean = team_stats.get("_global_mean", GLOBAL_MEAN)
        n_teams  = len(team_stats) - 1
        st.html(f"""
<div class="model-box">
  <strong style="color:var(--text)">Model</strong> &nbsp;·&nbsp;
  λ = shrunk_gf × shrunk_ga ÷ {cal_mean:.3f} &nbsp;·&nbsp;
  {n_teams:,} teams · data since 2018 &nbsp;·&nbsp;
  <span style="color:#a5b4fc">tournament-weighted</span>
  (WC 5× · continental 2.3–3.5× · qualifiers 2.2–3.0× · friendlies 1×) &nbsp;·&nbsp;
  <span style="color:#a5b4fc">time-decayed</span>
  (4 yrs ago ≈ 50% weight) &nbsp;·&nbsp;
  <span style="color:#86efac">Bayes-shrunk</span>
  (k={SHRINK_K:.0f}) &nbsp;·&nbsp;
  <span style="color:#86efac">neg-binomial</span>
  sampling (r={NB_DISPERSION:.0f})
</div>""")
    else:
        st.html("""<div class="model-box" style="border-left:4px solid var(--bubble)">
  ⚠ results.csv not found — using flat λ=1.35 for all matches
</div>""")

    ctrl1, ctrl2, ctrl3 = st.columns([2, 2, 1.2])
    with ctrl1:
        st.markdown('<div class="ctrl-label">Simulations</div>', unsafe_allow_html=True)
        n_sims = st.slider("n", 1_000, 50_000, 10_000, 1_000,
                           label_visibility="collapsed", format="%d")
    with ctrl2:
        st.markdown('<div class="ctrl-label">Data cutoff year</div>', unsafe_allow_html=True)
        recency = st.slider("cutoff", 2018, 2024, 2018, 1,
                            label_visibility="collapsed")
    with ctrl3:
        st.write("")
        run_btn = st.button("▶ Run Simulation", type="primary", use_container_width=True)

    if recency != 2018:
        team_stats = load_team_stats(CSV_PATH, cutoff_year=recency)

    if run_btn or "sim_results" not in st.session_state:
        with st.spinner(f"Running {n_sims:,} simulations…"):
            st.session_state.sim_results = run_monte_carlo(n_sims, team_stats, ftable)

    group_data, pts_gd, pts_thresh, n_used, _bd = st.session_state.sim_results

    top_p    = max(g["p_advance"]  for g in group_data)
    top_ag   = max(g["adv_given"] for g in group_data)
    bubble_n = sum(1 for g in group_data if 25 <= g["p_advance"] < 50)
    safe_n   = sum(1 for g in group_data if g["p_advance"] >= 75)

    h1, h2, h3, h4 = st.columns(4)
    with h1: st.html(f'<div class="hero-stat"><div class="val">{top_p:.0f}%</div><div class="lbl">Best P(advance)</div></div>')
    with h2: st.html(f'<div class="hero-stat"><div class="val">{top_ag:.0f}%</div><div class="lbl">Best P(adv | 3rd)</div></div>')
    with h3: st.html(f'<div class="hero-stat"><div class="val">{safe_n}</div><div class="lbl">Groups — Safe Slot</div></div>')
    with h4: st.html(f'<div class="hero-stat"><div class="val">{bubble_n}</div><div class="lbl">Groups — On Bubble</div></div>')

    st.write("")
    st.html(build_best_thirds_table(group_data, n_used))
    st.write("")
    st.html(build_pts_gd_matrix(pts_gd, pts_thresh, n_used))

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — GROUPS & RESULTS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_groups:

    sim_by_group = {}
    sim_n = 0
    if "sim_results" in st.session_state:
        gd_list, _, _, sim_n, _ = st.session_state.sim_results
        sim_by_group = {g["gid"]: g["all_teams"] for g in gd_list}

    st.html("""
<p style="color:#6b7494;font-size:12px;margin-bottom:12px">
  Highlighted (amber) row = current 3rd place.
  Simulated finish % updates after each simulation run.
</p>""")

    group_ids   = [g["id"] for g in GROUPS_CONFIG]
    _inprogress = st.session_state.get("live_inprogress", {})
    for row_start in range(0, 12, 4):
        cols = st.columns(4)
        for ci, gid in enumerate(group_ids[row_start:row_start+4]):
            with cols[ci]:
                st.html(build_group_card(gid, team_stats,
                                         all_teams_sim=sim_by_group.get(gid),
                                         n_sims=sim_n,
                                         live_matches=_inprogress.get(gid, [])))

    st.divider()
    st.html('<div style="font-size:11px;font-weight:700;color:var(--muted);'
            'text-transform:uppercase;letter-spacing:.07em;margin-bottom:10px">'
            '&#x2795; Add Match Result</div>')

    sel_group  = st.selectbox("Group", group_ids, key="form_group")
    remaining  = get_remaining(sel_group)
    g_cfg      = get_group(sel_group)
    match_opts = [f"{g_cfg['teams'][a]}  vs  {g_cfg['teams'][b]}" for a,b in remaining]

    if not match_opts:
        st.html("""
<div style="background:var(--surf);border:1px solid var(--border);
            border-left:4px solid var(--bubble);border-radius:6px;
            padding:12px 16px;margin:10px 0;font-size:13px;color:var(--muted)">
  All 6 matches have been entered for this group.
  Choose a different group above, or reset all results below.
</div>""")
        if st.button("↺ Reset to Defaults", key="reset_full_btn"):
            st.session_state.manual_mode = False
            st.session_state.results = copy.deepcopy(EMPTY_RESULTS)
            if "sim_results" in st.session_state:
                del st.session_state["sim_results"]
            st.rerun()
    else:
        sel_match  = st.selectbox("Match", match_opts, key="form_match")
        sel_idx    = match_opts.index(st.session_state.get("form_match", match_opts[0]))
        ma, mb     = remaining[sel_idx]
        team1_name = g_cfg["teams"][ma]
        team2_name = g_cfg["teams"][mb]

        with st.form("add_result_form", clear_on_submit=True):
            fc3, fc4 = st.columns([1, 1])
            with fc3: s1 = st.number_input(team1_name, 0, 20, 0)
            with fc4: s2 = st.number_input(team2_name, 0, 20, 0)

            c_save, c_reset = st.columns([1, 1])
            with c_save:
                submitted = st.form_submit_button("💾 Save Result", type="primary",
                                                  use_container_width=True)
            with c_reset:
                reset = st.form_submit_button("↺ Reset to Defaults",
                                              use_container_width=True)

            if submitted:
                st.session_state.manual_mode = True
                st.session_state.results[sel_group].append(
                    {"t1":ma,"t2":mb,"s1":int(s1),"s2":int(s2)}
                )
                if "sim_results" in st.session_state:
                    del st.session_state["sim_results"]
                st.rerun()

            if reset:
                st.session_state.manual_mode = False   # re-enable live on reset
                st.session_state.results = copy.deepcopy(EMPTY_RESULTS)
                if "sim_results" in st.session_state:
                    del st.session_state["sim_results"]
                st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — R32 BRACKET
# ═══════════════════════════════════════════════════════════════════════════════
with tab_r32:
    if "sim_results" not in st.session_state:
        st.html('<div class="model-box">Run a simulation in the 🏆 tab first to see bracket odds.</div>')
    else:
        _, _, _, _r32_n, _bracket = st.session_state.sim_results

        ftable_ok = bool(ftable)
        if not ftable_ok:
            st.html("""<div class="model-box" style="border-left:4px solid var(--bubble)">
  ⚠ third_place_combinations.csv not found — 3rd-place bracket slots may be approximate.
</div>""")

        st.html(f"""
<div style="padding:4px 0 12px 0">
  <p style="color:#6b7494;font-size:13px;margin:0">
    Each R32 match card shows the top teams likely to appear in each bracket slot
    (with their slot probability) and their overall P(win that match) across all {_r32_n:,} simulations.
    Bracket paths resolve via the official FIFA third-place combination table.
  </p>
</div>""")

        st.html(build_bracket_view(_bracket, _r32_n))
        st.write("")
        st.html(build_tournament_table(_bracket, _r32_n))


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — HISTORICAL REFERENCE
# ═══════════════════════════════════════════════════════════════════════════════
with tab_hist:
    st.html("""
<div class="info-box">
  <strong style="color:#fbbf24">Is the 4/6 era comparable to today's 8/12 era?</strong><br>
  Yes — structurally identical. Both advance <strong>66.7%</strong> of third-place teams
  (4÷6 = 8÷12). Teams still play 3 matches in a 4-team group.
  The larger pool (12 vs 6 groups) makes the cutoff <em>more predictable</em>
  and likely pushes it slightly higher.<br><br>
  <strong style="color:#fbbf24">Points conversion (1986 &amp; 1990):</strong>
  2-1-0 → 3-1-0:
  <code style="background:#22263a;padding:1px 6px;border-radius:3px;color:#a5b4fc">
    converted = original + wins</code>.
  Each win gains +1. Rankings below use original system, so converted pts
  can appear paradoxical.
</div>""")

    for yr in HISTORY:
        st.html(build_hist_table(yr))

    st.html("""
<div class="thresh-box">
  <strong style="color:#fbbf24">Historical thresholds (3-1-0 equivalent):</strong><br>
  <span style="color:#4ade80">■</span> <strong>6 pts</strong> — Guaranteed. Zero risk.<br>
  <span style="color:#4ade80">■</span> <strong>4 pts</strong> — Advanced every time across all eras (8/8). Very safe.<br>
  <span style="color:#fbbf24">■</span> <strong>3 pts</strong> — Mixed: Netherlands '90 (3 draws) advanced;
  Hungary '86 and Austria/Scotland '90 (all 1W+2L) did not.
  Draws safer than wins here — same converted pts, better GD on average.<br>
  <span style="color:#f87171">■</span> <strong>2 pts</strong> — Only in 1986's weaker field. Never again.<br>
  <span style="color:#f87171">■</span> <strong>1 pt or fewer</strong> — Never advanced.<br><br>
  <strong style="color:#fbbf24">2026 projection:</strong> With 12 groups, expect the cutoff
  at <strong>4–5 pts</strong>. The pts×GD matrix in the Best Third Place Teams tab quantifies this exactly.
</div>""")
