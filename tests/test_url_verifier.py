from __future__ import annotations

import csv
import io
import json
import socket
import unittest
from email.message import Message
from urllib.error import HTTPError
from urllib.request import Request
from unittest.mock import patch

from core.citation_integrity.models import BibEntry
from core.citation_integrity.url_verifier import (
    build_url_verification_report,
    verify_bib_urls,
    verify_url,
    write_url_flagged_csv,
    write_url_verification_json,
)
from tests.helpers import workspace_tempdir


class _MockHttpResponse:
    def __init__(self, url: str, status: int) -> None:
        self.url = url
        self.status = status

    def __enter__(self) -> "_MockHttpResponse":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None


def _http_error(url: str, code: int, message: str) -> HTTPError:
    return HTTPError(url, code, message, Message(), None)


class UrlVerifierTest(unittest.TestCase):
    def test_verify_url_ok(self) -> None:
        with patch("urllib.request.urlopen", return_value=_MockHttpResponse("https://example.com/doc", 200)):
            result = verify_url("https://example.com/doc")

        self.assertEqual(result.status, "URL_OK")
        self.assertEqual(result.http_status, 200)

    def test_verify_url_not_found(self) -> None:
        with patch("urllib.request.urlopen", return_value=_MockHttpResponse("https://example.com/missing", 404)):
            result = verify_url("https://example.com/missing")

        self.assertEqual(result.status, "URL_NOT_FOUND")
        self.assertEqual(result.http_status, 404)

    def test_verify_url_classifies_http_error_not_found(self) -> None:
        error = _http_error("https://example.com/missing", 404, "Not Found")
        with patch("urllib.request.urlopen", side_effect=error):
            result = verify_url("https://example.com/missing")

        self.assertEqual(result.status, "URL_NOT_FOUND")
        self.assertEqual(result.http_status, 404)

    def test_verify_url_classifies_http_error_forbidden(self) -> None:
        error = _http_error("https://example.com/private", 403, "Forbidden")
        with patch("urllib.request.urlopen", side_effect=error):
            result = verify_url("https://example.com/private")

        self.assertEqual(result.status, "URL_FORBIDDEN")
        self.assertEqual(result.http_status, 403)

    def test_verify_url_redirected(self) -> None:
        with patch("urllib.request.urlopen", return_value=_MockHttpResponse("https://final.example.com/doc", 200)):
            result = verify_url("https://example.com/doc")

        self.assertEqual(result.status, "URL_REDIRECTED")
        self.assertEqual(result.final_url, "https://final.example.com/doc")

    def test_verify_url_head_405_falls_back_to_get(self) -> None:
        calls: list[str] = []

        def fake_urlopen(request: Request, timeout: float = 10.0) -> _MockHttpResponse:
            method = request.get_method()
            calls.append(method)
            if method == "HEAD":
                return _MockHttpResponse("https://example.com/doc", 405)
            return _MockHttpResponse("https://example.com/doc", 200)

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            result = verify_url("https://example.com/doc")

        self.assertEqual(calls, ["HEAD", "GET"])
        self.assertEqual(result.status, "URL_OK")

    def test_verify_url_http_error_405_head_falls_back_to_get(self) -> None:
        calls: list[str] = []

        def fake_urlopen(request: Request, timeout: float = 10.0) -> _MockHttpResponse:
            method = request.get_method()
            calls.append(method)
            if method == "HEAD":
                raise _http_error("https://example.com/doc", 405, "Method Not Allowed")
            return _MockHttpResponse("https://example.com/doc", 200)

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            result = verify_url("https://example.com/doc")

        self.assertEqual(calls, ["HEAD", "GET"])
        self.assertEqual(result.status, "URL_OK")

    def test_verify_url_unreachable_on_timeout(self) -> None:
        with patch("urllib.request.urlopen", side_effect=TimeoutError("timeout")):
            result = verify_url("https://example.com/doc")

        self.assertEqual(result.status, "URL_UNREACHABLE")

    def test_verify_bib_urls_whitelists_gov_cn(self) -> None:
        entries = [
            BibEntry(
                key="gov2024",
                entry_type="misc",
                file="ref/refs.bib",
                line=1,
                fields={"url": "https://www.gov.cn/policy/test"},
                body="",
            )
        ]
        with patch("urllib.request.urlopen") as urlopen:
            results = verify_bib_urls(entries, whitelist_domains=("gov.cn", "edu.cn"))

        self.assertEqual(results[0].status, "URL_WHITELISTED")
        urlopen.assert_not_called()

    def test_verify_bib_urls_extracts_url_from_howpublished(self) -> None:
        entries = [
            BibEntry(
                key="site2024",
                entry_type="misc",
                file="ref/refs.bib",
                line=1,
                fields={"howpublished": "Available at https://example.com/policy"},
                body="",
            )
        ]
        with patch("urllib.request.urlopen", return_value=_MockHttpResponse("https://example.com/policy", 200)):
            results = verify_bib_urls(entries, whitelist_domains=("gov.cn", "edu.cn"))

        self.assertEqual(results[0].citation_key, "site2024")
        self.assertEqual(results[0].status, "URL_OK")

    def test_build_and_write_url_reports(self) -> None:
        entries = [
            BibEntry(
                key="bad2024",
                entry_type="misc",
                file="ref/refs.bib",
                line=1,
                fields={"url": "https://example.com/missing"},
                body="",
            )
        ]
        with patch("urllib.request.urlopen", return_value=_MockHttpResponse("https://example.com/missing", 404)):
            results = verify_bib_urls(entries, whitelist_domains=("gov.cn", "edu.cn"))
        report = build_url_verification_report(results)
        with workspace_tempdir("url-report-") as tmp:
            json_path = tmp / "reports" / "url-verification-report.json"
            csv_path = tmp / "reports" / "url-verification-flagged.csv"
            write_url_verification_json(report, json_path)
            write_url_flagged_csv(report, csv_path)
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            rows = list(csv.DictReader(io.StringIO(csv_path.read_text(encoding="utf-8"))))

        self.assertEqual(payload["module"], "url_verification")
        self.assertEqual(rows[0]["citation_key"], "bad2024")


if __name__ == "__main__":
    unittest.main()
