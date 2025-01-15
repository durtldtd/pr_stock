import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from main import get_combined_sampled_data  # 메인 코드에서 함수 가져오기

# 페이지 설정 (스크립트의 첫 번째 명령어로 이동)
st.set_page_config(page_title="대분류 및 소분류 관련 그래프 출력", layout="wide")

# 페이지 제목
st.title("📊 업종대분류 및 소분류 관련 정보")
st.markdown("이 페이지에서는 업종대분류 및 소분류에 관련된 다양한 내용을 제공합니다.")

# 캐시된 데이터 가져오기
sampled_df = get_combined_sampled_data()

if not sampled_df.empty:
    st.write("샘플링된 데이터 미리보기:")
    st.dataframe(sampled_df)
else:
    st.error("데이터를 불러올 수 없습니다.")
    st.stop()

df = sampled_df

# 데이터 컬럼 존재 여부 확인
# 1. 'age' 컬럼 존재 여부 확인
if 'age' in df.columns:
    st.write("'age' 컬럼이 데이터프레임에 존재합니다.")
else:
    st.error("'age' 컬럼이 데이터프레임에 존재하지 않습니다.")

# 2. 'ta_ymd' 컬럼 존재 여부 확인
if 'ta_ymd' in df.columns:
    st.write("'ta_ymd' 컬럼이 데이터프레임에 존재합니다.")
else:
    st.error("'ta_ymd' 컬럼이 데이터프레임에 존재하지 않습니다.")

# 3. 'card_tpbuz_nm_1' 컬럼 존재 여부 확인
if 'card_tpbuz_nm_1' in df.columns:
    st.write("'card_tpbuz_nm_1' 컬럼이 데이터프레임에 존재합니다.")
else:
    st.error("'card_tpbuz_nm_1' 컬럼이 데이터프레임에 존재하지 않습니다.")

# 4. 'card_tpbuz_nm_2' 컬럼 존재 여부 확인
if 'card_tpbuz_nm_2' in df.columns:
    st.write("'card_tpbuz_nm_2' 컬럼이 데이터프레임에 존재합니다.")
else:
    st.error("'card_tpbuz_nm_2' 컬럼이 데이터프레임에 존재하지 않습니다.")

# 대분류 관련 정보
st.header("📊 업종대분류 관련 정보")
# 대분류 관련 데이터 처리 및 시각화
unique_main_categories = df["card_tpbuz_nm_1"].dropna().unique()
selected_main = st.selectbox("비교하고 싶은 업종 대분류를 선택하세요:", sorted(unique_main_categories))

# 소분류 관련 정보
st.header("📊 업종소분류 관련 정보")
# 1. 해당 대분류에 속하는 소분류 목록 추출 및 선택 (최대 3개)
available_subcategories = df[df["card_tpbuz_nm_1"] == selected_main]["card_tpbuz_nm_2"].dropna().unique()
selected_subcategories = st.multiselect(
    f"{selected_main}에 속하는 업종 소분류를 최대 3개 선택하세요:",
    options=sorted(available_subcategories),
    default=[sorted(available_subcategories)[0]] if len(available_subcategories) > 0 else None,
    max_selections=3
)

# 최소 1개 이상 선택 확인
if not selected_subcategories:
    st.warning("적어도 하나의 업종 소분류를 선택해야 합니다.")
    st.stop()

# 선택한 업종 소분류로 데이터 필터링
filtered_df = df[df["card_tpbuz_nm_2"].isin(selected_subcategories) & (df["card_tpbuz_nm_1"] == selected_main)].copy()

st.subheader(f"선택한 업종 대분류: {selected_main}")
st.write(f"선택한 업종 소분류: {', '.join(selected_subcategories)}")

# 데이터 전처리: 날짜 처리
filtered_df['ta_ymd'] = pd.to_datetime(filtered_df['ta_ymd'], format='%Y%m%d', errors='coerce')
filtered_df['year_month'] = filtered_df['ta_ymd'].dt.to_period('M').astype(str)

# 1. 월별 총 매출 금액 추이 비교
monthly_sales = (
    filtered_df.groupby(['year_month', 'card_tpbuz_nm_2'])['amt']
    .sum()
    .reset_index()
)
fig1 = px.line(monthly_sales, x='year_month', y='amt', color='card_tpbuz_nm_2',
               title="선택한 업종 소분류 별 월별 총 매출 금액 추이",
               labels={'year_month': '년-월', 'amt': '매출 금액', 'card_tpbuz_nm_2': '업종 소분류'})
st.plotly_chart(fig1, use_container_width=True)

# 2. 성별 매출 비율 비교
gender_sales = (
    filtered_df.groupby(['sex', 'card_tpbuz_nm_2'])['amt']
    .sum()
    .reset_index()
)
fig2 = px.pie(gender_sales, names='sex', values='amt', color='sex',
              facet_col='card_tpbuz_nm_2', 
              title="선택한 업종 소분류 별 성별 매출 비율",
              color_discrete_map={'M': 'blue', 'F': 'pink'})
st.plotly_chart(fig2, use_container_width=True)

# 3. 연령대별 매출 비교
if 'age' in filtered_df.columns:
    # bins와 labels의 길이가 일치하도록 수정
    filtered_df['age_group'] = pd.cut(filtered_df['age'], bins=[0, 20, 30, 40, 50, 60],
                                  labels=['20대 이하', '30대', '40대', '50대', '60대 이상'], right=False)
    age_sales = (
        filtered_df.groupby(['age_group', 'card_tpbuz_nm_2'])['amt']
        .sum()
        .reset_index()
    )
    fig3 = px.bar(age_sales, x='age_group', y='amt', color='age_group',
                  title="선택한 업종 소분류 별 연령대별 매출 금액 비교",
                  labels={'age_group': '연령대', 'amt': '매출 금액', 'card_tpbuz_nm_2': '업종 소분류'},
                  facet_col='card_tpbuz_nm_2')
    st.plotly_chart(fig3, use_container_width=True)
#4
if 'ta_ymd' in filtered_df.columns:
    # 날짜 형식으로 변환 (필요한 경우)
    filtered_df['ta_ymd'] = pd.to_datetime(filtered_df['ta_ymd'], errors='coerce')

    # 요일 추출 (숫자형 요일을 한글로 매핑)
    filtered_df['weekday'] = filtered_df['ta_ymd'].dt.dayofweek + 1  # 월요일을 1로 설정 (0=월요일, 1=화요일, ...)

    # 요일 매핑 (숫자형 요일을 한글로 매핑)
    day_labels = {
        1: '월', 2: '화', 3: '수', 4: '목', 5: '금', 6: '토', 7: '일',  # 숫자형 매핑
    }

    # 숫자형 요일을 한글로 매핑
    filtered_df['weekday'] = filtered_df['weekday'].map(day_labels)

    # 요일별 매출 금액 합산
    weekday_sales = (
        filtered_df.groupby(['weekday', 'card_tpbuz_nm_2'])['amt']
        .sum()
        .reset_index()
    )

    # 요일 순서대로 정렬 (월, 화, 수, 목, 금, 토, 일)
    weekday_order = ['월', '화', '수', '목', '금', '토', '일']

    # 요일을 Categorical로 변환하여 순서를 맞춤
    weekday_sales['weekday'] = pd.Categorical(weekday_sales['weekday'], categories=weekday_order, ordered=True)

    # 데이터 정렬
    weekday_sales = weekday_sales.sort_values('weekday')

    # 그래프 그리기
    fig4 = px.bar(weekday_sales, x='weekday', y='amt', color='weekday',
                  title="선택한 업종 소분류 별 요일별 매출 금액 비교",
                  labels={'weekday': '요일', 'amt': '매출 금액', 'card_tpbuz_nm_2': '업종 소분류'},
                  facet_col='card_tpbuz_nm_2')
    st.plotly_chart(fig4, use_container_width=True)




# 5. 시간대별 데이터 집계 (선과 막대) -> 서로 다른 두가지 데이터 비교
# 시간대별 레이블 정의
hour_labels = {
    '01': '00:00~06:59', '02': '07:00~08:59', '03': '09:00~10:59',
    '04': '11:00~12:59', '05': '13:00~14:59', '06': '15:00~16:59',
    '07': '17:00~18:59', '08': '19:00~20:59', '09': '21:00~22:59',
    '10': '23:00~23:59'
}

# 5. 시간대별 데이터 집계 (선과 막대) -> 서로 다른 두가지 데이터 비교
if 'ta_ymd' in filtered_df.columns:
    # 'ta_ymd' 컬럼을 datetime 형식으로 변환
    filtered_df['ta_ymd'] = pd.to_datetime(filtered_df['ta_ymd'], errors='coerce')

    # 시간 추출 (1~10만 있음)
    filtered_df['hour'] = filtered_df['ta_ymd'].dt.hour

    # 시간대별 레이블을 'hour' 컬럼에 매핑
    filtered_df['hour_label'] = filtered_df['hour'].astype(str).map(hour_labels)

    # 'hour_label' 값이 비어있는 경우 처리
    if filtered_df['hour_label'].isnull().any():
        st.warning("시간대 레이블이 적용되지 않은 데이터가 있습니다.")
        filtered_df = filtered_df.dropna(subset=['hour_label'])  # 비어있는 hour_label 제거

    # 선택한 업종 소분류별 시간대별 매출 금액 집계
    hour_sales = (
        filtered_df.groupby(['hour_label', 'card_tpbuz_nm_2'])['amt']
        .sum()
        .reset_index()
    )

    # hour_sales가 비어있는지 확인
    if hour_sales.empty:
        st.warning("시간대별 매출 데이터가 없습니다.")
    else:
        # 그래프 그리기 (시간대별 매출 금액을 바 차트로 시각화)
        fig5 = px.bar(hour_sales, x='hour_label', y='amt', color='card_tpbuz_nm_2', barmode='group',
                      title="선택한 업종 소분류 별 시간대별 매출 금액",
                      labels={'hour_label': '시간대', 'amt': '매출 금액', 'card_tpbuz_nm_2': '업종 소분류'})

        st.plotly_chart(fig5, use_container_width=True)
