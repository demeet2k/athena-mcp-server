#!/usr/bin/env python3
"""Search Google Docs by keyword(s) using the Google Drive API."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
DOCS_MIME_TYPE = "application/vnd.google-apps.document"


def _escape_query_term(term: str) -> str:
    """Escape a term so it is safe inside a single-quoted Drive query."""
    return term.replace("\\", "\\\\").replace("'", "\\'")


def build_query(terms: Iterable[str], match_all_terms: bool) -> str:
    term_clauses = [f"fullText contains '{_escape_query_term(term)}'" for term in terms]
    if match_all_terms:
        text_clause = " and ".join(term_clauses)
    else:
        text_clause = "(" + " or ".join(term_clauses) + ")"

    return (
        f"mimeType = '{DOCS_MIME_TYPE}' and trashed = false and {text_clause}"
    )


def load_credentials(credentials_path: Path, token_path: Path) -> Credentials:
    creds: Credentials | None = None

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not credentials_path.exists():
                raise FileNotFoundError(
                    f"Missing OAuth client file: {credentials_path}\n"
                    "Create/download a Desktop App OAuth client in Google Cloud Console "
                    "and save it as credentials.json (or pass --credentials)."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path), SCOPES
            )
            creds = flow.run_local_server(port=0)

        token_path.write_text(creds.to_json(), encoding="utf-8")

    return creds


def search_docs(service, query: str, max_results: int) -> list[dict]:
    files: list[dict] = []
    page_token: str | None = None

    while len(files) < max_results:
        page_size = min(100, max_results - len(files))
        response = (
            service.files()
            .list(
                q=query,
                spaces="drive",
                corpora="user",
                pageSize=page_size,
                pageToken=page_token,
                fields="nextPageToken, files(id, name, modifiedTime, owners(displayName), webViewLink)",
            )
            .execute()
        )

        files.extend(response.get("files", []))
        page_token = response.get("nextPageToken")
        if not page_token:
            break

    return files


def print_results(files: list[dict]) -> None:
    if not files:
        print("No matching Google Docs found.")
        return

    print(f"Found {len(files)} matching Google Doc(s):\n")
    for index, file in enumerate(files, start=1):
        owner = ""
        owners = file.get("owners", [])
        if owners:
            owner = owners[0].get("displayName", "")
        link = file.get("webViewLink") or f"https://docs.google.com/document/d/{file['id']}/edit"
        print(f"{index}. {file.get('name', '(untitled)')}")
        print(f"   Modified: {file.get('modifiedTime', 'unknown')}")
        print(f"   Owner:    {owner or 'unknown'}")
        print(f"   Link:     {link}")
        print()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Search your Google Docs by keyword(s)."
    )
    parser.add_argument(
        "terms",
        nargs="+",
        help="Search term(s), e.g. manuscript holographic time",
    )
    parser.add_argument(
        "--any",
        action="store_true",
        help="Match docs containing ANY term (default is ALL terms).",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=50,
        help="Maximum docs to return (default: 50).",
    )
    parser.add_argument(
        "--credentials",
        default="credentials.json",
        help="Path to OAuth client JSON downloaded from Google Cloud Console.",
    )
    parser.add_argument(
        "--token",
        default="token.json",
        help="Path where the user auth token should be stored.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON instead of human-readable text.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.max_results < 1:
        print("--max-results must be >= 1", file=sys.stderr)
        return 2

    try:
        creds = load_credentials(Path(args.credentials), Path(args.token))
        service = build("drive", "v3", credentials=creds, cache_discovery=False)
        query = build_query(args.terms, match_all_terms=not args.any)
        files = search_docs(service, query=query, max_results=args.max_results)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(files, indent=2))
    else:
        print_results(files)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
