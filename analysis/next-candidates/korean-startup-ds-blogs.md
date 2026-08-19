# 국내 스타트업·IT 기업의 "AI × 디자인 시스템" 사례

- 조사일: 2026-08-19 (1차), 심화 조사 추가
- 계기: [tech.moyoplan.com/posts/ax-designstudio](https://tech.moyoplan.com/posts/ax-designstudio)(모요)와 당근마켓(Seed) 외에, 같은 결의 국내 사례를 전수 조사했다
- 범위: 일반 "디자인 시스템 구축기"가 아니라 사용자가 요구한 두 가지로 좁혔다
  1. AI 사용을 염두에 두고 디자인 시스템을 설계·개선한 사례
  2. AI 시대에 디자인 시스템을 기반으로 구체적 성과를 낸 사례
- 1차 조사(기업 블로그 검색)에 이어 **국내 컨퍼런스 발표(DEVIEW·if(kakao)·SLASH·우아콘·FEConf)**, **성과 수치 전문 검색**, **대기업 누락분 재조사**, **디자인 매체·커뮤니티**까지 심화 조사했다

## 1. 성과가 뚜렷한 사례 (구체적 수치 공개)

**오늘의집(버킷플레이스)이 압도적으로 두껍다.** 자체 매거진 `bucketplace.com/culture/Design`에 2026년 2월부터 8월까지 "AI frontier"라는 시리즈로 최소 8편을 연재했다. 모요·당근과 같은 결이면서 수치가 가장 촘촘하다.

| 회사 | 글 | 수치/성과 |
|---|---|---|
| 오늘의집 | [반복되는 어드민 디자인, PRD로 어디까지 자동화할 수 있을까?](https://www.bucketplace.com/post/2026-05-29-반복되는-어드민-디자인-prd로-어디까지-자동화할-수-있을까/) (2026.05.29) | Figma Make로 먼저 시도했다가 실패, Claude Code + MCP + Skill로 PRD→디자인 파이프라인 구축. **9개 신규 어드민 페이지 작업 기간 20일→5일** |
| 오늘의집 | [디자이너가 AI를 쓰는 법: 더 빠르게 고민하고, 더 깊게 검증하기](https://www.bucketplace.com/post/2026-05-06-디자이너가-ai를-쓰는-법-더-빠르게-고민하고-더-깊게-검증하기/) (2026.05.06) | 자체 "Figma DS MCP"를 만들었지만 화면 하나에 15~20분 걸리는 한계를 인지하고 "AI가 완성"이 아닌 "병목만 해결"로 전략 전환. **시안 작업 3~4일→반나절, UT 데이터 세팅 2시간→15분** |
| 오늘의집 | [리소스 8배 절감, AI로 해결한 로컬라이즈 대공사](https://www.bucketplace.com/post/2026-02-24-리소스-8배-절감-ai로-해결한-로컬라이즈-대공사/) (2026.02.24) | 로컬라이즈 작업 리소스 **8배 절감** |
| 오늘의집 | [디자이너의 '감각'이 AI를 만나 '시스템'이 될 때](https://www.bucketplace.com/post/2026-04-24-디자이너의-감각이-ai를-만나-시스템이-될-때/) (2026.04.24) | 아이콘 200개를 AI로 일관되게 생성하는 파이프라인 |
| 오늘의집 | [반복되는 디자인 작업, 우리는 AI와 시스템을 만들기로 했다](https://www.bucketplace.com/post/2026-08-13-반복되는-디자인-작업-우리는-ai와-시스템을-만들기로-했다/) (2026.08.13) | 웹 빌더 9개 자동화 |
| 오늘의집 | UI 코드 생성 자동화를 프로덕션까지 (FEConf 2025, 발표자 손효정) | 9명 팀, Figma MCP + Cursor로 UI 개발을 **실제 프로덕션까지 도입**. "디자인팀과 1px로 싸울 일이 없다". 참석 후기 2건이 최고 세션으로 꼽음: [devocean.sk.com](https://devocean.sk.com/blog/techBoardDetail.do?ID=167748), [flikary.dev](https://flikary.dev/blog/feconf-2025) |
| 원티드랩 | [AI 기반 에이전틱 디자인 시스템 '몽타주' — 기획~개발 90% 단축](https://platum.kr/archives/284141) (2026, 플래텀 보도) | "기획~개발 3~4주 → 2~3일"이라는 **90% 단축**. 단, 원티드랩 자체 발표 인용이라 제3자 검증은 없음 |
| 팀스파르타(Stack) | [Cursor가 디자인 시스템 컴포넌트를 모르는 게 답답해서 — MCP 도입기](https://gamguma.dev/post/2025/06/design-system-mcp) | LLMs.txt(397,180토큰) 대신 MCP 채택. **컴포넌트 정보 검색 2~3분→10~20초** |
| 카카오뱅크 | [Figma 고객 사례: 디자인 효율성 30% 개선](https://www.figma.com/ko-kr/customers/kakaobank-faster-design-delivery-with-figma) | 디자인 프로세스 효율 **30% 개선**, 온보딩 속도 향상. AI 직접 언급은 없어 참고용 |
| 인프랩(Inflearn) | [AI로 디자인시스템 마이그레이션하기 1편](https://tech.inflab.com/20260606-ds-migration-ai) (2026.06.06) | Mantine 기반 DS를 AI로 마이그레이션. 수치는 약하지만 "AI는 토대가 있어야 동료가 된다"는 결론이 참고할 만함 |

## 2. 디자인 시스템 자체를 AI 대응 구조로 재설계한 사례

가장 정교한 "설계" 사례는 우아한형제들이다. 3단계로 나눠 3년치 데이터를 쌓았다.

| 회사 | 글 | 핵심 내용 |
|---|---|---|
| 우아한형제들 | [당연해진 디자인시스템, 그다음 이야기: AST와 MCP로 여는 미래](https://www.youtube.com/watch?v=HTHcsVgI_CM) (WOOWACON 2025) | "우아한 공방" TF가 처리하는 티켓 **연 1000건**. 1단계: Figma API+Babel AST 분석으로 토큰 미준수 컴포넌트를 대시보드화("Atelier Analytics"). 2단계: 하드코딩 스타일→토큰 자동 변환 Codemod. 3단계: Figma·Storybook 문서+3년치 공방 데이터를 MCP로 통합, 퍼지 매칭(Levenshtein)으로 오타 자동 교정, 프롬프트로 코드 자동 생성. 후기: [dev-tomato.tistory.com](https://dev-tomato.tistory.com/35), [velog.io/@qorgkr26](https://velog.io/@qorgkr26/woowacon-2025) |
| 우아한형제들 | [우아한공방의 새로운 동료: 시스템 맥락을 가진 챗봇서비스(feat. RAG)](https://techblog.woowahan.com/26319) | AWS Bedrock Knowledge Bases + OpenSearch Serverless로 RAG 챗봇을 **Storybook 내부에 직접 임베드**. 메타데이터 필터링으로 컴포넌트 단위 검색 정확도 확보 |
| 우아한형제들 | [AI가 내 프롬프트를 흘려듣는 이유](https://techblog.woowahan.com/26459) (2026.07.07) | 디자인 시스템 안에서 MCP 서버를 직접 개발하며 실패를 반복, context engineering(lost-in-the-middle, 컨텍스트 큐레이션)을 재학습 |
| 토스 | [apps-in-toss-ax](https://github.com/toss/apps-in-toss-ax) (GitHub 오픈소스) | AI 어시스턴트가 미니앱을 개발하도록 설계된 MCP/CLI 툴킷. `search_tds_web_docs` 등 **TDS(Toss Design System) 전용 문서 검색 MCP 도구**를 코드 배포 워크플로우 전체에 내장. 가장 제품화된 사례 |
| 카카오페이 | [FIT Design System 2.0: AI가 읽을 수 있는 디자인 시스템](https://www.youtube.com/watch?v=ebw2DaQ60aY) (Figma Maker Collective Seoul 2026) | 기존 시스템 적용률 **88%**(목표 80% 초과)였지만 "임의 수정·이름만 같고 다른 컴포넌트 사용"이 문제였다는 인식에서 AI-ready로 재설계. **웹/Android/iOS/React Native 4개 플랫폼 스펙을 통일**해 AI 에이전트가 동시 개발 가능하게 함. 토큰 도입+Code Connect 고도화 |
| 네이버파이낸셜 | [디자인시스템이 AI를 만났을 때](https://d2.naver.com/helloworld/3442203) (NAVER ENGINEERING DAY 2025) | 설계 판단이 흥미로움: **MCP 대신 인스트럭션 방식을 먼저 선택**("변경 포인트가 너무 많아 안정화되면 MCP로 전환 예정"). Figma Code Connect 연결에 한 달 이상 소요, 아이콘은 API로 자동 생성 |
| 블룸에이아이(BlumnAI) | [AI가 이해하는 디자인 시스템 구축하기](https://blog.blumn.ai/ai-design-system-rulebook) | 'Sort UI' 디자인 시스템에 금지 패턴·결정 트리를 규칙서로 정리, Figma 변수보다 Storybook(코드)을 기준점으로 삼은 이유가 명확 |

## 3. 디자이너의 일하는 방식이 바뀐 사례 (AI로 직접 제품을 만듦)

| 회사 | 글 | 핵심 내용 |
|---|---|---|
| 토스 | [AI 시대에 디자이너로 살아남기](https://toss.tech/article/removing_designers_in_ai_era) (이다윗, 2025.05.13) | 정산 UI 반복 화면을 규칙으로 시스템화 → 개발자가 디자이너 없이 UI를 직접 만들기 시작 → 요구조건 문서까지 자동 매핑 → 지금은 MCP로 AI가 토스 자체 디자인 툴을 직접 조작하는 실험 중, **이미 AI가 디자인한 화면이 실제 제품에 쓰이는 중**이라고 명시 |
| 토스 | [디자이너가 시안 대신 앱을 만든 이유](https://toss.tech/article/deadend) | Xcode/SwiftUI 경험이 전혀 없는 디자이너가 AI로 동작하는 iOS 프로토타입(Metal 셰이더 애니메이션 포함)을 직접 구현, 코드 저장소를 그대로 개발자에게 전달해 첫 빌드가 디자인과 거의 일치 |
| 배달의민족 | [같은 시간, 더 나은 디자인을 할 수 있는 방법](https://www.youtube.com/watch?v=R9xqcIuhXSI) (WOOWACON 2025, DesignOps) | 클릭 한 번으로 실데이터를 Figma 시안에 반영하는 "데이터 브릿지", 디자인 QA를 끝내는 크롬 익스텐션 "티켓 브릿지" |
| 오픈패스(듀오톤 인터뷰) | [AI 시대, 디자이너에게 '디자인 시스템'이 더 중요해지는 이유](https://blog.openpath.kr/design-system-importance-ai-designers) | 원티드 Montage 소스를 Claude에 올려 카페 기록 앱을 **이틀 만에 완성**. 전용 `wds-mcp` 연결 팁 |
| 여기어때 | [디자이너의 상상을 현실로: 여기어때 아이콘 생성기 제작기](https://techblog.gccompany.co.kr/디자이너의-상상을-현실로-여기어때-아이콘-생성기-077fa8b6d795) | YDS 스타일을 지키는 AI 아이콘 생성·벡터화 파이프라인 |
| 개인(익명, Angular 조직) | [AI로 Design System을 만들며 배운 것들 1~3편](https://medium.com/@nexttonone/ai%EB%A1%9C-design-system%EC%9D%84-%EB%A7%8C%EB%93%A4%EB%A9%B0-%EB%B0%B0%EC%9A%B4-%EA%B2%83%EB%93%A4-3%ED%8E%B8-dfa9a24e2304) | 디자이너가 직접 Claude Code로 컴포넌트 PR 작성. 위반 시 다음 단계로 못 넘어가는 `생성→로컬 검증→PR→CI 재검증→merge` 파이프라인으로 전환 |
| 개인(brunch) | [AI로 일관된 결과가 나오는 디자인 시스템 만들기](https://brunch.co.kr/@dad8d14cac41474/23) | shadcn 기반 컴포넌트를 Primitive/Enforced 2계층으로 나누고 MCP로 디자인 시스템 저장소를 읽게 함, 훅으로 강제 검증 |

## 4. 근원: 모요·당근 (이미 알려진 두 건)

| 회사 | 글 | 핵심 내용 |
|---|---|---|
| 모요 | [화면을 그리는 디자이너에서, 규칙을 설계하는 디자이너로](https://tech.moyoplan.com/posts/ax-designstudio) | AX팀이 자체 AI 디자인 툴을 만들어 토큰·컴포넌트를 AI가 따르게 함 |
| 당근 | [프롬프트 한 줄로 화면이 나오는 시대, '당근스러운 화면'을 만드는 법](https://medium.com/daangn/프롬프트-한-줄로-화면이-나오는-시대-당근스러운-화면을-만드는-법-0bc268f819c7) | SEED 규칙을 스킬 모듈로 쪼개 AI 에이전트(Kraft)에 로드, Plan/Orchestra 구조로 발전 |

## 5. 매체 기고·칼럼 (2차 정리 글)

| 매체 | 글 | 핵심 내용 |
|---|---|---|
| 코리아메타버스저널 | [AI디자인 실전 #01~#08 시리즈](https://www.kmjournal.net/news/articleView.html?idxno=11096) | 김민우(올림플래닛 디자인 총괄) 연재. "CLAUDE.md/README.md 스펙 파일 유무", "컴포넌트 모든 상태(Hover/Loading/Disabled) 명시 여부" 같은 실무 체크리스트 |
| 요즘IT | [AI 에이전트와 함께 쓰는 기획/디자인 도구 6가지](https://yozm.wishket.com/magazine/detail/3885) | DESIGN.md(구글랩스), shadcn/ui MCP, taste-skill 등 도구 소개 (국내 사례는 아님) |
| Figma Korea 웨비나 | AI + 디자인 시스템으로 더 스마트하게 개발하는 법 | 당근소프트(Figma 한국 파트너사) 발표. Figma Make로 상태값까지 프로토타입화 실연. 텍스트 아티클은 아니고 영상 자료 |

## 조사 방법 메모

- velopers.kr 태그 페이지(#자동화, #Figma, #컴포넌트, #토큰)까지 확인했지만 새로운 국내 AI×DS 사례는 거의 없었다. **컨퍼런스 발표(WOOWACON, FEConf, NAVER ENGINEERING DAY, Figma Maker Collective)와 회사 자체 매거진(오늘의집 `bucketplace.com/culture`)이 기술 블로그보다 훨씬 밀도 높은 소스였다.**
- 시도했지만 AI×DS 연결 자료를 못 찾은 회사: 쿠팡, 무신사, 컬리, 왓챠, 뱅크샐러드, 라인(LY Corp), 크몽, 리멤버, 데이블, 스포카, 캐시노트, 그리팅/두들린, 뤼튼, 업스테이지, 카카오(본사)·카카오뱅크(디자인시스템+AI 직접 연결 자료 기준).
