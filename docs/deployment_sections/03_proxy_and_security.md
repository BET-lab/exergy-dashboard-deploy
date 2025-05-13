# 3. 프록시 서버 및 보안 (Ubuntu 22.04 LTS + Nginx 기준)

이 섹션에서는 Ubuntu 22.04 LTS 환경에서 Nginx를 활용한 리버스 프록시, HTTPS 적용, 방화벽, 인증/인가 등 실전 보안 설정 방법을 다룹니다.

---

## 3.1 Nginx 리버스 프록시 설정

### 1) Nginx 설치
```bash
sudo apt update
sudo apt install nginx -y
sudo systemctl enable nginx
sudo systemctl start nginx
```

### 2) Streamlit 앱용 리버스 프록시 설정
- `/etc/nginx/sites-available/exergy_dashboard` 파일 생성:
```nginx
server {
    listen 80;
    server_name your.domain.com;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
- 심볼릭 링크 생성 및 Nginx 재시작:
```bash
sudo ln -s /etc/nginx/sites-available/exergy_dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 3.2 HTTPS(SSL/TLS) 인증서 적용

### 1) Let's Encrypt 무료 인증서 발급 및 적용
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your.domain.com
```
- 자동으로 HTTPS 설정 및 인증서 갱신 크론탭 등록
- 방화벽에서 80, 443 포트 허용 필요

---

## 3.3 방화벽 및 네트워크 보안

### 1) UFW(Uncomplicated Firewall) 설정
```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'  # 80, 443
sudo ufw enable
sudo ufw status
```
- App 포트(8501)는 내부에서만 접근 가능하도록 제한(기본 비허용)

### 2) Fail2ban 등 추가 보안
- SSH, Nginx 등 주요 서비스에 대한 brute-force 방지
```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## 3.4 인증/인가(Access Control) 기본 전략

- **Nginx Basic Auth**: 간단한 접근 제어
```bash
sudo apt install apache2-utils -y
sudo htpasswd -c /etc/nginx/.htpasswd admin
```
- Nginx 설정에 추가:
```nginx
location / {
    auth_basic "Restricted";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://127.0.0.1:8501;
    # ... (이전과 동일)
}
```

- **고급 인증/인가**: OAuth2, SSO, JWT 등 외부 인증 서버 연동 가능 (Keycloak, Auth0 등)
- **IP 화이트리스트**: 내부망/특정 IP만 허용하는 설정도 가능

---

> 실제 운영 환경에서는 정기적인 보안 업데이트, 접근 로그 모니터링, 취약점 점검을 병행하세요. 