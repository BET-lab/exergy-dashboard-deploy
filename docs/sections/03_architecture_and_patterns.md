# 3. 아키텍처 및 디자인 패턴

## 전체 구조 및 흐름

Exergy Dashboard는 시스템 등록, 평가, 시각화의 세 가지 핵심 기능을 중심으로 모듈화되어 있다. 사용자는 새로운 시스템을 등록하고, 각 시스템에 대한 평가 함수를 추가하며, 결과를 시각화하는 과정을 통해 엑서지 분석을 수행할 수 있다.

- **시스템 등록**: 다양한 시스템(예: ASHP, GSHP 등)과 모드(냉방, 난방, 온수 등) 자유롭게 등록 가능
- **평가 함수 등록**: 각 시스템에 대한 엑서지 평가 로직을 함수로 등록하여, 입력 파라미터에 따라 결과를 계산함
- **시각화 함수 등록**: Altair 기반의 시각화 함수를 등록하여, 분석 결과를 대시보드 내에서 시각적으로 표현함
- **Streamlit 대시보드**: 위 기능들을 통합하여 사용자가 웹에서 손쉽게 분석을 수행할 수 있도록 UI 제공

## 사용된 디자인 패턴 및 예시

### 1. 레지스트리(Registry) 패턴

시스템, 평가 함수, 시각화 함수 각각에 대해 레지스트리 클래스를 두어, 새로운 기능(시스템/함수 등)을 동적으로 등록하고 관리할 수 있도록 설계한다. 데코레이터(Decorator)를 활용하여 함수 등록을 간결하게 처리한다.

#### 예시: 시각화 레지스트리 및 데코레이터

```python
from dataclasses import dataclass
from typing import Callable, Dict

@dataclass
class VisualizationRegistry:
    _visualizers: Dict[str, Dict[str, Callable]] = None
    def __post_init__(self):
        self._visualizers = {}
    def register(self, mode: str, name: str) -> Callable:
        def decorator(func: Callable) -> Callable:
            if mode not in self._visualizers:
                self._visualizers[mode] = {}
            self._visualizers[mode][name] = func
            return func
        return decorator

# 전역 레지스트리 인스턴스 생성
registry = VisualizationRegistry()

# 데코레이터를 이용한 시각화 함수 등록 예시
@registry.register('COOLING', 'Exergy Efficiency')
def plot_exergy_efficiency(session_state, selected_systems):
    # ... 시각화 코드 ...
    pass
```

#### 예시: 평가 함수 레지스트리 및 데코레이터

```python
class EvaluationRegistry:
    def __init__(self):
        self._evaluators = {}
    def register(self, mode: str, system_type: str) -> Callable:
        def decorator(func: Callable) -> Callable:
            if mode not in self._evaluators:
                self._evaluators[mode] = {}
            self._evaluators[mode][system_type] = func
            return func
        return decorator

registry = EvaluationRegistry()

@registry.register('HEATING', 'ASHP')
def evaluate_heating_ashp(params):
    # ... 평가 로직 ...
    pass
```

### 2. 데이터 클래스(DataClass) 패턴

Python의 dataclass를 활용하여 각 레지스트리의 데이터 구조를 명확하게 정의한다.

#### 예시: 시스템 파라미터 데이터 클래스

```python
from dataclasses import dataclass

@dataclass
class SystemParameter:
    name: str
    default: float
    unit: str

param = SystemParameter(name='온도', default=25.0, unit='°C')
print(param)
```

### 3. 모듈 구조 및 확장성

Exergy Dashboard는 각 기능별로 독립적인 모듈로 분리되어 있음. 새로운 시스템, 평가 함수, 시각화 함수는 별도의 파일에서 손쉽게 추가 가능. 모듈 임포트만으로 자동 등록됨.

#### 예시: 시스템 등록 및 템플릿 활용

```python
from exergy_dashboard.system import register_system, get_system_template

# 템플릿을 기반으로 새로운 시스템 구성
template = get_system_template()
new_system = template.copy()
new_system['display']['title'] = 'My New System'
new_system['display']['icon'] = ':star:'
new_system['parameters']['T_0'] = {
    'explanation': {'EN': 'Environment Temperature', 'KR': '환경온도'},
    'latex': r'$T_0$',
    'default': 32.0,
    'range': [-50, 50],
    'unit': '℃',
    'step': 0.5,
    'category': 'environment',
}
register_system('MY_MODE', 'NEW_SYSTEM', new_system)
```

### 4. 순수 함수(Pure Function) 기반 평가 함수

평가 함수는 입력 파라미터만을 사용하여 결과를 반환하는 순수 함수로 구현한다. 이는 테스트와 유지보수를 용이하게 한다.

#### 예시: 순수 함수 평가 함수

```python
@registry.register('COOLING', 'ASHP')
def evaluate_cooling_ashp(params):
    T_0 = params['T_0']
    T_h = params['T_h']
    Q_h = params['Q_h']
    X_h = Q_h * (1 - T_0 / T_h)
    return {'X_h': X_h}
```

## 구조적 장점 및 확장성

- **확장성**: 새로운 시스템, 평가 함수, 시각화 함수 별도 파일에서 손쉽게 추가 가능. 모듈 임포트만으로 자동 등록됨
- **유지보수성**: 각 기능이 명확히 분리되어 있어, 특정 기능의 수정/확장이 전체 코드에 영향을 주지 않음
- **유연성**: 다양한 모드와 시스템 지원, 사용자가 직접 커스텀 시스템/함수 추가 가능
- **테스트 용이성**: 평가 함수는 순수 함수(pure function)로 구현되어, 단위 테스트 및 검증이 용이함

> 이러한 구조는 연구, 교육, 실무 등 다양한 환경에서의 활용과 장기적인 프로젝트 유지보수에 적합함. 