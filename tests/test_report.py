import json
from personalisation_engine.core import run
from personalisation_engine.fixtures import fixture
from personalisation_engine.report import render

def test_report_matches_ground_truth_exact():
    result=json.loads(render(run(fixture()),'json'))
    assert result['counts'] == {'records':200,'generated':120,'abstained':80,'labelled':200,'true_positives':120,'false_positives':0,'true_negatives':80,'false_negatives':0}

def test_report_zero_false_positives():
    assert run(fixture())['counts']['false_positives'] == 0

def test_report_carries_provenance_banner():
    for fmt in ('md','json'):
        assert 'SYNTHETIC fixtures' in render(run(fixture()),fmt)
        data=fixture(0); data['synthetic']=False
        assert 'REAL inputs' in render(run(data),fmt)

def test_hypothetical_figures_labelled():
    for fmt in ('md','json'):
        output=render(run(fixture()),fmt)
        assert 'time saved and money saved are unmeasured; no estimates' in output

def test_no_em_dashes_in_outputs():
    for fmt in ('md','json'):
        assert chr(8212) not in render(run(fixture()),fmt)
