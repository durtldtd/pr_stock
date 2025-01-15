import streamlit as st
import pandas as pd
import plotly.express as px
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
age_sales = (
    filtered_df.groupby(['age', 'card_tpbuz_nm_2'])['amt']
    .sum()
    .reset_index()
)
age_labels = {
    '01': '0-9세', '02': '10-19세', '03': '20-29세', '04': '30-39세',
    '05': '40-49세', '06': '50-59세', '07': '60-69세', '08': '70-79세',
    '09': '80-89세', '10': '90-99세', '11': '100세 이상'
}
age_sales['age_label'] = age_sales['age'].map(age_labels)
fig3 = px.bar(age_sales, x='age_label', y='amt', color='card_tpbuz_nm_2', barmode='group',
              title="선택한 업종 소분류 별 연령대별 매출 금액",
              labels={'age_label': '연령대', 'amt': '매출 금액', 'card_tpbuz_nm_2': '업종 소분류'})
st.plotly_chart(fig3, use_container_width=True)

# 4. 요일별 매출 비교
day_labels = {
    '01': '월', '02': '화', '03': '수', '04': '목', '05': '금', '06': '토', '07': '일'
}
filtered_df['day_label'] = filtered_df['day'].map(day_labels)
day_sales = (
    filtered_df.groupby(['day_label', 'card_tpbuz_nm_2'])['amt']
    .sum()
    .reset_index()
)
fig4 = px.bar(day_sales, x='day_label', y='amt', color='card_tpbuz_nm_2', barmode='group',
              title="선택한 업종 소분류 별 요일별 매출 금액",
              labels={'day_label': '요일', 'amt': '매출 금액', 'card_tpbuz_nm_2': '업종 소분류'})
st.plotly_chart(fig4, use_container_width=True)

# 5. 시간대별 매출 비교
hour_labels = {
    '01': '00:00~06:59', '02': '07:00~08:59', '03': '09:00~10:59',
    '04': '11:00~12:59', '05': '13:00~14:59', '06': '15:00~16:59',
    '07': '17:00~18:59', '08': '19:00~20:59', '09': '21:00~22:59',
    '10': '23:00~23:59'
}
filtered_df['hour_label'] = filtered_df['hour'].map(hour_labels)
hour_sales = (
    filtered_df.groupby(['hour_label', 'card_tpbuz_nm_2'])['amt']
    .sum()
    .reset_index()
)
fig5 = px.bar(hour_sales, x='hour_label', y='amt', color='card_tpbuz_nm_2', barmode='group',
              title="선택한 업종 소분류 별 시간대별 매출 금액",
              labels={'hour_label': '시간대', 'amt': '매출 금액', 'card_tpbuz_nm_2': '업종 소분류'})
st.plotly_chart(fig5, use_container_width=True)