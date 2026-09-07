"""Read-only Git preservation audit and exact tracked archive validation."""
from pathlib import Path
import subprocess,json,hashlib,tarfile,sys,os
R=Path('/Users/kimchee/Documents/writ-decision-lab-build1');O=Path(__file__).resolve().parents[1]
def git(*a):return subprocess.check_output(['git','-C',str(R),*a])
def h(b):return hashlib.sha256(b).hexdigest()
def save(n,v):(O/'evidence'/n).write_text(json.dumps(v,indent=2)+'\n')
head='36b9bbf7dc3f92a647d9e6a341aa7334e0610cbd';old='cd8016eda9ccf17ccda4cdb2c37b22f72660bf76';repair='3b0ca2b05cbd0118662e50034e99c75aa49ad4a5'
if git('rev-parse','HEAD').decode().strip()!=head:raise RuntimeError('HEAD moved')
initial=json.loads((O/'evidence/initial-tracked-hashes.json').read_text())
for e in initial:
 if h((R/e['path']).read_bytes())!=e['sha256']:raise RuntimeError('working file changed '+e['path'])
with tarfile.open(O/'tracked-source.tar') as t:
 members={m.name:m for m in t.getmembers() if m.isfile()}
 if set(members)!={e['path'] for e in initial}:raise RuntimeError('archive membership mismatch')
 for e in initial:
  if h(t.extractfile(members[e['path']]).read())!=e['sha256']:raise RuntimeError('archive byte mismatch')
(O/'TRACKED_SOURCE_SHA256SUMS').write_text(''.join(e['sha256']+'  '+e['path']+'\n' for e in initial))
old_paths=git('ls-tree','-r','--name-only',old).decode().splitlines()
preserved=[];modified=[]
for p in old_paths:
 before=git('show',old+':'+p);after=git('show',head+':'+p)
 if before==after:preserved.append(p)
 else:modified.append(p)
protected=[p for p in old_paths if p.startswith(('fixtures/','research_probe/','outputs/','sources/')) or p in ('BUILD_1_REPORT.md','comparison/baseline.py')]
if not all(p in preserved for p in protected):raise RuntimeError('historical protected bytes changed')
if not git('show',head+':HANDOFF.md').startswith(git('show',old+':HANDOFF.md')):raise RuntimeError('handoff not append-only')
save('preservation-current.json',{'head':head,'tracked_files':len(initial),'working_tree_all_match':True,'archive_members_and_bytes_match':True,'protected_files':protected,'protected_count':len(protected),'unchanged_original_paths':preserved,'changed_original_paths':modified,'handoff_append_only':True,'evidence_commit_changed_paths':git('diff','--name-only',repair,head).decode().splitlines(),'git_status':git('status','--porcelain=v1').decode(),'git_diff_check_exit':subprocess.run(['git','-C',str(R),'diff','--check']).returncode})
# Compare all existing numerical fixtures between untouched original and current sources.
oldtar=O/'evidence/original-source.tar'
subprocess.run(['git','-C',str(R),'archive','--format=tar','--output='+str(oldtar),old],check=True)
oldroot=O/'evidence/original-source';oldroot.mkdir()
subprocess.run(['tar','-xf',str(oldtar),'-C',str(oldroot)],check=True)
script='''import json,sys
from pathlib import Path
from writ_decision_lab import solve_bytes,check_bytes
out={}
for d in sorted(Path('fixtures/v1').iterdir()):
 m=(d/'model.json').read_bytes();q=(d/'query.json').read_bytes();r=solve_bytes(m,q);c=check_bytes(m,q,r)
 out[d.name]={'result':json.loads(r),'status':c.status,'policies':c.policy_count}
print(json.dumps(out,sort_keys=True))
'''
results=[]
for label,root in [('original',oldroot),('current',R)]:
 cmd=[sys.executable,'-c',script];run=subprocess.run(cmd,cwd=root,env={**os.environ,'PYTHONPATH':str(root/'src'),'PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,check=True)
 (O/'evidence'/('fixture-results-'+label+'.json')).write_bytes(run.stdout);results.append(json.loads(run.stdout))
checks=[]
for name,a in results[0].items():
 b=results[1][name]
 oldhash=a['result']['producer']['code_sha256'];newhash=b['result']['producer']['code_sha256']
 aa=json.loads(json.dumps(a));bb=json.loads(json.dumps(b));aa['result']['producer'].pop('code_sha256');bb['result']['producer'].pop('code_sha256')
 if aa!=bb or b['status']!='checked':raise RuntimeError('fixture wire or mathematical mismatch '+name)
 checks.append({'fixture':name,'identical_except_producer_source_hash':True,'status':b['status'],'policy_count':b['policies']})
save('fixture-compatibility.json',{'original':old,'current':head,'runtime':sys.version,'old_source_digest':oldhash,'new_source_digest':newhash,'checks':checks,'command':cmd,'note':'New fixed-fixture compatibility execution; not original reviewer replay. Existing 16 fixtures only.'})
print(json.dumps({'tracked_files':len(initial),'protected_files':len(protected),'modified_original':modified,'fixture_comparisons':len(checks),'archive_sha256':h((O/'tracked-source.tar').read_bytes())},indent=2))
