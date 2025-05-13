# 8. 배포 FAQ & 트러블슈팅

실전에서 자주 겪는 배포/운영 문제와 해결법을 Github Actions, Docker, Nginx, 모니터링, 보안 등 각 파트별로 정리합니다.

---

## 8.1 Github Actions

- **Q: scp/ssh 단계에서 Permission denied (publickey) 오류**
  - SSH 키가 서버에 등록되어 있는지, Github Secrets에 올바르게 입력했는지 확인
  - 서버의 `~/.ssh/authorized_keys`에 공개키 추가 필요
  - 서버는 비밀번호 로그인 비활성화 권장

- **Q: docker build/run 단계에서 권한 오류**
  - Docker 그룹 권한, 파일/디렉토리 권한 확인
  - Github Actions Runner에 sudo 권한 필요시 `sudo: true` 옵션 사용

---

## 8.2 Docker & docker-compose

- **Q: docker-compose up 시 포트 충돌**
  - 이미 해당 포트를 사용하는 프로세스가 있는지 `lsof -i :포트번호`로 확인 후 종료

- **Q: 이미지 빌드가 느리거나 실패**
  - 캐시 활용, 불필요한 파일 COPY 최소화, 네트워크 연결 확인

- **Q: 환경변수(.env) 적용이 안 됨**
  - docker-compose.yml에 `env_file` 옵션 추가, .env 파일 경로/포맷 확인

---

## 8.3 Nginx

- **Q: 502 Bad Gateway**
  - app 컨테이너가 정상적으로 실행 중인지, 포트/네트워크 설정 확인
  - Nginx의 proxy_pass 대상이 올바른지 확인

- **Q: HTTPS 인증서 갱신 실패**
  - certbot 로그 확인, 포트 80/443이 외부에 열려 있는지 확인
  - 인증서 경로/권한 확인

---

## 8.4 모니터링/로깅

- **Q: Uptime Kuma/Netdata 접속 불가**
  - 방화벽(UFW 등)에서 포트 허용 여부 확인
  - 컨테이너 로그(`docker-compose logs`)로 에러 메시지 확인

- **Q: 로그가 너무 많아 디스크 부족**
  - 로그 순환(logrotate) 설정, 불필요한 로그 주기적 삭제

---

## 8.5 보안

- **Q: SSH brute force 시도 탐지**
  - fail2ban, UFW 등으로 IP 차단, SSH 포트 변경 고려

- **Q: .env, 인증서 등 민감정보가 깃에 올라감**
  - `.gitignore`에 반드시 추가, 이미 올라간 경우 Github 공식 가이드로 삭제

---

## 참고 링크
- [Github Actions 공식 문서](https://docs.github.com/actions)
- [Docker 공식 문서](https://docs.docker.com/)
- [Nginx 공식 문서](https://nginx.org/)
- [Uptime Kuma](https://github.com/louislam/uptime-kuma)
- [Netdata](https://www.netdata.cloud/)
- [Streamlit 배포 가이드](https://docs.streamlit.io/deploy) 