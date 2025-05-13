# 9. 예시 코드 및 샘플

이 섹션에서는 Exergy Dashboard의 실제 예시 코드와 샘플을 기술문서 스타일로 제공함. 예제 시스템, 평가 함수, 시각화 함수 구현 예시와 실제 파일 경로, 활용법, 주의사항 안내 포함.

---

## 9.1 예제 시스템 등록 코드

`examples/custom_system.py` 파일 예시:

```python
from exergy_dashboard.system import register_system

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

---

## 9.2 예제 평가 함수 코드

```python
from exergy_dashboard.evaluation import registry as eval_registry

@eval_registry.register('Hot water', 'TEST_SYSTEM')
def evaluate_she(params):
    T_in_h = params['T_in_h']
    T_out_h = params['T_out_h']
    diff_T = T_in_h - T_out_h
    return {'diff_T': diff_T}
```

---

## 9.3 예제 시각화 함수 코드

```python
from exergy_dashboard.visualization import registry
import altair as alt
import pandas as pd
from typing import Any, List

@registry.register('Hot water', '온도차 바 차트')
def plot_diff_T(session_state: Any, selected_systems: List[str]):
    data = [
        {
            'system': sys,
            'diff_T': session_state.systems[sys]['variables']['diff_T']
        }
        for sys in selected_systems
    ]
    df = pd.DataFrame(data)
    return alt.Chart(df).mark_bar().encode(x='system', y='diff_T', color='system')
```

---

## 9.4 주요 사용 예시 및 주의사항

- 여러 시스템 등록 및 각기 다른 파라미터로 평가/시각화 가능
- 예시 파일 복사/수정 시 새로운 시스템/평가/시각화 함수 손쉽게 추가 가능
- `examples/` 폴더 내 파일을 `app.py`에서 import해야 자동 대시보드 반영됨
- 파라미터 이름, 단위, 범위 등 일관성 있게 관리 권장
- 함수가 대시보드에 보이지 않을 경우, 예시 파일 import 여부 및 함수 등록 데코레이터 확인 필요

---

## 9.5 실제 예시 파일 경로 안내

- `examples/custom_system.py` : 커스텀 시스템/평가/시각화 예시
- `examples/heating_system.py` : 난방 시스템 예시
- `examples/cooling_system.py` : 냉방 시스템 예시

> 예시 코드는 신규 사용자와 확장 개발자 모두에게 좋은 출발점이 됨. 실제 파일 참고 후 자신만의 시스템과 함수 작성 필요 