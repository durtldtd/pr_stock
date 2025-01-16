import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from main import get_combined_sampled_data  # 메인 코드에서 함수 가져오기

st.set_page_config(page_title="업종 대분류 및 소분류 분석", layout="wide")
st.title(":bar_chart: 업종 분석 도구")
st.markdown(
    """
    선택한 업종의 대분류 및 소분류에 대한 다양한 데이터를 확인하고 분석할 수 있습니다.
    데이터를 시각적으로 이해하기 쉽게 정리하였습니다.
    """
)

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
st.markdown("## 🔍 데이터 필터링")
# 대분류 관련 데이터 처리 및 시각화
unique_main_categories = df["card_tpbuz_nm_1"].dropna().unique()
selected_main = st.selectbox("비교하고 싶은 업종 대분류를 선택하세요:", sorted(unique_main_categories))

# 소분류 관련 정보
st.header("📊 업종소분류 관련 정보")
# 1. 해당 대분류에 속하는 소분류 목록 추출 및 선택 (최대 3개)
available_subcategories = df[df["card_tpbuz_nm_1"] == selected_main]["card_tpbuz_nm_2"].dropna().unique()
selected_subcategories = st.multiselect(
    f"## 🔍 {selected_main}에 속하는 업종 소분류를 최대 3개 선택하세요:",
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
               title="📈 선택한 업종 소분류 별 월별 총 매출 금액 추이",
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
              title="🧑‍🤝‍🧑 선택한 업종 소분류 별 성별 매출 비율",
              color_discrete_map={'M': 'blue', 'F': 'pink'})
st.plotly_chart(fig2, use_container_width=True)

#3
age_mapping = {
    1: '10대 이하', 
    2: '10대', 
    3: '20대', 
    4: '30대', 
    5: '40대', 
    6: '50대', 
    7: '60대 이상'
}

if 'age' in filtered_df.columns:
    # 연령대 매핑
    filtered_df['age_group'] = filtered_df['age'].map(age_mapping)


    # 연령대별 매출 데이터 집계
    age_sales = (
        filtered_df.groupby(['age_group', 'card_tpbuz_nm_2'])['amt']
        .sum()
        .reset_index()
    )

    # 그래프 생성
    fig3 = px.bar(
        age_sales, 
        x='age_group', 
        y='amt', 
        color='age_group',
        title="👥 선택한 업종 소분류 별 연령대별 매출 금액 비교",
        labels={'age_group': '연령대', 'amt': '매출 금액', 'card_tpbuz_nm_2': '업종 소분류'},
        facet_col='card_tpbuz_nm_2'
    )
    st.plotly_chart(fig3, use_container_width=True)

else:
    st.write("데이터프레임에 'age' 열이 존재하지 않습니다.")


    
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
                  title="📅 선택한 업종 소분류 별 요일별 매출 금액 비교",
                  labels={'weekday': '요일', 'amt': '매출 금액', 'card_tpbuz_nm_2': '업종 소분류'},
                  facet_col='card_tpbuz_nm_2')
    st.plotly_chart(fig4, use_container_width=True)
   # 제품 & 성별 매출
st.header("🔍  제품 & 성별 매출")
category = st.multiselect(
    "분석할 업종 소분류를 선택하세요:",
    options=df["card_tpbuz_nm_2"].unique(),
    default=df["card_tpbuz_nm_2"].unique()[:3]  # 기본적으로 처음 3개 선택
)

if not category:
    st.warning("적어도 하나의 업종 소분류를 선택해야 합니다.")
    st.stop()

grouped_data = df.loc[df['card_tpbuz_nm_2'].isin(category)].groupby(['card_tpbuz_nm_2', 'sex'])['amt'].sum().reset_index()
products = grouped_data['card_tpbuz_nm_2'].unique()
fig_gender = make_subplots(
    rows=1,
    cols=len(products),
    subplot_titles=products,
    specs=[[{'type': 'domain'}] * len(products)]
)

for i, product in enumerate(products):
    product_data = grouped_data[grouped_data['card_tpbuz_nm_2'] == product]
    fig_gender.add_trace(
        go.Pie(
            labels=product_data['sex'],
            values=product_data['amt'],
            name=product,
            marker=dict(
                colors=['lightblue' if s == 'M' else 'lightpink' for s in product_data['sex']]
            )
        ),
        row=1,
        col=i + 1
    )

fig_gender.update_layout(
    title="제품별 성별 매출 비율",
    showlegend=True,
    legend_title_text='성별',
    height=400,
    width=250 * len(products)
)
st.plotly_chart(fig_gender, use_container_width=False)

# 제품 & 나이대별 매출
st.header("🔍  제품 & 나이대별 매출")
grouped_data2 = df.loc[df['card_tpbuz_nm_2'].isin(category)].groupby(['card_tpbuz_nm_2', 'age'])['amt'].sum().reset_index()
grouped_data2['age'] = grouped_data2['age'].astype(str)
products_age = grouped_data2['card_tpbuz_nm_2'].unique()

color_map = {
    '1': 'lightblue',
    '2': 'blue',
    '3': 'green',
    '4': 'orange',
    '5': 'red',
    '6': 'purple',
    '7': 'pink',
    '8': 'yellow',
    '9': 'brown',
    '10': 'grey',
    '11': 'cyan'
}

fig_age = make_subplots(
    rows=1,
    cols=len(products_age),
    subplot_titles=products_age,
    specs=[[{'type': 'domain'}] * len(products_age)]
)

for i, product in enumerate(products_age):
    product_data = grouped_data2[grouped_data2['card_tpbuz_nm_2'] == product]
    colors = [color_map.get(age, 'gray') for age in product_data['age']]
    fig_age.add_trace(
        go.Pie(
            labels=product_data['age'],
            values=product_data['amt'],
            name=product,
            marker=dict(colors=colors)
        ),
        row=1,
        col=i + 1
    )

fig_age.update_layout(
    title="제품별 나이대별 매출 비율",
    showlegend=True,
    height=400,
    width=250 * len(products_age),
)
st.plotly_chart(fig_age, use_container_width=False)
