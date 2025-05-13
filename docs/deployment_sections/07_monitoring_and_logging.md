# 7. 모니터링 및 로깅 (가장 쉬운 도구 중심)

이 섹션에서는 설치와 운영이 매우 쉬운 오픈소스 모니터링 도구(Uptime Kuma, Netdata 등)와 Streamlit 자체 헬스체크, 그리고 기본적인 로깅 방법을 안내합니다.

---

## 7.1 Uptime Kuma로 서비스 헬스 모니터링

- **Uptime Kuma**: 오픈소스 웹 기반 모니터링 툴, Docker로 1분만에 설치 가능
- HTTP, TCP, 포트 등 다양한 방식으로 서비스 상태 체크
- 알림(텔레그램, 슬랙, 이메일 등) 연동 지원

### 설치 예시 (docker-compose)
```yaml
services:
  uptime-kuma:
    image: louislam/uptime-kuma:1
    container_name: uptime-kuma
    restart: always
    ports:
      - "3001:3001"
    volumes:
      - ./uptime-kuma-data:/app/data
```
- 웹 UI 접속: http://your-server-ip:3001
- "New Monitor"에서 Exergy Dashboard의 443/80 포트, 혹은 /health 엔드포인트 등록

---

## 7.2 Netdata로 리소스 실시간 모니터링

- **Netdata**: 서버 CPU, 메모리, 네트워크 등 실시간 대시보드 제공
- 설치 명령 한 줄: `bash <(curl -Ss https://my-netdata.io/kickstart.sh)`
- 웹 UI: http://your-server-ip:19999
- Docker로도 설치 가능

---

## 7.3 Streamlit 헬스체크/로깅

- Streamlit 앱에 `/healthz` 등 헬스체크 엔드포인트 추가 가능
- 기본 stdout/stderr 로그는 docker-compose 로그, 혹은 파일로 리다이렉트 가능
- 예시: `docker-compose logs -f app`

---

## 7.4 운영/보안 팁
- 모니터링/관리 UI는 반드시 방화벽(IP 제한) 또는 VPN 뒤에 두기
- 알림(텔레그램, 슬랙 등) 연동 시 토큰/웹훅은 안전하게 관리
- 로그 파일은 주기적으로 순환/백업, 민감정보 포함 주의
- 너무 복잡한 APM/모니터링 도구보다, "잘 죽었는지/느려졌는지"만 빠르게 알 수 있는 도구부터 적용 추천

---

> Uptime Kuma, Netdata는 설치/운영이 매우 쉽고, 소규모/개인/스타트업 환경에 적합합니다. 대규모 환경에서는 Prometheus, Grafana 등 확장도 가능하지만, 처음에는 위 도구로도 충분합니다. 