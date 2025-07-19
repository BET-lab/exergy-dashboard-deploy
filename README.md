# Exergy Analyzer

엑서지 분석을 위한 애플리케이션입니다.


## 1. 새로운 시스템 등록하기

새로운 시스템은 `register_system` 함수를 사용하여 등록할 수 있습니다. 각 시스템은 특정 모드에 등록됩니다.

```python
from exergy_dashboard.system import register_system

# 새로운 시스템 정의
my_system = {
    'display': {
        'title': '나의 시스템',
        'icon': ':gear:',
    },
    'parameters': {
        'param1': {
            'explanation': {'EN': 'Parameter 1', 'KR': '파라미터 1'},
            'latex': r'$param_{1}$',
            'default': 80,
            'range': [50, 100],
            'unit': '°C',
            'step': 1,
            'category': 'temperature'
        },
        'param2': {
            'explanation': {'EN': 'Parameter 2', 'KR': '파라미터 2'},
            'latex': r'$param_{2}$',
            'default': 20,
            'range': [10, 30],
            'unit': 'kg/s',
            'step': 0.1,
            'category': 'flow'
        },
        # 더 많은 파라미터 추가
    }
}

# 모듈 레벨에서 시스템 직접 등록
# 이 코드는 임포트 시점에 자동으로 실행됩니다
register_system('MY_MODE', 'MY_SYS', my_system)
print("MY_MODE 모드에 시스템 등록 완료: MY_SYS")
```

### 시스템 템플릿 필수 필드
- `display`: 시스템 표시 정보
  - `title`: 시스템 제목
  - `icon`: 시스템 아이콘 (이모지 형식)
- `parameters`: 시스템 파라미터 정보
  - 각 파라미터는 다음 필드를 포함할 수 있습니다:
    - `explanation`: 다국어 파라미터 설명 (`EN`, `KR` 등)
    - `latex`: LaTeX 형식의 수식 표현
    - `default`: 기본값
    - `range`: 최소값과 최대값의 리스트 `[min, max]`
    - `unit`: 단위
    - `step`: 입력 스텝 크기
    - `category`: 파라미터 분류

## 2. 시스템 평가 함수 구현하기

각 시스템에 대한 평가 함수는 데코레이터를 사용하여 등록합니다. 이 함수는 파라미터를 받아 계산 결과를 반환합니다.

```python
from exergy_dashboard.evaluation import registry as eval_registry

@eval_registry.register('MY_MODE', 'MY_SYS')
def evaluate_my_system(params):
    """
    시스템 계산 함수
    
    Parameters
    ----------
    params : dict
        사용자가 설정한 파라미터 값 딕셔너리
        
    Returns
    -------
    dict
        계산 결과를 담은 딕셔너리
    """
    # 파라미터 추출
    param1 = params['param1']
    param2 = params['param2']
    
    # 계산 수행
    result1 = param1 * 2
    result2 = param2 / 10
    
    # 계산 결과 반환
    return {
        'result1': result1,
        'result2': result2,
        # 다른 계산 결과들
    }
```

### 주의사항
- 평가 함수는 `@eval_registry.register('모드', '시스템명')` 데코레이터를 사용하여 등록합니다
- 함수는 파라미터 딕셔너리를 입력으로 받아 계산 결과 딕셔너리를 반환합니다
- 계산 오류 시 대시보드에서 예외 처리되지만, 가능한 자체 오류 검사를 구현하세요

## 3. 모드별 시각화 추가하기

시각화 함수는 특정 모드에 등록되며, 해당 모드가 활성화되었을 때만 표시됩니다.

```python
from exergy_dashboard.visualization import registry
import altair as alt
import pandas as pd
from typing import Any, List

@registry.register('MY_MODE', 'My Visualization')
def plot_my_visualization(session_state: Any, selected_systems: List[str]) -> alt.Chart:
    """커스텀 시각화 함수
    
    Parameters
    ----------
    session_state : Any
        Streamlit 세션 상태 객체
    selected_systems : List[str]
        시각화할 시스템 이름 목록
        
    Returns
    -------
    alt.Chart
        Altair 차트 객체
    """
    # 데이터 준비
    data = []
    for system in selected_systems:
        data.append({
            'system': system,
            'result1': session_state.systems[system]['variables']['result1'],
            'result2': session_state.systems[system]['variables']['result2']
        })
    
    # 데이터프레임 생성
    df = pd.DataFrame(data)
    
    # Altair 차트 생성 및 반환
    chart = alt.Chart(df).mark_bar().encode(
        x='system:N',
        y='result1:Q',
        color='system'
    )
    
    return chart
```

### 시각화 함수 규칙
- 모든 시각화 함수는 `@registry.register('모드', '시각화이름')` 데코레이터로 등록합니다
- 함수 형식은 `(session_state, selected_systems) -> alt.Chart` 형식을 따라야 합니다
- 반환값은 Altair 차트 혹시 Streamlit이 시각화 가능한 객체여야 합니다
- 선택된 모든 시스템을 처리할 수 있어야 합니다
- 데이터가 없는 경우 빈 차트를 반환해야 합니다

## 4. 시스템 등록 및 시각화 추가를 위한 파일 구성

시스템 등록과 시각화 추가는 별도의 모듈에서 수행할 수 있습니다. 모듈이 임포트될 때 자동으로 시스템이 등록됩니다:

```
systems/
  my_custom_system.py  # 사용자 정의 시스템, 계산 함수, 시각화 등록
```

`my_custom_system.py` 예시:

```python
from exergy_dashboard.system import register_system
from exergy_dashboard.evaluation import registry as eval_registry
from exergy_dashboard.visualization import registry
import pandas as pd
import altair as alt
from typing import List, Any

# 1. 시스템 정의
my_system = {
    'display': {
        'title': '나의 시스템',
        'icon': ':gear:',
    },
    'parameters': {
        'param1': {
            'explanation': {'EN': 'Parameter 1', 'KR': '파라미터 1'},
            'latex': r'$param_{1}$',
            'default': 80,
            'range': [50, 100],
            'unit': '°C',
            'step': 1,
            'category': 'temperature'
        },
        # 더 많은 파라미터 추가
    }
}

# 2. 시스템 직접 등록 (모듈 임포트 시 자동 실행)
register_system('MY_MODE', 'MY_SYS', my_system)
print("MY_MODE 모드에 시스템 등록 완료: MY_SYS")

# 3. 평가 함수 등록
@eval_registry.register('MY_MODE', 'MY_SYS')
def evaluate_my_system(params):
    """나의 시스템 평가 함수"""
    # 파라미터 추출
    param1 = params['param1']
   
    # 계산 수행
    result = param1 * 2
    
    # 결과 반환
    return {
        'result': result,
    }

# 4. 시각화 함수 등록
@registry.register('MY_MODE', 'My Visualization')
def plot_my_visualization(session_state: Any, selected_systems: List[str]) -> alt.Chart:
    """선택된 시스템의 결과값 시각화"""
    # 데이터 준비
    data = []
    for system in selected_systems:
        data.append({
            'system': system,
            'result': session_state.systems[system]['variables']['result']
        })

    # 시각화 생성
    chart = alt.Chart(pd.DataFrame(data)).mark_bar().encode(
        x='system',
        y='result',
        color='system'
    )
    
    return chart
```

## 5. 애플리케이션 임포트 및 실행하기

1. 필요한 패키지 설치:
   ```bash
   uv sync
   ```

2. 시스템 파일 자동 임포트:
   - `systems/` 폴더에 `*_system.py` 파일을 추가하면, `app.py`가 자동으로 모든 시스템 파일을 임포트합니다.
   - 별도의 임포트 코드를 작성할 필요가 없습니다.
   - 예시 파일로는 `systems/custom_system.py` 참고.

3. Streamlit 앱 실행:
   ```bash
   uv run streamlit run app.py
   ```

4. 웹 브라우저에서 애플리케이션 접속:
   ```
   http://localhost:8501
   ```

## 6. 예시 코드

실제 구현 예시는 다음 파일을 참조하세요:
- `systems/custom_system.py`: TEST 모드의 TEST_SYSTEM 시스템 구현

## 주의사항

1. 시스템 등록 시 고려사항:
   - 모든 필수 필드가 포함되어 있는지 확인
   - 파라미터 구조가 표준 양식을 따르는지 확인
   - 시스템 이름이 기존 시스템과 중복되지 않도록 주의
   - 모듈 레벨에서 직접 등록하면 임포트만으로 시스템이 등록됩니다

2. 평가 함수 작성 시 고려사항:
   - 올바른 모드와 시스템명으로 데코레이터 등록
   - 모든 파라미터를 올바르게 처리하는지 확인
   - 오류 상황에 대한 적절한 예외 처리 포함

3. 시각화 함수 작성 시 고려사항:
   - 항상 Altair 차트 객체를 반환하도록 구현
   - 선택된 모든 시스템을 지원하도록 개발
   - 데이터가 없는 경우의 예외 처리 포함
   - 필요한 모든 데이터가 session_state에서 추출되는지 확인
