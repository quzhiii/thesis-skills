from __future__ import annotations

import csv
import io
import json
import unittest

from core.citation_integrity.models import BibEntry, CitationWithContext
from core.citation_integrity.tex_parser import extract_citation_contexts
from tests.helpers import workspace_tempdir


class CitationContextExtractionTest(unittest.TestCase):
    def test_extracts_single_citation_mid_sentence_context(self) -> None:
        text = "Recent studies show measurable improvements \\cite{smith2024} in benchmark settings."

        contexts = extract_citation_contexts(text, "chapters/results.tex")

        self.assertEqual(len(contexts), 1)
        self.assertEqual(contexts[0].key, "smith2024")
        self.assertEqual(contexts[0].command, "cite")
        self.assertEqual(contexts[0].file, "chapters/results.tex")
        self.assertEqual(contexts[0].line, 1)
        self.assertEqual(
            contexts[0].context,
            "Recent studies show measurable improvements in benchmark settings.",
        )

    def test_extracts_citation_at_sentence_end_context(self) -> None:
        text = "Transformer models improved sequence modeling in prior work \\citep{vaswani2017}. Next sentence."

        contexts = extract_citation_contexts(text, "main.tex")

        self.assertEqual(len(contexts), 1)
        self.assertEqual(contexts[0].key, "vaswani2017")
        self.assertEqual(contexts[0].command, "citep")
        self.assertEqual(
            contexts[0].context,
            "Transformer models improved sequence modeling in prior work.",
        )

    def test_bare_citation_on_own_line_has_empty_context(self) -> None:
        text = "Intro sentence.\n\\cite{bare2024}\nFollow-up sentence."

        contexts = extract_citation_contexts(text, "main.tex")

        self.assertEqual(len(contexts), 1)
        self.assertEqual(contexts[0].key, "bare2024")
        self.assertEqual(contexts[0].line, 2)
        self.assertEqual(contexts[0].context, "")

    def test_multiple_keys_share_clean_context(self) -> None:
        text = "Several studies report stable effects \\cite{alpha2022, beta2023, gamma2024}."

        contexts = extract_citation_contexts(text, "chapter2.tex")

        self.assertEqual([item.key for item in contexts], ["alpha2022", "beta2023", "gamma2024"])
        self.assertEqual([item.command for item in contexts], ["cite", "cite", "cite"])
        self.assertEqual(
            [item.context for item in contexts],
            ["Several studies report stable effects."] * 3,
        )


class ClaimCitationTriageTest(unittest.TestCase):
    def _context(self, key: str = "smith2024", context: str = "Prior work shows stable accuracy gains.") -> CitationWithContext:
        return CitationWithContext(
            key=key,
            command="cite",
            file="main.tex",
            line=3,
            context=context,
        )

    def _entry(self, key: str = "smith2024", fields: dict[str, str] | None = None) -> BibEntry:
        return BibEntry(
            key=key,
            entry_type="article",
            file="ref/refs.bib",
            line=1,
            fields=fields or {"title": "Reliable Study", "author": "Smith, Jane", "year": "2024"},
            body="",
        )

    def _risk(self, key: str = "smith2024", label: str = "PASS") -> dict[str, object]:
        return {"citation_key": key, "risk_label": label}

    def test_pass_reference_with_substantive_context_is_well_supported(self) -> None:
        from core.citation_integrity.claim_citation import triage_claim_citation

        result = triage_claim_citation(self._context(), self._entry(), self._risk(), 2)

        self.assertEqual(result["triage_label"], "WELL_SUPPORTED")
        self.assertEqual(result["triage_score"], 0.0)
        self.assertEqual(result["reference_metadata"]["title"], "Reliable Study")
        self.assertTrue(result["evidence"]["has_complete_metadata"])

    def test_review_reference_is_weak(self) -> None:
        from core.citation_integrity.claim_citation import triage_claim_citation

        result = triage_claim_citation(self._context(), self._entry(), self._risk(label="REVIEW"), 2)

        self.assertEqual(result["triage_label"], "WEAK")
        self.assertEqual(result["triage_score"], 0.25)
        self.assertEqual(result["hallucination_risk_label"], "REVIEW")

    def test_missing_bib_entry_is_orphaned(self) -> None:
        from core.citation_integrity.claim_citation import triage_claim_citation

        result = triage_claim_citation(self._context("missing2024"), None, None, 1)

        self.assertEqual(result["triage_label"], "ORPHANED")
        self.assertGreaterEqual(result["triage_score"], 0.5)
        self.assertEqual(result["reference_metadata"], {})

    def test_unsupported_reference_is_unverifiable(self) -> None:
        from core.citation_integrity.claim_citation import triage_claim_citation

        result = triage_claim_citation(self._context(), self._entry(), self._risk(label="UNSUPPORTED"), 1)

        self.assertEqual(result["triage_label"], "UNVERIFIABLE")
        self.assertIsNone(result["triage_score"])

    def test_bare_citation_gets_context_score_boost(self) -> None:
        from core.citation_integrity.claim_citation import triage_claim_citation

        result = triage_claim_citation(self._context(context=""), self._entry(), self._risk(), 2)

        self.assertEqual(result["triage_label"], "SUPPORTED")
        self.assertEqual(result["triage_score"], 0.15)
        self.assertFalse(result["evidence"]["has_claim_context"])

    def test_high_risk_with_existing_bib_entry_is_weak_not_orphaned(self) -> None:
        from core.citation_integrity.claim_citation import triage_claim_citation

        result = triage_claim_citation(self._context(), self._entry(), self._risk(label="HIGH_RISK"), 1)

        self.assertEqual(result["triage_label"], "WEAK")
        self.assertGreaterEqual(result["triage_score"], 0.5)
        self.assertIn("HIGH_RISK", str(result["recommended_action"]))
        self.assertNotIn("not found in bibliography", str(result["recommended_action"]))

    def test_build_report_counts_entries_and_uncited_references(self) -> None:
        from core.citation_integrity.claim_citation import build_claim_citation_report

        contexts = [self._context("smith2024"), self._context("missing2024")]
        entries = [self._entry("smith2024"), self._entry("unused2023")]
        hallucination_report = {
            "entries": [
                self._risk("smith2024", "PASS"),
                self._risk("unused2023", "WARN"),
            ]
        }

        report = build_claim_citation_report(contexts, entries, hallucination_report)

        self.assertEqual(report["module"], "claim_citation_triage")
        self.assertEqual(report["version"], "3.1")
        self.assertEqual(report["status"], "ORPHANED")
        self.assertEqual(report["summary"]["claim_citation_pairs"], 2)
        self.assertEqual(report["summary"]["orphaned_pairs"], 1)
        self.assertEqual(report["summary"]["unique_references_cited"], 2)
        self.assertEqual(report["summary"]["unique_references_never_cited"], 1)
        self.assertEqual(report["uncited_references"][0]["citation_key"], "unused2023")


class ClaimCitationReportWritersTest(unittest.TestCase):
    def _report(self) -> dict[str, object]:
        from core.citation_integrity.claim_citation import build_claim_citation_report

        ctx = lambda k, c: CitationWithContext(key=k, command="cite", file="main.tex", line=1, context=c)
        ent = lambda k, t, a, y: BibEntry(key=k, entry_type="article", file="ref/refs.bib", line=1, fields={"title": t, "author": a, "year": y}, body="")
        contexts = [ctx("ok2024", "A well-supported claim."), ctx("weak2024", "Vague claim.")]
        entries = [ent("ok2024", "Good Title", "Author A", "2024"), ent("weak2024", "Meh", "", "2024")]
        hallucination = {"entries": [{"citation_key": "ok2024", "risk_label": "PASS"}, {"citation_key": "weak2024", "risk_label": "REVIEW"}]}
        return build_claim_citation_report(contexts, entries, hallucination)

    def test_write_json_report_produces_valid_schema(self) -> None:
        from core.citation_integrity.claim_citation import write_claim_citation_report_json

        report = self._report()
        with workspace_tempdir("cc-json-") as tmp:
            output = tmp / "reports" / "claim-citation-triage-report.json"
            write_claim_citation_report_json(report, output)
            payload = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(payload["module"], "claim_citation_triage")
        self.assertEqual(payload["version"], "3.1")
        self.assertIn("generated_at", payload)
        self.assertIn("status", payload)
        self.assertIn("summary", payload)
        self.assertIn("entries", payload)
        self.assertIn("uncited_references", payload)
        self.assertIsInstance(payload["entries"], list)
        self.assertGreaterEqual(len(payload["entries"]), 2)

    def test_write_markdown_report_groups_by_triage_label(self) -> None:
        from core.citation_integrity.claim_citation import write_claim_citation_report_md

        report = self._report()
        with workspace_tempdir("cc-md-") as tmp:
            output = tmp / "reports" / "claim-citation-triage.md"
            write_claim_citation_report_md(report, output)
            text = output.read_text(encoding="utf-8")

        self.assertIn("# Claim-Citation Triage Report", text)
        self.assertIn("**Status:**", text)
        self.assertIn("## Summary", text)
        self.assertIn("SUPPORTED", text)
        self.assertIn("WEAK", text)

    def test_write_csv_report_excludes_well_supported_by_default(self) -> None:
        from core.citation_integrity.claim_citation import write_claim_citation_report_csv

        report = self._report()
        with workspace_tempdir("cc-csv-") as tmp:
            output = tmp / "reports" / "claim-citation-triage.csv"
            write_claim_citation_report_csv(report, output)
            text = output.read_text(encoding="utf-8")

        reader = csv.DictReader(io.StringIO(text))
        rows = list(reader)
        labels = [row["triage_label"] for row in rows]
        self.assertNotIn("WELL_SUPPORTED", labels)
        self.assertIn("WEAK", labels)

    def test_csv_has_correct_header_columns(self) -> None:
        from core.citation_integrity.claim_citation import write_claim_citation_report_csv

        report = self._report()
        with workspace_tempdir("cc-csv2-") as tmp:
            output = tmp / "reports" / "claim-citation-triage.csv"
            write_claim_citation_report_csv(report, output)
            text = output.read_text(encoding="utf-8")

        reader = csv.DictReader(io.StringIO(text))
        self.assertEqual(
            reader.fieldnames,
            ["citation_key", "triage_label", "triage_score", "claim_context", "file", "line", "hallucination_risk_label", "citation_frequency", "recommended_action"],
        )


if __name__ == "__main__":
    unittest.main()
