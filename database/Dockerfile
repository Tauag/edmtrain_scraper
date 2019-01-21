FROM mysql:8.0

ENV MYSQL_DATABASE database

COPY InitDatabase.sql /docker-entrypoint-initdb.d/

VOLUME ["/data"]