from __future__ import annotations

from .next_quest_pipeline import RollingQuestPipelineRuntime, RESEED_HOLD, _canon_task, _task_key, _valid_baton


def install_next_pipeline_successor_authority_hardening() -> None:
    if getattr(RollingQuestPipelineRuntime, "_athena_successor_authority_hardening_v1", False):
        return

    @classmethod
    def choose_reseed(cls, baton, state, reseed_candidate_id, allow_revisit):
        if not _valid_baton(baton):
            raise ValueError("invalid successor baton")
        active = cls._active_keys(state)
        completed = cls._completed_keys(state)
        seen = active | (set() if allow_revisit else completed)

        def usable(row):
            task = _canon_task(row)
            return bool(task and _task_key(task) not in seen)

        status = str(baton.get("status") or "")
        if status == "SELECTED":
            selected = dict(baton.get("selected") or {})
            if not selected:
                raise ValueError("SELECTED successor baton is missing selected candidate")
            if reseed_candidate_id and reseed_candidate_id != selected.get("candidate_id"):
                raise ValueError("SELECTED successor baton cannot be overridden by another candidate_id")
            if usable(selected):
                return selected, None
            return None, {
                "status": "SELECTED_SUCCESSOR_INADMISSIBLE",
                "candidate_ids": [selected.get("candidate_id")],
                "candidates": [selected],
                "baton_digest": baton.get("baton_digest"),
                "law": "PIPELINE_MAY_FILTER_SELECTED_SUCCESSOR_BUT_MAY_NOT_SUBSTITUTE_A_LOWER_RANKED_CANDIDATE",
            }

        if status == "AMBIGUOUS":
            ties = [dict(row) for row in baton.get("ties") or []]
            if reseed_candidate_id:
                matched = [row for row in ties if row.get("candidate_id") == reseed_candidate_id]
                if len(matched) != 1:
                    raise ValueError("reseed_candidate_id is not one of the preserved ties")
                if not usable(matched[0]):
                    raise ValueError("selected reseed candidate duplicates active/completed work")
                return matched[0], None
            usable_rows = [row for row in ties if usable(row)]
            if len(usable_rows) == 1:
                return usable_rows[0], None
            return None, {
                "status": "AMBIGUOUS",
                "candidate_ids": [row.get("candidate_id") for row in usable_rows],
                "candidates": usable_rows,
                "baton_digest": baton.get("baton_digest"),
                "law": "AMBIGUITY != HIDDEN_TIE_BREAK",
            }

        if status in {"NO_SUCCESSOR", "TERMINAL"}:
            return None, {
                "status": status,
                "candidate_ids": [],
                "candidates": [],
                "baton_digest": baton.get("baton_digest"),
                "law": "NO_CANONICAL_SUCCESSOR => NO_SYNTHETIC_Q4",
            }
        raise ValueError("successor baton has unsupported status")

    original_rotate = RollingQuestPipelineRuntime.rotate

    def rotate_with_resolved_horizon(self, *args, **kwargs):
        pipeline_id = kwargs.get("pipeline_id")
        if pipeline_id is None and args:
            raise ValueError("pipeline_id must be supplied by keyword for hardened rotate")
        state, _ = self._read_state(pipeline_id)
        if state.get("status") == RESEED_HOLD or state.get("reseed_hold"):
            raise ValueError("resolve current pipeline reseed hold before another focus rotation")
        return original_rotate(self, *args, **kwargs)

    RollingQuestPipelineRuntime._choose_reseed = choose_reseed
    RollingQuestPipelineRuntime.rotate = rotate_with_resolved_horizon
    RollingQuestPipelineRuntime._athena_successor_authority_hardening_v1 = True


__all__ = ["install_next_pipeline_successor_authority_hardening"]
