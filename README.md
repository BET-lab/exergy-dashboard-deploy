# Exergy Analysis Dashboard

엑서지 분석을 위한 대시보드 애플리케이션입니다.

## 1. 새로운 시스템 등록하기

시스템 등록은 `register_system` 함수를 사용하여 수행할 수 있습니다.

```python
from exergy_dashboard.system import register_system, get_system_template

# 템플릿 가져오기
template = get_system_template()

# 템플릿을 수정하여 새로운 시스템 설정
new_system = template.copy()
new_system['display'] = {
    'title': 'My New System',
    'icon': ':star:'
}
new_system['parameters'] = {
    'T_0': {
        'explanation': {'EN': 'Environment Temperature', 'KR': '환경온도'},
        'latex': r'$T_0$',
        'default': 32.0,
        'range': [-50, 50],
        'unit': '℃',
        'step': 0.5,
        'category': 'environment',
    }
    # ... 더 많은 파라미터 추가 ...
}

# 시스템 등록
register_system('COOLING', 'NEW_SYSTEM', new_system)
```

### 필수 필드
- `display`: 시스템 표시 정보
  - `title`: 시스템 이름
  - `icon`: 시스템 아이콘 (Streamlit 이모지 코드)
- `parameters`: 시스템 파라미터 정보
  - 각 파라미터는 `explanation`, `latex`, `default`, `range`, `unit`, `step` 필드 필요
  - `category`는 선택사항 (기본값: 'General')

## 2. 엑서지 계산 모듈 추가하기

엑서지 계산 모듈은 `evaluation.py`의 `registry`를 사용하여 등록합니다.

```python
from exergy_dashboard.evaluation import registry
from typing import Dict

@registry.register('MODE_NAME', 'SYSTEM_TYPE')
def evaluate_new_system(params: Dict[str, float]) -> Dict[str, float]:
    """새로운 시스템의 엑서지 계산 함수
    
    Parameters
    ----------
    params : Dict[str, float]
        시스템 파라미터 (온도는 자동으로 켈빈으로 변환됨)
        
    Returns
    -------
    Dict[str, float]
        계산된 모든 변수를 포함하는 딕셔너리
    """
    # 파라미터 추출
    T_0 = params['T_0']  # 이미 켈빈으로 변환됨
    
    # 계산 수행
    result = some_calculation(T_0)
    
    # 모든 로컬 변수 반환 (params 제외)
    return {k: v for k, v in locals().items() if k != 'params'}
```

### 주의사항
- 시스템 등록 시 반드시 해당하는 엑서지 계산 모듈도 등록해야 합니다
- 미등록 시 런타임 에러가 발생할 수 있습니다

## 3. 시각화 도구 추가하기

시각화 도구는 `visualization.py`의 `registry`를 사용하여 등록합니다.

```python
from exergy_dashboard.visualization import registry
import streamlit as st
from typing import Dict, Any

@registry.register('VISUALIZATION_NAME')
def plot_new_visualization(variables: Dict[str, float], params: Dict[str, Any]) -> None:
    """새로운 시각화 함수
    
    Parameters
    ----------
    variables : Dict[str, float]
        계산된 변수들
    params : Dict[str, Any]
        시스템 파라미터
    """
    st.write("### My New Visualization")
    # 시각화 로직 구현
```

## 4. 예시 코드

전체 예시는 `examples/custom_system.py`를 참조하세요. 이 예시는:
- 테스트용 시스템 2개 추가
- 엑서지 계산 모듈 구현
- 간단한 시각화 도구 추가

를 보여줍니다.

## 주의사항

1. 시스템 등록 시 고려사항:
   - 모든 필수 필드가 포함되어 있는지 확인
   - 파라미터 이름이 기존 시스템과 중복되지 않도록 주의
   - 범위와 기본값이 적절한지 검토

2. 엑서지 계산 모듈 작성 시 고려사항:
   - 모든 입력 파라미터가 사용되는지 확인
   - 온도 단위 변환 주의 (섭씨 → 켈빈)
   - 중간 계산 결과도 모두 반환

3. 시각화 도구 작성 시 고려사항:
   - Streamlit 위젯 사용법 숙지
   - 적절한 차트 타입 선택
   - 사용자 상호작용 고려
