#!/bin/sh
DB="/var/www/bidrag/bidrag.db"
echo "Content-Type:text/plain;charset=utf-8"
echo

CONTENT_LENGTH=$HTTP_CONTENT_LENGTH$CONTENT_LENGTH
KR=$(head -c "$CONTENT_LENGTH")

echo "bidrag-db fikk dette i kroppen: $KR" >&2

# Parse XML-felt fra POST/PUT/DELETE
N=$(echo "$KR" | xmllint --xpath "string(/bidrag/pseudonym)" - 2>/dev/null)
E=$(echo "$KR" | xmllint --xpath "string(/bidrag/epost)" - 2>/dev/null)
P=$(echo "$KR" | xmllint --xpath "string(/bidrag/passord)" - 2>/dev/null)
K=$(echo "$KR" | xmllint --xpath "string(/bidrag/kommentar)" - 2>/dev/null)
T=$(echo "$KR" | xmllint --xpath "string(/bidrag/tittel)" - 2>/dev/null)
X=$(echo "$KR" | xmllint --xpath "string(/bidrag/tekst)" - 2>/dev/null)
AP=$(echo "$KR" | xmllint --xpath "string(/bidrag/adminpassord)" - 2>/dev/null)

ADMIN_PASS="hemmelig_admin_passord"

# 🚀 **Beregner epost_hash likt i alle operasjoner**
if [ "$E" != "" ]; then
    EPOST_HASH=$(echo -n "$E" | sha256sum | awk '{print $1}')
else
    EPOST_HASH=""
fi

# -------- GET (brukes av H=Liste) --------
if [ "$REQUEST_METHOD" = "GET" ]; then
    E=$(echo "$HTTP_EMAIL")
    if [ "$E" != "" ]; then
        EPOST_HASH=$(echo -n "$E" | sha256sum | awk '{print $1}')
    else
        EPOST_HASH=""
    fi

    echo "[DEBUG] Henter bidrag for epost_hash='$EPOST_HASH'" >&2

    if [ "$E" = "admin@admin.no" ]; then
        echo "[DEBUG] Admin-visning – viser alle bidrag" >&2
        sqlite3 -line $DB "SELECT pseudonym, tittel, tekst, kommentar FROM bidrag;"
    elif [ "$E" != "" ]; then
        echo "[DEBUG] Bruker-visning – viser kommentar også" >&2
        sqlite3 -line $DB "SELECT tittel, tekst, kommentar FROM bidrag WHERE epost_hash='$EPOST_HASH';"
    else
        echo "[DEBUG] Anonym-visning – kun tittel og tekst" >&2
        sqlite3 -line $DB "SELECT tittel, tekst FROM bidrag;"
    fi
    exit
fi

# -------- POST = opprett nytt bidrag --------
if [ "$REQUEST_METHOD" = "POST" ]; then
    echo "[DEBUG] Lagrer bidrag for '$N' med hash '$EPOST_HASH'" >&2

    # 🚀 **Begrensning: Kun ett bidrag per bruker**
    BIDRAG_EKSISTERER=$(sqlite3 $DB "SELECT COUNT(*) FROM bidrag WHERE epost_hash='$EPOST_HASH';")
    if [ "$BIDRAG_EKSISTERER" -gt 0 ]; then
        echo "[ERROR] Bruker '$N' kan kun ha ett bidrag." >&2
        exit
    fi

    if [ "$N" != "" ] && [ "$P" != "" ] && [ "$T" != "" ]; then
        S=$(for I in $(seq 11); do echo -n $(($RANDOM % 9)); done)
        H=$(mkpasswd -m sha-256 -S $S $P | cut -f4 -d$)
        sqlite3 $DB "INSERT INTO bidrag (pseudonym, salt, passordhash, kommentar, tittel, tekst, epost_hash,timestamp) \
            VALUES ('$N', '$S', '$H', '$K', '$T', '$X', '$EPOST_HASH', CURRENT_TIMESTAMP);"
        echo "[SUCCESS] Bidrag lagret for bruker '$N'."
    else
        echo "[ERROR] Ugyldig POST-data" >&2
    fi
    exit
fi

# -------- PUT = endre bidrag --------
if [ "$REQUEST_METHOD" = "PUT" ]; then
    echo "[DEBUG] PUT forespørsel for epost_hash='$EPOST_HASH'" >&2

    S=$(sqlite3 $DB "SELECT salt FROM bidrag WHERE epost_hash='$EPOST_HASH'")
    if [ "$S" = "" ]; then echo "[ERROR] Salt mangler for bruker '$E'" >&2; exit; fi

    H1=$(mkpasswd -m sha-256 -S $S $P | cut -f4 -d$)
    H2=$(sqlite3 $DB "SELECT passordhash FROM bidrag WHERE epost_hash='$EPOST_HASH'")

    if [ "$H1" != "$H2" ]; then echo "[ERROR] Feil passord for bruker '$E'" >&2; exit; fi

    sqlite3 $DB "UPDATE bidrag SET kommentar='$K', tittel='$T', tekst='$X', timestamp=CURRENT_TIMESTAMP WHERE epost_hash='$EPOST_HASH'"
    echo "[SUCCESS] Bidrag oppdatert for bruker '$E'."
    exit
fi

# -------- DELETE = slett ALLE bidrag fra brukeren --------
if [ "$REQUEST_METHOD" = "DELETE" ]; then
    echo "[DEBUG] DELETE forespørsel for epost_hash='$EPOST_HASH'" >&2

    S=$(sqlite3 "$DB" "SELECT salt FROM bidrag WHERE epost_hash='$EPOST_HASH' LIMIT 1")
    if [ -z "$S" ]; then 
        echo "[ERROR] Ingen bidrag funnet for bruker '$E'" >&2
        exit
    fi

    H1=$(mkpasswd -m sha-256 -S $S $P | cut -f4 -d$)
    H2=$(sqlite3 "$DB" "SELECT passordhash FROM bidrag WHERE epost_hash='$EPOST_HASH' LIMIT 1")

    if [ "$H1" != "$H2" ]; then 
        echo "[ERROR] Feil passord for bruker '$E'" >&2
        exit
    fi

    sqlite3 "$DB" "DELETE FROM bidrag WHERE epost_hash='$EPOST_HASH'"
    echo "[SUCCESS] Alle bidrag fra '$E' slettet" >&2
    exit
fi

echo "[ERROR] Ukjent metode" >&2
