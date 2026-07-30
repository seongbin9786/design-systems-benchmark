#!/usr/bin/env bash
# 분석 대상 디자인 시스템 소스 얕은 클론
# 사용: bash sources/clone.sh [repo-key ...]   (인자 없으면 전체)
#
# MANIFEST.md 의 전체 SHA 를 fetch 해 체크아웃한다. 이게 없으면 상류 기본 브랜치가 움직인 뒤
# 재실행할 때 다른 코드를 받게 되고, 리포트가 주장하는 "고정 커밋" 이 거짓이 된다.
# 이미 받아둔 클론도 HEAD 가 매니페스트와 다르면 맞춘다 (무조건 SKIP 하지 않는다).
set -uo pipefail
cd "$(dirname "$0")"

MIN_FREE_MB=2500
MANIFEST="MANIFEST.md"

# key|url|sparse-paths(공백구분, 비면 전체 클론)
# sparse 경로는 MANIFEST.md 의 실측값과 일치해야 한다 — 다르면 다른 파일 집합을 측정하게 된다.
REPOS='
spectrum-css|https://github.com/adobe/spectrum-css|
spectrum-tokens|https://github.com/adobe/spectrum-design-data|
react-spectrum|https://github.com/adobe/react-spectrum|packages/@adobe packages/@react-aria packages/@react-spectrum packages/@react-stately packages/@react-types
material-web|https://github.com/material-components/material-web|
material-ui|https://github.com/mui/material-ui|packages/mui-material packages/mui-styled-engine packages/mui-system packages/mui-utils
fluentui|https://github.com/microsoft/fluentui|packages/react-components packages/tokens
carbon|https://github.com/carbon-design-system/carbon|packages/colors packages/elements packages/grid packages/layout packages/motion packages/react packages/styles packages/themes packages/type
polaris|https://github.com/Shopify/polaris|polaris-react polaris-tokens
shadcn-ui|https://github.com/shadcn-ui/ui|apps/v4/app apps/v4/lib apps/v4/registry apps/v4/styles packages
radix-primitives|https://github.com/radix-ui/primitives|
ant-design|https://github.com/ant-design/ant-design|components
'

free_mb() { df -m . | awk 'NR==2{print $4}'; }

# MANIFEST.md 표에서 key 의 전체 SHA 를 읽는다. 없으면 빈 문자열.
manifest_sha() {
  [ -f "$MANIFEST" ] || return 0
  awk -F'|' -v k="$1" '
    $2 ~ "`"k"`" {
      for (i = 3; i <= NF; i++) if ($i ~ /`[0-9a-f]{40}`/) { gsub(/[` ]/, "", $i); print $i; exit }
    }' "$MANIFEST"
}

# 매니페스트 SHA 로 맞춘다. 실패하면 조용히 HEAD 를 쓰지 않고 경고한다.
pin() {
  local key="$1" sha="$2" cur
  if [ -z "$sha" ]; then
    echo "WARN   $key — MANIFEST 에 전체 SHA 가 없어 원격 HEAD 를 씁니다 (재현 불가)"
    return 0
  fi
  cur=$(git -C "$key" rev-parse HEAD 2>/dev/null)
  [ "$cur" = "$sha" ] && return 0
  if git -C "$key" fetch --depth 1 -q origin "$sha" 2>/dev/null \
     && git -C "$key" checkout -q --detach FETCH_HEAD 2>/dev/null; then
    return 0
  fi
  echo "WARN   $key — SHA ${sha:0:7} 체크아웃 실패. 현재 HEAD $(git -C "$key" rev-parse --short HEAD)"
  echo "         상류에서 커밋이 사라졌거나 서버가 SHA fetch 를 막는 경우입니다."
  echo "         이 상태로 측정하면 MANIFEST 와 어긋납니다 — MANIFEST 를 갱신하세요."
  return 1
}

apply_sparse() {
  local key="$1"; shift
  [ $# -eq 0 ] && return 0
  git -C "$key" sparse-checkout set "$@"
}

clone_one() {
  local key="$1" url="$2" sparse="$3" sha
  sha=$(manifest_sha "$key")

  if [ -d "$key/.git" ]; then
    if [ -n "$sha" ] && [ "$(git -C "$key" rev-parse HEAD 2>/dev/null)" = "$sha" ]; then
      echo "SKIP   $key (이미 매니페스트 SHA ${sha:0:7})"
      return 0
    fi
    echo "PIN    $key (기존 클론을 매니페스트 SHA 로 맞춤)"
    if ! pin "$key" "$sha"; then
      echo "FAIL   $key — 매니페스트 SHA 로 맞추지 못했습니다. 이 상태로 측정하면 안 됩니다."
      return 1
    fi
    echo "OK     $key  $(du -sh "$key" | cut -f1)  $(git -C "$key" rev-parse --short HEAD)"
    return 0
  fi

  if [ "$(free_mb)" -lt "$MIN_FREE_MB" ]; then
    echo "ABORT  $key — 여유 $(free_mb)MB < ${MIN_FREE_MB}MB"
    return 2
  fi

  if [ -n "$sparse" ]; then
    git clone --depth 1 --single-branch --filter=blob:none --sparse "$url" "$key" -q \
      || { echo "FAIL   $key"; return 1; }
    apply_sparse "$key" $sparse || { echo "FAIL   $key (sparse)"; return 1; }
  else
    git clone --depth 1 --single-branch "$url" "$key" -q || { echo "FAIL   $key"; return 1; }
  fi
  if ! pin "$key" "$sha"; then
    echo "FAIL   $key — 클론은 됐지만 매니페스트 SHA 로 맞추지 못했습니다."
    return 1
  fi
  echo "OK     $key  $(du -sh "$key" | cut -f1)  $(git -C "$key" rev-parse --short HEAD)"
}

targets="${*:-}"
# `echo | while` 은 서브셸이라 카운터 변수가 살아남지 못한다 — 실패를 임시 파일로 센다.
fail_log=$(mktemp)
trap 'rm -f "$fail_log"' EXIT

echo "$REPOS" | while IFS='|' read -r key url sparse; do
  [ -z "${key:-}" ] && continue
  if [ -n "$targets" ]; then case " $targets " in *" $key "*) ;; *) continue;; esac; fi
  clone_one "$key" "$url" "$sparse" || echo "$key" >> "$fail_log"
done

echo "--- 완료. 여유: $(free_mb)MB ---"
if [ -s "$fail_log" ]; then
  echo
  echo "실패: $(tr '\n' ' ' < "$fail_log")"
  echo "이 소스는 MANIFEST.md 와 어긋난 상태입니다. 측정 파이프라인을 돌리지 마세요."
  echo "MANIFEST 를 갱신하거나 해당 클론을 지우고 다시 받으세요."
  exit 1
fi
