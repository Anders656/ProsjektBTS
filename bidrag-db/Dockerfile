FROM alpine
RUN apk add busybox-extras libxml2-utils sqlite mkpasswd

COPY index.cgi /var/www/cgi-bin/

CMD /bin/sh -c '\
  if [ ! -f /data/bidrag.db ]; then \
    echo "Oppretter tom bidrag.db..."; \
    sqlite3 /data/bidrag.db "CREATE TABLE bidrag ( \
      id INTEGER PRIMARY KEY AUTOINCREMENT, \
      pseudonym TEXT NOT NULL, \
      tittel TEXT NOT NULL, \
      tekst TEXT NOT NULL, \
      kommentar TEXT, \
      epost_hash TEXT NOT NULL, \
      passordhash TEXT NOT NULL, \
      salt TEXT NOT NULL \
    );"; \
  else \
    echo "Databasen eksisterer – hopper over init."; \
  fi && \
  httpd -p 82 -h /var/www -f -vv'
