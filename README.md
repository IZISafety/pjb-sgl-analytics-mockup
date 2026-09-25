# PJB & SGL analytics, interactive mockup

Mockup of the merged **Prejob briefing and Safety green light** analytics for the IZI Safety platform, built while the two old pages were redesigned into one.

**Open it:** https://USER.github.io/REPO/

Every figure, company and site name in this page is invented. No client data is used.

## What it shows

Two tabs, as the platform has them:

**PJB & SGL**

- **Number of forms**: totals and a chart over the period, split by outcome (GO, GO corrected, STOP), with a volume / percentage toggle and a legend that hides and shows an outcome.
- **Form origin**: at intervention start, during intervention, no intervention.
- **Percentage of prejob briefing linked to an e-permit**: the existing widget, with the forms linked to no permit added so the slices reach 100%.
- **Comparison of results**: the three outcomes across companies, sites and workspaces.

**Cross data**

The existing tab with PJB & SGL added to the KPI picker. The picker is live: pick at least two indicators and the three widgets follow.

Blocks designed but kept for a later release are in the file, hidden behind `display:none`: corrective actions and the STOP funnel, overrides by initiator, top 10 recurring risks, alone or accompanied, briefing substance.

## Rules the page follows

- **Time axis**: up to 31 days, one bar per day. 32 to 92 days, one bar per fortnight. Beyond that, one bar per month. Values are summed in the bucket, and in percentage mode the share is computed on the bucket total rather than averaged across days.
- **Outcome colours**: GO `#0E7C5A`, GO corrected `#6AA22B`, STOP `#C81E1E`. Two greens because both mean the work started; they are far enough apart to stay distinguishable under red-green colour blindness, and every chart also carries a label or a value table.
- **Wording**: STOP is never plural, the three outcomes are always capitalised, the merged form is written PJB & SGL.

## Files

| Path | What it is |
|---|---|
| `index.html` | The page. One file, no build step, no external dependency, opens offline. |
| `source/page.html` | The template, with `/*__DATA__*/{}` where the data is injected. |
| `source/build.py` | Generates `data.json` and asserts it is consistent. |
| `source/data.json` | The placeholder payload. |

## Rebuilding after a change

Edit `source/page.html`, then:

```bash
cd source
python3 build.py                     # regenerates data.json and checks it
python3 - <<'EOF'
data = open("data.json", encoding="utf-8").read().replace("\n", "").replace("  ", "")
page = open("page.html", encoding="utf-8").read()
open("../index.html", "w", encoding="utf-8").write(page.replace("/*__DATA__*/{}", data))
EOF
```

`build.py` refuses to write a payload that contradicts itself: the three outcomes must sum to the submitted total, origin and permit must each sum to the same total, and the forms with no permit must be the same count as the forms with no intervention.

## Publishing

GitHub Pages, from the default branch, root folder. `.nojekyll` is there so Jekyll leaves the file alone.
