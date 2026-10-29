# MoralityBench.ai

[Live website](https://moralitybench.ai) · [Public data and analysis](https://github.com/FreecaseAI/moralitybench-data/tree/master/repeated-runs/2026-10-29) · [Working paper](https://github.com/FreecaseAI/moralitybench-data/blob/master/paper/moralitybench.md)

The site compares questionnaire response profiles from 20 LLM configurations over five administrations across October 4, October 14 and October 29 collections, with a separate structured-decision comparison for Jev. It uses an adapted MFQ-2 and EPQ. The human reference is exploratory because wording and four Purity items differ from the original instrument.

## Results

The October 29 extension adds five fresh runs for GPT-6.1 Terra, Claude Haiku 5.5, Kimi K3.1 Pro and MiniMax M3.1 Flash: all 1,120 answers are valid whole-answer integers. The October 14 additions use the same strict scoring; older rows retain their historical parser. Earlier models and Jev were not rerun. Concurrent new trials and older cross-time pairs are not strictly comparable; requested temperature does not prove backend enforcement. Gemini’s 47 prose-derived digits remain excluded, and its partial questionnaire remains flagged. [Latest data](https://github.com/FreecaseAI/moralitybench-data/tree/master/repeated-runs/2026-10-29) · [Updated paper](https://github.com/FreecaseAI/moralitybench-data/blob/master/paper/moralitybench.md).

The leaderboard reports average distance from US human reference means, exact answer agreement across all ten pairs of five runs, missing counts, and average foundation scores. Each run receives equal weight in score averages. Average distance is the mean of five per-run distances, not distance recalculated from the averaged profile. Missing answers are omitted, never scored as neutral or counted as matching each other. EPQ category changes are flagged.

| Model | Agreement across 5 runs | Valid answers | Average distance | Lowest to highest distance |
| --- | --- | --- | --- | --- |
| DeepSeek V4.1 Flash | 71.8% (399/556 pairs) | 279/280 | 0.239 | 0.142 to 0.312 |
| MiMo v2.6 Pro | 82.5% (462/560 pairs) | 280/280 | 0.253 | 0.207 to 0.278 |
| GPT-6.1 Terra | 74.5% (417/560 pairs) | 280/280 | 0.301 | 0.190 to 0.364 |
| GPT-6 Astra | 74.8% (419/560 pairs) | 280/280 | 0.304 | 0.261 to 0.333 |
| Gemini 4 Argon | 85.6% (249/291 pairs) | 155/280 | 0.335 | 0.210 to 0.420 |
| Nemotron 3 Ultra 550B | 60.4% (336/556 pairs) | 279/280 | 0.336 | 0.178 to 0.431 |
| GPT-6.1 Sol | 80.5% (451/560 pairs) | 280/280 | 0.340 | 0.278 to 0.389 |
| Gemini 3.8 Flash | 85.3% (451/529 pairs) | 269/280 | 0.379 | 0.298 to 0.492 |
| Qwen3.8 27B | 86.1% (482/560 pairs) | 280/280 | 0.380 | 0.353 to 0.397 |
| Claude Opus 5.5 | 90.6% (483/533 pairs) | 270/280 | 0.402 | 0.328 to 0.469 |
| Claude Haiku 5.5 | 80.0% (448/560 pairs) | 280/280 | 0.405 | 0.369 to 0.452 |
| Grok 4.7 | 63.2% (354/560 pairs) | 280/280 | 0.413 | 0.266 to 0.523 |
| Kimi K3.1 Pro | 72.1% (404/560 pairs) | 280/280 | 0.438 | 0.384 to 0.496 |
| Muse Wonder | 84.5% (473/560 pairs) | 280/280 | 0.482 | 0.440 to 0.548 |
| Kimi K3 | 70.1% (376/536 pairs) | 274/280 | 0.493 | 0.373 to 0.551 |
| Llama 4 Maverick | 93.9% (526/560 pairs) | 280/280 | 0.506 | 0.472 to 0.528 |
| GLM 5.3 | 68.8% (385/560 pairs) | 280/280 | 0.508 | 0.460 to 0.571 |
| MiniMax M3.1 Flash | 57.1% (320/560 pairs) | 280/280 | 0.518 | 0.357 to 0.634 |
| MiniMax M3 | 67.0% (375/560 pairs) | 280/280 | 0.589 | 0.568 to 0.651 |
| Mistral Large 2512 | 94.7% (415/438 pairs) | 249/280 | 0.644 | 0.599 to 0.702 |

Jev: 95.7% agreement, 280/280 ratings, mean distance 0.206. Its batched ethical-alignment task differs from the LLM self-description prompt, so it remains outside the leaderboard. Repeatability and closeness to the human reference do not measure moral correctness.

## Analytics

The live website uses the MoralityBench Google Analytics 4 property and the `MoralityBench website` web stream. Its public measurement ID is `G-TWHN1QS4PY`. The Google tag appears once in `index.html`; no API key or account credentials are needed by the site. Enhanced measurement covers page views, scrolls, outbound clicks, and file downloads. Search, form, and video measurements are disabled. Reporting uses Chicago time and US dollars.

After changing the tag, verify the published site with the stream's **Test installation** control and check **Realtime** in Analytics for incoming visits. Creating the property alone does not install tracking; the deployed HTML must contain the tag.

## Update and verify

The static page and SVG charts share values from `data/five-run-summary.json`, copied from the public data release. After recomputing the study and copying the verified summary, run:

```sh
python3 scripts/update_results.py
```

The renderer updates the leaderboard, Jev summary, key findings, and chart averages. Findings are written for this release; review their interpretation if the dataset changes. No build framework or external chart library is required. The leaderboard remains readable without JavaScript; JavaScript supplies sorting, model selection, and charts.

Before publishing, verify both sorting directions, chart selectors, all three SVG plots, synchronized legends, and narrow-screen scrolling. The data repository's analysis and verification scripts reproduce the numeric source.

## Publishing

The live custom domain currently belongs to [jimdawdy-hub/moralitybench](https://github.com/jimdawdy-hub/moralitybench), GitHub Pages from `master` at `/`. [FreecaseAI/moralitybench](https://github.com/FreecaseAI/moralitybench) holds the matching public website source; update the existing live mirror to publish without moving DNS. The data and working paper remain in FreecaseAI/moralitybench-data. This binding was verified through GitHub’s Pages API on October 29, 2026.
