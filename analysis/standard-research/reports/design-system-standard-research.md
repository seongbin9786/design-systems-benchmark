<!-- 생성물입니다. 직접 편집하지 마세요 — 다음 빌드에 덮어써집니다.
     고치려면 analysis/standard-research/tools/ 의 스크립트를 고치고
     `python3 analysis/standard-research/run.py` 를 다시 실행하세요. -->
# 디자인 시스템에서 표준화할 수 있는 것

> 8개 컴포넌트 라이브러리의 **실제 소스**에서 semantic 토큰 2876개와 컴포넌트 인벤토리를 추출해, 어느 개념이 예외 없이 공통이고 어느 개념이 갈리는지 셌다.
> 공통인 것만이 표준화 가능하다.
>
> **대상** Spectrum · Material Web · MUI · Fluent 2 · Carbon · Polaris · shadcn/ui · Ant Design  
> **기준일** 2026-07-30 · **소스** 고정 커밋 (부록)  
> **시각화판** [design-system-standard-research.html](design-system-standard-research.html) — 커버리지 히트맵, 덤벨 차트 등 8종. 이 문서와 같은 데이터에서 생성된다.

| 예외 없이 공통인 토큰 어휘 | 8개 시스템 전부에 있는 컴포넌트 | 추출한 semantic 토큰 총수 | category 축을 못 붙인 잔여 |
|---:|---:|---:|---:|
| 8 | 10 | 2876 | 5.3% |

## 측정 방법과 한계

결론보다 이 절이 먼저다. 이 저장소의 기존 감사가 남긴 교훈이 "집계 기준을 명시하지 않은 감사는 비교 불가"이기 때문이다.

- **수집 범위** — 각 시스템의 *semantic(alias) 계층*만. primitive 램프(`gray-100` 류)는 제외했다. 표준화 대상이 아니다.
- **판정** — 토큰 이름을 4개 축(값의 종류 / 자리 / 의미 / 상태)으로 분류하고, 각 값이 8개 중 몇 개 시스템에 등장하는지 센다.
- **이름이 곧 근거** — 값이 아니라 *이름*을 본다. 이름에 개념이 드러나지 않으면 그 시스템은 실제로 그 개념을 구분하지 않는다고 본다.
- **잔여 152개(5.3%)** 는 *값의 종류* 축만 못 붙은 것이다 (다른 축은 기록됐다). 대부분 Carbon 의 `code01`/`container01` 같은 시스템 고유 스케일이다.

> [!WARNING]
> **이름이 같아야 개념이 같은 것은 아니다.** Fluent 2 는 상태색을 `status` 가 아니라 *색조* 이름으로 부른다 — `colorPaletteCranberryForeground1` 이 위험색이다. 이 문서는 `statusColorMapping.ts`(success→green, warning→orange, danger→cranberry)를 읽어 매핑한 뒤 커버리지에 넣었다. 해당 사례: Spectrum 3개, Fluent 2 45개

## 1. 토큰 규모와 구성

최대(Spectrum 935)와 최소(shadcn/ui 93)가 **10배** 차이다. 토큰이 많은 게 좋은 것은 아니다 — 그 수가 어디에 쓰였는지가 갈린다.

| 시스템 | 토큰 수 | 색상 | 타이포그래피 | 간격 | 크기 | elevation | 모션 | radius | 기타·미분류 |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Spectrum | 935 | 26.3% | 32.6% | 24.0% | 3.4% | 4.6% | — | 3.2% | 5.9% |
| Polaris | 519 | 43.5% | 21.6% | 4.2% | 7.7% | 4.4% | 7.9% | 1.9% | 8.8% |
| Fluent 2 | 459 | 79.7% | 5.9% | 4.8% | — | 2.6% | 3.7% | 2.4% | 0.9% |
| Carbon | 341 | 33.1% | 15.8% | 5.9% | 1.8% | 1.5% | 1.8% | — | 40.1% |
| Ant Design | 228 | 46.5% | 10.5% | 10.1% | 8.8% | 6.1% | 4.4% | 2.2% | 11.4% |
| Material Web | 192 | 26.0% | 48.4% | — | — | 3.1% | 14.1% | 6.2% | 2.2% |
| MUI | 109 | 34.9% | 18.3% | 0.9% | — | 22.9% | 10.1% | 0.9% | 12.0% |
| shadcn/ui | 93 | 83.9% | 3.2% | — | — | — | — | 8.6% | 4.3% |

간격을 토큰화하지 않은 시스템이 둘(Material Web · shadcn/ui) 있다.

## 2. 어휘 커버리지 매트릭스

`●` = 그 시스템이 그 개념을 **이름에 드러낸다**, `·` = 드러내지 않는다. 행을 가로로 읽으면 표준화 가능성, 열을 세로로 읽으면 그 시스템의 성향이 보인다.

판정 기준: **표준** = 8/8 예외 없음 · **우세** = 5~7/8 · **분기** = 2~4/8 · **고유** = 1/8

### 값의 종류 — 토큰이 무엇을 담는가

| 정규 어휘 | SPE | MTW | MUI | FLU | CAR | POL | SCN | ANT | 보유 | 판정 | 미보유 |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---:|:---|:---|
| `color` | ● | ● | ● | ● | ● | ● | ● | ● | 8/8 | 표준 | — |
| `typography` | ● | ● | ● | ● | ● | ● | ● | ● | 8/8 | 표준 | — |
| `elevation` | ● | ● | ● | ● | ● | ● | · | ● | 7/8 | 우세 | shadcn/ui |
| `radius` | ● | ● | ● | ● | · | ● | ● | ● | 7/8 | 우세 | Carbon |
| `motion` | · | ● | ● | ● | ● | ● | · | ● | 6/8 | 우세 | Spectrum, shadcn/ui |
| `spacing` | ● | · | ● | ● | ● | ● | · | ● | 6/8 | 우세 | Material Web, shadcn/ui |
| `border` | ● | · | · | ● | · | ● | · | ● | 4/8 | 분기 | Carbon, MUI, Material Web, shadcn/ui |
| `opacity` | ● | ● | ● | · | · | · | · | ● | 4/8 | 분기 | Carbon, Fluent 2, Polaris, shadcn/ui |
| `sizing` | ● | · | · | · | ● | ● | · | ● | 4/8 | 분기 | Fluent 2, MUI, Material Web, shadcn/ui |
| `breakpoint` | · | · | · | · | · | ● | ● | ● | 3/8 | 분기 | Carbon, Fluent 2, MUI, Material Web, Spectrum |
| `z-index` | · | · | ● | · | · | ● | · | ● | 3/8 | 분기 | Carbon, Fluent 2, Material Web, Spectrum, shadcn/ui |
| `icon-size` | ● | · | · | · | ● | · | · | · | 2/8 | 분기 | Ant Design, Fluent 2, MUI, Material Web, Polaris, shadcn/ui |

### 색이 칠해지는 자리 — 같은 색을 어디에 쓰는가

| 정규 어휘 | SPE | MTW | MUI | FLU | CAR | POL | SCN | ANT | 보유 | 판정 | 미보유 |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---:|:---|:---|
| `border` | ● | ● | ● | ● | ● | ● | ● | ● | 8/8 | 표준 | — |
| `foreground` | ● | ● | ● | ● | ● | ● | ● | ● | 8/8 | 표준 | — |
| `surface` | ● | ● | ● | ● | ● | ● | ● | ● | 8/8 | 표준 | — |
| `shadow` | ● | ● | ● | ● | ● | ● | · | ● | 7/8 | 우세 | shadcn/ui |
| `overlay` | ● | ● | · | ● | ● | ● | · | · | 5/8 | 우세 | Ant Design, MUI, shadcn/ui |
| `icon` | ● | · | · | · | ● | ● | · | ● | 4/8 | 분기 | Fluent 2, MUI, Material Web, shadcn/ui |
| `link` | · | · | · | ● | ● | ● | · | ● | 4/8 | 분기 | MUI, Material Web, Spectrum, shadcn/ui |
| `focus-ring` | ● | · | · | · | · | · | ● | · | 2/8 | 분기 | Ant Design, Carbon, Fluent 2, MUI, Material Web, Polaris |

### 의미와 강조도 — 그 색이 무슨 뜻인가

| 정규 어휘 | SPE | MTW | MUI | FLU | CAR | POL | SCN | ANT | 보유 | 판정 | 미보유 |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---:|:---|:---|
| `brand` | ● | ● | ● | ● | ● | ● | ● | ● | 8/8 | 표준 | — |
| `secondary` | ● | ● | ● | ● | ● | ● | ● | ● | 8/8 | 표준 | — |
| `status:critical` | ● | ● | ● | ● | ● | ● | ● | ● | 8/8 | 표준 | — |
| `disabled` | ● | · | ● | ● | ● | ● | · | ● | 6/8 | 우세 | Material Web, shadcn/ui |
| `status:success` | ● | · | ● | ● | ● | ● | · | ● | 6/8 | 우세 | Material Web, shadcn/ui |
| `status:warning` | ● | · | ● | ● | ● | ● | · | ● | 6/8 | 우세 | Material Web, shadcn/ui |
| `status:info` | ● | · | ● | · | ● | ● | · | ● | 5/8 | 우세 | Fluent 2, Material Web, shadcn/ui |
| `inverse` | · | ● | · | ● | ● | ● | · | · | 4/8 | 분기 | Ant Design, MUI, Spectrum, shadcn/ui |
| `neutral` | ● | · | ● | ● | · | · | · | · | 3/8 | 분기 | Ant Design, Carbon, Material Web, Polaris, shadcn/ui |

### 상호작용 상태 — 상태에 따라 값이 바뀌는가

| 정규 어휘 | SPE | MTW | MUI | FLU | CAR | POL | SCN | ANT | 보유 | 판정 | 미보유 |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---:|:---|:---|
| `active` | ● | ● | ● | ● | ● | ● | · | ● | 7/8 | 우세 | shadcn/ui |
| `focus` | ● | ● | ● | ● | ● | ● | · | ● | 7/8 | 우세 | shadcn/ui |
| `hover` | ● | ● | ● | ● | ● | ● | · | ● | 7/8 | 우세 | shadcn/ui |
| `disabled` | ● | · | ● | ● | ● | ● | · | ● | 6/8 | 우세 | Material Web, shadcn/ui |
| `selected` | ● | · | ● | ● | ● | ● | · | · | 5/8 | 우세 | Ant Design, Material Web, shadcn/ui |
| `loading` | · | · | · | · | ● | · | · | ● | 2/8 | 분기 | Fluent 2, MUI, Material Web, Polaris, Spectrum, shadcn/ui |
| `visited` | · | · | · | · | ● | · | · | · | 1/8 | 고유 | Ant Design, Fluent 2, MUI, Material Web, Polaris, Spectrum, shadcn/ui |

열 코드: **SPE** Spectrum · **MTW** Material Web · **MUI** MUI · **FLU** Fluent 2 · **CAR** Carbon · **POL** Polaris · **SCN** shadcn/ui · **ANT** Ant Design

> [!NOTE]
> 세로로 읽으면 **shadcn/ui 열이 눈에 띄게 비어 있다.** 상태(hover·focus·active)와 elevation·간격 토큰이 없다. 없어서 못 만든 게 아니라 그 표현을 토큰이 아닌 Tailwind 유틸리티로 옮긴 설계다 — 대가는 상태 표현이 컴포넌트 코드에 흩어진다는 것.

## 3. 컴포넌트 교집합

디렉터리·파일 인벤토리를 정규 개념으로 접은 결과. 시스템마다 분해 단위가 달라 (Carbon 은 DataTable 하위를 개별 디렉터리로 둔다) 절대 개수는 비교하지 않고 *개념 커버리지*만 본다.

| 정규 컴포넌트 | SPE | MTW | MUI | FLU | CAR | POL | SCN | ANT | 보유 | 미보유 |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---:|:---|
| **Button** | ● | ● | ● | ● | ● | ● | ● | ● | 8/8 | — |
| **Checkbox** | ● | ● | ● | ● | ● | ● | ● | ● | 8/8 | — |
| **Dialog** | ● | ● | ● | ● | ● | ● | ● | ● | 8/8 | — |
| **Menu** | ● | ● | ● | ● | ● | ● | ● | ● | 8/8 | — |
| **Progress** | ● | ● | ● | ● | ● | ● | ● | ● | 8/8 | — |
| **Radio** | ● | ● | ● | ● | ● | ● | ● | ● | 8/8 | — |
| **Select** | ● | ● | ● | ● | ● | ● | ● | ● | 8/8 | — |
| **Slider** | ● | ● | ● | ● | ● | ● | ● | ● | 8/8 | — |
| **Tabs** | ● | ● | ● | ● | ● | ● | ● | ● | 8/8 | — |
| **TextInput** | ● | ● | ● | ● | ● | ● | ● | ● | 8/8 | — |
| **Alert** | ● | · | ● | ● | ● | ● | ● | ● | 7/8 | Material Web |
| **Badge** | ● | · | ● | ● | ● | ● | ● | ● | 7/8 | Material Web |
| **Breadcrumbs** | ● | · | ● | ● | ● | ● | ● | ● | 7/8 | Material Web |
| **Card** | ● | · | ● | ● | ● | ● | ● | ● | 7/8 | Material Web |
| **Combobox** | ● | · | ● | ● | ● | ● | ● | ● | 7/8 | Material Web |
| **Divider** | ● | ● | ● | ● | · | ● | ● | ● | 7/8 | Carbon |
| **List** | ● | ● | ● | ● | ● | ● | · | ● | 7/8 | shadcn/ui |
| **Switch** | ● | ● | ● | ● | ● | · | ● | ● | 7/8 | Polaris |
| **Table** | ● | · | ● | ● | ● | ● | ● | ● | 7/8 | Material Web |
| **Tooltip** | ● | · | ● | ● | ● | ● | ● | ● | 7/8 | Material Web |
| **Typography** | ● | ● | ● | ● | ● | ● | · | ● | 7/8 | shadcn/ui |
| **Accordion** | ● | · | ● | ● | ● | · | ● | ● | 6/8 | Material Web, Polaris |
| **Avatar** | ● | · | ● | ● | · | ● | ● | ● | 6/8 | Material Web, Carbon |
| **Form** | ● | · | ● | · | ● | ● | ● | ● | 6/8 | Material Web, Fluent 2 |
| **Icon** | ● | ● | ● | · | ● | ● | · | ● | 6/8 | Fluent 2, shadcn/ui |
| **Label** | ● | · | ● | ● | ● | ● | ● | · | 6/8 | Material Web, Ant Design |
| **Link** | ● | · | ● | ● | ● | ● | · | ● | 6/8 | Material Web, shadcn/ui |
| **Popover** | · | · | ● | ● | ● | ● | ● | ● | 6/8 | Spectrum, Material Web |
| **ButtonGroup** | ● | · | ● | · | · | ● | ● | ● | 5/8 | Material Web, Fluent 2, Carbon |
| **Drawer** | · | · | ● | ● | · | ● | ● | ● | 5/8 | Spectrum, Material Web, Carbon |
| **Layout** | ● | · | ● | · | ● | ● | · | ● | 5/8 | Material Web, Fluent 2, shadcn/ui |
| **Navigation** | · | · | ● | ● | ● | ● | ● | · | 5/8 | Spectrum, Material Web, Ant Design |
| **Pagination** | · | · | ● | · | ● | ● | ● | ● | 5/8 | Spectrum, Material Web, Fluent 2 |
| **Skeleton** | · | · | ● | ● | ● | · | ● | ● | 5/8 | Spectrum, Material Web, Polaris |
| **DatePicker** | ● | · | · | · | ● | ● | · | ● | 4/8 | Material Web, MUI, Fluent 2, shadcn/ui |
| **Field** | · | ● | ● | ● | · | · | ● | · | 4/8 | Spectrum, Carbon, Polaris, Ant Design |
| **FileUpload** | ● | · | · | · | ● | ● | · | ● | 4/8 | Material Web, MUI, Fluent 2, shadcn/ui |
| **Image** | ● | · | · | ● | · | ● | · | ● | 4/8 | Material Web, MUI, Carbon, shadcn/ui |
| **Spinner** | · | · | · | ● | ● | ● | ● | · | 4/8 | Spectrum, Material Web, MUI, Ant Design |
| **Toast** | ● | · | ● | ● | · | ● | · | · | 4/8 | Material Web, Carbon, shadcn/ui, Ant Design |
| **Tree** | ● | · | · | ● | ● | · | · | ● | 4/8 | Material Web, MUI, Polaris, shadcn/ui |
| **Calendar** | ● | · | · | · | · | · | ● | ● | 3/8 | Material Web, MUI, Fluent 2, Carbon, Polaris |
| **Carousel** | · | · | · | ● | · | · | ● | ● | 3/8 | Spectrum, Material Web, MUI, Carbon, Polaris |
| **ColorPicker** | · | · | · | ● | · | ● | · | ● | 3/8 | Spectrum, Material Web, MUI, Carbon, shadcn/ui |
| **Empty** | · | · | · | · | · | ● | ● | ● | 3/8 | Spectrum, Material Web, MUI, Fluent 2, Carbon |
| **IconButton** | · | ● | ● | · | ● | · | · | · | 3/8 | Spectrum, Fluent 2, Polaris, shadcn/ui, Ant Design |
| **NumberInput** | ● | · | · | · | ● | · | · | ● | 3/8 | Material Web, MUI, Fluent 2, Polaris, shadcn/ui |
| **Rating** | · | · | ● | ● | · | · | · | ● | 3/8 | Spectrum, Material Web, Carbon, Polaris, shadcn/ui |
| **SearchInput** | ● | · | · | ● | ● | · | · | · | 3/8 | Material Web, MUI, Polaris, shadcn/ui, Ant Design |
| **Stepper** | · | · | ● | · | ● | · | · | ● | 3/8 | Spectrum, Material Web, Fluent 2, Polaris, shadcn/ui |
| **Textarea** | · | · | · | ● | ● | · | ● | · | 3/8 | Spectrum, Material Web, MUI, Polaris, Ant Design |
| **Toolbar** | ● | · | ● | ● | · | · | · | · | 3/8 | Material Web, Carbon, Polaris, shadcn/ui, Ant Design |

### 같은 개념, 다른 이름

| 정규 컴포넌트 | SPE | MTW | MUI | FLU | CAR | POL | SCN | ANT |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| **Button** | `button` | `button` | `Button`, `ListItemButton`, `StepButton` | `button` | `Button`, `ChatButton`, `ComboButton` | `Button`, `CheckableButton`, `UnstyledButton` | `button` | `button`, `float-button` |
| **Checkbox** | `checkbox` | `checkbox` | `Checkbox` | `checkbox` | `Checkbox` | `Checkbox` | `checkbox` | `checkbox` |
| **Dialog** | `dialog` | `dialog` | `Dialog`, `Modal` | `dialog` | `Dialog`, `Modal` | `Modal` | `alert-dialog`, `dialog` | `modal` |
| **Menu** | `menu` | `menu` | `Menu` | `menu` | `ContextMenu`, `Menu`, `OverflowMenu` | `ActionList`, `ActionMenu` | `context-menu`, `dropdown-menu` | `menu` |
| **Progress** | `meter`, `progress` | `progress` | `CircularProgress`, `LinearProgress` | `progress` | `ProgressBar` | `ProgressBar` | `progress` | `progress` |
| **Radio** | `radio` | `radio` | `Radio`, `RadioGroup` | `radio` | `RadioButton` | `RadioButton` | `radio-group` | `radio` |
| **Select** | `picker` | `select` | `NativeSelect`, `Select` | `select` | `Dropdown`, `Select` | `Picker`, `Select` | `native-select`, `select` | `dropdown`, `select` |
| **Slider** | `slider` | `slider` | `Slider` | `slider` | `Slider` | `RangeSlider` | `slider` | `slider` |
| **Tabs** | `tabs` | `tabs` | `Tab`, `Tabs` | `tabs` | `Tab`, `Tabs` | `Tabs` | `tabs` | `tabs` |
| **TextInput** | `textfield` | `textfield` | `Input`, `TextField` | `input` | `TextInput` | `TextField` | `input` | `input` |

## 4. Button variant 축 — 8종 실측

축 자체는 거의 같다. **강조도**(얼마나 강해 보이나) · **의미**(무슨 일을 하나) · **크기** · **형태**. 갈리는 건 이름, 그리고 강조도와 의미를 *분리했는지 합쳤는지*다.

| 시스템 | 강조도 | 의미 | 크기 | 형태 | 두 축 관계 |
|:---|:---|:---|:---|:---|:---|
| Spectrum | `fillStyle`<br>fill · outline | `variant`<br>primary · secondary · accent · negative · premium · genai | `size`<br>S · M · L · XL | — | 분리 |
| Material Web | *prop 없음*<br>filled · outlined · text · elevated · filled-tonal | — | — | — | 의미 축 없음 |
| MUI | `variant`<br>text · outlined · contained | `color`<br>inherit · primary · secondary · success · error · info · warning | `size`<br>small · medium · large | — | 분리 |
| Fluent 2 | `appearance`<br>secondary · primary · outline · subtle · transparent | — | `size`<br>small · medium · large | `shape`<br>rounded · circular · square | 의미 축 없음 |
| Carbon | `kind`<br>primary · secondary · tertiary · ghost | `kind`<br>danger · danger--primary · danger--ghost · danger--tertiary | `size`<br>xs · sm · md · lg · xl · 2xl | — | **합침** |
| Polaris | `variant`<br>primary · secondary · tertiary · plain · monochromePlain | `tone`<br>critical · success | `size`<br>micro · slim · medium · large | — | 분리 |
| shadcn/ui | `variant`<br>default · outline · secondary · ghost · link | `variant`<br>destructive | `size`<br>default · xs · sm · lg · icon | — | **합침** |
| Ant Design | `variant`<br>outlined · dashed · solid · filled · text · link | `color`<br>default · primary · danger · …PresetColors | `size`<br>small · middle · large | `shape`<br>default · circle · round · square | 분리 |

- **Spectrum** — 강조도와 의미를 fillStyle / variant 로 분리한 유일한 시스템. premium·genai 는 도메인 확장 축.
- **Material Web** — variant prop 이 없다. 강조도별로 *별도 커스텀 엘리먼트*(<md-filled-button> 등)로 나눈다. 크기 축도 없다.
- **MUI** — emphasis(variant) × intent(color) 를 분리. Spectrum 과 같은 설계, 다른 이름.
- **Fluent 2** — emphasis 와 intent 를 appearance 한 축에 섞었다. 위험(danger) 의미 축이 Button 에 없다. disabledFocusable 은 접근성 배려(비활성이어도 포커스 가능).
- **Carbon** — emphasis 와 intent 를 한 축(kind)에 합치고 `danger--tertiary` 처럼 곱을 문자열로 인코딩한다. 축이 늘면 값이 곱으로 폭발하는 구조.
- **Polaris** — emphasis(variant) × intent(tone) 분리. tone 이라는 이름을 쓰는 유일한 시스템.
- **shadcn/ui** — Carbon 처럼 한 축에 합쳤다. 상태는 prop 이 아니라 Tailwind `disabled:` 유틸리티로 처리 — 그래서 상태 토큰이 없다. size 에 `icon` 이 섞여 있어 크기 축이 순수하지 않다.
- **Ant Design** — 축이 가장 많다. 구 `type` 축과 신 `variant`+`color` 축이 공존해 같은 결과를 두 방식으로 표현할 수 있다 — 하위호환의 대가.

> [!IMPORTANT]
> **합치면 값이 곱으로 폭발한다.** Carbon 은 `kind` 하나에 강조도와 의미를 합쳐 `danger--tertiary` 처럼 조합을 문자열로 인코딩한다. Spectrum·MUI·Polaris·Ant Design 은 두 축을 분리해 같은 표현력을 값의 곱 없이 얻는다. 새로 만든다면 분리가 맞다.
>
> **Material Web 은 variant prop 자체가 없다.** 강조도별로 별도 커스텀 엘리먼트(`<md-filled-button>` 등)로 나눈다. 크기 축도 없다. Figma 킷에는 variant 가 있으니 — 이 지점이 Figma↔Code 매핑이 구조적으로 어긋나는 자리다.

## 5. Figma 쪽 축 분포

공식 Figma 킷 4종의 COMPONENT_SET 에서 variant property 이름을 집계했다. **어느 킷에서도 1위가 `state`** 다 — 디자인 파일이 가장 많이 표현하는 축은 상호작용 상태다. 코드에서 상태는 prop 이 아니라 CSS 의사클래스이므로, 이 축은 원리상 1:1 매핑되지 않는다.

| Figma 킷 | SET 수 | 1위 | 2위 | 3위 | 4위 | 5위 | 6위 |
|:---|---:|:---|:---|:---|:---|:---|:---|
| Carbon | 177 | `state` 58.2% | `size` 45.2% | `type` 15.3% | `open` 13.0% | `selected` 11.3% | `alignment` 6.8% |
| Fluent 2 | 104 | `state` 44.2% | `size` 43.3% | `style` 29.8% | `layout` 24.0% | `type` 11.5% | `selected` 9.6% |
| Material Web | 171 | `state` 52.6% | `selected` 29.2% | `type` 25.7% | `size` 17.5% | `configuration` 10.5% | `style` 5.3% |
| Spectrum | 462 | `state` 55.4% | `style` 31.2% | `color` 6.9% | `label position` 6.9% | `selected ?` 6.1% | `track size` 5.2% |

## 6. 재감사 — 기존 결론이 지금도 성립하나

### 6-1. 토큰 의존율 재측정

컴포넌트 4종(Button / Checkbox / Dialog / TextInput)의 스타일 소스에서 `토큰 참조 / (토큰 참조 + hardcoded)` 를 셌다. **느슨**은 컴포넌트 로컬 변수(`--pc-*` 류)와 Tailwind 스케일 클래스를 토큰으로 인정한 값, **엄격**은 제외한 값.

| 시스템 | 느슨 평균 | 엄격 평균 | 범위 | 기존 문서값 | 차이 | 측정 수 |
|:---|---:|---:|---:|---:|---:|---:|
| Spectrum | 97.2% | 95.8% | 94~100% | 98.9% | -2pt | 4 |
| Ant Design | 95.6% | 95.6% | 91~100% | ~82% | +14pt | 4 |
| shadcn/ui | 89.1% | 80.7% | 76~98% | 18.5% | **+71pt** ⚠ | 4 |
| Material Web | 88.9% | 88.9% | 72~100% | ~95%+ | -6pt | 4 |
| Polaris | 85.8% | 73.1% | 50~100% | ~53% | **+33pt** ⚠ | 4 |
| Fluent 2 | 77.9% | 77.9% | 64~91% | ~83% | -5pt | 4 |
| Carbon | 65.4% | 65.4% | 38~85% | ~50% | +15pt | 4 |
| MUI | 64.4% | 64.4% | 25~100% | ~70% | -6pt | 3 |

> [!CAUTION]
> **2개 시스템(shadcn/ui, Polaris)에서 20pt 이상 벌어졌다.** 원인은 소스 변화가 아니라 *집계 기준*이다. 기존 감사는 shadcn 의 Tailwind 클래스를 전부 hardcoded 로 세었고(205개), 이 재측정은 테마 스케일을 참조하는 클래스를 토큰 참조로 센다. 어느 쪽도 틀리지 않았다 — 그래서 **"토큰 의존율 3 클러스터"는 시스템의 속성이 아니라 계수 규칙의 산물**이라고 봐야 한다. 이 저장소가 스스로 경고한 함정 7번이 자기 결론에도 적용된다.

### 6-2. Mapping Fidelity Index (부분)

로드맵 §2.1 의 MFI 5개 항목 중 계산 가능한 2개만 구해 가중치 0.50 구간으로 재정규화했다. 로드맵의 MFI 와 **같은 값이 아니다**.

| 시스템 | Figma SET | 정규화 후 | 코드 | 매칭 | 매칭률 | 네이밍 근접도 | MFI-partial |
|:---|---:|---:|---:|---:|---:|---:|---:|
| Fluent 2 | 104 | 94 | 57 | 34 | 59.6% | 83.7% | **69.3** |
| Material Web | 171 | 149 | 20 | 10 | 50.0% | 77.4% | **61.0** |
| Carbon | 177 | 124 | 125 | 47 | 37.6% | 77.2% | **53.5** |
| Spectrum | 462 | 44 | 58 | 21 | 36.2% | 71.2% | **50.2** |


> [!WARNING]
> **이 수치는 매칭 규칙에 극도로 민감하다.** 이름 매칭에 "한쪽이 다른 쪽을 포함하면 매칭" 이라는 보정을 넣었을 때 Carbon 매칭률이 74.2%, 제거했을 때 37.6% 였다. 보정판은 `context-selector`↔`.Text`, `icon`↔`Icon button` 같은 무관한 쌍을 세고 있었다. 지금은 보정 없는 순수 문자열 유사도만 쓴다 — 사람 눈에는 대응하는 쌍(`radio`↔`Radio buttons`)도 놓치지만, 과대평가보다 과소평가가 정직하다. 의존율과 같은 교훈이다: **집계 규칙을 밝히지 않은 수치는 비교 불가다.**
계산하지 못한 항목 (가중치 0.50):

- `variant` (가중치 0.20) — 코드 prop 축 자동 추출 미구현 (Button 만 수동 실측 — button_api.json)
- `token` (가중치 0.20) — Figma Variables API 403 — figma/raw/*-variables.json 전부 error
- `structural` (가중치 0.10) — auto-layout ↔ flex/grid 수동 평가 필요

## 7. 그래서 최소 시스템은 무엇을 갖춰야 하나

위 측정에서 **8/8** 로 나온 것만 모은 목록이다. 하나라도 빠뜨리면 8개 시스템 중 어느 것도 하지 않은 선택을 하는 셈이다.

1. **색상 토큰을 세 자리로 나눈다** — 면(surface) · 글자(foreground) · 선(border). 예외 없이 8/8이다. 하나로 뭉치면 다크 테마에서 반드시 깨진다.
2. **의미 축에 최소 세 값** — 브랜드 · 보조 · 위험(critical). 성공·경고는 6/8로 그다음 순위.
3. **상태를 토큰으로 만든다** — hover · focus · active 는 7/8. 미보유는 shadcn/ui — 그 대가로 상태 표현이 컴포넌트 코드에 흩어진다.
4. **타이포그래피 스케일을 토큰화한다** — 8/8. 색상과 함께 유일하게 예외가 없는 값 종류다.
5. **Elevation·radius 는 7/8** — 미보유는 shadcn/ui · Carbon 로 예외다 (shadcn 은 Tailwind 유틸리티, Carbon 은 radius 토큰이 *아예 없다*).
6. **컴포넌트는 10개부터** — Button · Checkbox · Dialog · Menu · Progress · Radio · Select · Slider · Tabs · TextInput.
7. **Button 의 variant 축은 강조도와 의미를 분리한다** — 합치면 값이 곱으로 폭발한다.
8. **상태는 Figma 와 코드가 원리상 어긋난다** — Figma 킷의 1위 축이 `state` 인데 코드에서는 prop 이 아니라 의사클래스다. 자동 동기화를 시도하지 말고 계약 문서로 남긴다.

## 부록 — 측정에 쓴 소스 커밋

얕은 클론으로 받은 고정 커밋. 재현은 `bash sources/clone.sh`.

| key | repo | HEAD (전체) | 커밋일 | 용량 | 파일 수 | sparse 경로 |
|---|---|---|---|---:|---:|---|
| `ant-design` | ant-design/ant-design | `dae6efed9e3713e281312697b326868d95fb358c` | 2026-07-30 | 71M | 4969 | components |
| `carbon` | carbon-design-system/carbon | `0a75905da8e49901d60354c779fea2245a7a434d` | 2026-07-29 | 22M | 9396 | packages/colors packages/elements packages/grid packages/layout packages/motion packages/react packages/styles packages/themes packages/type |
| `fluentui` | microsoft/fluentui | `a50f6d4d680e8bdb811866473e3a89aea3c89def` | 2026-07-29 | 86M | 19063 | packages/react-components packages/tokens |
| `material-ui` | mui/material-ui | `319668c95b56b44c53541b48c09a2515d07704f5` | 2026-07-29 | 20M | 41098 | packages/mui-material packages/mui-styled-engine packages/mui-system packages/mui-utils |
| `material-web` | material-components/material-web | `70e259d464f627a21c7831cb4e871e0061bc0644` | 2026-07-23 | 31M | 1486 | (전체) |
| `polaris` | Shopify/polaris | `2b1ea88625e0613853ca8577c9acd1980a90f382` | 2025-12-20 | 14M | 4642 | polaris-react polaris-tokens |
| `radix-primitives` | radix-ui/primitives | `df8f89ac8e22e9cd4159e100a644ae94596fdd3a` | 2026-07-28 | 6.6M | 683 | (전체) |
| `react-spectrum` | adobe/react-spectrum | `3823fb84918e5819953092cfba9a603a7200c546` | 2026-07-30 | 64M | 10147 | packages/@adobe packages/@react-aria packages/@react-spectrum packages/@react-stately packages/@react-types |
| `shadcn-ui` | shadcn-ui/ui | `5203f537d152844a920caa66e865bc61c6ff4860` | 2026-07-29 | 25M | 5679 | apps/v4/app apps/v4/lib apps/v4/registry apps/v4/styles packages |
| `spectrum-css` | adobe/spectrum-css | `37620864c60c4c142a506017e1a15348a26abb0e` | 2026-04-06 | 20M | 1252 | (전체) |
| `spectrum-tokens` | adobe/spectrum-design-data | `ca0f605e617e27b3b7a5e0edefcf4ce45400a8fe` | 2026-07-29 | 28M | 2011 | (전체) |

### 시스템별 추출 경로

| 시스템 | 토큰 수 | 계층 | 추출 경로 |
|:---|---:|:---|:---|
| Spectrum | 935 | alias(semantic) | `spectrum-tokens/packages/tokens/src/{color-aliases,semantic-color-palette,layout,typography}.json` |
| Polaris | 519 | base theme(semantic) | `polaris/polaris-tokens/src/themes/base/*.ts` |
| Fluent 2 | 459 | alias(semantic) | `fluentui/packages/tokens/src/{alias/lightColor.ts,tokens.ts}` |
| Carbon | 341 | theme(semantic, DTCG) + scale | `carbon/packages/{themes/src/dtcg/white.json, layout\|type\|motion\|elements/src/tokens.ts}` |
| Ant Design | 228 | seed→map→alias | `ant-design/components/theme/interface/{seeds,alias,maps/*}.ts` |
| Material Web | 192 | sys(semantic) | `material-web/tokens/{,versions/v0_192/}_md-sys-*.scss` |
| MUI | 109 | palette/typography/shape(semantic) | `material-ui/packages/mui-material/src/styles/*.d.ts (타입 선언)` |
| shadcn/ui | 93 | semantic(단층) | `shadcn-ui/apps/v4/app/globals.css (:root CSS vars)` |

---

생성: `python3 analysis/standard-research/run.py` — 데이터는 `measured/` · `derived/` · `curated/` 에서 읽는다.  
측정 스크립트: `extract_tokens.py` · `classify_tokens.py` · `extract_components.py` · `measure_dependency.py` · `mfi.py`
