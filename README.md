# titanxgear-site

Coming-soon page for Titan X, meant to replace what is on titanxgear.com. Static HTML, CSS and JS, no build step.
Draft, 2026-11-22 11:51 AM PT. **Not approved and not published.** Publishing needs Mo's explicit yes.

## Run it locally

```powershell
python -m http.server 8091 --bind 127.0.0.1 -d C:/dev/titanxgear-site
```

Open http://localhost:8091. Screenshots: `node tools/screens.mjs` (server running) writes `screens/`, and exits 1
if a page overflows sideways, an image fails or the console shows an error.

## Files

| Path | What |
|---|---|
| `index.html`, `styles.css`, `main.js`, `waitlist.js` | The page |
| `img/` | Built images (WebP). Rebuild with `python -I tools/build-images.py` |
| `fonts/` | Fraunces, IBM Plex Sans and Mono, self hosted (SIL Open Font License, files beside them) |
| `source-img/` | Originals the images are built from. Not uploaded |
| `tools/` | Image build, app screen render, screenshots. Not uploaded |
| `screens/` | Desktop 1440 and phone 390 screenshots. Not uploaded |

## Where the content comes from

| On the page | Source |
|---|---|
| Headline, "One coach. Thirty athletes...", "The best sensor is the one the athlete doesn't have to remember", "Titan X flags exposure and recommends evaluation...", footer line | Pitch deck V1.0 (`Consulting\Titan X\Titan_X_Pitch_Deck_V1.0.pdf`), slides 1, 2, 5, 10, 16 |
| "wellness device" | DECISIONS.md D26 |
| "Built for wrestling first" | The task brief from Mo's Titan X session, 2026-11-22 |
| Hero photo, headgear render, logo | Pitch deck V1.0, slides 16, 6, 1. **Who made them and whether they may be used on a public site is not recorded.** |
| App screens | `C:\dev\titanx-coach\docs\design\ios` sheets 05, 08, 09, 10, 13 (design draft marked UNAPPROVED, made-up athletes). Not native simulator captures |
| "Athletes can also wear a Polar heart rate sensor" | titanx-coach commit "Engine 0.12.0: sensor roles (hr/contact/both)", 2026-11-17. To confirm before publishing |

Left out on purpose: prices (DECISIONS.md C12, open), SpO2 and core temperature (D21, D22), "concussion detection"
(D27), athletes per hub and latency (C4, deck says unvalidated targets), market figures, team, the LiveMat and
Sa7a Labs names (C10, open), football and rugby (D25).

## Waitlist

`waitlist.js` has `DESTINATION = 'preview'`: the form checks the email and says nothing was sent. Nothing leaves
the browser until Mo picks a destination and the config is filled in. Options:

| Option | How | For | Against |
|---|---|---|---|
| Supabase (the titanx-supabase project) | Table `waitlist` (email unique, role, created_at); RLS allows insert only, no select | Same place as future accounts; no extra service | Needs the project live and the table plus policy added |
| Formspree | Paste the form endpoint into `CONFIG.formspree` | Five minutes, emails also land in an inbox | Third party holds the list; free tier limits |

## Privacy policy page (/privacy)

Needed as the hosted privacy URL for the Titan X app's TestFlight external review. Source: the app's
`pack/docs/testflight/privacy-policy.md` (Titan X iOS repo on the Mac). Build:

```powershell
python -I tools/build-privacy.py C:\path\to\privacy-policy.md
```

It writes `privacy/index.html`, keeps Mo's blanks (`[legal entity]`, `[address]`, `[privacy email]`) highlighted
in yellow and never fills them, underlines "to confirm" notes, prints counts of both, and stops on Markdown it
cannot convert. Fill the blanks in the Markdown, rebuild, then upload `privacy/` with the rest. The URL is
`https://titanxgear.com/privacy/` (the server also answers `/privacy` with a redirect to it).

Not used: `C:\dev\titanx-coach\docs\testflight\privacy-policy.md` is an older draft (2026-11-11, 73 lines,
`MO_CONTACT_EMAIL`, says the app has no account or server).

## Temporary public preview (GitHub Pages)

Mo asked on 2026-11-22 for a public GitHub link to share, to be taken down once people have seen it.
Repo `mofarah01-hue/titanxgear-site` (public), Pages from `master`. Every page carries
`<meta name="robots" content="noindex">` so search engines skip it; remove that line from `index.html` and
`tools/build-privacy.py` when the site moves to titanxgear.com. Take the preview down: repo Settings, Pages,
Unpublish site (or make the repo private).

Terms of use (`content/terms.md`, page `terms/`): written 2026-11-22 by Claude from common practice for training
apps and a web search of comparable terms and Apple's HealthKit privacy rules. Not legal advice; blanks and
"counsel to confirm" items are Mo's. Build: `python -I tools/build-privacy.py content/terms.md --out terms --page-title "Terms of use" --status "..."`.

## Deploy to Hostinger (after Mo says yes)

**Found 2026-11-22:** titanxgear.com today is a different site, "Custom Sportswear for Teams - Titan X Apparel",
built with Hostinger Website Builder (response header `X-Powered-By: HostingerWebsiteBuilder`). Replacing it takes
that store offline, so the cofounder has to agree first. Website Builder cannot take uploaded HTML files; the
domain has to point at a Hostinger web hosting plan instead.

Steps for whoever holds the Hostinger login (Claude never signs in):

1. In hPanel, check the plan includes **Web hosting** (Premium or Business), not only Website Builder.
2. Websites → Add website → choose titanxgear.com (or a subdomain, e.g. `soon.titanxgear.com`, to keep the store) →
   "Empty website" / custom PHP-HTML.
3. Files → File Manager → `public_html` → upload `index.html`, `styles.css`, `main.js`, `waitlist.js`, `.htaccess`,
   and the folders `img/`, `fonts/` and `privacy/`. Do not upload `source-img/`, `tools/`, `screens/`.
4. If the domain is still tied to the Website Builder site, disconnect it there first (Website Builder →
   Settings → Domain). Back up or keep the builder site; nothing has to be deleted.
5. Security → SSL: make sure the certificate is active, then open https://titanxgear.com and check the form shows the
   preview message (or, once a destination is set, that a test email arrives).
