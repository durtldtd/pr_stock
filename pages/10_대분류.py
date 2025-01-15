import streamlit as st
import pandas as pd
import plotly.express as px
from main import get_combined_sampled_data  # 메인 코드에서 함수 가져오기



# 페이지 설정
st.set_page_config(page_title="대분류 관련 그래프 출력", layout="wide")
st.title("📊 업종대분류 관련 정보")
st.markdown("이 페이지에서는 업종대분류에 관련된 다양한 내용을 제공합니다.")


# 캐시된 데이터 가져오기
sampled_df = get_combined_sampled_data()

if not sampled_df.empty:
    st.write("샘플링된 데이터 미리보기:")
    st.dataframe(sampled_df)
else:
    st.error("데이터를 불러올 수 없습니다.")

df= sampled_df
# 업종대분류 목록 추출 및 선택
unique_main_categories = df["card_tpbuz_nm_1"].dropna().unique()
selected_category = st.selectbox("관심 있는 업종 대분류를 선택하세요:", sorted(unique_main_categories))
# 선택한 업종중분류로 데이터 필터링
filtered_df = df[df["card_tpbuz_nm_1"] == selected_category]
st.subheader(f"선택한 업종: {selected_category}")
