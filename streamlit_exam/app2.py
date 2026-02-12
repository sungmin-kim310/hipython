import streamlit as st

# ----------------------------
# UI: 환경 상태 미니 대시보드
# 사용 함수: st.set_page_config, st.title, st.caption, st.columns, st.metric, st.divider
# ----------------------------

st.set_page_config(page_title="환경 상태 대시보드", layout="centered")

st.title("🌿 환경 상태 미니 대시보드")
st.caption("오늘의 온도와 공기질을 한눈에 확인합니다.")
st.divider()

# 가로 2개 카드 레이아웃
col1, col2 = st.columns(2)

# (예시 데이터) 필요하면 여기만 바꿔서 연습
temp_value = "35°C"
temp_delta = "+3°C"          # +면 상승, -면 하락

air_value = "좋음"
air_delta = "-30"            # 예: 수치가 줄어 좋다는 의미로 inverse 사용

with col1:
    st.metric(
        label="오늘의 날씨(온도)",
        value=temp_value,
        delta=temp_delta,
        # delta_color 기본값: normal (증가=초록, 감소=빨강)
    )

with col2:
    st.metric(
        label="오늘의 미세먼지",
        value=air_value,
        delta=air_delta,
        delta_color="inverse"  # 감소=초록, 증가=빨강 (미세먼지는 낮을수록 좋다고 가정)
    )
