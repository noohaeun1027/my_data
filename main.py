import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 페이지 설정
st.set_page_config(
    page_title="서울 100년 기온 변화",
    page_icon="🌡️",
    layout="wide"
)

# 제목
st.title("🌡️ 서울의 100년 연평균 기온 변화")
st.write("서울의 일별 기온 데이터를 이용해 연도별 평균기온 변화를 확인합니다.")

# 데이터 주소
url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"


@st.cache_data
def load_data():
    # CSV 파일 읽기
    # GitHub 파일은 UTF-8 인코딩 사용
    df = pd.read_csv(url, encoding="utf-8")

    # 열 이름 공백 제거
    df.columns = df.columns.str.strip()

    # 날짜를 날짜 형식으로 변환
    df["날짜"] = pd.to_datetime(df["날짜"])

    # 연도 열 만들기
    df["연도"] = df["날짜"].dt.year

    # 평균기온을 숫자로 변환
    df["평균기온"] = pd.to_numeric(
        df["평균기온"],
        errors="coerce"
    )

    # 결측값 제거
    df = df.dropna(subset=["평균기온"])

    # 연도별 평균기온 계산
    yearly_temp = (
        df.groupby("연도")["평균기온"]
        .mean()
        .reset_index()
    )

    return df, yearly_temp


try:
    # 데이터 불러오기
    df, yearly_temp = load_data()

    # 데이터 정보
    st.subheader("📊 데이터 정보")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "시작 연도",
        f"{yearly_temp['연도'].min()}년"
    )

    col2.metric(
        "마지막 연도",
        f"{yearly_temp['연도'].max()}년"
    )

    col3.metric(
        "전체 기간",
        f"{len(yearly_temp)}년"
    )

    # 그래프
    st.subheader("📈 연도별 평균기온 변화")

    fig, ax = plt.subplots(figsize=(14, 6))

    ax.plot(
        yearly_temp["연도"],
        yearly_temp["평균기온"],
        marker="o",
        markersize=2,
        linewidth=1.5
    )

    ax.set_title(
        "서울의 연평균 기온 변화",
        fontsize=18,
        fontweight="bold"
    )

    ax.set_xlabel("연도", fontsize=13)
    ax.set_ylabel("연평균 기온 (℃)", fontsize=13)

    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    # 스트림릿에 그래프 출력
    st.pyplot(fig)

    # 기온 변화량 계산
    first_temp = yearly_temp.iloc[0]["평균기온"]
    last_temp = yearly_temp.iloc[-1]["평균기온"]
    change = last_temp - first_temp

    # 변화 요약
    st.subheader("🔎 기온 변화 요약")

    st.metric(
        "전체 기간 평균기온 변화",
        f"{change:.2f}℃",
        delta=f"{change:.2f}℃"
    )

    if change > 0:
        st.success(
            f"{int(yearly_temp.iloc[0]['연도'])}년부터 "
            f"{int(yearly_temp.iloc[-1]['연도'])}년까지 "
            f"서울의 연평균 기온은 약 {change:.2f}℃ 상승했습니다."
        )
    else:
        st.info(
            f"전체 기간 동안 연평균 기온은 "
            f"약 {abs(change):.2f}℃ 변화했습니다."
        )

    # 데이터 보기
    with st.expander("📋 연도별 평균기온 데이터 보기"):
        st.dataframe(
            yearly_temp,
            use_container_width=True
        )

except Exception as e:
    st.error("데이터를 불러오는 중 오류가 발생했습니다.")
    st.exception(e)


import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go


# ---------------------------------
# 기본 설정
# ---------------------------------
st.set_page_config(
    page_title="기온 예측기",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 기온 예측기")
st.write("서울의 연평균기온을 이용해 연도에 따른 기온 변화를 살펴봅니다.")


# ---------------------------------
# 데이터 주소
# ---------------------------------
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/bb860932644270ad1199f10d3e7670e30231bce4/data/seoul.csv"


# ---------------------------------
# 데이터 불러오기
# ---------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL, encoding="utf-8")

    # 날짜 변환
    df["날짜"] = pd.to_datetime(
        df["날짜"].astype(str),
        format="%Y%m%d",
        errors="coerce"
    )

    # 평균기온 숫자로 변환
    df["평균기온"] = pd.to_numeric(
        df["평균기온"],
        errors="coerce"
    )

    # 필요한 데이터만 남기기
    df = df.dropna(subset=["날짜", "평균기온"])

    # 연도 만들기
    df["연도"] = df["날짜"].dt.year

    return df


df = load_data()


# ---------------------------------
# 2025년까지의 데이터만 사용
# ---------------------------------
df = df[df["연도"] <= 2025].copy()


# ---------------------------------
# 연도별 평균기온 계산
# 관측일수가 300일 이상인 해만 사용
# ---------------------------------
yearly = (
    df.groupby("연도")
    .agg(
        연평균기온=("평균기온", "mean"),
        관측일수=("날짜", "nunique")
    )
    .reset_index()
)

yearly = yearly[yearly["관측일수"] >= 300].copy()

yearly = yearly.sort_values("연도").reset_index(drop=True)


# ---------------------------------
# 데이터 확인
# ---------------------------------
if len(yearly) == 0:
    st.error("분석할 데이터가 없습니다.")
    st.write("날짜 형식이나 관측일수 조건을 확인해 주세요.")
    st.stop()


# ---------------------------------
# 독립 변수 만들기
# 1908년부터 지난 연수
# ---------------------------------
yearly["지난연수"] = yearly["연도"] - 1908


# ---------------------------------
# 회귀 분석
# ---------------------------------
x = yearly["지난연수"].to_numpy(dtype=float)
y = yearly["연평균기온"].to_numpy(dtype=float)

slope, intercept = np.polyfit(x, y, 1)

# 상관계수
correlation = np.corrcoef(x, y)[0, 1]


# ---------------------------------
# 회귀선의 예상값
# ---------------------------------
yearly["회귀예측기온"] = (
    slope * yearly["지난연수"] + intercept
)


# ---------------------------------
# 분석 기간 정보
# ---------------------------------
start_year = int(yearly["연도"].min())
end_year = int(yearly["연도"].max())
year_count = len(yearly)


st.subheader("📊 회귀 분석에 사용한 기간")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("사용한 해의 개수", f"{year_count}개")

with col2:
    st.metric("시작 연도", f"{start_year}년")

with col3:
    st.metric("끝 연도", f"{end_year}년")

st.write(
    "2025년 이후 데이터와 관측일수가 300일 미만인 해는 제외했습니다."
)


# ---------------------------------
# 상관계수
# ---------------------------------
st.subheader("📈 연도와 연평균기온의 관계")

st.metric(
    "상관계수",
    f"{correlation:.3f}"
)


# ---------------------------------
# 산점도 + 회귀직선
# ---------------------------------
fig = go.Figure()


# 실제 연평균기온
fig.add_trace(
    go.Scatter(
        x=yearly["연도"],
        y=yearly["연평균기온"],
        mode="markers",
        name="실제 연평균기온",
        customdata=yearly[["관측일수"]],
        hovertemplate=(
            "연도: %{x}년<br>"
            "연평균기온: %{y:.2f}℃<br>"
            "관측일수: %{customdata[0]}일"
            "<extra></extra>"
        )
    )
)


# 회귀직선
fig.add_trace(
    go.Scatter(
        x=yearly["연도"],
        y=yearly["회귀예측기온"],
        mode="lines",
        name="회귀직선",
        hovertemplate=(
            "연도: %{x}년<br>"
            "회귀값: %{y:.2f}℃"
            "<extra></extra>"
        )
    )
)


fig.update_layout(
    title="서울 연평균기온과 연도",
    xaxis_title="연도",
    yaxis_title="연평균기온 (℃)",
    xaxis=dict(
        tickmode="linear",
        dtick=10
    ),
    hovermode="x unified"
)

st.plotly_chart(fig, width="stretch")


# ---------------------------------
# 회귀식
# ---------------------------------
st.write(
    f"회귀식: 연평균기온 = "
    f"{slope:.4f} × (연도 - 1908) + {intercept:.2f}"
)

st.write(
    f"회귀선을 만든 해의 개수: {year_count}개"
    f" / 시작 연도: {start_year}년"
    f" / 끝 연도: {end_year}년"
)


# ---------------------------------
# 연도 선택
# ---------------------------------
st.subheader("🔮 연도별 예상 기온")

selected_year = st.slider(
    "예상할 연도를 선택하세요.",
    min_value=1900,
    max_value=2100,
    value=2025,
    step=1
)


# ---------------------------------
# 선택한 연도의 예상 기온
# ---------------------------------
selected_x = selected_year - 1908

predicted_temp = (
    slope * selected_x + intercept
)


st.metric(
    f"{selected_year}년 예상 연평균기온",
    f"{predicted_temp:.2f} ℃"
)


# ---------------------------------
# 1900~2100년 회귀 예측 그래프
# ---------------------------------
prediction_years = np.arange(1900, 2101)

prediction_x = prediction_years - 1908

prediction_temps = (
    slope * prediction_x + intercept
)


fig2 = go.Figure()


# 회귀선
fig2.add_trace(
    go.Scatter(
        x=prediction_years,
        y=prediction_temps,
        mode="lines",
        name="회귀직선"
    )
)


# 실제 데이터
fig2.add_trace(
    go.Scatter(
        x=yearly["연도"],
        y=yearly["연평균기온"],
        mode="markers",
        name="실제 연평균기온"
    )
)


# 선택한 연도
fig2.add_trace(
    go.Scatter(
        x=[selected_year],
        y=[predicted_temp],
        mode="markers",
        marker=dict(size=14),
        name=f"{selected_year}년 예상값",
        hovertemplate=(
            f"{selected_year}년<br>"
            f"예상 연평균기온: {predicted_temp:.2f}℃"
            "<extra></extra>"
        )
    )
)


fig2.update_layout(
    title="1900~2100년 연평균기온 예상",
    xaxis_title="연도",
    yaxis_title="예상 연평균기온 (℃)",
    xaxis=dict(
        range=[1900, 2100],
        dtick=10
    )
)

st.plotly_chart(fig2, width="stretch")

