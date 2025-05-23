# 2. 애플리케이션 배포 전략

이 섹션에서는 Exergy Dashboard의 실제 운영 환경에서 사용할 수 있는 다양한 배포 전략을 다룹니다.

---

## 2.1 단일 서버 배포

- **특징**: 모든 구성요소(앱, 프록시, DB 등)를 한 서버에 설치
- **장점**: 설정이 간단, 소규모/테스트 환경에 적합
- **단점**: 장애 시 전체 서비스 중단, 확장성 한계

### 배포 예시
- App: Streamlit 앱(8501), 프록시(Nginx, 80/443), DB(내부 또는 외부)
- 방화벽: 외부는 80/443만 오픈, 내부 포트 제한

---

## 2.2 멀티 서버/분산 환경 배포

- **특징**: 프론트엔드, 백엔드, DB, 프록시 서버를 분리하여 운영
- **장점**: 장애 격리, 확장성, 보안성 향상
- **단점**: 네트워크/운영 복잡도 증가

### 구성 예시
- Reverse Proxy(Nginx/Apache) → App 서버(여러 대) → DB 서버(별도)
- 각 서버는 별도 방화벽/보안그룹 적용
- App 서버 수평 확장(로드 밸런싱)

---

## 2.3 무중단 배포(Blue-Green, Rolling 등) 개요

- **Blue-Green 배포**: 두 개의 환경(Blue/Green)을 번갈아가며 배포, 트래픽 전환으로 무중단 서비스
- **Rolling 배포**: 서버를 순차적으로 업데이트, 전체 중단 없이 점진적 배포

### 적용 방법
- Nginx/로드밸런서에서 트래픽 분기 설정
- Docker Compose, Kubernetes 등 오케스트레이션 도구 활용
- 배포 자동화(CI/CD)와 연계 시 효과적

---

## 2.4 배포 자동화 및 관리 팁

- 배포 스크립트, Ansible 등 IaC(Infrastructure as Code) 도구 활용 권장
- 배포 전후 헬스체크, 롤백 전략 필수
- 배포 로그/이력 관리, 알림 시스템 연동

> 실제 운영 환경에서는 서비스 규모, 예산, 인력에 따라 적합한 배포 전략을 선택하세요. 