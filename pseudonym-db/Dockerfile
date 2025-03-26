FROM alpine

# Installer nødvendige verktøy
RUN apk add busybox-extras libxml2-utils sqlite curl mkpasswd

# Kopier CGI-scriptet
COPY index.cgi /var/www/cgi-bin/

# Opprett persistent katalog for database
RUN mkdir /data && chmod 777 /data

# Opprett pseudonym-database
RUN sqlite3 /data/pseudonym.db "\
CREATE TABLE pseudonym ( \
    epost TEXT PRIMARY KEY, \
    pseudonym TEXT NOT NULL, \
    salt TEXT NOT NULL, \
    passordhash TEXT NOT NULL \
);"

# Legg inn eksempelbrukere med passordhash og salt
RUN sqlite3 /data/pseudonym.db "\
INSERT INTO pseudonym (epost, pseudonym, salt, passordhash) VALUES \
('Ante@example.com',    'osiedahs', '1712167670', 'Aw16YyLRWTS0BOoOb7DpvBMeYb444g.kl1a542GYpJA'), \
('Bjart@example.com',   'uozaixav', '1712167671', 'q37QpOdM2jSDeXOVAyiCSzMgy08dI7pLQ1aBElJps48'), \
('Cecilie@example.com', 'olaebaev', '1712167672', 'D0z6dLRTSw.u7tct9zQVBUOCBhPEiFn2Eb./li.oyUA');"

# Eksponer port 83
EXPOSE 83

# Start HTTP-server
CMD ["httpd", "-p", "83", "-h", "/var/www", "-f", "-vv"]
