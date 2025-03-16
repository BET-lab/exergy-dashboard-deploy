# Exergy Analysis Dashboard

엑서지 분석을 위한 대시보드 애플리케이션입니다.

## 새로운 시스템 등록하기

이 대시보드는 확장 가능하도록 설계되어 있어, 새로운 시스템을 쉽게 추가할 수 있습니다.

### 시스템 등록 방법

1. 먼저 시스템 템플릿을 가져옵니다:

```python
from exergy_dashboard.system import register_system, get_system_template

# 템플릿 가져오기
template = get_system_template()
```

2. 템플릿을 수정하여 새로운 시스템을 정의합니다:

```python
# 시스템 기본 정보 설정
new_system = template.copy()
new_system['display']['title'] = 'My New Heat Pump'  # 시스템 표시 이름
new_system['display']['icon'] = ':zap:'  # 시스템 아이콘 (이모지)

# 파라미터 추가
new_system['parameters']['T_0'] = {
    'explanation': {
        'EN': 'Environment Temperature',  # 영문 설명
        'KR': '환경온도',  # 한글 설명
    },
    'latex': r'$T_0$',  # LaTeX 수식
    'default': 32.0,  # 기본값
    'range': [-50, 50],  # 값 범위
    'unit': '℃',  # 단위
    'step': 0.5,  # 조정 단위
    'category': 'environment',  # 파라미터 카테고리
}

# 더 많은 파라미터 추가...
```

3. 시스템을 등록합니다:

```python
# 시스템 등록 (모드와 시스템 타입 지정)
register_system('COOLING', 'NEW_HP', new_system)
```

### 필수 필드

시스템 설정에는 다음 필드들이 반드시 포함되어야 합니다:

1. `display`:
   - `title`: 시스템 표시 이름
   - `icon`: 시스템 아이콘 (이모지)

2. `parameters`: 각 파라미터는 다음 필드를 포함해야 합니다
   - `explanation`: 파라미터 설명 (`EN`과 `KR` 필수)
   - `latex`: LaTeX 수식
   - `default`: 기본값
   - `range`: 값 범위 (최소값, 최대값)
   - `unit`: 단위
   - `step`: 조정 단위
   - `category`: 파라미터 카테고리 (선택사항, 기본값: 'General')

### 예시

전체 시스템 등록 예시:

```python
from exergy_dashboard.system import register_system, get_system_template

# 템플릿 가져오기
template = get_system_template()

# 새로운 시스템 정의
new_system = template.copy()
new_system['display'] = {
    'title': 'Advanced Heat Pump',
    'icon': ':zap:',
}

# 파라미터 추가
new_system['parameters'] = {
    'T_0': {
        'explanation': {
            'EN': 'Environment Temperature',
            'KR': '환경온도',
        },
        'latex': r'$T_0$',
        'default': 32.0,
        'range': [-50, 50],
        'unit': '℃',
        'step': 0.5,
        'category': 'environment',
    },
    'efficiency': {
        'explanation': {
            'EN': 'System Efficiency',
            'KR': '시스템 효율',
        },
        'latex': r'$\eta$',
        'default': 0.85,
        'range': [0, 1],
        'unit': '-',
        'step': 0.01,
        'category': 'performance',
    },
}

# 시스템 등록
register_system('COOLING', 'ADVANCED_HP', new_system)
```

## 주의사항

1. 모든 필수 필드를 반드시 포함해야 합니다.
2. 파라미터 이름은 고유해야 합니다.
3. 범위 값은 숫자 또는 다른 파라미터 참조 문자열일 수 있습니다.
4. LaTeX 수식은 올바른 형식이어야 합니다.
