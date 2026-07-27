# Matchday Frontend Design System

## 방향

Matchday의 화면은 [Spotify DESIGN.md](https://getdesign.md/spotify/design-md)의 시각 언어를 경기 운영 도구에 맞게 적용한다. 콘텐츠가 먼저 보이는 근검정 캔버스, 촘촘한 정보 밀도, 굵기 대비가 분명한 글자, pill 형태의 조작 요소로 운영 흐름을 빠르게 훑을 수 있게 한다.

- 기본 캔버스: `#121212`, 카드: `#181818`, 조작 표면: `#1f1f1f`
- 기본 글자: 흰색, 보조 글자: `#b3b3b3`
- 유일한 기능 액센트: `#1ed760`
- 기본 서체: Helvetica 계열과 한글용 Pretendard/Noto Sans KR fallback
- 버튼과 입력: pill, 카드와 overlay: `6px`~`8px`
- 콘텐츠 최대 폭: `1200px`
- 데스크톱: 고정 전역 sidebar와 콘텐츠 surface
- 모바일: 상단 브랜드 bar, 하단 전역 navigation, 가로 스크롤 지역 navigation

초록은 주요 CTA, 선택·활성, LIVE·성공 상태에만 사용한다. 넓은 배경이나 장식에는 사용하지 않는다. Spotify의 로고, 상표, 전용 서체와 음악 서비스 구조는 복제하지 않는다.

## 토큰 정본

실제 값의 정본은 `packages/design-system/src/styles/globals.css`다. 앱과 Storybook은 이 파일을 직접 import한다.

| 토큰군 | 용도 |
| --- | --- |
| `--background`, `--foreground` | 근검정 앱 캔버스와 흰 기본 글자 |
| `--card`, `--popover` | charcoal 정보 표면과 overlay |
| `--primary` | 주요 CTA·선택·활성 상태의 기능 초록 |
| `--secondary`, `--muted`, `--accent` | 조작·hover·비활성 표면 |
| `--destructive`, `--warning`, `--success` | 오류·경고·성공 상태 |
| `--field`, `--field-foreground` | 스코어보드·실시간 기록의 중립 dark surface |
| `--radius-*` | 카드·overlay 모서리. pill은 컴포넌트에서 별도 적용 |
| `--shadow-*` | 어두운 표면 사이의 뚜렷한 계층 |

Organizer 브랜드색은 전역 토큰을 덮지 않는다. 공개 브랜드 shell의 최상위 요소에 `--brand`, `--brand-foreground`만 주입하고, 내부 컴포넌트는 이 semantic token을 사용한다.

## 컴포넌트 원칙

1. `packages/design-system/src/components`의 shadcn 컴포넌트를 우선 사용한다.
2. 앱 화면은 `Route → Page → Domain → Shared` 순서로 조합한다.
3. 공용 컴포넌트는 도메인, Router, GraphQL, Storage를 알지 못한다.
4. shadcn에 이미 있는 Button, Dialog, Field, Select, Tabs, Table, Sheet, Empty를 다시 만들지 않는다.
5. 여러 하위 영역을 선택적으로 조합해야 할 때만 compound component를 만든다.
6. compound component는 `Root`, `Header`, `Content`, `Footer`처럼 역할이 드러나는 이름을 쓰고 context는 실제 공유 상태가 있을 때만 도입한다.
7. 한 화면에서만 쓰는 단순 JSX 조각은 해당 Page의 `-modules`에 둔다. 예상 사용처만으로 공용화하지 않는다.
8. 모든 입력은 label, 오류 문구, 키보드 focus를 제공한다. 색만으로 상태를 구분하지 않는다.

## 화면 밀도

- 페이지 제목과 주요 액션은 한 줄 header로 묶는다.
- 기본 간격은 `8px` 단위를 사용하고 카드 사이 여백보다 표면 명도 차이로 영역을 구분한다.
- 카드 안에 카드를 반복하지 않는다. raw gray border 대신 surface 또는 inset shadow를 사용한다.
- 목록 행의 기본 높이는 48px 이상, 모바일 주요 버튼은 44px 이상을 사용한다.
- 데이터 표는 모바일에서 card로 재발명하지 않고 필요한 경우 가로 스크롤한다.
- destructive 액션은 `AlertDialog` 확인을 거친다.
- 로딩은 layout이 유지되는 `Skeleton`, 데이터 없음은 원인과 다음 행동이 있는 `Empty`를 사용한다.

## 상태와 애니메이션

- 상태 전이는 120~200ms 범위의 색, opacity, transform만 사용한다.
- 메뉴·dialog는 `0 8px 24px rgb(0 0 0 / 50%)`, 카드는 더 낮은 단계의 어두운 그림자를 사용한다.
- 실시간 기록의 새 이벤트만 짧게 강조하고 반복 애니메이션은 사용하지 않는다.
- `prefers-reduced-motion`에서는 이동 애니메이션을 제거한다.
- 성공/실패 메시지는 `sonner`를 사용하고, 폼 오류는 해당 필드 가까이에 함께 표시한다.

## Storybook과 테스트

- 디자인 시스템과 앱은 서로 독립된 Storybook을 사용한다. 디자인 시스템 Storybook은 앱 경로를 읽지 않는다.
- shadcn primitive는 시각 variant와 keyboard/focus 상태를 Storybook에 둔다.
- custom compound component는 정상, 빈 상태, 긴 텍스트, 모바일 폭 story를 둔다.
- Route Page는 colocated Story에서 `Default`, `Loading`, `Empty`, `Error`와 주요 도메인 상태를 재현한다.
- Testing Library는 role/label 기반으로 사용자의 관찰 가능한 행동을 검증한다.
- 도메인 화면 통합 테스트는 GraphQL 결과를 stub해 사용자에게 보이는 상태와 mutation 결과를 검증한다.
- Playwright는 로그인 복귀, 초대 수락, 운영사 생성, 공개 경기 탐색 같은 화면 간 사용자 흐름만 검증한다.
- Story DOM 스냅샷과 비주얼 리그레션은 사용하지 않는다.
