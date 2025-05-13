# 5. Docker를 이용한 컨테이너화 (docker-compose + 보안)

이 섹션에서는 Exergy Dashboard를 Docker 및 docker-compose로 컨테이너화하는 방법과, 실전 보안 고려사항을 다룹니다.

---

## 5.1 Dockerfile 작성 예시

```dockerfile
# 베이스 이미지: slim, LTS, 보안 패치 최신
FROM python:3.10-slim

# 보안: OS 패키지 최소화, 빌드 중 임시 파일 삭제
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 의존성 분리: 보안 취약점 최소화
COPY pyproject.toml uv.lock ./
RUN pip install --upgrade pip && pip install uv && uv sync

# 앱 소스 복사
COPY . .

# 비권한 사용자로 실행 (보안)
RUN useradd -m appuser
USER appuser

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
```

---

## 5.2 docker-compose.yml 예시 (Nginx + App)

```yaml
version: '3.8'
services:
  app:
    build: .
    container_name: exergy_app
    restart: always
    environment:
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_HEADLESS=true
      # 비밀정보는 .env 파일로 분리 권장
    expose:
      - "8501"
    networks:
      - backend

  nginx:
    image: nginx:1.25-alpine
    container_name: exergy_nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/certs:/etc/letsencrypt:ro
      - ./nginx/.htpasswd:/etc/nginx/.htpasswd:ro
    depends_on:
      - app
    networks:
      - backend
      - frontend

networks:
  backend:
  frontend:
```

- **보안**: 내부 네트워크(backend)와 외부(frontend) 분리, 비밀정보는 .env 파일/Secret Manager 사용 권장

---

## 5.3 Nginx 컨테이너용 nginx.conf 예시 (리버스 프록시 + HTTPS + Basic Auth)

```nginx
user  nginx;
worker_processes  auto;
error_log  /var/log/nginx/error.log warn;
pid        /var/run/nginx.pid;

# ... (events, http 등 기본 설정)

http {
    server {
        listen 80;
        server_name your.domain.com;
        return 301 https://$host$request_uri;
    }
    server {
        listen 443 ssl;
        server_name your.domain.com;

        ssl_certificate /etc/letsencrypt/live/your.domain.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/your.domain.com/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        auth_basic "Restricted";
        auth_basic_user_file /etc/nginx/.htpasswd;

        location / {
            proxy_pass http://app:8501;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

---

## 5.4 운영/보안 팁

- **비밀정보 관리**: 환경변수(.env), Docker Secret, Vault 등 활용, 이미지에 직접 포함 금지
- **최소 권한 원칙**: 컨테이너는 root가 아닌 일반 사용자로 실행
- **네트워크 분리**: 내부/외부 네트워크, DB 등 민감 서비스는 외부 노출 금지
- **이미지 경량화**: 불필요한 패키지/툴 미포함, 멀티스테이지 빌드 활용 가능
- **취약점 점검**: `docker scan`, Trivy 등으로 이미지 보안 점검
- **로그/모니터링**: stdout/stderr 로그 수집, 외부 모니터링 연동
- **자동화**: CI/CD에서 빌드/배포 자동화, 이미지 태그 관리

---

> 컨테이너 환경에서도 정기적 보안 업데이트, 비밀정보 관리, 네트워크 정책 점검을 병행하세요. 