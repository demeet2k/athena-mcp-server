from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time


def _witness_cell(science,a):
    science._REGRESSION_REF=science.ecology._REGRESSION_REF
    ref=str(a['regression_ref']);m=science._REGRESSION_REF.fullmatch(ref)
    if not m or '..' in m.group(1).split('/'):
        return {'status':'INVALID_REF','regression_ref':ref,'hermetic':False,'executed':False}
    rel,cls,method=m.groups();root=science.ecology._repo_root();target=(root/rel).resolve()
    if root not in target.parents or not target.is_file():
        return {'status':'INVALID_REF','regression_ref':ref,'hermetic':False,'executed':False}
    module=rel[:-3].replace('/','.')
    bootstrap=f'''import sys, unittest, socket\nsys.path.insert(0, {str(root)!r})\nclass _DeniedSocket:\n    def __init__(self,*a,**k):\n        raise RuntimeError("network disabled in witness cell")\nsocket.socket=_DeniedSocket\ns=unittest.defaultTestLoader.loadTestsFromName({(module+'.'+cls+'.'+method)!r})\nr=unittest.TextTestRunner(verbosity=1).run(s)\nraise SystemExit(0 if r.wasSuccessful() else 1)\n'''
    timeout=max(1.0,min(60.0,float(a.get('timeout_s',20.0))));memory_mb=max(64,min(16384,int(a.get('memory_mb',512))));cpu_s=max(1,min(60,int(a.get('cpu_s',10))))
    env={'PYTHONHASHSEED':'0','PATH':os.environ.get('PATH',''),'HOME':tempfile.mkdtemp(prefix='athena-witness-')}
    isolation=['python_-I','shell_false','sanitized_env','network_socket_monkeypatch','timeout'];preexec=None
    if os.name=='posix':
        try:
            import resource
            def _limit():
                resource.setrlimit(resource.RLIMIT_CPU,(cpu_s,cpu_s+1));mem=memory_mb*1024*1024
                resource.setrlimit(resource.RLIMIT_AS,(mem,mem));resource.setrlimit(resource.RLIMIT_FSIZE,(8*1024*1024,8*1024*1024));resource.setrlimit(resource.RLIMIT_NOFILE,(64,64))
            preexec=_limit;isolation += ['rlimit_cpu','rlimit_as','rlimit_fsize','rlimit_nofile']
        except Exception: pass
    started=time.time()
    try:
        p=subprocess.run([sys.executable,'-I','-c',bootstrap],cwd=str(root),env=env,text=True,capture_output=True,timeout=timeout,shell=False,preexec_fn=preexec)
        status='PASS' if p.returncode==0 else 'FAIL';rc=p.returncode;out=p.stdout[-4000:];err=p.stderr[-4000:]
    except subprocess.TimeoutExpired as e:
        status='TIMEOUT';rc=None;out=(e.stdout or '')[-4000:] if isinstance(e.stdout,str) else '';err=(e.stderr or '')[-4000:] if isinstance(e.stderr,str) else ''
    except Exception as e:
        status='ERROR';rc=None;out='';err=str(e)
    return {'status':status,'regression_ref':ref,'returncode':rc,'duration_s':round(time.time()-started,6),'stdout_tail':out,'stderr_tail':err,'isolation':isolation,'hermetic':False,'executed':True,'law':'constrained process cell is stronger than the V4 runner but is not claimed OS-hermetic'}


def call(science, core, name, a):
    if name=='athena_bayes_predict': return science.bayes_predict(a['features'],a['regime'],a['arm_id'],a.get('scope','global'),a.get('target_coverage',.90),a.get('ridge',1.0))
    if name=='athena_bayes_observe': return science.bayes_observe(a['features'],a['reward'],a['regime'],a['arm_id'],a.get('scope','global'),a.get('actor','agent'),a.get('weight',1.0),a.get('target_coverage',.90),a.get('ridge',1.0))
    if name=='athena_uncertainty_calibrate': return science.uncertainty_calibration(a.get('scope','global'),a.get('regime'),a.get('arm_id'),a.get('target_coverage',.90))
    if name=='athena_experiment_design': return science.experiment_design(a['hypotheses'],a['experiments'],a.get('sample_size',20),a.get('control_fraction',.5),a.get('cost_weight',.10),a.get('risk_weight',.20))
    if name=='athena_interaction_credit': return science.interaction_credit(a['analysis_key'],a['experiments'],a.get('actor','agent'))
    if name=='athena_delayed_credit_record': return science.delayed_credit_record(a['action_id'],a['outcome_key'],a['outcome_delta'],a['delay_cycles'],a['causal_confidence'],a.get('discount',.95),a.get('regime','GLOBAL'),a.get('actor','agent'))
    if name=='athena_delayed_credit_summary': return science.delayed_credit_summary(a.get('action_id'),a.get('regime'),a.get('limit',1000))
    if name=='athena_transition_observe': return science.transition_observe(a['action_id'],a['before'],a['after'],a.get('evidence_weight',1.0),a.get('actor','agent'))
    if name=='athena_transition_predict': return science.transition_predict(a['action_id'],a['context'],a.get('prior_strength',5.0))
    if name=='athena_rollout_learned': return science.rollout_learned(a['initial_context'],a['trajectories'],a.get('discount',.95),a.get('uncertainty_alpha',1.0),a.get('prior_strength',5.0))
    if name=='athena_schedule_multiperiod': return science.schedule_multiperiod(a['tasks'],a['workers'],a.get('horizon',12),a.get('budget'),a.get('beam_width',128),a.get('scope','global'),a.get('discount',.97))
    if name=='athena_witness_cell': return _witness_cell(science,a)
    if name=='athena_regime_geometry_observe': return science.regime_geometry_observe(a['signals'],a['reward'],a.get('cluster_id'),a.get('domain'),a.get('weight',1.0))
    if name=='athena_regime_geometry_resolve': return science.regime_geometry_resolve(a['signals'],a.get('top_k',5),a.get('domain'))
    if name=='athena_pareto_frontier': return science.pareto_frontier(a['candidates'],a.get('directions'),a.get('epsilon',0.0),a.get('robust',False))
    if name=='athena_projection_compensate': return science.projection_compensate(core,a['projection_id'],a.get('expected_semantic_eid'),a.get('actor','agent'))
    raise KeyError(name)
