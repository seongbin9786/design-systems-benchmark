#!/usr/bin/env bash
# 차기 벤치마킹 후보(1군, 2군) 소스 얕은 클론
# 사용: bash sources-candidates/clone.sh
# 완료 후 MANIFEST.md 에 실측 SHA 를 기록한다.
set -uo pipefail
cd "$(dirname "$0")"

# key|url|sparse-paths(공백구분, 비면 전체 클론)
REPOS='
baseweb|https://github.com/uber/baseweb|
primer-react|https://github.com/primer/react|
primer-primitives|https://github.com/primer/primitives|
mantine|https://github.com/mantinedev/mantine|packages/@mantine/core
semi-design|https://github.com/DouyinFE/semi-design|packages/semi-ui packages/semi-foundation packages/semi-theme-default
ant-design-mobile|https://github.com/ant-design/ant-design-mobile|
seed-design|https://github.com/daangn/seed-design|
abc-def|https://github.com/line/abc-def|
vkui|https://github.com/VKCOM/VKUI|packages/vkui
'

clone_one() {
  local key="$1" url="$2" sparse="$3"
  if [ -d "$key/.git" ]; then
    echo "SKIP   $key (이미 존재)"
    return 0
  fi
  if [ -n "$sparse" ]; then
    git clone --depth 1 --single-branch --filter=blob:none --sparse "$url" "$key" -q \
      || { echo "FAIL   $key"; return 1; }
    git -C "$key" sparse-checkout set $sparse || { echo "FAIL   $key (sparse)"; return 1; }
  else
    git clone --depth 1 --single-branch "$url" "$key" -q || { echo "FAIL   $key"; return 1; }
  fi
  echo "OK     $key  $(du -sh "$key" | cut -f1)  $(git -C "$key" rev-parse --short HEAD)"
}

# 4개씩 병렬 클론
i=0
echo "$REPOS" | grep -v '^$' | {
  while IFS='|' read -r key url sparse; do
    clone_one "$key" "$url" "$sparse" &
    i=$((i+1))
    if [ $((i % 4)) -eq 0 ]; then wait; fi
  done
  wait
}

# MANIFEST 기록
{
  echo "# 후보 소스 고정 커밋 (자동 생성: clone.sh)"
  echo
  echo "| key | commit | date |"
  echo "|---|---|---|"
  echo "$REPOS" | grep -v '^$' | while IFS='|' read -r key url sparse; do
    [ -d "$key/.git" ] || continue
    echo "| \`$key\` | \`$(git -C "$key" rev-parse HEAD)\` | $(git -C "$key" log -1 --format=%cs) |"
  done
} > MANIFEST.md
echo "--- 완료. MANIFEST.md 기록됨 ---"
