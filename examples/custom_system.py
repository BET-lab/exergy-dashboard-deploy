"""예시: 커스텀 시스템, 평가 함수, 시각화 추가

이 스크립트는 새로운 시스템과 시각화를 등록하는 간단한 예시입니다.
'TEST' 모드에 간단한 열교환기 시스템을 추가합니다.
"""

from typing import List, Any
import pandas as pd
import altair as alt
from exergy_dashboard.system import register_system
from exergy_dashboard.evaluation import registry as eval_registry
from exergy_dashboard.visualization import registry


# 1. 간단한 열교환기 시스템 정의
she_system = {
    'display': {
        'title': '간단한 열교환기 시스템',
        'icon': ':earth_americas:',
    },
    'parameters': {
        'T_in_h': {
            'explanation': {'EN': 'Hot Side Inlet Temperature', 'KR': '고온측 입구 온도'},
            'latex': r'$T_{in,h}$',
            'default': 80,
            'range': [50, 100],
            'unit': '°C',
            'step': 1,
            'category': 'temperature'
        },
        'T_out_h': {
            'explanation': {'EN': 'Hot Side Outlet Temperature', 'KR': '고온측 출구 온도'},
            'latex': r'$T_{out,h}$',
            'default': 70,
            'range': [50, 100],
            'unit': '°C',
            'step': 1,
            'category': 'temperature'
        },
    }
}


# Simple Heat Exchanger(SHE) 시스템 등록
register_system('TEST_MODE', 'TEST_SYSTEM', she_system)
    

# 3. 간단한 엑서지 계산 함수
@eval_registry.register('TEST_MODE', 'TEST_SYSTEM')
def evaluate_she(params):
    """간단한 열교환기의 엑서지 계산"""
    # 파라미터 추출
    T_in_h = params['T_in_h']
    T_out_h = params['T_out_h']
   
    diff_T = T_in_h - T_out_h

    # 결과 반환 (plot에 사용할 변수수)
    return {
        'diff_T': diff_T,  # 온도차 (℃)
    }


# 4. 모드별 시각화 등록
@registry.register('TEST_MODE', 'Temperature difference')
def plot_diff_temperature(session_state: Any, selected_systems: List[str]) -> alt.Chart:
    """선택된 열교환기 시스템들의 온도 프로필 시각화"""
    # 데이터 준비
    data = []
    for system in selected_systems:
        data.append({
            'system': system,
            'diff_T': session_state.systems[system]['variables']['diff_T']
        })

    # 시각화 생성
    chart = alt.Chart(pd.DataFrame(data)).mark_bar().encode(
        x='system',
        y='diff_T',
        color='system'
    )
    
    return chart