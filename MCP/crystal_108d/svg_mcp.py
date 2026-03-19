# CRYSTAL: Xi108:W3:A7:S25 | face=R | node=704 | depth=0 | phase=Cardinal
# METRO: Sa
# BRIDGES: primitives→scorer→challenges→self_play→mcp
"""
SVG MCP Tools — Agent-Facing SVG Generation Interface
======================================================
17 MCP tools for SVG self-play + transcendence + nervous system + 108D:

  1. svg_challenge(category, difficulty)  — list/generate challenges
  2. svg_generate(challenge_id, primitive, params)  — generate SVG
  3. svg_score(svg_str, challenge_id)     — score SVG quality
  4. svg_self_play(rounds, category, progressive)  — run self-play session
  5. svg_history(last_n)                  — view improvement trajectory
  6. svg_best(challenge_id)               — retrieve best SVG
  7. svg_evolve(generations, population)  — run evolutionary tournament
  8. svg_transcend(cycles, generations)   — META LOOP^N aggressive evolution
  9. svg_seeds()                          — view crystallized seed library
 10. svg_nervous_system()                 — full nervous system dashboard
 11. svg_shard_cloud(max_shards)          — 4D shard cloud projection
 12. svg_brain_topology()                 — 8-node brain topology
 13. svg_108d_crystal()                   — full 108D crystal projection
 14. svg_108d_panel(panel)                — individual 108D panel
 15. svg_108d_inversion()                 — 108D inversion cascade (3D→108D)
 16. svg_108d_inversion_panel(panel)      — individual inversion panel
"""

from typing import Optional


def register_svg_tools(mcp) -> None:
    """Register all SVG self-play tools onto the MCP server."""

    @mcp.tool()
    def svg_challenge(category: str = "", difficulty: float = -1) -> str:
        """List or filter SVG challenges from the built-in catalog.

        Args:
            category: Filter by category (primitive|composite|sacred|fractal|crystal).
                      Empty string returns all.
            difficulty: Filter by max difficulty (0.0-1.0). -1 returns all.

        Returns catalog of challenges with IDs, names, difficulty, and descriptions.
        """
        from .svg_challenges import catalog as get_catalog

        challenges = get_catalog()
        if category:
            challenges = [c for c in challenges if c.category == category]
        if difficulty >= 0:
            challenges = [c for c in challenges if c.difficulty <= difficulty]

        lines = [f"# SVG Challenges ({len(challenges)} found)", ""]
        for c in challenges:
            lines.append(
                f"- **{c.challenge_id}** [{c.category}] "
                f"d={c.difficulty:.2f} — {c.name}: {c.description}"
            )
        return "\n".join(lines)

    @mcp.tool()
    def svg_generate(challenge_id: str = "", primitive: str = "",
                     params: str = "{}") -> str:
        """Generate SVG for a challenge or from a named primitive.

        Args:
            challenge_id: Challenge to generate reference SVG for.
            primitive: Direct primitive name (circle, rect, golden_spiral, etc.).
            params: JSON string of parameters for the primitive.

        Returns the generated SVG string.
        """
        import json as _json
        if challenge_id:
            from .svg_challenges import get_challenge
            ch = get_challenge(challenge_id)
            if ch is None:
                return f"Challenge '{challenge_id}' not found."
            from .svg_self_play import _generate_reference
            return _generate_reference(ch)

        if primitive:
            from .svg_self_play import _REFERENCE_FNS
            from .svg_primitives import SVGCanvas
            fn = _REFERENCE_FNS.get(primitive)
            if fn is None:
                available = ", ".join(sorted(_REFERENCE_FNS.keys()))
                return f"Unknown primitive '{primitive}'. Available: {available}"
            try:
                p = _json.loads(params)
            except _json.JSONDecodeError:
                return f"Invalid JSON params: {params}"
            canvas = SVGCanvas()
            canvas.add(fn(**p))
            return canvas.render()

        return "Provide either challenge_id or primitive name."

    @mcp.tool()
    def svg_score(svg_str: str, target_elements: int = 0,
                  target_symmetry: int = 0) -> str:
        """Score an SVG string for quality across multiple dimensions.

        Args:
            svg_str: The SVG content to score.
            target_elements: Expected number of elements (0 = auto).
            target_symmetry: Expected symmetry order (0 = auto).

        Returns multi-dimensional quality scores and 15D observation vector.
        """
        from .svg_scorer import get_scorer

        scorer = get_scorer()
        score = scorer.score(svg_str,
                             target_elements=target_elements,
                             target_symmetry=target_symmetry)
        v15 = score.to_15d()

        lines = [
            "# SVG Quality Score",
            "",
            f"**Total Score: {score.total_score:.3f}**",
            "",
            "## Dimensions",
            f"- Element Count Accuracy: {score.element_count_accuracy:.3f}",
            f"- Bounding Box Accuracy:  {score.bounding_box_accuracy:.3f}",
            f"- Centroid Accuracy:      {score.centroid_accuracy:.3f}",
            f"- Symmetry Score:         {score.symmetry_score:.3f}",
            f"- Golden Ratio Adherence: {score.golden_ratio_adherence:.3f}",
            f"- Balance Score:          {score.balance_score:.3f}",
            f"- Path Complexity:        {score.path_complexity:.3f}",
            f"- Element Diversity:      {score.element_diversity:.3f}",
            f"- Transform Depth:        {score.transform_depth:.3f}",
            f"- Compression Ratio:      {score.compression_ratio:.3f}",
            "",
            f"## Efficiency",
            f"- SVG Byte Size: {score.svg_byte_size}",
            "",
            f"## 15D Observation Vector",
            f"```",
            f"{[round(x, 4) for x in v15]}",
            f"```",
        ]
        return "\n".join(lines)

    @mcp.tool()
    def svg_self_play(rounds: int = 5, category: str = "",
                      progressive: bool = True) -> str:
        """Run an SVG self-play improvement session.

        Args:
            rounds: Number of challenge rounds to run (default 5).
            category: Filter challenges by category (empty = all).
            progressive: If true, challenges increase in difficulty.

        Returns improvement trajectory and scores for each round.
        """
        from .svg_self_play import get_engine

        engine = get_engine()
        results = engine.run_session(
            rounds=rounds,
            progressive=progressive,
            category=category or None,
        )

        lines = [f"# SVG Self-Play Session ({len(results)} rounds)", ""]
        total_improvement = 0.0
        for rnd in results:
            traj = rnd.improvement_trajectory
            improvement = traj[-1] - traj[0] if len(traj) > 1 else 0.0
            total_improvement += improvement
            ch_name = rnd.challenge.name if rnd.challenge else "?"
            lines.append(
                f"## Round {rnd.round_id}: {ch_name} "
                f"[{rnd.challenge.category if rnd.challenge else '?'}]"
            )
            lines.append(f"- Best Score: **{rnd.best_score:.3f}**")
            lines.append(f"- Attempts: {len(rnd.attempts)}")
            lines.append(f"- Trajectory: {[round(s, 3) for s in traj]}")
            lines.append(f"- Improvement: {improvement:+.3f}")
            lines.append("")

        lines.append("## Summary")
        best_overall = max(r.best_score for r in results) if results else 0
        avg_score = sum(r.best_score for r in results) / max(1, len(results))
        lines.append(f"- Best Overall: {best_overall:.3f}")
        lines.append(f"- Average Score: {avg_score:.3f}")
        lines.append(f"- Total Improvement: {total_improvement:+.3f}")
        lines.append(f"- Outputs saved to: MCP/data/svg_arena/outputs/")

        return "\n".join(lines)

    @mcp.tool()
    def svg_history(last_n: int = 10) -> str:
        """View recent SVG self-play history and improvement trajectory.

        Args:
            last_n: Number of recent rounds to show (default 10).
        """
        from .svg_self_play import get_engine

        engine = get_engine()
        history = engine.get_history(last_n)

        rounds = history.get("rounds", [])
        meta = history.get("meta", {})
        lines = [
            f"# SVG Self-Play History",
            f"Total rounds: {meta.get('total_rounds', 0)}",
            f"Best overall: {meta.get('best_overall', 0):.3f}",
            "",
        ]
        for r in rounds:
            lines.append(
                f"- Round {r['round_id']}: **{r.get('challenge_name', r['challenge_id'])}** "
                f"→ {r['best_score']:.3f} ({r['attempts']} attempts)"
            )
        if not rounds:
            lines.append("No rounds recorded yet. Run svg_self_play first.")
        return "\n".join(lines)

    @mcp.tool()
    def svg_best(challenge_id: str) -> str:
        """Retrieve the best SVG generated for a specific challenge.

        Args:
            challenge_id: The challenge ID to look up.

        Returns the SVG string of the best attempt, or a message if not found.
        """
        from .svg_self_play import get_engine

        engine = get_engine()
        svg = engine.get_best(challenge_id)
        if svg:
            return svg
        return f"No best SVG found for challenge '{challenge_id}'. Run svg_self_play first."

    # ------------------------------------------------------------------
    # Transcendence tools — evolutionary composition discovery
    # ------------------------------------------------------------------

    @mcp.tool()
    def svg_evolve(generations: int = 20, population: int = 20,
                   cross_category: bool = True) -> str:
        """Run evolutionary tournament to discover emergent SVG compositions.

        Uses tournament selection, breeding, mutation, and cross-category
        fusion to discover compositions that score higher than any
        individual primitive.

        Args:
            generations: Number of evolutionary generations (default 20).
            population: Population size per generation (default 20).
            cross_category: Allow cross-category breeding (default true).

        Returns evolution trajectory, emergences detected, and best genome.
        """
        from .svg_transcendence import (
            get_transcendence_engine, format_evolution_result,
        )

        engine = get_transcendence_engine(population=population)
        result = engine.evolve(
            generations=generations,
            cross_category=cross_category,
        )
        return format_evolution_result(result)

    @mcp.tool()
    def svg_transcend(cycles: int = 3, generations_per_cycle: int = 20,
                      population: int = 20) -> str:
        """Run META LOOP^N aggressive evolution — multi-cycle transcendence.

        Each cycle loads seeds from previous cycles, runs full evolution,
        crystallizes winners, and feeds seeds forward. Population increases
        each cycle for accelerating returns.

        Args:
            cycles: Number of META LOOP cycles (default 3).
            generations_per_cycle: Generations per cycle (default 20).
            population: Starting population size (default 20).

        Returns multi-cycle results with score trajectories and emergences.
        """
        from .svg_transcendence import (
            get_transcendence_engine, format_session_results,
        )

        engine = get_transcendence_engine(population=population)
        results = engine.aggressive_session(
            cycles=cycles,
            generations_per_cycle=generations_per_cycle,
            population=population,
        )
        return format_session_results(results)

    @mcp.tool()
    def svg_seeds() -> str:
        """View the crystallized seed library from evolutionary runs.

        Seeds are compressed genome recipes that can be loaded and
        re-evolved in future sessions. Each seed records its score,
        emergence synergy, lineage depth, and layer composition.

        Returns list of all crystallized seeds with metadata.
        """
        from .svg_transcendence import get_transcendence_engine

        engine = get_transcendence_engine()
        seeds = engine.load_seeds()

        if not seeds:
            return ("# SVG Seed Library\n\n"
                    "No seeds crystallized yet. Run svg_evolve or "
                    "svg_transcend first.")

        lines = [
            f"# SVG Seed Library ({len(seeds)} seeds)",
            "",
        ]
        seeds.sort(key=lambda g: g.score, reverse=True)
        for g in seeds:
            prims = [l.primitive for l in g.layers]
            lines.append(
                f"- **{g.genome_id}** score={g.score:.4f} "
                f"emergence={g.emergence_score:.4f} "
                f"gen={g.generation} depth={g.lineage_depth} "
                f"layers=[{', '.join(prims)}]"
            )
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Nervous System Visualization — Real Data
    # ------------------------------------------------------------------

    @mcp.tool()
    def svg_nervous_system() -> str:
        """Generate full nervous system dashboard SVG from live data.

        Renders 4 panels: brain topology (8 nodes), momentum field (148
        params), 4D shard cloud (14,750 shards), and dimensional sector
        distribution with QShrink 1/8 lift cascade.

        Returns the SVG and saves to MCP/data/svg_arena/outputs/.
        """
        from .svg_nervous_system import save_nervous_system_dashboard
        path = save_nervous_system_dashboard()
        return f"Dashboard saved to: {path}"

    @mcp.tool()
    def svg_shard_cloud(max_shards: int = 2000) -> str:
        """Render the 4D shard cloud — actual corpus seed vectors projected to 2D.

        Each of 14,750 shards has a [S,F,C,R] seed vector. Projects via
        x = S-R (earth-air axis), y = F-C (fire-water axis). Color by
        dominant element.

        Args:
            max_shards: Maximum shards to render (default 2000).

        Returns SVG string of the shard cloud.
        """
        from .svg_primitives import SVGCanvas
        from .svg_nervous_system import render_shard_cloud_4d
        canvas = SVGCanvas(800, 800)
        canvas.add(render_shard_cloud_4d(400, 400, 300, max_shards=max_shards))
        return canvas.render()

    @mcp.tool()
    def svg_brain_topology() -> str:
        """Render the 8-node distributed brain topology with SFCR bridges.

        Shows: athena-mcp-server (center), 4 SFCR lobes, 3 support nodes.
        Bridge weights: golden (SF/FC/CR = phi^-1), neutral (SC/FR = 0.5),
        distant (SR = phi^-2).

        Returns SVG string.
        """
        from .svg_primitives import SVGCanvas
        from .svg_nervous_system import render_brain_topology
        canvas = SVGCanvas(800, 800)
        canvas.add(render_brain_topology(400, 400, 300))
        return canvas.render()

    # ------------------------------------------------------------------
    # 108D Crystal Projection — Full Organism
    # ------------------------------------------------------------------

    @mcp.tool()
    def svg_108d_crystal() -> str:
        """Generate full 108D crystal projection dashboard.

        9-panel layout showing: shell cascade (36 shells golden spiral),
        wreath trefoil (3 interlocked rings), archetype wheel (12 zodiacal),
        Sigma-60 icosahedral field, E8-240 root star, shard density heatmap,
        momentum shells, 12D observation radar, and Flower of Life overlay.

        36 shells x 3 wreaths = 108D. x4 faces = 432 gates.
        x60 sigma = 25,920. x4 E8 = 103,680 roots.

        Saves to MCP/data/svg_arena/outputs/ and returns confirmation.
        """
        from .svg_108d_projection import save_108d_crystal
        path = save_108d_crystal()
        return f"108D crystal projection saved to: {path}"

    @mcp.tool()
    def svg_108d_panel(panel: str = "shell_cascade") -> str:
        """Render a single panel from the 108D crystal projection.

        Available panels:
          shell_cascade   — 36 shells on golden spiral
          wreath_trefoil  — 3 interlocked wreath rings
          archetype_wheel — 12 archetypes with SFCR faces
          sigma60         — 60 icosahedral viewpoints
          e8_240          — 240 E8 roots projected to 2D
          shard_density   — shards per shell heatmap
          momentum_shells — training gradients per shell
          observation_12d — 12D observation radar chart
          flower_overlay  — Flower of Life PHI-decay rings

        Args:
            panel: Panel name (default: shell_cascade).

        Returns SVG string for the requested panel.
        """
        from .svg_primitives import SVGCanvas
        from .svg_108d_projection import (
            render_shell_cascade, render_wreath_trefoil,
            render_archetype_wheel, render_sigma60_field,
            render_e8_240, render_shard_density,
            render_momentum_shells, render_12d_observation,
            render_flower_overlay,
        )

        dispatch = {
            "shell_cascade": render_shell_cascade,
            "wreath_trefoil": render_wreath_trefoil,
            "archetype_wheel": render_archetype_wheel,
            "sigma60": render_sigma60_field,
            "e8_240": render_e8_240,
            "shard_density": render_shard_density,
            "momentum_shells": render_momentum_shells,
            "observation_12d": render_12d_observation,
            "flower_overlay": render_flower_overlay,
        }

        fn = dispatch.get(panel)
        if fn is None:
            available = ", ".join(sorted(dispatch.keys()))
            return f"Unknown panel '{panel}'. Available: {available}"

        canvas = SVGCanvas(800, 800)
        canvas.add(fn(400, 400, 300))
        return canvas.render()

    # ------------------------------------------------------------------
    # 108D Inversion Cascade — The Generative Principle
    # ------------------------------------------------------------------

    @mcp.tool()
    def svg_108d_inversion() -> str:
        """Generate the full 108D inversion cascade SVG.

        Shows how each dimension is born from the previous one fused with
        its own mirror: D_{n+1} = D_n ∪ D_n⁻¹.

        8-panel layout:
          3D∪3D⁻¹ hexagram, 4D→6D Möbius twist, 6D→8D Wu Xing fusion,
          8D→10D planetary opposition, 10D→12D matrix transpose,
          12D→36D→108D triple crown, w-operator spiral, containment counting.

        Saves to MCP/data/svg_arena/outputs/ and returns confirmation.
        """
        from .svg_108d_projection import save_inversion_cascade
        path = save_inversion_cascade()
        return f"108D inversion cascade saved to: {path}"

    @mcp.tool()
    def svg_inverse_double_fold() -> str:
        """Generate the inverse double fold SVG: 3D^(3D⁻¹) ∧ (3D⁻¹)^3D.

        The form raised to its own inverse — flipped AND reversed.
        Shows: (1) 9-point W9 seed interaction matrix where each wreath
        meets each anti-wreath, (2) double fold cascade showing D² at
        every level (3²=9, 6²=36, 36×3=108).

        The diagonal = self-annihilation (Su·-Su → Z*).
        The off-diagonal = cross-creation.
        M · Mᵀ = symmetric fixed point = holographic encoding.

        Saves to MCP/data/svg_arena/outputs/ and returns confirmation.
        """
        from .svg_108d_projection import save_inverse_double_fold
        path = save_inverse_double_fold()
        return f"Inverse double fold saved to: {path}"

    @mcp.tool()
    def svg_108d_inversion_panel(panel: str = "3d_pair") -> str:
        """Render a single panel from the inversion cascade.

        Available panels:
          3d_pair          — 3D seed + 3D⁻¹ anti-seed = hexagram
          inverse_double_fold — 3D^(3D⁻¹) ∧ (3D⁻¹)^3D = W9 seed
          double_fold_cascade — D² self-squaring at every level
          mobius_inversion — 4D→6D Möbius half-twist chirality
          wuxing_inversion — 6D→8D Wu Xing generative+destructive
          planetary_inv    — 8D→10D exaltation/detriment opposition
          matrix_inversion — 10D→12D 3×3 matrix + transpose
          triple_crown     — 12D→36D→108D crown expansion
          w_cascade        — w-operator emergence spiral
          containment      — containment counting (bodies inside bodies)

        Args:
            panel: Panel name (default: 3d_pair).

        Returns SVG string for the requested panel.
        """
        from .svg_primitives import SVGCanvas
        from .svg_108d_projection import (
            _render_3d_pair, _render_inverse_double_fold,
            _render_double_fold_cascade,
            _render_mobius_inversion,
            _render_wuxing_inversion, _render_planetary_inversion,
            _render_matrix_inversion, _render_triple_crown_expansion,
            _render_w_cascade, _render_containment_count,
        )

        dispatch = {
            "3d_pair": _render_3d_pair,
            "inverse_double_fold": _render_inverse_double_fold,
            "double_fold_cascade": _render_double_fold_cascade,
            "mobius_inversion": _render_mobius_inversion,
            "wuxing_inversion": _render_wuxing_inversion,
            "planetary_inv": _render_planetary_inversion,
            "matrix_inversion": _render_matrix_inversion,
            "triple_crown": _render_triple_crown_expansion,
            "w_cascade": _render_w_cascade,
            "containment": _render_containment_count,
        }

        fn = dispatch.get(panel)
        if fn is None:
            available = ", ".join(sorted(dispatch.keys()))
            return f"Unknown panel '{panel}'. Available: {available}"

        canvas = SVGCanvas(800, 800)
        canvas.add(fn(400, 400, 300))
        return canvas.render()
