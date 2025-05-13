# 6. 설치 및 실행 방법

이 섹션에서는 Exergy Dashboard를 설치하고 실행하는 방법을 단계별로 기술문서 스타일로 자세히 안내한다. 개발 환경과 운영 환경 모두를 고려한 팁도 포함함.

---

## 6.1 환경 세팅

### 1) Python 환경 준비
- Python 3.8 이상 권장
- 가상환경(venv, conda 등) 사용 추천

#### 예시: venv로 가상환경 생성
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2) 소스코드 다운로드
- GitHub 등에서 소스코드 클론 또는 zip 파일 다운로드 후 압축 해제

```bash
git clone <레포지토리 주소>
cd exergy-dashboard-deploy
```

---

## 6.2 의존성 설치

### 1) uv 패키지 매니저 사용
- 본 프로젝트는 [uv](https://github.com/astral-sh/uv) 패키지 매니저 사용 (pip도 사용 가능)
- `pyproject.toml`과 `uv.lock` 파일 기반으로 모든 의존성 설치함

#### 의존성 설치
```bash
uv sync
```

### 2) pip로 설치 (대체 방법)
```bash
pip install .  # requirements.txt 제공 시
```

---

## 6.3 애플리케이션 실행

### 1) 커스텀 시스템/평가/시각화 자동 임포트
- `systems/` 폴더에 *_system.py 파일을 추가하면 자동으로 임포트 및 등록됨
- 별도의 import 작업 없이 대시보드에 반영됨

### 2) Streamlit 앱 실행
```bash
uv run streamlit run app.py
```
- 또는 일반적으로:
```bash
streamlit run app.py
```

### 3) 웹 브라우저에서 접속
- 기본적으로 `http://localhost:8501`에서 대시보드에 접속 가능

---

## 6.4 개발/운영 환경 팁

- **자동 새로고침**: Streamlit은 코드 변경 시 자동으로 앱을 새로고침함. 필요시 수동으로 새로고침(`R` 키)도 가능
- **포트 변경**: 여러 인스턴스를 띄우거나 포트 충돌 시 `--server.port` 옵션 사용 가능
  ```bash
  streamlit run app.py --server.port 8502
  ```
- **환경 변수**: Streamlit 설정, 디버깅, 로깅 등은 환경 변수로 제어 가능
- **패키지 추가**: 새로운 패키지 설치 후 `uv sync` 또는 `pip install` 실행, 필요시 `pyproject.toml`/`requirements.txt`에 반영
- **Jupyter 노트북 활용**: `notebooks/` 폴더에서 실험/테스트/분석 수행 가능

---

> 설치 및 실행 과정에서 문제가 발생하면 FAQ 문서 또는 README.md의 문제 해결 가이드 참고