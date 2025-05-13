# 1. 프로젝트 개요 및 개발 목적

## 프로젝트 소개

Exergy Dashboard는 다양한 에너지 시스템의 엑서지(Exergy) 분석을 손쉽게 수행할 수 있도록 설계된 대시보드 애플리케이션임. 사용자는 다양한 시스템을 등록하고, 각 시스템의 파라미터를 입력하여 엑서지 분석 결과를 시각적으로 확인 가능. 본 도구는 연구자, 엔지니어, 학생 등 에너지 시스템 분석이 필요한 모든 사용자를 대상으로 함.

## 개발 배경 및 목표

- **배경**: 엑서지 분석은 에너지 시스템의 효율성과 손실을 정량적으로 평가하는 데 필수적인 도구임. 기존의 엑서지 분석 도구는 사용이 복잡하거나, 특정 시스템에 한정되어 있는 경우가 많음.
- **목표**: 다양한 시스템과 모드(냉방, 난방, 온수 등)에 대해 손쉽게 엑서지 분석을 수행할 수 있는 범용적이고 확장 가능한 대시보드 개발이 목표임. 누구나 새로운 시스템과 평가/시각화 함수를 쉽게 추가 가능하도록 설계함.

## 주요 기능 및 상세 예시

### 1. 다양한 시스템 및 모드 지원

Exergy Dashboard는 ASHP, GSHP 등 다양한 시스템과 냉방, 난방, 온수 등 여러 모드를 지원함. 새로운 시스템을 등록하는 예시는 다음과 같음.

```python
from exergy_dashboard.system import register_system

# 예시: 간단한 열교환기 시스템 등록
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

register_system('Hot water', 'TEST_SYSTEM', she_system)
```

### 2. 시스템별 파라미터 입력 및 관리 기능

시스템 등록 시 각 파라미터의 기본값, 범위, 단위, 설명 등을 명확히 정의 가능. 예시는 위 시스템 등록 코드의 'parameters' 항목 참고.

### 3. 엑서지 평가 함수의 손쉬운 등록 및 실행

평가 함수는 시스템별로 등록하며, 파라미터를 입력받아 결과를 반환한다. 다음은 평가 함수 등록 예시이다.

```python
from exergy_dashboard.evaluation import registry as eval_registry

@eval_registry.register('Hot water', 'TEST_SYSTEM')
def evaluate_she(params):
    """간단한 열교환기의 엑서지 계산"""
    T_in_h = params['T_in_h']
    T_out_h = params['T_out_h']
    diff_T = T_in_h - T_out_h
    return {
        'diff_T': diff_T,  # 온도차 (℃)
    }
```

### 4. Altair 기반의 시각화 함수 등록 및 대시보드 내 시각적 결과 제공

시각화 함수는 Altair를 활용하여 분석 결과를 시각적으로 표현한다. 다음은 시각화 함수 등록 예시이다.

```python
from exergy_dashboard.visualization import registry
import pandas as pd
import altair as alt
from typing import Any, List

@registry.register('Hot water', 'Temperature difference')
def plot_diff_temperature(session_state: Any, selected_systems: List[str]) -> alt.Chart:
    data = []
    for system in selected_systems:
        data.append({
            'system': system,
            'diff_T': session_state.systems[system]['variables']['diff_T']
        })
    chart = alt.Chart(pd.DataFrame(data)).mark_bar().encode(
        x='system',
        y='diff_T',
        color='system'
    )
    return chart
```

### 5. Streamlit 기반의 웹 대시보드 제공

본 프로젝트는 Streamlit을 기반으로 하여, 웹 브라우저에서 대시보드를 실행할 수 있다. 예시는 다음과 같다.

```bash
streamlit run app.py
```

### 6. 사용자 정의 시스템, 평가, 시각화 함수의 손쉬운 확장성

사용자는 새로운 시스템, 평가 함수, 시각화 함수를 위와 같은 방식으로 추가함으로써 손쉽게 기능을 확장할 수 있다. 예를 들어, 새로운 냉방 시스템과 평가/시각화 함수를 추가하는 코드는 다음과 같다.

```python
from exergy_dashboard.system import register_system
from exergy_dashboard.evaluation import registry as eval_registry
from exergy_dashboard.visualization import registry as viz_registry

# 새로운 냉방 시스템 등록
cooling_system = {
    'display': {'title': 'Custom Cooling System', 'icon': ':snowflake:'},
    'parameters': {
        'T_in': {'explanation': {'KR': '입구 온도'}, 'default': 10, 'range': [0, 50], 'unit': '°C', 'step': 1, 'category': 'temperature'},
        'T_out': {'explanation': {'KR': '출구 온도'}, 'default': 5, 'range': [0, 50], 'unit': '°C', 'step': 1, 'category': 'temperature'},
    }
}
register_system('COOLING', 'CUSTOM', cooling_system)

# 평가 함수 등록
@eval_registry.register('COOLING', 'CUSTOM')
def evaluate_custom_cooling(params):
    return {'delta_T': params['T_in'] - params['T_out']}

# 시각화 함수 등록
@viz_registry.register('COOLING', 'Delta T')
def plot_delta_t(session_state, selected_systems):
    import pandas as pd
    import altair as alt
    data = [{'system': s, 'delta_T': session_state.systems[s]['variables']['delta_T']} for s in selected_systems]
    return alt.Chart(pd.DataFrame(data)).mark_bar().encode(x='system', y='delta_T')
```

> 위 예시들은 실제 프로젝트 내 examples/ 폴더의 예제 코드와 동일한 방식으로 작성함. 모든 기능은 코드 기반으로 확장 및 커스터마이징 가능. 