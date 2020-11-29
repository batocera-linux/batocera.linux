#!/bin/sh

GET_BIN="$(dirname "$0")/../../src/build/batocera-settings-get"
SET_BIN="$(dirname "$0")/../../src/build/batocera-settings-set"
ORIG_CONF="$(dirname "$0")/batocera-test.conf"
CONF=/tmp/batocera-settings-test.conf

ERRORS=""

# Arguments: <message>
add_error() {
  ERRORS="$ERRORS
$1"
}

# Arguments: <key> <expected>
expect_key() {
  ACTUAL="$("$GET_BIN" -f "$CONF" "$1")"
  if [ "$ACTUAL" != "$2" ]; then
    add_error "Expected $1 to be $2, got $ACTUAL"
  fi
}

# Arguments: <key> <value>
write_key() {
  "$SET_BIN" -f "$CONF" "$1" "$2" || add_error "write failed"
}

cp "$ORIG_CONF" "$CONF"

# Read existing key
expect_key kodi.enabled 1

# Read commented key
expect_key splash.screen.enabled ''

# Read key that does not exist
expect_key does.not.exist ''

# Update existing key
write_key kodi.enabled 2
expect_key kodi.enabled 2

# Uncomment key
write_key splash.screen.enabled 1
expect_key splash.screen.enabled 1

# Write an entirely new key
write_key totally.new.key 10
expect_key totally.new.key 10

if [ -n "$ERRORS" ]; then
  echo >&2 "$ERRORS"
  exit 1
else
  echo >&2 OK
fi
