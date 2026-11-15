"""Meaningful local import-safety checks; no network or account writes."""

import csv
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import ad_csv


def ad(number=1, **changes):
    row = dict(zip(ad_csv.HEADERS, [
        f"ad_{number:032x}", "adgrp_" + "a" * 32, "Optional group label", f"Ad {number}",
        "paused", "Learn useful workflows", "Practical lessons, with examples.",
        "https://example.com/learn?source=chatgpt", "", "file_" + f"{number:032x}",
    ]))
    row.update(changes)
    return row


class CsvTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)

    def tearDown(self):
        self.directory.cleanup()

    def write(self, name, rows, headers=None, bom=False):
        path = self.root / name
        with path.open("w", encoding="utf-8-sig" if bom else "utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=headers or ad_csv.HEADERS, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
        return path

    def cli(self, *args, ok=True):
        process = subprocess.run([sys.executable, str(Path(ad_csv.__file__)), *map(str, args)], capture_output=True, text=True)
        result = json.loads(process.stdout)
        self.assertEqual(process.returncode, 0 if ok else 1, process.stdout + process.stderr)
        self.assertEqual(result["ok"], ok)
        return result

    def validate(self, rows, mode="update", ok=True, **kwargs):
        path = self.write("input.csv", rows, **kwargs)
        return self.cli("validate", path, "--mode", mode, ok=ok)

    def reconcile(self, prepared, native, *options, ok=True, native_headers=None):
        before = self.write("prepared.csv", prepared, bom=True)
        export = self.write("native.csv", native, headers=native_headers or ad_csv.NATIVE_HEADERS)
        output = self.root / "output.csv"
        result = self.cli("reconcile", before, export, output, *options, ok=ok)
        return output, result

    def test_valid_update_bom_hash_and_optional_group_label(self):
        result = self.validate([ad(adgroup_name="")], bom=True)
        self.assertEqual(result["counts"], {"rows": 1, "creates": 0, "updates": 1, "groups": 1})
        self.assertTrue(result["utf8_bom"])
        self.assertEqual(result["sha256"], hashlib.sha256((self.root / "input.csv").read_bytes()).hexdigest())

    def test_quotes_commas_newlines_and_unicode_preserved(self):
        row = ad(ad_id="", ad_name='Angle, "workflow"\nsecond line', title='Learn "AI", step by step', copy="First line\nNext: café, not a promise.")
        self.validate([row], mode="create")
        output, _ = self.reconcile([row], [dict(row, ad_id="ad_" + "b" * 32)])
        result, _, _ = ad_csv.read_csv(output)
        self.assertEqual({k: v for k, v in result[0].items() if k != "ad_id"}, {k: v for k, v in row.items() if k != "ad_id"})
        self.assertTrue(output.read_bytes().startswith(b"\xef\xbb\xbf"))

    def test_modes_and_paused_creation_explicit(self):
        self.validate([ad(ad_id="")], mode="create")
        self.validate([ad()], mode="create", ok=False)
        self.validate([ad(ad_id="")], mode="update", ok=False)
        self.validate([ad(), ad(2, ad_id="")], mode="mixed")
        result = self.validate([ad(ad_id="", status="active")], mode="create", ok=False)
        self.assertIn("create_status", [e["code"] for e in result["errors"]])
        self.cli("validate", self.root / "input.csv", "--mode", "create", "--allow-non-paused-creates")
        self.validate([ad(ad_id="", status="")], mode="create", ok=False)

    def test_duplicate_id_and_group_name_key(self):
        self.validate([ad(), ad(2, ad_id=ad()["ad_id"])], ok=False)
        self.validate([ad(), ad(2, ad_name="Ad 1")], ok=False)
        self.validate([ad(), ad(2, ad_name="Ad 1", ad_group_id="adgrp_" + "b" * 32)])

    def test_header_order_extra_missing_and_duplicates_fail(self):
        variants = [ad_csv.HEADERS[1:] + ad_csv.HEADERS[:1], ad_csv.HEADERS + ["other"], ad_csv.NATIVE_HEADERS, ad_csv.HEADERS[:-1] + ["image_url"]]
        for headers in variants:
            with self.subTest(headers=headers):
                result = self.validate([ad()], headers=headers, ok=False)
                self.assertEqual(result["errors"][0]["code"], "headers")

    def test_blank_ragged_bad_quotes_and_encoding_fail(self):
        header = ",".join(ad_csv.HEADERS) + "\n"
        for raw in [(header + "\n").encode(), (header + "one,two\n").encode(), (header + '"unterminated\n').encode(), b"\xff"]:
            with self.subTest(raw=raw):
                path = self.root / "malformed.csv"
                path.write_bytes(raw)
                self.cli("validate", path, "--mode", "mixed", ok=False)

    def test_required_length_ids_https_and_images(self):
        bad = [dict(title="ab"), dict(title="x" * 51), dict(copy="x" * 101), dict(ad_group_id=""), dict(ad_name=" "), dict(copy=""), dict(ad_id="123"), dict(ad_group_id="campaign_abc"), dict(image_file_id="image_123"), dict(link="http://example.com"), dict(link="https://"), dict(link="https://example.com/a b"), dict(image_file_id="", image_url=""), dict(image_file_id="", image_url="file:///tmp/a.png")]
        for changes in bad:
            with self.subTest(changes=changes):
                self.validate([ad(**changes)], ok=False)
        self.validate([ad(title="abc", copy="x" * 100, image_file_id="", image_url="https://example.com/image.png")])

    def test_reconcile_complete_set_reorders_by_key_changes_only_ids(self):
        rows = [ad(1), ad(2, adgroup_name="", ad_group_id="adgrp_" + "b" * 32)]
        native = [dict(rows[1], ad_id="ad_" + "d" * 32), dict(rows[0], ad_id="ad_" + "c" * 32)]
        mapping = self.root / "map.json"
        originals = self.write("originals.csv", rows)
        output, result = self.reconcile(rows, native, "--exclude-original-ids", originals, "--map-output", mapping)
        actual, _, _ = ad_csv.read_csv(output)
        self.assertEqual(actual, [dict(rows[0], ad_id=native[1]["ad_id"]), dict(rows[1], ad_id=native[0]["ad_id"])])
        self.assertEqual(json.loads(mapping.read_text())[0]["original_ad_id"], rows[0]["ad_id"])
        self.assertEqual(result["counts"]["updates"], 2)
        self.assertEqual(result["excluded_original_ids"], 2)

    def test_reconcile_native_ten_headers_and_optional_metadata(self):
        row = ad()
        output, _ = self.reconcile([row], [dict(row, ad_id="ad_new123", adgroup_name="")], native_headers=ad_csv.HEADERS)
        self.assertEqual(ad_csv.read_csv(output)[0][0]["adgroup_name"], row["adgroup_name"])

    def test_reconcile_old_plus_new_duplicate_rejected_even_with_exclusion(self):
        old = ad()
        new = dict(old, ad_id="ad_" + "b" * 32)
        exclude = self.root / "old.json"
        exclude.write_text(json.dumps([old["ad_id"]]))
        output, result = self.reconcile([old], [old, new], "--exclude-original-ids", exclude, ok=False)
        self.assertFalse(output.exists())
        self.assertIn("duplicate_key", [e["code"] for e in result["errors"]])

    def test_reconcile_partial_extra_export_and_duplicate_prepared_fail(self):
        for prepared, native in [([ad(), ad(2)], [ad()]), ([ad()], [ad(), ad(2)]), ([ad(), ad()], [ad()])]:
            with self.subTest(prepared=prepared, native=native):
                output, _ = self.reconcile(prepared, native, ok=False)
                self.assertFalse(output.exists())

    def test_every_shared_creative_status_image_mismatch_blocks_output(self):
        changed = {"status": "active", "title": "Another valid title", "copy": "Other copy", "link": "https://example.com/other", "image_url": "https://example.com/image.png", "image_file_id": "file_" + "f" * 32}
        for field, value in changed.items():
            with self.subTest(field=field):
                output, result = self.reconcile([ad()], [ad(**{field: value})], ok=False)
                self.assertFalse(output.exists())
                self.assertIn(field, [e.get("field") for e in result["errors"] if e["code"] == "field_mismatch"])

    def test_excluded_original_cannot_be_reused(self):
        excluded = self.root / "ids.json"
        excluded.write_text(json.dumps([ad()["ad_id"]]))
        output, result = self.reconcile([ad()], [ad()], "--exclude-original-ids", excluded, ok=False)
        self.assertFalse(output.exists())
        self.assertIn("excluded_original_id", [e["code"] for e in result["errors"]])

    def test_json_original_mapping_recovers_blank_prepared_id(self):
        original = ad()
        excluded = self.root / "mapping.json"
        excluded.write_text(json.dumps([{"ad_name": original["ad_name"], "group_id": original["ad_group_id"], "old_draft_id": original["ad_id"]}]))
        mapping = self.root / "result-map.json"
        self.reconcile([dict(original, ad_id="")], [dict(original, ad_id="ad_new123")], "--exclude-original-ids", excluded, "--map-output", mapping)
        self.assertEqual(json.loads(mapping.read_text())[0]["original_ad_id"], original["ad_id"])

    def test_outputs_require_force_and_inputs_never_overwritten(self):
        prepared = self.write("prepared.csv", [ad()])
        native = self.write("native.csv", [ad(ad_id="ad_new123")], headers=ad_csv.NATIVE_HEADERS)
        original_bytes = prepared.read_bytes(), native.read_bytes()
        output = self.root / "output.csv"
        output.write_text("keep me")
        self.cli("reconcile", prepared, native, output, ok=False)
        self.assertEqual(output.read_text(), "keep me")
        self.cli("reconcile", prepared, native, output, "--force")
        for protected in (prepared, native):
            self.cli("reconcile", prepared, native, protected, "--force", ok=False)
        self.assertEqual(original_bytes, (prepared.read_bytes(), native.read_bytes()))

    def test_map_collision_and_existing_map_block_csv(self):
        prepared = self.write("prepared.csv", [ad()])
        native = self.write("native.csv", [ad(ad_id="ad_new123")])
        output = self.root / "output.csv"
        self.cli("reconcile", prepared, native, output, "--map-output", output, ok=False)
        mapping = self.root / "map.json"
        mapping.write_text("keep")
        self.cli("reconcile", prepared, native, output, "--map-output", mapping, ok=False)
        self.assertFalse(output.exists())
        self.assertEqual(mapping.read_text(), "keep")

    def test_output_case_alias_and_hardlink_alias_cannot_overwrite_mapping(self):
        prepared = self.write("prepared.csv", [ad()])
        native = self.write("native.csv", [ad(ad_id="ad_new123")])
        output = self.root / "results.csv"
        alias = self.root / "RESULTS.csv"
        self.cli("reconcile", prepared, native, output, "--map-output", alias, "--force", ok=False)
        self.assertFalse(output.exists())
        output.write_text("keep")
        hardlink = self.root / "separate-name.json"
        os.link(output, hardlink)
        self.cli("reconcile", prepared, native, output, "--map-output", hardlink, "--force", ok=False)
        self.assertEqual(output.read_text(), "keep")
        self.assertEqual(hardlink.read_text(), "keep")

    def test_directory_output_is_rejected_before_mapping_write(self):
        prepared = self.write("prepared.csv", [ad()])
        native = self.write("native.csv", [ad(ad_id="ad_new123")])
        directory = self.root / "output-directory"
        directory.mkdir()
        mapping = self.root / "map.json"
        result = self.cli("reconcile", prepared, native, directory, "--map-output", mapping, "--force", ok=False)
        self.assertIn("output_type", [e["code"] for e in result["errors"]])
        self.assertFalse(mapping.exists())


if __name__ == "__main__":
    unittest.main()
