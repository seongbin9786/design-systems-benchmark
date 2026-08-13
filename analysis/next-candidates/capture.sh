#!/bin/bash
# targets.txt 의 각 줄(name|url|mode)을 playwright CLI 로 캡처한다.
# 사용: bash capture.sh [병렬수]
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"
OUT="$DIR/captures"
mkdir -p "$OUT"
PAR="${1:-4}"

capture_one() {
  line="$1"
  name="${line%%|*}"
  rest="${line#*|}"
  url="${rest%%|*}"
  mode="${rest##*|}"
  out="$OUT/$name.png"
  if [ "$mode" = "mobile" ]; then
    npx playwright screenshot --device="iPhone 13" --wait-for-timeout=8000 "$url" "$out" >/dev/null 2>&1
  else
    npx playwright screenshot --viewport-size=1440,900 --wait-for-timeout=8000 "$url" "$out" >/dev/null 2>&1
  fi
  if [ -s "$out" ]; then
    echo "OK   $name"
  else
    echo "FAIL $name $url"
  fi
}
export -f capture_one
export OUT

grep -v '^#' "$DIR/targets.txt" | grep -v '^$' | xargs -P "$PAR" -I {} bash -c 'capture_one "$@"' _ {}
