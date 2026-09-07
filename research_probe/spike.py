"""Isolated engineering probe, not Build 1 and not a KL experiment.
Python 3.13 standard library only. Fixed fixtures; no grid search.
"""
from __future__ import annotations
import copy
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import re
import sys


def rat(s: str) -> F:
    if not isinstance(s, str) or not re.fullmatch(r'(?:0|-?[1-9][0-9]*)/[1-9][0-9]*', s):
        raise ValueError('E_RATIONAL')
    a, b = s.split('/')
    if len(a.lstrip('-')) > 128 or len(b) > 128:
        raise ValueError('E_RATIONAL_LIMIT')
    f = F(int(a), int(b))
    if f'{f.numerator}/{f.denominator}' != s:
        raise ValueError('E_RATIONAL_CANONICAL')
    return f


def wire(value):
    if isinstance(value, F):
        return f'{value.numerator}/{value.denominator}'
    if isinstance(value, dict):
        return {k: wire(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [wire(v) for v in value]
    return value


def encoded(value) -> bytes:
    return (json.dumps(wire(value), sort_keys=True, separators=(',', ':'), ensure_ascii=True)+'\n').encode('ascii')


def digest(b: bytes) -> str:
    return 'sha256:' + sha256(b).hexdigest()


def inputs(model, query):
    p = list(map(rat, model['prior']))
    k = [list(map(rat, row)) for row in model['likelihood']]
    l = [list(map(rat, row)) for row in query['losses']]
    c = rat(query['cost'])
    ns, nx, na = len(p), len(model['outcomes']), len(query['actions'])
    assert len(model['states']) == ns and len(k) == ns and all(len(row) == nx for row in k)
    assert len(l) == na and all(len(row) == ns for row in l)
    assert all(v >= 0 for v in p) and sum(p) == 1
    assert all(all(v >= 0 for v in row) and sum(row) == 1 for row in k)
    assert c >= 0
    return p, k, l, c


def solve(model, query):
    p, k, l, c = inputs(model, query)
    ns, nx, na = len(p), len(k[0]), len(l)
    prior_risks = [sum(p[s]*l[a][s] for s in range(ns)) for a in range(na)]
    current = min(prior_risks)
    branches, observed = [], F(0)
    for x in range(nx):
        joint = [p[s]*k[s][x] for s in range(ns)]
        mass = sum(joint)
        if mass == 0:
            branches.append({'outcome': model['outcomes'][x], 'status': 'impossible', 'mass': F(0), 'posterior': None, 'risks': None, 'argmin': None})
            continue
        post = [j/mass for j in joint]
        risks = [sum(post[s]*l[a][s] for s in range(ns)) for a in range(na)]
        best = min(risks)
        observed += mass*best
        branches.append({'outcome': model['outcomes'][x], 'status': 'possible', 'mass': mass, 'posterior': post, 'risks': risks, 'argmin': [query['actions'][a] for a in range(na) if risks[a] == best]})
    alternatives = {'act_now': current, 'observe_once': observed+c}
    return {'prior_risks': prior_risks, 'current_argmin': [query['actions'][a] for a in range(na) if prior_risks[a] == current], 'current_risk': current, 'branches': branches, 'observed_risk': observed, 'evsi': current-observed, 'net_value': current-observed-c, 'acquisition_argmin': [a for a, risk in alternatives.items() if risk == min(alternatives.values())]}


def enumerate_policies(model, query):
    # Deliberately does not call solve or posterior/branch-risk helpers.
    # It shares the parser, rational library, specification and author.
    p, k, l, c = inputs(model, query)
    ns, nx, na = len(p), len(k[0]), len(l)
    values = []
    for policy in product(range(na), repeat=nx):
        values.append(sum(p[s]*k[s][x]*l[policy[x]][s] for s in range(ns) for x in range(nx)))
    current = min(sum(p[s]*l[a][s] for s in range(ns)) for a in range(na))
    return {'current_risk': current, 'observed_risk': min(values), 'evsi': current-min(values), 'policies': len(values)}


def binary(k0, k1, loss=((0, 1), (1, 0)), prior=F(1, 4), cost=0):
    k0, k1 = F(k0), F(k1)
    model = {'states': ['s0', 's1'], 'outcomes': ['x0', 'x1'], 'prior': [1-prior, prior], 'likelihood': [[1-k0, k0], [1-k1, k1]]}
    query = {'actions': ['a0', 'a1'], 'losses': [[F(v) for v in row] for row in loss], 'cost': F(cost)}
    return wire(model), wire(query)


def check_binding(model, query, result):
    return result['model_hash'] == digest(encoded(model)) and result['query_hash'] == digest(encoded(query))


def run():
    fixtures = {
        'weak': binary(0, F(1, 2)),
        'perfect': binary(0, 1),
        'base_unit': binary(0, 0),
        'base_asymmetric': binary(0, 0, ((0, 1), (2, 0))),
        'revised_unit': binary(0, 0, ((1, 1), (1, 0))),
        'revised_asymmetric': binary(0, 0, ((1, 1), (2, 0))),
        'tie': binary(F(1, 2), F(1, 2), prior=F(1, 2)),
        'zero_prior': binary(0, 1, prior=F(0)),
        'large_rational': binary(0, 0, prior=F(500000000000000000, 1000000000000000001)),
        'acquisition_tie': binary(0, F(1, 2), cost=F(1, 8)),
    }
    model = {'states': ['s0', 's1', 's2'], 'outcomes': ['x0', 'x1', 'x2'], 'prior': ['1/2', '1/3', '1/6'], 'likelihood': [['1/1', '0/1', '0/1'], ['0/1', '1/1', '0/1'], ['0/1', '0/1', '1/1']]}
    query = {'actions': ['a0', 'a1', 'a2'], 'losses': [['0/1', '2/1', '3/1'], ['1/1', '0/1', '2/1'], ['3/1', '1/1', '0/1']], 'cost': '0/1'}
    fixtures['three_state'] = (model, query)
    model, query = binary(0, 1)
    query['actions'], query['losses'] = ['a0'], [query['losses'][0]]
    fixtures['restricted_action'] = (model, query)
    results, policies = {}, 0
    for name, (model, query) in fixtures.items():
        result, reference = solve(model, query), enumerate_policies(model, query)
        for key in ('current_risk', 'observed_risk', 'evsi'):
            assert result[key] == reference[key], (name, key)
        policies += reference['policies']
        results[name] = result
    assert results['weak']['evsi'] == F(1, 8)
    assert results['perfect']['evsi'] == F(1, 4)
    def policy(r): return [r['current_argmin']] + [b['argmin'] for b in r['branches']]
    assert policy(results['weak']) == policy(results['perfect'])
    assert results['base_unit']['evsi'] == results['base_asymmetric']['evsi'] == 0
    assert policy(results['base_unit']) == policy(results['base_asymmetric'])
    assert results['revised_unit']['prior_risks'] == [F(1), F(3, 4)]
    assert results['revised_asymmetric']['prior_risks'] == [F(1), F(3, 2)]
    assert results['revised_unit']['current_argmin'] == ['a1']
    assert results['revised_asymmetric']['current_argmin'] == ['a0']
    assert results['base_unit']['branches'][1]['status'] == 'impossible'
    assert results['tie']['branches'][1]['argmin'] == ['a0', 'a1']
    assert results['three_state']['evsi'] == F(5, 6)
    assert results['restricted_action']['evsi'] == 0
    assert results['acquisition_tie']['acquisition_argmin'] == ['act_now', 'observe_once']
    near = results['large_rational']['prior_risks']
    assert near[0] < near[1] and float(near[0]) == float(near[1])
    rejected = 0
    for bad in [0.25, '0.25', '2/4', '1/0', '-0/1', '1/-2', '1e-3', ' 1/2 ', True]:
        try: rat(bad)
        except ValueError: rejected += 1
        else: raise AssertionError(('accepted malformed rational', bad))
    model, query = fixtures['weak']
    envelope = {'model_hash': digest(encoded(model)), 'query_hash': digest(encoded(query)), 'answer': wire(results['weak'])}
    assert check_binding(model, query, envelope)
    assert not check_binding(fixtures['perfect'][0], query, envelope)
    changed = copy.deepcopy(query); changed['cost'] = '1/8'
    assert not check_binding(model, changed, envelope)
    tampered = copy.deepcopy(envelope); tampered['answer']['evsi'] = '1/4'
    assert check_binding(model, query, tampered)  # Identity of inputs alone is insufficient.
    assert rat(tampered['answer']['evsi']) != enumerate_policies(model, query)['evsi']
    output = {'python': sys.version.split()[0], 'fixed_fixtures': len(fixtures), 'enumerated_policies': policies, 'rational_rejections': rejected, 'binding_mutations_rejected': 2, 'tampered_value_detected_by_recomputation': True, 'results': wire(results)}
    out = Path(__file__).parent
    (out/'spike_results.json').write_bytes(encoded(output))
    (out/'spike_fixtures.json').write_bytes(encoded(fixtures))
    print(json.dumps({k: v for k, v in output.items() if k != 'results'}, sort_keys=True))


if __name__ == '__main__':
    run()
