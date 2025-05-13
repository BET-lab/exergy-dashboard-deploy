# 6. CI/CD 및 자동화 배포 (Github Actions만 사용)

이 섹션에서는 Github Actions만을 활용한 CI/CD 및 자동화 배포 방법을 다룹니다. 외부 레지스트리(Docker Hub 등) 없이, Github Actions에서 직접 서버로 배포하는 실전 예시와 보안 팁을 제공합니다.

---

## 6.1 Github Actions 워크플로우 개요

- **빌드/테스트/배포**를 Github Actions에서 자동화
- Docker 이미지 빌드 및 서버로 직접 전송(ssh/scp)
- Secrets(GITHUB_TOKEN, SSH_KEY 등)으로 민감정보 보호
- 외부 레지스트리 미사용: 서버에 직접 배포

---

## 6.2 예시: Github Actions 워크플로우 (deploy.yml)

```yaml
name: CI/CD Deploy
on:
  push:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Build Docker image
        run: docker build -t exergy-dashboard:latest .

      - name: Save Docker image as tar
        run: docker save exergy-dashboard:latest -o exergy-dashboard.tar

      - name: Copy image to server (scp)
        uses: appleboy/scp-action@v0.1.7
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SERVER_SSH_KEY }}
          source: "exergy-dashboard.tar"
          target: "~/deploy/"

      - name: Remote deploy (ssh)
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SERVER_SSH_KEY }}
          script: |
            cd ~/deploy
            docker load -i exergy-dashboard.tar
            docker-compose down
            docker-compose up -d --force-recreate
            docker image prune -f
```

### 주요 포인트
- **Secrets**: Github 저장소의 Settings > Secrets에 SSH 키, 서버 정보 등록
- **appleboy/scp-action, ssh-action**: 서버로 파일 전송 및 원격 명령 실행
- **외부 레지스트리 불필요**: 이미지 tar 파일로 직접 전송/배포
- **보안**: SSH 키는 반드시 Secrets로 관리, 서버는 공개키 인증만 허용

---

## 6.3 보안 및 운영 팁
- Github Actions Secrets에 민감정보(SSH 키, 서버 IP 등)만 저장, 코드에 노출 금지
- 서버는 SSH 공개키 인증만 허용, 비밀번호 로그인 비활성화
- 배포 후 불필요한 이미지/파일 정리(docker image prune 등)
- Github Actions 권한 최소화(필요한 권한만 부여)
- 서버 방화벽(UFW 등)으로 Github Actions Runner IP만 허용(가능하다면)

---

> Github Actions만으로도 안전하고 효율적인 자동화 배포가 가능합니다. 외부 레지스트리 없이 tar 파일로 직접 배포하면, 사설망/내부망 환경에도 적합합니다. 