# 10. 최소 동작 예제: 커스텀 시스템 등록

이 문서는 Exergy Dashboard에서 커스텀 시스템을 가장 빠르고 간단하게 등록하는 최소 동작 예제를 제공함. 복사-수정-붙여넣기만으로 동작 가능하도록 안내함.

---

## 10.1 준비 사항
- Python 및 Exergy Dashboard 설치 완료 필요
- `systems/` 폴더에 파일 추가 시 자동 인식 및 임포트됨

---

## 10.2 최소 커스텀 시스템 등록 2단계

### 1) 시스템 정의 및 등록 코드 작성
`systems/my_system.py` 파일 생성 후 아래 코드 복사:

```python
from exergy_dashboard.system import register_system

my_system = {
    'display': {
        'title': '나만의 시스템',
        'icon': ':star:',
    },
    'parameters': {
        'T_in': {
            'explanation': {'EN': 'Inlet Temp', 'KR': '입구 온도'},
            'latex': r'$T_{in}$',
            'default': 60,
            'range': [0, 100],
            'unit': '℃',
            'step': 1,
            'category': 'temperature',
        },
    }
}
register_system('COOLING', 'MY_SYSTEM', my_system)
```

### 2) 평가 함수 작성
동일 파일에 아래 코드 추가:

```python
from exergy_dashboard.evaluation import registry

@registry.register('COOLING', 'MY_SYSTEM')
def evaluate_my_system(params):
    T_in = params['T_in']
    return {'result': T_in * 2}
```

> 이제 `systems/` 폴더에 `*_system.py` 파일을 추가하면 자동으로 임포트되어 별도의 import 작업 없이 대시보드에 반영됨

---

## 10.3 필수 파라미터 필드 요약

| 필드명        | 설명                | 예시 값         |
|---------------|---------------------|-----------------|
| explanation   | 파라미터 설명(영/한) | {'EN': 'Inlet Temp', 'KR': '입구 온도'} |
| latex         | 수식 표기           | r'$T_{in}$'     |
| default       | 기본값              | 60              |
| range         | 허용 범위           | [0, 100]        |
| unit          | 단위                | '℃'             |
| step          | 증분                | 1               |
| category      | 분류(선택)          | 'temperature'   |

---

## 10.4 실행 및 확인
- 터미널에서 대시보드 실행:
  ```bash
  streamlit run app.py
  ```
- 웹 브라우저에서 시스템 추가 및 파라미터 입력 후 결과 확인 가능

> 위 2단계만 따라 하면 커스텀 시스템 등록 및 평가가 바로 동작함. 추가 시각화 등은 7~9번 문서 참고 바람 