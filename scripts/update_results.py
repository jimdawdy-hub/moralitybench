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
STUDY = PUBLIC + '/tree/master/repeated-runs/2026-10-14'
ORIGINAL_STUDY = PUBLIC + '/tree/master/repeated-runs/2026-10-04'
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
          <th scope="row"><div class="model-name">{esc(m['name'])}</div><div class="model-provider">{esc(m['provider'])} · {esc(m.get('collection_date','2026-10-04'))}</div></th>
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
    <p>We tested {len(MODELS)} LLM configurations five times each. The ranking shows how close their average scores are to the US human reference. It cannot tell us which model makes better moral judgments.</p>
  </div>
  <div class="card-grid">
    <div class="card metric-card"><div class="metric-label">Closest on average</div><div class="metric-value" style="font-size:1.25rem">{esc(leader['name'])}</div><div class="metric-sub">Average distance: {show(leader['distance'])}</div></div>
    <div class="card metric-card"><div class="metric-label">Most repeatable with complete data</div><div class="metric-value" style="font-size:1.25rem">{esc(complete['name'])}</div><div class="metric-sub">{complete['agreement']:.1f}% agreement · 280/280 answers</div></div>
    <div class="card metric-card"><div class="metric-label">EPQ group changed between runs</div><div class="metric-value">{changed} of {len(MODELS)}</div><div class="metric-sub">Small score shifts can cross a category boundary</div></div>
    <div class="card metric-card"><div class="metric-label">Usable answers across five runs</div><div class="metric-value">{DATA['llm_numeric']:,} / {DATA['llm_scheduled']:,}</div><div class="metric-sub">Missing answers remain visible below</div></div>
  </div>
  <div class="results-guide" id="agreement-explainer">
    <p>Agreement measures how often a model gives the same answer. We compare each question across all ten pairs of runs; 80% means the answers matched in 8 out of 10 available comparisons. This percentage leaves moral quality unassessed.</p>
    <p>Scores and distances are averages of five runs. The range under each distance shows its lowest and highest values. We leave missing answers out of the calculations, so check the missing count as well as the agreement percentage.</p>
    <p class="chart-note">The first 13 models were tested by October 4. On October 14 we ran five new trials of GPT-6 Astra, Muse Wonder, and Gemini 4 Argon. We did not retest the earlier models. The new results accept only a complete integer answer; earlier results retain their original first-digit rule. The earlier trials span different times, while the new trials ran concurrently in one session. Providers and model versions may also differ. These differences limit comparisons between the two groups. <a href="{STUDY}">October 14 data and calculation details</a> · <a href="{ORIGINAL_STUDY}">Original five-run study</a> · <a href="{PAPER}">Read the working paper</a></p>
  </div>
  <div class="table-wrap" tabindex="0" role="region" aria-label="Five-run LLM leaderboard; scroll horizontally to see all scores">
    <table id="leaderboard-table" aria-describedby="agreement-explainer">
      <caption class="visually-hidden">Five-run average scores and exact pairwise agreement; initial order is lowest average distance first.</caption>
      <thead><tr><th scope="col">#</th><th scope="col">Model</th><th scope="col" aria-sort="ascending"><button type="button" data-sort="distance">Avg. distance ↑</button></th><th scope="col"><button type="button" data-sort="agreement">Agreement<br><span class="header-note">across 5 runs</span></button></th><th scope="col">Care</th><th scope="col">Equality</th><th scope="col">Proportionality</th><th scope="col">Loyalty</th><th scope="col">Authority</th><th scope="col">Purity</th><th scope="col">EPQ group*</th><th scope="col">Missing</th></tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
  </div>
  <p class="chart-note" style="margin-top:1rem">*EPQ groups come from the average scores. “Varied by run” marks a model that changed groups at least once. Missing answers include responses we could not score and API errors, as well as refusals.</p>
  <div class="norms-bar"><span class="norms-dot"></span>US human reference: Care 4.05 · Equality 2.88 · Proportionality 3.63 · Loyalty 2.81 · Authority 3.01 · Purity 2.26</div>
  <details class="repeat-details"><summary>See exact agreement counts and group changes</summary>
    <p>Five runs give ten pairs per question, or 560 comparisons for a fully answered questionnaire. We leave out pairs with a missing answer. “Same in all 5” counts only questions answered identically in every run, among questions answered in all five. Four matching answers and one different answer give 60% pairwise agreement, but fail this stricter check.</p>
    <div class="table-wrap" tabindex="0"><table><thead><tr><th scope="col">Model</th><th scope="col">Matching / available comparisons</th><th scope="col">Same in all 5 / complete questions</th><th scope="col">EPQ groups by run</th></tr></thead><tbody>{same_rows}</tbody></table></div>
  </details>
</section>'''


def render_jev():
    m = JEV
    foundation = ''.join(f'<span>{name} <strong>{show(v)}</strong></span>' for name, v in zip(DATA['foundations'], m['foundations']))
    return f'''<section id="jev-comparison" aria-labelledby="jev-heading">
  <div class="section-header"><h2 id="jev-heading">Jev: a separate comparison</h2><p>Jev completed five runs using a different prompt and interface from the {len(MODELS)} LLM configurations.</p></div>
  <div class="card">
    <div class="jev-copy"><p>TypeSafe calls Jev a System One model. It returns scores with probabilities and confidence values through a structured interface. We gave it the same 56 items five times, using its own questionnaire protocol.</p></div>
    <dl class="jev-summary">
      <div><dt>Agreement across 5 runs</dt><dd>{m['agreement']:.1f}%</dd></div>
      <div><dt>Average distance from US norms</dt><dd>{show(m['distance'])}</dd></div>
      <div><dt>Usable answers</dt><dd>280 / 280</dd></div>
      <div><dt>EPQ group in every run</dt><dd>{m['ideology']}</dd></div>
    </dl>
    <div class="jev-foundations" aria-label="Jev average foundation scores on a scale of 1 to 5">{foundation}</div>
    <div class="jev-copy">
      <p>Average EPQ scores: Idealism {show(m['idealism'])} / 9; Relativism {show(m['relativism'])} / 9. Distance ranged from {show(m['distance_min'])} to {show(m['distance_max'])} across the five runs.</p>
      <p>Jev matched in {m['matched_pairs']} of {m['compared_pairs']} answer comparisons. It gave the same rounded answer in all five runs on {m['all_five_identical_items']} of 56 questions. Its scores before rounding still varied; the agreement percentage uses the rounded ratings.</p>
      <p>Jev’s repeatable scores are close to the human reference, though the questionnaire cannot establish human-like beliefs or moral reasoning. Its average Purity score is {show(m['foundations'][5])}, against the human reference of 2.26.</p>
      <p>Jev rated how well batches of statements fit ethical principles. The LLMs answered one question at a time as an immediate self-description. The prompts, interfaces, and score conversions differ, so these results cannot show whether model design explains the difference. We report Jev separately from the LLM ranking and charts.</p>
    </div>
    <p class="jev-sources"><a href="{ORIGINAL_STUDY}">Five-run source records and analysis</a> · <a href="https://typesafe.ai/blog/introducing-system-one-models-and-jev">About Jev</a></p>
  </div>
</section>'''


def render_findings():
    leader=MODELS[0]
    complete=max((m for m in MODELS if m['missing']==0),key=lambda m:m['agreement'])
    changed=[m['name'] for m in MODELS if m['category_changed']]
    below=[m['name'] for m in MODELS if m['foundations'][5]<DATA['human_norms'][5]]
    addition=DATA['latest_extension']
    availability=addition.get('unscored_models',[])
    strict={m['name']:m for m in addition.get('strict_models',[])}
    gemini=strict.get('Gemini 4 Argon')
    sensitivity=(f"""<p><strong>Gemini often ignored the answer instructions.</strong> It gave {gemini['numeric']} complete integer answers out of 280. We excluded 125 responses, including 47 that described other frameworks’ ratings. Counting digits from those explanations would wrongly label its average profile Absolutist. The strict result is {esc(gemini['ideology'])} in all five runs. It answered few Equality and Authority items, so the profile covers only part of the questionnaire. <a href=\"{STUDY}/five-run-summary.json\">Inspect both parser calculations and item counts</a>. <a href="gemini-answers.html">Read Gemini’s original answers</a> · <a href="https://github.com/FreecaseAI/moralitybench-data/blob/master/repeated-runs/2026-10-14/gemini-instruction-addendum.md">Instruction-following addendum</a>.</p>""" if gemini else '')
    note=''.join(f"<p><strong>{esc(m['name'])} is not ranked:</strong> {esc(m['reason'])}. Its raw responses and missing-answer counts are preserved in the October 14 release.</p>" for m in availability)
    return f'''<section id="findings">
  <div class="section-header"><h2>Findings</h2><p>We collected these results in two groups and did not retest the earlier models.</p></div>
  <div class="findings-grid">
    <div class="finding"><h4>Closest average scores</h4><p>{esc(leader['name'])} has the lowest average distance ({leader['distance']:.3f}) from the selected human reference. The distance measures score similarity and cannot establish moral correctness.</p></div>
    <div class="finding"><h4>Repeatability differs</h4><p>Agreement ranges from {min(m['agreement'] for m in MODELS):.1f}% to {max(m['agreement'] for m in MODELS):.1f}%. Of the models that answered every item, {esc(complete['name'])} has the highest agreement ({complete['agreement']:.1f}%). A model with missing answers has fewer comparisons, so read the denominator too.</p></div>
    <div class="finding"><h4>{len(changed)} configurations changed EPQ group</h4><p>{esc(', '.join(changed))} changed groups between runs. Their average scores hide some of that movement.</p></div>
    <div class="finding"><h4>The Purity comparison has limits</h4><p>Models below the Purity reference: {esc(', '.join(below)) or 'none'}. We replaced four of the six Purity questions, so this is an exploratory comparison. The October 14 models have five new runs; earlier rows keep their original results. We leave unanswered items missing, without treating them as neutral.</p></div>
  </div>
  {sensitivity}
  {note}
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
    page=page.replace('across 13 LLMs',f'across {len(MODELS)} LLMs').replace('asked 13 LLMs',f'asked {len(MODELS)} LLMs').replace('13 + Jev',f'{len(MODELS)} + Jev').replace('all 13 models',f'all {len(MODELS)} models').replace('All 13 models',f'All {len(MODELS)} models')
    page=page.replace('We asked '+str(len(MODELS))+' LLMs the same 56 questions five times, using adapted moral psychology questionnaires.', 'We tested '+str(len(MODELS))+' LLM configurations on the same 56 questions five times, across October 4 and October 14 collections. Older configurations were not retested.')
    path.write_text(page)
    print('Rendered current LLM rows, Jev, findings, and synchronized chart averages.')


if __name__ == '__main__':
    main()
