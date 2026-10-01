import json
from personalisation_engine.fixtures import generate
from personalisation_engine.cli import write
from personalisation_engine.core import run

def test_fixtures_labelled_synthetic(tmp_path):
    generate(tmp_path, write)
    for path in tmp_path.rglob('*.json'):
        assert json.loads(path.read_text(encoding='utf-8'))['synthetic'] is True
    assert 'SYNTHETIC' in (tmp_path/'SYNTHETIC.md').read_text()

def test_fixture_ground_truth_matches_hand_computed(tmp_path):
    generate(tmp_path, write)
    data=json.loads((tmp_path/'input.json').read_text())
    expected=json.loads((tmp_path/'expectations.json').read_text())
    assert run(data)['counts'] == expected['counts']
    assert [r['expected_eligible'] for r in data['records']].count(True) == 120
