# 11. cooling_system.py 상세 분석 및 커스텀 시스템 작성 가이드

이 문서는 `systems/cooling_system.py` 파일을 상세히 분석하고, 사용자가 이를 참고하여 자신만의 커스텀 시스템 파일(`*_system.py`)을 작성할 수 있도록 단계별로 안내함.

---

## 11.1 상수 및 라이브러리 정의
- `c_a`, `rho_a` 등 물리 상수 정의함
- `math`, `pandas`, `altair` 등 필수 라이브러리 import 필요
- 대시보드 핵심 모듈(`register_system`, `eval_registry`, `viz_registry`, `plot_waterfall_multi`) import 필요

---

## 11.2 시스템 딕셔너리 구조

각 시스템은 Python 딕셔너리로 정의함. 주요 필드는 다음과 같음:

| 필드명         | 설명                                 | 예시 값/형식           |
| -------------- | ------------------------------------ | ---------------------- |
| display        | 시스템 표시 정보(이름, 아이콘 등)     | {'title': '...', ...}  |
| parameters     | 파라미터 정의(입력값, 범위 등)        | { ... }                |

### display 예시
```python
'display': {
    'title': 'Air Source Heat Pump',
    'icon': ':snowflake:',
}
```

### parameters 예시 및 필드 설명
각 파라미터는 다음과 같은 필드를 가짐:

| 필드명      | 설명                        | 예시 값/형식                |
| ----------- | --------------------------- | --------------------------- |
| explanation | 영문/한글 설명              | {'EN': '...', 'KR': '...'}  |
| latex       | 수식 표기                   | r'$T_0$'                    |
| default     | 기본값                      | 32.0                        |
| range       | 허용 범위                   | [-50, 50] 또는 식           |
| unit        | 단위                        | '℃', 'kW' 등                |
| step        | 증분 단위                   | 0.5, 0.01 등                |
| category    | 파라미터 분류               | 'environment', 'power' 등   |

---

## 11.3 시스템 등록
- `register_system(모드, 시스템명, 시스템딕셔너리)` 함수로 시스템 등록함
- 예시:
```python
register_system('COOLING', 'ASHP', COOLING_ASHP)
register_system('COOLING', 'GSHP', COOLING_GSHP)
```
- systems/ 폴더에 *_system.py 파일로 저장 시 자동 등록됨

---

## 11.4 평가 함수 등록
- `@eval_registry.register(모드, 시스템명)` 데코레이터로 평가 함수 등록함
- 함수명은 자유, 입력은 params(dict), 반환은 dict로 구성
- 내부에서 파라미터를 꺼내어 계산 수행, 결과를 dict로 반환함
- 예시 템플릿:
```python
@eval_registry.register('COOLING', 'ASHP')
def evaluate_cooling_ashp(params: Dict[str, float]) -> Dict[str, float]:
    # 파라미터 추출
    T_0 = params['T_0']
    ...
    # 계산 로직
    ...
    return { ... }
```
- 반환 dict의 키는 대시보드에서 시각화/출력에 사용됨

---

## 11.5 시각화 함수 등록
- `@viz_registry.register(모드, 시각화명)` 데코레이터로 시각화 함수 등록함
- 입력: session_state, selected_systems
- pandas, altair 등으로 차트 생성 후 반환
- 예시 템플릿:
```python
@viz_registry.register('COOLING', 'Exergy Efficiency')
def plot_exergy_efficiency(session_state: Any, selected_systems: List[str]) -> alt.Chart:
    ...
    return chart
```
- 여러 시스템을 비교하거나, waterfall 등 복합 시각화 가능

---

## 11.6 커스텀 시스템 작성/확장 방법
1. `systems/` 폴더에 새 파일(`*_system.py`) 생성
2. 상단에 상수/필요 라이브러리 import
3. 시스템 딕셔너리 작성 (display, parameters 필수)
4. `register_system`으로 등록
5. 평가 함수/시각화 함수 작성 및 데코레이터로 등록
6. 저장 후 대시보드에서 자동 인식됨

---

## 11.7 참고: 주요 패턴 요약
- 파라미터명, 반환값 등은 자유롭게 설계 가능하나, 일관성 유지 권장
- 파라미터 범위, 단위, 설명 등은 실제 시스템에 맞게 조정 필요
- 복수 시스템/모드 지원 시, 각 시스템별로 딕셔너리/함수 분리 작성
- 복잡한 계산/시각화는 별도 함수로 분리 가능

---

이 문서를 참고하여 자신만의 시스템을 쉽게 구현할 수 있음. 추가적인 예시나 확장 패턴은 기존 cooling_system.py 파일을 참고하거나, 기존 함수/딕셔너리 구조를 복사-수정하여 활용 가능함. 