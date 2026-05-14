from __future__ import annotations

import csv
import io
import json
import unittest

from core.citation_integrity.doi_candidates import write_doi_candidate_csv, write_doi_candidate_json
from core.citation_integrity.external_report import write_external_verification_report
from core.citation_integrity.hallucination_risk import write_hallucination_risk_report
from core.citation_integrity.url_verifier import write_url_flagged_csv, write_url_verification_json
from tests.helpers import workspace_tempdir


class UnicodeReportIntegrityTest(unittest.TestCase):
    def test_external_report_json_round_trips_cjk(self) -> None:
        report = {
            "module": "citation_external_verification",
            "version": "2.0-alpha",
            "summary": {"entries_considered": 1},
            "entries": [{"citation_key": "zh2024", "local_metadata": {"title": "\u4eba\u5de5\u667a\u80fd\u8bba\u6587"}, "match_status": "REVIEW", "providers": [], "consensus": {}, "recommended_action": "manual"}],
        }
        with workspace_tempdir("unicode-ext-") as tmp:
            path = tmp / "reports" / "external-verification-report.json"
            write_external_verification_report(report, path)
            text = path.read_text(encoding="utf-8")
            payload = json.loads(text)

        self.assertIn("人工智能论文", text)
        self.assertEqual(payload["entries"][0]["local_metadata"]["title"], "人工智能论文")

    def test_hallucination_risk_json_round_trips_cjk(self) -> None:
        report = {
            "module": "citation_hallucination_risk",
            "version": "3.0",
            "summary": {"entries_considered": 1},
            "entries": [{"citation_key": "zh2024", "local_metadata": {"title": "\u4e2d\u6587\u6807\u9898"}, "risk_label": "UNSUPPORTED", "hallucination_risk_score": 0.0, "external_match_status": "UNSUPPORTED", "evidence": {"metadata_mismatches": []}, "recommended_action": "manual"}],
        }
        with workspace_tempdir("unicode-hrisk-") as tmp:
            path = tmp / "reports" / "hallucination-risk-report.json"
            write_hallucination_risk_report(report, path)
            payload = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(payload["entries"][0]["local_metadata"]["title"], "中文标题")

    def test_doi_candidate_json_and_csv_round_trip_cjk(self) -> None:
        report = {
            "module": "missing_doi_candidates",
            "version": "3.3",
            "summary": {"candidate_count": 1},
            "entries": [{"citation_key": "zh2024", "local_title": "\u4e2d\u6587\u6587\u732e", "local_year": "2024", "candidate_doi": "10.1000/test", "candidate_title": "\u4e2d\u6587\u6587\u732e", "candidate_year": "2024", "candidate_authors": "\u5f20\u4e09", "provider": "crossref", "confidence": 0.9, "recommended_action": "manual"}],
        }
        with workspace_tempdir("unicode-doi-") as tmp:
            json_path = tmp / "reports" / "missing-doi-candidates.json"
            csv_path = tmp / "reports" / "missing-doi-candidates.csv"
            write_doi_candidate_json(report, json_path)
            write_doi_candidate_csv(report, csv_path)
            json_payload = json.loads(json_path.read_text(encoding="utf-8"))
            csv_rows = list(csv.DictReader(io.StringIO(csv_path.read_text(encoding="utf-8"))))

        self.assertEqual(json_payload["entries"][0]["local_title"], "中文文献")
        self.assertEqual(csv_rows[0]["candidate_authors"], "张三")

    def test_url_report_json_and_csv_round_trip_cjk(self) -> None:
        report = {
            "module": "url_verification",
            "version": "3.3",
            "summary": {"checked": 1, "flagged": 1},
            "entries": [{"citation_key": "zh2024", "url": "https://example.com/\u653f\u7b56", "status": "URL_NOT_FOUND", "http_status": 404, "final_url": "https://example.com/\u653f\u7b56", "note": "\u4eba\u5de5\u590d\u6838"}],
        }
        with workspace_tempdir("unicode-url-") as tmp:
            json_path = tmp / "reports" / "url-verification-report.json"
            csv_path = tmp / "reports" / "url-verification-flagged.csv"
            write_url_verification_json(report, json_path)
            write_url_flagged_csv(report, csv_path)
            json_payload = json.loads(json_path.read_text(encoding="utf-8"))
            csv_rows = list(csv.DictReader(io.StringIO(csv_path.read_text(encoding="utf-8"))))

        self.assertEqual(json_payload["entries"][0]["note"], "人工复核")
        self.assertEqual(csv_rows[0]["note"], "人工复核")


if __name__ == "__main__":
    unittest.main()
