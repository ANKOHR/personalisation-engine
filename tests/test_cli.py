import json
import subprocess
import sys
import time
from pathlib import Path
from personalisation_engine.cli import main, write
from personalisation_engine.fixtures import fixture

def test_run_completes_on_fixture(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    start=time.perf_counter()
    assert main(['fixtures','--out','demo']) == 0
    assert main(['run','--input','demo']) == 0
    assert main(['report','--format','md','--out','report.md']) == 0
    assert time.perf_counter()-start < 5
    assert 'SYNTHETIC' in Path('report.md').read_text()

def test_empty_input_renders_without_traceback(tmp_path, capsys):
    assert main(['run','--input',str(tmp_path),'--result',str(tmp_path/'result.json')]) == 0
    assert main(['report','--result',str(tmp_path/'result.json')]) == 0
    assert 'records: 0' in capsys.readouterr().out

def test_malformed_input_named_error(tmp_path, capsys):
    (tmp_path/'input.json').write_text('{\n invalid')
    assert main(['validate','--input',str(tmp_path)]) == 2
    error=capsys.readouterr().err
    assert 'ParseError' in error and 'input.json' in error and 'line 2' in error

def test_determinism_byte_identical(tmp_path):
    write(tmp_path/'input.json', fixture())
    output=tmp_path/'result.json'
    args=['run','--input',str(tmp_path),'--result',str(output)]
    main(args); first=output.read_bytes(); main(args)
    assert output.read_bytes()==first
    for fmt in ('md','json'):
        target=tmp_path/f'report.{fmt}'
        args=['report','--result',str(output),'--format',fmt,'--out',str(target)]
        main(args); first=target.read_bytes(); main(args)
        assert target.read_bytes()==first

def test_cli_smoke_all_subcommands(tmp_path):
    for cmd in ('fixtures','run','report','validate','preview'):
        result=subprocess.run([sys.executable,'-m','personalisation_engine.cli',cmd,'--help'],capture_output=True,text=True)
        assert result.returncode==0 and 'Example:' in result.stdout
    main(['fixtures','--out',str(tmp_path)])
    assert main(['validate','--input',str(tmp_path)])==0
    assert main(['preview','--input',str(tmp_path/'tiny')])==0

def test_missing_input_and_schema_errors(tmp_path,capsys):
    assert main(['run','--input',str(tmp_path/'absent')])==2
    assert 'MissingInput' in capsys.readouterr().err
    write(tmp_path/'input.json',{'synthetic':True})
    assert main(['validate','--input',str(tmp_path)])==2
    assert 'as_of' in capsys.readouterr().err

def test_write_failure_no_partial_files(tmp_path,capsys):
    write(tmp_path/'input.json',fixture())
    assert main(['run','--input',str(tmp_path),'--result',str(tmp_path)])==2
    assert 'WriteError' in capsys.readouterr().err
    assert sorted(p.name for p in tmp_path.iterdir())==['input.json']
