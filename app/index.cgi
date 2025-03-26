#!/bin/sh
echo "Content-Type:text/plain;charset=utf-8"
echo

# Avslutter om HTTP-forespørsel ikke er en POST
if [ "$REQUEST_METHOD" != "POST" ]; then exit; fi

# Omgår bug i httpd
CONTENT_LENGTH=$HTTP_CONTENT_LENGTH$CONTENT_LENGTH

# Henter data fra HTTP-kroppen
KROPP=$(head -c "$CONTENT_LENGTH")
KROPP=$(echo $KROPP | sed "s/%40/@/")
KROPP=$(echo "$KROPP" | sed -e 's/+/ /g;s/%\(..\)/\\x\1/g;' | xargs -0 printf "%b")


# Til loggen
echo "app fikk dette i kroppen: $KROPP" >&2

# Fordeler inndataene i variabler
for I in $(echo $KROPP | tr '&' ' '); do
    N=$(echo "$I" | cut -f1 -d=)
    V=$(echo "$I" | cut -f2 -d=)

    if [ "$N" = "epost"            ]; then  E="$V"; fi  
    if [ "$N" = "passord"          ]; then  P="$V"; fi  
    if [ "$N" = "kommentar"        ]; then  K="$V"; fi
    if [ "$N" = "offentlig_nokkel" ]; then  O="$V"; fi
    if [ "$N" = "tittel"           ]; then  T="$V"; fi
    if [ "$N" = "tekst"            ]; then  X="$V"; fi
    if [ "$N" = "handling"         ]; then  H="$V"; fi  
done

### 1. HENT PSEUDONYM FRA pseudonym-db ###

XML="<pseudonym>
  <epost>$E</epost>
  <passord>$P</passord>
</pseudonym>"

URL='allpodd:83'

# Til loggen
cat <<EOF >&2
PN-URL: $URL
PN-XML:
$XML
EOF

# Henter pseudonym
N=$(curl -s -d "$XML" $URL)

### 2. BYGG XML FOR bidrag-db ###

XML="<bidrag>
  <pseudonym>$N</pseudonym>
  <epost>$E</epost>
  <passord>$P</passord>
  <kommentar>$K</kommentar>
  <offentlig_nokkel>$O</offentlig_nokkel>
  <tittel>$T</tittel>
  <tekst>$X</tekst>
</bidrag>"

URL='allpodd:82'

### 3. Send til bidrag-db basert på handling ###

if [ "$H" = "Slett" ]; then curl -s -X DELETE -d "$XML" $URL; fi     
if [ "$H" = "Endre" ]; then curl -s -X PUT    -d "$XML" $URL; fi
if [ "$H" = "Ny"    ]; then curl -s -X POST   -d "$XML" $URL; fi
if [ "$H" = "Liste" ]; then curl -s -X GET         -H "email: $E" $URL; fi

# Til loggen
cat <<EOF >&2
BIDRAG-URL: $URL
BIDRAG-XML:
$XML
EOF
