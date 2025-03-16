"""예시: 커스텀 시스템, 평가 함수, 시각화 추가

이 스크립트는 새로운 시스템을 등록하고, 해당 시스템의 엑서지 계산 모듈을 구현하며,
시각화 도구를 추가하는 방법을 보여줍니다.

이 예시에서는 'TEST' 모드에 두 가지 시스템을 추가합니다:
1. Simple Heat Exchanger (SHE)
2. Counter Flow Heat Exchanger (CHE)
"""

from exergy_dashboard.system import register_system, get_system_template
from exergy_dashboard.evaluation import registry as eval_registry
from exergy_dashboard.visualization import registry as viz_registry
import streamlit as st
import altair as alt
import pandas as pd
import math
from typing import Dict, Any, List


# 시스템 템플릿을 전역 변수로 정의
she_system = get_system_template()
she_system['display'] = {
    'title': 'Simple Heat Exchanger',
    'icon': ':arrows_counterclockwise:',
}
she_system['parameters'] = {
    'T_h_in': {
        'explanation': {'EN': 'Hot Side Inlet Temperature', 'KR': '고온측 입구 온도'},
        'latex': r'$T_{h,in}$',
        'default': 80.0,
        'range': [0, 100],
        'unit': '℃',
        'step': 0.5,
        'category': 'hot side',
    },
    'T_h_out': {
        'explanation': {'EN': 'Hot Side Outlet Temperature', 'KR': '고온측 출구 온도'},
        'latex': r'$T_{h,out}$',
        'default': 40.0,
        'range': [0, 'T_h_in'],
        'unit': '℃',
        'step': 0.5,
        'category': 'hot side',
    },
    'T_c_in': {
        'explanation': {'EN': 'Cold Side Inlet Temperature', 'KR': '저온측 입구 온도'},
        'latex': r'$T_{c,in}$',
        'default': 20.0,
        'range': [0, 'T_h_out'],
        'unit': '℃',
        'step': 0.5,
        'category': 'cold side',
    },
    'T_c_out': {
        'explanation': {'EN': 'Cold Side Outlet Temperature', 'KR': '저온측 출구 온도'},
        'latex': r'$T_{c,out}$',
        'default': 60.0,
        'range': ['T_c_in', 'T_h_in'],
        'unit': '℃',
        'step': 0.5,
        'category': 'cold side',
    },
    'm_h': {
        'explanation': {'EN': 'Hot Side Mass Flow Rate', 'KR': '고온측 질량유량'},
        'latex': r'$\dot{m}_h$',
        'default': 1.0,
        'range': [0, 10],
        'unit': 'kg/s',
        'step': 0.1,
        'category': 'flow',
    },
    'm_c': {
        'explanation': {'EN': 'Cold Side Mass Flow Rate', 'KR': '저온측 질량유량'},
        'latex': r'$\dot{m}_c$',
        'default': 1.0,
        'range': [0, 10],
        'unit': 'kg/s',
        'step': 0.1,
        'category': 'flow',
    },
}

# Counter Flow Heat Exchanger 템플릿도 전역 변수로 정의
che_system = she_system.copy()
che_system['display'] = {
    'title': 'Counter Flow Heat Exchanger',
    'icon': ':repeat:',
}
che_system['parameters'].update({
    'UA': {
        'explanation': {'EN': 'Overall Heat Transfer Coefficient', 'KR': '총괄열전달계수'},
        'latex': r'$UA$',
        'default': 1000.0,
        'range': [0, 5000],
        'unit': 'W/K',
        'step': 10.0,
        'category': 'performance',
    },
})


# 시스템 등록 함수
def register_test_systems():
    """테스트용 시스템 등록"""
    # 시스템 등록
    register_system('TEST', 'SHE', she_system)
    register_system('TEST', 'CHE', che_system)


# 2. 엑서지 계산 모듈
@eval_registry.register('TEST', 'SHE')
def evaluate_she(params: Dict[str, float]) -> Dict[str, float]:
    """Simple Heat Exchanger 엑서지 계산
    
    단순 열교환기의 엑서지 효율과 손실을 계산합니다.
    """
    # 파라미터 추출 (온도는 켈빈으로 자동 변환됨)
    T_h_in = params['T_h_in']
    T_h_out = params['T_h_out']
    T_c_in = params['T_c_in']
    T_c_out = params['T_c_out']
    m_h = params['m_h']
    m_c = params['m_c']
    
    # 물의 비열 (kJ/kg-K)
    cp = 4.18
    
    # 열전달량 계산
    Q_h = m_h * cp * (T_h_in - T_h_out)  # 고온측 방출 열량
    Q_c = m_c * cp * (T_c_out - T_c_in)  # 저온측 흡수 열량
    
    # 엑서지 계산
    T_0 = 298.15  # 기준 온도 (25℃)
    E_h = Q_h * (1 - T_0/((T_h_in + T_h_out)/2))  # 고온측 엑서지
    E_c = Q_c * (1 - T_0/((T_c_in + T_c_out)/2))  # 저온측 엑서지
    
    # 엑서지 효율
    eta_ex = E_c / E_h if E_h != 0 else 0
    
    # 엑서지 파괴
    E_d = E_h - E_c
    
    return {k: v for k, v in locals().items() if k != 'params'}


@eval_registry.register('TEST', 'CHE')
def evaluate_che(params: Dict[str, float]) -> Dict[str, float]:
    """Counter Flow Heat Exchanger 엑서지 계산
    
    대향류 열교환기의 엑서지 효율과 손실을 계산합니다.
    NTU-effectiveness 방법을 사용합니다.
    """
    # 기본 계산은 SHE와 동일
    basic_results = evaluate_she(params)
    
    # 추가 파라미터
    UA = params['UA']
    m_h = params['m_h']
    m_c = params['m_c']
    
    # 물의 비열 (kJ/kg-K)
    cp = 4.18
    
    # NTU-effectiveness 계산
    C_h = m_h * cp  # 고온측 열용량
    C_c = m_c * cp  # 저온측 열용량
    C_min = min(C_h, C_c)  # 최소 열용량
    C_max = max(C_h, C_c)  # 최대 열용량
    C_r = C_min / C_max  # 열용량비
    NTU = UA / C_min  # Number of Transfer Units
    
    # 유효도 계산 (대향류)
    if C_r == 1:
        effectiveness = NTU / (1 + NTU)
    else:
        effectiveness = (1 - math.exp(-NTU * (1 - C_r))) / (1 - C_r * math.exp(-NTU * (1 - C_r)))
    
    # 결과 업데이트
    results = basic_results.copy()
    results.update({
        'NTU': NTU,
        'effectiveness': effectiveness,
        'C_r': C_r,
    })
    
    return results


# 3. 시각화 도구
@viz_registry.register('Temperature Distribution')
def plot_temperature_distribution(variables: Dict[str, float], params: Dict[str, Any]) -> None:
    """온도 분포 시각화
    
    열교환기의 입출구 온도를 시각화합니다.
    """
    # 데이터 준비
    data = []
    for side in ['Hot', 'Cold']:
        for position in ['Inlet', 'Outlet']:
            key = f'T_{side[0].lower()}_{"in" if position == "Inlet" else "out"}'
            temp = params[key] if key in params else 0
            data.append({
                'Side': side,
                'Position': position,
                'Temperature': temp
            })
    
    # 차트 생성
    chart = alt.Chart(pd.DataFrame(data)).mark_line().encode(
        x=alt.X('Position:N', sort=['Inlet', 'Outlet']),
        y=alt.Y('Temperature:Q', title='Temperature (°C)'),
        color='Side:N',
        tooltip=['Side', 'Position', 'Temperature']
    ).properties(
        title='Temperature Distribution in Heat Exchanger'
    )
    
    st.altair_chart(chart, use_container_width=True)


if __name__ == "__main__":
    # 시스템 등록
    register_test_systems() 