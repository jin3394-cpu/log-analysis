import streamlit as st
import os
import re
from datetime import datetime, timedelta
import pandas as pd

# ==========================================
# 0. 페이지 설정 및 CSS
# ==========================================
st.set_page_config(page_title="디지털 탐정 Web (Mobile)", page_icon="🕵️‍♂️", layout="wide")

st.markdown("""
<style>
    /* 다크모드 기반 스타일 */
    .stApp { background-color: #1E1E1E; color: #E0E0E0; }
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stRadio div[role="radiogroup"] { background-color: #2D2D2D !important; color: #FFFFFF !important; }
    
    /* 업로더 스타일 */
    .stFileUploader section { background-color: #2D2D2D; border: 1px dashed #FFD700; }
    .stFileUploader section:hover { border: 1px solid #4FC3F7; }
    
    /* 로그 텍스트 스타일 */
    .log-header { color: #FFD700; font-size: 20px; font-weight: bold; margin-top: 30px; border-bottom: 1px solid #444; padding-bottom: 5px; }
    .log-file { color: #4FC3F7; font-weight: bold; font-size: 14px; margin-bottom: 10px; }
    .status-normal { background-color: #00C853; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .status-cancel { background-color: #FF9800; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .status-error  { background-color: #D500F9; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    
    .step-pass { color: #87CEEB; font-weight: bold; font-size: 16px; margin-top: 5px; }
    .step-fail { color: #FF5252; font-weight: bold; font-size: 16px; margin-top: 5px; }
    
    .info-money { color: #FFD700; font-size: 14px; font-weight: bold; }
    .critical { background-color: #FF0099; color: #FFFFFF; font-weight: bold; padding: 4px 8px; border-radius: 4px; }
    .info-detail { color: #E0E0E0; font-size: 14px; font-family: monospace; }
    .money-box { background-color: #3E2723; padding: 15px; border-radius: 5px; margin-top: 20px; border-left: 5px solid #FFD700; }
    .separator { border-top: 1px dashed #444; margin: 20px 0; }
    .highlight { background-color: #FFFF00; color: #000000; font-weight: bold; padding: 0 4px; border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. 플로우 정의 (상수)
# ==========================================
RE_DATE = re.compile(r"(\d{4}-\d{2}-\d{2})")
RE_TIME = re.compile(r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})")
RE_MONEY = re.compile(r"\{(\d+)\}\s*/\s*([A-Z]+)\s*/\s*(\d+)")
RE_PASSPORT = re.compile(r"passport\s*:\s*\{(.*?)\}", re.IGNORECASE)

FLOW_CARD_CASH = ["[SERVER CONTENTS]CARD_INDEX2", "[SERVER CONTENTS]CARD_MAIN", "[SERVER CONTENTS]C_SEL_CURRENCY", "[SERVER CONTENTS]C_SCAN_PASS", "[SERVER CONTENTS]C_I_AGREE", "[SERVER CONTENTS]C_I_INPUT", "[SERVER CONTENTS]C_I_SELCASH", "[SERVER CONTENTS]C_I_SELAMT", "[SERVER CONTENTS]C_I_OUTKRW", "[SERVER CONTENTS]C_I_ACTIVATE", "[SERVER CONTENTS]C_RECEIPT", "[SERVER CONTENTS]C_I_COMPLETE"]
FLOW_CARD_CREDIT = ["[SERVER CONTENTS]CARD_INDEX2", "[SERVER CONTENTS]CARD_MAIN", "[SERVER CONTENTS]C_I_SELVOUCHER", "[SERVER CONTENTS]C_SEL_PAYMENT", "[SERVER CONTENTS]C_SCAN_PASS", "[SERVER CONTENTS]C_I_AGREE", "[SERVER CONTENTS]C_I_CREDIT", "[SERVER CONTENTS]C_I_PAYMENT", "[SERVER CONTENTS]C_I_ACTIVATE", "[SERVER CONTENTS]C_RECEIPT", "[SERVER CONTENTS]C_I_COMPLETE", "[SERVER CONTENTS]NOTIFICATION"]
FLOW_CARD_REISSUE = ["[SERVER CONTENTS]CARD_INDEX2", "[SERVER CONTENTS]CARD_MAIN", "[SERVER CONTENTS]C_R_AGREE", "[SERVER CONTENTS]C_SCAN_PASS", "[SERVER CONTENTS]C_VERIFY_PIN", "[SERVER CONTENTS]C_R_ACTIVATE", "[SERVER CONTENTS]C_RECEIPT", "[SERVER CONTENTS]C_R_COMPLETE", "[SERVER CONTENTS]NOTIFICATION"]
FLOW_CHARGE_CASH = ["[SERVER CONTENTS]CARD_INDEX2", "[SERVER CONTENTS]CARD_MAIN", "[SERVER CONTENTS]C_T_TARGET", "[SERVER CONTENTS]C_SEL_PAYMENT", "[SERVER CONTENTS]C_INSERT_CARD", "[SERVER CONTENTS]C_SEL_CURRENCY", "[SERVER CONTENTS]C_T_INPUT", "[SERVER CONTENTS]C_T_TRANSACTION", "[SERVER CONTENTS]C_T_RECEIPT", "[SERVER CONTENTS]C_T_COMPLETE"]
FLOW_CHARGE_CREDIT = ["[SERVER CONTENTS]CARD_INDEX2", "[SERVER CONTENTS]CARD_MAIN", "[SERVER CONTENTS]C_T_TARGET", "[SERVER CONTENTS]C_SEL_PAYMENT", "[SERVER CONTENTS]C_INSERT_CARD", "[SERVER CONTENTS]C_T_SEL_AMT", "[SERVER CONTENTS]C_T_PAYMENT", "[SERVER CONTENTS]C_T_RECEIPT", "[SERVER CONTENTS]C_T_COMPLETE"]
FLOW_EXCHANGE_KRW = ["[SERVER CONTENTS]CARD_INDEX2", "[SERVER CONTENTS]MAIN", "[SERVER CONTENTS]SCAN_BY_PASSPORT", "[SERVER CONTENTS]INPUT_CURRENCY", "[SERVER CONTENTS]RECEIPT_OUTPUT", "[SERVER CONTENTS]OUTPUT_KRW", "[SERVER CONTENTS]OUTPUT_THERMAL", "[SERVER CONTENTS]NOTIFICATION"]
FLOW_EXCHANGE_FOREIGN = ["[SERVER CONTENTS]CARD_INDEX2", "[SERVER CONTENTS]MAIN2", "[SERVER CONTENTS]CALCULATOR_CURRENCY", "[SERVER CONTENTS]SCAN_PASSPORT", "[SERVER CONTENTS]SELECT_SALE_GB", "[SERVER CONTENTS]INPUT_KRW", "[SERVER CONTENTS]OUTPUT_CURRENCY", "[SERVER CONTENTS]OUTPUT_THERMAL_CURRENCY"]
FLOW_CARD_WITHDRAWAL = ["[SERVER CONTENTS]CARD_INDEX2", "[SERVER CONTENTS]CARD_MAIN", "[SERVER CONTENTS]C_INSERT_CARD", "[SERVER CONTENTS]C_VERIFY_PIN", "[SERVER CONTENTS]C_W_SELECT_AMT", "[SERVER CONTENTS]C_W_OUTKRW", "[SERVER CONTENTS]C_W_COMPLETE"]
FLOW_EXCHANGE_FOREIGN_CREDIT = ["[SERVER CONTENTS]CARD_INDEX2", "[SERVER CONTENTS]CALCULATOR_CURRENCY", "[SERVER CONTENTS]SCAN_PASSPORT", "[SERVER CONTENTS]SELECT_SALE_GB", "[SERVER CONTENTS]SALE_ACC_PHONE", "[SERVER CONTENTS]SALE_ACC_CHECK", "[SERVER CONTENTS]SALE_ACC_OUTPUT_CURRENCY", "[SERVER CONTENTS]OUTPUT_THERMAL_CURRENCY", "[SERVER CONTENTS]NOTIFICATION"]

TRANSACTION_MAP = {
    "카드 발급 (현금)": (FLOW_CARD_CASH, "CASH", "C_I_INPUT"),
    "카드 발급 (신용카드)": (FLOW_CARD_CREDIT, "CREDIT", "C_I_CREDIT"),
    "카드 재발급": (FLOW_CARD_REISSUE, "REISSUE", "C_R_ACTIVATE"),
    "카드 충전 (현금)": (FLOW_CHARGE_CASH, "CASH", "C_T_INPUT"),
    "카드 충전 (신용카드)": (FLOW_CHARGE_CREDIT, "CREDIT", "C_T_SEL_AMT"),
    "원화 환전": (FLOW_EXCHANGE_KRW, "EXCHANGE", "INPUT_CURRENCY"),
    "외화 환전 (현금)": (FLOW_EXCHANGE_FOREIGN, "EXCHANGE_FOREIGN", "INPUT_KRW"),
    "외화 환전 (신용카드)": (FLOW_EXCHANGE_FOREIGN_CREDIT, "CREDIT", "SALE_ACC_CHECK"),
    "카드 출금": (FLOW_CARD_WITHDRAWAL, "WITHDRAWAL", "C_W_SELECT_AMT"),
}

# --- 2. 분석 로직 ---

def get_file_content(uploaded_file):
    """업로드된 파일을 메모리에서 읽기"""
    bytes_data = uploaded_file.getvalue()
    try: return bytes_data.decode('cp949').splitlines()
    except:
        try: return bytes_data.decode('utf-8').splitlines()
        except: return []

def search_simple_text_upload(files, keyword, start_date, end_date):
    """단순 텍스트 검색 (띄어쓰기 무시)"""
    html_parts = []
    excel_data_list = []
    found_any = False
    
    s_date_str = start_date.strftime("%Y-%m-%d")
    e_date_str = end_date.strftime("%Y-%m-%d")
    keyword_no_space = "".join(keyword.split()).lower()
    
    for uploaded_file in files:
        filename = uploaded_file.name
        
        # 날짜 필터
        date_match = RE_DATE.search(filename)
        if date_match:
            file_date = date_match.group(1)
            if not (s_date_str <= file_date <= e_date_str): continue
        
        file_lines = get_file_content(uploaded_file)
        if not file_lines: continue
        
        found_lines_in_file = []
        for idx, line in enumerate(file_lines):
            # 내용 비교 (공백 제거 후)
            if keyword_no_space in "".join(line.split()).lower():
                display_line = line.strip().replace("<", "&lt;").replace(">", "&gt;") 
                # 하이라이트
                highlighted_line = re.sub(f"({re.escape(keyword)})", r"<span class='highlight'>\1</span>", display_line, flags=re.IGNORECASE)
                found_lines_in_file.append((idx + 1, highlighted_line, line.strip()))
        
        if found_lines_in_file:
            found_any = True
            html_parts.append("<div class='separator'></div>")
            html_parts.append(f"<div class='log-file'>📁 파일: {filename} (총 {len(found_lines_in_file)}건 발견)</div>")
            for line_num, html_line, raw_line in found_lines_in_file:
                html_parts.append(f"<div class='info-detail' style='margin-left:20px;'>Line {line_num}: {html_line}</div>")
                excel_data_list.append({"날짜": date_match.group(1) if date_match else "Unknown", "파일명": filename, "라인": line_num, "내용": raw_line})

    return found_any, "".join(html_parts), excel_data_list

def analyze_flow_web_upload(files, target_keyword, flow_list, mode, validator_step, start_date, end_date, category_name):
    """정밀 흐름 분석"""
    html_parts = []
    found_any_target = False 
    excel_data_list = [] 
    
    if not flow_list: return False, "", [] 

    start_step_marker = "".join(flow_list[0].split()).lower()
    last_step_marker = "".join(flow_list[-1].split()).lower()
    s_date_str = start_date.strftime("%Y-%m-%d")
    e_date_str = end_date.strftime("%Y-%m-%d")
    processed_keyword_lower = target_keyword

    for uploaded_file in files:
        filename = uploaded_file.name

        date_match = RE_DATE.search(filename)
        if date_match:
            file_date = date_match.group(1)
            if not (s_date_str <= file_date <= e_date_str): continue 

        file_lines = get_file_content(uploaded_file)
        if not file_lines: continue

        keyword_indices = [i for i, line in enumerate(file_lines) if processed_keyword_lower in "".join(line.split()).lower()]
        if not keyword_indices: continue 

        processed_ranges = [] 
        transaction_count = 0

        for keyword_line_index in keyword_indices:
            start_idx = 0
            for i in range(keyword_line_index, -1, -1): 
                if start_step_marker in "".join(file_lines[i].split()).lower():
                    start_idx = i; break
            end_idx = len(file_lines)
            for i in range(keyword_line_index + 1, len(file_lines)):
                if start_step_marker in "".join(file_lines[i].split()).lower(): 
                    end_idx = i; break
            
            is_duplicate = False
            for r_start, r_end in processed_ranges:
                if r_start == start_idx and r_end == end_idx:
                    is_duplicate = True; break
            if is_duplicate: continue

            processed_ranges.append((start_idx, end_idx))
            target_lines = file_lines[start_idx : end_idx]

            if not any(validator_step in line for line in target_lines): continue 
            
            found_any_target = True
            transaction_count += 1
            has_critical_error = False; missing_steps = False; pre_calc_cash = {} 
            
            for line in target_lines:
                line_clean = "".join(line.split()).lower()
                if "[error]" in line_clean:
                    if "networkerror" in line_clean or "servercontents" in line_clean: has_critical_error = True
                if "SCN8237R" in line and "ACCEPT" in line:
                    match = RE_MONEY.search(line)
                    if match:
                        cnt = 1; cur = match.group(2); val = int(match.group(3))
                        if cur not in pre_calc_cash: pre_calc_cash[cur] = {'total_amt': 0, 'total_cnt': 0, 'breakdown': {}}
                        pre_calc_cash[cur]['total_amt'] += cnt * val
                        pre_calc_cash[cur]['total_cnt'] += cnt
                        if val not in pre_calc_cash[cur]['breakdown']: pre_calc_cash[cur]['breakdown'][val] = 0
                        pre_calc_cash[cur]['breakdown'][val] += cnt
            
            is_last_step_found = False
            if not has_critical_error:
                full_block = "".join([l.lower().replace(" ", "") for l in target_lines])
                for step in flow_list:
                    if "".join(step.split()).lower() not in full_block: missing_steps = True
                if last_step_marker in full_block:
                    is_last_step_found = True
            
            if has_critical_error: status_html = "<span class='status-error'>🚨 에러</span>"
            elif is_last_step_found: status_html = "<span class='status-normal'>✅ 정상</span>"
            elif missing_steps: status_html = "<span class='status-cancel'>⚠️ 취소</span>"
            else: status_html = "<span class='status-normal'>✅ 정상</span>"

            html_parts.append("<div class='separator'></div>")
            html_parts.append(f"<div class='log-header'>🔎 분석 대상: {category_name} (No.{transaction_count}) &nbsp;&nbsp; {status_html}</div>")
            html_parts.append(f"<div class='log-file'>📁 파일: {filename}</div>")

            for step_name in flow_list:
                clean_step = "".join(step_name.split()).lower()
                step_found = False; timestamp_str = "" 
                step_line_idx = -1
                for idx, line in enumerate(target_lines):
                    if clean_step in "".join(line.split()).lower():
                        step_found = True; step_line_idx = idx
                        time_match = RE_TIME.search(line)
                        if time_match: timestamp_str = f"[{time_match.group(1)}] "
                        break
                
                clean_name = step_name.replace("[SERVER CONTENTS]", "").strip()
                if step_found:
                    html_parts.append(f"<div class='step-pass'>&nbsp;&nbsp;✅ {timestamp_str}{clean_name}</div>")
                    excel_data_list.append({"날짜": timestamp_str.strip("[] "), "거래유형": category_name, "거래상태": status_html, "파일명": filename, "단계": clean_name, "결과": "성공", "내용": ""})
                    
                    found_input = False; found_credit = False; capturing_data = False; capturing_payment = False 
                    for scan_idx in range(step_line_idx + 1, len(target_lines)):
                        current_line = target_lines[scan_idx]
                        if "[SERVER CONTENTS]" in current_line and "[ERROR]" not in current_line.upper(): break
                        line_clean = "".join(current_line.split()).lower(); line_content = current_line.strip()

                        if "[error]" in line_clean:
                            if "networkerror" in line_clean: html_parts.append(f"<div class='critical'>&nbsp;&nbsp;&nbsp;&nbsp;🚨 [치명적] {line_content}</div>")
                            elif "servercontents" in line_clean: html_parts.append(f"<div class='critical'>&nbsp;&nbsp;&nbsp;&nbsp;💥 [서버] {line_content}</div>")
                            else: html_parts.append(f"<div class='critical'>&nbsp;&nbsp;&nbsp;&nbsp;💀 {line_content}</div>")
                        
                        if "HSCDU2_1" in current_line or "HSCDU2_2" in current_line: html_parts.append(f"<div class='info-money'>&nbsp;&nbsp;&nbsp;&nbsp;💸 {line_content}</div>")
                        if "SCAN" in step_name and "passport:" in line_clean:
                            match = RE_PASSPORT.search(current_line)
                            if match: html_parts.append(f"<div class='info-detail'>&nbsp;&nbsp;&nbsp;&nbsp;🛂 [여권] {match.group(1).strip()}</div>")
                        if "PAYMENT" in step_name or "SALE_ACC" in step_name:
                            if "결제 시작" in current_line or "결제시작" in current_line: capturing_payment = True; html_parts.append(f"<div class='info-money'>&nbsp;&nbsp;&nbsp;&nbsp;💳 [결제 시작]</div>"); html_parts.append(f"<div class='info-detail'>&nbsp;&nbsp;&nbsp;&nbsp;{line_content}</div>"); continue
                            if capturing_payment:
                                html_parts.append(f"<div class='info-detail'>&nbsp;&nbsp;&nbsp;&nbsp;{line_content}</div>")
                                if "결제 성공" in current_line or "결제성공" in current_line: capturing_payment = False; html_parts.append(f"<div class='step-pass'>&nbsp;&nbsp;&nbsp;&nbsp;✅ [결제 완료]</div>")
                        if (mode in ["CASH", "CHARGE", "EXCHANGE", "EXCHANGE_FOREIGN"]) and ("INPUT" in step_name or "CURRENCY" in step_name):
                            if "SCN8237R" in current_line:
                                if "ACCEPT" in current_line: html_parts.append(f"<div class='info-money'>&nbsp;&nbsp;&nbsp;&nbsp;💵 {line_content}</div>"); found_input = True
                                elif "REJECT" in current_line: html_parts.append(f"<div class='info-alert'>&nbsp;&nbsp;&nbsp;&nbsp;🚨 {line_content}</div>"); found_input = True
                        if (mode in ["CREDIT", "CHARGE"]) and "C_I_CREDIT" in step_name:
                            if "{SUC: '00'" in current_line: html_parts.append(f"<div class='info-money'>&nbsp;&nbsp;&nbsp;&nbsp;💳 {line_content}</div>"); found_credit = True
                            if "{SUC: '01'" in current_line: html_parts.append(f"<div class='info-alert'>&nbsp;&nbsp;&nbsp;&nbsp;🚨 {line_content} (승인 실패)</div>"); found_credit = True
                            if "결제 성공" in current_line: html_parts.append(f"<div class='step-pass'>&nbsp;&nbsp;&nbsp;&nbsp;✅ {line_content}</div>"); found_credit = True
                        if "ACTIVATE" in step_name or "C_INSERT_CARD" in step_name:
                            if "client callback :: TDR210S / WOWICCARD_DATA" in current_line: capturing_data = True; html_parts.append(f"<div class='info-detail'>&nbsp;&nbsp;&nbsp;&nbsp;📂 [카드 데이터]</div>"); continue
                            if capturing_data:
                                html_parts.append(f"<div class='info-detail'>&nbsp;&nbsp;&nbsp;&nbsp;{line_content}</div>")
                                if "empty" in current_line: capturing_data = False

                    if (mode in ["CASH", "CHARGE", "EXCHANGE"]) and ("INPUT" in step_name) and not found_input: html_parts.append(f"<div class='info-detail'>&nbsp;&nbsp;&nbsp;&nbsp;(⚠️ 투입 로그 없음)</div>")
                    if (mode in ["CREDIT", "CHARGE"]) and "C_I_CREDIT" in step_name and not found_credit: html_parts.append(f"<div class='info-detail'>&nbsp;&nbsp;&nbsp;&nbsp;(⚠️ 결제 상세 로그 없음)</div>")
                else:
                    html_parts.append(f"<div class='step-fail'> ❌ {clean_name} (누락됨)</div>")
                    excel_data_list.append({"날짜": "", "거래유형": category_name, "거래상태": status_html, "파일명": filename, "단계": clean_name, "결과": "누락", "내용": "단계 없음"})

            if pre_calc_cash:
                html_parts.append("<div class='money-box'><div class='info-money'>💰 [투입 금액 상세 요약]</div>")
                for curr, info in pre_calc_cash.items():
                    html_parts.append(f"<div style='color:#FFD700; font-weight:bold; margin-top:5px; font-size:15px;'>&nbsp;&nbsp;🪙 {curr}: Total {info['total_amt']:,} (총 {info['total_cnt']}장)</div>")
                    for den in sorted(info['breakdown'].keys(), reverse=True):
                        den_cnt = info['breakdown'][den]
                        html_parts.append(f"<div style='color:#E0E0E0; font-size:13px; font-family:monospace;'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- {den:,} x {den_cnt}장 (= {den*den_cnt:,})</div>")
                html_parts.append("</div>")
            
            html_parts.append("<div class='separator'></div>")

    return found_any_target, "".join(html_parts), excel_data_list

# ==========================================
# 3. 메인 UI
# ==========================================
st.title("🕵️‍♂️ 디지털 탐정 Web (Upload Ver.)")
st.markdown("---")

with st.sidebar:
    st.header("📂 파일 업로드")
    
    # 드래그 앤 드롭 업로더
    uploaded_files = st.file_uploader(
    "분석할 로그 파일을 드래그하거나 선택하세요", 
    accept_multiple_files=True
    # type 옵션 삭제됨 -> 모든 파일 업로드 가능
)
    
    st.markdown("---")
    
    today = datetime.now(); yesterday = today - timedelta(days=1)
    start_date = st.date_input("시작 날짜", value=yesterday)
    end_date = st.date_input("종료 날짜", value=today)

    search_mode = st.radio("검색 모드", ["거래 정밀 분석", "단순 텍스트 검색"])
    
    selected_category = "전체"
    if search_mode == "거래 정밀 분석":
        category_list = ["전체"] + list(TRANSACTION_MAP.keys())
        selected_category = st.selectbox("거래 유형", category_list)
    
    keyword_label = "고객 정보 (카드/여권번호)" if search_mode == "거래 정밀 분석" else "검색할 단어 (Text)"
    keyword = st.text_input(keyword_label, value="")
    
    search_btn = st.button("🔍 분석 시작", type="primary")

if search_btn:
    if not uploaded_files:
        st.error("❌ 분석할 파일을 먼저 업로드해주세요!")
    elif not keyword.strip():
        st.warning("⚠️ 검색어를 입력해주세요!")
    else:
        with st.spinner('업로드된 파일을 분석 중입니다...'):
            found_total = False
            final_html = ""
            final_excel = []

            if search_mode == "거래 정밀 분석":
                processed_keyword = "".join(keyword.split()).lower()
                if selected_category == "전체": target_configs = TRANSACTION_MAP.items()
                else: target_configs = [(selected_category, TRANSACTION_MAP[selected_category])]

                html_list = []
                for category_name, config in target_configs:
                    flow_list, mode, validator = config
                    found, html_res, excel_list = analyze_flow_web_upload(
                        uploaded_files, processed_keyword, flow_list, mode, validator, start_date, end_date, category_name
                    )
                    if found:
                        found_total = True
                        html_list.append(html_res)
                        final_excel.extend(excel_list)
                final_html = "".join(html_list)

            else:
                found_total, final_html, final_excel = search_simple_text_upload(
                    uploaded_files, keyword, start_date, end_date
                )

            if found_total:
                st.markdown(final_html, unsafe_allow_html=True)
                if final_excel:
                    df = pd.DataFrame(final_excel)
                    csv = df.to_csv(index=False).encode('utf-8-sig')
                    st.download_button(label="💾 결과 엑셀(CSV) 다운로드", data=csv, file_name='search_result.csv', mime='text/csv')
            else:
                st.warning(f"😥 업로드된 파일에서 '{keyword}' 관련 내용을 찾지 못했습니다.")

