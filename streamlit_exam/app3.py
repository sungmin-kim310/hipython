import streamlit as st
import pandas as pd
import numpy as np
import random

# ---------------------------
# 기본 설정
# ---------------------------
st.set_page_config(page_title="Tiny Vibe Dashboard", page_icon="🐾", layout="wide")

# ---------------------------
# 미니멀 + 귀여운 CSS (초보자도 유지보수 쉬움)
# ---------------------------
st.markdown("""
<style>
.main .block-container {max-width: 1100px; padding-top: 1rem;}
.card {
  background: #fff;
  border: 1px solid #eee;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 8px 18px rgba(0,0,0,0.06);
}
.badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.8rem;
  background: #f3f4f6;
  margin-bottom: 10px;
}
.mini-note {color:#6b7280; font-size:0.9rem;}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# 사이드바: 컨트롤 센터
# ---------------------------
st.sidebar.title("🎛 컨트롤 센터")
page = st.sidebar.radio("이동", ["메인페이지", "분석보고서", "설정"])

st.sidebar.divider()
show_fun = st.sidebar.checkbox("재미 요소 켜기", value=True)
compact_mode = st.sidebar.checkbox("컴팩트 모드", value=True)

if st.sidebar.button("✨ 반짝 효과"):
    st.snow()

# ---------------------------
# 상단 헤더 (큰 이미지 대신 작은 스티커 이미지)
# ---------------------------
left, right = st.columns([1, 5])

with left:
    # 작은 이미지(스티커처럼)
    st.image(
        "https://images.unsplash.com/photo-1517849845537-4d257902454a",
        width=80
    )

with right:
    st.title("🐾 Tiny Vibe Dashboard")
    st.caption("큰 배너 없이도 ‘전문적 + 귀여움 + 쉬운 조작’을 목표로 만든 미니 대시보드")

st.divider()

# ---------------------------
# 공통: 더미 데이터(연습용)
# ---------------------------
np.random.seed(42)
df = pd.DataFrame({
    "날짜": pd.date_range("2025-01-01", periods=30),
    "방문자수": np.random.randint(1000, 5000, 30),
    "활성사용자수": np.random.randint(200, 1200, 30)
})

# ---------------------------
# 메인페이지
# ---------------------------
if page == "메인페이지":
    st.markdown("### ✅ 오늘의 상태 요약")

    # KPI 카드 2개
    c1, c2, c3 = st.columns([2, 2, 3] if not compact_mode else [1, 1, 1])

    visitors_today = int(df["방문자수"].iloc[-1])
    active_today = int(df["활성사용자수"].iloc[-1])

    with c1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="badge">👣 Traffic</div>', unsafe_allow_html=True)
        st.metric("방문자수(오늘)", f"{visitors_today:,}", "+4%")
        st.markdown('<div class="mini-note">오늘 유입이 어떤지 빠르게 확인</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="badge">🔥 Active</div>', unsafe_allow_html=True)
        st.metric("활성 사용자(오늘)", f"{active_today:,}", "-2%", delta_color="inverse")
        st.markdown('<div class="mini-note">활성도 변화는 inverse로 표현</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # 🎯 창의적 요소: "오늘의 미션 카드"
    with c3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="badge">🎯 오늘의 미션</div>', unsafe_allow_html=True)

        missions = [
            "방문자수가 높은 날의 원인 1개 적어보기",
            "활성 사용자수를 올릴 아이디어 1개 스케치하기",
            "가장 반응 좋은 날짜를 찾아 메모하기",
            "차트에서 급등/급락 구간 1개 표시해보기"
        ]
        st.write("✅ " + random.choice(missions))
        st.caption("연습용 기능: 새로고침하면 미션이 바뀝니다.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # 🧪 재미 요소: '무드 바' (슬라이더로 상태 바꾸기)
    if show_fun:
        st.markdown("### 🧪 무드 조절 바")
        mood = st.slider("오늘의 대시보드 무드", 0, 100, 65)

        if mood >= 80:
            st.success("오늘은 아주 반짝이는 날 ✨😄")
        elif mood >= 50:
            st.info("무난하고 안정적인 흐름 🙂")
        else:
            st.warning("조용한 날이에요. 실험하기 딱 좋아요 🧪")

        if st.button("🎲 랜덤 응원 받기"):
            cheers = [
                "오늘의 작은 개선이 내일의 큰 성과! 🚀",
                "기록하면 성장합니다 📌",
                "데이터는 거짓말을 안 해요 📊",
                "꾸준함이 제일 강력해요 💪"
            ]
            st.toast(random.choice(cheers), icon="🐾")

# ---------------------------
# 분석보고서
# ---------------------------
elif page == "분석보고서":
    st.markdown("### 📈 분석보고서")

    tab1, tab2, tab3 = st.tabs(["📈 차트", "📋 데이터", "🧩 인사이트"])

    with tab1:
        st.line_chart(df.set_index("날짜")[["방문자수", "활성사용자수"]])

    with tab2:
        st.dataframe(df, use_container_width=True)

    # 🧩 창의적 요소: "자동 인사이트 카드" (아주 쉬운 통계)
    with tab3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="badge">🧩 자동 인사이트</div>', unsafe_allow_html=True)

        peak_day = df.loc[df["방문자수"].idxmax(), "날짜"]
        peak_value = int(df["방문자수"].max())

        low_day = df.loc[df["방문자수"].idxmin(), "날짜"]
        low_value = int(df["방문자수"].min())

        st.write(f"📌 방문자 최고: **{peak_day.date()}** / **{peak_value:,}명**")
        st.write(f"📌 방문자 최저: **{low_day.date()}** / **{low_value:,}명**")
        st.caption("연습용: 아주 간단한 통계로도 ‘보고서 느낌’을 낼 수 있어요.")
        st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# 설정
# ---------------------------
else:
    st.markdown("### ⚙ 설정")
    theme = st.selectbox("테마 선택(연습용)", ["Light", "Soft Blue", "Mint"])
    refresh = st.slider("새로고침 주기(초, 연습용)", 5, 60, 10)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="badge">🛠 현재 설정</div>', unsafe_allow_html=True)
    st.write("테마:", theme)
    st.write("새로고침:", f"{refresh}초")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("저장"):
        st.success("저장 완료 ✅")
