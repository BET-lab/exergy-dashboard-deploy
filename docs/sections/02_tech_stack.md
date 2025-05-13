# 2. 기술 스택

## 주요 언어 및 프레임워크

- **Python**: 전체 애플리케이션의 핵심 언어로, 데이터 처리, 시스템 등록, 평가, 시각화 등 모든 로직 구현에 사용함.
- **Streamlit**: 대시보드 UI 및 웹 애플리케이션 프레임워크로, 사용자가 웹 브라우저에서 손쉽게 엑서지 분석을 수행 가능하도록 지원함.

### Python 예시

```python
# Python을 이용한 간단한 함수 정의 예시
def add(a, b):
    return a + b
```

### Streamlit 예시

```python
# Streamlit을 이용한 대시보드 실행 예시
import streamlit as st
st.title('Exergy Dashboard')
st.write('엑서지 분석을 시작함.')
```

## 주요 라이브러리 및 도구

- **Altair**: 직관적이고 강력한 데이터 시각화 라이브러리로, 분석 결과를 대시보드 내에서 시각적으로 표현하는 데 활용함.
- **Pandas**: 데이터 처리 및 변환을 위한 표준 라이브러리로, 시스템 파라미터 및 결과 데이터의 관리에 활용함.
- **Dataclasses**: Python의 데이터 구조 정의를 간결하게 해주는 표준 라이브러리로, 시스템/시각화/평가 레지스트리 구현에 사용함.
- **uv**: Python 패키지 의존성 관리 및 실행을 위한 도구로, 빠르고 일관된 환경 구성을 지원함.

### Pandas 예시

```python
import pandas as pd
# 데이터프레임 생성 및 처리 예시
data = {'온도': [20, 21, 22], '압력': [1.0, 1.1, 1.2]}
df = pd.DataFrame(data)
df['온도_차'] = df['온도'] - 20
print(df)
```

### Altair 예시

```python
import altair as alt
import pandas as pd
data = pd.DataFrame({'x': [1, 2, 3], 'y': [10, 20, 30]})
chart = alt.Chart(data).mark_line().encode(x='x', y='y')
chart.show()
```

### Dataclasses 예시

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

### uv 예시

```bash
# uv를 이용한 패키지 설치 및 실행 예시
uv pip install pandas altair
uv venv .venv
uv pip freeze > requirements.txt
```

## 기타 도구

- **Markdown**: 문서화 및 예시 코드 작성에 활용함.
- **Git**: 버전 관리 및 협업 도구로 사용함.

### Git 예시

```bash
git clone https://github.com/your-org/exergy-dashboard-deploy.git
git checkout -b feature/new-system
```

> 위 기술 스택은 확장 및 커스터마이징이 용이하도록 선정함. 추가적인 라이브러리나 도구는 프로젝트의 필요에 따라 자유롭게 도입 가능. 