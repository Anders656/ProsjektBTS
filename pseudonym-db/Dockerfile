FROM alpine

# Installer nødvendige verktøy
RUN apk add --no-cache busybox-extras libxml2-utils sqlite curl mkpasswd

# Opprett nødvendige kataloger og kopier CGI-scriptet
COPY index.cgi /var/www/cgi-bin/

# Startkommando – init og HTTP-server
CMD /bin/sh -c '\
  mkdir -p /var/www/pseudonym && \
  chmod -R a+w /var/www/pseudonym && \
  if [ ! -f /var/www/pseudonym/pseudonym.db ]; then \
    echo "Oppretter tom pseudonym.db..."; \
    sqlite3 /var/www/pseudonym/pseudonym.db "CREATE TABLE pseudonym ( \
      epost TEXT PRIMARY KEY, \
      pseudonym TEXT NOT NULL, \
      salt TEXT NOT NULL, \
      passordhash TEXT NOT NULL \
    );"; \
    sqlite3 /var/www/pseudonym/pseudonym.db "INSERT INTO pseudonym (epost, pseudonym, salt, passordhash) VALUES \
      (\"Ante@example.com\", \"osiedahs\", \"1712167670\", \"Aw16YyLRWTS0BOoOb7DpvBMeYb444g.kl1a542GYpJA\"), \
      (\"Bjart@example.com\", \"uozaixav\", \"1712167671\", \"q37QpOdM2jSDeXOVAyiCSzMgy08dI7pLQ1aBElJps48\"), \
      (\"Cecilie@example.com\", \"olaebaev\", \"1712167672\", \"D0z6dLRTSw.u7tct9zQVBUOCBhPEiFn2Eb./li.oyUA\");"; \
  else \
    echo "Databasen eksisterer – hopper over init."; \
  fi && \
  httpd -p 83 -h /var/www -f -vv'
