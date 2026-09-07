"""New repair-session probe; not either unavailable reviewer script."""
import json
import sys
from unittest.mock import patch
from pathlib import Path
from writ_decision_lab import check_and_load, check_bytes, solve_bytes
from writ_decision_lab.checker import report_bytes
from writ_decision_lab.decode import decode_json
from writ_decision_lab.identity import code_digest, source_manifest

root = Path(__file__).resolve().parents[2]
m = (root / 'examples/weak/model.json').read_bytes()
q = (root / 'examples/weak/query.json').read_bytes()
r = solve_bytes(m, q)
c = check_and_load(m, q, r)
before = c.summary()
c.answer['evsi'] = '999/1'
c.answer['current_argmin'].append('never_checked')
report = check_bytes(m,q,r)
report.record['status'] = 'computation_mismatch'
canary = json.loads(q)
canary['REPAIR_SYNTHETIC_CANARY'] = {'nested': '\ud800'}
depths = {}
for n in (32,33,995,1100,2000):
    data = b'['*n+b'0'+b']'*n
    try:
        decode_json(data, kind='model')
        status = 'decoded'
    except Exception as e:
        status = getattr(e,'status',type(e).__name__)
    depths[str(n)] = {'decoder':status,'checker':check_bytes(data,q,r).status}
try:
    with patch('writ_decision_lab.consumer.decode_result', side_effect=RuntimeError('synthetic')):
        check_and_load(m,q,r)
except Exception as e:
    post_decode = getattr(e,'status',type(e).__name__)
print(json.dumps({'runtime':sys.version,'optimized':sys.flags.optimize,'source':code_digest(),
 'manifest':source_manifest(),'summary_before':before,'summary_after':c.summary(),
 'record_status':json.loads(report_bytes(report))['status'],'typed_status':report.status,
 'unicode_diagnostic':json.loads(report_bytes(check_bytes(m,json.dumps(canary).encode(),r))),
 'depths':depths,'post_decode_failure':post_decode}, indent=2))
