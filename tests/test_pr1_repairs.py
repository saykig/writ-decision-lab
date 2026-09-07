"""Durable union of the two PR #1 repair packets; synthetic inputs only."""
from dataclasses import FrozenInstanceError
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from support import ROOT, changed, encoded, fixture, parsed
from writ_decision_lab import check_and_load, check_bytes, solve_bytes
from writ_decision_lab.checker import report_bytes
from writ_decision_lab.decode import decode_json, decode_inputs, decode_result, parse_rational
from writ_decision_lab.errors import CheckFailure, WdlError
from writ_decision_lab.identity import code_digest, digest_bytes, output_bytes, source_manifest
from writ_decision_lab.types import CheckedAnswer, CheckReport


def wrong_bundle(result):
    # R0=1/4 and c=0: scalars remain mutually consistent but disagree with joint losses.
    result['answer'].update(observed_risk='0/1', evsi='1/4', net_value='1/4')
    result['answer']['acquisition_risks']['observe_once'] = '0/1'


class RepairTests(unittest.TestCase):
    def setUp(self):
        self.m, self.q = fixture('F01-weak')
        self.r = solve_bytes(self.m, self.q)

    def reject(self, call, status, code):
        with self.assertRaises(WdlError) as caught:
            call()
        self.assertEqual((caught.exception.status, caught.exception.diagnostic.code), (status, code))

    def test_deep_snapshots_and_summary_copies(self):
        for name in ('F01-weak', 'F07-real-tie', 'F08-zero-prior'):
            m,q = fixture(name)
            r = solve_bytes(m,q)
            original = parsed(r)['answer']
            checked = check_and_load(m,q,r)
            self.assertEqual(output_bytes(checked.answer), output_bytes(original))
            with self.assertRaises(TypeError):
                checked.answer['evsi'] = '999/1'
            with self.assertRaises((AttributeError, TypeError)):
                checked.answer['current_argmin'].append('unchecked')
            with self.assertRaises(TypeError):
                checked.answer['branches'][0]['posterior'][0] = '0/1'
            with self.assertRaises((AttributeError, TypeError)):
                checked.answer['branches'][0]['argmin'].clear()
            with self.assertRaises(TypeError):
                checked.answer['acquisition_risks']['observe_once'] = '999/1'
            with self.assertRaises(FrozenInstanceError):
                checked.answer = {}
            summary = checked.summary()
            summary['current_argmin'].clear()
            summary['evsi'] = '999/1'
            self.assertEqual(output_bytes(checked.answer), output_bytes(original))
            self.assertEqual(checked.summary()['evsi'], original['evsi'])
            self.assertEqual(checked.result_sha256, digest_bytes(r))
        raw = parsed(self.r)['answer']
        detached = CheckedAnswer(raw, 'm', 'q', 'r')
        raw['branches'][0]['posterior'].clear()
        self.assertTrue(detached.answer['branches'][0]['posterior'])

    def test_check_record_snapshot_consistency(self):
        for r in (self.r, b'{}'):
            report = check_bytes(self.m,self.q,r)
            before = report_bytes(report)
            with self.assertRaises(TypeError):
                report.record['status'] = 'unchecked'
            with self.assertRaises(TypeError):
                report.record['subject']['model_sha256'] = 'changed'
            with self.assertRaises((AttributeError, TypeError)):
                report.record['limitations'].clear()
            if report.diagnostics:
                with self.assertRaises(TypeError):
                    report.record['diagnostics'][0]['message'] = 'changed'
            copy = parsed(before)
            detached = CheckReport(copy, report.status, report.diagnostics, report.policy_count)
            copy['status'] = 'changed'
            copy['subject'].clear()
            self.assertEqual(report_bytes(detached), before)
            self.assertEqual(parsed(before)['status'], report.status)

    def test_entire_consumer_boundary_structures_failures(self):
        for target in ('checker.check_bytes', 'decode_result', 'CheckedAnswer'):
            with patch('writ_decision_lab.consumer.'+target, side_effect=RuntimeError('SYNTHETIC_PRIVATE')):
                self.reject(lambda: check_and_load(self.m,self.q,self.r), 'checker_error', 'E_CHECKER_INTERNAL')
        error = WdlError('out_of_scope', 'E_JSON_DEPTH', '$', 'JSON nesting exceeds 32 levels.')
        with patch('writ_decision_lab.consumer.decode_result', side_effect=error):
            self.reject(lambda: check_and_load(self.m,self.q,self.r), 'out_of_scope', 'E_JSON_DEPTH')

    def test_depth_boundary_deep_arrays_objects_and_quoted_delimiters(self):
        for opening, closing in ((b'[', b']'), (b'{"x":', b'}')):
            decode_json(opening*31+b'0'+closing*31, kind='model')
            for n in (32,33,995,1100,2000):
                data = opening*n+b'0'+closing*n
                self.reject(lambda: decode_json(data,kind='model'), 'out_of_scope','E_JSON_DEPTH')
                report = check_bytes(data,self.q,self.r)
                self.assertEqual(report.status, 'out_of_scope')
                self.assertEqual(report.diagnostics[0].code,'E_JSON_DEPTH')
        decode_json(b'['*32+b']'*32, kind='model')  # Empty leaf at level 32.
        quoted = encoded({'x': '[]{}"\\' * 2000})
        self.assertEqual(decode_json(quoted, kind='model'), json.loads(quoted))
        for malformed in (b'[{]', b'{"x":', b'"unterminated', b'{}[]'):
            self.reject(lambda: decode_json(malformed, kind='model'), 'invalid_input','E_JSON')

    def test_manifest_independently_reconstructed_from_repository_root(self):
        entries = [{'path':p.relative_to(ROOT).as_posix(),
                    'sha256':'sha256:'+sha256(p.read_bytes()).hexdigest()}
                   for p in sorted((ROOT/'src/writ_decision_lab').rglob('*.py'))
                   if '__pycache__' not in p.parts]
        self.assertEqual(source_manifest(),entries)
        for entry in entries:
            self.assertTrue(entry['path'].startswith('src/writ_decision_lab/'))
            self.assertTrue((ROOT/entry['path']).is_file())
        raw = (json.dumps(entries,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)+'\n').encode('ascii')
        self.assertEqual(code_digest(),'sha256:'+sha256(raw).hexdigest())

    def test_diagnostics_never_echo_untrusted_keys_or_values(self):
        canary = 'SYNTHETIC_PRIVATE_CANARY'
        cases = []
        for value in (canary, {canary:'\ud800'}, [canary+'\ud800'], {canary+'\ud800':canary}):
            cases.append((self.m,changed(self.q,lambda q:q.__setitem__(canary,value)),self.r))
            cases.append((self.m,self.q,changed(self.r,lambda r:r['answer']['branches'][0].__setitem__(canary,value))))
        cases.append((self.m,self.q,changed(self.r,lambda r:r['answer'].__setitem__('loss_unit',canary+'!'))))
        for m,q,r in cases:
            report=check_bytes(m,q,r)
            self.assertEqual(report.status,'invalid_input')
            self.assertNotIn(canary.encode(),report_bytes(report))
            self.assertLess(len(output_bytes([d.as_dict() for d in report.diagnostics])),512)

    def test_correlated_wrong_answer_correct_hashes(self):
        wrong=changed(self.r,wrong_bundle)
        self.assertEqual(parsed(wrong)['input_bindings'],parsed(self.r)['input_bindings'])
        self.assertEqual(check_bytes(self.m,self.q,wrong).status,'computation_mismatch')

    def test_positive_whitespace_rebinding_and_other_producer_source(self):
        m,q=self.m+b' ',self.q+b'\n'
        self.assertEqual(check_bytes(m,q,self.r).status,'input_mismatch')
        self.assertEqual(check_bytes(m,q,solve_bytes(m,q)).status,'checked')
        r=parsed(self.r)
        r['input_bindings']={'model_sha256':digest_bytes(m),'query_sha256':digest_bytes(q)}
        r['producer']['code_sha256']='sha256:'+'a'*64
        self.assertEqual(check_bytes(m,q,encoded(r)).status,'checked')
        self.assertEqual(check_bytes(self.m,self.q,self.r).status,'checked')

    def test_exact_byte_digit_limits_and_escaped_duplicate(self):
        m=self.m+b' '*(1024*1024-len(self.m))
        q=self.q+b' '*(1024*1024-len(self.q))
        decode_inputs(m,q)
        r=solve_bytes(m,q)
        r+=b' '*(4*1024*1024-len(r))
        self.assertEqual(check_bytes(m,q,r).status,'checked')
        for mm,qq,rr in ((m+b' ',q,r),(m,q+b' ',r),(m,q,r+b' ')):
            self.assertEqual(check_bytes(mm,qq,rr).diagnostics[0].code,'E_BYTE_LIMIT')
        for limit in (32,4096):
            self.assertEqual(parse_rational('1/'+'9'*limit,'$.cost',digit_limit=limit).numerator,1)
            self.reject(lambda:parse_rational('1/'+'9'*(limit+1),'$.cost',digit_limit=limit),'out_of_scope','E_RATIONAL_LIMIT')
        duplicate=self.q.rstrip()[:-1]+b',"co\\u0073t":"1/1"}'
        self.assertEqual(check_bytes(self.m,duplicate,self.r).diagnostics[0].code,'E_JSON_DUPLICATE_KEY')


class RepairProcessTests(unittest.TestCase):
    setUp = RepairTests.setUp
    # Separate process cases explicitly propagate the parent optimization mode.
    def run_python(self, root, *args):
        run=subprocess.run([sys.executable,*(['-O'] if sys.flags.optimize else []),*map(str,args)],
            cwd=root,env={**os.environ,'PYTHONPATH':str(root/'src')},capture_output=True)
        return run

    def test_fresh_process_producer_disabled(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=Path(tmp)/'result.json';r.write_bytes(self.r)
            script='''
import inspect,json,sys
from pathlib import Path
from writ_decision_lab import solver,check_and_load
from writ_decision_lab.errors import CheckFailure
from writ_decision_lab.identity import output_bytes
m=Path('examples/weak/model.json').read_bytes();q=Path('examples/weak/query.json').read_bytes()
r=Path(sys.argv[1]).read_bytes()
def disabled(*a,**k): raise RuntimeError('producer disabled')
names=[n for n,v in vars(solver).items() if inspect.isfunction(v) and v.__module__==solver.__name__]
for n in names: setattr(solver,n,disabled)
c=check_and_load(m,q,r)
if c.summary()['evsi']!='1/8': raise RuntimeError('positive control failed')
bad=json.loads(r);bad['answer'].update(observed_risk='0/1',evsi='1/4',net_value='1/4');bad['answer']['acquisition_risks']['observe_once']='0/1'
try: check_and_load(m,q,output_bytes(bad))
except CheckFailure as e:
    if e.status!='computation_mismatch': raise
else: raise RuntimeError('wrong answer exposed')
print(json.dumps({'optimized':sys.flags.optimize,'disabled':names}))
'''
            run=self.run_python(ROOT,'-c',script,r)
            self.assertEqual(run.returncode,0,run.stderr)
            result=json.loads(run.stdout)
            self.assertEqual(result['optimized'],sys.flags.optimize)
            self.assertTrue(result['disabled'])

    def test_consumer_process_all_statuses_and_post_check_faults(self):
        cases=[('valid',self.m,self.q,self.r,0),('missing',None,self.q,self.r,6),
            ('unsupported',self.m,changed(self.q,lambda q:q.__setitem__('semantics','unsupported')),self.r,3),
            ('invalid',b'{}',self.q,self.r,2),('stale',self.m,self.q+b' ',self.r,4),
            ('wrong',self.m,self.q,changed(self.r,wrong_bundle),5)]
        for fault in ('checker.check_bytes','decode_result','CheckedAnswer'):
            cases.append((fault,self.m,self.q,self.r,70))
        for name,m,q,r,exit_code in cases:
            with self.subTest(case=name),tempfile.TemporaryDirectory() as tmp:
                d=Path(tmp)
                for role,data in (('m',m),('q',q),('r',r)):
                    if data is not None: (d/role).write_bytes(data)
                args=['--expected-model',d/'m','--expected-query',d/'q','--result',d/'r','--output',d/'out']
                if exit_code==70:
                    script="import runpy;from unittest.mock import patch\nwith patch('writ_decision_lab.consumer."+name+"',side_effect=RuntimeError('SYNTHETIC_PRIVATE')): runpy.run_path('examples/consume_answer.py',run_name='__main__')"
                    run=self.run_python(ROOT,'-c',script,*args)
                else: run=self.run_python(ROOT,ROOT/'examples/consume_answer.py',*args)
                self.assertEqual(run.returncode,exit_code,run.stderr)
                self.assertEqual((d/'out').exists(),exit_code==0)
                self.assertNotIn(b'SYNTHETIC_PRIVATE',run.stderr)
                self.assertEqual(run.stdout,b'')
                if exit_code==0: self.assertEqual(parsed((d/'out').read_bytes())['evsi'],'1/8')

    def test_cli_depth_and_canaries_in_stderr_and_records(self):
        canary='SYNTHETIC_PRIVATE_CANARY'
        cases=[(b'['*n+b'0'+b']'*n,3,'E_JSON_DEPTH') for n in (32,33,995,1100,2000)]
        cases += [(b'{"x":'*1100+b'0'+b'}'*1100,3,'E_JSON_DEPTH'),(b'[{]',2,'E_JSON')]
        for value,code in ((canary,'E_UNKNOWN_FIELD'),({canary:'\ud800'},'E_UNICODE_SCALAR')):
            cases.append((changed(self.m,lambda m:m.__setitem__(canary,value)),2,code))
        for m,exit_code,diagnostic in cases:
            with tempfile.TemporaryDirectory() as tmp:
                d=Path(tmp);(d/'m').write_bytes(m);(d/'r').write_bytes(self.r)
                run=self.run_python(ROOT,'-m','writ_decision_lab','check','--model',d/'m',
                    '--query',ROOT/'examples/weak/query.json','--result',d/'r','--output',d/'check')
                self.assertEqual(run.returncode,exit_code,run.stderr)
                record=(d/'check').read_bytes()
                self.assertEqual(parsed(record)['diagnostics'][0]['code'],diagnostic)
                self.assertNotIn(canary.encode(),record+run.stderr)

    def test_cli_nested_query_and_result_canaries(self):
        canary = 'SYNTHETIC_PRIVATE_CANARY'
        for role in ('query', 'result'):
            for value in (canary, {canary: '\ud800'}, {canary+'\ud800': canary}):
                q, r = self.q, self.r
                if role == 'query':
                    q = changed(q, lambda q: q.__setitem__(canary, value))
                else:
                    r = changed(r, lambda r: r['answer']['branches'][0].__setitem__(canary, value))
                with tempfile.TemporaryDirectory() as tmp:
                    d = Path(tmp)
                    (d/'q').write_bytes(q)
                    (d/'r').write_bytes(r)
                    run = self.run_python(ROOT, '-m', 'writ_decision_lab', 'check',
                        '--model', ROOT/'examples/weak/model.json', '--query', d/'q',
                        '--result', d/'r', '--output', d/'check')
                    self.assertEqual(run.returncode, 2, run.stderr)
                    self.assertNotIn(canary.encode(), (d/'check').read_bytes()+run.stderr)
                    consume = self.run_python(ROOT, ROOT/'examples/consume_answer.py',
                        '--expected-model', ROOT/'examples/weak/model.json', '--expected-query', d/'q',
                        '--result', d/'r', '--output', d/'out')
                    self.assertEqual(consume.returncode, 2, consume.stderr)
                    self.assertNotIn(canary.encode(), consume.stderr)
                    self.assertFalse((d/'out').exists())

    def test_genuinely_relocated_sources_solve_check_consume(self):
        artifacts=[]
        with tempfile.TemporaryDirectory() as tmp:
            for name in ('one','different/tree/two'):
                root=Path(tmp)/name
                for directory in ('src','examples'):
                    shutil.copytree(ROOT/directory,root/directory,ignore=shutil.ignore_patterns('__pycache__'))
                identity=self.run_python(root,'-c',"import json,sys;from pathlib import Path;from writ_decision_lab.identity import source_manifest;print(json.dumps({'optimized':sys.flags.optimize,'manifest':source_manifest(),'root':str(Path.cwd())}))")
                self.assertEqual(identity.returncode,0,identity.stderr)
                observed=json.loads(identity.stdout)
                self.assertEqual(observed['optimized'],sys.flags.optimize)
                self.assertEqual(observed['manifest'],source_manifest())
                for entry in observed['manifest']:
                    self.assertEqual(digest_bytes((root/entry['path']).read_bytes()),entry['sha256'])
                common=['--model','examples/weak/model.json','--query','examples/weak/query.json']
                commands=[['-m','writ_decision_lab','solve',*common,'--output','result.json'],
                    ['-m','writ_decision_lab','check',*common,'--result','result.json','--output','check.json'],
                    ['examples/consume_answer.py','--expected-model','examples/weak/model.json','--expected-query','examples/weak/query.json','--result','result.json','--output','consumer.json']]
                for command in commands:
                    run=self.run_python(root,*command)
                    self.assertEqual(run.returncode,0,run.stderr)
                artifacts.append(tuple((root/file).read_bytes() for file in ('result.json','check.json','consumer.json')))
        self.assertEqual(*artifacts)


class BaselineQualificationTests(unittest.TestCase):
    def test_duplicate_labels_and_escaped_cost_unequal_assurance(self):
        sys.path.insert(0,str(ROOT/'comparison'))
        import baseline
        m,q=fixture('F01-weak')
        cases=[(changed(m,lambda m:m.__setitem__('outcomes',['x','x'])),q),
               (m,changed(q,lambda q:q.__setitem__('actions',['a','a']))),
               (m,q.rstrip()[:-1]+b',"co\\u0073t":"1/1"}')]
        for mm,qq in cases:
            self.assertTrue(baseline.consume(mm,qq,baseline.produce(mm,qq)))
            with self.assertRaises(WdlError): solve_bytes(mm,qq)

    def test_injected_shared_algorithm_fault_is_not_natural_bug(self):
        sys.path.insert(0,str(ROOT/'comparison'))
        import baseline
        m,q=fixture('F01-weak')
        original=baseline._compute
        def injected(mm,qq):
            return original(mm,changed(qq,lambda q:q.__setitem__('cost','1/2')))
        with patch.object(baseline,'_compute',injected):
            answer=baseline.consume(m,q,baseline.produce(m,q))
        self.assertEqual(answer['net_value'],'-3/8')
        self.assertEqual(answer['acquisition_argmin'],['act_now'])
        r=parsed(solve_bytes(m,q));r['answer']=answer
        self.assertEqual(check_bytes(m,q,encoded(r)).status,'computation_mismatch')
