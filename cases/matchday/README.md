# 사례: matchday-saas — 상용 제품(Spotify)에서 추출한 디자인 시스템의 실물

[playbook.md](../../playbook.md)의 각 단계가 실제로 출력한 산출물의 **사본**이다.
포인터가 아니라 실물을 동봉한다 — 원본 repo(matchday-saas, private)에 접근하지 않고도
이 폴더만으로 사례를 읽을 수 있게.

## 파일과 출처

| 파일 | 단계 | 출처 (repo · 커밋/브랜치 · 스냅샷 일자) |
|---|---|---|
| `design.md` | C 규칙 번역 | matchday-saas `docs/design.md` · main · 2026-07-27 |
| `encore-readme.md` | C 규칙 번역 | matchday-design `README.md` (Encore 디자인 언어 + 벤치마크 교훈→적용 대응표) · 2026-07-27 |
| `globals.2tier.css` | D 토큰 (1차: semantic 단층) | matchday-saas `packages/design-system/src/styles/globals.css` · main · 2026-07-27 |
| `globals.3tier.css` | D 토큰 (2차: primitive→semantic 재편) | matchday-saas 동일 경로 · `design/mobile-first-refresh` 브랜치 |
| `design-qa.md` | F 검증 | matchday-saas `design-qa.md` (Spotify 레퍼런스 대비 픽셀 QA 로그, passed) · main |
| `design-system.html` | G 시각 레퍼런스 | matchday-saas `docs/design-system.html` (PR #126, `design/mobile-first-refresh` 브랜치 사본) — 자기 완결 단일 파일 932KB, 11개 섹션, 적용 화면 29개. 브라우저로 열 것 |
| `design-system-changelog.md` | H (이력 전체) | matchday-saas `docs/design-system-changelog.md` (PR #127, `docs/design-system-changelog` 브랜치) — 작성자가 남긴 9단계 구축 이력 |

## 읽는 순서 (playbook 단계 순)

1. `encore-readme.md` → `design.md` — 시각 언어가 어떻게 "규칙"으로 번역됐는지
2. `globals.2tier.css` → `globals.3tier.css` — 토큰이 2계층에서 3계층으로 성장한 diff
3. `design-qa.md` — 레퍼런스 대비 실측 검증이 어떤 형식인지
4. `design-system.html` — 최종 출력물 (브라우저로 열 것)
5. `design-system-changelog.md` — 전체 서사

주의: 사본은 스냅샷이다. 원본이 진화해도 이 폴더는 갱신하지 않는다 —
이 사례의 목적은 "그 시점에 무엇이 출력됐는가"의 기록이다.
