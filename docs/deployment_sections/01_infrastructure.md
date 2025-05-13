# 1. 서버 환경 및 인프라 설계

이 섹션에서는 Exergy Dashboard의 안정적이고 확장 가능한 운영을 위한 서버 환경 및 인프라 설계 방안을 다룹니다.

---

## 1.1 온프레미스 vs 클라우드 환경 비교

| 항목         | 온프레미스(자체 서버)         | 클라우드(AWS, GCP, Azure 등)   |
|--------------|-------------------------------|-------------------------------|
| 초기 비용    | 서버 구매/구축 필요           | 사용량 기반 과금, 초기비용 낮음 |
| 확장성       | 물리적 한계, 증설 시간 소요    | 손쉬운 확장/축소, Auto Scaling |
| 유지보수     | 직접 관리(보안, 백업 등)      | 클라우드 사업자 관리           |
| 네트워크     | 내부망/전용선 등 직접 구성     | 글로벌 네트워크 인프라 활용    |
| 장애 대응    | 자체 인력 필요                | SLA, 자동 장애 조치 지원       |

- **권장**: PoC/소규모는 클라우드, 대규모/보안 특화는 온프레미스 또는 하이브리드 권장

---

## 1.2 권장 서버 사양 및 네트워크 구성

- **CPU**: 2코어(테스트) ~ 4코어 이상(운영)
- **RAM**: 4GB(최소) ~ 8GB 이상(권장)
- **디스크**: SSD 20GB 이상, 데이터/로그 분리 권장
- **네트워크**: 1Gbps 이상, 방화벽/보안그룹 설정 필수
- **백업**: 정기적 스냅샷/DB 백업 권장

### 네트워크 구성 예시
- DMZ(공개망) + 내부망 분리
- Reverse Proxy(프록시 서버) → App 서버 → DB 서버
- 방화벽: 80/443(Proxy), 8501(App, 내부), DB(내부)

---

## 1.3 운영체제 및 필수 패키지 설치

- **운영체제**: Ubuntu 22.04 LTS, CentOS 8, Amazon Linux 등 최신 LTS 권장
- **필수 패키지**:
  - Python 3.8 이상
  - pip, uv, venv/conda
  - Docker, docker-compose (컨테이너화 시)
  - git, curl, wget, unzip 등
  - (보안) ufw/firewalld, fail2ban 등

### 설치 예시 (Ubuntu)
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv git curl ufw -y
# Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

> 실제 운영 환경에서는 보안 패치, 계정 관리, 접근 제어 등도 반드시 함께 고려해야 합니다. 