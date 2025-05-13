# 4. 폴더 및 파일 구조

## 주요 폴더/파일 설명

```
exergy-dashboard-deploy/
├── app.py                  # Streamlit 기반 대시보드 메인 실행 파일
├── pyproject.toml          # Python 프로젝트 및 의존성 관리 파일
├── uv.lock                 # uv 패키지 매니저 lock 파일
├── README.md               # 프로젝트 기본 설명서
├── docs/                   # 공식 문서 및 가이드 폴더
│   └── sections/           # 각 문서화 항목별 세부 문서 폴더
├── src/
│   └── exergy_dashboard/   # 핵심 라이브러리 소스 코드
│       ├── system.py           # 시스템 등록/관리 모듈
│       ├── evaluation.py       # 평가 함수 등록/관리 모듈
│       └── visualization.py    # 시각화 함수 등록/관리 모듈
├── systems/                # 사용자 정의 시스템/평가/시각화 코드 (자동 임포트)
├── notebooks/              # 실험/테스트/분석용 Jupyter 노트북
└── .gitignore              # Git 버전관리 제외 파일 목록
```

## 각 디렉터리 역할 및 예시

- **app.py**: Streamlit 대시보드의 진입점임. 전체 UI 및 사용자 상호작용 관리
    - 예시: 대시보드 실행
    ```bash
    streamlit run app.py
    ```
- **src/exergy_dashboard/**: 시스템, 평가, 시각화 등 핵심 기능을 담당하는 라이브러리 코드 위치함
    - `system.py`: 시스템 등록 및 관리 레지스트리 구현 파일
        - 예시: 시스템 등록 함수 임포트
        ```python
        from exergy_dashboard.system import register_system
        ```
    - `evaluation.py`: 평가 함수 등록 및 관리 레지스트리 구현 파일
        - 예시: 평가 함수 등록
        ```python
        from exergy_dashboard.evaluation import registry as eval_registry
        @eval_registry.register('HEATING', 'ASHP')
        def evaluate_heating_ashp(params):
            # ...
            pass
        ```
    - `visualization.py`: 시각화 함수 등록 및 관리 레지스트리 구현 파일
        - 예시: 시각화 함수 등록
        ```python
        from exergy_dashboard.visualization import registry
        @registry.register('COOLING', 'Exergy Efficiency')
        def plot_exergy_efficiency(session_state, selected_systems):
            # ...
            pass
        ```
- **systems/**: 사용자 정의 시스템/평가/시각화 코드 저장 위치 (파일명: *_system.py, 자동 임포트)
    - 예시: 커스텀 시스템 등록 예제
    ```python
    # systems/my_system.py
    from exergy_dashboard.system import register_system
    my_system = {
        'display': {'title': '나만의 시스템', 'icon': ':star:'},
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
    - systems/ 폴더에 *_system.py 파일을 추가하면 별도 import 없이 자동으로 대시보드에 반영됨
- **notebooks/**: 분석, 실험, 테스트용 Jupyter 노트북 저장
    - 예시: 노트북 파일 생성
    ```bash
    jupyter notebook notebooks/analysis_example.ipynb
    ```
- **docs/**: 공식 문서, 가이드, 목차 등 문서화 자료 저장
    - `sections/`: 각 문서화 항목별 세부 문서 저장
    - 예시: 문서 추가
    ```bash
    touch docs/sections/11_new_section.md
    ```
- **README.md**: 프로젝트 개요, 설치법, 간단 사용법 등 기본 안내 제공
    - 예시: 프로젝트 정보 확인
    ```bash
    cat README.md
    ```
- **pyproject.toml, uv.lock**: Python 패키지 및 의존성 관리 파일
    - 예시: 의존성 설치
    ```bash
    uv pip install -r requirements.txt
    ```
- **.gitignore**: Git 버전관리에서 제외할 파일 목록 정의
    - 예시: .gitignore에 파일 추가
    ```bash
    echo "*.pyc" >> .gitignore
    ```

> 폴더 구조는 확장성과 유지보수성을 고려하여 설계함. 각 디렉터리의 역할을 명확히 하여, 새로운 기능 추가 및 협업이 용이함. 