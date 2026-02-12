import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# =========================
# 0) 페이지 설정 + 스타일
# =========================
st.set_page_config(
    page_title="전세 레버리지를 활용한 시세 차익 지역 예측 분석",
    page_icon="🏠",
    layout="wide",
)

st.markdown(
    """
<style>
.main .block-container {max-width: 1220px; padding-top: 1.1rem;}

.hero {border-radius: 16px; overflow:hidden; border:1px solid #eee; margin-bottom: 14px; background:#fafafa;}
.hero img {height: 165px; width:100%; object-fit: cover;}

.card {
  background:#fff; border:1px solid #eee; border-radius:16px;
  padding:16px; box-shadow: 0 8px 18px rgba(0,0,0,0.06); margin-bottom: 12px;
}
.badge {
  display:inline-block; padding:4px 10px; border-radius:999px; font-size:.85rem;
  background:#f3f4f6; margin-bottom:8px;
}
.small {color:#6b7280; font-size:.92rem; line-height: 1.45;}
.kpi-note {color:#6b7280; font-size:.85rem; margin-top: -6px;}
.pill {
  display:inline-block; padding:4px 10px; border-radius:999px; font-size:.8rem;
  border:1px solid #eee; background:#fafafa;
}
</style>
""",
    unsafe_allow_html=True,
)

# =========================
# 1) 상단 헤더
# =========================
st.title("전세 레버리지를 활용한 시세 차익 지역 예측 분석")
st.caption(
    "KB 부동산 주간 매매지수·전세지수를 기반으로, ‘전세 레버리지(갭)’ 관점에서 "
    "지역별 자기자본 기준 성과(ROE)를 예측하고 리스크 지표로 보완합니다."
)

# =========================
# 2) 사이드바
# =========================
st.sidebar.title("📌 Navigation")

page = st.sidebar.radio(
    "메뉴",
    [
        "0. 프로젝트 개요",
        "1. 데이터의 이해",
        "2. 데이터 전처리 & 검증",
        "3. 분석 결과(Top 지역 선별)",
        "4. 예측 & 자기자본 수익률(ROE)",
        "5. 인사이트 & 한계",
    ],
)

# =========================
# HERO (안정형 URL + fallback)
# =========================
def u(img_id):
    return "https://images.unsplash.com/{}?auto=format&fit=crop&w=1600&q=80".format(img_id)

HERO_IMAGES = {
    "0. 프로젝트 개요": u("photo-1560518883-ce09059eeffa"),
    "1. 데이터의 이해": u("photo-1551288049-bebda4e38f71"),
    "2. 데이터 전처리 & 검증": u("photo-1526379095098-d400fd0bf935"),
    "3. 분석 결과(Top 지역 선별)": u("photo-1486406146926-c627a92ad1ab"),
    "4. 예측 & 자기자본 수익률(ROE)": u("photo-1553729459-efe14ef6055d"),
    "5. 인사이트 & 한계": u("photo-1454165804606-c3d57bc86b40"),
}
FALLBACK_HERO = u("photo-1516542076529-1ea3854896f2")

def render_hero(page_name):
    url = HERO_IMAGES.get(page_name, FALLBACK_HERO)
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    try:
        st.image(url, use_container_width=True)
    except Exception:
        st.image(FALLBACK_HERO, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

render_hero(page)

# -------------------------
# 사이드바 옵션(기존 유지)
# -------------------------
st.sidebar.divider()
st.sidebar.markdown("### ⚙ 분석 파라미터")
start_year = st.sidebar.selectbox("분석 시작 연도", [2014, 2015, 2016, 2017, 2018], index=2)
dash_threshold = st.sidebar.slider("결측(‘-’) 허용 비율(지역 제외 기준)", 0.10, 0.90, 0.50, 0.05)
top_n = st.sidebar.slider("비교할 상위 지역 수(Top N)", 5, 20, 10)
horizon_years = st.sidebar.selectbox("예측 기간(년)", [1, 5, 10], index=0)

st.sidebar.divider()
st.sidebar.markdown("### 📂 데이터 로드")
data_mode = st.sidebar.radio("데이터 방식", ["폴더(data/)에서 자동 로드", "파일 업로드"], index=0)

sale_file = None
rent_file = None
sale_path = "data/주간 아파트 매매가격지수_20260210.xlsx"
rent_path = "data/주간 아파트 전세가격지수_20260210.xlsx"

if data_mode == "파일 업로드":
    sale_file = st.sidebar.file_uploader("매매지수 엑셀(.xlsx)", type=["xlsx"])
    rent_file = st.sidebar.file_uploader("전세지수 엑셀(.xlsx)", type=["xlsx"])
else:
    st.sidebar.caption("기본 경로:")
    st.sidebar.code(sale_path)
    st.sidebar.code(rent_path)

st.sidebar.divider()
show_debug = st.sidebar.checkbox("중간 산출물 자세히 보기", value=True)

st.sidebar.divider()
st.sidebar.markdown("### 🧮 결과 정렬(예측 페이지)")
pred_sort = st.sidebar.selectbox(
    "정렬 기준",
    ["예상 ROE(내림차순)", "ROE/Vol(내림차순)", "누적 매매 상승률(내림차순)"],
    index=0,
)

# =========================
# 3) 유틸
# =========================
@st.cache_data(show_spinner=False)
def load_excel(path_or_file):
    return pd.read_excel(path_or_file, engine="openpyxl")

def melt_long(df_wide, value_name):
    df_long = df_wide.melt(id_vars="지역명", var_name="날짜", value_name=value_name)
    df_long["날짜"] = pd.to_datetime(df_long["날짜"], errors="coerce")
    df_long = df_long.dropna(subset=["날짜"])
    return df_long

def dash_ratio_by_region(df_long, value_col):
    tmp = df_long.copy()
    tmp["is_dash"] = (tmp[value_col] == "-")
    return tmp.groupby("지역명")["is_dash"].mean().sort_values(ascending=False)

def clean_numeric(df_long, value_col, valid_regions):
    tmp = df_long[df_long["지역명"].isin(valid_regions)].copy()
    tmp[value_col] = tmp[value_col].replace("-", np.nan)
    tmp[value_col] = pd.to_numeric(tmp[value_col], errors="coerce")
    tmp = tmp.dropna(subset=[value_col])
    return tmp

def cumulative_return(df_long_clean, value_col):
    g = df_long_clean.sort_values(["지역명", "날짜"]).groupby("지역명")[value_col]
    return g.apply(lambda x: x.iloc[-1] / x.iloc[0] - 1).sort_values(ascending=False)

def merge_sale_rent(sale_clean, rent_clean):
    return pd.merge(
        sale_clean,
        rent_clean[["지역명", "날짜", "전세지수"]],
        on=["지역명", "날짜"],
        how="inner",
    )

# =========================
# ✅ Risk 지표 계산 안정화 (핵심 수정)
# - 매매: pct_change 기반(기존 방식 유지)
# - 갭: pct_change는 0/음수 교차에서 inf/NaN 폭증 → diff 기반 정규화 + MDD는 양수 시프트
# =========================
def _to_clean_series(x):
    return pd.to_numeric(x, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()

def annualized_vol_price_pct(index_series):
    s = _to_clean_series(index_series)
    r = s.pct_change().replace([np.inf, -np.inf], np.nan).dropna()
    if len(r) < 2:
        return np.nan
    return float(r.std(ddof=0) * np.sqrt(52) * 100)

def annualized_vol_gap_diff_norm(gap_series):
    """
    갭은 pct_change가 불안정하므로,
    - 주간 변화량(diff)의 표준편차를
    - 갭의 대표 규모(중앙값(|gap|))로 나눠 정규화(%)
    """
    s = _to_clean_series(gap_series)
    d = s.diff().replace([np.inf, -np.inf], np.nan).dropna()
    if len(d) < 2:
        return np.nan

    scale = float(s.abs().median())
    if scale == 0 or np.isnan(scale):
        return np.nan

    r = (d / scale).replace([np.inf, -np.inf], np.nan).dropna()
    if len(r) < 2:
        return np.nan
    return float(r.std(ddof=0) * np.sqrt(52) * 100)

def max_drawdown_price(index_series):
    s = _to_clean_series(index_series)
    if len(s) < 2:
        return np.nan
    cum_max = s.cummax()
    dd = (s / cum_max) - 1.0
    return float(dd.min() * 100)

def max_drawdown_gap_shifted(gap_series):
    """
    갭은 음수/0이 가능해서 (s/cummax)-1 방식이 깨질 수 있음
    → 최소값을 0 위로 시프트한 뒤 drawdown 계산
    """
    s = _to_clean_series(gap_series)
    if len(s) < 2:
        return np.nan
    minv = float(s.min())
    shifted = s - minv + 1e-6  # 항상 양수
    cum_max = shifted.cummax()
    dd = (shifted / cum_max) - 1.0
    return float(dd.min() * 100)

def polyfit_predict_and_r2(index_series, horizon_weeks):
    y = _to_clean_series(index_series).values.astype(float)
    if len(y) < 10:
        return (np.nan, np.nan)

    x = np.arange(len(y)).astype(float)
    a, b = np.polyfit(x, y, 1)
    y_hat = a * x + b

    ss_res = np.sum((y - y_hat) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot != 0 else np.nan

    future_x = x.max() + horizon_weeks
    pred = float(a * future_x + b)
    return pred, float(r2)

def equity_return_percent(predicted_sale, current_sale, current_rent):
    equity = current_sale - current_rent
    if equity == 0:
        return np.nan
    return (predicted_sale - current_sale) / equity * 100

def roe_grade(roe):
    if np.isnan(roe):
        return "N/A"
    if roe >= 80:
        return "A (High)"
    if roe >= 40:
        return "B (Medium)"
    if roe >= 0:
        return "C (Low)"
    return "D (Negative)"

def r2_badge(r2):
    if np.isnan(r2):
        return "N/A"
    if r2 >= 0.80:
        return "높음"
    if r2 >= 0.60:
        return "보통"
    return "낮음"

def risk_score(vol_sale, mdd_sale, vol_gap, mdd_gap):
    parts = [vol_sale, mdd_sale, vol_gap, mdd_gap]
    if any(pd.isna(p) for p in parts):
        return np.nan
    return float(0.35*abs(vol_sale) + 0.15*abs(mdd_sale) + 0.35*abs(vol_gap) + 0.15*abs(mdd_gap))

# =========================
# ✅ Risk Score 표시 정책(축소형)
# - 기본: 표에 표시(없으면 '-'로)
# - 유효 값이 충분할 때만 그래프 노출
# =========================
def render_risk_score_section(df_indexed, colname="Risk Score(참고)", min_valid_for_chart=3):
    if df_indexed is None or df_indexed.empty or colname not in df_indexed.columns:
        st.caption("Risk Score 데이터를 표시할 수 없습니다.")
        return

    s = pd.to_numeric(df_indexed[colname], errors="coerce")
    valid_cnt = int(s.notna().sum())
    total_cnt = int(len(s))

    st.caption("Risk Score 유효값: {}/{} (유효값이 충분할 때만 그래프가 표시됩니다)".format(valid_cnt, total_cnt))

    display_df = df_indexed[[colname]].copy()
    display_df[colname] = pd.to_numeric(display_df[colname], errors="coerce")
    display_df = display_df.sort_values(colname, ascending=False)
    display_df[colname] = display_df[colname].map(lambda x: "-" if pd.isna(x) else float(x))
    st.dataframe(display_df, use_container_width=True)

    if valid_cnt >= min_valid_for_chart:
        chart_df = pd.to_numeric(df_indexed[colname], errors="coerce").dropna().to_frame(colname)
        st.bar_chart(chart_df)
    else:
        st.info("현재 조건에서는 Risk Score 유효값이 부족하여 그래프를 숨겼습니다. (표로만 표시)")

# =========================
# 4) 데이터 로드
# =========================
sale_wide = rent_wide = None
load_error = None

try:
    if data_mode == "파일 업로드":
        if sale_file is not None and rent_file is not None:
            sale_wide = load_excel(sale_file)
            rent_wide = load_excel(rent_file)
    else:
        sale_wide = load_excel(sale_path)
        rent_wide = load_excel(rent_path)
except Exception as e:
    load_error = str(e)

data_ready = (sale_wide is not None) and (rent_wide is not None) and (load_error is None)

# =========================
# 5) 공통 파이프라인
# =========================
sale_long = rent_long = sale_clean = rent_clean = merged = None
dash_sale = dash_rent = None
return_sale = None
top_regions = []
top_data = None

if data_ready:
    sale_long = melt_long(sale_wide, "매매지수")
    rent_long = melt_long(rent_wide, "전세지수")

    sale_long = sale_long[sale_long["날짜"].dt.year >= start_year].copy()
    rent_long = rent_long[rent_long["날짜"].dt.year >= start_year].copy()

    dash_sale = dash_ratio_by_region(sale_long, "매매지수")
    dash_rent = dash_ratio_by_region(rent_long, "전세지수")

    valid_regions = dash_sale[dash_sale < dash_threshold].index

    sale_clean = clean_numeric(sale_long, "매매지수", valid_regions)
    rent_clean = clean_numeric(rent_long, "전세지수", valid_regions)

    merged = merge_sale_rent(sale_clean, rent_clean)

    return_sale = cumulative_return(sale_clean, "매매지수")
    top_regions = return_sale.head(top_n).index.tolist()
    top_data = merged[merged["지역명"].isin(top_regions)].copy().sort_values(["지역명", "날짜"])

# =========================
# 6) 선택 지역(session_state) 동기화
# =========================
def sync_selected_region(options):
    if not options:
        return
    if "selected_region" not in st.session_state:
        st.session_state.selected_region = options[0]
    if st.session_state.selected_region not in options:
        st.session_state.selected_region = options[0]

if data_ready and top_regions:
    sync_selected_region(top_regions)

if data_ready and top_regions:
    st.sidebar.divider()
    st.sidebar.markdown("### 🗺️ 지역 선택(공통)")
    st.sidebar.selectbox(
        "분석 지역",
        top_regions,
        key="selected_region",
        help="모든 메뉴에서 동일 지역이 자동 반영됩니다."
    )

# =========================
# 7) KPI + 공통 설명
# =========================
def kpi_row():
    if not data_ready:
        return
    n_regions_raw = int(sale_wide["지역명"].nunique()) if "지역명" in sale_wide.columns else 0
    n_regions_valid = int(len(dash_sale[dash_sale < dash_threshold])) if dash_sale is not None else 0
    date_min = sale_long["날짜"].min().date()
    date_max = sale_long["날짜"].max().date()

    total_obs = len(sale_long)
    clean_obs = len(sale_clean) if sale_clean is not None else 0
    coverage = (clean_obs / total_obs * 100) if total_obs > 0 else np.nan

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("원본 지역 수", "{:,}".format(n_regions_raw))
    c2.metric("분석 대상 지역 수", "{:,}".format(n_regions_valid), "-{:,}".format(n_regions_raw - n_regions_valid))
    c3.metric("분석 시작", str(date_min))
    c4.metric("분석 종료", str(date_max))
    c5.metric("데이터 커버리지", "{:.1f}%".format(coverage))
    st.markdown(
        "<div class='kpi-note'>커버리지 = (수치형 변환 후 유효 데이터 수) ÷ (원본 Long 데이터 수)</div>",
        unsafe_allow_html=True
    )

def scoring_explain_compact():
    st.markdown(
        """
<div class="small">
<span class="pill">ROE</span>
(예측매매 − 현재매매) ÷ (현재매매 − 현재전세) × 100
&nbsp;&nbsp;|&nbsp;&nbsp;
<span class="pill">Risk Score</span>
0.35·|매매Vol| + 0.15·|매매MDD| + 0.35·|갭Vol| + 0.15·|갭MDD|
&nbsp;&nbsp;|&nbsp;&nbsp;
<span class="pill">R² 신뢰도</span>
≥0.80 높음 / ≥0.60 보통 / 그 외 낮음
</div>
""",
        unsafe_allow_html=True,
    )

# =========================
# ✅ (필수) region_snapshot 복원 (NameError 해결)
# =========================
def region_snapshot(region):
    if (not data_ready) or (merged is None) or (region is None):
        return None

    df = merged[merged["지역명"] == region].sort_values("날짜").dropna(subset=["매매지수", "전세지수"]).copy()
    if len(df) < 20:
        return None

    sale_s = df["매매지수"]
    rent_s = df["전세지수"]
    gap_s = (sale_s - rent_s)

    cur_sale = float(pd.to_numeric(sale_s, errors="coerce").dropna().iloc[-1])
    cur_rent = float(pd.to_numeric(rent_s, errors="coerce").dropna().iloc[-1])
    cur_gap = float(pd.to_numeric(gap_s, errors="coerce").dropna().iloc[-1])

    # 매매는 pct 기반
    vol_sale = annualized_vol_price_pct(sale_s)
    mdd_sale = max_drawdown_price(sale_s)

    # 갭은 안정화된 방식
    vol_gap = annualized_vol_gap_diff_norm(gap_s)
    mdd_gap = max_drawdown_gap_shifted(gap_s)

    horizon_weeks = {1: 52, 5: 260, 10: 520}.get(horizon_years, 52)
    pred_sale, r2 = polyfit_predict_and_r2(sale_s, horizon_weeks)
    roe = equity_return_percent(pred_sale, cur_sale, cur_rent)

    score = risk_score(vol_sale, mdd_sale, vol_gap, mdd_gap)

    return {
        "cur_sale": cur_sale,
        "cur_rent": cur_rent,
        "cur_gap": cur_gap,
        "vol_sale": vol_sale,
        "mdd_sale": mdd_sale,
        "vol_gap": vol_gap,
        "mdd_gap": mdd_gap,
        "pred_sale": pred_sale,
        "r2": r2,
        "roe": roe,
        "roe_grade": roe_grade(roe),
        "risk_score": score,
        "r2_badge": r2_badge(r2),
    }

# =========================
# 에러 안내
# =========================
if load_error:
    st.error(
        "데이터 로드에 실패했습니다.\n\n"
        "- 원인: {}\n\n"
        "체크 포인트:\n"
        "1) openpyxl 설치 여부 (pip install openpyxl)\n"
        "2) 자동 로드 모드라면 data/ 폴더에 파일이 있는지\n"
        "3) 업로드 모드라면 매매/전세 파일을 둘 다 올렸는지".format(load_error)
    )

# =========================
# 8) 페이지 렌더링
# =========================
selected_region = st.session_state.get("selected_region", top_regions[0] if top_regions else None)

if page == "0. 프로젝트 개요":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="badge">🎯 프로젝트 목적</div>', unsafe_allow_html=True)
    st.write(
        "전세 레버리지 구조에서 지역별 시세차익 가능성을 비교하기 위해, "
        "KB 주간 매매지수·전세지수를 기반으로 후보 지역을 선별하고 "
        "자기자본 기준 성과(ROE)를 예측합니다. 또한 변동성/최대낙폭 지표로 해석의 안정성을 보완합니다."
    )
    st.markdown('<div class="badge">🧭 분석 설계</div>', unsafe_allow_html=True)
    st.write(
        "① 데이터 구조 이해 → ② 전처리/결측 검증 → ③ 상위 지역 선별 → "
        "④ 추세 예측(polyfit) → ⑤ ROE 산출 → ⑥ 리스크 지표(Vol/MDD)로 보완"
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if data_ready:
        kpi_row()
        st.info("사이드바에서 지역/예측기간을 바꾸면 3/4/5번 메뉴의 모든 차트·표가 자동으로 반영됩니다.")

elif page == "1. 데이터의 이해":
    st.header("1) 데이터의 이해")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="badge">📌 데이터 구조</div>', unsafe_allow_html=True)
    st.write(
        "- 원본 엑셀: **행=지역명**, **열=주간 날짜**, 값=지수(매매/전세)\n"
        "- 분석 테이블: **(지역명, 날짜, 매매지수, 전세지수)** 형태로 변환해 계산합니다.\n"
        "- 지수 데이터는 절대가격이 아닌 **상대적 추세 비교**에 적합합니다."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if not data_ready:
        st.warning("데이터가 아직 로드되지 않았습니다. 사이드바에서 data/ 경로 또는 업로드를 확인하세요.")
    else:
        kpi_row()
        with st.expander("원본 엑셀 미리보기(앞 5행)", expanded=True):
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("매매지수(원본)")
                st.dataframe(sale_wide.head(), use_container_width=True)
            with c2:
                st.subheader("전세지수(원본)")
                st.dataframe(rent_wide.head(), use_container_width=True)

elif page == "2. 데이터 전처리 & 검증":
    st.header("2) 데이터 전처리 & 검증")

    if not data_ready:
        st.warning("데이터가 아직 로드되지 않았습니다. 사이드바에서 data/ 경로 또는 업로드를 확인하세요.")
    else:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="badge">🔍 전처리 원칙</div>', unsafe_allow_html=True)
        st.write(
            "1) `'-'`는 결측으로 처리\n"
            "2) 결측 비율이 높은 지역은 분석에서 제외(품질 확보)\n"
            "3) 날짜 타입 변환 후, 지수를 수치형으로 변환\n"
            "4) 매매/전세를 동일 날짜 기준으로 병합"
        )
        st.markdown("</div>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="badge">📉 결측(‘-’) 비율: 매매</div>', unsafe_allow_html=True)
            st.dataframe(dash_sale.head(15), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="badge">📉 결측(‘-’) 비율: 전세</div>', unsafe_allow_html=True)
            st.dataframe(dash_rent.head(15), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        if show_debug:
            with st.expander("전처리 후 Long 테이블(샘플 20행)", expanded=False):
                c3, c4 = st.columns(2)
                with c3:
                    st.subheader("매매(Long, clean)")
                    st.dataframe(sale_clean.head(20), use_container_width=True)
                with c4:
                    st.subheader("전세(Long, clean)")
                    st.dataframe(rent_clean.head(20), use_container_width=True)

            with st.expander("병합 테이블(샘플 20행)", expanded=False):
                st.dataframe(merged.head(20), use_container_width=True)

elif page == "3. 분석 결과(Top 지역 선별)":
    st.header("3) 분석 결과: Top 지역 선별")

    if not data_ready:
        st.warning("데이터가 아직 로드되지 않았습니다. 사이드바에서 data/ 경로 또는 업로드를 확인하세요.")
    else:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="badge">🏁 선별 기준</div>', unsafe_allow_html=True)
        st.write(
            "후보 지역은 **분석 기간 동안의 누적 매매지수 상승률**을 기준으로 1차 선별합니다. "
            "Risk Score는 참고 지표로 제공되며, 유효 데이터가 충분할 때만 그래프가 표시됩니다."
        )
        scoring_explain_compact()
        st.markdown("</div>", unsafe_allow_html=True)

        base = (return_sale.head(top_n) * 100).to_frame("누적 매매지수 상승률(%)")

        risk_rows = []
        for r in top_regions:
            df = merged[merged["지역명"] == r].sort_values("날짜").dropna(subset=["매매지수", "전세지수"]).copy()
            sale_s = df["매매지수"]
            gap_s = (df["매매지수"] - df["전세지수"])

            vol_sale = annualized_vol_price_pct(sale_s)
            mdd_sale = max_drawdown_price(sale_s)
            vol_gap = annualized_vol_gap_diff_norm(gap_s)
            mdd_gap = max_drawdown_gap_shifted(gap_s)
            score = risk_score(vol_sale, mdd_sale, vol_gap, mdd_gap)

            risk_rows.append([r, vol_sale, mdd_sale, vol_gap, mdd_gap, score])

        risk_df = pd.DataFrame(
            risk_rows,
            columns=["지역", "매매 Vol(연%)", "매매 MDD(%)", "갭 Vol(연%)", "갭 MDD(%)", "Risk Score(참고)"]
        ).set_index("지역")

        top_table = base.join(risk_df, how="left").sort_values("누적 매매지수 상승률(%)", ascending=False)

        st.subheader("✅ Top {} 지역 (산출물 테이블)".format(top_n))
        st.dataframe(top_table, use_container_width=True)

        cA, cB = st.columns([1, 1])
        with cA:
            st.subheader("📊 누적 상승률(%)")
            st.bar_chart(top_table[["누적 매매지수 상승률(%)"]])

        with cB:
            st.subheader("📊 Risk Score(참고) — 축소형 표시")
            render_risk_score_section(top_table, colname="Risk Score(참고)", min_valid_for_chart=3)

        st.subheader("📈 선택 지역: 매매/전세 지수 추이")
        if selected_region is None:
            st.write("선택 지역이 없습니다.")
        else:
            ts = (
                merged[merged["지역명"] == selected_region][["날짜", "매매지수", "전세지수"]]
                .sort_values("날짜")
                .set_index("날짜")
            )
            st.line_chart(ts)
            st.caption("현재 선택 지역: {}".format(selected_region))

        st.download_button(
            label="⬇ Top 지역 테이블 다운로드(CSV)",
            data=top_table.to_csv(encoding="utf-8-sig"),
            file_name="top_regions_with_risk_top{}.csv".format(top_n),
            mime="text/csv",
        )

elif page == "4. 예측 & 자기자본 수익률(ROE)":
    st.header("4) 예측 & 자기자본 수익률(ROE)")

    if not data_ready:
        st.warning("데이터가 아직 로드되지 않았습니다. 사이드바에서 data/ 경로 또는 업로드를 확인하세요.")
    else:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="badge">📐 산식 정의</div>', unsafe_allow_html=True)
        st.write(
            "- 자기자본(Equity) = 현재 매매지수 − 현재 전세지수\n"
            "- 예상 ROE(%) = (예측 매매지수 − 현재 매매지수) ÷ 자기자본 × 100\n"
            "- 예측 모델: 1차 추세회귀(np.polyfit), 적합도 지표로 R² 제공"
        )
        scoring_explain_compact()
        st.markdown("</div>", unsafe_allow_html=True)

        horizon_weeks = {1: 52, 5: 260, 10: 520}.get(horizon_years, 52)

        results = []
        for r in top_regions:
            df = top_data[top_data["지역명"] == r].sort_values("날짜").dropna(subset=["매매지수", "전세지수"]).copy()
            if len(df) < 20:
                continue

            sale_s = df["매매지수"]
            rent_s = df["전세지수"]
            gap_s = (sale_s - rent_s)

            pred_sale, r2 = polyfit_predict_and_r2(sale_s, horizon_weeks)
            cur_sale = float(_to_clean_series(sale_s).iloc[-1])
            cur_rent = float(_to_clean_series(rent_s).iloc[-1])
            roe = equity_return_percent(pred_sale, cur_sale, cur_rent)

            vol_sale = annualized_vol_price_pct(sale_s)
            mdd_sale = max_drawdown_price(sale_s)
            vol_gap = annualized_vol_gap_diff_norm(gap_s)
            mdd_gap = max_drawdown_gap_shifted(gap_s)
            score = risk_score(vol_sale, mdd_sale, vol_gap, mdd_gap)

            roe_over_vol = (roe / vol_sale) if (not pd.isna(vol_sale) and vol_sale != 0) else np.nan
            cum_sale = float(return_sale.loc[r] * 100) if (return_sale is not None and r in return_sale.index) else np.nan

            results.append([
                r,
                cur_sale,
                cur_rent,
                pred_sale,
                roe,
                roe_grade(roe),
                r2,
                r2_badge(r2),
                vol_sale,
                mdd_sale,
                vol_gap,
                mdd_gap,
                score,
                roe_over_vol,
                cum_sale,
            ])

        pred_df = pd.DataFrame(
            results,
            columns=[
                "지역",
                "현재매매지수",
                "현재전세지수",
                "{}년후_예측매매지수".format(horizon_years),
                "예상{}년_ROE(%)".format(horizon_years),
                "ROE 등급",
                "추세적합도 R²",
                "R² 신뢰도",
                "매매 Vol(연%)",
                "매매 MDD(%)",
                "갭 Vol(연%)",
                "갭 MDD(%)",
                "Risk Score(참고)",
                "ROE/Vol(참고)",
                "누적 매매 상승률(%)",
            ],
        ).dropna(subset=["예상{}년_ROE(%)".format(horizon_years)])

        if pred_sort == "예상 ROE(내림차순)":
            pred_df = pred_df.sort_values(by="예상{}년_ROE(%)".format(horizon_years), ascending=False)
        elif pred_sort == "ROE/Vol(내림차순)":
            pred_df = pred_df.sort_values(by="ROE/Vol(참고)", ascending=False)
        else:
            pred_df = pred_df.sort_values(by="누적 매매 상승률(%)", ascending=False)

        st.subheader("✅ 산출물: Top {} 지역 예측 결과".format(top_n))
        st.dataframe(pred_df.head(top_n), use_container_width=True)

        c1, c2 = st.columns([1, 1])
        with c1:
            st.subheader("📊 예상 ROE(%)")
            st.bar_chart(pred_df.head(top_n).set_index("지역")[["예상{}년_ROE(%)".format(horizon_years)]])

            st.subheader("📊 Risk Score(참고) — 축소형 표시")
            render_risk_score_section(
                pred_df.head(top_n).set_index("지역"),
                colname="Risk Score(참고)",
                min_valid_for_chart=3
            )

        with c2:
            st.subheader("🔎 선택 지역 상세(자동 반영)")
            if selected_region is None:
                st.write("선택 지역이 없습니다.")
            else:
                df = top_data[top_data["지역명"] == selected_region].sort_values("날짜").dropna(subset=["매매지수", "전세지수"]).copy()
                sale_s = df["매매지수"]
                rent_s = df["전세지수"]
                gap_s = (sale_s - rent_s)

                pred_sale, r2 = polyfit_predict_and_r2(sale_s, horizon_weeks)
                cur_sale = float(_to_clean_series(sale_s).iloc[-1])
                cur_rent = float(_to_clean_series(rent_s).iloc[-1])
                equity = cur_sale - cur_rent
                roe = equity_return_percent(pred_sale, cur_sale, cur_rent)

                vol_sale = annualized_vol_price_pct(sale_s)
                mdd_sale = max_drawdown_price(sale_s)
                vol_gap = annualized_vol_gap_diff_norm(gap_s)
                mdd_gap = max_drawdown_gap_shifted(gap_s)
                score = risk_score(vol_sale, mdd_sale, vol_gap, mdd_gap)

                st.line_chart(df.set_index("날짜")[["매매지수", "전세지수"]])

                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="badge">요약</div>', unsafe_allow_html=True)

                def _fmt(v, suffix=""):
                    return "-" if pd.isna(v) else "{:.2f}{}".format(float(v), suffix)

                st.write("- 지역: **{}**".format(selected_region))
                st.write("- 현재 매매지수: **{}**".format(_fmt(cur_sale)))
                st.write("- 현재 전세지수: **{}**".format(_fmt(cur_rent)))
                st.write("- 자기자본(매매-전세): **{}**".format(_fmt(equity)))
                st.write("- {}년 후 예측 매매지수: **{}**".format(horizon_years, _fmt(pred_sale)))
                st.write("- 예상 {}년 ROE: **{}%** ({})".format(horizon_years, _fmt(roe), roe_grade(roe)))
                st.write("- 추세 적합도(R²): **{}** / 신뢰도: **{}**".format("-" if pd.isna(r2) else "{:.3f}".format(r2), r2_badge(r2)))
                st.write("- 매매 Vol: **{}**, 매매 MDD: **{}**".format(_fmt(vol_sale, "%"), _fmt(mdd_sale, "%")))
                st.write("- 갭 Vol: **{}**, 갭 MDD: **{}**".format(_fmt(vol_gap, "%"), _fmt(mdd_gap, "%")))
                st.write("- Risk Score(참고): **{}**".format(_fmt(score)))
                st.markdown("</div>", unsafe_allow_html=True)

        st.download_button(
            label="⬇ 예측 결과 다운로드(CSV)",
            data=pred_df.to_csv(index=False, encoding="utf-8-sig"),
            file_name="predicted_roe_{}y_top{}.csv".format(horizon_years, top_n),
            mime="text/csv",
        )

elif page == "5. 인사이트 & 한계":
    st.header("5) 인사이트 & 한계")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="badge">요약</div>', unsafe_allow_html=True)
    st.write(
        "본 분석은 지수 기반 추세와 전세 레버리지(갭) 구조를 결합하여 지역별 상대 비교를 수행합니다. "
        "예측은 단순 추세회귀 기반이므로 정책·금리·공급·수급의 구조적 변화는 직접 반영하지 않습니다. "
        "따라서 결과 해석 시 리스크 지표(Vol/MDD)와 함께 참고하는 접근이 유효합니다."
    )
    scoring_explain_compact()
    st.markdown("</div>", unsafe_allow_html=True)

    if not data_ready:
        st.warning("데이터가 아직 로드되지 않았습니다. 사이드바에서 data/ 경로 또는 업로드를 확인하세요.")
    elif not selected_region:
        st.info("선택 지역이 없습니다. 사이드바에서 분석 지역을 선택하세요.")
    else:
        snap = region_snapshot(selected_region)

        st.subheader("선택 지역 요약(자동 반영)")
        if snap is None:
            st.write("데이터가 충분하지 않아 요약을 산출할 수 없습니다.")
        else:
            def _fmt(v, suffix=""):
                return "-" if pd.isna(v) else "{:.2f}{}".format(float(v), suffix)

            rs_txt = _fmt(snap.get("risk_score"))
            r2_txt = "-" if pd.isna(snap.get("r2")) else "{:.3f}".format(float(snap.get("r2")))
            roe_txt = _fmt(snap.get("roe"))

            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="badge">한 줄 결론</div>', unsafe_allow_html=True)

            st.write(
                "**{}**은(는) 예측 {}년 ROE가 **{}%({})**로 산출되었습니다. "
                "동시에 Risk Score(참고) **{}** 및 R² 신뢰도 **{}**를 함께 확인할 수 있습니다.".format(
                    selected_region,
                    horizon_years,
                    roe_txt,
                    snap.get("roe_grade", "N/A"),
                    rs_txt,
                    snap.get("r2_badge", "N/A"),
                )
            )

            st.markdown('<div class="badge">해석 포인트</div>', unsafe_allow_html=True)
            st.write(
                "- ROE가 높아도 갭 변동성/최대낙폭이 크면 체감 리스크가 커질 수 있습니다.\n"
                "- R² 신뢰도가 낮다면(추세가 불안정) 예측 수치를 ‘참고값’으로만 활용하는 것이 안전합니다.\n"
                "- Risk Score는 비교용 스코어이며, 값이 '-'이면(유효값 부족) ROE/추세 중심으로 해석하세요."
            )

            st.markdown('<div class="badge">핵심 지표(요약)</div>', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("예상 ROE(%)", roe_txt, snap.get("roe_grade", ""))
            c2.metric("Risk Score(참고)", rs_txt)
            c3.metric("R²", r2_txt, snap.get("r2_badge", ""))
            c4.metric("현재 갭(매매-전세)", _fmt(snap.get("cur_gap")))

            st.markdown("</div>", unsafe_allow_html=True)

st.caption("Last updated: {}".format(datetime.now().strftime("%Y-%m-%d %H:%M")))
