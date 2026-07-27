# Design QA

**Comparison Target**

- Source visual truth: https://getdesign.md/spotify/design-md
- Source dark preview: https://getdesign.md/design-md/spotify/preview-dark
- Implementation: `http://127.0.0.1:4173/`
- State: logged-out landing page and login form, dark theme
- Viewports: desktop `1440x900`, mobile `390x844`
- Comparison constraint: the source is a design-system catalog and the implementation is a product screen, so the review evaluates system-level fidelity rather than identical content composition.

**Evidence**

- Desktop source: `/private/tmp/spotify-source-desktop.png`
- Desktop implementation: `/private/tmp/spotify-implementation-desktop.png`
- Desktop full-view comparison: `/private/tmp/spotify-comparison-desktop.png`
- Mobile source: `/private/tmp/spotify-source-mobile.png`
- Mobile implementation: `/private/tmp/spotify-implementation-mobile.png`
- Mobile full-view comparison: `/private/tmp/spotify-comparison-mobile.png`
- Source forms: `/private/tmp/spotify-source-forms-desktop.png`
- Implementation login form: `/private/tmp/spotify-implementation-login-desktop.png`
- Focused form comparison: `/private/tmp/spotify-comparison-forms.png`

**Findings**

- No actionable P0, P1, or P2 differences remain.
- Typography: bold/regular hierarchy, compact UI sizing, letter spacing, and Helvetica/Pretendard fallback preserve the source's dense scanning rhythm while supporting Korean copy.
- Spacing and layout: the 8px rhythm, pill controls, 8px surfaces, desktop sidebar, and mobile bottom navigation remain stable at both checked viewports; mobile has no horizontal overflow.
- Colors and tokens: near-black canvas, charcoal surfaces, white/silver text, functional green, error red, and heavy dark elevation match the source palette and semantic use.
- Image quality and assets: neither checked state requires source imagery; Matchday's score and team initials are product content rather than substitutes for a source asset.
- Copy and content: landing and login copy remain coherent for a competition-operations product without copying Spotify's music IA or trademarks.
- Icons and accessibility: Lucide icons are visually consistent, controls retain practical tap targets, and the focused password input exposes the green focus ring in computed browser styles.

**Primary Interactions Tested**

- Desktop landing page to email login navigation.
- Desktop email and password entry, including keyboard focus styling.
- Mobile persistent bottom navigation to login.
- Desktop and mobile landing layout without horizontal overflow.
- Browser console and page errors with the anonymous session API isolated by the existing E2E GraphQL mock: none.

**Comparison History**

1. Initial focused comparison found a P2 form-state mismatch: the source preview used a green focus ring while Input, Select, and Textarea rendered a white `2px` inset ring. Browser computed style confirmed `rgb(255, 255, 255)`.
2. Updated Input, Select, and Textarea focus shadows to `var(--primary)`.
3. Re-captured the implementation and focused comparison at `1440x900`. The post-fix browser check confirmed `rgb(30, 215, 96)`, and `/private/tmp/spotify-comparison-forms.png` shows the source and implementation focus treatment together.
4. Re-ran the desktop and mobile interaction checks; both passed with no console or page errors.

**Implementation Checklist**

- [x] Match dark palette, surface hierarchy, typography, pill geometry, and elevation.
- [x] Verify desktop sidebar and mobile bottom navigation.
- [x] Verify landing-to-login navigation, form input, focus state, and console output.
- [x] Capture and compare desktop, mobile, and focused form evidence.

**Follow-up Polish**

- No blocking polish remains. The source catalog and Matchday product screen intentionally use different content structures.

final result: passed
