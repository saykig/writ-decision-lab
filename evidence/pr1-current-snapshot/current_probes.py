"""New bounded current-snapshot probes. Not an archival reviewer script."""
import sys,os,json,hashlib,subprocess,unittest,inspect,operator,shutil
from pathlib import Path
from collections.abc import Mapping
from unittest.mock import patch
ROOT=Path(sys.argv[1]).resolve(); OUT=Path(sys.argv[2]).resolve()
sys.path.insert(0,str(ROOT/'src'))
from writ_decision_lab import solve_bytes,check_bytes,check_and_load
from writ_decision_lab import checker,consumer,solver
from writ_decision_lab.checker import report_bytes
from writ_decision_lab.decode import decode_json
from writ_decision_lab.identity import output_bytes,wire,source_manifest,code_digest
from writ_decision_lab.types import CheckedAnswer,CheckReport
from writ_decision_lab.errors import WdlError,CheckFailure
MODE='optimized' if sys.flags.optimize else 'normal'
D=OUT/MODE;D.mkdir(exist_ok=False)
OBS={}; COMMANDS=[]
def enc(v): return (json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)+'\n').encode()
def digest(b): return 'sha256:'+hashlib.sha256(b).hexdigest()
def fixture(name):
 d=ROOT/'fixtures/v1'/name
 return (d/'model.json').read_bytes(),(d/'query.json').read_bytes()
def run(root,args):
 cmd=[sys.executable,*(['-O'] if sys.flags.optimize else []),*map(str,args)]
 r=subprocess.run(cmd,cwd=root,env={**os.environ,'PYTHONPATH':str(root/'src'),'PYTHONDONTWRITEBYTECODE':'1'},capture_output=True)
 COMMANDS.append({'argv':cmd,'cwd':str(root),'exit':r.returncode,'stdout':r.stdout.decode(errors='replace'),'stderr':r.stderr.decode(errors='replace')})
 return r
class CurrentReview(unittest.TestCase):
 def setUp(self):
  self.m,self.q=fixture('F01-weak'); self.r=solve_bytes(self.m,self.q)
 def test_01_snapshots_all_nested_collections(self):
  totals={'collections':0,'fixtures':[]}
  def frozen(v):
   if isinstance(v,Mapping):
    totals['collections']+=1
    with self.assertRaises(TypeError): operator.setitem(v,'review_mutation','changed')
    for item in v.values(): frozen(item)
   elif isinstance(v,tuple):
    totals['collections']+=1
    with self.assertRaises((TypeError,AttributeError)): v.append('changed')
    for item in v: frozen(item)
  def mutate(v):
   if isinstance(v,dict):
    for x in list(v.values()): mutate(x)
    v.clear()
   elif isinstance(v,list):
    for x in list(v): mutate(x)
    v.clear()
  for name in ('F01-weak','F07-real-tie','F08-zero-prior','F10-acquisition-tie'):
   m,q=fixture(name); r=solve_bytes(m,q); c=check_and_load(m,q,r)
   raw=json.loads(r)['answer']; expected=enc(raw)
   alias=CheckedAnswer(raw,digest(m),digest(q),digest(r));mutate(raw)
   self.assertEqual(output_bytes(alias.answer),expected)
   frozen(c.answer); self.assertEqual(output_bytes(c.answer),expected)
   view=wire(c.answer); mutate(view); summary=c.summary(); initial=enc(summary);mutate(summary)
   self.assertEqual(output_bytes(c.answer),expected);self.assertEqual(enc(c.summary()),initial)
   self.assertEqual(c.result_sha256,digest(r));totals['fixtures'].append(name)
  variants=[self.r,b'{}',enc({**json.loads(self.r),'semantics':'unsupported'}),self.r+b' ']
  for r in variants:
   report=check_bytes(self.m,self.q,r);before=report_bytes(report);record=json.loads(before)
   frozen(report.record)
   alias=CheckReport(record,report.status,report.diagnostics,report.policy_count); mutate(record)
   self.assertEqual(report_bytes(alias),before)
   self.assertEqual(json.loads(before)['status'],report.status)
   self.assertEqual(json.loads(before)['policy_count'],report.policy_count)
   self.assertEqual(json.loads(before)['diagnostics'],[d.as_dict() for d in report.diagnostics])
   for diag in report.diagnostics:
    copy=diag.as_dict();copy.clear()
   self.assertEqual(report_bytes(report),before)
  OBS['snapshots']=totals
 def test_02_manifest_relocation_and_artifact_binding(self):
  entries=[{'path':p.relative_to(ROOT).as_posix(),'sha256':digest(p.read_bytes())} for p in sorted((ROOT/'src/writ_decision_lab').rglob('*.py')) if '__pycache__' not in p.parts]
  self.assertEqual(entries,source_manifest());aggregate=digest(enc(entries));self.assertEqual(aggregate,code_digest())
  (D/'source-manifest.json').write_bytes(enc(entries));OBS['source_digest']=aggregate
  collected=[]
  for label in ('relocated-one','relocated/deeper/two'):
   root=D/label
   for folder in ('src','examples'): shutil.copytree(ROOT/folder,root/folder,ignore=shutil.ignore_patterns('__pycache__'))
   r=run(root,['-c',"import sys,json;from pathlib import Path;from writ_decision_lab.identity import source_manifest,code_digest;import writ_decision_lab;print(json.dumps({'manifest':source_manifest(),'digest':code_digest(),'optimize':sys.flags.optimize,'module':writ_decision_lab.__file__}))"])
   self.assertEqual(r.returncode,0,r.stderr);info=json.loads(r.stdout)
   self.assertEqual(info['manifest'],entries);self.assertEqual(info['digest'],aggregate);self.assertEqual(info['optimize'],sys.flags.optimize)
   self.assertTrue(Path(info['module']).is_relative_to(root))
   for e in entries:self.assertEqual(digest((root/e['path']).read_bytes()),e['sha256'])
   for args in [ ['-m','writ_decision_lab','solve','--model','examples/weak/model.json','--query','examples/weak/query.json','--output','result.json'],['-m','writ_decision_lab','check','--model','examples/weak/model.json','--query','examples/weak/query.json','--result','result.json','--output','check.json'],['examples/consume_answer.py','--expected-model','examples/weak/model.json','--expected-query','examples/weak/query.json','--result','result.json','--output','consumer.json'] ]:
    r=run(root,args);self.assertEqual(r.returncode,0,r.stderr)
   artifacts={n:(root/n).read_bytes() for n in ('result.json','check.json','consumer.json')};collected.append(artifacts)
   result=json.loads(artifacts['result.json']);check=json.loads(artifacts['check.json'])
   self.assertEqual(result['producer']['code_sha256'],aggregate);self.assertEqual(check['checker']['code_sha256'],aggregate)
   self.assertEqual(check['subject'],{'model_sha256':digest((root/'examples/weak/model.json').read_bytes()),'query_sha256':digest((root/'examples/weak/query.json').read_bytes()),'result_sha256':digest(artifacts['result.json'])})
  self.assertEqual(*collected)
  OBS['artifact_hashes']={n:digest(b) for n,b in collected[0].items()}
 def test_03_depth_syntax_precedence(self):
  cases=[]
  for op,cl in ((b'[',b']'),(b'{"k":',b'}')):
   for n in (30,31,32,33,995,1100,2000):
    cases.append((op*n+b'null'+cl*n,None if n<32 else 'E_JSON_DEPTH'))
   cases.append((op*31+(b'[]' if op==b'[' else b'{}')+cl*31,None))
  for value in ('[{}]','\\"[{','\\\\"[]{}','a'*40+'[]{}\\"'*400):
   cases.append((b'['*31+enc(value).rstrip()+b']'*31,None))
  for data in (b'[{]',b'{"k":',b'"bad\\q"',b'{} []',b'[1,]',b']',b'"unterminated'):
   cases.append((data,'E_JSON'))
  # Once 33 containers were seen, later malformed syntax/Unicode does not replace resource rejection.
  cases.extend([(b'['*33+b'bad','E_JSON_DEPTH'),(b'{"k":'*33+b'"\\ud800"','E_JSON_DEPTH')])
  results=[]
  for data,expected in cases:
   try: decode_json(data,kind='model');code=None
   except WdlError as e: code=e.diagnostic.code;self.assertEqual(e.status,'out_of_scope' if code=='E_JSON_DEPTH' else 'invalid_input')
   self.assertEqual(code,expected,(len(data),data[:40]));results.append({'sha256':digest(data),'bytes':len(data),'diagnostic':code})
  OBS['depth_cases']=results
 def test_04_persistent_diagnostics_canaries(self):
  canary='CURRENT_REVIEW_PRIVATE_CANARY';cases=[]
  for role in ('model','query','result'):
   for value in (canary,{canary:[canary]}, {canary:'\ud800'}, {canary+'\udfff':canary},[canary+'\ud800']):
    m,q,r=self.m,self.q,self.r;obj=json.loads({'model':m,'query':q,'result':r}[role]);target=obj['answer']['branches'][0] if role=='result' else obj;target[canary]=value
    if role=='model':m=enc(obj)
    elif role=='query':q=enc(obj)
    else:r=enc(obj)
    cases.append((role,m,q,r))
  evidence=[]
  for i,(role,m,q,r) in enumerate(cases):
   d=D/('canary-'+str(i));d.mkdir()
   for name,b in [('m',m),('q',q),('r',r)]: (d/name).write_bytes(b)
   rep=check_bytes(m,q,r);self.assertEqual(rep.status,'invalid_input');self.assertNotIn(canary.encode(),report_bytes(rep))
   runcheck=run(ROOT,['-m','writ_decision_lab','check','--model',d/'m','--query',d/'q','--result',d/'r','--output',d/'check.json'])
   self.assertEqual(runcheck.returncode,2);self.assertNotIn(canary.encode(),(d/'check.json').read_bytes()+runcheck.stderr)
   consume=run(ROOT,['examples/consume_answer.py','--expected-model',d/'m','--expected-query',d/'q','--result',d/'r','--output',d/'answer.json'])
   self.assertEqual(consume.returncode,2);self.assertEqual(consume.stdout,b'');self.assertNotIn(canary.encode(),consume.stderr);self.assertFalse((d/'answer.json').exists())
   evidence.append({'role':role,'diagnostic':rep.diagnostics[0].as_dict()})
  OBS['canary_cases']=evidence
 def test_05_consumer_entire_guard_separate_processes(self):
  wrong=json.loads(self.r);wrong['answer'].update(observed_risk='0/1',evsi='1/4',net_value='1/4');wrong['answer']['acquisition_risks']['observe_once']='0/1'
  unsupported=json.loads(self.q);unsupported['semantics']='finite-two-observation.v1'
  cases=[('valid',self.m,self.q,self.r,0),('missing',None,self.q,self.r,6),('unsupported',self.m,enc(unsupported),self.r,3),('invalid',b'{}',self.q,self.r,2),('stale',self.m,self.q+b' ',self.r,4),('wrong',self.m,self.q,enc(wrong),5)]
  cases += [(name,self.m,self.q,self.r,70) for name in ('checker','decode','snapshot','hash1','hash2','hash3')]
  cases += [('typed_decode',self.m,self.q,self.r,3)]
  observations=[]
  for name,m,q,r,code in cases:
   d=D/('consumer-'+name);d.mkdir()
   for n,b in [('m',m),('q',q),('r',r)]:
    if b is not None:(d/n).write_bytes(b)
   script='''import sys,runpy,json
from pathlib import Path
from unittest.mock import patch
from writ_decision_lab import consumer
from writ_decision_lab.errors import WdlError
name=sys.argv.pop(1); trace=Path(sys.argv.pop(1)); events={'optimize':sys.flags.optimize,'checked_statuses':[]}
original=consumer.checker.check_bytes
real_hash=consumer.digest_bytes
calls=0
def observed(*a,**kw):
 if name=='checker': raise RuntimeError('CURRENT_PRIVATE_FAILURE')
 report=original(*a,**kw); events['checked_statuses'].append(report.status); return report
def fail(*a,**kw):
 if name=='typed_decode':raise WdlError('out_of_scope','E_JSON_DEPTH','$','JSON nesting exceeds 32 levels.')
 raise RuntimeError('CURRENT_PRIVATE_FAILURE')
def digest(*a,**kw):
 global calls
 calls+=1
 if name=='hash'+str(calls): fail()
 return real_hash(*a,**kw)
consumer.checker.check_bytes=observed
if name in ('decode','typed_decode'): consumer.decode_result=fail
if name=='snapshot': consumer.CheckedAnswer=fail
consumer.digest_bytes=digest
try: runpy.run_path('examples/consume_answer.py',run_name='__main__')
finally: trace.write_text(json.dumps(events))
'''
   launched=run(ROOT,['-c',script,name,d/'trace.json','--expected-model',d/'m','--expected-query',d/'q','--result',d/'r','--output',d/'functional.json'])
   self.assertEqual(launched.returncode,code,launched.stderr);self.assertEqual(launched.stdout,b'');self.assertNotIn(b'CURRENT_PRIVATE_FAILURE',launched.stderr)
   self.assertEqual((d/'functional.json').exists(),code==0)
   trace=json.loads((d/'trace.json').read_text());self.assertEqual(trace['optimize'],sys.flags.optimize)
   if name in ('decode','snapshot','hash1','hash2','hash3','typed_decode'): self.assertEqual(trace['checked_statuses'],['checked'])
   observations.append({'case':name,'exit':launched.returncode,**trace})
  OBS['consumer_cases']=observations
 def test_06_wrong_bundle_and_producer_disabled_controls(self):
  (D/'saved-result.json').write_bytes(self.r)
  script='''import sys,json,inspect
from pathlib import Path
from writ_decision_lab import check_and_load,solver
from writ_decision_lab.errors import CheckFailure
from hashlib import sha256
m=Path('fixtures/v1/F01-weak/model.json').read_bytes();q=Path('fixtures/v1/F01-weak/query.json').read_bytes();r=Path(sys.argv[1]).read_bytes()
def enc(x):return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\\n').encode()
def h(x):return 'sha256:'+sha256(x).hexdigest()
def disabled(*a,**k):raise RuntimeError('producer disabled')
names=[n for n,v in vars(solver).items() if inspect.isfunction(v) and v.__module__==solver.__name__]
for n in names:setattr(solver,n,disabled)
out={'disabled':names,'optimize':sys.flags.optimize,'cases':{}}
def check(name,m,q,r):
 try: a=check_and_load(m,q,r);out['cases'][name]='checked'
 except CheckFailure as e:out['cases'][name]=e.status
check('valid',m,q,r)
bad=json.loads(r);bad['answer'].update(observed_risk='0/1',evsi='1/4',net_value='1/4');bad['answer']['acquisition_risks']['observe_once']='0/1'
check('coherent_wrong_correct_hashes',m,q,enc(bad))
check('whitespace_stale',m+b' ',q+b'\\n',r)
rebound=json.loads(r);rebound['input_bindings']={'model_sha256':h(m+b' '),'query_sha256':h(q+b'\\n')};rebound['producer']['code_sha256']='sha256:'+'b'*64
check('whitespace_rebound_other_producer',m+b' ',q+b'\\n',enc(rebound))
check('original_again',m,q,r)
print(json.dumps(out))
'''
  child=run(ROOT,['-c',script,D/'saved-result.json']);self.assertEqual(child.returncode,0,child.stderr);info=json.loads(child.stdout)
  self.assertEqual(info['optimize'],sys.flags.optimize);self.assertEqual(set(info['disabled']),{'_argmin','calculate','solve_with_context','solve_bytes'})
  self.assertEqual(info['cases'],{'valid':'checked','coherent_wrong_correct_hashes':'computation_mismatch','whitespace_stale':'input_mismatch','whitespace_rebound_other_producer':'checked','original_again':'checked'})
  self.assertEqual(check_bytes(self.m+b' ',self.q,solve_bytes(self.m+b' ',self.q)).status,'checked')
  OBS['producer_disabled']=info
 def test_07_eight_step_and_baseline_qualification(self):
  r=run(ROOT,['comparison/run_sequence.py','--output',D/'comparison.json']);self.assertEqual(r.returncode,0,r.stderr)
  comparison=json.loads((D/'comparison.json').read_bytes())
  for arm in ('candidate','simpler_baseline'):
   self.assertEqual(len(comparison[arm]['steps']),8);self.assertTrue(comparison[arm]['all_passed']);self.assertEqual(comparison[arm]['erroneous_downstream_uses'],0)
   old=json.loads((ROOT/'outputs/comparison.json').read_bytes());self.assertEqual(comparison[arm]['steps'],old[arm]['steps'])
  sys.path.insert(0,str(ROOT/'comparison'));import baseline
  m=json.loads(self.m);m['outcomes']=['x','x'];q=json.loads(self.q);q['actions']=['a','a']
  pairs=[(enc(m),self.q),(self.m,enc(q)),(self.m,self.q.rstrip()[:-1]+b',"co\\u0073t":"1/2"}')]
  for m,q in pairs:
   self.assertTrue(baseline.consume(m,q,baseline.produce(m,q)))
   with self.assertRaises(WdlError):solve_bytes(m,q)
  real=baseline._compute
  def injected(m,q):
   q=json.loads(q);q['cost']='1/2';return real(m,enc(q))
  with patch.object(baseline,'_compute',injected): wrong=baseline.consume(self.m,self.q,baseline.produce(self.m,self.q))
  self.assertEqual(wrong['net_value'],'-3/8');self.assertEqual(wrong['acquisition_argmin'],['act_now'])
  result=json.loads(self.r);result['answer']=wrong;self.assertEqual(check_bytes(self.m,self.q,enc(result)).status,'computation_mismatch')
  OBS['baseline']={'historical_steps_equal':True,'duplicate_cases':3,'injected_not_natural_fault':True,'injected_net_value':wrong['net_value']}
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(CurrentReview))
 (D/'observations.json').write_bytes(enc({'reviewed_commit':'36b9bbf7dc3f92a647d9e6a341aa7334e0610cbd','python':sys.version,'optimize':sys.flags.optimize,'testsRun':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'observations':OBS}))
 (D/'commands.json').write_bytes(enc(COMMANDS))
 sys.exit(not result.wasSuccessful())
