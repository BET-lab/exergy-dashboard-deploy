# 5. 주요 모듈/클래스 설명

이 섹션에서는 Exergy Dashboard의 핵심 기능을 담당하는 주요 모듈과 클래스, 그리고 그 역할과 구조, 사용법, 장점에 대해 기술문서 스타일로 자세히 설명한다.

---

## 5.1 시스템 등록/관리 모듈 (`system.py`)

### 역할 및 구조
- 다양한 시스템(예: ASHP, GSHP 등)과 모드(냉방, 난방, 온수 등) 등록/관리 기능 담당
- 시스템의 파라미터, 표시 정보, 기본값, 범위, 단위 등 구조화하여 저장함
- 시스템 등록은 레지스트리(Registry) 패턴을 사용하여 동적으로 이루어짐

### 주요 클래스 및 함수
- **SystemRegistry**: 시스템 정보를 저장/관리하는 핵심 클래스임. 각 모드별로 여러 시스템을 딕셔너리 형태로 관리함
- **register_system(mode, system_type, system_config)**: 새로운 시스템을 등록하는 함수임. 모듈 임포트 시 자동 등록 가능하도록 설계함
- **get_system_template()**: 새로운 시스템 등록을 위한 템플릿 딕셔너리 반환

### 사용 예시
```python
from exergy_dashboard.system import register_system, get_system_template

# 시스템 템플릿을 복사하여 커스텀 시스템 생성
my_system = get_system_template()
my_system['display']['title'] = 'My System'
my_system['display']['icon'] = ':star:'
my_system['parameters']['T_0'] = {
    'explanation': {'EN': 'Environment Temp', 'KR': '환경온도'},
    'latex': r'$T_0$',
    'default': 25.0,
    'range': [-50, 50],
    'unit': '℃',
    'step': 0.5,
    'category': 'environment',
}
register_system('MY_MODE', 'MY_SYS', my_system)
```

### 장점
- 시스템 추가/수정 매우 용이, 모듈 임포트만으로 자동 등록 가능
- 파라미터 구조 명확, 확장성과 유지보수성 뛰어남

---

## 5.2 평가 함수 등록/관리 모듈 (`evaluation.py`)

### 역할 및 구조
- 각 시스템에 대한 엑서지 평가(계산) 함수 등록/관리 담당
- 평가 함수는 입력 파라미터를 받아 계산 결과(엑서지, 효율 등) 반환
- 레지스트리 패턴과 데코레이터 활용하여 함수 등록 간결하게 처리

### 주요 클래스 및 함수
- **EvaluationRegistry**: 모드/시스템별 평가 함수 저장/관리 클래스임
- **@registry.register(mode, system_type)**: 평가 함수를 해당 모드/시스템에 등록하는 데코레이터임
- **evaluate(mode, system_type, params)**: 등록된 평가 함수 호출하여 결과 반환

### 사용 예시
```python
from exergy_dashboard.evaluation import registry

# 평가 함수 등록 예시
@registry.register('HEATING', 'ASHP')
def evaluate_heating_ashp(params):
    T_0 = params['T_0']
    T_h = params['T_h']
    Q_h = params['Q_h']
    X_h = Q_h * (1 - T_0 / T_h)
    return {'X_h': X_h}

# 평가 함수 호출 예시
params = {'T_0': 20, 'T_h': 60, 'Q_h': 10}
result = registry.evaluate('HEATING', 'ASHP', params)
print(result)  # {'X_h': 6.666...}
```

### 장점
- 평가 함수 추가/수정 쉽고, 함수형 프로그래밍 스타일로 테스트 용이
- 다양한 시스템/모드에 대해 독립적으로 평가 함수 관리 가능

---

## 5.3 시각화 등록/관리 모듈 (`visualization.py`)

### 역할 및 구조
- 분석 결과를 시각적으로 표현하는 Altair 기반 시각화 함수 등록/관리 담당
- 각 모드별로 다양한 시각화 함수 등록 가능, Streamlit UI에서 탭 형태로 표시
- 레지스트리 패턴과 데코레이터 활용하여 시각화 함수 등록 간결하게 처리

### 주요 클래스 및 함수
- **VisualizationRegistry**: 모드별 시각화 함수 저장/관리 클래스임
- **VisualizationManager**: Streamlit UI에서 시각화 탭 렌더링 클래스임
- **@registry.register(mode, name)**: 시각화 함수를 해당 모드에 등록하는 데코레이터임
- **render_tabs(session_state, selected_systems, mode)**: 등록된 시각화 함수 탭으로 렌더링

### 사용 예시
```python
from exergy_dashboard.visualization import registry
import altair as alt
import pandas as pd

# 시각화 함수 등록 예시
@registry.register('COOLING', 'COP Distribution')
def plot_cop_distribution(session_state, selected_systems):
    data = [
        {'system': sys, 'cop': session_state.systems[sys]['variables']['cop']}
        for sys in selected_systems
    ]
    df = pd.DataFrame(data)
    return alt.Chart(df).mark_bar().encode(x='system', y='cop', color='system')
```

### 장점
- 다양한 시각화 함수 동적 추가/확장 가능
- Streamlit UI와의 자연스러운 통합 및 사용자 경험 향상

---

## 5.4 기타 핵심 모듈 및 구조

- **examples/**: 실제 시스템/평가/시각화 함수 예시와 템플릿 제공, 신규 사용자나 확장 개발자 참고용
    - 예시: 사용자 정의 시스템/평가/시각화 예제
    ```python
    # examples/custom_system.py
    from exergy_dashboard.system import register_system
    from exergy_dashboard.evaluation import registry as eval_registry
    from exergy_dashboard.visualization import registry as viz_registry
    # ...
    ```
- **notebooks/**: 실험, 테스트, 분석용 Jupyter 노트북 저장소, 개발 및 연구에 활용
    - 예시: 노트북 파일 생성
    ```bash
    jupyter notebook notebooks/analysis_example.ipynb
    ```
- **app.py**: Streamlit 기반 대시보드 진입점, 전체 UI/UX 및 사용자 상호작용 관리
    - 예시: 대시보드 실행
    ```bash
    streamlit run app.py
    ```

> 각 모듈은 독립적으로 설계되어 있어, 새로운 기능 추가 및 유지보수 용이함. 레지스트리 패턴과 데코레이터 활용으로 코드의 일관성과 확장성 극대화함. 