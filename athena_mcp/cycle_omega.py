from __future__ import annotations

from .cycle import CycleRuntime


class OmegaCycleRuntime(CycleRuntime):
    """CYCLE.1 with one canonical whole-state representation.

    Only RECONSTRUCT is overridden. Every other CYCLE.1 transition remains the
    tested fail-closed state machine. The reconstruction phase now persists a
    RECONRUN whose Omega packet is the exact state artifact consumed downstream.
    """

    def _step(self, cycle_id, row):
        if row['phase'] != 'RECONSTRUCT':
            return super()._step(cycle_id, row)

        state = row['state']
        actor = row['actor']
        artifacts = state['artifacts']
        state['wait'] = None
        foundation = self.dev.integrity.state_foundation
        cfg = self._cfg(state, 'reconstruction', {}) or {}
        source_refs = list(cfg.get('source_refs') or ['runtime://local'])
        expected_refs = cfg.get('expected_refs')
        recon = foundation.reconstruction.compile(
            state['task_ref'], source_refs, expected_refs, actor, True
        )
        artifacts['reconstruction_run'] = recon
        artifacts['reconstruct'] = recon['omega']
        payload = {
            'run_id': recon['run_id'],
            'omega_id': recon['omega']['omega_id'],
            'state_digest': recon['omega']['state_digest'],
            'reconstruction_digest': recon['reconstruction_digest'],
            'status': recon['status'],
            'defects': recon['defects'],
            'boundary': recon['boundary'],
        }
        return self._event(
            cycle_id, state, 'RECONSTRUCT', 'RECONRUN', payload, actor,
            next_phase='MEMORY'
        )
