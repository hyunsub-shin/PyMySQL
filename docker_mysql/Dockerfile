# MySQL 8.0 버전을 기본 이미지로 사용
FROM mysql:8.0

# 시스템 설정
ENV TZ=Asia/Seoul

# MySQL 설정 파일 복사 (필요한 경우)
COPY my.cnf /etc/mysql/conf.d/

# 초기화 SQL 스크립트 복사
COPY init.sql /docker-entrypoint-initdb.d/

# MySQL 포트 노출
EXPOSE 3307

# 볼륨 설정
VOLUME ["/var/lib/mysql"] 