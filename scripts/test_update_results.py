"""Exercise the published renderer without changing the checked-in results."""
import copy
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
ADDITIONS = [
    ('GPT-6.1 Terra', 'OpenAI'),
    ('Claude Haiku 5.5', 'Anthropic'),
    ('Kimi K3.1 Pro', 'Moonshot AI'),
    ('MiniMax M3.1 Flash', 'MiniMax'),
]


def original_collection():
    data = json.loads((ROOT / 'data/five-run-summary.json').read_text())
    data['models'] = [m for m in data['models']
                      if m['collection_date'] in ('2026-10-04', '2026-10-14')]
    for rank, model in enumerate(data['models'], 1):
        model['rank'] = rank
    extensions = data.get('extensions', [data['latest_extension']])
    data['latest_extension'] = next(e for e in extensions
                                    if e['collection_date'] == '2026-10-14')
    data.pop('extensions', None)
    data.pop('collection_dates', None)
    data['llm_numeric'] = sum(m['numeric'] for m in data['models'])
    data['llm_scheduled'] = 16 * 280
    return data


def extended_collection(unscored=False):
    data = original_collection()
    previous = copy.deepcopy(data['latest_extension'])
    addition = {'collection_date': '2026-10-29', 'models': [],
                'strict_models': [], 'unscored_models': []}
    for index, (name, provider) in enumerate(ADDITIONS):
        addition['models'].append(name)
        if unscored and name == 'Claude Haiku 5.5':
            addition['unscored_models'].append({
                'name': name, 'reason': 'No complete EPQ axis was available',
                'numeric': 0, 'scheduled': 280})
            continue
        model = copy.deepcopy(data['models'][0])
        model.update(name=name, provider=provider, numeric=280, missing=0,
                     distance=0.7 + index / 100, collection_date='2026-10-29',
                     release_path='repeated-runs/2026-10-29',
                     parser='strict whole-answer integer')
        data['models'].append(model)
        addition['strict_models'].append(model)
    for rank, model in enumerate(data['models'], 1):
        model['rank'] = rank
    data['latest_extension'] = addition
    data['extensions'] = [previous, addition]
    data['collection_dates'] = ['2026-10-04', '2026-10-14', '2026-10-29']
    data['llm_numeric'] = sum(m['numeric'] for m in data['models'])
    data['llm_scheduled'] = 20 * 280
    return data


class RenderResultsTests(unittest.TestCase):
    def assertContains(self, text, page):
        self.assertTrue(text in page, f"Rendered page is missing {text!r}")

    def assertOmits(self, text, page):
        self.assertFalse(text in page, f"Rendered page unexpectedly contains {text!r}")

    def render(self, data):
        with tempfile.TemporaryDirectory(prefix='moralitybench-render-') as folder:
            target = Path(folder)
            (target / 'scripts').mkdir()
            (target / 'data').mkdir()
            shutil.copyfile(ROOT / 'scripts/update_results.py',
                            target / 'scripts/update_results.py')
            shutil.copyfile(ROOT / 'index.html', target / 'index.html')
            (target / 'data/five-run-summary.json').write_text(json.dumps(data))
            result = subprocess.run([sys.executable, '-B', 'scripts/update_results.py'],
                                    cwd=target, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            return (target / 'index.html').read_text()

    def test_original_sixteen_model_collection_is_preserved(self):
        page = self.render(original_collection())
        self.assertEqual(page.count('<tr data-distance='), 16)
        self.assertContains('16 + Jev', page)
        self.assertContains('4,295 / 4,480', page)
        self.assertContains('Gemini often ignored the answer instructions.', page)
        self.assertContains('2026-10-14/five-run-summary.json', page)

    def test_three_collections_update_counts_links_and_keep_gemini_notes(self):
        page = self.render(extended_collection())
        self.assertEqual(page.count('<tr data-distance='), 20)
        self.assertContains('We asked 20 LLM configurations', page)
        self.assertContains('20 + Jev', page)
        self.assertContains('across 20 LLMs and Jev', page)
        self.assertContains('3 dated groups', page)
        self.assertContains('October 29', page)
        self.assertContains('2026-10-29">October 29 data', page)
        self.assertContains('2026-10-14">October 14 data', page)
        self.assertContains('Gemini often ignored the answer instructions.', page)
        self.assertContains('2026-10-14/five-run-summary.json', page)
        self.assertContains('2026-10-14/gemini-instruction-addendum.md', page)
        self.assertOmits('2026-10-29/five-run-summary.json">Inspect both parser', page)
        chart = re.search(r'const chartModels = (\[.*?\]);', page, re.S)
        self.assertEqual(len(json.loads(chart.group(1))), 20)
        self.assertContains('20 ranked models', page)
        self.assertOmits('between the two groups', page)

    def test_unscored_model_is_counted_as_tested_without_being_plotted(self):
        page = self.render(extended_collection(unscored=True))
        self.assertEqual(page.count('<tr data-distance='), 19)
        self.assertContains('20 + Jev', page)
        self.assertContains('We asked 20 LLM configurations', page)
        self.assertContains('19 ranked models', page)
        self.assertContains('Claude Haiku 5.5 is not ranked:', page)
        self.assertContains('No complete EPQ axis was available', page)
        self.assertContains('2026-10-29', page)


if __name__ == '__main__':
    unittest.main()
