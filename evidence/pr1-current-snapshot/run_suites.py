"""Review-only complete-suite runner; observes Popen commands without changing them."""
import sys,unittest,json,subprocess,os
from pathlib import Path
root=Path(sys.argv[1]).resolve(); out=Path(sys.argv[2]).resolve()
mode='optimized' if sys.flags.optimize else 'normal'
sys.path.insert(0,str(root/'src'));sys.path.insert(0,str(root/'tests'))
events=[]
def audit(event,args):
 if event=='subprocess.Popen': events.append({'executable':str(args[0]),'argv':list(map(str,args[1])),'cwd':str(args[2])})
sys.addaudithook(audit)
suite=unittest.defaultTestLoader.discover(str(root/'tests'))
result=unittest.TextTestRunner(verbosity=2).run(suite)
record={'runtime':sys.version,'optimize':sys.flags.optimize,'testsRun':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'subprocesses':events}
(out/('suite-'+mode+'.json')).write_text(json.dumps(record,indent=2)+'\n')
if any(('-O' in e['argv']) != bool(sys.flags.optimize) for e in events): raise RuntimeError('child optimization mismatch')
sys.exit(not result.wasSuccessful())
