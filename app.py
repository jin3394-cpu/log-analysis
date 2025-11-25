import streamlit as st
import os
import re
from datetime import datetime, timedelta
import pandas as pd

# ==========================================
# 0. 페이지 설정 및 CSS (사이버네틱 프로)
# ==========================================
st.set_page_config(page_title="디지털 탐정 Web", page_icon="🕵️‍♂️", layout="wide")

st.markdown("""
<style>
    /* 전체 배경 */
    .stApp { background-color: #1E1E1E; color: #E0E0E0; }
    
    /* 입력칸 스타일 */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #2D2D2D !important;
        color: #FFFFFF !important;
    }
    
    /* 제목 */
    .log-header { 
        color: #FFD700; font-size: 20px; font-weight: bold; 
        margin-top: 30px; border-bottom: 1px solid #444; padding-bottom: 5px; 
    }
    
    /* 파일명 */
    .log-file { color: #4FC3F7; font-weight: bold; font-size: 14px; margin-bottom: 10px; }
    
    /* 상태 뱃지 */
    .status-normal { background-color: #00C853; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; vertical-align: middle; }
    .status-cancel { background-color: #FF9800; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; vertical-align: middle; }
    .status-error  { background-color: #D500F9; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; vertical-align: middle; }

    /* 단계 표시 */
    .step-pass { color: #87CEEB; font-weight: bold; font-size: 16px; margin-top: 5px; }
    .step-fail { color: #FF5252; font-weight: bold; font-size: 16px; margin-top: 5px; }
    
    /* 정보/돈 */
    .info-money { color: #FFD700; font-size: 14px; font-weight: bold; }
    
    /* 치명적 에러 (핫핑크 배경) */
    .critical { 
        background-color: #FF0099; color: #FFFFFF; font-weight: bold; 
        padding: 4px 8px; border-radius: 4px; margin: 2px 0; 
        display: block; width: fit-content;
    }

    /* 상세 로그 */
    .info-detail { color: #E0E0E0; font-size: 14px; font-family: monospace; }

    /* 돈 요약 박스 */
    .money-box {
        background-color: #3E2723; padding: 10px; border-radius: 5px; 
        margin-top: 20px; border-left: 5px solid #FFD700;
    }
    
    /* 구분선 */
    .separator { border-top: 1px dashed #444; margin: 20px 0; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. 플로우 정의
# ==========================================
FLOW_CARD_CASH = ["[SERVER CONTENTS]CARD_INDEX2", "[SERVER CONTENTS]CARD_MAIN", "[SERVER CONTENTS]C_SEL_CURRENCY", "[SERVER CONTENTS]C_SCAN_PASS", "[SERVER CONTENTS]C_I_AGREE", "[SERVER CONTENTS]C_I_INPUT", "[SERVER CONTENTS]C_I_SELCASH", "[SERVER CONTENTS]C_I_SELAMT", "[SERVER CONTENTS]C_I_OUTKRW", "[SERVER CONTENTS]C_I_ACTIVATE", "[SERVER CONTENTS]C_RECEIPT", "[SERVER CONTENTS]C_I_COMPLETE"]
FLOW_CARD_CREDIT = ["[SERVER CONTENTS]CARD_INDEX2", "[SERVER CONTENTS]CARD_MAIN", "[SERVER CONTENTS]C_I_SELVOUCHER", "[SERVER CONTENTS]C_SEL_PAYMENT", "[SERVER CONTENTS]C_SCAN_PASS", "[SERVER CONTENTS]C_I_AGREE", "[SERVER CONTENTS]C_I_CREDIT", "[SERVER CONTENTS]C_I_PAYMENT", "[SERVER CONTENTS]C_I_ACTIVATE", "[SERVER CONTENTS]C_RECEIPT", "[SERVER CONTENTS]C_I_COMPLETE", "[SERVER CONTENTS]NOTIFICATION"]
FLOW_CARD_REISSUE = ["[SERVER CONTENTS]CARD_INDEX2", "[SERVER CONTENTS]CARD_MAIN", "[SERVER CONTENTS]C_R_AGREE", "[SERVER CONTENTS]C_SCAN_PASS", "[SERVER CONTENTS]C_VERIFY_PIN", "[SERVER CONTENTS]C_R_ACTIVATE", "[SERVER CONTENTS]C_RECEIPT", "[SERVER CONTENTS]C_R_COMPLETE", "[SERVER CONTENTS]NOTIFICATION"]
FLOW_CHARGE_CASH = ["[SERVER CONTENTS]CARD_INDEX2", "[SERVER CONTENTS]CARD_MAIN", "[SERVER CONTENTS]C_T_TARGET", "[SERVER CONTENTS]C_SEL_PAYMENT", "[SERVER CONTENTS]C_INSERT_CARD", "[SERVER CONTENTS]C_SEL_CURRENCY", "[SERVER CONTENTS]C_T_INPUT", "[SERVER CONTENTS]C_T_TRANSACTION", "[SERVER CONTENTS]C_T_RECEIPT", "[SERVER CONTENTS]C_T_COMPLETE"]
FLOW_CHARGE_CREDIT = ["[SERVER CONTENTS]CARD_INDEX2", "[SERVER CONTENTS]CARD_MAIN", "[SERVER CONTENTS]C_T_TARGET", "[SERVER CONTENTS]C_SEL_PAYMENT", "[SERVER CONTENTS]C_INSERT_CARD", "[SERVER CONTENTS]C_T_SEL_AMT", "[SERVER CONTENTS]C_T_PAYMENT", "[SERVER CONTENTS]C_T_RECEIPT", "[SERVER CONTENTS]C_T_COMPLETE"]
FLOW_EXCHANGE_KRW = ["[SERVER CONTENTS]CARD_INDEX2", "[SERVER CONTENTS]MAIN", "[SERVER CONTENTS]SCAN_BY_PASSPORT", "[SERVER CONTENTS]INPUT_CURRENCY", "[SERVER CONTENTS]RECEIPT_OUTPUT", "[SERVER CONTENTS]OUTPUT_KRW", "[SERVER CONTENTS]OUTPUT_THERMAL", "[SERVER CONTENTS]NOTIFICATION"]
FLOW_EXCHANGE_FOREIGN = ["[SERVER CONTENTS]CARD_INDEX2", "[SERVER CONTENTS]MAIN2", "[SERVER CONTENTS]CALCULATOR_CURRENCY", "[SERVER CONTENTS]SCAN_PASSPORT", "[SERVER CONTENTS]SELECT_SALE_GB", "[SERVER CONTENTS]INPUT_KRW", "[SERVER CONTENTS]OUTPUT_CURRENCY", "[SERVER CONTENTS]OUTPUT_THERMAL_CURRENCY"]
FLOW_CARD_WITHDRAWAL = ["[SERVER CONTENTS]CARD_INDEX2", "[SERVER CONTENTS]CARD_MAIN", "[SERVER CONTENTS]C_INSERT_CARD", "[SERVER CONTENTS]C_VERIFY_PIN", "[SERVER CONTENTS]C_W_SELECT_AMT", "[SERVER CONTENTS]C_W_OUTKRW", "[SERVER CONTENTS]C_W_COMPLETE"]
FLOW_EXCHANGE_FOREIGN_CREDIT = ["[SERVER CONTENTS]CARD_INDEX2", "[SERVER CONTENTS]CALCULATOR_CURRENCY", "[SERVER CONTENTS]SCAN_PASSPORT", "[SERVER CONTENTS]SELECT_SALE_GB", "[SERVER CONTENTS]SALE_ACC_PHONE", "[SERVER CONTENTS]SALE_ACC_CHECK", "[SERVER CONTENTS]SALE_ACC_OUTPUT_CURRENCY", "[SERVER CONTENTS]OUTPUT_THERMAL_CURRENCY", "[SERVER CONTENTS]NOTIFICATION"]

# (자동 감지 지도)
# (⭐수정됨: 카드 재발급 검증 키 변경⭐)
TRANSACTION_MAP = {
    "카드 발급 (현금)": (FLOW_CARD_CASH, "CASH", "C_I_INPUT"),
    "카드 발급 (신용카드)": (FLOW_CARD_CREDIT, "CREDIT", "C_I_CREDIT"),
    "카드 재발급": (FLOW_CARD_REISSUE, "REISSUE", "C_R_ACTIVATE"), # (변경: C_R_AGREE -> C_R_ACTIVATE)
    "카드 충전 (현금)": (FLOW_CHARGE_CASH, "CASH", "C_T_INPUT"), 
    "카드 충전 (신용카드)": (FLOW_CHARGE_CREDIT, "CREDIT", "C_T_SEL_AMT"),
    "원화 환전": (FLOW_EXCHANGE_KRW, "EXCHANGE", "INPUT_CURRENCY"),
    "외화 환전 (현금)": (FLOW_EXCHANGE_FOREIGN, "EXCHANGE_FOREIGN", "INPUT_KRW"),
    "외화 환전 (신용카드)": (FLOW_EXCHANGE_FOREIGN_CREDIT, "CREDIT", "SALE_ACC_CHECK"),
    "카드 출금": (FLOW_CARD_WITHDRAWAL, "WITHDRAWAL", "C_W_SELECT_AMT"),
}

TYPE_DEFINITIONS = TRANSACTION_MAP 

# --- 2. 분석 로직 ---
def read_log_file(path):
    """파일 읽기"""
    try:
        with open(path, 'r', encoding='cp949') as f: return f.readlines()
    except:
        try:
            with open(path, 'r', encoding='utf-8') as f: return f.readlines()
        except: return []

def analyze_flow_web(folder_path, target_keyword, flow_list, mode, validator_step, start_date, end_date, category_name):
    """로컬 폴더를 탐색하여 분석"""
    output_html = ""
    found_any_target = False 
    excel_data_list = [] 
    
    if not flow_list: return False, "", [] 

    start_step_marker = "".join(flow_list[0].split()).lower()
    validator_step_clean = "".join(validator_step.split()).lower()
    
    s_date_str = start_date.strftime("%Y-%m-%d")
    e_date_str = end_date.strftime("%Y-%m-%d")

    # (⭐로컬 폴더 탐색: os.walk 사용⭐)
    for foldername, subfolders, filenames in os.walk(folder_path):
        for filename in filenames:
            if filename.endswith(".txt") or filename.endswith(".log"):
                
                # 날짜 필터링
                date_match = re.search(r"(\d{4}-\d{2}-\d{2})", filename)
                if date_match:
                    file_date = date_match.group(1)
                    if not (s_date_str <= file_date <= e_date_str):
                        continue 

                full_path = os.path.join(foldername, filename)
                file_lines = read_log_file(full_path)
                if not file_lines: continue

                keyword_indices = []
                for idx, line in enumerate(file_lines):
                    if target_keyword in "".join(line.split()).lower():
                        keyword_indices.append(idx)
                
                if not keyword_indices: continue 

                processed_ranges = [] 
                transaction_count = 0

                for keyword_line_index in keyword_indices:
                    # 시작점 찾기
                    start_idx = 0
                    for i in range(keyword_line_index, -1, -1): 
                        clean_line = "".join(file_lines[i].split()).lower()
                        if start_step_marker in clean_line:
                            start_idx = i; break
                    
                    # 끝점 찾기
                    end_idx = len(file_lines)
                    for i in range(keyword_line_index + 1, len(file_lines)):
                        clean_line = "".join(file_lines[i].split()).lower()
                        if start_step_marker in clean_line: 
                            end_idx = i; break
                    
                    # 중복 방지
                    is_duplicate = False
                    for r_start, r_end in processed_ranges:
                        if r_start == start_idx and r_end == end_idx:
                            is_duplicate = True; break
                    if is_duplicate: continue

                    processed_ranges.append((start_idx, end_idx))
                    target_lines = file_lines[start_idx : end_idx]

                    # 엄격 검증
                    is_valid_transaction = False
                    for line in target_lines:
                        if validator_step in line: 
                            is_valid_transaction = True; break
                    if not is_valid_transaction: continue 
                    
                    # === 분석 시작 ===
                    found_any_target = True
                    transaction_count += 1
                    
                    has_critical_error = False
                    missing_steps = False
                    pre_calc_cash = {} 
                    
                    for line in target_lines:
                        line_clean = "".join(line.split()).lower()
                        if "[error]" in line_clean:
                            if "[error][3]networkerror" in line_clean or "[error][servercontents]" in line_clean:
                                has_critical_error = True
                        
                        # 돈 계산
                        if "client callback" in line and "SCN8237R" in line and "ACCEPT" in line:
                            match = re.search(r"\{(\d+)\}\s*/\s*([A-Z]+)\s*/\s*(\d+)", line)
                            if match:
                                cnt = 1; cur = match.group(2); val = int(match.group(3))
                                tot_amt = cnt * val
                                if cur not in pre_calc_cash: pre_calc_cash[cur] = {'amount': 0, 'count': 0}
                                pre_calc_cash[cur]['amount'] += tot_amt
                                pre_calc_cash[cur]['count'] += cnt
                    
                    if not has_critical_error:
                        full_block = "".join([l.lower().replace(" ", "") for l in target_lines])
                        for step in flow_list:
                            clean = "".join(step.split()).lower()
                            if clean not in full_block:
                                missing_steps = True; break
                    
                    if has_critical_error: status_html = "<span class='status-error'>🚨 에러</span>"
                    elif missing_steps: status_html = "<span class='status-cancel'>⚠️ 취소</span>"
                    else: status_html = "<span class='status-normal'>✅ 정상</span>"

                    if not any("SCN8237R" in line and "ACCEPT" in line for line in target_lines):
                         pre_calc_cash = {}

                    parent_folder = os.path.basename(foldername)
                    output_html += "<div class='separator'></div>"
                    output_html += f"<div class='log-header'>🔎 분석 대상: {category_name} (No.{transaction_count}) &nbsp;&nbsp; {status_html}</div>"
                    output_html += f"<div class='log-file'>📁 파일: [{parent_folder}] {filename}</div>"

                    for i, step_name in enumerate(flow_list):
                        clean_step = "".join(step_name.split()).lower()
                        step_found = False; timestamp_str = "" 

                        for line in target_lines:
                            if clean_step in "".join(line.split()).lower():
                                step_found = True
                                time_match = re.search(r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})", line)
                                if time_match: timestamp_str = f"[{time_match.group(1)}] "
                                break
                        
                        if step_found:
                            clean_name = step_name.replace("[SERVER CONTENTS]", "").strip()
                            output_html += f"<div class='step-pass'>&nbsp;&nbsp;✅ {timestamp_str}{clean_name}</div>"
                            excel_data_list.append({"날짜": timestamp_str.strip("[] "), "거래유형": category_name, "거래상태": status_html, "파일명": filename, "단계": clean_name, "결과": "성공", "내용": ""})
                            
                            step_line_idx = -1
                            for idx, line in enumerate(target_lines):
                                if clean_step in "".join(line.split()).lower():
                                    step_line_idx = idx; break
                            
                            if step_line_idx != -1:
                                found_input_details = False; found_credit_details = False
                                capturing_data = False; found_data = False; capturing_payment = False 
                                start_marker = "client callback :: TDR210S / WOWICCARD_DATA"
                                end_marker = "client callback :: TDR210S / WOWICCARD_STATUS / {2} / {3} / empty"

                                for scan_idx in range(step_line_idx + 1, len(target_lines)):
                                    current_line = target_lines[scan_idx]
                                    if "[SERVER CONTENTS]" in current_line and "[ERROR]" not in current_line.upper(): break
                                    
                                    line_clean = "".join(current_line.split()).lower()
                                    line_content = current_line.strip()

                                    # 에러
                                    if "[error][3]networkerror" in line_clean:
                                         output_html += f"<div class='critical'>&nbsp;&nbsp;&nbsp;&nbsp;🚨 [치명적 에러] {line_content}</div>"; excel_data_list.append({"날짜": "", "거래유형": category_name, "거래상태": status_html, "파일명": filename, "단계": clean_name, "결과": "치명적 에러", "내용": line_content})
                                    elif "[error][servercontents]" in line_clean:
                                         output_html += f"<div class='critical'>&nbsp;&nbsp;&nbsp;&nbsp;💥 [서버 에러] {line_content}</div>"; excel_data_list.append({"날짜": "", "거래유형": category_name, "거래상태": status_html, "파일명": filename, "단계": clean_name, "결과": "서버 에러", "내용": line_content})
                                    elif "[error]" in line_clean:
                                         output_html += f"<div class='critical'>&nbsp;&nbsp;&nbsp;&nbsp;💀 {line_content}</div>"
                                    
                                    # 상세 로그
                                    if "ORDER_RATE" in current_line: output_html += f"<div class='info-detail'>&nbsp;&nbsp;&nbsp;&nbsp;💱 {line_content}</div>"
                                    if "HSCDU2_1" in current_line or "HSCDU2_2" in current_line:
                                        output_html += f"<div class='info-money'>&nbsp;&nbsp;&nbsp;&nbsp;💸 {line_content}</div>"; excel_data_list.append({"날짜": "", "거래유형": category_name, "거래상태": status_html, "파일명": filename, "단계": clean_name, "결과": "배출", "내용": line_content})
                                    if "SCAN_PASS" in step_name or "SCAN_BY_PASSPORT" in step_name or "SCAN_PASSPORT" in step_name:
                                        if "일 한도" in current_line: output_html += f"<div class='info-money'>&nbsp;&nbsp;&nbsp;&nbsp;💳 {line_content}</div>"
                                        if "passport:" in current_line.lower():
                                            match = re.search(r"passport\s*:\s*\{(.*?)\}", current_line, re.IGNORECASE)
                                            if match: output_html += f"<div class='info-detail'>&nbsp;&nbsp;&nbsp;&nbsp;🛂 [여권 정보] {match.group(1).strip()}</div>"; excel_data_list.append({"날짜": "", "거래유형": category_name, "거래상태": status_html, "파일명": filename, "단계": clean_name, "결과": "정보", "내용": match.group(1).strip()})
                                    if "C_T_SEL_AMT" in step_name or "C_W_SELECT_AMT" in step_name:
                                        if "선택 금액" in current_line: output_html += f"<div class='info-detail'>&nbsp;&nbsp;&nbsp;&nbsp;💰 {line_content}</div>"
                                    if "PAYMENT" in step_name or "SALE_ACC_CHECK" in step_name:
                                        if "결제 시작" in current_line or "결제시작" in current_line:
                                            capturing_payment = True; output_html += f"<div class='info-money'>&nbsp;&nbsp;&nbsp;&nbsp;💳 [결제 로그 시작]</div>"; output_html += f"<div class='info-detail'>&nbsp;&nbsp;&nbsp;&nbsp;{line_content}</div>"; continue
                                        if capturing_payment:
                                            output_html += f"<div class='info-detail'>&nbsp;&nbsp;&nbsp;&nbsp;{line_content}</div>"
                                            if "결제 성공" in current_line or "결제성공" in current_line:
                                                capturing_payment = False; output_html += f"<div class='step-pass'>&nbsp;&nbsp;&nbsp;&nbsp;✅ [결제 완료]</div>"; excel_data_list.append({"날짜": "", "거래유형": category_name, "거래상태": status_html, "파일명": filename, "단계": clean_name, "결과": "결제성공", "내용": "결제 완료"})
                                    if (mode == "CASH" or mode == "CHARGE" or mode == "EXCHANGE" or mode == "EXCHANGE_FOREIGN") and ("INPUT" in step_name or "CURRENCY" in step_name):
                                        if "SCN8237R" in current_line:
                                            if "ACCEPT" in current_line: output_html += f"<div class='info-money'>&nbsp;&nbsp;&nbsp;&nbsp;💵 {line_content}</div>"; found_input_details = True; excel_data_list.append({"날짜": "", "거래유형": category_name, "거래상태": status_html, "파일명": filename, "단계": clean_name, "결과": "투입", "내용": line_content})
                                            elif "REJECT" in current_line: output_html += f"<div class='info-alert'>&nbsp;&nbsp;&nbsp;&nbsp;🚨 {line_content}</div>"; found_input_details = True; excel_data_list.append({"날짜": "", "거래유형": category_name, "거래상태": status_html, "파일명": filename, "단계": clean_name, "결과": "반환", "내용": line_content})
                                    if (mode == "CREDIT" or mode == "CHARGE") and "C_I_CREDIT" in step_name:
                                        if "{SUC: '00'" in current_line: output_html += f"<div class='info-money'>&nbsp;&nbsp;&nbsp;&nbsp;💳 {line_content}</div>"; found_credit_details = True
                                        if "{SUC: '01'" in current_line: output_html += f"<div class='info-alert'>&nbsp;&nbsp;&nbsp;&nbsp;🚨 {line_content} (승인 실패)</div>"; found_credit_details = True
                                        if "결제 성공" in current_line: output_html += f"<div class='step-pass'>&nbsp;&nbsp;&nbsp;&nbsp;✅ {line_content}</div>"; found_credit_details = True
                                    if "ACTIVATE" in step_name or "C_INSERT_CARD" in step_name:
                                        if start_marker in current_line:
                                            capturing_data = True; output_html += f"<div class='info-detail'>&nbsp;&nbsp;&nbsp;&nbsp;📂 [카드 데이터 구간]</div>"; continue
                                        if capturing_data:
                                            output_html += f"<div class='info-detail'>&nbsp;&nbsp;&nbsp;&nbsp;{line_content}</div>"
                                            if end_marker in current_line: capturing_data = False

                                # 누락 경고
                                if (mode == "CASH" or mode == "CHARGE" or mode == "EXCHANGE") and ("INPUT" in step_name) and not found_input_details: output_html += f"<div class='info-detail'>&nbsp;&nbsp;&nbsp;&nbsp;(⚠️ 투입 로그 없음)</div>"
                                if (mode == "CREDIT" or mode == "CHARGE") and "C_I_CREDIT" in step_name and not found_credit_details: output_html += f"<div class='info-detail'>&nbsp;&nbsp;&nbsp;&nbsp;(⚠️ 결제 상세 로그 없음)</div>"
                        else:
                            clean_name = step_name.replace("[SERVER CONTENTS]", "").strip()
                            output_html += f"<div class='step-fail'> ❌ {clean_name} (누락됨)</div>"
                            excel_data_list.append({"날짜": "", "거래유형": category_name, "거래상태": status_html, "파일명": filename, "단계": clean_name, "결과": "누락", "내용": "단계 없음"})

                    if pre_calc_cash:
                        output_html += "<div class='money-box'><div class='info-money'>💰 [투입 금액 요약]</div>"
                        for curr, info in pre_calc_cash.items():
                            amt = info['amount']; cnt = info['count']
                            output_html += f"<div style='color:white; font-weight:bold;'>&nbsp;&nbsp;&nbsp;&nbsp;- Total {curr}: {amt:,} (총 {cnt}장)</div>"
                        output_html += "</div>"
                    
                    output_html += "<div class='separator'></div>"

    return found_any_target, output_html, excel_data_list

# ==========================================
# 3. 메인 UI
# ==========================================
st.title("🕵️‍♂️ 디지털 탐정 Web")
st.markdown("---")

with st.sidebar:
    st.header("🔍 검색 설정")
    # (⭐수정됨: 로컬 경로 입력창 복구!⭐)
    default_path = r"C:\Users\jin33\OneDrive\바탕 화면\My_logs"
    folder_path = st.text_input("로그 폴더 경로", value=default_path)
    
    today = datetime.now(); yesterday = today - timedelta(days=1)
    start_date = st.date_input("시작 날짜", value=yesterday)
    end_date = st.date_input("종료 날짜", value=today)
    
    category_list = ["전체", "카드 발급 (현금)", "카드 발급 (신용카드)", "카드 재발급", "카드 충전 (현금)", "카드 충전 (신용카드)", "원화 환전", "외화 환전 (현금)", "외화 환전 (신용카드)", "카드 출금"]
    selected_category = st.selectbox("거래 유형", category_list)
    
    keyword = st.text_input("고객 정보 (카드/여권번호)", value="9710029904831725")
    search_btn = st.button("🔍 분석 시작", type="primary")

if search_btn:
    processed_keyword = "".join(keyword.split()).lower()
    
    if not os.path.exists(folder_path):
        st.error(f"❌ 폴더를 찾을 수 없습니다: {folder_path}")
    else:
        with st.spinner('로그 파일을 정밀 분석 중입니다...'):
            if selected_category == "전체":
                target_configs = TRANSACTION_MAP.items()
            else:
                if selected_category in TRANSACTION_MAP:
                    target_configs = [(selected_category, TRANSACTION_MAP[selected_category])]
                else:
                    st.error("설정되지 않은 유형입니다.")
                    target_configs = []

            found_something_total = False
            final_html = ""
            final_excel_list = []

            for category_name, config in target_configs:
                flow_list, mode, validator = config
                if not flow_list: continue
                
                found, html_result, excel_list = analyze_flow_web(
                    folder_path, 
                    processed_keyword, 
                    flow_list, 
                    mode, 
                    validator, 
                    start_date, 
                    end_date, 
                    category_name
                )
                
                if found:
                    found_something_total = True
                    final_html += html_result
                    final_excel_list.extend(excel_list)

            if found_something_total:
                st.markdown(final_html, unsafe_allow_html=True)
                if final_excel_list:
                    df = pd.DataFrame(final_excel_list)
                    df['거래상태'] = df['거래상태'].apply(lambda x: re.sub('<[^<]+?>', '', x))
                    csv = df.to_csv(index=False).encode('utf-8-sig')
                    st.download_button(label="💾 결과 엑셀(CSV) 다운로드", data=csv, file_name='search_result.csv', mime='text/csv')
            else:
                st.warning(f"😥 '{keyword}' 정보가 포함된 로그를 찾지 못했습니다.")

