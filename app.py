import streamlit as st
import os
import re
import time
import threading
import hashlib
import tempfile
import shutil
import streamlit.components.v1 as components 
from datetime import datetime, timedelta
from collections import defaultdict
from streamlit.runtime import get_instance

# ==========================================
# [시스템] 브라우저 자동 종료 감시
# ==========================================
def monitor_browser_close():
    time.sleep(5)
    while True:
        try:
            runtime = get_instance()
            if runtime:
                session_infos = runtime._session_mgr.list_active_sessions()
                if len(session_infos) == 0:
                    time.sleep(2)
                    if len(runtime._session_mgr.list_active_sessions()) == 0:
                        os._exit(0) 
        except Exception:
            pass 
        time.sleep(1)

if "monitor_started" not in st.session_state:
    st.session_state.monitor_started = True
    threading.Thread(target=monitor_browser_close, daemon=True).start()

# ==========================================
# 0. 페이지 설정 및 CSS
# ==========================================
st.set_page_config(page_title="NEURAL CORE", page_icon="💠", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    /* 폰트 로드 */
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700;800&display=swap');
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

    /* GLOBAL THEME */
    .stApp, section[data-testid="stSidebar"], .stMarkdown, .stMarkdown p, .stText, h1, h2, h3 {
        background-color: #0E1117;
        color: #ECEFF1 !important;
        font-family: 'Pretendard', sans-serif; 
    }

    /* SIDEBAR STYLE */
    section[data-testid="stSidebar"] {
        background-color: #050608;
        border-right: 1px solid #1E2329;
        width: 300px;
    }
    .sidebar-header {
        font-family: 'JetBrains Mono', monospace !important;
        color: #00E5FF !important;
        font-size: 14px;
        font-weight: 800;
        border-bottom: 2px solid #00E5FF;
        padding-bottom: 12px;
        margin-bottom: 25px;
        letter-spacing: 2px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        text-shadow: 0 0 10px rgba(0, 229, 255, 0.4);
    }
    div.control-label {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 10px !important;
        font-weight: 700 !important;
        color: #546E7A !important;
        margin-top: 20px;
        margin-bottom: 8px;
        letter-spacing: 1px;
        display: flex;
        align-items: center;
        text-transform: uppercase;
    }
    .label-accent { color: #00E5FF; margin-right: 6px; }
    
    /* Input Widgets */
    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: #0E1117 !important;
        color: #ECEFF1 !important;
        border: 1px solid #263238 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 11px !important;
        border-radius: 0px !important;
        min-height: 32px !important;
        transition: border 0.3s, box-shadow 0.3s;
    }
    section[data-testid="stSidebar"] input:focus,
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div:focus-within {
        border-color: #00E5FF !important;
        box-shadow: 0 0 8px rgba(0, 229, 255, 0.2) !important;
    }
    
    /* Radio Buttons */
    section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] {
        display: flex;
        gap: 0px;
        background: transparent;
        border: 1px solid #263238;
    }
    section[data-testid="stSidebar"] .stRadio label {
        background: #0E1117;
        border: none;
        padding: 6px 0;
        margin: 0;
        border-radius: 0px;
        flex: 1;
        display: flex;
        justify-content: center;
        align-items: center;
        border-right: 1px solid #263238;
        transition: all 0.2s;
    }
    section[data-testid="stSidebar"] .stRadio label:last-child { border-right: none; }
    section[data-testid="stSidebar"] .stRadio label p {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 10px !important;
        color: #607D8B !important;
        font-weight: 700;
    }
    section[data-testid="stSidebar"] .stRadio div[aria-checked="true"] {
        background-color: rgba(0, 229, 255, 0.1) !important;
    }
    section[data-testid="stSidebar"] .stRadio div[aria-checked="true"] p {
        color: #00E5FF !important;
        text-shadow: 0 0 5px rgba(0, 229, 255, 0.5);
    }
    
    /* Button */
    section[data-testid="stSidebar"] .stButton { margin-top: 30px; }
    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        height: 45px;
        background: transparent;
        color: #00E5FF;
        border: 1px solid #00E5FF;
        border-radius: 0px;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 800;
        font-size: 12px;
        letter-spacing: 2px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        box-shadow: 0 0 5px rgba(0, 229, 255, 0.2);
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: #00E5FF;
        color: #000 !important;
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.6);
        border-color: #00E5FF;
        transform: translateY(-1px);
    }
    section[data-testid="stSidebar"] .stButton > button:active {
        transform: translateY(1px);
        box-shadow: 0 0 5px rgba(0, 229, 255, 0.4);
    }
    .separator-line { height: 1px; background: linear-gradient(90deg, #1E2329, transparent); margin: 25px 0; }

    /* DASHBOARD STYLES */
    .stMainBlockContainer {
        max-width: 1400px !important;
        margin-left: auto !important;
        margin-right: auto !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    .st-emotion-cache-zh2fnc { width: 100% !important; }

    .dashboard-container {
        background: #0D1117;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 30px;
        border: 1px solid #30363D;
        display: flex;
        gap: 20px;
        justify-content: space-between;
    }
    .stat-panel {
        flex: 1;
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid #30363D;
        border-radius: 12px;
        padding: 15px 20px;
        display: flex;
        align-items: center; 
        justify-content: flex-start;
        gap: 20px;
        transition: border-color 0.3s;
    }
    .stat-panel:hover { border-color: #58A6FF; }
    .stat-main {
        text-align: center;
        min-width: 70px;
        border-right: 1px solid rgba(255,255,255,0.1);
        padding-right: 15px;
        margin-right: 5px;
    }
    .stat-label { color: #8B949E; font-size: 0.8em; font-weight: 700; letter-spacing: 1px; margin-bottom: 2px; }
    .stat-value { font-size: 1.8em; font-weight: 800; color: #fff; line-height: 1; }
    .stat-details {
        flex: 1;
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        align-content: center;
    }
    .detail-badge {
        display: inline-flex;
        align-items: center;
        text-decoration: none !important;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 0.7em;
        font-weight: 600;
        transition: all 0.2s;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        color: #C9D1D9;
    }
    .detail-badge:hover { transform: translateY(-2px); filter: brightness(1.2); }
    .count-tag { border-radius: 10px; padding: 0 6px; margin-left: 6px; font-size: 0.9em; font-weight: bold; }

    /* Theme Colors */
    .theme-blue .stat-label { color: #58A6FF; }
    .theme-blue .stat-value { text-shadow: 0 0 15px rgba(88, 166, 255, 0.3); }
    .theme-blue .detail-badge { border-color: rgba(88, 166, 255, 0.3); color: #a5d6ff; }
    .theme-blue .count-tag { background: #58A6FF; color: #000; }

    .theme-green .stat-label { color: #3FB950; }
    .theme-green .stat-value { text-shadow: 0 0 15px rgba(63, 185, 80, 0.3); }
    .theme-green .detail-badge { border-color: rgba(63, 185, 80, 0.3); color: #b3f2c4; }
    .theme-green .count-tag { background: #3FB950; color: #000; }

    .theme-orange .stat-label { color: #D29922; }
    .theme-orange .stat-value { text-shadow: 0 0 15px rgba(210, 153, 34, 0.3); }
    .theme-orange .detail-badge { border-color: rgba(210, 153, 34, 0.3); color: #FFECB3; }
    .theme-orange .count-tag { background: #D29922; color: #000; }

    .theme-red .stat-label { color: #F85149; }
    .theme-red .stat-value { text-shadow: 0 0 15px rgba(248, 81, 73, 0.3); }
    .theme-red .detail-badge { border-color: rgba(248, 81, 73, 0.3); color: #ffdcd7; }
    .theme-red .count-tag { background: #F85149; color: #000; }

    /* Transaction Card */
    .trans-card {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-left: 4px solid #58A6FF;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        scroll-margin-top: 20px;
    }
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: linear-gradient(90deg, rgba(33, 60, 100, 0.6) 0%, rgba(22, 33, 62, 0.3) 100%);
        border: 1px solid rgba(88, 166, 255, 0.3);
        border-radius: 10px;
        padding: 12px 18px;
        margin-bottom: 15px;
        box-shadow: inset 0 0 15px rgba(0, 0, 0, 0.2);
    }
    .status-badge { padding: 4px 10px; border-radius: 6px; font-size: 0.75em; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; }
    .bg-success { background: rgba(35, 134, 54, 0.2); color: #3FB950; border: 1px solid rgba(35, 134, 54, 0.4); }
    .bg-error { background: rgba(218, 54, 51, 0.2); color: #F85149; border: 1px solid rgba(218, 54, 51, 0.4); }
    .bg-warn { background: rgba(210, 153, 34, 0.2); color: #D29922; border: 1px solid rgba(210, 153, 34, 0.4); }

    .step-row { border-left: 2px solid #30363D; padding-left: 20px; margin-bottom: 6px; }
    .border-pass { border-left-color: #3FB950; }
    .border-fail { border-left-color: #F85149; }
    .step-name { font-weight: bold; color: #E6EDF3; margin-right: 10px; }
    
    .highlight-time { color: #58A6FF; font-weight: bold; font-family: monospace; }
    .highlight-cate { color: #C9D1D9; font-weight: bold; }
    .highlight-money { color: #D29922; font-weight: bold; font-family: monospace; }
    .headline-rate { color: #4FC3F7; margin-left: 10px; font-size: 0.9em; font-weight: bold; }
    .highlight-out { color: #FF7B72; font-weight: bold; font-family: monospace; margin-left: 5px; } 

    .tag { padding: 2px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; margin-left: 5px; font-family: 'Consolas', monospace; }
    .tag-money { background: rgba(210, 153, 34, 0.2); color: #D29922; border: 1px solid rgba(210, 153, 34, 0.4); }
    .tag-card { background: rgba(88, 166, 255, 0.2); color: #58A6FF; border: 1px solid rgba(88, 166, 255, 0.4); }
    
    .critical-box {
        background: rgba(248, 81, 73, 0.1);
        border-left: 4px solid #F85149;
        color: #FF7B72;
        padding: 10px;
        margin: 8px 0;
        font-family: monospace;
        font-weight: bold;
    }
    
    .stMainBlockContainer { 
        margin : auto;
    }
    
    details.card-data-toggle { background-color: #252526; border: 1px solid #444; border-radius: 6px; margin: 5px 0; overflow: hidden; }
    details.card-data-toggle summary { padding: 8px 12px; cursor: pointer; font-size: 13px; font-weight: bold; color: #90CAF9; background-color: #2D2D2D; list-style: none; display: flex; align-items: center; }
    details.card-data-toggle summary:hover { background-color: #383838; }
    details.card-data-toggle summary::before { content: "▶"; font-size: 10px; margin-right: 8px; transition: transform 0.2s; color: #90CAF9; }
    details.card-data-toggle[open] summary::before { transform: rotate(90deg); }
    .toggle-content { padding: 10px; background-color: #1a1a1a; border-top: 1px solid #444; font-family: 'Consolas', monospace; font-size: 12px; color: #ccc; line-height: 1.4; white-space: pre-wrap; }
    .data-line { margin-bottom: 2px; border-bottom: 1px dashed #333; padding-bottom: 2px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. 플로우 정의 (상수)
# ==========================================
RE_DATE = re.compile(r"(\d{4}-\d{2}-\d{2})")
RE_TIME = re.compile(r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})")
RE_MONEY = re.compile(r"\{(\d+)\}\s*/\s*([A-Z]+)\s*/\s*(\d+)")
RE_PASSPORT = re.compile(r"passport\s*:\s*\{(.*?)\}", re.IGNORECASE)
RE_PAYMENT_REQ = re.compile(r"결제요청하기\s*->\s*(\d+)")

FLOW_CARD_CASH = ["[SERVER CONTENTS]CARD_INDEX2", "[SERVER CONTENTS]CARD_MAIN", "[SERVER CONTENTS]C_SEL_CURRENCY", "[SERVER CONTENTS]C_SCAN_PASS", "[SERVER CONTENTS]C_I_AGREE", "[SERVER CONTENTS]C_I_INPUT", "[SERVER CONTENTS]C_I_SELCASH", "[SERVER CONTENTS]C_I_SELAMT", "[SERVER CONTENTS]C_I_OUTKRW", "[SERVER CONTENTS]C_I_ACTIVATE", "[SERVER CONTENTS]C_RECEIPT", "[SERVER CONTENTS]C_I_COMPLETE"]
FLOW_CARD_CREDIT = ["[SERVER CONTENTS]CARD_INDEX2", "[SERVER CONTENTS]CARD_MAIN", "[SERVER CONTENTS]C_I_SELVOUCHER", "[SERVER CONTENTS]C_SEL_PAYMENT", "[SERVER CONTENTS]C_SCAN_PASS", "[SERVER CONTENTS]C_I_AGREE", "[SERVER CONTENTS]C_I_CREDIT", "[SERVER CONTENTS]C_I_PAYMENT", "[SERVER CONTENTS]C_I_ACTIVATE", "[SERVER CONTENTS]C_RECEIPT", "[SERVER CONTENTS]C_I_COMPLETE"]
FLOW_CARD_REISSUE = ["[SERVER CONTENTS]CARD_INDEX2", "[SERVER CONTENTS]CARD_MAIN", "[SERVER CONTENTS]C_R_AGREE", "[SERVER CONTENTS]C_SCAN_PASS", "[SERVER CONTENTS]C_VERIFY_PIN", "[SERVER CONTENTS]C_R_ACTIVATE", "[SERVER CONTENTS]C_RECEIPT", "[SERVER CONTENTS]C_R_COMPLETE"]
FLOW_CHARGE_CASH = ["[SERVER CONTENTS]CARD_INDEX2", "[SERVER CONTENTS]CARD_MAIN", "[SERVER CONTENTS]C_T_TARGET", "[SERVER CONTENTS]C_SEL_PAYMENT", "[SERVER CONTENTS]C_INSERT_CARD", "[SERVER CONTENTS]C_SCAN_PASS", "[SERVER CONTENTS]C_SEL_CURRENCY", "[SERVER CONTENTS]C_T_INPUT", "[SERVER CONTENTS]C_T_TRANSACTION", "[SERVER CONTENTS]C_T_RECEIPT", "[SERVER CONTENTS]C_T_COMPLETE"]
FLOW_CHARGE_CREDIT = ["[SERVER CONTENTS]CARD_INDEX2", "[SERVER CONTENTS]CARD_MAIN", "[SERVER CONTENTS]C_T_TARGET", "[SERVER CONTENTS]C_SEL_PAYMENT", "[SERVER CONTENTS]C_INSERT_CARD", "[SERVER CONTENTS]C_T_SEL_AMT", "[SERVER CONTENTS]C_T_PAYMENT", "[SERVER CONTENTS]C_T_RECEIPT", "[SERVER CONTENTS]C_T_COMPLETE"]
FLOW_EXCHANGE_KRW = ["[SERVER CONTENTS]CARD_INDEX2", "[SERVER CONTENTS]MAIN", "[SERVER CONTENTS]SCAN_BY_PASSPORT", "[SERVER CONTENTS]INPUT_CURRENCY", "[SERVER CONTENTS]RECEIPT_OUTPUT", "[SERVER CONTENTS]OUTPUT_KRW", "[SERVER CONTENTS]OUTPUT_THERMAL"]
FLOW_EXCHANGE_FOREIGN = ["[SERVER CONTENTS]CARD_INDEX2", "[SERVER CONTENTS]MAIN2", "[SERVER CONTENTS]CALCULATOR_CURRENCY", "[SERVER CONTENTS]SCAN_PASSPORT", "[SERVER CONTENTS]SELECT_SALE_GB", "[SERVER CONTENTS]INPUT_KRW", "[SERVER CONTENTS]OUTPUT_CURRENCY", "[SERVER CONTENTS]OUTPUT_THERMAL_CURRENCY"]
FLOW_CARD_WITHDRAWAL = ["[SERVER CONTENTS]CARD_INDEX2", "[SERVER CONTENTS]CARD_MAIN", "[SERVER CONTENTS]C_INSERT_CARD", "[SERVER CONTENTS]C_VERIFY_PIN", "[SERVER CONTENTS]C_W_SELECT_AMT", "[SERVER CONTENTS]C_W_OUTKRW", "[SERVER CONTENTS]C_W_COMPLETE"]
FLOW_EXCHANGE_FOREIGN_CREDIT = ["[SERVER CONTENTS]CARD_INDEX2", "[SERVER CONTENTS]CALCULATOR_CURRENCY", "[SERVER CONTENTS]SCAN_PASSPORT", "[SERVER CONTENTS]SELECT_SALE_GB", "[SERVER CONTENTS]SALE_ACC_PHONE", "[SERVER CONTENTS]SALE_ACC_CHECK", "[SERVER CONTENTS]SALE_ACC_OUTPUT_CURRENCY", "[SERVER CONTENTS]OUTPUT_THERMAL_CURRENCY"]

TRANSACTION_MAP = {
    "카드 발급 (현금)": (FLOW_CARD_CASH, "CASH", "C_I_INPUT"),
    "카드 발급 (신용카드)": (FLOW_CARD_CREDIT, "CREDIT", "C_I_CREDIT"),
    "카드 재발급": (FLOW_CARD_REISSUE, "REISSUE", "C_R_ACTIVATE"),
    "카드 충전 (현금)": (FLOW_CHARGE_CASH, "CASH", "C_T_INPUT"),
    "카드 충전 (신용카드)": (FLOW_CHARGE_CREDIT, "CREDIT", "C_T_SEL_AMT"),
    "원화 환전": (FLOW_EXCHANGE_KRW, "EXCHANGE", "INPUT_CURRENCY"),
    "외화 환전 (현금)": (FLOW_EXCHANGE_FOREIGN, "EXCHANGE_FOREIGN", "INPUT_KRW"),
    "외화 환전 (계좌 이체)": (FLOW_EXCHANGE_FOREIGN_CREDIT, "CREDIT", "SALE_ACC_CHECK"),
    "카드 출금": (FLOW_CARD_WITHDRAWAL, "WITHDRAWAL", "C_W_SELECT_AMT"),
}

# ==========================================
# 2. 유틸리티 및 분석 로직
# ==========================================
def read_log_file(path):
    try:
        with open(path, 'r', encoding='cp949') as f: return f.readlines()
    except:
        try:
            with open(path, 'r', encoding='utf-8') as f: return f.readlines()
        except: return []

def get_folder_stats(folder_path):
    if not os.path.exists(folder_path): return None
    file_count = 0; total_size = 0; last_mod_time = 0
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".txt") or file.endswith(".log"):
                file_count += 1
                fp = os.path.join(root, file)
                try:
                    stats = os.stat(fp)
                    total_size += stats.st_size
                    if stats.st_mtime > last_mod_time: last_mod_time = stats.st_mtime
                except: pass
    if total_size < 1024: size_str = f"{total_size} B"
    elif total_size < 1024**2: size_str = f"{total_size/1024:.1f} KB"
    else: size_str = f"{total_size/1024**2:.1f} MB"
    last_active = datetime.fromtimestamp(last_mod_time).strftime("%Y-%m-%d %H:%M") if last_mod_time > 0 else "N/A"
    return {"count": file_count, "size": size_str, "last_active": last_active}

def show_ai_loading_effect(keyword):
    status_text = st.empty()
    bar = st.progress(0)
    search_term = keyword if keyword.strip() else "GLOBAL_SCAN"
    steps = [
        "🔄 Initializing Neural Search Engine...",
        "📂 Loading Log Files into Memory...",
        f"🔍 Scanning Pattern: '{search_term}'",
        "🧠 Vectorizing Transaction Flows...",
        "⚠️ Cross-referencing Error Codes...",
        "📊 Calculating Success Metrics...",
        "✅ Analysis Complete."
    ]
    for i, step in enumerate(steps):
        status_text.markdown(f"<span style='font-family:monospace; color:#58A6FF; font-weight:bold;'>{step}</span>", unsafe_allow_html=True)
        bar.progress((i + 1) * (100 // len(steps)))
        time.sleep(0.15) 
    time.sleep(0.3)
    status_text.empty()
    bar.empty()

# [수정] 대시보드 UI - 4분할 (Total, Success, Canceled, Error)
def draw_summary_ui(total_cnt, success_cnt, canceled_cnt, fail_cnt, success_details, issue_details, stats_total, stats_success, stats_canceled, stats_fail):
    if total_cnt == 0: return
    
    success_rate = (success_cnt / total_cnt * 100) if total_cnt > 0 else 0
    ai_comment = ""
    ai_color = ""
    ai_border_color = ""
    
    if fail_cnt == 0 and canceled_cnt == 0:
        ai_comment = "모든 거래가 정상적으로 완료되었습니다. 시스템 상태가 **매우 안정적(Stable)**입니다."
        ai_color = "#3FB950" 
        ai_border_color = "#2ea043"
    elif success_rate < 50:
        ai_comment = f"⚠️ **주의 요망(Critical):** 거래 성공률이 {success_rate:.1f}%로 매우 낮습니다. 에러 및 중단 로그를 집중 점검하세요."
        ai_color = "#F85149" 
        ai_border_color = "#da3633"
    else:
        ai_comment = f"거래 분석 완료. **성공 {success_cnt}건**, **취소 {canceled_cnt}건**, **에러 {fail_cnt}건**이 감지되었습니다."
        ai_color = "#D29922" 
        ai_border_color = "#bb8800"

    st.markdown(f"""
    <div style='background: rgba(22, 27, 34, 0.8); border-left: 5px solid {ai_border_color}; padding: 20px; border-radius: 8px; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);'>
        <div style='color: {ai_color}; font-weight: 800; font-size: 0.9em; margin-bottom: 8px; letter-spacing: 1px;'>🤖 AI ANALYST BRIEFING</div>
        <div style='color: #E6EDF3; font-size: 1.15em; line-height: 1.5;'>"{ai_comment}"</div>
    </div>
    """, unsafe_allow_html=True)

    def create_badges_html(stats_dict, prefix_id=""):
        if not stats_dict: return "<span style='color:#555; font-size:0.8em;'>- 없음 -</span>"
        html = ""
        for cat, count in stats_dict.items():
            safe_id = re.sub(r'[^a-zA-Z0-9]', '', cat)
            html += f"<a href='#{prefix_id}{safe_id}' class='detail-badge' target='_self'>{cat} <span class='count-tag'>{count}</span></a> "
        return html

    html = f"""
    <div class='dashboard-container'>
        <div class='stat-panel theme-blue'>
            <div class='stat-main'><div class='stat-label'>TOTAL</div><div class='stat-value'>{total_cnt}</div></div>
            <div class='stat-details'>{create_badges_html(stats_total, "cat-total-")}</div>
        </div>
        <div class='stat-panel theme-green'>
            <div class='stat-main'><div class='stat-label'>SUCCESS</div><div class='stat-value'>{success_cnt}</div></div>
            <div class='stat-details'>{create_badges_html(stats_success, "cat-succ-")}</div>
        </div>
        <div class='stat-panel theme-orange'>
            <div class='stat-main'><div class='stat-label'>CANCELED</div><div class='stat-value'>{canceled_cnt}</div></div>
            <div class='stat-details'>{create_badges_html(stats_canceled, "cat-canc-")}</div>
        </div>
        <div class='stat-panel theme-red'>
            <div class='stat-main'><div class='stat-label'>ERROR</div><div class='stat-value'>{fail_cnt}</div></div>
            <div class='stat-details'>{create_badges_html(stats_fail, "cat-fail-")}</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def draw_landing_page(folder_path):
    st.markdown("""
<style>
    /* 전체 컨테이너 */
    .neural-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 40px 0;
        perspective: 1000px;
    }

    /* 타이틀 스타일 */
    .neural-title {
        font-size: 3em;
        font-weight: 800;
        letter-spacing: 4px;
        background: linear-gradient(to bottom, #fff, #58A6FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
        text-shadow: 0 0 20px rgba(88, 166, 255, 0.5);
    }
    
    /* 뉴럴 코어 애니메이션 */
    .core-container {
        position: relative;
        width: 220px;
        height: 200px;
        margin: 40px auto;
        display: flex;
        justify-content: center;
        align-items: center;
    }

    /* 중앙 빛나는 구체 - 커서 및 z-index 추가 */
    .ai-core {
        width: 100px;
        height: 100px;
        background: radial-gradient(circle at 30% 30%, #a5d6ff, #0D47A1);
        border-radius: 50%;
        box-shadow: 0 0 40px #007bff, inset 0 0 20px #fff;
        z-index: 100; /* 클릭 우선순위 높임 */
        animation: breathe 3s infinite ease-in-out;
        cursor: pointer; /* 클릭 가능 표시 */
        transition: transform 0.2s, box-shadow 0.2s;
    }
    /* 클릭 효과 */
    .ai-core:active {
        transform: scale(0.9);
        box-shadow: 0 0 10px #007bff;
    }

    /* 회전하는 바깥 링 1 */
    .ring-1 {
        position: absolute;
        width: 160px;
        height: 160px;
        border: 2px solid rgba(88, 166, 255, 0.3);
        border-top: 2px solid #58A6FF;
        border-radius: 50%;
        animation: spin 4s linear infinite;
        pointer-events: none;
    }

    /* 회전하는 바깥 링 2 (반대 방향) */
    .ring-2 {
        position: absolute;
        width: 190px;
        height: 190px;
        border: 1px dashed rgba(88, 166, 255, 0.4);
        border-radius: 50%;
        animation: spin-reverse 7s linear infinite;
        pointer-events: none;
    }

    /* 애니메이션 키프레임 */
    @keyframes breathe {
        0% { transform: scale(0.95); box-shadow: 0 0 25px #007bff; }
        50% { transform: scale(1.05); box-shadow: 0 0 50px #00aaff; }
        100% { transform: scale(0.95); box-shadow: 0 0 25px #007bff; }
    }
    @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    @keyframes spin-reverse { 0% { transform: rotate(360deg); } 100% { transform: rotate(0deg); } }

    /* HUD 카드 스타일 (PCT.py 디자인 적용) */
    .hud-card {
        background: rgba(13, 17, 23, 0.8);
        border: 1px solid rgba(88, 166, 255, 0.2);
        border-left: 3px solid #58A6FF;
        padding: 20px;
        position: relative;
        overflow: hidden;
        transition: all 0.3s;
    }
    .hud-card:hover {
        border-color: #58A6FF;
        box-shadow: 0 0 15px rgba(88, 166, 255, 0.1);
        transform: translateY(-5px);
    }
    
    /* 스캔라인 애니메이션 (누락되었던 부분 추가) */
    .hud-card::after {
        content: '';
        position: absolute;
        top: 0; left: 0; width: 100%; height: 2px;
        background: linear-gradient(90deg, transparent, rgba(88, 166, 255, 0.8), transparent);
        animation: scanline 3s infinite linear;
        opacity: 0.5;
    }
    @keyframes scanline { 0% { top: -10%; } 100% { top: 110%; } }

    .hud-label {
        font-size: 0.8em;
        color: #58A6FF;
        letter-spacing: 1px;
        margin-bottom: 5px;
        text-transform: uppercase;
    }
    .hud-value {
        font-size: 1.8em;
        color: #fff;
        font-weight: 700;
        font-family: 'Consolas', monospace;
        text-shadow: 0 0 5px rgba(255,255,255,0.3);
    }
    
    .system-msg {
        font-family: 'Consolas', monospace;
        color: #8B949E;
        font-size: 0.9em;
        margin-top: 10px;
        text-align: center;
    }
    .blink { animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }

</style>
""", unsafe_allow_html=True)

    stats = get_folder_stats(folder_path)
    
    if not stats:
        stats = {"count": 0, "size": "0 B", "last_active": "OFFLINE"}
        status_msg = "⚠️ TARGET NOT FOUND - SYSTEM OFFLINE"
    else:
        status_msg = f"SYSTEM ONLINE · WATCHING {os.path.basename(folder_path)}"

    # 메인 코어 UI
    st.markdown(f"""
<div class='neural-wrapper'>
<div class='neural-title'>NEURAL CORE</div>
<div style='color:#8B949E; letter-spacing:2px; font-size:0.9em; margin-bottom:10px;'>DIGITAL FORENSIC ENGINE v2.2</div>
<div class='core-container'>
<div class='ring-1'></div>
<div class='ring-2'></div>
<div class='ai-core' id='ai-core-btn'></div>
</div>
<div class='system-msg'>
<span class='blink'>_</span> {status_msg}
</div>
</div>
""", unsafe_allow_html=True)
    
    # [강력해진 JS] 전역 클릭 리스너 방식 (화면 갱신에도 클릭 유지)
    js_code = """
    <script>
    (function() {
        const doc = window.parent.document;
        
        // 기존에 등록된 리스너가 있다면 제거 (중복 방지)
        if (window.toggleSidebarFunc) {
            doc.removeEventListener('click', window.toggleSidebarFunc);
        }

        // 새 클릭 핸들러 정의
        window.toggleSidebarFunc = function(e) {
            // 클릭된 요소가 .ai-core 클래스를 가지고 있거나, 그 자식인지 확인
            if (e.target.classList.contains('ai-core') || e.target.closest('.ai-core')) {
                // 1. 닫혀있는 사이드바 열기 버튼 찾기 ( > 모양)
                let toggleBtn = doc.querySelector('[data-testid="stSidebarCollapsedControl"]');
                
                // 2. 만약 없다면, 열려있는 사이드바 닫기 버튼 찾기 ( < 모양)
                if (!toggleBtn) {
                    toggleBtn = doc.querySelector('[data-testid="stSidebarExpandedControl"]');
                }
                
                // 3. 버튼이 있으면 클릭
                if (toggleBtn) {
                    toggleBtn.click();
                }
            }
        };

        // 문서 전체에 클릭 리스너 부착 (Capture phase X, Bubble phase O)
        doc.addEventListener('click', window.toggleSidebarFunc);
    })();
    </script>
    """
    components.html(js_code, height=0, width=0)

    # 하단 HUD 통계
    if stats['count'] > 0:
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.markdown(f"""
<div class='hud-card'>
<div class='hud-label'>MEMORY NODES</div>
<div class='hud-value'>{stats['count']}</div>
<div style='font-size:0.7em; color:#8B949E; margin-top:5px;'>LOG FILES DETECTED</div>
</div>
""", unsafe_allow_html=True)
            
        with c2:
            st.markdown(f"""
<div class='hud-card'>
<div class='hud-label'>DATA DENSITY</div>
<div class='hud-value'>{stats['size']}</div>
<div style='font-size:0.7em; color:#8B949E; margin-top:5px;'>TOTAL STORAGE USAGE</div>
</div>
""", unsafe_allow_html=True)
            
        with c3:
            st.markdown(f"""
<div class='hud-card'>
<div class='hud-label'>LAST SYNC</div>
<div class='hud-value' style='font-size:1.4em; line-height:1.4;'>{stats['last_active']}</div>
<div style='font-size:0.7em; color:#8B949E; margin-top:5px;'>TIMESTAMP CONFIRMED</div>
</div>
""", unsafe_allow_html=True)
            
    else:
        st.error(f"❌ 폴더를 찾을 수 없습니다: {folder_path}")

# [수정] 분석 로직 (중복 제거 강화 및 환전 파싱)
def analyze_flow_web(folder_path, target_keyword, flow_list, mode, validator_step, start_date, end_date, category_name, anchor_map):
    html_parts = []
    found_any_target = False 
    
    success_details_list = []
    issue_details_list = []
    
    stat_total = 0; stat_success = 0; stat_canceled = 0; stat_fail = 0
    
    if not flow_list: return False, "", 0, 0, 0, 0, [], []

    start_step_marker = "".join(flow_list[0].split()).lower()
    last_step_marker = "".join(flow_list[-1].split()).lower()
    
    s_date_str = start_date.strftime("%Y-%m-%d")
    e_date_str = end_date.strftime("%Y-%m-%d")
    processed_keyword_lower = target_keyword

    # [추가] 글로벌 중복 방지 (해시 기반)
    global_processed_hashes = set()

    for foldername, subfolders, filenames in os.walk(folder_path):
        for filename in filenames:
            if not (filename.endswith(".txt") or filename.endswith(".log")): continue

            date_match = RE_DATE.search(filename)
            if date_match:
                file_date = date_match.group(1)
                if not (s_date_str <= file_date <= e_date_str): continue 

            full_path = os.path.join(foldername, filename)
            file_lines = read_log_file(full_path)
            if not file_lines: continue

            keyword_indices = [i for i, line in enumerate(file_lines) if processed_keyword_lower in "".join(line.split()).lower()]
            if not keyword_indices: continue 

           # [수정] 중복 방지를 위한 '시작 줄 번호' 저장소 (Set) - 단일 파일 내 중복 방지
            processed_start_indices = set()

            for keyword_line_index in keyword_indices:
                # 1. 거래 시작 지점(Line) 찾기
                start_idx = 0
                for i in range(keyword_line_index, -1, -1): 
                    if start_step_marker in "".join(file_lines[i].split()).lower(): 
                        start_idx = i
                        break
                
                # 2. 이미 처리된 시작 지점(같은 거래)라면 즉시 건너뜀 (단일 파일 내)
                if start_idx in processed_start_indices:
                    continue
                
                # 3. 거래 종료 지점 찾기
                end_idx = len(file_lines)
                for i in range(keyword_line_index + 1, len(file_lines)):
                    if start_step_marker in "".join(file_lines[i].split()).lower(): 
                        end_idx = i
                        break
                
                target_lines = file_lines[start_idx : end_idx]

                if not any(validator_step in line for line in target_lines): continue 

                # ==========================================================
                # [추가] 강력한 중복 방지 (내용 기반 서명 확인)
                # 추출된 거래 로그 블록 전체를 하나의 문자열로 합친 뒤 해시값 생성
                # 백업 파일 등으로 인해 파일명/경로가 달라도 내용이 같으면 걸러냄
                # ==========================================================
                content_signature = hashlib.md5("".join(target_lines).encode('utf-8')).hexdigest()
                
                if content_signature in global_processed_hashes:
                    continue # 이미 출력된 거래 내용과 동일하므로 스킵
                
                global_processed_hashes.add(content_signature)
                processed_start_indices.add(start_idx) # 파일 내 중복 방지 업데이트
                # ==========================================================
                
                found_any_target = True
                stat_total += 1 

                has_critical_error = False; pre_calc_cash = {} 
                collected_order_rates = []
                credit_payment_amt = 0 
                transfer_deposit_amt = 0 # [추가] 환전할 금액(입금) 저장용
                total_withdraw_krw = 0
                withdraw_foreign_info = []
                
                start_time_str = "Unknown"
                if target_lines:
                    time_match = RE_TIME.search(target_lines[0])
                    if time_match: start_time_str = time_match.group(1)

                last_withdraw_pattern = None

                for line in target_lines:
                    line_clean = "".join(line.split()).lower()
                    
                    # [판정 기준 1] 에러 감지 (반드시 [ERROR]와 [SERVER CONTENTS]가 동시에 있어야 함)
                    if "[error]" in line_clean and "[servercontents]" in line_clean: 
                        has_critical_error = True
                    
                    rate_match = re.search(r"(\[INFO\]\s*ORDER_RATE.*)", line, re.IGNORECASE)
                    if rate_match: collected_order_rates.append(rate_match.group(1))
                    
                    payment_match = RE_PAYMENT_REQ.search(line)
                    if payment_match: credit_payment_amt = int(payment_match.group(1))

                    # [추가] "환전할 금액" 파싱 -> "입금 금액" 변수
                    if category_name == "외화 환전 (계좌 이체)":
                        exchange_match = re.search(r"환전할 금액\s*:\s*(\d+)", line)
                        if exchange_match:
                            transfer_deposit_amt = int(exchange_match.group(1))                    
                    
                    if "SCN8237R" in line and "ACCEPT" in line:
                        match = RE_MONEY.search(line)
                        if match:
                            cnt = 1; cur = match.group(2); val = int(match.group(3))
                            if cur not in pre_calc_cash: pre_calc_cash[cur] = {'total_amt': 0, 'total_cnt': 0, 'breakdown': {}}
                            pre_calc_cash[cur]['total_amt'] += cnt * val
                            pre_calc_cash[cur]['total_cnt'] += cnt
                            if val not in pre_calc_cash[cur]['breakdown']: pre_calc_cash[cur]['breakdown'][val] = 0
                            pre_calc_cash[cur]['breakdown'][val] += cnt
                    
                    if "HSCDU2_1" in line or "HSCDU2_2" in line:
                        try:
                            match = re.search(r"((?:\d+/\d+\s*,\s*)+\d+/\d+)", line)
                            if match:
                                current_pattern = match.group(1)
                                if current_pattern != last_withdraw_pattern:
                                    last_withdraw_pattern = current_pattern 
                                    parts = [p.strip() for p in match.group(1).split(',')]
                                    disp_counts = [int(p.split('/')[1]) for p in parts]
                                    if len(disp_counts) == 3:
                                        total_withdraw_krw += (disp_counts[0]*50000 + disp_counts[1]*10000 + disp_counts[2]*1000)
                                    elif len(disp_counts) == 6:
                                        total_withdraw_krw += (disp_counts[0]*50000 + disp_counts[1]*10000 + disp_counts[3]*1000)
                                        if disp_counts[2] > 0: withdraw_foreign_info.append(f"TWD {disp_counts[2]}장")
                                        if disp_counts[4] > 0: withdraw_foreign_info.append(f"USD {disp_counts[4]}장")
                                        if disp_counts[5] > 0: withdraw_foreign_info.append(f"JPY {disp_counts[5]}장")
                        except: pass

                header_money_parts = []
                if pre_calc_cash:
                    for cur, info in pre_calc_cash.items():
                        breakdown_str_list = []
                        for val, cnt in info['breakdown'].items(): breakdown_str_list.append(f"{val:,}x{cnt}장")
                        breakdown_final = ", ".join(breakdown_str_list)
                        header_money_parts.append(f"입금: {cur} {info['total_amt']:,} ({breakdown_final})")
                
                if credit_payment_amt > 0:
                    header_money_parts.append(f"결제: {credit_payment_amt:,}원")
                
                # [추가] 헤더에 "입금 금액" 추가
                if transfer_deposit_amt > 0:
                    header_money_parts.append(f"입금 금액: {transfer_deposit_amt:,}원")
                
                if total_withdraw_krw > 0 or withdraw_foreign_info:
                    out_str = f"출금: {total_withdraw_krw:,} KRW"
                    if withdraw_foreign_info: out_str += f" + {', '.join(withdraw_foreign_info)}"
                    header_money_parts.append(f"<span class='highlight-out'>{out_str}</span>")

                money_summary_str = " / ".join(header_money_parts) if header_money_parts else "금액 미투입"
                if collected_order_rates:
                    clean_rates = [r.replace("[INFO]", "").strip() for r in collected_order_rates]
                    money_summary_str += f" <span class='headline-rate'>📉 {' / '.join(clean_rates)}</span>"

                # 단계 검사
                full_block = "".join([l.lower().replace(" ", "") for l in target_lines])
                last_successful_step = "시작 전"
                for step in flow_list:
                    step_clean = "".join(step.split()).lower()
                    if step_clean in full_block: last_successful_step = step.replace("[SERVER CONTENTS]", "").strip() 
                
                is_last_step_found = last_step_marker in full_block
                
                safe_cat_id = re.sub(r'[^a-zA-Z0-9]', '', category_name)
                anchor_id = ""
                if category_name not in anchor_map['total']:
                    anchor_id += f" id='cat-total-{safe_cat_id}'"
                    anchor_map['total'].add(category_name)

                # ==========================================
                # [판정 로직 구현]
                # ==========================================
                
                status_badge = ""
                narrative_text = ""
                
                if has_critical_error:
                    # 1. 에러
                    status_badge = "<span class='status-badge bg-error'>ERROR</span>"
                    stat_fail += 1
                    issue_details_list.append(f"[{category_name}] 에러 발생: {last_successful_step} 단계 이후")
                    narrative_text = f"<span class='narrative-text'><span class='highlight-time'>{start_time_str}</span>에 <span class='highlight-cate'>{category_name}</span> 진행 중, <span class='highlight-error'>시스템 에러</span>가 감지되었습니다.<br><span class='highlight-money'>({money_summary_str})</span></span>"
                    if category_name not in anchor_map['fail']:
                        if 'id=' not in anchor_id: anchor_id = f" id='cat-fail-{safe_cat_id}'"
                        anchor_map['fail'].add(category_name)

                elif not is_last_step_found:
                    # 2. 취소 (중단)
                    status_badge = "<span class='status-badge bg-warn'>CANCELED</span>"
                    stat_canceled += 1
                    issue_details_list.append(f"[{category_name}] 취소(중단): {last_successful_step} 단계까지 진행")
                    narrative_text = f"<span class='narrative-text'><span class='highlight-time'>{start_time_str}</span>에 <span class='highlight-cate'>{category_name}</span> 거래가 <span class='highlight-cancel'>취소(중단)</span>되었습니다. (마지막 단계 미도달)<br><span class='highlight-money'>({money_summary_str})</span></span>"
                    if category_name not in anchor_map['canceled']:
                        if 'id=' not in anchor_id: anchor_id = f" id='cat-canc-{safe_cat_id}'"
                        anchor_map['canceled'].add(category_name)

                else:
                    # 3. 정상
                    status_badge = "<span class='status-badge bg-success'>SUCCESS</span>"
                    stat_success += 1
                    success_details_list.append(f"[{category_name}] 정상 완료")
                    narrative_text = f"<span class='narrative-text'><span class='highlight-time'>{start_time_str}</span>에 <span class='highlight-cate'>{category_name}</span> 거래가 <span class='highlight-success'>정상적으로 완료</span>되었습니다.<br><span class='highlight-money'>({money_summary_str})</span></span>"
                    if category_name not in anchor_map['success']:
                        if 'id=' not in anchor_id: anchor_id = f" id='cat-succ-{safe_cat_id}'"
                        anchor_map['success'].add(category_name)

                extra_anchors = ""
                if category_name in anchor_map['total'] and f"cat-total-{safe_cat_id}" not in anchor_id: extra_anchors += f"<span id='cat-total-{safe_cat_id}'></span>"
                if has_critical_error and category_name in anchor_map['fail'] and f"cat-fail-{safe_cat_id}" not in anchor_id: extra_anchors += f"<span id='cat-fail-{safe_cat_id}'></span>"
                if not has_critical_error and is_last_step_found and category_name in anchor_map['success'] and f"cat-succ-{safe_cat_id}" not in anchor_id: extra_anchors += f"<span id='cat-succ-{safe_cat_id}'></span>"
                if not has_critical_error and not is_last_step_found and category_name in anchor_map['canceled'] and f"cat-canc-{safe_cat_id}" not in anchor_id: extra_anchors += f"<span id='cat-canc-{safe_cat_id}'></span>"

                html_parts.append(f"""<div class='trans-card' {anchor_id}>{extra_anchors}<div class='card-header'><div>{narrative_text}</div><div>{status_badge}</div></div><div style='margin-bottom:15px; font-size:0.8em; color:#8B949E;'>📁 {filename}</div>""")

                for step_name in flow_list:
                    clean_step = "".join(step_name.split()).lower()
                    step_found = False; timestamp_str = "" 
                    step_line_idx = -1
                    for idx, line in enumerate(target_lines):
                        if clean_step in "".join(line.split()).lower():
                            step_found = True; step_line_idx = idx
                            time_match = RE_TIME.search(line)
                            if time_match: timestamp_str = time_match.group(1).split()[-1] 
                            break
                    
                    clean_name = step_name.replace("[SERVER CONTENTS]", "").strip()
                    
                    if step_found:
                        html_parts.append(f"""<div class='step-row border-pass'><div class='step-content'><span class='step-name'>✅ {clean_name}</span> <span style='font-family:monospace;'>{timestamp_str}</span></div>""")
                        
                        is_printed = False
                        card_data_buffer = []
                        is_capturing_card = False
                        
                        is_target_toggle_step = ("C_I_CREDIT" in step_name or "C_T_SEL_AMT" in step_name)
                        toggle_step_buffer = []
                        is_scan_pass_step = ("C_SCAN_PASS" in step_name) or ("SCAN_PASSPORT" in step_name)
                        scan_pass_buffer = []

                        for scan_idx in range(step_line_idx + 1, len(target_lines)):
                            current_line = target_lines[scan_idx]
                            if "[SERVER CONTENTS]" in current_line and "[ERROR]" not in current_line.upper(): break
                            
                            line_lower = current_line.lower()
                            line_content = current_line.strip().replace("<", "&lt;").replace(">", "&gt;")

                            final_output_html = ""
                            is_printed = False

                            if "client callback" in line_lower and ("wowiccard" in line_lower or "wowiccard_data" in line_lower):
                                is_capturing_card = True
                            
                            if is_capturing_card:
                                card_data_buffer.append(line_content)
                                if "empty" in line_lower or "result" in line_lower:
                                    is_capturing_card = False
                                    toggle_body = "<br>".join([f"<div class='data-line'>{l}</div>" for l in card_data_buffer])
                                    final_output_html = f"""<details class='card-data-toggle'><summary>📂 CARD DATA PACKET (Click)</summary><div class='toggle-content'>{toggle_body}</div></details>"""
                                    card_data_buffer = [] 
                                    is_printed = True
                                else:
                                    is_printed = True 
                            
                            if is_capturing_card: continue 
                            
                            if is_scan_pass_step:
                                scan_pass_buffer.append(line_content)
                                is_printed = True 
                            
                            if is_target_toggle_step and final_output_html:
                                toggle_step_buffer.append(final_output_html)
                                continue
                            elif is_target_toggle_step: 
                                pass

                            if is_printed and final_output_html:
                                if is_target_toggle_step: toggle_step_buffer.append(final_output_html)
                                else: html_parts.append(final_output_html)
                                continue

                            if not is_printed and "[error]" in line_lower:
                                final_output_html = f"<div class='critical-box'>🚨 {line_content}</div>"
                                is_printed = True
                            
                            if not is_printed and is_target_toggle_step:
                                is_printed = True
                                if "결제 성공" in line_content or "결제성공" in line_content:
                                    final_output_html = f"<div class='log-text'><span class='tag tag-money'>💳 결제 성공</span> {line_content}</div>"
                                else:
                                    final_output_html = f"<div class='log-text'>{line_content}</div>"

                            if not is_printed:
                                if "hscdu2_1" in line_lower or "hscdu2_2" in line_lower:
                                    calc_str = ""
                                    try:
                                        match = re.search(r"((?:\d+/\d+\s*,\s*)+\d+/\d+)", line_content)
                                        if match:
                                            parts = [p.strip() for p in match.group(1).split(',')]
                                            disp_counts = [int(p.split('/')[1]) for p in parts]
                                            krw_total = 0
                                            foreign_info = []
                                            if len(disp_counts) == 3:
                                                krw_total = disp_counts[0]*50000 + disp_counts[1]*10000 + disp_counts[2]*1000
                                            elif len(disp_counts) == 6:
                                                krw_total = disp_counts[0]*50000 + disp_counts[1]*10000 + disp_counts[3]*1000
                                                if disp_counts[2] > 0: foreign_info.append(f"TWD {disp_counts[2]}장")
                                                if disp_counts[4] > 0: foreign_info.append(f"USD {disp_counts[4]}장")
                                                if disp_counts[5] > 0: foreign_info.append(f"JPY {disp_counts[5]}장")
                                            
                                            if krw_total > 0:
                                                calc_str += f" <span style='color:#FFD700; font-weight:bold;'>(Total: {krw_total:,} KRW"
                                                if foreign_info: calc_str += " + " + ", ".join(foreign_info)
                                                calc_str += ")</span>"
                                            elif foreign_info:
                                                calc_str += f" <span style='color:#FFD700; font-weight:bold;'>(Foreign: {', '.join(foreign_info)})</span>"
                                    except: pass
                                    final_output_html = f"<div class='log-text'><span class='tag tag-money' style='background:rgba(255, 193, 7, 0.2); border-color:#FFC107; color:#FFD700;'>📤 출금</span> {line_content}{calc_str}</div>"
                                    is_printed = True
                                
                                elif "scn8237r" in line_lower and "accept" in line_lower:
                                    final_output_html = f"<div class='log-text'><span class='tag tag-money'>💵 입금</span> {line_content}</div>"
                                    is_printed = True
                                elif "passport" in line_lower and "scan" in step_name.lower():
                                    match = RE_PASSPORT.search(current_line)
                                    if match: 
                                        final_output_html = f"<div class='log-text'><span class='tag tag-card'>🛂 여권</span> {match.group(1)}</div>"
                                        is_printed = True
                                elif "결제 시작" in line_lower:
                                    final_output_html = f"<div class='log-text'><span class='tag tag-money'>💳 결제 요청</span> 시작</div>"
                                    is_printed = True

                            if is_printed and final_output_html:
                                if is_target_toggle_step: toggle_step_buffer.append(final_output_html)
                                elif not is_scan_pass_step: html_parts.append(final_output_html)

                        if card_data_buffer:
                            toggle_body = "<br>".join([f"<div class='data-line'>{l}</div>" for l in card_data_buffer])
                            html_str = f"<details class='card-data-toggle'><summary>📂 CARD DATA (Partial)</summary><div class='toggle-content'>{toggle_body}</div></details>"
                            if is_target_toggle_step: toggle_step_buffer.append(html_str)
                            elif not is_scan_pass_step: html_parts.append(html_str)
                        
                        if is_scan_pass_step and scan_pass_buffer:
                            final_buffer = []
                            for l in scan_pass_buffer:
                                if category_name == "외화 환전 (계좌 이체)" and (re.search(r"\{[A-Z]{3}\}.*\d+", l) or "환전" in l):
                                    final_buffer.append(f"<span class='tag tag-card'>💱 환전 정보</span> {l}")
                                else:
                                    final_buffer.append(l)
                            toggle_body = "<br>".join([f"<div class='data-line'>{l}</div>" for l in final_buffer])
                            html_parts.append(f"""<details class='card-data-toggle'><summary>🛂 PASSPORT SCAN DATA (Click)</summary><div class='toggle-content'>{toggle_body}</div></details>""")

                        if is_target_toggle_step and toggle_step_buffer:
                            toggle_body = "".join(toggle_step_buffer)
                            html_parts.append(f"""<details class='card-data-toggle'><summary>📜 FULL LOG ({len(toggle_step_buffer)} lines)</summary><div class='toggle-content'>{toggle_body}</div></details>""")

                        html_parts.append("</div>")

                    else:
                        if "C_SCAN_PASS" in step_name and category_name == "카드 충전 (현금)":
                            continue 
                        html_parts.append(f"""<div class='step-row border-fail'><div class='step-content'><span class='step-name' style='color:#F85149;'>❌ {clean_name}</span> (Missing)</div></div>""")

                html_parts.append("</div>")

    return found_any_target, "".join(html_parts), stat_total, stat_success, stat_canceled, stat_fail, success_details_list, issue_details_list

# ==========================================
# 3. 메인 UI (사이드바)
# ==========================================
if "log_folder_path" not in st.session_state:
    st.session_state.log_folder_path = r"C:\Users\jin33\OneDrive\바탕 화면\My_logs"

with st.sidebar:
    st.markdown("<div class='sidebar-header'><span>SYSTEM_CONTROLLER</span><span>v2.2</span></div>", unsafe_allow_html=True)
    
    st.markdown("<div class='control-label'><span class='label-accent'>01.</span> UPLOAD LOGS</div>", unsafe_allow_html=True)
    uploaded_files = st.file_uploader("Upload", accept_multiple_files=True, type=['txt', 'log'], label_visibility="collapsed")
    
    if uploaded_files:
        temp_dir = os.path.join(tempfile.gettempdir(), "neural_core_logs")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        # Save uploaded files
        for uploaded_file in uploaded_files:
            with open(os.path.join(temp_dir, uploaded_file.name), "wb") as f:
                f.write(uploaded_file.getbuffer())
        
        st.session_state.log_folder_path = temp_dir
    
    st.markdown("<div class='separator-line'></div>", unsafe_allow_html=True)
    
    # [수정] 날짜 필터링 UI 제거 (내부적으로 전체 기간 설정)
    start_date = datetime(2000, 1, 1)
    end_date = datetime(2099, 12, 31)

    st.markdown("<div class='control-label'><span class='label-accent'>02.</span> PROTOCOL</div>", unsafe_allow_html=True)
    search_mode_ui = st.radio("Mode", ["DEEP_SCAN", "TEXT_FIND"], horizontal=True, label_visibility="collapsed", key="ui_mode_selection")

    search_mode = "단순 텍스트 검색" 
    selected_category = "전체"
    keyword = ""

    if search_mode_ui == "DEEP_SCAN":
        search_mode = "거래 정밀 분석"
        st.markdown("<div class='control-label'><span class='label-accent'>03.</span> TYPE SELECTOR</div>", unsafe_allow_html=True)
        category_list = ["ALL_TYPES"] + list(TRANSACTION_MAP.keys())
        cat_selection = st.selectbox("Category", category_list, label_visibility="collapsed", key="sb_category")
        selected_category = "전체" if cat_selection == "ALL_TYPES" else cat_selection
        st.markdown("<div class='control-label'><span class='label-accent'>04.</span> TARGET KEY</div>", unsafe_allow_html=True)
        keyword = st.text_input("Keyword_Deep", value="", label_visibility="collapsed", placeholder="CARD / PASSPORT NO.", key="input_deep_keyword")
    else:
        search_mode = "단순 텍스트 검색"
        selected_category = "전체"
        st.markdown("<div class='control-label'><span class='label-accent'>03.</span> QUERY STRING</div>", unsafe_allow_html=True)
        keyword = st.text_input("Keyword_Simple", value="", label_visibility="collapsed", placeholder="SEARCH PATTERN...", key="input_simple_keyword")

    st.markdown("<div class='separator-line'></div>", unsafe_allow_html=True)
    search_btn = st.button("EXECUTE_PROTOCOL", type="primary")
    st.markdown("""<div style='margin-top: 15px; font-size: 9px; color: #37474F; text-align: center; font-family: "JetBrains Mono", monospace; opacity: 0.7;'>NEURAL_CORE // ACCESS_GRANTED</div>""", unsafe_allow_html=True)

# ==========================================
# 4. 메인 실행 로직
# ==========================================
if search_btn:
    if not os.path.exists(st.session_state.log_folder_path):
        st.error(f"❌ 폴더를 찾을 수 없습니다: {st.session_state.log_folder_path}")
    elif not keyword.strip():
        st.warning("⚠️ 검색어를 입력해주세요!")
    else:
        show_ai_loading_effect(keyword)
        with st.spinner('GENERATING FINAL REPORT...'):
            found_total = False; final_html = ""
            grand_total = 0; grand_success = 0; grand_canceled = 0; grand_fail = 0
            grand_success_details = []; grand_issue_details = []
            stats_total = defaultdict(int); stats_success = defaultdict(int); stats_canceled = defaultdict(int); stats_fail = defaultdict(int)
            anchor_map = {'total': set(), 'success': set(), 'canceled': set(), 'fail': set()}

            if search_mode == "거래 정밀 분석":
                processed_keyword = "".join(keyword.split()).lower()
                target_configs = TRANSACTION_MAP.items() if selected_category == "전체" else [(selected_category, TRANSACTION_MAP[selected_category])]
                html_list = []
                for category_name, config in target_configs:
                    flow_list, mode, validator = config
                    found, html_res, c_tot, c_suc, c_canc, c_fail, s_list, i_list = analyze_flow_web(
                        st.session_state.log_folder_path, processed_keyword, flow_list, mode, validator, start_date, end_date, category_name, anchor_map
                    )
                    if found:
                        found_total = True; html_list.append(html_res)
                        grand_total += c_tot; grand_success += c_suc; grand_canceled += c_canc; grand_fail += c_fail
                        grand_success_details.extend(s_list); grand_issue_details.extend(i_list)
                        stats_total[category_name] += c_tot
                        if c_suc > 0: stats_success[category_name] += c_suc
                        if c_canc > 0: stats_canceled[category_name] += c_canc
                        if c_fail > 0: stats_fail[category_name] += c_fail
                final_html = "".join(html_list)
            else:
                found_total, final_html, grand_total = search_simple_text(st.session_state.log_folder_path, keyword, start_date, end_date)
                grand_success = grand_total; grand_fail = 0
                if found_total: stats_total["Simple Search"] = grand_total

            if found_total:
                draw_summary_ui(grand_total, grand_success, grand_canceled, grand_fail, grand_success_details, grand_issue_details, stats_total, stats_success, stats_canceled, stats_fail)
                st.markdown(final_html, unsafe_allow_html=True)
            else:
                st.warning(f"😥 NO RECORDS FOUND FOR '{keyword}'")
else:
    draw_landing_page(st.session_state.log_folder_path)import streamlit as st
import os
import re
import time
import threading
import hashlib  # [추가] 중복 방지를 위한 해시 모듈
import tempfile # [추가] 업로드 파일 임시 저장을 위한 모듈
import shutil   # [추가] 파일 작업을 위한 모듈
from datetime import datetime, timedelta
from collections import defaultdict
from streamlit.runtime import get_instance

# ==========================================
# [시스템] 브라우저 자동 종료 감시
# ==========================================
def monitor_browser_close():
    time.sleep(5)
    while True:
        try:
            runtime = get_instance()
            if runtime:
                session_infos = runtime._session_mgr.list_active_sessions()
                if len(session_infos) == 0:
                    time.sleep(2)
                    if len(runtime._session_mgr.list_active_sessions()) == 0:
                        os._exit(0) 
        except Exception:
            pass 
        time.sleep(1)

if "monitor_started" not in st.session_state:
    st.session_state.monitor_started = True
    threading.Thread(target=monitor_browser_close, daemon=True).start()

# ==========================================
# 0. 페이지 설정 및 CSS
# ==========================================
st.set_page_config(page_title="NEURAL CORE", page_icon="💠", layout="wide")

st.markdown("""
<style>
    /* 폰트 로드 */
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700;800&display=swap');
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

    /* GLOBAL THEME */
    .stApp, section[data-testid="stSidebar"], .stMarkdown, .stMarkdown p, .stText, h1, h2, h3 {
        background-color: #0E1117;
        color: #ECEFF1 !important;
        font-family: 'Pretendard', sans-serif; 
    }

    /* SIDEBAR STYLE */
    section[data-testid="stSidebar"] {
        background-color: #050608;
        border-right: 1px solid #1E2329;
        width: 300px;
    }
    .sidebar-header {
        font-family: 'JetBrains Mono', monospace !important;
        color: #00E5FF !important;
        font-size: 14px;
        font-weight: 800;
        border-bottom: 2px solid #00E5FF;
        padding-bottom: 12px;
        margin-bottom: 25px;
        letter-spacing: 2px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        text-shadow: 0 0 10px rgba(0, 229, 255, 0.4);
    }
    div.control-label {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 10px !important;
        font-weight: 700 !important;
        color: #546E7A !important;
        margin-top: 20px;
        margin-bottom: 8px;
        letter-spacing: 1px;
        display: flex;
        align-items: center;
        text-transform: uppercase;
    }
    .label-accent { color: #00E5FF; margin-right: 6px; }
    
    /* Input Widgets */
    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: #0E1117 !important;
        color: #ECEFF1 !important;
        border: 1px solid #263238 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 11px !important;
        border-radius: 0px !important;
        min-height: 32px !important;
        transition: border 0.3s, box-shadow 0.3s;
    }
    section[data-testid="stSidebar"] input:focus,
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div:focus-within {
        border-color: #00E5FF !important;
        box-shadow: 0 0 8px rgba(0, 229, 255, 0.2) !important;
    }
    
    /* Radio Buttons */
    section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] {
        display: flex;
        gap: 0px;
        background: transparent;
        border: 1px solid #263238;
    }
    section[data-testid="stSidebar"] .stRadio label {
        background: #0E1117;
        border: none;
        padding: 6px 0;
        margin: 0;
        border-radius: 0px;
        flex: 1;
        display: flex;
        justify-content: center;
        align-items: center;
        border-right: 1px solid #263238;
        transition: all 0.2s;
    }
    section[data-testid="stSidebar"] .stRadio label:last-child { border-right: none; }
    section[data-testid="stSidebar"] .stRadio label p {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 10px !important;
        color: #607D8B !important;
        font-weight: 700;
    }
    section[data-testid="stSidebar"] .stRadio div[aria-checked="true"] {
        background-color: rgba(0, 229, 255, 0.1) !important;
    }
    section[data-testid="stSidebar"] .stRadio div[aria-checked="true"] p {
        color: #00E5FF !important;
        text-shadow: 0 0 5px rgba(0, 229, 255, 0.5);
    }
    
    /* Button */
    section[data-testid="stSidebar"] .stButton { margin-top: 30px; }
    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        height: 45px;
        background: transparent;
        color: #00E5FF;
        border: 1px solid #00E5FF;
        border-radius: 0px;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 800;
        font-size: 12px;
        letter-spacing: 2px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        box-shadow: 0 0 5px rgba(0, 229, 255, 0.2);
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: #00E5FF;
        color: #000 !important;
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.6);
        border-color: #00E5FF;
        transform: translateY(-1px);
    }
    section[data-testid="stSidebar"] .stButton > button:active {
        transform: translateY(1px);
        box-shadow: 0 0 5px rgba(0, 229, 255, 0.4);
    }
    .separator-line { height: 1px; background: linear-gradient(90deg, #1E2329, transparent); margin: 25px 0; }

    /* DASHBOARD STYLES */
    .stMainBlockContainer {
        max-width: 1400px !important;
        margin-left: auto !important;
        margin-right: auto !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    .st-emotion-cache-zh2fnc { width: 100% !important; }

    .dashboard-container {
        background: #0D1117;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 30px;
        border: 1px solid #30363D;
        display: flex;
        gap: 20px;
        justify-content: space-between;
    }
    .stat-panel {
        flex: 1;
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid #30363D;
        border-radius: 12px;
        padding: 15px 20px;
        display: flex;
        align-items: center; 
        justify-content: flex-start;
        gap: 20px;
        transition: border-color 0.3s;
    }
    .stat-panel:hover { border-color: #58A6FF; }
    .stat-main {
        text-align: center;
        min-width: 70px;
        border-right: 1px solid rgba(255,255,255,0.1);
        padding-right: 15px;
        margin-right: 5px;
    }
    .stat-label { color: #8B949E; font-size: 0.8em; font-weight: 700; letter-spacing: 1px; margin-bottom: 2px; }
    .stat-value { font-size: 1.8em; font-weight: 800; color: #fff; line-height: 1; }
    .stat-details {
        flex: 1;
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        align-content: center;
    }
    .detail-badge {
        display: inline-flex;
        align-items: center;
        text-decoration: none !important;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 0.7em;
        font-weight: 600;
        transition: all 0.2s;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        color: #C9D1D9;
    }
    .detail-badge:hover { transform: translateY(-2px); filter: brightness(1.2); }
    .count-tag { border-radius: 10px; padding: 0 6px; margin-left: 6px; font-size: 0.9em; font-weight: bold; }

    /* Theme Colors */
    .theme-blue .stat-label { color: #58A6FF; }
    .theme-blue .stat-value { text-shadow: 0 0 15px rgba(88, 166, 255, 0.3); }
    .theme-blue .detail-badge { border-color: rgba(88, 166, 255, 0.3); color: #a5d6ff; }
    .theme-blue .count-tag { background: #58A6FF; color: #000; }

    .theme-green .stat-label { color: #3FB950; }
    .theme-green .stat-value { text-shadow: 0 0 15px rgba(63, 185, 80, 0.3); }
    .theme-green .detail-badge { border-color: rgba(63, 185, 80, 0.3); color: #b3f2c4; }
    .theme-green .count-tag { background: #3FB950; color: #000; }

    .theme-orange .stat-label { color: #D29922; }
    .theme-orange .stat-value { text-shadow: 0 0 15px rgba(210, 153, 34, 0.3); }
    .theme-orange .detail-badge { border-color: rgba(210, 153, 34, 0.3); color: #FFECB3; }
    .theme-orange .count-tag { background: #D29922; color: #000; }

    .theme-red .stat-label { color: #F85149; }
    .theme-red .stat-value { text-shadow: 0 0 15px rgba(248, 81, 73, 0.3); }
    .theme-red .detail-badge { border-color: rgba(248, 81, 73, 0.3); color: #ffdcd7; }
    .theme-red .count-tag { background: #F85149; color: #000; }

    /* Transaction Card */
    .trans-card {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-left: 4px solid #58A6FF;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        scroll-margin-top: 20px;
    }
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: linear-gradient(90deg, rgba(33, 60, 100, 0.6) 0%, rgba(22, 33, 62, 0.3) 100%);
        border: 1px solid rgba(88, 166, 255, 0.3);
        border-radius: 10px;
        padding: 12px 18px;
        margin-bottom: 15px;
        box-shadow: inset 0 0 15px rgba(0, 0, 0, 0.2);
    }
    .status-badge { padding: 4px 10px; border-radius: 6px; font-size: 0.75em; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; }
    .bg-success { background: rgba(35, 134, 54, 0.2); color: #3FB950; border: 1px solid rgba(35, 134, 54, 0.4); }
    .bg-error { background: rgba(218, 54, 51, 0.2); color: #F85149; border: 1px solid rgba(218, 54, 51, 0.4); }
    .bg-warn { background: rgba(210, 153, 34, 0.2); color: #D29922; border: 1px solid rgba(210, 153, 34, 0.4); }

    .step-row { border-left: 2px solid #30363D; padding-left: 20px; margin-bottom: 6px; }
    .border-pass { border-left-color: #3FB950; }
    .border-fail { border-left-color: #F85149; }
    .step-name { font-weight: bold; color: #E6EDF3; margin-right: 10px; }
    
    .highlight-time { color: #58A6FF; font-weight: bold; font-family: monospace; }
    .highlight-cate { color: #C9D1D9; font-weight: bold; }
    .highlight-money { color: #D29922; font-weight: bold; font-family: monospace; }
    .headline-rate { color: #4FC3F7; margin-left: 10px; font-size: 0.9em; font-weight: bold; }
    .highlight-out { color: #FF7B72; font-weight: bold; font-family: monospace; margin-left: 5px; } 

    .tag { padding: 2px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; margin-left: 5px; font-family: 'Consolas', monospace; }
    .tag-money { background: rgba(210, 153, 34, 0.2); color: #D29922; border: 1px solid rgba(210, 153, 34, 0.4); }
    .tag-card { background: rgba(88, 166, 255, 0.2); color: #58A6FF; border: 1px solid rgba(88, 166, 255, 0.4); }
    
    .critical-box {
        background: rgba(248, 81, 73, 0.1);
        border-left: 4px solid #F85149;
        color: #FF7B72;
        padding: 10px;
        margin: 8px 0;
        font-family: monospace;
        font-weight: bold;
    }
    
    .stMainBlockContainer { 
        margin : auto;
    }
    
    details.card-data-toggle { background-color: #252526; border: 1px solid #444; border-radius: 6px; margin: 5px 0; overflow: hidden; }
    details.card-data-toggle summary { padding: 8px 12px; cursor: pointer; font-size: 13px; font-weight: bold; color: #90CAF9; background-color: #2D2D2D; list-style: none; display: flex; align-items: center; }
    details.card-data-toggle summary:hover { background-color: #383838; }
    details.card-data-toggle summary::before { content: "▶"; font-size: 10px; margin-right: 8px; transition: transform 0.2s; color: #90CAF9; }
    details.card-data-toggle[open] summary::before { transform: rotate(90deg); }
    .toggle-content { padding: 10px; background-color: #1a1a1a; border-top: 1px solid #444; font-family: 'Consolas', monospace; font-size: 12px; color: #ccc; line-height: 1.4; white-space: pre-wrap; }
    .data-line { margin-bottom: 2px; border-bottom: 1px dashed #333; padding-bottom: 2px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. 플로우 정의 (상수)
# ==========================================
RE_DATE = re.compile(r"(\d{4}-\d{2}-\d{2})")
RE_TIME = re.compile(r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})")
RE_MONEY = re.compile(r"\{(\d+)\}\s*/\s*([A-Z]+)\s*/\s*(\d+)")
RE_PASSPORT = re.compile(r"passport\s*:\s*\{(.*?)\}", re.IGNORECASE)
RE_PAYMENT_REQ = re.compile(r"결제요청하기\s*->\s*(\d+)")

FLOW_CARD_CASH = ["[SERVER CONTENTS]CARD_INDEX2", "[SERVER CONTENTS]CARD_MAIN", "[SERVER CONTENTS]C_SEL_CURRENCY", "[SERVER CONTENTS]C_SCAN_PASS", "[SERVER CONTENTS]C_I_AGREE", "[SERVER CONTENTS]C_I_INPUT", "[SERVER CONTENTS]C_I_SELCASH", "[SERVER CONTENTS]C_I_SELAMT", "[SERVER CONTENTS]C_I_OUTKRW", "[SERVER CONTENTS]C_I_ACTIVATE", "[SERVER CONTENTS]C_RECEIPT", "[SERVER CONTENTS]C_I_COMPLETE"]
FLOW_CARD_CREDIT = ["[SERVER CONTENTS]CARD_INDEX2", "[SERVER CONTENTS]CARD_MAIN", "[SERVER CONTENTS]C_I_SELVOUCHER", "[SERVER CONTENTS]C_SEL_PAYMENT", "[SERVER CONTENTS]C_SCAN_PASS", "[SERVER CONTENTS]C_I_AGREE", "[SERVER CONTENTS]C_I_CREDIT", "[SERVER CONTENTS]C_I_PAYMENT", "[SERVER CONTENTS]C_I_ACTIVATE", "[SERVER CONTENTS]C_RECEIPT", "[SERVER CONTENTS]C_I_COMPLETE"]
FLOW_CARD_REISSUE = ["[SERVER CONTENTS]CARD_INDEX2", "[SERVER CONTENTS]CARD_MAIN", "[SERVER CONTENTS]C_R_AGREE", "[SERVER CONTENTS]C_SCAN_PASS", "[SERVER CONTENTS]C_VERIFY_PIN", "[SERVER CONTENTS]C_R_ACTIVATE", "[SERVER CONTENTS]C_RECEIPT", "[SERVER CONTENTS]C_R_COMPLETE"]
FLOW_CHARGE_CASH = ["[SERVER CONTENTS]CARD_INDEX2", "[SERVER CONTENTS]CARD_MAIN", "[SERVER CONTENTS]C_T_TARGET", "[SERVER CONTENTS]C_SEL_PAYMENT", "[SERVER CONTENTS]C_INSERT_CARD", "[SERVER CONTENTS]C_SCAN_PASS", "[SERVER CONTENTS]C_SEL_CURRENCY", "[SERVER CONTENTS]C_T_INPUT", "[SERVER CONTENTS]C_T_TRANSACTION", "[SERVER CONTENTS]C_T_RECEIPT", "[SERVER CONTENTS]C_T_COMPLETE"]
FLOW_CHARGE_CREDIT = ["[SERVER CONTENTS]CARD_INDEX2", "[SERVER CONTENTS]CARD_MAIN", "[SERVER CONTENTS]C_T_TARGET", "[SERVER CONTENTS]C_SEL_PAYMENT", "[SERVER CONTENTS]C_INSERT_CARD", "[SERVER CONTENTS]C_T_SEL_AMT", "[SERVER CONTENTS]C_T_PAYMENT", "[SERVER CONTENTS]C_T_RECEIPT", "[SERVER CONTENTS]C_T_COMPLETE"]
FLOW_EXCHANGE_KRW = ["[SERVER CONTENTS]CARD_INDEX2", "[SERVER CONTENTS]MAIN", "[SERVER CONTENTS]SCAN_BY_PASSPORT", "[SERVER CONTENTS]INPUT_CURRENCY", "[SERVER CONTENTS]RECEIPT_OUTPUT", "[SERVER CONTENTS]OUTPUT_KRW", "[SERVER CONTENTS]OUTPUT_THERMAL"]
FLOW_EXCHANGE_FOREIGN = ["[SERVER CONTENTS]CARD_INDEX2", "[SERVER CONTENTS]MAIN2", "[SERVER CONTENTS]CALCULATOR_CURRENCY", "[SERVER CONTENTS]SCAN_PASSPORT", "[SERVER CONTENTS]SELECT_SALE_GB", "[SERVER CONTENTS]INPUT_KRW", "[SERVER CONTENTS]OUTPUT_CURRENCY", "[SERVER CONTENTS]OUTPUT_THERMAL_CURRENCY"]
FLOW_CARD_WITHDRAWAL = ["[SERVER CONTENTS]CARD_INDEX2", "[SERVER CONTENTS]CARD_MAIN", "[SERVER CONTENTS]C_INSERT_CARD", "[SERVER CONTENTS]C_VERIFY_PIN", "[SERVER CONTENTS]C_W_SELECT_AMT", "[SERVER CONTENTS]C_W_OUTKRW", "[SERVER CONTENTS]C_W_COMPLETE"]
FLOW_EXCHANGE_FOREIGN_CREDIT = ["[SERVER CONTENTS]CARD_INDEX2", "[SERVER CONTENTS]CALCULATOR_CURRENCY", "[SERVER CONTENTS]SCAN_PASSPORT", "[SERVER CONTENTS]SELECT_SALE_GB", "[SERVER CONTENTS]SALE_ACC_PHONE", "[SERVER CONTENTS]SALE_ACC_CHECK", "[SERVER CONTENTS]SALE_ACC_OUTPUT_CURRENCY", "[SERVER CONTENTS]OUTPUT_THERMAL_CURRENCY"]

TRANSACTION_MAP = {
    "카드 발급 (현금)": (FLOW_CARD_CASH, "CASH", "C_I_INPUT"),
    "카드 발급 (신용카드)": (FLOW_CARD_CREDIT, "CREDIT", "C_I_CREDIT"),
    "카드 재발급": (FLOW_CARD_REISSUE, "REISSUE", "C_R_ACTIVATE"),
    "카드 충전 (현금)": (FLOW_CHARGE_CASH, "CASH", "C_T_INPUT"),
    "카드 충전 (신용카드)": (FLOW_CHARGE_CREDIT, "CREDIT", "C_T_SEL_AMT"),
    "원화 환전": (FLOW_EXCHANGE_KRW, "EXCHANGE", "INPUT_CURRENCY"),
    "외화 환전 (현금)": (FLOW_EXCHANGE_FOREIGN, "EXCHANGE_FOREIGN", "INPUT_KRW"),
    "외화 환전 (계좌 이체)": (FLOW_EXCHANGE_FOREIGN_CREDIT, "CREDIT", "SALE_ACC_CHECK"),
    "카드 출금": (FLOW_CARD_WITHDRAWAL, "WITHDRAWAL", "C_W_SELECT_AMT"),
}

# ==========================================
# 2. 유틸리티 및 분석 로직
# ==========================================
def read_log_file(path):
    try:
        with open(path, 'r', encoding='cp949') as f: return f.readlines()
    except:
        try:
            with open(path, 'r', encoding='utf-8') as f: return f.readlines()
        except: return []

def get_folder_stats(folder_path):
    if not os.path.exists(folder_path): return None
    file_count = 0; total_size = 0; last_mod_time = 0
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".txt") or file.endswith(".log"):
                file_count += 1
                fp = os.path.join(root, file)
                try:
                    stats = os.stat(fp)
                    total_size += stats.st_size
                    if stats.st_mtime > last_mod_time: last_mod_time = stats.st_mtime
                except: pass
    if total_size < 1024: size_str = f"{total_size} B"
    elif total_size < 1024**2: size_str = f"{total_size/1024:.1f} KB"
    else: size_str = f"{total_size/1024**2:.1f} MB"
    last_active = datetime.fromtimestamp(last_mod_time).strftime("%Y-%m-%d %H:%M") if last_mod_time > 0 else "N/A"
    return {"count": file_count, "size": size_str, "last_active": last_active}

def show_ai_loading_effect(keyword):
    status_text = st.empty()
    bar = st.progress(0)
    search_term = keyword if keyword.strip() else "GLOBAL_SCAN"
    steps = [
        "🔄 Initializing Neural Search Engine...",
        "📂 Loading Log Files into Memory...",
        f"🔍 Scanning Pattern: '{search_term}'",
        "🧠 Vectorizing Transaction Flows...",
        "⚠️ Cross-referencing Error Codes...",
        "📊 Calculating Success Metrics...",
        "✅ Analysis Complete."
    ]
    for i, step in enumerate(steps):
        status_text.markdown(f"<span style='font-family:monospace; color:#58A6FF; font-weight:bold;'>{step}</span>", unsafe_allow_html=True)
        bar.progress((i + 1) * (100 // len(steps)))
        time.sleep(0.15) 
    time.sleep(0.3)
    status_text.empty()
    bar.empty()

# [수정] 대시보드 UI - 4분할 (Total, Success, Canceled, Error)
def draw_summary_ui(total_cnt, success_cnt, canceled_cnt, fail_cnt, success_details, issue_details, stats_total, stats_success, stats_canceled, stats_fail):
    if total_cnt == 0: return
    
    success_rate = (success_cnt / total_cnt * 100) if total_cnt > 0 else 0
    ai_comment = ""
    ai_color = ""
    ai_border_color = ""
    
    if fail_cnt == 0 and canceled_cnt == 0:
        ai_comment = "모든 거래가 정상적으로 완료되었습니다. 시스템 상태가 **매우 안정적(Stable)**입니다."
        ai_color = "#3FB950" 
        ai_border_color = "#2ea043"
    elif success_rate < 50:
        ai_comment = f"⚠️ **주의 요망(Critical):** 거래 성공률이 {success_rate:.1f}%로 매우 낮습니다. 에러 및 중단 로그를 집중 점검하세요."
        ai_color = "#F85149" 
        ai_border_color = "#da3633"
    else:
        ai_comment = f"거래 분석 완료. **성공 {success_cnt}건**, **취소 {canceled_cnt}건**, **에러 {fail_cnt}건**이 감지되었습니다."
        ai_color = "#D29922" 
        ai_border_color = "#bb8800"

    st.markdown(f"""
    <div style='background: rgba(22, 27, 34, 0.8); border-left: 5px solid {ai_border_color}; padding: 20px; border-radius: 8px; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);'>
        <div style='color: {ai_color}; font-weight: 800; font-size: 0.9em; margin-bottom: 8px; letter-spacing: 1px;'>🤖 AI ANALYST BRIEFING</div>
        <div style='color: #E6EDF3; font-size: 1.15em; line-height: 1.5;'>"{ai_comment}"</div>
    </div>
    """, unsafe_allow_html=True)

    def create_badges_html(stats_dict, prefix_id=""):
        if not stats_dict: return "<span style='color:#555; font-size:0.8em;'>- 없음 -</span>"
        html = ""
        for cat, count in stats_dict.items():
            safe_id = re.sub(r'[^a-zA-Z0-9]', '', cat)
            html += f"<a href='#{prefix_id}{safe_id}' class='detail-badge' target='_self'>{cat} <span class='count-tag'>{count}</span></a> "
        return html

    html = f"""
    <div class='dashboard-container'>
        <div class='stat-panel theme-blue'>
            <div class='stat-main'><div class='stat-label'>TOTAL</div><div class='stat-value'>{total_cnt}</div></div>
            <div class='stat-details'>{create_badges_html(stats_total, "cat-total-")}</div>
        </div>
        <div class='stat-panel theme-green'>
            <div class='stat-main'><div class='stat-label'>SUCCESS</div><div class='stat-value'>{success_cnt}</div></div>
            <div class='stat-details'>{create_badges_html(stats_success, "cat-succ-")}</div>
        </div>
        <div class='stat-panel theme-orange'>
            <div class='stat-main'><div class='stat-label'>CANCELED</div><div class='stat-value'>{canceled_cnt}</div></div>
            <div class='stat-details'>{create_badges_html(stats_canceled, "cat-canc-")}</div>
        </div>
        <div class='stat-panel theme-red'>
            <div class='stat-main'><div class='stat-label'>ERROR</div><div class='stat-value'>{fail_cnt}</div></div>
            <div class='stat-details'>{create_badges_html(stats_fail, "cat-fail-")}</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def draw_landing_page(folder_path):
    st.markdown("""
<style>
    /* 전체 컨테이너 */
    .neural-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 40px 0;
        perspective: 1000px;
    }

    /* 타이틀 스타일 */
    .neural-title {
        font-size: 3em;
        font-weight: 800;
        letter-spacing: 4px;
        background: linear-gradient(to bottom, #fff, #58A6FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
        text-shadow: 0 0 20px rgba(88, 166, 255, 0.5);
    }
    
    /* 뉴럴 코어 애니메이션 */
    .core-container {
        position: relative;
        width: 220px;
        height: 200px;
        margin: 40px auto;
        display: flex;
        justify-content: center;
        align-items: center;
    }

    /* 중앙 빛나는 구체 */
    .ai-core {
        width: 100px;
        height: 100px;
        background: radial-gradient(circle at 30% 30%, #a5d6ff, #0D47A1);
        border-radius: 50%;
        box-shadow: 0 0 40px #007bff, inset 0 0 20px #fff;
        z-index: 10;
        animation: breathe 3s infinite ease-in-out;
    }

    /* 회전하는 바깥 링 1 */
    .ring-1 {
        position: absolute;
        width: 160px;
        height: 160px;
        border: 2px solid rgba(88, 166, 255, 0.3);
        border-top: 2px solid #58A6FF;
        border-radius: 50%;
        animation: spin 4s linear infinite;
    }

    /* 회전하는 바깥 링 2 (반대 방향) */
    .ring-2 {
        position: absolute;
        width: 190px;
        height: 190px;
        border: 1px dashed rgba(88, 166, 255, 0.4);
        border-radius: 50%;
        animation: spin-reverse 7s linear infinite;
    }

    /* 애니메이션 키프레임 */
    @keyframes breathe {
        0% { transform: scale(0.95); box-shadow: 0 0 25px #007bff; }
        50% { transform: scale(1.05); box-shadow: 0 0 50px #00aaff; }
        100% { transform: scale(0.95); box-shadow: 0 0 25px #007bff; }
    }
    @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    @keyframes spin-reverse { 0% { transform: rotate(360deg); } 100% { transform: rotate(0deg); } }

    /* HUD 카드 스타일 (PCT.py 디자인 적용) */
    .hud-card {
        background: rgba(13, 17, 23, 0.8);
        border: 1px solid rgba(88, 166, 255, 0.2);
        border-left: 3px solid #58A6FF;
        padding: 20px;
        position: relative;
        overflow: hidden;
        transition: all 0.3s;
    }
    .hud-card:hover {
        border-color: #58A6FF;
        box-shadow: 0 0 15px rgba(88, 166, 255, 0.1);
        transform: translateY(-5px);
    }
    
    /* 스캔라인 애니메이션 (누락되었던 부분 추가) */
    .hud-card::after {
        content: '';
        position: absolute;
        top: 0; left: 0; width: 100%; height: 2px;
        background: linear-gradient(90deg, transparent, rgba(88, 166, 255, 0.8), transparent);
        animation: scanline 3s infinite linear;
        opacity: 0.5;
    }
    @keyframes scanline { 0% { top: -10%; } 100% { top: 110%; } }

    .hud-label {
        font-size: 0.8em;
        color: #58A6FF;
        letter-spacing: 1px;
        margin-bottom: 5px;
        text-transform: uppercase;
    }
    .hud-value {
        font-size: 1.8em;
        color: #fff;
        font-weight: 700;
        font-family: 'Consolas', monospace;
        text-shadow: 0 0 5px rgba(255,255,255,0.3);
    }
    
    .system-msg {
        font-family: 'Consolas', monospace;
        color: #8B949E;
        font-size: 0.9em;
        margin-top: 10px;
        text-align: center;
    }
    .blink { animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }

</style>
""", unsafe_allow_html=True)

    stats = get_folder_stats(folder_path)
    
    if not stats:
        stats = {"count": 0, "size": "0 B", "last_active": "OFFLINE"}
        status_msg = "⚠️ TARGET NOT FOUND - SYSTEM OFFLINE"
    else:
        status_msg = f"SYSTEM ONLINE · WATCHING {os.path.basename(folder_path)}"

    # 메인 코어 UI
    st.markdown(f"""
<div class='neural-wrapper'>
<div class='neural-title'>NEURAL CORE</div>
<div style='color:#8B949E; letter-spacing:2px; font-size:0.9em; margin-bottom:10px;'>DIGITAL FORENSIC ENGINE v2.2</div>
<div class='core-container'>
<div class='ring-1'></div>
<div class='ring-2'></div>
<div class='ai-core'></div>
</div>
<div class='system-msg'>
<span class='blink'>_</span> {status_msg}
</div>
</div>
""", unsafe_allow_html=True)
    
    # 하단 HUD 통계 (PCT.py와 동일하게 3단 구성으로 변경)
    if stats['count'] > 0:
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.markdown(f"""
<div class='hud-card'>
<div class='hud-label'>MEMORY NODES</div>
<div class='hud-value'>{stats['count']}</div>
<div style='font-size:0.7em; color:#8B949E; margin-top:5px;'>LOG FILES DETECTED</div>
</div>
""", unsafe_allow_html=True)
            
        with c2:
            st.markdown(f"""
<div class='hud-card'>
<div class='hud-label'>DATA DENSITY</div>
<div class='hud-value'>{stats['size']}</div>
<div style='font-size:0.7em; color:#8B949E; margin-top:5px;'>TOTAL STORAGE USAGE</div>
</div>
""", unsafe_allow_html=True)
            
        with c3:
            st.markdown(f"""
<div class='hud-card'>
<div class='hud-label'>LAST SYNC</div>
<div class='hud-value' style='font-size:1.4em; line-height:1.4;'>{stats['last_active']}</div>
<div style='font-size:0.7em; color:#8B949E; margin-top:5px;'>TIMESTAMP CONFIRMED</div>
</div>
""", unsafe_allow_html=True)
            
    else:
        st.error(f"❌ 폴더를 찾을 수 없습니다: {folder_path}")

def search_simple_text(folder_path, keyword, start_date, end_date):
    html_parts = []
    found_any = False
    s_date_str = start_date.strftime("%Y-%m-%d")
    e_date_str = end_date.strftime("%Y-%m-%d")
    keyword_no_space = "".join(keyword.split()).lower()
    total_found_lines = 0 
    
    for foldername, subfolders, filenames in os.walk(folder_path):
        for filename in filenames:
            if not (filename.endswith(".txt") or filename.endswith(".log")): continue
            date_match = RE_DATE.search(filename)
            if date_match:
                file_date = date_match.group(1)
                if not (s_date_str <= file_date <= e_date_str): continue
            
            full_path = os.path.join(foldername, filename)
            file_lines = read_log_file(full_path)
            if not file_lines: continue
            
            found_lines_in_file = []
            for idx, line in enumerate(file_lines):
                if keyword_no_space in "".join(line.split()).lower():
                    clean_line = line.strip().replace("<", "&lt;").replace(">", "&gt;") 
                    highlighted_line = re.sub(f"({re.escape(keyword)})", r"<span class='pill pill-warn'>\1</span>", clean_line, flags=re.IGNORECASE)
                    found_lines_in_file.append((idx + 1, highlighted_line, line.strip()))
            
            if found_lines_in_file:
                found_any = True
                total_found_lines += len(found_lines_in_file)
                html_parts.append(f"""<div class='trans-card'><div class='card-header'><span class='highlight-cate'>📂 {filename}</span><span class='status-badge bg-warn'>{len(found_lines_in_file)} HITS</span></div>""")
                for line_num, html_line, raw_line in found_lines_in_file:
                    html_parts.append(f"<div class='step-row border-fail'><div class='log-text'>Line {line_num}: {html_line}</div></div>")
                html_parts.append("</div>")

    return found_any, "".join(html_parts), total_found_lines

# [수정] 분석 로직 (중복 제거 강화 및 환전 파싱)
def analyze_flow_web(folder_path, target_keyword, flow_list, mode, validator_step, start_date, end_date, category_name, anchor_map):
    html_parts = []
    found_any_target = False 
    
    success_details_list = []
    issue_details_list = []
    
    stat_total = 0; stat_success = 0; stat_canceled = 0; stat_fail = 0
    
    if not flow_list: return False, "", 0, 0, 0, 0, [], []

    start_step_marker = "".join(flow_list[0].split()).lower()
    last_step_marker = "".join(flow_list[-1].split()).lower()
    
    s_date_str = start_date.strftime("%Y-%m-%d")
    e_date_str = end_date.strftime("%Y-%m-%d")
    processed_keyword_lower = target_keyword

    # [추가] 글로벌 중복 방지 (해시 기반)
    global_processed_hashes = set()

    for foldername, subfolders, filenames in os.walk(folder_path):
        for filename in filenames:
            if not (filename.endswith(".txt") or filename.endswith(".log")): continue

            date_match = RE_DATE.search(filename)
            if date_match:
                file_date = date_match.group(1)
                if not (s_date_str <= file_date <= e_date_str): continue 

            full_path = os.path.join(foldername, filename)
            file_lines = read_log_file(full_path)
            if not file_lines: continue

            keyword_indices = [i for i, line in enumerate(file_lines) if processed_keyword_lower in "".join(line.split()).lower()]
            if not keyword_indices: continue 

           # [수정] 중복 방지를 위한 '시작 줄 번호' 저장소 (Set) - 단일 파일 내 중복 방지
            processed_start_indices = set()

            for keyword_line_index in keyword_indices:
                # 1. 거래 시작 지점(Line) 찾기
                start_idx = 0
                for i in range(keyword_line_index, -1, -1): 
                    if start_step_marker in "".join(file_lines[i].split()).lower(): 
                        start_idx = i
                        break
                
                # 2. 이미 처리된 시작 지점(같은 거래)라면 즉시 건너뜀 (단일 파일 내)
                if start_idx in processed_start_indices:
                    continue
                
                # 3. 거래 종료 지점 찾기
                end_idx = len(file_lines)
                for i in range(keyword_line_index + 1, len(file_lines)):
                    if start_step_marker in "".join(file_lines[i].split()).lower(): 
                        end_idx = i
                        break
                
                target_lines = file_lines[start_idx : end_idx]

                if not any(validator_step in line for line in target_lines): continue 

                # ==========================================================
                # [추가] 강력한 중복 방지 (내용 기반 서명 확인)
                # 추출된 거래 로그 블록 전체를 하나의 문자열로 합친 뒤 해시값 생성
                # 백업 파일 등으로 인해 파일명/경로가 달라도 내용이 같으면 걸러냄
                # ==========================================================
                content_signature = hashlib.md5("".join(target_lines).encode('utf-8')).hexdigest()
                
                if content_signature in global_processed_hashes:
                    continue # 이미 출력된 거래 내용과 동일하므로 스킵
                
                global_processed_hashes.add(content_signature)
                processed_start_indices.add(start_idx) # 파일 내 중복 방지 업데이트
                # ==========================================================
                
                found_any_target = True
                stat_total += 1 

                has_critical_error = False; pre_calc_cash = {} 
                collected_order_rates = []
                credit_payment_amt = 0 
                transfer_deposit_amt = 0 # [추가] 환전할 금액(입금) 저장용
                total_withdraw_krw = 0
                withdraw_foreign_info = []
                
                start_time_str = "Unknown"
                if target_lines:
                    time_match = RE_TIME.search(target_lines[0])
                    if time_match: start_time_str = time_match.group(1)

                last_withdraw_pattern = None

                for line in target_lines:
                    line_clean = "".join(line.split()).lower()
                    
                    # [판정 기준 1] 에러 감지 (반드시 [ERROR]와 [SERVER CONTENTS]가 동시에 있어야 함)
                    if "[error]" in line_clean and "[servercontents]" in line_clean: 
                        has_critical_error = True
                    
                    rate_match = re.search(r"(\[INFO\]\s*ORDER_RATE.*)", line, re.IGNORECASE)
                    if rate_match: collected_order_rates.append(rate_match.group(1))
                    
                    payment_match = RE_PAYMENT_REQ.search(line)
                    if payment_match: credit_payment_amt = int(payment_match.group(1))

                    # [추가] "환전할 금액" 파싱 -> "입금 금액" 변수
                    if category_name == "외화 환전 (계좌 이체)":
                        exchange_match = re.search(r"환전할 금액\s*:\s*(\d+)", line)
                        if exchange_match:
                            transfer_deposit_amt = int(exchange_match.group(1))                    
                    
                    if "SCN8237R" in line and "ACCEPT" in line:
                        match = RE_MONEY.search(line)
                        if match:
                            cnt = 1; cur = match.group(2); val = int(match.group(3))
                            if cur not in pre_calc_cash: pre_calc_cash[cur] = {'total_amt': 0, 'total_cnt': 0, 'breakdown': {}}
                            pre_calc_cash[cur]['total_amt'] += cnt * val
                            pre_calc_cash[cur]['total_cnt'] += cnt
                            if val not in pre_calc_cash[cur]['breakdown']: pre_calc_cash[cur]['breakdown'][val] = 0
                            pre_calc_cash[cur]['breakdown'][val] += cnt
                    
                    if "HSCDU2_1" in line or "HSCDU2_2" in line:
                        try:
                            match = re.search(r"((?:\d+/\d+\s*,\s*)+\d+/\d+)", line)
                            if match:
                                current_pattern = match.group(1)
                                if current_pattern != last_withdraw_pattern:
                                    last_withdraw_pattern = current_pattern 
                                    parts = [p.strip() for p in match.group(1).split(',')]
                                    disp_counts = [int(p.split('/')[1]) for p in parts]
                                    if len(disp_counts) == 3:
                                        total_withdraw_krw += (disp_counts[0]*50000 + disp_counts[1]*10000 + disp_counts[2]*1000)
                                    elif len(disp_counts) == 6:
                                        total_withdraw_krw += (disp_counts[0]*50000 + disp_counts[1]*10000 + disp_counts[3]*1000)
                                        if disp_counts[2] > 0: withdraw_foreign_info.append(f"TWD {disp_counts[2]}장")
                                        if disp_counts[4] > 0: withdraw_foreign_info.append(f"USD {disp_counts[4]}장")
                                        if disp_counts[5] > 0: withdraw_foreign_info.append(f"JPY {disp_counts[5]}장")
                        except: pass

                header_money_parts = []
                if pre_calc_cash:
                    for cur, info in pre_calc_cash.items():
                        breakdown_str_list = []
                        for val, cnt in info['breakdown'].items(): breakdown_str_list.append(f"{val:,}x{cnt}장")
                        breakdown_final = ", ".join(breakdown_str_list)
                        header_money_parts.append(f"입금: {cur} {info['total_amt']:,} ({breakdown_final})")
                
                if credit_payment_amt > 0:
                    header_money_parts.append(f"결제: {credit_payment_amt:,}원")
                
                # [추가] 헤더에 "입금 금액" 추가
                if transfer_deposit_amt > 0:
                    header_money_parts.append(f"입금 금액: {transfer_deposit_amt:,}원")
                
                if total_withdraw_krw > 0 or withdraw_foreign_info:
                    out_str = f"출금: {total_withdraw_krw:,} KRW"
                    if withdraw_foreign_info: out_str += f" + {', '.join(withdraw_foreign_info)}"
                    header_money_parts.append(f"<span class='highlight-out'>{out_str}</span>")

                money_summary_str = " / ".join(header_money_parts) if header_money_parts else "금액 미투입"
                if collected_order_rates:
                    clean_rates = [r.replace("[INFO]", "").strip() for r in collected_order_rates]
                    money_summary_str += f" <span class='headline-rate'>📉 {' / '.join(clean_rates)}</span>"

                # 단계 검사
                full_block = "".join([l.lower().replace(" ", "") for l in target_lines])
                last_successful_step = "시작 전"
                for step in flow_list:
                    step_clean = "".join(step.split()).lower()
                    if step_clean in full_block: last_successful_step = step.replace("[SERVER CONTENTS]", "").strip() 
                
                is_last_step_found = last_step_marker in full_block
                
                safe_cat_id = re.sub(r'[^a-zA-Z0-9]', '', category_name)
                anchor_id = ""
                if category_name not in anchor_map['total']:
                    anchor_id += f" id='cat-total-{safe_cat_id}'"
                    anchor_map['total'].add(category_name)

                # ==========================================
                # [판정 로직 구현]
                # ==========================================
                
                status_badge = ""
                narrative_text = ""
                
                if has_critical_error:
                    # 1. 에러
                    status_badge = "<span class='status-badge bg-error'>ERROR</span>"
                    stat_fail += 1
                    issue_details_list.append(f"[{category_name}] 에러 발생: {last_successful_step} 단계 이후")
                    narrative_text = f"<span class='narrative-text'><span class='highlight-time'>{start_time_str}</span>에 <span class='highlight-cate'>{category_name}</span> 진행 중, <span class='highlight-error'>시스템 에러</span>가 감지되었습니다.<br><span class='highlight-money'>({money_summary_str})</span></span>"
                    if category_name not in anchor_map['fail']:
                        if 'id=' not in anchor_id: anchor_id = f" id='cat-fail-{safe_cat_id}'"
                        anchor_map['fail'].add(category_name)

                elif not is_last_step_found:
                    # 2. 취소 (중단)
                    status_badge = "<span class='status-badge bg-warn'>CANCELED</span>"
                    stat_canceled += 1
                    issue_details_list.append(f"[{category_name}] 취소(중단): {last_successful_step} 단계까지 진행")
                    narrative_text = f"<span class='narrative-text'><span class='highlight-time'>{start_time_str}</span>에 <span class='highlight-cate'>{category_name}</span> 거래가 <span class='highlight-cancel'>취소(중단)</span>되었습니다. (마지막 단계 미도달)<br><span class='highlight-money'>({money_summary_str})</span></span>"
                    if category_name not in anchor_map['canceled']:
                        if 'id=' not in anchor_id: anchor_id = f" id='cat-canc-{safe_cat_id}'"
                        anchor_map['canceled'].add(category_name)

                else:
                    # 3. 정상
                    status_badge = "<span class='status-badge bg-success'>SUCCESS</span>"
                    stat_success += 1
                    success_details_list.append(f"[{category_name}] 정상 완료")
                    narrative_text = f"<span class='narrative-text'><span class='highlight-time'>{start_time_str}</span>에 <span class='highlight-cate'>{category_name}</span> 거래가 <span class='highlight-success'>정상적으로 완료</span>되었습니다.<br><span class='highlight-money'>({money_summary_str})</span></span>"
                    if category_name not in anchor_map['success']:
                        if 'id=' not in anchor_id: anchor_id = f" id='cat-succ-{safe_cat_id}'"
                        anchor_map['success'].add(category_name)

                extra_anchors = ""
                if category_name in anchor_map['total'] and f"cat-total-{safe_cat_id}" not in anchor_id: extra_anchors += f"<span id='cat-total-{safe_cat_id}'></span>"
                if has_critical_error and category_name in anchor_map['fail'] and f"cat-fail-{safe_cat_id}" not in anchor_id: extra_anchors += f"<span id='cat-fail-{safe_cat_id}'></span>"
                if not has_critical_error and is_last_step_found and category_name in anchor_map['success'] and f"cat-succ-{safe_cat_id}" not in anchor_id: extra_anchors += f"<span id='cat-succ-{safe_cat_id}'></span>"
                if not has_critical_error and not is_last_step_found and category_name in anchor_map['canceled'] and f"cat-canc-{safe_cat_id}" not in anchor_id: extra_anchors += f"<span id='cat-canc-{safe_cat_id}'></span>"

                html_parts.append(f"""<div class='trans-card' {anchor_id}>{extra_anchors}<div class='card-header'><div>{narrative_text}</div><div>{status_badge}</div></div><div style='margin-bottom:15px; font-size:0.8em; color:#8B949E;'>📁 {filename}</div>""")

                for step_name in flow_list:
                    clean_step = "".join(step_name.split()).lower()
                    step_found = False; timestamp_str = "" 
                    step_line_idx = -1
                    for idx, line in enumerate(target_lines):
                        if clean_step in "".join(line.split()).lower():
                            step_found = True; step_line_idx = idx
                            time_match = RE_TIME.search(line)
                            if time_match: timestamp_str = time_match.group(1).split()[-1] 
                            break
                    
                    clean_name = step_name.replace("[SERVER CONTENTS]", "").strip()
                    
                    if step_found:
                        html_parts.append(f"""<div class='step-row border-pass'><div class='step-content'><span class='step-name'>✅ {clean_name}</span> <span style='font-family:monospace;'>{timestamp_str}</span></div>""")
                        
                        is_printed = False
                        card_data_buffer = []
                        is_capturing_card = False
                        
                        is_target_toggle_step = ("C_I_CREDIT" in step_name or "C_T_SEL_AMT" in step_name)
                        toggle_step_buffer = []
                        is_scan_pass_step = ("C_SCAN_PASS" in step_name) or ("SCAN_PASSPORT" in step_name)
                        scan_pass_buffer = []

                        for scan_idx in range(step_line_idx + 1, len(target_lines)):
                            current_line = target_lines[scan_idx]
                            if "[SERVER CONTENTS]" in current_line and "[ERROR]" not in current_line.upper(): break
                            
                            line_lower = current_line.lower()
                            line_content = current_line.strip().replace("<", "&lt;").replace(">", "&gt;")

                            final_output_html = ""
                            is_printed = False

                            if "client callback" in line_lower and ("wowiccard" in line_lower or "wowiccard_data" in line_lower):
                                is_capturing_card = True
                            
                            if is_capturing_card:
                                card_data_buffer.append(line_content)
                                if "empty" in line_lower or "result" in line_lower:
                                    is_capturing_card = False
                                    toggle_body = "<br>".join([f"<div class='data-line'>{l}</div>" for l in card_data_buffer])
                                    final_output_html = f"""<details class='card-data-toggle'><summary>📂 CARD DATA PACKET (Click)</summary><div class='toggle-content'>{toggle_body}</div></details>"""
                                    card_data_buffer = [] 
                                    is_printed = True
                                else:
                                    is_printed = True 
                            
                            if is_capturing_card: continue 
                            
                            if is_scan_pass_step:
                                scan_pass_buffer.append(line_content)
                                is_printed = True 
                            
                            if is_target_toggle_step and final_output_html:
                                toggle_step_buffer.append(final_output_html)
                                continue
                            elif is_target_toggle_step: 
                                pass

                            if is_printed and final_output_html:
                                if is_target_toggle_step: toggle_step_buffer.append(final_output_html)
                                else: html_parts.append(final_output_html)
                                continue

                            if not is_printed and "[error]" in line_lower:
                                final_output_html = f"<div class='critical-box'>🚨 {line_content}</div>"
                                is_printed = True
                            
                            if not is_printed and is_target_toggle_step:
                                is_printed = True
                                if "결제 성공" in line_content or "결제성공" in line_content:
                                    final_output_html = f"<div class='log-text'><span class='tag tag-money'>💳 결제 성공</span> {line_content}</div>"
                                else:
                                    final_output_html = f"<div class='log-text'>{line_content}</div>"

                            if not is_printed:
                                if "hscdu2_1" in line_lower or "hscdu2_2" in line_lower:
                                    calc_str = ""
                                    try:
                                        match = re.search(r"((?:\d+/\d+\s*,\s*)+\d+/\d+)", line_content)
                                        if match:
                                            parts = [p.strip() for p in match.group(1).split(',')]
                                            disp_counts = [int(p.split('/')[1]) for p in parts]
                                            krw_total = 0
                                            foreign_info = []
                                            if len(disp_counts) == 3:
                                                krw_total = disp_counts[0]*50000 + disp_counts[1]*10000 + disp_counts[2]*1000
                                            elif len(disp_counts) == 6:
                                                krw_total = disp_counts[0]*50000 + disp_counts[1]*10000 + disp_counts[3]*1000
                                                if disp_counts[2] > 0: foreign_info.append(f"TWD {disp_counts[2]}장")
                                                if disp_counts[4] > 0: foreign_info.append(f"USD {disp_counts[4]}장")
                                                if disp_counts[5] > 0: foreign_info.append(f"JPY {disp_counts[5]}장")
                                            
                                            if krw_total > 0:
                                                calc_str += f" <span style='color:#FFD700; font-weight:bold;'>(Total: {krw_total:,} KRW"
                                                if foreign_info: calc_str += " + " + ", ".join(foreign_info)
                                                calc_str += ")</span>"
                                            elif foreign_info:
                                                calc_str += f" <span style='color:#FFD700; font-weight:bold;'>(Foreign: {', '.join(foreign_info)})</span>"
                                    except: pass
                                    final_output_html = f"<div class='log-text'><span class='tag tag-money' style='background:rgba(255, 193, 7, 0.2); border-color:#FFC107; color:#FFD700;'>📤 출금</span> {line_content}{calc_str}</div>"
                                    is_printed = True
                                
                                elif "scn8237r" in line_lower and "accept" in line_lower:
                                    final_output_html = f"<div class='log-text'><span class='tag tag-money'>💵 입금</span> {line_content}</div>"
                                    is_printed = True
                                elif "passport" in line_lower and "scan" in step_name.lower():
                                    match = RE_PASSPORT.search(current_line)
                                    if match: 
                                        final_output_html = f"<div class='log-text'><span class='tag tag-card'>🛂 여권</span> {match.group(1)}</div>"
                                        is_printed = True
                                elif "결제 시작" in line_lower:
                                    final_output_html = f"<div class='log-text'><span class='tag tag-money'>💳 결제 요청</span> 시작</div>"
                                    is_printed = True

                            if is_printed and final_output_html:
                                if is_target_toggle_step: toggle_step_buffer.append(final_output_html)
                                elif not is_scan_pass_step: html_parts.append(final_output_html)

                        if card_data_buffer:
                            toggle_body = "<br>".join([f"<div class='data-line'>{l}</div>" for l in card_data_buffer])
                            html_str = f"<details class='card-data-toggle'><summary>📂 CARD DATA (Partial)</summary><div class='toggle-content'>{toggle_body}</div></details>"
                            if is_target_toggle_step: toggle_step_buffer.append(html_str)
                            elif not is_scan_pass_step: html_parts.append(html_str)
                        
                        if is_scan_pass_step and scan_pass_buffer:
                            final_buffer = []
                            for l in scan_pass_buffer:
                                if category_name == "외화 환전 (계좌 이체)" and (re.search(r"\{[A-Z]{3}\}.*\d+", l) or "환전" in l):
                                    final_buffer.append(f"<span class='tag tag-card'>💱 환전 정보</span> {l}")
                                else:
                                    final_buffer.append(l)
                            toggle_body = "<br>".join([f"<div class='data-line'>{l}</div>" for l in final_buffer])
                            html_parts.append(f"""<details class='card-data-toggle'><summary>🛂 PASSPORT SCAN DATA (Click)</summary><div class='toggle-content'>{toggle_body}</div></details>""")

                        if is_target_toggle_step and toggle_step_buffer:
                            toggle_body = "".join(toggle_step_buffer)
                            html_parts.append(f"""<details class='card-data-toggle'><summary>📜 FULL LOG ({len(toggle_step_buffer)} lines)</summary><div class='toggle-content'>{toggle_body}</div></details>""")

                        html_parts.append("</div>")

                    else:
                        if "C_SCAN_PASS" in step_name and category_name == "카드 충전 (현금)":
                            continue 
                        html_parts.append(f"""<div class='step-row border-fail'><div class='step-content'><span class='step-name' style='color:#F85149;'>❌ {clean_name}</span> (Missing)</div></div>""")

                html_parts.append("</div>")

    return found_any_target, "".join(html_parts), stat_total, stat_success, stat_canceled, stat_fail, success_details_list, issue_details_list

# ==========================================
# 3. 메인 UI (사이드바)
# ==========================================
if "log_folder_path" not in st.session_state:
    st.session_state.log_folder_path = r"C:\Users\jin33\OneDrive\바탕 화면\My_logs"

with st.sidebar:
    st.markdown("<div class='sidebar-header'><span>SYSTEM_CONTROLLER</span><span>v2.2</span></div>", unsafe_allow_html=True)
    
    st.markdown("<div class='control-label'><span class='label-accent'>01.</span> UPLOAD LOGS</div>", unsafe_allow_html=True)
    uploaded_files = st.file_uploader("Upload", accept_multiple_files=True, type=['txt', 'log'], label_visibility="collapsed")
    
    if uploaded_files:
        temp_dir = os.path.join(tempfile.gettempdir(), "neural_core_logs")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        # Save uploaded files
        for uploaded_file in uploaded_files:
            with open(os.path.join(temp_dir, uploaded_file.name), "wb") as f:
                f.write(uploaded_file.getbuffer())
        
        st.session_state.log_folder_path = temp_dir
    
    st.markdown("<div class='separator-line'></div>", unsafe_allow_html=True)
    
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    
    st.markdown("<div class='control-label'><span class='label-accent'>02.</span> TIME WINDOW</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1: start_date = st.date_input("Start", value=yesterday, label_visibility="collapsed")
    with col2: end_date = st.date_input("End", value=today, label_visibility="collapsed")

    st.markdown("<div class='control-label'><span class='label-accent'>03.</span> PROTOCOL</div>", unsafe_allow_html=True)
    search_mode_ui = st.radio("Mode", ["DEEP_SCAN", "TEXT_FIND"], horizontal=True, label_visibility="collapsed", key="ui_mode_selection")

    search_mode = "단순 텍스트 검색" 
    selected_category = "전체"
    keyword = ""

    if search_mode_ui == "DEEP_SCAN":
        search_mode = "거래 정밀 분석"
        st.markdown("<div class='control-label'><span class='label-accent'>04.</span> TYPE SELECTOR</div>", unsafe_allow_html=True)
        category_list = ["ALL_TYPES"] + list(TRANSACTION_MAP.keys())
        cat_selection = st.selectbox("Category", category_list, label_visibility="collapsed", key="sb_category")
        selected_category = "전체" if cat_selection == "ALL_TYPES" else cat_selection
        st.markdown("<div class='control-label'><span class='label-accent'>05.</span> TARGET KEY</div>", unsafe_allow_html=True)
        keyword = st.text_input("Keyword_Deep", value="", label_visibility="collapsed", placeholder="CARD / PASSPORT NO.", key="input_deep_keyword")
    else:
        search_mode = "단순 텍스트 검색"
        selected_category = "전체"
        st.markdown("<div class='control-label'><span class='label-accent'>04.</span> QUERY STRING</div>", unsafe_allow_html=True)
        keyword = st.text_input("Keyword_Simple", value="", label_visibility="collapsed", placeholder="SEARCH PATTERN...", key="input_simple_keyword")

    st.markdown("<div class='separator-line'></div>", unsafe_allow_html=True)
    search_btn = st.button("EXECUTE_PROTOCOL", type="primary")
    st.markdown("""<div style='margin-top: 15px; font-size: 9px; color: #37474F; text-align: center; font-family: "JetBrains Mono", monospace; opacity: 0.7;'>NEURAL_CORE // ACCESS_GRANTED</div>""", unsafe_allow_html=True)

# ==========================================
# 4. 메인 실행 로직
# ==========================================
if search_btn:
    if not os.path.exists(st.session_state.log_folder_path):
        st.error(f"❌ 폴더를 찾을 수 없습니다: {st.session_state.log_folder_path}")
    elif not keyword.strip():
        st.warning("⚠️ 검색어를 입력해주세요!")
    else:
        show_ai_loading_effect(keyword)
        with st.spinner('GENERATING FINAL REPORT...'):
            found_total = False; final_html = ""
            grand_total = 0; grand_success = 0; grand_canceled = 0; grand_fail = 0
            grand_success_details = []; grand_issue_details = []
            stats_total = defaultdict(int); stats_success = defaultdict(int); stats_canceled = defaultdict(int); stats_fail = defaultdict(int)
            anchor_map = {'total': set(), 'success': set(), 'canceled': set(), 'fail': set()}

            if search_mode == "거래 정밀 분석":
                processed_keyword = "".join(keyword.split()).lower()
                target_configs = TRANSACTION_MAP.items() if selected_category == "전체" else [(selected_category, TRANSACTION_MAP[selected_category])]
                html_list = []
                for category_name, config in target_configs:
                    flow_list, mode, validator = config
                    found, html_res, c_tot, c_suc, c_canc, c_fail, s_list, i_list = analyze_flow_web(
                        st.session_state.log_folder_path, processed_keyword, flow_list, mode, validator, start_date, end_date, category_name, anchor_map
                    )
                    if found:
                        found_total = True; html_list.append(html_res)
                        grand_total += c_tot; grand_success += c_suc; grand_canceled += c_canc; grand_fail += c_fail
                        grand_success_details.extend(s_list); grand_issue_details.extend(i_list)
                        stats_total[category_name] += c_tot
                        if c_suc > 0: stats_success[category_name] += c_suc
                        if c_canc > 0: stats_canceled[category_name] += c_canc
                        if c_fail > 0: stats_fail[category_name] += c_fail
                final_html = "".join(html_list)
            else:
                
                grand_success = grand_total; grand_fail = 0
                if found_total: stats_total["Simple Search"] = grand_total

            if found_total:
                draw_summary_ui(grand_total, grand_success, grand_canceled, grand_fail, grand_success_details, grand_issue_details, stats_total, stats_success, stats_canceled, stats_fail)
                st.markdown(final_html, unsafe_allow_html=True)
            else:
                st.warning(f"😥 NO RECORDS FOUND FOR '{keyword}'")
else:
    draw_landing_page(st.session_state.log_folder_path)


