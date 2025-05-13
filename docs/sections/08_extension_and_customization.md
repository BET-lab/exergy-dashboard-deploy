# 8. 확장 및 커스터마이징 방법

이 섹션에서는 Exergy Dashboard의 확장성과 커스터마이징 방법을 기술문서 스타일로 구체적으로 안내함. 새로운 시스템/모드 추가, 커스텀 평가 및 시각화 함수 작성, 예시 코드 활용, 확장 시 주의사항 등 포함.

---

## 8.1 새로운 시스템/모드 추가

### 1) 새로운 모드/시스템 정의
- 기존 모드(예: COOLING, HEATING) 외에 임의의 모드명 자유롭게 추가 가능
- 시스템 템플릿 복사 후 새로운 시스템 정의 및 파라미터 자유 설계 가능

```python
from exergy_dashboard.system import register_system, get_system_template

my_mode = 'MY_MODE'
my_system_name = 'MY_NEW_SYSTEM'
my_system = get_system_template()
my_system['display']['title'] = 'My New System'
my_system['display']['icon'] = ':star:'
my_system['parameters']['T_0'] = {
    'explanation': {'EN': 'Environment Temp', 'KR': '환경온도'},
    'latex': r'$T_0$',
    'default': 20.0,
    'range': [-50, 50],
    'unit': '℃',
    'step': 0.5,
    'category': 'environment',
}
register_system(my_mode, my_system_name, my_system)
```

### 2) 시스템 등록 시 주의사항
- 시스템 이름, 모드 이름은 대소문자 구분 없이 자동 변환됨
- 파라미터 구조가 표준 템플릿을 따르는지 확인 필요
- 동일 모드 내 시스템 이름 중복 주의

---

## 8.2 커스텀 평가 함수 작성

- 각 시스템별 입력 파라미터에 따라 엑서지, 효율 등 다양한 결과 계산 함수 자유롭게 작성 가능
- 함수는 반드시 `@registry.register('MODE', 'SYSTEM_NAME')` 데코레이터로 등록, 입력/반환값 모두 딕셔너리여야 함

```python
from exergy_dashboard.evaluation import registry

@registry.register('MY_MODE', 'MY_NEW_SYSTEM')
def evaluate_my_system(params):
    T_0 = params['T_0']
    # ... 계산 로직 ...
    exergy = T_0 * 1.5
    return {'exergy': exergy}
```

- 중간 계산 결과, 예외 상황 등도 자유롭게 반환 가능
- 함수는 순수 함수(pure function)로 작성 권장

---

## 8.3 커스텀 시각화 함수 작성

- Altair, Plotly 등 Streamlit 지원 시각화 라이브러리 자유롭게 사용 가능
- 시각화 함수는 반드시 `@registry.register('MODE', 'Visualization Name')` 데코레이터로 등록, `(session_state, selected_systems)` 인자 필요

```python
from exergy_dashboard.visualization import registry
import altair as alt
import pandas as pd

@registry.register('MY_MODE', 'My Custom Chart')
def plot_my_chart(session_state, selected_systems):
    data = [
        {'system': sys, 'exergy': session_state.systems[sys]['variables']['exergy']}
        for sys in selected_systems
    ]
    df = pd.DataFrame(data)
    return alt.Chart(df).mark_line().encode(x='system', y='exergy', color='system')
```

- 데이터가 없는 경우 빈 차트 또는 안내 메시지 반환 권장

---

## 8.4 예시 코드 안내

- `examples/` 폴더의 다양한 예시 파일(`custom_system.py`, `heating_system.py` 등) 참고 시 실제 확장/커스터마이징 방법 쉽게 익힐 수 있음
- 예시 파일 복사 후 이름만 변경해도 새로운 시스템/평가/시각화 바로 추가 가능

---

## 8.5 확장/커스터마이징 시 주의사항

- 시스템/평가/시각화 함수 등록 시 표준 인터페이스(입력/출력 타입, 데코레이터 등) 반드시 준수 필요
- 모듈 임포트 시점에 자동 등록되므로, `app.py`에서 예시 파일 import 필요
- 파라미터 이름, 단위, 범위 등 일관성 있게 관리 권장
- Streamlit, Altair 등 외부 라이브러리 버전 호환성 유의

### 추가 팁 및 오류 대처
- 함수가 대시보드에 보이지 않을 경우, 해당 예시 파일이 `app.py`에서 import되고 있는지 확인 필요
- 파라미터 입력값 오류 시 입력값 범위 확인 필요
- Streamlit 앱 자동 새로고침이 되지 않을 경우, 브라우저 수동 새로고침 또는 `R` 키 사용 가능

> 확장/커스터마이징 관련 추가 질문은 FAQ 문서 또는 README.md 참고 또는 예시 코드 적극 활용 바람 