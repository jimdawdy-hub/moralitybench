#!/usr/bin/env python3
"""Render public results from the checked-in, reproducible five-run summary."""
import html
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'data/five-run-summary.json').read_text())
MODELS = DATA['models']
JEV = DATA['jev']
PUBLIC = 'https://github.com/FreecaseAI/moralitybench-data'
STUDY = PUBLIC + '/tree/master/repeated-runs/2026-10-04'
PAPER = PUBLIC + '/blob/master/paper/moralitybench.md'
esc = html.escape


def show(value):
    return f'{value:.2f}'


def category_note(model):
    return ', '.join(f'{name}: {count} of 5 runs' for name, count in model['category_counts'].items())


def render_leaderboard():
    rows = []
    for m in MODELS:
        rank = m['rank']
        cells = ''.join(f'<td>{show(v)}</td>' for v in m['foundations'])
        category = f'<span class="{m["ideology"].lower()}">{m["ideology"]}</span>'
        if m['category_changed']:
            category += '<small class="cell-note">Varied by run*</small>'
        rows.append(f'''<tr data-distance="{m['distance']}" data-agreement="{m['agreement']}">
          <td><span class="rank rank-{rank}">{rank}</span></td>
          <th scope="row"><div class="model-name">{esc(m['name'])}</div><div class="model-provider">{esc(m['provider'])}</div></th>
          <td><strong>{show(m['distance'])}</strong><small class="cell-note" title="Lowest to highest distance across the five runs">{show(m['distance_min'])} to {show(m['distance_max'])}</small></td>
          <td><strong>{m['agreement']:.1f}%</strong></td>
          {cells}
          <td title="{esc(category_note(m))}">{category}</td>
          <td>{m['missing']}<small class="cell-note">of 280</small></td>
        </tr>''')
    same_rows = ''.join(f'<tr><th scope="row">{esc(m["name"])}</th><td>{m["matched_pairs"]} / {m["compared_pairs"]}</td><td>{m["all_five_identical_items"]} / {m["all_five_observed_items"]}</td><td>{esc(category_note(m))}</td></tr>' for m in MODELS)
    leader = MODELS[0]
    complete = max((m for m in MODELS if m['missing'] == 0), key=lambda m: m['agreement'])
    changed = sum(m['category_changed'] for m in MODELS)
    return f'''<section id="leaderboard">
  <div class="section-header">
    <h2>Leaderboard</h2>
    <p>13 LLMs, each tested five times. Ranked by average distance from US human reference scores. Lower distance means a closer profile; it does not mean a better moral judgment.</p>
  </div>
  <div class="card-grid">
    <div class="card metric-card"><div class="metric-label">Closest on average</div><div class="metric-value" style="font-size:1.25rem">{esc(leader['name'])}</div><div class="metric-sub">Average distance: {show(leader['distance'])}</div></div>
    <div class="card metric-card"><div class="metric-label">Most repeatable with complete data</div><div class="metric-value" style="font-size:1.25rem">{esc(complete['name'])}</div><div class="metric-sub">{complete['agreement']:.1f}% agreement · 280/280 answers</div></div>
    <div class="card metric-card"><div class="metric-label">EPQ group changed between runs</div><div class="metric-value">{changed} of 13</div><div class="metric-sub">Small score shifts can cross a category boundary</div></div>
    <div class="card metric-card"><div class="metric-label">Usable answers across five runs</div><div class="metric-value">{DATA['llm_numeric']:,} / {DATA['llm_scheduled']:,}</div><div class="metric-sub">Missing answers remain visible below</div></div>
  </div>
  <div class="results-guide" id="agreement-explainer">
    <p><strong>Agreement across 5 runs:</strong> We compare answers to the same question across every pair of runs. An 80% result means the answers matched in 8 out of 10 comparisons. Higher agreement means more repeatable answers, not more ethical answers.</p>
    <p><strong>Reading the scores:</strong> Distance, foundation scores, and EPQ scores are averages across five runs. The small numbers under distance show its lowest and highest values. Missing answers are excluded from both scoring and agreement; read the missing count alongside each percentage.</p>
    <p class="chart-note">The original run and four additional runs are included. Models may have been served by different providers or backend versions. <a href="{STUDY}">Download the data and calculation details</a> · <a href="{PAPER}">Read the working paper</a></p>
  </div>
  <div class="table-wrap" tabindex="0" role="region" aria-label="Five-run LLM leaderboard; scroll horizontally to see all scores">
    <table id="leaderboard-table" aria-describedby="agreement-explainer">
      <caption class="visually-hidden">Five-run average scores and exact pairwise agreement; initial order is lowest average distance first.</caption>
      <thead><tr><th scope="col">#</th><th scope="col">Model</th><th scope="col" aria-sort="ascending"><button type="button" data-sort="distance">Avg. distance ↑</button></th><th scope="col"><button type="button" data-sort="agreement">Agreement<br><span class="header-note">across 5 runs</span></button></th><th scope="col">Care</th><th scope="col">Equality</th><th scope="col">Proportionality</th><th scope="col">Loyalty</th><th scope="col">Authority</th><th scope="col">Purity</th><th scope="col">EPQ group*</th><th scope="col">Missing</th></tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
  </div>
  <p class="chart-note" style="margin-top:1rem">*EPQ groups use the average scores. “Varied by run” means the model crossed a group boundary at least once. Missing covers unavailable or unusable answers, including API errors; it does not necessarily mean a refusal.</p>
  <div class="norms-bar"><span class="norms-dot"></span>US human reference: Care 4.05 · Equality 2.88 · Proportionality 3.63 · Loyalty 2.81 · Authority 3.01 · Purity 2.26</div>
  <details class="repeat-details"><summary>See exact agreement counts and group changes</summary>
    <p>Each question can contribute 10 comparisons across five runs, for up to 560 comparisons per model. We omit any comparison with a missing answer. “Same in all 5” is a stricter check: how many questions received the identical answer in every run, among questions answered in all five. A question with four identical answers and one different answer has 60% pairwise agreement, but does not count as identical in all five.</p>
    <div class="table-wrap" tabindex="0"><table><thead><tr><th scope="col">Model</th><th scope="col">Matching / available comparisons</th><th scope="col">Same in all 5 / complete questions</th><th scope="col">EPQ groups by run</th></tr></thead><tbody>{same_rows}</tbody></table></div>
  </details>
</section>'''


def render_jev():
    m = JEV
    foundation = ''.join(f'<span>{name} <strong>{show(v)}</strong></span>' for name, v in zip(DATA['foundations'], m['foundations']))
    return f'''<section id="jev-comparison" aria-labelledby="jev-heading">
  <div class="section-header"><h2 id="jev-heading">Jev: A Non-LLM Comparison</h2><p>A structured decision model, evaluated separately from the 13 generative LLMs. Five runs are complete.</p></div>
  <div class="card">
    <div class="jev-copy"><p>TypeSafe describes Jev as a System One model. It returns structured scores, probabilities, and confidence values instead of generating a text answer. We tested the same 56 items five times using its separate questionnaire protocol.</p></div>
    <dl class="jev-summary">
      <div><dt>Agreement across 5 runs</dt><dd>{m['agreement']:.1f}%</dd></div>
      <div><dt>Average distance from US norms</dt><dd>{show(m['distance'])}</dd></div>
      <div><dt>Usable answers</dt><dd>280 / 280</dd></div>
      <div><dt>EPQ group in every run</dt><dd>{m['ideology']}</dd></div>
    </dl>
    <div class="jev-foundations" aria-label="Jev average foundation scores on a scale of 1 to 5">{foundation}</div>
    <div class="jev-copy">
      <p>Average EPQ scores: Idealism {show(m['idealism'])} / 9; Relativism {show(m['relativism'])} / 9. Distance ranged from {show(m['distance_min'])} to {show(m['distance_max'])} across the five runs.</p>
      <p><strong>What repeated.</strong> {m['matched_pairs']} of {m['compared_pairs']} answer comparisons matched, and {m['all_five_identical_items']} of 56 questions received the same rounded answer in all five runs. Its underlying continuous scores still varied. The agreement percentage describes the rounded questionnaire ratings.</p>
      <p><strong>Why it matters.</strong> A system that returns structured decisions can produce a repeatable questionnaire profile close to these human reference scores. That does not establish human-like beliefs or moral reasoning. Jev’s average Purity score is {show(m['foundations'][5])}, compared with the human reference of 2.26.</p>
      <p><strong>How to interpret it.</strong> Jev evaluated statements’ alignment with ethical principles in batches. The LLMs answered each question as an immediate self-description. Different prompts, interfaces, and score conversion prevent a controlled comparison of architectures, so Jev stays outside the LLM ranking and charts.</p>
    </div>
    <p class="jev-sources"><a href="{STUDY}">Five-run source records and analysis</a> · <a href="https://typesafe.ai/blog/introducing-system-one-models-and-jev">About Jev</a></p>
  </div>
</section>'''


def render_findings():
    return '''<section id="findings">
  <div class="section-header"><h2>Key Findings</h2><p>What changed when we asked the same questions five times.</p></div>
  <div class="findings-grid">
    <div class="finding"><h4>DeepSeek leads on average, but the winner changes</h4><p>DeepSeek has the lowest five-run average distance (0.24), followed by MiMo (0.25). MiMo led in three of the four new runs. These close results do not establish a lasting winner.</p></div>
    <div class="finding"><h4>Identical settings do not guarantee identical answers</h4><p>LLM agreement across all five runs ranges from 60.4% to 94.7%. Mistral has the highest percentage, with 31 missing answers out of 280. Among models with complete data, Llama has the highest agreement at 93.9%.</p></div>
    <div class="finding"><h4>Four models changed EPQ group</h4><p>DeepSeek, MiMo, Qwen, and Claude crossed a category boundary between runs. The charts show average scores; the leaderboard flags these changes. A label near the midpoint can change after a small score shift.</p></div>
    <div class="finding"><h4>The original Purity finding does not hold across repeats</h4><p>Every LLM exceeded the human Purity reference in the first run. Across five runs, DeepSeek averages 2.00, below the reference of 2.26. Four of the six Purity questions were replaced in this adapted instrument, which also limits the human comparison.</p></div>
  </div>
</section>'''


def main():
    path = ROOT / 'index.html'
    page = path.read_text()
    for identifier, renderer in [('leaderboard', render_leaderboard), ('jev-comparison', render_jev), ('findings', render_findings)]:
        page, count = re.subn(r'<section id="' + identifier + r'"[^>]*>.*?</section>', lambda _: renderer(), page, count=1, flags=re.S)
        assert count == 1, identifier
    chart_fields = ['name', 'foundations', 'idealism', 'relativism', 'ideology', 'category_changed', 'color']
    chart_models = [{key: m[key] for key in chart_fields} for m in MODELS]
    page, count = re.subn(r'const chartModels = \[.*?\];', lambda _: 'const chartModels = ' + json.dumps(chart_models, indent=2) + ';', page, count=1, flags=re.S)
    assert count == 1
    path.write_text(page)
    print('Rendered 13 LLM rows, Jev, findings, and synchronized chart averages.')


if __name__ == '__main__':
    main()
