#!/bin/sh

DB="/data/pseudonym.db"

echo 'Access-Control-Allow-Origin: http://localhost:8080'
echo 'Access-Control-Allow-Credentials: true'
echo 'Access-Control-Allow-Methods: GET,POST,PUT,DELETE'
echo 'Access-Control-Allow-Headers: Content-Type'

echo "Content-Type:text/plain;charset=utf-8"
echo

if [ "$REQUEST_METHOD" != "POST" ]; then exit; fi

CONTENT_LENGTH=$HTTP_CONTENT_LENGTH$CONTENT_LENGTH

KR=$(head -c "$CONTENT_LENGTH")
echo "pseudonym-db fikk dette i kroppen: $KR" >&2

E=$(echo "$KR" | xmllint --xpath "/pseudonym/epost/text()" - 2>/dev/null)
P=$(echo "$KR" | xmllint --xpath "/pseudonym/passord/text()" - 2>/dev/null)

S=$(sqlite3 $DB "SELECT salt FROM pseudonym WHERE epost='$E'")
if [ "$S" = "" ]; then 
  echo "Salt mangler, finnes ikke bruker: $E?" >&2
  exit
fi

H1=$(mkpasswd -m sha-256 -S $S $P | cut -f4 -d$)
H2=$(sqlite3 $DB "SELECT passordhash FROM pseudonym WHERE epost='$E'")

if [ "$H1" != "$H2" ]; then 
  echo "Feil passord for bruker: $E" >&2
  exit
fi

PN=$(sqlite3 $DB "SELECT pseudonym FROM pseudonym WHERE epost='$E'")
echo "Fant pseudonym: $PN for bruker: $E" >&2
echo $PN
