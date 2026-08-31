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
    df = pd.read_csv(url, encoding="cp949")

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

    # 연도별 평균기온 계산
    yearly_temp = (
        df.groupby("연도")["평균기온"]
        .mean()
        .reset_index()
    )

    return df, yearly_temp


try:
    df, yearly_temp = load_data()

    # 데이터 정보 표시
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
        linewidth=1.8
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

    st.pyplot(fig)

    # 변화량 계산
    first_temp = yearly_temp.iloc[0]["평균기온"]
    last_temp = yearly_temp.iloc[-1]["평균기온"]
    change = last_temp - first_temp

    st.subheader("🔎 기온 변화 요약")

    if change > 0:
        st.success(
            f"{yearly_temp.iloc[0]['연도']}년부터 "
            f"{yearly_temp.iloc[-1]['연도']}년까지 "
            f"연평균 기온은 약 {change:.2f}℃ 상승했습니다."
        )
    else:
        st.info(
            f"전체 기간 동안 연평균 기온은 약 "
            f"{abs(change):.2f}℃ 변화했습니다."
        )

    # 데이터 보기
    with st.expander("연도별 평균기온 데이터 보기"):
        st.dataframe(
            yearly_temp,
            use_container_width=True
        )

except Exception as e:
    st.error("데이터를 불러오는 중 오류가 발생했습니다.")
    st.write(e)
