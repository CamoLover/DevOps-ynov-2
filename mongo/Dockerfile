FROM mongo:7.0

RUN groupadd -r mongouser && useradd -r -g mongouser mongouser

COPY init-scripts/ /docker-entrypoint-initdb.d/

RUN chown -R mongouser:mongouser /docker-entrypoint-initdb.d/

EXPOSE 27017