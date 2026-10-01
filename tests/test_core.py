import copy
import pytest
from personalisation_engine.core import run, SchemaError
from personalisation_engine.fixtures import fixture

def test_rejects_adversarial_values():
    for mutate in (lambda d: d['records'].append(copy.deepcopy(d['records'][0])), lambda d: d['records'][0]['signals'][0].update(date='2027-01-01'), lambda d: d['records'][0].update(amount=-1), lambda d: d['records'][0].update(company='x'*201), lambda d: d.update(as_of='bad')):
        data = fixture(5)
        mutate(data)
        with pytest.raises(SchemaError): run(data)

def test_handles_unicode_and_long_inputs():
    data = fixture(5)
    data['records'][0]['company'] = '日本 café'
    data['records'][0]['signals'][0].update(fact='資料'*4000, source=r'C:\Users\Henry\evidence.md')
    assert '日本 café' in run(data)['rows'][0]['line']

def test_corrupted_ground_truth_changes_computed_figures():
    data = fixture()
    original = run(data)
    data['records'][0]['expected_eligible'] = False
    changed = run(data)
    assert changed['counts']['false_positives'] == 1
    assert changed['counts']['true_positives'] == original['counts']['true_positives'] - 1
    data['records'][1]['signals'] = []
    assert run(data)['counts']['generated'] == 119

def test_selection_latest_and_tie_deterministic():
    data = fixture(1)
    data['records'][0]['signals'].append({'kind':'hiring','fact':'Platform engineer vacancy posted','source':'manual note','date':'2026-09-02'})
    assert run(data)['rows'][0]['evidence']['kind'] == 'hiring'
