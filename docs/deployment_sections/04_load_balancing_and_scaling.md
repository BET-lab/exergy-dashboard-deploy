# 4. 로드 밸런싱 및 확장성 (Ubuntu 22.04 LTS + Nginx 기준)

이 섹션에서는 Exergy Dashboard의 고가용성(HA) 및 확장성을 위한 로드 밸런싱, Auto Scaling, 장애조치, 세션 관리 전략을 다룹니다.

---

## 4.1 L4/L7 로드 밸런서 개념

- **L4(Transport Layer)**: TCP/UDP 레벨에서 트래픽 분산 (ex. HAProxy, AWS ELB)
- **L7(Application Layer)**: HTTP/HTTPS 레벨에서 트래픽 분산, 경로/호스트 기반 라우팅 (ex. Nginx, Traefik)
- **Streamlit 등 웹앱**은 L7(Nginx) 로드밸런싱이 일반적

---

## 4.2 Nginx를 이용한 L7 로드 밸런싱 설정

### 1) App 서버 여러 대에 분산
- `/etc/nginx/sites-available/exergy_dashboard_lb` 예시:
```nginx
upstream exergy_app {
    server 10.0.0.11:8501;
    server 10.0.0.12:8501;
    # 필요시 weight, max_fails, fail_timeout 등 옵션 추가
}

server {
    listen 80;
    server_name your.domain.com;

    location / {
        proxy_pass http://exergy_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
- Nginx 재시작:
```bash
sudo ln -s /etc/nginx/sites-available/exergy_dashboard_lb /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 2) HTTPS 적용은 기존 방식과 동일 (certbot 등)

---

## 4.3 Auto Scaling 및 장애 조치(Failover)

- **클라우드**: AWS EC2 Auto Scaling, GCP Managed Instance Group 등 활용
- **온프레미스**: Ansible, Terraform 등으로 서버 자동 증설/축소 스크립트화
- **Nginx health_check** 모듈(또는 외부 모니터링)로 장애 서버 자동 제외

#### Nginx 단순 장애조치 예시
```nginx
upstream exergy_app {
    server 10.0.0.11:8501 max_fails=3 fail_timeout=30s;
    server 10.0.0.12:8501 max_fails=3 fail_timeout=30s;
}
```

---

## 4.4 세션 관리 전략

- **Streamlit**는 기본적으로 서버리스/무상태(stateless) 구조이나, 사용자별 세션 데이터(session_state)를 사용
- **로드밸런싱 환경**에서는 sticky session(고정 세션) 또는 외부 세션 저장소(Redis 등) 필요할 수 있음

### Nginx sticky session 예시 (ip_hash)
```nginx
upstream exergy_app {
    ip_hash;
    server 10.0.0.11:8501;
    server 10.0.0.12:8501;
}
```
- 또는, Streamlit 세션을 Redis 등 외부 저장소에 연동하는 커스텀 구현 필요

---

> 대규모 서비스에서는 로드밸런서 이중화, 모니터링, 자동 장애조치, 세션 일관성 등도 함께 고려해야 합니다. 