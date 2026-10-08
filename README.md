# PJB & SGL analytics, interactive mockup

Mockup of the **Enhanced KPIs** for the IZI Safety platform: the merged Prejob briefing and Safety green light analytics, and the new HSE Observation tab.

**Open it:** https://izisafety.github.io/pjb-sgl-analytics-mockup/

Every figure, company and site name in this page is invented. No client data is used.

## What it shows

Three tabs, as the platform has them:

**PJB & SGL**

- **Number of forms**: totals and a chart over the period, split by outcome (GO, GO corrected, STOP), with a volume / percentage toggle and a legend that hides and shows an outcome.
- **Forms attachment to intervention**: a ring on every submitted form, at intervention check-in, during intervention, without intervention.
- **Percentage of forms linked to an e-permit**: its own card. Two figures for the period, e-permit and paper permit, and a stacked bar chart of the two types day by day, with a legend that hides and shows a type. Counted on the forms created at intervention check-in only, standalone forms excluded.
- **Comparison of results**: the three outcomes across companies, sites and workspaces.

**HSE Observation**

- **Number of observations**: totals and a chart over the period, split between good practice and anomaly. The banner figures are the legend and the filter: each carries the colour that draws it, and clicking one takes that kind out of the chart. The Stop Card is a part of the anomalies, so it is hatched inside the orange and never stacked on it.
- **Observations by category**: two rings, good practice in shades of blue and anomalies in shades of safety orange, each with its list of volumes and shares. Computed on the categories selected rather than on the observations, since one observation can carry several.
- **Anomalies by Golden rules**: one bar per golden rule, anomalies only, since a good practice carries no golden rule. Sorted by volume. The share where a Stop Card was used is hatched over the bar, and clicking a bar opens the Observed anomaly list ticked under that rule.
- **Comparison of results**: across companies, sites and workspaces. Category is deliberately not a dimension here: it is a multi select, so its rows would sum to more than the observations, unlike a company, a site or a workspace. The categories have their own block, the two rings.

**Cross data**

The existing tab with PJB & SGL and HSE Observation added to the KPI picker. The picker is live: pick at least two indicators and the three widgets follow.

Blocks designed but kept for a later release are in the file, hidden behind `display:none`: corrective actions and the STOP funnel, overrides by initiator, top 10 recurring risks, alone or accompanied, briefing substance.

## Rules the page follows

- **Time axis**: up to 31 days, one bar per day. 32 to 92 days, one bar per fortnight. Beyond that, one bar per month. Values are summed in the bucket, and in percentage mode the share is computed on the bucket total rather than averaged across days.
- **Outcome colours**: GO `#1C9C5C`, GO corrected `#32CD32`, STOP `#FF1515`, with `--go-ink` `#157544` and `--stop-ink` `#B3050A` where those colours are written rather than filled. One lime family at two strengths for the greens, 16 apart in normal vision; the GO leans a few degrees towards emerald because a pure green darkens towards the red under deuteranopia. Every chart also carries a label or a value table.
- **The platform blue** `#004196` means the same thing in two places on purpose: the forms created at intervention check-in, and the e-permit share of those same forms.
- **HSE Observation colours**: good practice `#6C20DF`, a cool violet, anomaly `#FF6700`, the safety orange. Not the GO green and the STOP red, which belong to the PJB & SGL outcomes. The pair sits 43 apart in normal vision and 35 under protanopia. The categories are told apart by lightness inside one family: one colour per ring laid at 100%, 74%, 56% and 40%, Safety at full strength, fixed per category rather than per rank.
- **The Stop Card** has no colour of its own. It is hatching: 45 degree stripes in `--hatch` `#E4FDFF`, an electric white cooled towards cyan, drawn at full opacity over the orange. 4.6px on a 10px pitch in the charts, 1.6px on 4.5px in an 11px legend swatch, because a texture does not carry from a large surface to a small one unchanged.
- **Paper grey** `#968F85`, warm rather than slate: on this page blue means inside the digital flow and grey means outside it, which is what a paper permit and a standalone form are.
- **Wording**: STOP is never plural, the three outcomes are always capitalised, the merged form is written PJB & SGL, and **Stop Card stays singular** since it names a question on the form rather than a countable object.
- **Figures**: a tile that counts a part of the tile before it is written one size down. Tile numbers are in the ordinary ink, not in the colour of what they count. No figure is repeated across the volume and percentage views, and every percentage names its base in words.
- **Type of chart**: a Type dropdown at the top right of a block changes the drawing, never the data. Charts over time offer stacked bars, grouped bars, lines and stacked areas; the comparisons offer stacked bars, grouped bars and a table. The golden rules have no dropdown, the table only repeated the two numbers the tooltip gives.
- **Multi-select**: an observation can carry several categories, so that breakdown adds up to more than the number of observations. The golden rules are counted on the anomalies alone and add up to more than the number of anomalies. Company, site and workspace still sum to the total exactly, and `build.py` asserts the right rule for each.

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

`build.py` refuses to write a payload that contradicts itself: 59 assertions. The three outcomes must sum to the submitted total, the origin ring must sum to that same total, the permit figures over the period and day by day must sum to the forms created at intervention check-in, and **a Stop Card never outnumbers the anomalies at any cut**, day by day included, since it lives on an anomaly.

## Publishing

GitHub Pages, from the default branch, root folder. `.nojekyll` is there so Jekyll leaves the file alone.
