FROM alpine
RUN apk add --no-cache busybox-extras libxml2-utils sqlite mkpasswd

COPY index.cgi /var/www/cgi-bin/

CMD /bin/sh -c '\
  mkdir -p /var/www/bidrag && \
  chmod -R a+w /var/www/bidrag && \
  if [ ! -f /var/www/bidrag/bidrag.db ]; then \
    echo "Oppretter tom bidrag.db..."; \
    sqlite3 /var/www/bidrag/bidrag.db "CREATE TABLE bidrag ( \
      id INTEGER PRIMARY KEY AUTOINCREMENT, \
      pseudonym TEXT NOT NULL, \
      tittel TEXT NOT NULL, \
      tekst TEXT NOT NULL, \
      kommentar TEXT, \
      epost_hash TEXT NOT NULL, \
      passordhash TEXT NOT NULL, \
      salt TEXT NOT NULL \
      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP \
    );"; \
  else \
    echo "Databasen eksisterer – hopper over init."; \
  fi && \
  httpd -p 82 -h /var/www -f -vv'
