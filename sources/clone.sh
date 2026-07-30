#!/usr/bin/env bash
# 분석 대상 디자인 시스템 소스 얕은 클론
# 사용: bash sources/clone.sh [repo-key ...]   (인자 없으면 전체)
set -uo pipefail
cd "$(dirname "$0")"

MIN_FREE_MB=2500

# key|url|sparse-paths(공백구분, 비면 전체 클론)
REPOS='
spectrum-css|https://github.com/adobe/spectrum-css|
spectrum-tokens|https://github.com/adobe/spectrum-design-data|
react-spectrum|https://github.com/adobe/react-spectrum|packages/@adobe packages/@react-spectrum packages/@react-aria packages/@react-stately packages/@react-types
material-web|https://github.com/material-components/material-web|
material-ui|https://github.com/mui/material-ui|packages/mui-material packages/mui-system packages/mui-base packages/mui-utils
fluentui|https://github.com/microsoft/fluentui|packages
carbon|https://github.com/carbon-design-system/carbon|packages
polaris|https://github.com/Shopify/polaris|polaris-react polaris-tokens polaris-icons
shadcn-ui|https://github.com/shadcn-ui/ui|apps/v4 packages
radix-primitives|https://github.com/radix-ui/primitives|
ant-design|https://github.com/ant-design/ant-design|components
'

free_mb() { df -m . | awk 'NR==2{print $4}'; }

clone_one() {
  local key="$1" url="$2" sparse="$3"
  if [ -d "$key/.git" ]; then echo "SKIP   $key (이미 있음)"; return 0; fi
  if [ "$(free_mb)" -lt "$MIN_FREE_MB" ]; then echo "ABORT  $key — 여유 $(free_mb)MB < ${MIN_FREE_MB}MB"; return 2; fi

  if [ -n "$sparse" ]; then
    git clone --depth 1 --single-branch --filter=blob:none --sparse "$url" "$key" -q || { echo "FAIL   $key"; return 1; }
    ( cd "$key" && git sparse-checkout set $sparse ) || { echo "FAIL   $key (sparse)"; return 1; }
  else
    git clone --depth 1 --single-branch "$url" "$key" -q || { echo "FAIL   $key"; return 1; }
  fi
  echo "OK     $key  $(du -sh "$key" | cut -f1)  $(cd "$key" && git rev-parse --short HEAD)"
}

targets="${*:-}"
echo "$REPOS" | while IFS='|' read -r key url sparse; do
  [ -z "${key:-}" ] && continue
  if [ -n "$targets" ]; then case " $targets " in *" $key "*) ;; *) continue;; esac; fi
  clone_one "$key" "$url" "$sparse"
done
echo "--- 완료. 여유: $(free_mb)MB ---"
