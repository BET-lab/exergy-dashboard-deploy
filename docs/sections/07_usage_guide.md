# 7. 사용법 가이드

이 섹션에서는 Exergy Dashboard의 실제 사용법을 단계별로 기술문서 스타일로 자세히 안내한다. 시스템 등록, 평가 함수 추가, 시각화 함수 추가, 대시보드 UI 사용법까지 예시와 함께 설명함.

---

## 7.1 시스템 등록 방법

### 1) 시스템 템플릿 가져오기 및 수정
- `get_system_template()` 함수로 기본 템플릿 제공
- 필요한 정보 입력 및 수정 가능

```python
from exergy_dashboard.system import register_system, get_system_template

my_system = get_system_template()
my_system['display']['title'] = 'My Custom System'
my_system['display']['icon'] = ':rocket:'
my_system['parameters']['T_in'] = {
    'explanation': {'EN': 'Inlet Temp', 'KR': '입구 온도'},
    'latex': r'$T_{in}$',
    'default': 60,
    'range': [0, 100],
    'unit': '℃',
    'step': 1,
    'category': 'temperature',
}
```

### 2) 시스템 등록
- `register_system('MODE', 'SYSTEM_NAME', my_system)` 함수로 시스템 등록함
- 모듈 임포트 시 자동 등록됨

```python
register_system('COOLING', 'MY_CUSTOM_SYS', my_system)
```

---

## 7.2 평가 함수 추가 방법

### 1) 평가 함수 작성 및 데코레이터 등록
- 시스템별 입력 파라미터를 받아 결과 반환 함수 작성
- `@registry.register('MODE', 'SYSTEM_NAME')` 데코레이터로 등록함

```python
from exergy_dashboard.evaluation import registry

@registry.register('COOLING', 'MY_CUSTOM_SYS')
def evaluate_my_system(params):
    T_in = params['T_in']
    # ... 계산 로직 ...
    result = T_in * 2
    return {'result': result}
```

---

## 7.3 시각화 함수 추가 방법

### 1) Altair 기반 시각화 함수 작성 및 등록
- 분석 결과 시각화용 Altair 차트 함수 작성
- `@registry.register('MODE', 'Visualization Name')` 데코레이터로 등록함

```python
from exergy_dashboard.visualization import registry
import altair as alt
import pandas as pd

@registry.register('COOLING', 'My Custom Visualization')
def plot_custom_viz(session_state, selected_systems):
    data = [
        {'system': sys, 'result': session_state.systems[sys]['variables']['result']}
        for sys in selected_systems
    ]
    df = pd.DataFrame(data)
    return alt.Chart(df).mark_bar().encode(x='system', y='result', color='system')
```

---

## 7.4 Streamlit 대시보드 사용법

### 1) 시스템 추가 및 파라미터 입력
- 사이드바에서 모드/시스템 유형 선택 및 시스템 추가 가능
- 각 시스템별 파라미터 입력/수정 가능

### 2) 결과 확인 및 시각화
- 'Output Data' 영역에서 여러 시스템 결과 비교 가능
- 상단 탭에서 다양한 시각화 확인 가능

### 3) 시스템/모드 전환 및 초기화
- 모드 변경 시 해당 모드에 등록된 시스템만 표시됨
- 시스템 상태 초기화 및 선택 시스템 별도 관리 가능

---

## 7.5 커스텀 파일 활용
- `systems/` 폴더에 커스텀 시스템/평가/시각화 코드(`*_system.py`) 추가 시 자동으로 대시보드에 반영됨
- 별도의 import 작업 없이 파일만 추가하면 됨

### 추가 팁 및 오류 대처
- 시스템/평가/시각화 함수가 대시보드에 보이지 않을 경우, `systems/` 폴더에 *_system.py 파일이 정상적으로 추가되었는지, 파일명/코드 오류가 없는지 확인 필요
- 파라미터 입력값 오류 시 입력값 범위 확인 필요
- Streamlit 앱 자동 새로고침이 되지 않을 경우, 브라우저 수동 새로고침 또는 `R` 키 사용 가능

> 실제 사용 중 궁금한 점이나 오류 발생 시 FAQ 문서 또는 README.md 참고 바람 