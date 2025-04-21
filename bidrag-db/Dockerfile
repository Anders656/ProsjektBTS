FROM alpine
RUN apk add busybox-extras libxml2-utils sqlite mkpasswd

COPY index.cgi var/www/cgi-bin/

# ✅ Opprett databasen direkte i /data
RUN mkdir -p /data && \
    echo "CREATE TABLE bidrag ( \
        id INTEGER PRIMARY KEY AUTOINCREMENT, \
        pseudonym TEXT NOT NULL, \
        tittel TEXT NOT NULL, \
        tekst TEXT NOT NULL, \
        kommentar TEXT, \
        epost_hash TEXT NOT NULL, \
        passordhash TEXT NOT NULL, \
        salt TEXT NOT NULL \
    );" | sqlite3 /data/bidrag.db
   
RUN chmod a+w /data/bidrag.db
EXPOSE 82
CMD httpd -p 82 -h /var/www -f -vv