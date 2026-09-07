"""New explicit validation-order and all-status report consistency checks."""
import sys,json
from pathlib import Path
from unittest.mock import patch
R=Path(sys.argv[1]); O=Path(sys.argv[2]);sys.path.insert(0,str(R/'src'))
from writ_decision_lab import solve_bytes,check_bytes
from writ_decision_lab.checker import not_checked_report,report_bytes
from writ_decision_lab.identity import output_bytes
m=(R/'examples/weak/model.json').read_bytes();q=(R/'examples/weak/query.json').read_bytes();r=solve_bytes(m,q)
u=json.loads(q);u['semantics']='unsupported'
bad=json.loads(r);bad['answer']['evsi']='1/4'
unsupported_result=json.loads(r);unsupported_result['semantics']='unsupported'
wrong_shape=json.loads(r);wrong_shape['answer']['extra']='CANARY'
cases=[('input_before_result',b'{}',q,b'!','invalid_input','E_REQUIRED_FIELD'),('input_scope_before_result',m,output_bytes(u),b'!','out_of_scope','E_SEMANTICS'),('result_syntax_before_binding',m,q+b' ',b'!','invalid_input','E_JSON'),('result_version_before_binding',m,q+b' ',output_bytes(unsupported_result),'out_of_scope','E_SEMANTICS'),('shape_before_binding',m,q+b' ',output_bytes(wrong_shape),'invalid_input','E_UNKNOWN_FIELD'),('binding_before_math',m,q+b' ',output_bytes(bad),'input_mismatch','E_QUERY_BINDING'),('math_after_binding',m,q,output_bytes(bad),'computation_mismatch','E_COMPUTATION_MISMATCH'),('valid',m,q,r,'checked',None)]
observed=[];reports=[]
for name,mm,qq,rr,status,code in cases:
 report=check_bytes(mm,qq,rr);actual=report.diagnostics[0].code if report.diagnostics else None
 if (report.status,actual)!=(status,code):raise RuntimeError(name)
 observed.append({'case':name,'status':report.status,'primary':actual,'policy_count':report.policy_count});reports.append(report)
reports.append(not_checked_report(None,q,r,['model']))
with patch('writ_decision_lab.checker._expected_answer',side_effect=RuntimeError('CURRENT_PRIVATE_INTERNAL')):reports.append(check_bytes(m,q,r))
statuses=[]
for report in reports:
 record=json.loads(report_bytes(report))
 if record['status']!=report.status or record['policy_count']!=report.policy_count or record['diagnostics']!=[d.as_dict() for d in report.diagnostics]:raise RuntimeError('report inconsistency')
 if b'CURRENT_PRIVATE_INTERNAL' in report_bytes(report):raise RuntimeError('diagnostic leak')
 statuses.append(report.status)
if set(statuses)!={'checked','invalid_input','out_of_scope','input_mismatch','computation_mismatch','not_checked','checker_error'}:raise RuntimeError('status coverage')
mode='optimized' if sys.flags.optimize else 'normal'
(O/('precedence-'+mode+'.json')).write_bytes(output_bytes({'runtime':sys.version,'optimize':sys.flags.optimize,'cases':observed,'consistent_report_statuses':sorted(set(statuses))}))
print('PASS: 8 validation-order cases; all 7 report statuses consistent; optimize='+str(sys.flags.optimize))
