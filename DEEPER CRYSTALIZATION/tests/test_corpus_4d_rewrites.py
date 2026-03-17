import argparse
import hashlib
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock


DEEPER_ROOT = Path(__file__).resolve().parents[1]
if str(DEEPER_ROOT) not in sys.path:
    sys.path.insert(0, str(DEEPER_ROOT))

import build_corpus_4d_rewrites as driver
import audit_corpus_4d_rewrites as audit_driver
import build_corpus_4d_archive_members as archive_driver
import build_corpus_4d_registry as registry_driver
import build_awakening_agent_transition_notes as notes_driver
import classify_corpus_4d_orphans as orphan_driver
import export_corpus_4d_to_deeper_network as export_driver
import integrate_corpus_4d_next46 as integrate_driver
import query_corpus_4d_registry as query_driver
import tesseract_metro_v4 as metro


class Corpus4DRewriteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace_root = Path(self.temp_dir.name)
        (self.workspace_root / "self_actualize").mkdir(parents=True, exist_ok=True)
        (self.workspace_root / "DEEPER CRYSTALIZATION" / "_build").mkdir(parents=True, exist_ok=True)
        self._write_docs_gate()
        self._seed_deeper_network_root()
        self.record_specs = self._seed_workspace()
        self.atlas_path = self._write_atlas()
        self.main_manifest_path = self.workspace_root / "DEEPER CRYSTALIZATION" / "_build" / "corpus_4d_rewrites_manifest.json"
        self.audit_path = self.workspace_root / "DEEPER CRYSTALIZATION" / "_build" / "corpus_4d_rewrites_audit.json"
        self.archive_manifest_path = self.workspace_root / "DEEPER CRYSTALIZATION" / "_build" / "corpus_4d_archive_members_manifest.json"
        self.orphan_classification_path = self.workspace_root / "DEEPER CRYSTALIZATION" / "_build" / "corpus_4d_orphan_classification.json"
        self.registry_path = self.workspace_root / "DEEPER CRYSTALIZATION" / "_build" / "corpus_4d_registry.json"
        self.notes_path = self.workspace_root / "DEEPER CRYSTALIZATION" / "_build" / "awakening_agent_transition_notes.md"
        self.integration_receipt_path = self.workspace_root / "DEEPER CRYSTALIZATION" / "_build" / "corpus_4d_next46_integration_receipt.json"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _write_docs_gate(self) -> None:
        gate_path = self.workspace_root / "self_actualize" / "live_docs_gate_status.md"
        gate_path.write_text(
            "# Live Docs Gate Status\n\n- Command status: `BLOCKED`\n- Missing Files: `Trading Bot/credentials.json`\n",
            encoding="utf-8",
        )

    def _seed_deeper_network_root(self) -> None:
        self.network_root = (
            self.workspace_root
            / "self_actualize"
            / "mycelium_brain"
            / "dynamic_neural_network"
            / "14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK"
        )
        metro_dir = self.network_root / "07_METRO_STACK"
        appendix_dir = self.network_root / "08_APPENDIX_CRYSTAL"
        metro_dir.mkdir(parents=True, exist_ok=True)
        appendix_dir.mkdir(parents=True, exist_ok=True)
        (metro_dir / "03_level_4_transcendence_metro_map.md").write_text(
            "# Level 4 Transcendence Metro Map\n\nOriginal level 4 content.\n",
            encoding="utf-8",
        )
        (appendix_dir / "AppQ_appendix_only_metro_map.md").write_text(
            "# Appendix Q: Appendix-Only Metro Map\n\nOriginal Appendix Q content.\n",
            encoding="utf-8",
        )

    def _seed_workspace(self) -> list[dict[str, object]]:
        specs: list[dict[str, object]] = []
        specs.append(
            self._write_text_source(
                "Manuscripts/alpha.md",
                "# Alpha Atlas\n\nMetro routing and replay kernel for manuscript architecture.",
                headings=["Alpha Atlas"],
                excerpt="Metro routing and replay kernel for manuscript architecture.",
            )
        )
        specs.append(
            self._write_text_source(
                "Manuscripts/dup1.txt",
                "Duplicate theorem shell with witness routing.",
                headings=["Duplicate One"],
                excerpt="Duplicate theorem shell with witness routing.",
            )
        )
        specs.append(
            self._write_text_source(
                "Manuscripts/dup2.txt",
                "Duplicate theorem shell with witness routing.",
                headings=["Duplicate Two"],
                excerpt="Duplicate theorem shell with witness routing.",
            )
        )
        specs.append(
            self._write_docx_source(
                "Manuscripts/beta.docx",
                "Beta Chronicle\n\nPhase rotation, orbit coupling, and synchronization calculus.",
                headings=["Beta Chronicle"],
                excerpt="Phase rotation, orbit coupling, and synchronization calculus.",
            )
        )
        specs.append(
            self._write_binary_source(
                "Manuscripts/gamma.pdf",
                b"%PDF-1.4 minimal placeholder",
                headings=["Gamma Proof"],
                excerpt="Proof witness closure and replay verification.",
            )
        )
        specs.append(
            self._write_zip_source(
                "Manuscripts/archive.zip",
                {
                    "inner/short.md": "# Short\nCloud corridor residuals.",
                    "inner/long.md": "# Long Archive\nCloud corridor residuals with multiple candidate branches and ambiguity plans.",
                },
                headings=["Archive Capsule"],
                excerpt="Cloud corridor residuals with ambiguity plans.",
            )
        )
        specs.append(
            self._write_zip_source(
                "Manuscripts/single.zip",
                {
                    "inner/only.md": "# Only Member\nSingle archive member with route construction.",
                },
                headings=["Single Archive"],
                excerpt="Single archive member with route construction.",
            )
        )
        specs.append(
            self._write_zip_source(
                "Manuscripts/empty.zip",
                {
                    "inner/binary.bin": "not-readable-here",
                },
                headings=["Empty Archive"],
                excerpt="No readable manuscript members.",
            )
        )
        specs.append(
            self._write_text_source(
                "Manuscripts/already.4d.md",
                "# Existing Rewrite\nShould be excluded.",
                headings=["Existing Rewrite"],
                excerpt="Should be excluded.",
            )
        )
        specs.append(
            self._write_text_source(
                "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/generated.md",
                "# Generated Artifact\nShould be excluded by denylist.",
                headings=["Generated Artifact"],
                excerpt="Should be excluded by denylist.",
            )
        )
        specs.append(
            self._write_text_source(
                "Notes/non_manuscript.md",
                "# Side Note\nNot tagged as a manuscript.",
                role_tags=["readable"],
                headings=["Side Note"],
                excerpt="Not tagged as a manuscript.",
            )
        )
        return specs

    def _write_text_source(
        self,
        relative_path: str,
        text: str,
        role_tags: list[str] | None = None,
        headings: list[str] | None = None,
        excerpt: str = "",
    ) -> dict[str, object]:
        path = self.workspace_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return {
            "relative_path": relative_path,
            "role_tags": role_tags or ["manuscript", "readable"],
            "heading_candidates": headings or [],
            "excerpt": excerpt,
        }

    def _write_binary_source(
        self,
        relative_path: str,
        payload: bytes,
        role_tags: list[str] | None = None,
        headings: list[str] | None = None,
        excerpt: str = "",
    ) -> dict[str, object]:
        path = self.workspace_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
        return {
            "relative_path": relative_path,
            "role_tags": role_tags or ["manuscript"],
            "heading_candidates": headings or [],
            "excerpt": excerpt,
        }

    def _write_docx_source(self, relative_path: str, text: str, headings: list[str], excerpt: str) -> dict[str, object]:
        path = self.workspace_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            + "".join(f"<w:p><w:r><w:t>{paragraph}</w:t></w:r></w:p>" for paragraph in text.split("\n\n"))
            + "</w:document>"
        )
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("word/document.xml", xml)
        return {
            "relative_path": relative_path,
            "role_tags": ["manuscript"],
            "heading_candidates": headings,
            "excerpt": excerpt,
        }

    def _write_zip_source(self, relative_path: str, members: dict[str, str], headings: list[str], excerpt: str) -> dict[str, object]:
        path = self.workspace_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(path, "w") as archive:
            for member_name, text in members.items():
                archive.writestr(member_name, text)
        return {
            "relative_path": relative_path,
            "role_tags": ["manuscript"],
            "heading_candidates": headings,
            "excerpt": excerpt,
        }

    def _write_atlas(self) -> Path:
        records = []
        for index, spec in enumerate(self.record_specs, start=1):
            relative_path = spec["relative_path"]
            path = self.workspace_root / relative_path
            payload = path.read_bytes()
            sha256 = hashlib.sha256(payload).hexdigest()
            records.append(
                {
                    "record_id": f"rec-{index:04d}",
                    "path": str(path),
                    "relative_path": relative_path,
                    "top_level": Path(relative_path).parts[0],
                    "extension": path.suffix.lower(),
                    "size_bytes": len(payload),
                    "modified_at": "2026-03-12T00:00:00+00:00",
                    "sha256": sha256,
                    "kind": "document",
                    "role_tags": spec["role_tags"],
                    "text_extractable": path.suffix.lower() in {".md", ".txt"},
                    "heading_candidates": spec["heading_candidates"],
                    "excerpt": spec["excerpt"],
                    "errors": [],
                    "evidence": {"source_type": "test", "locator": str(path)},
                }
            )
        atlas = {
            "generated_at": "2026-03-12T00:00:00+00:00",
            "root": str(self.workspace_root),
            "record_count": len(records),
            "summary": {},
            "records": records,
        }
        atlas_path = self.workspace_root / "self_actualize" / "corpus_atlas.json"
        atlas_path.write_text(json.dumps(atlas, indent=2), encoding="utf-8")
        return atlas_path

    def _args(self, force: bool = False) -> argparse.Namespace:
        return argparse.Namespace(
            workspace_root=str(self.workspace_root),
            atlas="self_actualize/corpus_atlas.json",
            manifest_out="DEEPER CRYSTALIZATION/_build/corpus_4d_rewrites_manifest.json",
            dry_run=False,
            limit=None,
            path_prefix=None,
            force=force,
        )

    def _run_pipeline(self, force: bool = False) -> dict[str, object]:
        with mock.patch("tesseract_metro_v4._read_pdf_path", return_value="Gamma Proof\n\nProof witness closure and replay verification."):
            return driver.run(self._args(force=force))

    def _audit_args(self) -> argparse.Namespace:
        return argparse.Namespace(
            workspace_root=str(self.workspace_root),
            manifest="DEEPER CRYSTALIZATION/_build/corpus_4d_rewrites_manifest.json",
            audit_out="DEEPER CRYSTALIZATION/_build/corpus_4d_rewrites_audit.json",
        )

    def _archive_args(self) -> argparse.Namespace:
        return argparse.Namespace(
            workspace_root=str(self.workspace_root),
            manifest="DEEPER CRYSTALIZATION/_build/corpus_4d_rewrites_manifest.json",
            archive_manifest_out="DEEPER CRYSTALIZATION/_build/corpus_4d_archive_members_manifest.json",
        )

    def _orphan_args(self) -> argparse.Namespace:
        return argparse.Namespace(
            workspace_root=str(self.workspace_root),
            manifest="DEEPER CRYSTALIZATION/_build/corpus_4d_rewrites_manifest.json",
            audit="DEEPER CRYSTALIZATION/_build/corpus_4d_rewrites_audit.json",
            output="DEEPER CRYSTALIZATION/_build/corpus_4d_orphan_classification.json",
        )

    def _registry_args(self) -> argparse.Namespace:
        return argparse.Namespace(
            workspace_root=str(self.workspace_root),
            manifest="DEEPER CRYSTALIZATION/_build/corpus_4d_rewrites_manifest.json",
            audit="DEEPER CRYSTALIZATION/_build/corpus_4d_rewrites_audit.json",
            archive_manifest="DEEPER CRYSTALIZATION/_build/corpus_4d_archive_members_manifest.json",
            registry_out="DEEPER CRYSTALIZATION/_build/corpus_4d_registry.json",
        )

    def _notes_args(self) -> argparse.Namespace:
        return argparse.Namespace(
            workspace_root=str(self.workspace_root),
            registry="DEEPER CRYSTALIZATION/_build/corpus_4d_registry.json",
            orphan_classification="DEEPER CRYSTALIZATION/_build/corpus_4d_orphan_classification.json",
            archive_manifest="DEEPER CRYSTALIZATION/_build/corpus_4d_archive_members_manifest.json",
            output="DEEPER CRYSTALIZATION/_build/awakening_agent_transition_notes.md",
        )

    def _query_args(self, **overrides) -> argparse.Namespace:
        payload = {
            "workspace_root": str(self.workspace_root),
            "registry": "DEEPER CRYSTALIZATION/_build/corpus_4d_registry.json",
            "ms": None,
            "path_prefix": None,
            "chapter": None,
            "appendix": None,
            "lens": None,
            "truth": None,
            "family": None,
            "duplicate_group": None,
            "limit": None,
            "format": "json",
        }
        payload.update(overrides)
        return argparse.Namespace(**payload)

    def _export_args(self) -> argparse.Namespace:
        return argparse.Namespace(
            workspace_root=str(self.workspace_root),
            registry="DEEPER CRYSTALIZATION/_build/corpus_4d_registry.json",
            deeper_network_root="self_actualize/mycelium_brain/dynamic_neural_network/14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK",
        )

    def _integrate_args(self) -> argparse.Namespace:
        return argparse.Namespace(
            workspace_root=str(self.workspace_root),
            manifest="DEEPER CRYSTALIZATION/_build/corpus_4d_rewrites_manifest.json",
            audit="DEEPER CRYSTALIZATION/_build/corpus_4d_rewrites_audit.json",
            orphan_classification="DEEPER CRYSTALIZATION/_build/corpus_4d_orphan_classification.json",
            archive_manifest="DEEPER CRYSTALIZATION/_build/corpus_4d_archive_members_manifest.json",
            registry="DEEPER CRYSTALIZATION/_build/corpus_4d_registry.json",
            notes="DEEPER CRYSTALIZATION/_build/awakening_agent_transition_notes.md",
            receipt="DEEPER CRYSTALIZATION/_build/corpus_4d_next46_integration_receipt.json",
            deeper_network_root="self_actualize/mycelium_brain/dynamic_neural_network/14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK",
        )

    def _run_audit(self) -> dict[str, object]:
        return audit_driver.run(self._audit_args())

    def _run_archive_members(self) -> dict[str, object]:
        return archive_driver.run(self._archive_args())

    def _run_orphan_classification(self) -> dict[str, object]:
        return orphan_driver.run(self._orphan_args())

    def _run_registry(self) -> dict[str, object]:
        return registry_driver.run(self._registry_args())

    def _run_notes(self) -> Path:
        return notes_driver.run(self._notes_args())

    def _run_export(self) -> dict[str, str]:
        return export_driver.run(self._export_args())

    def _run_integration(self) -> dict[str, object]:
        return integrate_driver.run(self._integrate_args())

    def test_selection_excludes_derivatives_and_existing_4d_sources(self) -> None:
        selected, excluded = metro.select_source_records(self.atlas_path)
        selected_paths = {record.relative_path for record in selected}
        excluded_map = {item.relative_path: item.reason for item in excluded}

        self.assertNotIn("Manuscripts/already.4d.md", selected_paths)
        self.assertNotIn("DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/generated.md", selected_paths)
        self.assertEqual(excluded_map["Manuscripts/already.4d.md"], "existing-4d-derivative")
        self.assertEqual(
            excluded_map["DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/generated.md"],
            "denylisted-derivative-tree",
        )

    def test_pipeline_writes_contract_outputs(self) -> None:
        manifest = self._run_pipeline()
        self.assertEqual(manifest["docs_gate_status"], "BLOCKED")
        self.assertEqual(manifest["selected_count"], 8)
        self.assertEqual(manifest["written_count"], 8)
        self.assertGreaterEqual(manifest["truth_totals"]["AMBIG"], 1)
        self.assertGreaterEqual(manifest["truth_totals"]["FAIL"], 1)
        self.assertEqual(len(manifest["duplicate_groups"]), 1)

        alpha_output = self.workspace_root / "Manuscripts" / "alpha.4d.md"
        archive_output = self.workspace_root / "Manuscripts" / "archive.4d.md"
        self.assertTrue(alpha_output.exists())
        self.assertTrue(archive_output.exists())

        alpha_text = alpha_output.read_text(encoding="utf-8")
        archive_text = archive_output.read_text(encoding="utf-8")
        self.assertTrue(alpha_text.startswith("**[Z_i <-> Z* | Arc "))
        self.assertIn("Primary hubs:", alpha_text)
        self.assertIn("Tunnel:", alpha_text)
        self.assertIn("Truth state:", alpha_text)
        self.assertIn("## **Square**", alpha_text)
        self.assertIn("## **Flower**", alpha_text)
        self.assertIn("## **Cloud**", alpha_text)
        self.assertIn("## **Fractal**", alpha_text)
        self.assertIn("## **Crystal Tile**", alpha_text)
        self.assertIn("- S1:", alpha_text)
        self.assertIn("- R4:", alpha_text)
        self.assertIn("## **Support Graph**", alpha_text)
        self.assertIn("## **Replay Hooks**", alpha_text)
        self.assertIn("Docs gate state: BLOCKED", alpha_text)
        self.assertIn("Archive candidates:", alpha_text)
        self.assertIn("Truth state: AMBIG", archive_text)

    def test_determinism_and_idempotency(self) -> None:
        first = self._run_pipeline()
        second = self._run_pipeline()
        forced = self._run_pipeline(force=True)

        self.assertEqual(second["written_count"], 0)
        self.assertEqual(second["skipped_unchanged_count"], first["selected_count"])
        self.assertEqual(
            [(item["relative_path"], item["ms_code"], item["home_chapter"], item["z_point"], item["truth_state"]) for item in first["ms_registry"]],
            [(item["relative_path"], item["ms_code"], item["home_chapter"], item["z_point"], item["truth_state"]) for item in forced["ms_registry"]],
        )

    def test_only_changed_source_rewrites_on_next_run(self) -> None:
        first = self._run_pipeline()
        alpha_source = self.workspace_root / "Manuscripts" / "alpha.md"
        alpha_source.write_text(
            "# Alpha Atlas\n\nMetro routing and replay kernel for manuscript architecture.\n\nAdded migration ledger.",
            encoding="utf-8",
        )
        self.atlas_path = self._write_atlas()
        second = self._run_pipeline()

        self.assertEqual(second["written_count"], 1)
        self.assertEqual(second["skipped_unchanged_count"], first["selected_count"] - 1)

        first_entry = next(item for item in first["ms_registry"] if item["relative_path"] == "Manuscripts/alpha.md")
        second_entry = next(item for item in second["ms_registry"] if item["relative_path"] == "Manuscripts/alpha.md")
        self.assertNotEqual(first_entry["source_sha256"], second_entry["source_sha256"])

    def test_audit_receipt_catches_missing_orphan_stale_and_contract_failures(self) -> None:
        self._run_pipeline()
        missing_output = self.workspace_root / "Manuscripts" / "dup1.4d.md"
        missing_output.unlink()
        orphan_source = self.workspace_root / "Manuscripts" / "orphan.md"
        orphan_source.write_text("# Orphan Source\n\nThis source is not in the manifest.\n", encoding="utf-8")
        orphan_output = self.workspace_root / "Manuscripts" / "orphan.4d.md"
        orphan_output.write_text("**[banner]**\n", encoding="utf-8")
        stale_source = self.workspace_root / "Manuscripts" / "beta.docx"
        stale_source.write_bytes(b"changed-docx-payload")
        broken_output = self.workspace_root / "Manuscripts" / "single.4d.md"
        broken_output.write_text(broken_output.read_text(encoding="utf-8").replace("## **Support Graph**", "## **Support Missing**"), encoding="utf-8")

        audit = self._run_audit()
        self.assertEqual(audit["summary"]["missing_output_count"], 1)
        self.assertEqual(audit["summary"]["orphan_output_count"], 2)
        self.assertEqual(audit["summary"]["stale_output_count"], 1)
        self.assertEqual(audit["summary"]["contract_failure_count"], 1)
        self.assertEqual(audit["missing_outputs"][0]["relative_path"], "Manuscripts/dup1.txt")
        orphan_paths = [item["relative_path"] for item in audit["orphan_outputs"]]
        self.assertIn("Manuscripts/already.4d.md", orphan_paths)
        self.assertIn("Manuscripts/orphan.4d.md", orphan_paths)
        self.assertEqual(audit["stale_outputs"][0]["relative_path"], "Manuscripts/beta.docx")
        self.assertEqual(audit["contract_failures"][0]["relative_path"], "Manuscripts/single.zip")

    def test_archive_member_manifest_keeps_parent_path_level_and_exposes_members(self) -> None:
        manifest = self._run_pipeline()
        archive_receipt = self._run_archive_members()

        self.assertEqual(archive_receipt["summary"]["zip_parent_count"], 3)
        self.assertEqual(archive_receipt["summary"]["multi_candidate_parent_count"], 1)
        self.assertEqual(archive_receipt["summary"]["single_candidate_parent_count"], 1)
        self.assertEqual(archive_receipt["summary"]["zero_candidate_parent_count"], 1)
        self.assertEqual(archive_receipt["summary"]["member_record_count"], 3)

        archive_entry = next(item for item in manifest["ms_registry"] if item["relative_path"] == "Manuscripts/archive.zip")
        single_entry = next(item for item in manifest["ms_registry"] if item["relative_path"] == "Manuscripts/single.zip")
        empty_entry = next(item for item in manifest["ms_registry"] if item["relative_path"] == "Manuscripts/empty.zip")
        archive_parent = next(item for item in archive_receipt["parents"] if item["parent_relative_path"] == "Manuscripts/archive.zip")

        self.assertEqual(len(archive_entry["archive_candidates"]), 2)
        self.assertIsNotNone(archive_entry["archive_member_manifest_path"])
        self.assertEqual(len(single_entry["archive_candidates"]), 1)
        self.assertIsNone(single_entry["archive_member_manifest_path"])
        self.assertEqual(len(empty_entry["archive_candidates"]), 0)
        self.assertEqual(empty_entry["truth_state"], "FAIL")
        self.assertIn("disagreement_summary", archive_parent)
        self.assertGreaterEqual(len(archive_parent["disagreement_summary"]["home_chapters"]), 1)

        member_paths = [item["member_path"] for item in archive_receipt["member_records"]]
        self.assertEqual(member_paths, ["inner/long.md", "inner/short.md", "inner/only.md"])

    def test_orphan_classification_distinguishes_denylisted_historical_standalone_and_true_sibling(self) -> None:
        self._run_pipeline()

        denylisted_output = self.workspace_root / "DEEPER CRYSTALIZATION" / "ACTIVE_NERVOUS_SYSTEM" / "generated.4d.md"
        denylisted_output.write_text("# Denylisted Orphan\n", encoding="utf-8")
        historical_output = self.workspace_root / "Notes" / "non_manuscript.4d.md"
        historical_output.write_text("# Historical Orphan\n", encoding="utf-8")
        standalone_output = self.workspace_root / "Manuscripts" / "already.4d.md"
        true_sibling_source_spec = self._write_text_source(
            "Manuscripts/new_orphan.md",
            "# New Orphan\n\nA selected manuscript that exists in the atlas but not in the manifest.",
            headings=["New Orphan"],
            excerpt="A selected manuscript that exists in the atlas but not in the manifest.",
        )
        true_sibling_output = self.workspace_root / "Manuscripts" / "new_orphan.4d.md"
        true_sibling_output.write_text("# True Sibling Orphan\n", encoding="utf-8")

        self.record_specs.extend(
            [
                {
                    "relative_path": "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/generated.4d.md",
                    "role_tags": ["readable"],
                    "heading_candidates": ["Generated Orphan"],
                    "excerpt": "Denylisted orphan output.",
                },
                {
                    "relative_path": "Notes/non_manuscript.4d.md",
                    "role_tags": ["readable"],
                    "heading_candidates": ["Historical Orphan"],
                    "excerpt": "Historical orphan output.",
                },
                true_sibling_source_spec,
                {
                    "relative_path": "Manuscripts/new_orphan.4d.md",
                    "role_tags": ["readable"],
                    "heading_candidates": ["True Sibling Orphan"],
                    "excerpt": "True sibling orphan output.",
                },
            ]
        )
        self.atlas_path = self._write_atlas()

        self._run_audit()
        orphan_receipt = self._run_orphan_classification()
        by_path = {item["relative_path"]: item for item in orphan_receipt["orphan_records"]}

        self.assertEqual(
            by_path["DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/generated.4d.md"]["orphan_class"],
            "denylisted",
        )
        self.assertEqual(by_path["Notes/non_manuscript.4d.md"]["orphan_class"], "historical-4d")
        self.assertEqual(by_path["Manuscripts/already.4d.md"]["orphan_class"], "standalone-4d")
        self.assertEqual(by_path["Manuscripts/new_orphan.4d.md"]["orphan_class"], "true-sibling-orphan")
        self.assertNotIn("Manuscripts/alpha.4d.md", by_path)
        self.assertIn("classification problem", orphan_receipt["integration_note"])

    def test_registry_query_is_deterministic_and_filterable(self) -> None:
        manifest = self._run_pipeline()
        self._run_audit()
        self._run_archive_members()
        registry = self._run_registry()

        ambig_nodes = query_driver.run(self._query_args(truth="AMBIG"))
        self.assertEqual([node["relative_path"] for node in ambig_nodes], ["Manuscripts/archive.zip"])

        duplicate_group = next(item["duplicate_group"] for item in manifest["ms_registry"] if item["relative_path"] == "Manuscripts/dup1.txt")
        duplicate_nodes = query_driver.run(self._query_args(duplicate_group=duplicate_group))
        self.assertEqual([node["relative_path"] for node in duplicate_nodes], ["Manuscripts/dup1.txt", "Manuscripts/dup2.txt"])

        chapter_nodes = query_driver.run(self._query_args(chapter="Ch21"))
        self.assertTrue(all(node["home_chapter"] == "Ch21" for node in chapter_nodes))

        path_nodes = query_driver.run(self._query_args(path_prefix="Manuscripts/du"))
        self.assertEqual([node["relative_path"] for node in path_nodes], ["Manuscripts/dup1.txt", "Manuscripts/dup2.txt"])

        lens = registry["nodes"][0]["dominant_lens"]
        lens_nodes = query_driver.run(self._query_args(lens=lens))
        self.assertTrue(all(node["dominant_lens"] == lens for node in lens_nodes))

        appendix = registry["nodes"][0]["appendices"][0]
        appendix_nodes = query_driver.run(self._query_args(appendix=appendix))
        self.assertTrue(all(appendix in node["appendices"] for node in appendix_nodes))

        self.assertEqual(registry["summary"]["node_count"], 8)
        self.assertEqual(registry["summary"]["ambig_archive_parent_count"], 1)

    def test_transition_notes_capture_stages_and_live_fronts(self) -> None:
        self._run_pipeline()
        self._run_audit()
        self._run_archive_members()
        self._run_orphan_classification()
        self._run_registry()

        notes_path = self._run_notes()
        notes_text = notes_path.read_text(encoding="utf-8")

        self.assertTrue(notes_path.exists())
        self.assertIn("## Stage 0 - Orientation Before Action", notes_text)
        self.assertIn("## Stage 6 - Complete Act / Omega Window", notes_text)
        self.assertIn("orphan frontier", notes_text.lower())
        self.assertIn("archive frontier", notes_text.lower())
        self.assertIn("registry", notes_text.lower())
        self.assertIn("overlay", notes_text.lower())
        self.assertIn("Mapping agents", notes_text)
        self.assertIn("Omega stewards", notes_text)

    def test_export_writes_additive_deeper_network_surfaces(self) -> None:
        self._run_pipeline()
        self._run_audit()
        self._run_archive_members()
        registry = self._run_registry()
        self._run_orphan_classification()
        self._run_notes()

        level4_before = (self.network_root / "07_METRO_STACK" / "03_level_4_transcendence_metro_map.md").read_text(encoding="utf-8")
        appq_before = (self.network_root / "08_APPENDIX_CRYSTAL" / "AppQ_appendix_only_metro_map.md").read_text(encoding="utf-8")

        result = self._run_export()
        overlay_path = Path(result["overlay_path"])
        appendix_path = Path(result["appendix_path"])
        transition_map_path = Path(result["transition_map_path"])
        transition_appendix_path = Path(result["transition_appendix_path"])
        overlay_text = overlay_path.read_text(encoding="utf-8")
        appendix_text = appendix_path.read_text(encoding="utf-8")
        transition_map_text = transition_map_path.read_text(encoding="utf-8")
        transition_appendix_text = transition_appendix_path.read_text(encoding="utf-8")

        self.assertTrue(overlay_path.exists())
        self.assertTrue(appendix_path.exists())
        self.assertTrue(transition_map_path.exists())
        self.assertTrue(transition_appendix_path.exists())
        self.assertIn("## AMBIG Archive Frontier", overlay_text)
        self.assertIn("Manuscripts/archive.zip", overlay_text)
        self.assertIn("Docs gate truth: BLOCKED", appendix_text)
        self.assertIn(f"NEAR: {registry['summary']['truth_totals']['NEAR']}", appendix_text)
        self.assertIn("## Transition Notes", transition_map_text)
        self.assertIn("## Stage 6 - Complete Act / Omega Window", transition_map_text)
        self.assertIn("AppS is the appendix-side contract", transition_appendix_text)
        self.assertIn("Parent zip manuscripts remain AMBIG", transition_appendix_text)
        self.assertEqual(level4_before, (self.network_root / "07_METRO_STACK" / "03_level_4_transcendence_metro_map.md").read_text(encoding="utf-8"))
        self.assertEqual(appq_before, (self.network_root / "08_APPENDIX_CRYSTAL" / "AppQ_appendix_only_metro_map.md").read_text(encoding="utf-8"))

    def test_integration_receipt_binds_registry_orphans_notes_and_exports(self) -> None:
        self._run_pipeline()

        receipt = self._run_integration()

        self.assertTrue(self.integration_receipt_path.exists())
        self.assertEqual(receipt["summary"]["selected_count"], 8)
        self.assertEqual(receipt["summary"]["registry_summary"]["node_count"], 8)
        self.assertEqual(receipt["summary"]["stage_count"], 7)
        self.assertEqual(receipt["docs_gate_status"], "BLOCKED")
        self.assertTrue(receipt["additive_only_export_policy"])
        self.assertEqual(receipt["interface_precedence"][0], "main manifest")
        self.assertIn("local corpus evidence only", receipt["docs_gate_constraint"])
        self.assertIn("transition_map_path", receipt["export_paths"])
        self.assertIn("transition_appendix_path", receipt["export_paths"])
        self.assertTrue((self.workspace_root / receipt["export_paths"]["transition_map_path"]).exists())
        self.assertTrue((self.workspace_root / receipt["export_paths"]["transition_appendix_path"]).exists())


if __name__ == "__main__":
    unittest.main()
