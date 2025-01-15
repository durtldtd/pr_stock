import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import matplotlib 
from io import BytesIO 
import pandas as pd
import os
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title="메인", layout="wide")
st.title("Welcome!")
st.markdown("""
            ## 🏢 창업을 꿈꾸는 당신을 위한 정보 플랫폼
            
            창업을 준비하고 계신가요? 
            본 홈페이지는 예비 창업자들이 자신만의 비즈니스를 계획하고 실행하는 데 필요한 데이터와 인사이트를 제공합니다. 
            
            ### 🌟 제공 기능
            
            **1. 업종 분석**
            - **대분류 정보 제공**: 주요 업종에 대한 전반적인 데이터를 제공
              - **차트 및 그래프**: 업종별 매출, 소비자 트렌드, 시간대별 매출 등을 시각적으로 이해하기 쉽게 제공합니다.
            - **소분류 정보 제공**: 특정 업종 내 세부 카테고리에 대한 상세 데이터를 제공합니다. 
              - **상세 통계**: 소비자 성향, 연령대별 소비 패턴 등 창업자에게 실질적인 도움이 되는 정보를 확인하세요.
            **2. 맞춤형 시각화 도구**
            - 입력하신 데이터와 조건을 바탕으로, 업종 및 지역별 데이터를 커스터마이즈하여 시각화할 수 있습니다.
              - **시간 단위 분석**: 일별, 주별, 월별 데이터를 선택하여 비즈니스 성과를 예측.
              - **트렌드 비교**: 다양한 카테고리를 한눈에 비교.
            **3. 추가 개발 예정 기능**
            - **지역별 소비 분석**: 창업 예정 지역의 소비자 데이터를 통해 시장성을 확인하세요.
            - **추천 업종**: 소비 패턴 및 데이터 기반으로 적합한 업종을 추천해 드립니다.
            - **투자 전략 도구**: 창업 초기 자본 투자 계획 수립을 돕는 시뮬레이션 도구.
            ### 🎯 당신의 성공적인 창업을 응원합니다!
            데이터를 활용한 철저한 시장 분석으로, 창업의 첫걸음을 내딛어 보세요. 
            제공되는 정보를 통해 창업 계획을 더욱 구체화하고, 성공적인 비즈니스로 발전시킬 수 있습니다.
            함께 성장하는 미래를 만들어 봅시다! 🚀
            오류 문의: dahee7446@gmail.com
            """)
# 지역 선택 기능 추가
# 지역 선택 기능 추가
st.sidebar.header("지역 선택")
regions = ['포천']
selected_region = st.sidebar.selectbox("창업 예정 지역을 선택하세요", regions)

# 파일 읽기 함수 (캐싱)
@st.cache_data
def load_csv_file(file_path):
    """CSV 파일을 읽어오는 함수"""
    try:
        df = pd.read_csv(file_path, encoding="utf-8")
        return df
    except Exception as e:
        st.write("에러 발생:", e)
        return None

# 데이터 병합 및 샘플링 함수 (캐싱)
@st.cache_data
def get_combined_sampled_data():
    """2023년 데이터를 병합하고 샘플링"""
    # 파일 경로 템플릿
    base_url = 'https://woori-fisa-bucket.s3.ap-northeast-2.amazonaws.com/fisa04-card/tbsh_gyeonggi_day_2023{}_pochun.csv'

    combined_df = pd.DataFrame()

    # 202301부터 202312까지 반복 처리
    for month in range(1, 13):
        month_str = f"{month:02d}"  # 월을 두 자리로 포맷팅
        file_path = base_url.format(month_str)

        df = load_csv_file(file_path)
        if df is not None:
            combined_df = pd.concat([combined_df, df], ignore_index=True)

    # 데이터 샘플링
    if not combined_df.empty:
        sample_ratio = 0.01  # 샘플링 비율 (1%)
        sampled_df = combined_df.sample(frac=sample_ratio, random_state=42)
        return sampled_df
    else:
        return pd.DataFrame()  # 빈 데이터프레임 반환


# 메인 함수
def main():
    st.title("CSV 파일 병합 및 데이터 미리보기")

    # 병합 및 샘플링된 데이터 가져오기
    with st.spinner("데이터 로드 중..."):
        sampled_df = get_combined_sampled_data()

    # 데이터 표시
    if not sampled_df.empty:
        st.write("샘플링된 데이터 미리보기:")
        st.dataframe(sampled_df.head(50))
    else:
        st.error("데이터를 로드할 수 없습니다.")

    st.success("모든 작업 완료!")


if __name__ == "__main__":
    main()

