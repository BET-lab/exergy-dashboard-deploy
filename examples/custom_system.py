"""예시: 커스텀 시스템, 평가 함수, 시각화 추가

이 스크립트는 새로운 시스템과 시각화를 등록하는 간단한 예시입니다.
'TEST' 모드에 간단한 열교환기 시스템을 추가합니다.
"""

from exergy_dashboard.system import register_system
from exergy_dashboard.evaluation import registry as eval_registry
from exergy_dashboard.visualization import registry as viz_registry
from exergy_dashboard.visualization import new_viz_format
import streamlit as st
import pandas as pd
import altair as alt


# 1. 간단한 열교환기 시스템 정의
simple_heat_exchanger = {
    'display': {
        'title': '간단한 열교환기',
        'icon': '🔄',
    },
    'parameters': {
        'T_hot_in': {
            'explanation': {'EN': 'Hot Side Inlet Temperature', 'KR': '고온측 입구 온도'},
            'latex': r'$T_{hot,in}$',
            'default': 80.0,
            'range': [0, 100],
            'unit': '℃',
            'step': 1.0,
            'category': '온도',
        },
        'T_hot_out': {
            'explanation': {'EN': 'Hot Side Outlet Temperature', 'KR': '고온측 출구 온도'},
            'latex': r'$T_{hot,out}$',
            'default': 40.0,
            'range': [0, 100],
            'unit': '℃',
            'step': 1.0,
            'category': '온도',
        },
        'T_cold_in': {
            'explanation': {'EN': 'Cold Side Inlet Temperature', 'KR': '저온측 입구 온도'},
            'latex': r'$T_{cold,in}$',
            'default': 20.0,
            'range': [0, 100],
            'unit': '℃',
            'step': 1.0,
            'category': '온도',
        },
        'T_cold_out': {
            'explanation': {'EN': 'Cold Side Outlet Temperature', 'KR': '저온측 출구 온도'},
            'latex': r'$T_{cold,out}$',
            'default': 60.0,
            'range': [0, 100],
            'unit': '℃',
            'step': 1.0,
            'category': '온도',
        },
        'flow_rate': {
            'explanation': {'EN': 'Flow Rate', 'KR': '유량'},
            'latex': r'$\dot{m}$',
            'default': 1.0,
            'range': [0, 10],
            'unit': 'kg/s',
            'step': 0.1,
            'category': '유량',
        },
    }
}


# 2. 시스템 등록 함수
def register_test_systems():
    """테스트용 시스템 등록 - 아주 간단한 버전"""
    # 시스템 등록
    register_system('TEST', 'SHE', simple_heat_exchanger)
    print("SHE 시스템이 TEST 모드에 등록되었습니다.")


# 3. 간단한 엑서지 계산 함수
@eval_registry.register('TEST', 'SHE')
def evaluate_she(params):
    """간단한 열교환기의 엑서지 계산"""
    # 파라미터 추출
    T_hot_in = params['T_hot_in']
    T_hot_out = params['T_hot_out']
    T_cold_in = params['T_cold_in']
    T_cold_out = params['T_cold_out']
    flow_rate = params['flow_rate']
    
    # 물의 비열 (kJ/kg-K)
    cp = 4.18
    
    # 열전달량 계산
    Q = flow_rate * cp * (T_hot_in - T_hot_out)  # 열전달량 (kW)
    
    # 간단한 효율 계산
    efficiency = (T_cold_out - T_cold_in) / (T_hot_in - T_cold_in) * 100  # 효율 (%)
    
    # 결과 반환
    return {
        'heat_transfer': Q,           # 열전달량 (kW)
        'efficiency': efficiency,      # 효율 (%)
        'hot_delta_T': T_hot_in - T_hot_out,  # 고온측 온도차 (℃)
        'cold_delta_T': T_cold_out - T_cold_in,  # 저온측 온도차 (℃)
    }


# 4. 모드별 시각화 등록
@viz_registry.register('TEST', '온도 그래프')
@new_viz_format
def plot_temperature(systems_data, selected_systems):
    """열교환기 온도 시각화 - TEST 모드 전용"""
    # 첫 번째 선택된 시스템에 대해서만 시각화 수행
    if not selected_systems:
        st.write("시스템을 선택해주세요.")
        return

    system_name = selected_systems[0]
    if system_name not in systems_data:
        st.write(f"시스템 '{system_name}'의 데이터가 없습니다.")
        return
        
    # 선택된 시스템의 파라미터와 변수 가져오기
    system = systems_data[system_name]
    params = system['params']
    variables = system['variables']
    
    # 데이터 준비
    data = [
        {'위치': '입구', '유형': '고온측', '온도': params['T_hot_in']},
        {'위치': '출구', '유형': '고온측', '온도': params['T_hot_out']},
        {'위치': '입구', '유형': '저온측', '온도': params['T_cold_in']},
        {'위치': '출구', '유형': '저온측', '온도': params['T_cold_out']},
    ]
    
    # 차트 생성
    chart = alt.Chart(pd.DataFrame(data)).mark_line().encode(
        x='위치:N',
        y='온도:Q',
        color='유형:N',
        tooltip=['유형', '위치', '온도']
    ).properties(
        title='열교환기 입출구 온도',
        width=400,
        height=300
    )
    
    st.altair_chart(chart, use_container_width=True)


@viz_registry.register('TEST', '열전달 정보')
@new_viz_format
def show_heat_transfer_info(systems_data, selected_systems):
    """열전달 정보 표시 - TEST 모드 전용"""
    # 첫 번째 선택된 시스템에 대해서만 시각화 수행
    if not selected_systems:
        st.write("시스템을 선택해주세요.")
        return

    system_name = selected_systems[0]
    if system_name not in systems_data:
        st.write(f"시스템 '{system_name}'의 데이터가 없습니다.")
        return
        
    # 선택된 시스템의 파라미터와 변수 가져오기
    system = systems_data[system_name]
    params = system['params']
    variables = system['variables']
    
    st.write("### 열전달 정보")
    
    # 열전달량 표시
    st.metric(
        label="열전달량", 
        value=f"{variables['heat_transfer']:.2f} kW"
    )
    
    # 효율 표시
    st.metric(
        label="열교환 효율", 
        value=f"{variables['efficiency']:.1f}%"
    )
    
    # 온도차 정보
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label="고온측 온도차", 
            value=f"{variables['hot_delta_T']:.1f}°C"
        )
    with col2:
        st.metric(
            label="저온측 온도차", 
            value=f"{variables['cold_delta_T']:.1f}°C"
        )


# 시스템 등록 실행
if __name__ == "__main__":
    register_test_systems() 