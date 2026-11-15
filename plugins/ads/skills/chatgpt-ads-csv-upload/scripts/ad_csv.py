#!/usr/bin/env python3
"""Validate and reconcile ChatGPT Ads CSV files locally, without account access."""

import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import unicodedata
from urllib.parse import urlsplit


HEADERS = [
    "ad_id", "ad_group_id", "adgroup_name", "ad_name", "status",
    "title", "copy", "link", "image_url", "image_file_id",
]
NATIVE_HEADERS = [name for name in HEADERS if name != "adgroup_name"]
CREATIVE_FIELDS = ["status", "title", "copy", "link", "image_url", "image_file_id"]
ID_PATTERNS = {
    "ad_id": re.compile(r"ad_[A-Za-z0-9]+\Z"),
    "ad_group_id": re.compile(r"adgrp_[A-Za-z0-9]+\Z"),
    "image_file_id": re.compile(r"file_[A-Za-z0-9]+\Z"),
}


class CsvProblem(Exception):
    def __init__(self, errors):
        super().__init__("CSV checks failed")
        self.errors = errors


def error(code, message, *, row=None, field=None):
    item = {"code": code, "message": message}
    if row is not None:
        item["row"] = row
    if field is not None:
        item["field"] = field
    return item


def read_csv(filename, *, native=False):
    path = Path(filename)
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise CsvProblem([error("encoding", "CSV must be UTF-8 (a BOM is allowed).")]) from exc
    reader = csv.reader(io.StringIO(text, newline=""), strict=True)
    errors, rows = [], []
    try:
        headers = next(reader, None)
        valid = (headers == HEADERS) if not native else (
            headers is not None
            and len(headers) == len(set(headers))
            and set(headers) in (set(HEADERS), set(NATIVE_HEADERS))
        )
        if not valid:
            kind = "native nine- or ten-column schema" if native else "exact ten-column template order"
            raise CsvProblem([error("headers", "Headers must match the " + kind + ".", row=1)])
        for number, values in enumerate(reader, 2):
            if not values or all(not value.strip() for value in values):
                errors.append(error("blank_row", "Blank CSV records are not allowed.", row=number))
            elif len(values) != len(headers):
                errors.append(error("ragged_row", f"Expected {len(headers)} fields; got {len(values)}.", row=number))
            else:
                row = dict(zip(headers, values))
                row.setdefault("adgroup_name", "")
                rows.append(row)
    except csv.Error as exc:
        errors.append(error("csv_syntax", str(exc), row=reader.line_num))
    if not rows:
        errors.append(error("empty", "At least one ad row is required."))
    if errors:
        raise CsvProblem(errors)
    return rows, hashlib.sha256(raw).hexdigest(), raw.startswith(b"\xef\xbb\xbf")


def https_url(value):
    if not value or any(ch.isspace() or ord(ch) < 32 for ch in value):
        return False
    try:
        parts = urlsplit(value)
        # Checking .port also rejects malformed ports; no remote request is made.
        _ = parts.port
        return parts.scheme == "https" and bool(parts.hostname) and not parts.username and not parts.password
    except ValueError:
        return False


def check_rows(rows, mode, *, allow_non_paused_creates=False):
    errors, seen_ids, seen_keys = [], set(), set()
    counts = {"rows": len(rows), "creates": 0, "updates": 0, "groups": len({r["ad_group_id"] for r in rows})}
    for number, row in enumerate(rows, 2):
        has_id = bool(row["ad_id"])
        counts["updates" if has_id else "creates"] += 1
        for field in ("ad_group_id", "ad_name", "title", "copy", "link", "status"):
            if not row[field].strip():
                errors.append(error("required", "A nonblank value is required.", row=number, field=field))
        for field, pattern in ID_PATTERNS.items():
            value = row[field]
            if value and not pattern.fullmatch(value):
                errors.append(error("id_format", "ID must have the native prefix and an alphanumeric suffix.", row=number, field=field))
        if row["ad_id"]:
            if row["ad_id"] in seen_ids:
                errors.append(error("duplicate_id", "Repeated nonblank ad_id.", row=number, field="ad_id"))
            seen_ids.add(row["ad_id"])
        key = (row["ad_group_id"], row["ad_name"])
        if key in seen_keys:
            errors.append(error("duplicate_key", "Repeated (ad_group_id, ad_name); do not select a row implicitly.", row=number))
        seen_keys.add(key)
        if mode == "create" and has_id:
            errors.append(error("mode", "Create mode requires every ad_id to be blank.", row=number, field="ad_id"))
        if mode == "update" and not has_id:
            errors.append(error("mode", "Update mode requires every ad_id to be populated.", row=number, field="ad_id"))
        if not has_id and row["status"] != "paused" and not allow_non_paused_creates:
            errors.append(error("create_status", "New ads must explicitly use status=paused unless overridden.", row=number, field="status"))
        if not 3 <= len(row["title"]) <= 50:
            errors.append(error("title_length", "Title must be 3–50 characters.", row=number, field="title"))
        if len(row["copy"]) > 100:
            errors.append(error("copy_length", "Copy must be at most 100 characters.", row=number, field="copy"))
        for field in ("link", "image_url"):
            if (field == "link" or row[field]) and not https_url(row[field]):
                errors.append(error("https_url", "A valid HTTPS URL without whitespace or embedded credentials is required.", row=number, field=field))
        if not row["image_file_id"] and not row["image_url"]:
            errors.append(error("image", "Supply an existing image_file_id or an HTTPS image_url.", row=number))
    return counts, errors


def exclusions(filename):
    """Read an old export/prepared CSV or a JSON array of IDs/mapping records."""
    if filename is None:
        return set(), {}
    path = Path(filename)
    if path.suffix.lower() == ".csv":
        rows, _, _ = read_csv(path, native=True)
        ids = [row["ad_id"] for row in rows]
        keyed = {(row["ad_group_id"], row["ad_name"]): row["ad_id"] for row in rows}
        if len(keyed) != len(rows):
            raise CsvProblem([error("original_ids", "Original CSV has ambiguous group/name keys.")])
    else:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        if not isinstance(data, list):
            raise CsvProblem([error("original_ids", "Original ID JSON must be an array of IDs or mapping records.")])
        ids, keyed = [], {}
        for item in data:
            if isinstance(item, str):
                ids.append(item)
            elif isinstance(item, dict):
                ad_id = item.get("old_draft_id", item.get("original_ad_id", item.get("ad_id")))
                ids.append(ad_id)
                group = item.get("group_id", item.get("ad_group_id"))
                if group and item.get("ad_name"):
                    if not isinstance(group, str) or not isinstance(item["ad_name"], str):
                        raise CsvProblem([error("original_ids", "Original group/name keys must be strings.")])
                    key = (group, item["ad_name"])
                    if key in keyed:
                        raise CsvProblem([error("original_ids", "Original mapping has ambiguous group/name keys.")])
                    keyed[key] = ad_id
            else:
                raise CsvProblem([error("original_ids", "Each original ID entry must be a string or mapping object.")])
    if any(not isinstance(value, str) or not ID_PATTERNS["ad_id"].fullmatch(value) for value in ids):
        raise CsvProblem([error("original_ids", "Every excluded original ID must be a nonblank native ad_id.")])
    if len(set(ids)) != len(ids):
        raise CsvProblem([error("original_ids", "Original IDs must be unique.")])
    return set(ids), keyed


def check_destinations(paths, inputs, force):
    resolved = [Path(path).resolve() for path in paths]
    # Reject case/Unicode aliases conservatively even before files exist. This
    # keeps outputs portable between case-sensitive disks and default macOS.
    names = {unicodedata.normalize("NFC", str(path)).casefold() for path in resolved}
    same_existing_file = any(
        a.exists() and b.exists() and a.samefile(b)
        for index, a in enumerate(resolved) for b in resolved[index + 1:]
    )
    if len(names) != len(resolved) or same_existing_file:
        raise CsvProblem([error("output_collision", "CSV and mapping outputs must be distinct, including case/Unicode aliases.")])
    for path in resolved:
        if path in inputs or (path.exists() and any(path.samefile(source) for source in inputs)):
            raise CsvProblem([error("input_overwrite", "Input/evidence files are never overwritten, including with --force.")])
        if path.exists() and not path.is_file():
            raise CsvProblem([error("output_type", f"Output must be a regular file, not a directory or device: {path}.")])
        if path.exists() and not force:
            raise CsvProblem([error("output_exists", f"Output exists: {path}. Use --force to replace an output.")])
        if not path.parent.is_dir():
            raise CsvProblem([error("output_directory", f"Output directory does not exist: {path.parent}.")])
    return resolved


def atomic_write(path, raw, force):
    """Create without a clobber race, or atomically replace an explicit output."""
    fd, temp = tempfile.mkstemp(prefix="." + path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
        if force:
            os.replace(temp, path)
        else:
            os.link(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def reconcile(args):
    rows, prepared_hash, bom = read_csv(args.prepared)
    native, native_hash, _ = read_csv(args.native_export, native=True)
    counts, errors = check_rows(rows, "mixed", allow_non_paused_creates=args.allow_non_paused_creates)
    _, native_errors = check_rows(native, "update", allow_non_paused_creates=True)
    errors += [dict(item, source="native_export") for item in native_errors]
    excluded, originals = exclusions(args.exclude_original_ids)
    by_key = {(r["ad_group_id"], r["ad_name"]): r for r in native}
    expected = {(r["ad_group_id"], r["ad_name"]) for r in rows}
    actual = set(by_key)
    for key in sorted(expected - actual):
        errors.append(error("missing_export_row", f"Native export is missing group/name {key!r}."))
    for key in sorted(actual - expected):
        errors.append(error("extra_export_row", f"Native export has extra group/name {key!r}; scope the export first."))
    mapping, output_rows = [], []
    for number, row in enumerate(rows, 2):
        key = (row["ad_group_id"], row["ad_name"])
        found = by_key.get(key)
        if found is None:
            continue
        if found["ad_id"] in excluded:
            errors.append(error("excluded_original_id", "Native export still contains an excluded original ad ID.", row=number, field="ad_id"))
        for field in CREATIVE_FIELDS:
            if row[field] != found[field]:
                errors.append(error("field_mismatch", "Prepared and native-export values differ; nothing was reconciled.", row=number, field=field))
        original = row["ad_id"] or originals.get(key, "")
        if row["ad_id"] and originals.get(key) and row["ad_id"] != originals[key]:
            errors.append(error("original_mapping", "Prepared ID conflicts with the original mapping for this group/name.", row=number, field="ad_id"))
        mapping.append({"ad_group_id": key[0], "ad_name": key[1], "original_ad_id": original, "new_ad_id": found["ad_id"]})
        output_rows.append(dict(row, ad_id=found["ad_id"]))
    if errors:
        raise CsvProblem(errors)
    sources = {Path(args.prepared).resolve(), Path(args.native_export).resolve()}
    if args.exclude_original_ids:
        sources.add(Path(args.exclude_original_ids).resolve())
    paths = [args.output] + ([args.map_output] if args.map_output else [])
    destinations = check_destinations(paths, sources, args.force)
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=HEADERS, lineterminator="\r\n")
    writer.writeheader()
    writer.writerows(output_rows)
    raw = stream.getvalue().encode("utf-8-sig" if bom else "utf-8")
    if args.map_output:
        atomic_write(destinations[1], (json.dumps(mapping, indent=2, ensure_ascii=False) + "\n").encode("utf-8"), args.force)
    atomic_write(destinations[0], raw, args.force)
    return {
        "ok": True, "command": "reconcile", "counts": dict(counts, creates=0, updates=len(rows)),
        "prepared_sha256": prepared_hash, "native_export_sha256": native_hash,
        "output_sha256": hashlib.sha256(raw).hexdigest(), "output": str(destinations[0]),
        "map_output": str(destinations[1]) if args.map_output else None,
        "changed_fields": ["ad_id"], "other_field_values_preserved": True,
        "excluded_original_ids": len(excluded), "errors": [],
        "account_state_verified": False,
    }


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    sub = result.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate", help="Check a ten-column upload CSV without changing it.")
    validate.add_argument("csv")
    validate.add_argument("--mode", required=True, choices=("create", "update", "mixed"))
    validate.add_argument("--allow-non-paused-creates", action="store_true", help="Explicitly bypass the paused-only create safeguard; does not establish platform acceptance.")
    rec = sub.add_parser("reconcile", help="Fill actual ad IDs from a strictly matching native export.")
    rec.add_argument("prepared")
    rec.add_argument("native_export")
    rec.add_argument("output")
    rec.add_argument("--exclude-original-ids", metavar="FILE", help="Old CSV or JSON IDs/mappings; any exported original ID is rejected, never filtered out.")
    rec.add_argument("--map-output", metavar="JSON")
    rec.add_argument("--force", action="store_true", help="Replace existing output files, never input/evidence files.")
    rec.add_argument("--allow-non-paused-creates", action="store_true")
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    validation_metadata = {}
    try:
        if args.command == "validate":
            raw = Path(args.csv).read_bytes()
            validation_metadata = {
                "mode": args.mode, "sha256": hashlib.sha256(raw).hexdigest(),
                "utf8_bom": raw.startswith(b"\xef\xbb\xbf"),
                "counts": {"rows": None, "creates": None, "updates": None, "groups": None},
                "account_state_verified": False,
            }
            rows, sha256, bom = read_csv(args.csv)
            counts, errors = check_rows(rows, args.mode, allow_non_paused_creates=args.allow_non_paused_creates)
            report = {"ok": not errors, "command": "validate", "mode": args.mode, "counts": counts, "sha256": sha256, "utf8_bom": bom, "errors": errors, "account_state_verified": False}
        else:
            report = reconcile(args)
    except CsvProblem as exc:
        report = {"ok": False, "command": args.command, **validation_metadata, "errors": exc.errors}
    except (OSError, ValueError) as exc:
        report = {"ok": False, "command": args.command, **validation_metadata, "errors": [error("file_error", str(exc))]}
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
