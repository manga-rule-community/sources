import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_mirror_release import fixtures, m

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import generate_source_directory as d


class SourceDirectoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.catalog = self.root / "catalog"
        self.output = self.root / "directory"
        files, _ = fixtures()
        m.prepare(self.catalog, lambda url, limit: files[url])
        self.all = json.loads((self.catalog / "all.json").read_text())
        self.general = json.loads((self.catalog / "general.json").read_text())

    def tearDown(self):
        self.temp.cleanup()

    def save(self):
        m.write_json(self.catalog / "all.json", self.all)
        m.write_json(self.catalog / "general.json", self.general)

    def repartition(self):
        self.all["count"] = len(self.all["rules"])
        self.general["rules"] = copy.deepcopy([r for r in self.all["rules"] if r["contentRating"] != "adult"])
        self.general["count"] = len(self.general["rules"])
        self.save()

    def documents(self):
        return d.generate_documents(self.catalog)

    def test_stable_import_and_immutable_download_links(self):
        general = self.documents()[d.GENERAL_PATH]
        self.assertIn("[导入链接](https://github.com/manga-rule-community/sources/releases/latest/download/sample.kyyrule)", general)
        self.assertIn(f"[下载该版本]({self.general['rules'][0]['url']})", general)
        self.assertIn("`rules-test-39`", general)
        self.assertIn("`39`", general)
        self.assertIn("不代表安装后会自动更新", general)
        self.assertIn("不代表能一键唤起 App 安装", general)
        self.assertNotIn("kiokuyomi://", general)

    def test_adult_sources_only_in_separate_directory(self):
        documents = self.documents()
        general, adult = documents[d.GENERAL_PATH], documents[d.ADULT_PATH]
        self.assertNotIn("restricted", general)
        self.assertIn("restricted.kyyrule", adult)
        self.assertNotIn("sample.kyyrule", adult)
        self.assertIn("本页共 1 个常规来源", general)
        self.assertIn("本页共 1 个成人来源", adult)
        self.assertIn("另有 1 个成人来源", general)
        self.assertIn("适用年龄", adult)

    def test_teen_and_mature_remain_in_general_directory(self):
        for rating in ("teen", "mature"):
            rule = copy.deepcopy(self.all["rules"][0])
            rule.update(id=rating, name=rating, contentRating=rating,
                        url=f"{d.RELEASE_BASE}/download/{self.all['releaseId']}/{rating}.kyyrule")
            self.all["rules"].append(rule)
        self.repartition()
        general = self.documents()[d.GENERAL_PATH]
        self.assertIn("本页共 3 个常规来源", general)
        for rating in ("safe", "teen", "mature"):
            self.assertIn(d.RATINGS[rating], general)
        self.assertNotIn(d.RATINGS["adult"], general)

    def test_removal_clears_old_entries_and_empty_adult_directory(self):
        d.generate(self.catalog, self.output)
        self.all["rules"] = self.all["rules"][:1]
        self.repartition()
        d.generate(self.catalog, self.output)
        adult = (self.output / d.ADULT_PATH).read_text()
        self.assertNotIn("restricted", adult)
        self.assertIn("本页共 0 个成人来源", adult)
        self.assertIn("当前没有此分组的已发布来源", adult)
        self.assertTrue(d.generate(self.catalog, self.output, check=True))

    def test_deterministic_sorting_and_duplicate_display_names(self):
        for rule_id, name in (("z-last", "zulu"), ("a-first", "Alpha"), ("b-second", "Alpha")):
            rule = copy.deepcopy(self.all["rules"][0])
            rule.update(id=rule_id, name=name,
                        url=f"{d.RELEASE_BASE}/download/{self.all['releaseId']}/{rule_id}.kyyrule")
            self.all["rules"].append(rule)
        self.repartition()
        before = self.documents()
        text = before[d.GENERAL_PATH]
        self.assertLess(text.index("`a-first`"), text.index("`b-second`"))
        self.assertLess(text.index("`b-second`"), text.index("`sample`"))
        self.assertLess(text.index("`sample`"), text.index("`z-last`"))
        self.all["rules"].reverse()
        self.repartition()
        self.assertEqual(self.documents(), before)

    def test_external_names_cannot_inject_markdown_or_html(self):
        name = '雪 & <script>alert(1)</script>\n[x](https://evil.invalid) | `x` **bold** \\ _x_'
        self.all["rules"][0]["name"] = name
        self.repartition()
        general = self.documents()[d.GENERAL_PATH]
        row = next(line for line in general.splitlines() if "`sample`" in line)
        self.assertIn("雪 &amp; &lt;script&gt;", row)
        self.assertIn(r"\[x\]\(https://evil.invalid\)", row)
        self.assertIn(r"\| \`x\` \*\*bold\*\*", row)
        self.assertNotIn("<script>", general)
        self.assertNotIn("[x](https://evil.invalid)", general)
        self.assertEqual(row.count("|") - row.count(r"\|"), 6)

    def test_unknown_or_sensitive_fields_are_not_rendered(self):
        for target in ("root", "rule"):
            for key in ("token", "privateKey", "javascript", "unexpected"):
                all_collection = copy.deepcopy(self.all)
                selected = all_collection if target == "root" else all_collection["rules"][0]
                selected[key] = "must-not-leak"
                m.write_json(self.catalog / "all.json", all_collection)
                with self.subTest(target=target, key=key), self.assertRaises(d.MirrorError):
                    self.documents()

    def test_rejects_untrusted_or_mutable_package_url(self):
        for url in ("https://evil.invalid/sample.kyyrule",
                    f"{d.RELEASE_BASE}/latest/download/sample.kyyrule",
                    self.all["rules"][0]["url"] + "?token=secret"):
            self.all["rules"][0]["url"] = url
            self.save()
            with self.subTest(url=url), self.assertRaises(d.MirrorError):
                self.documents()

    def test_rejects_version_sequence_or_subset_mismatch(self):
        for field, value in (("catalogSequence", 40), ("releaseId", "other-release")):
            bad = copy.deepcopy(self.general)
            bad[field] = value
            m.write_json(self.catalog / "general.json", bad)
            with self.subTest(field=field), self.assertRaises(d.MirrorError):
                self.documents()
        self.general["rules"][0]["name"] = "inconsistent"
        self.save()
        with self.assertRaises(d.MirrorError):
            self.documents()

    def test_rejects_invalid_id_rating_and_count(self):
        for field, value in (("id", "../escape"), ("id", "sample|bad"), ("contentRating", "unknown")):
            bad = copy.deepcopy(self.all)
            bad["rules"][0][field] = value
            m.write_json(self.catalog / "all.json", bad)
            with self.subTest(field=field, value=value), self.assertRaises(d.MirrorError):
                self.documents()
        self.all["count"] += 1
        self.save()
        with self.assertRaises(d.MirrorError):
            self.documents()

    def test_invalid_inputs_leave_existing_documents_untouched(self):
        d.generate(self.catalog, self.output)
        before = {path: (self.output / path).read_bytes() for path in (d.GENERAL_PATH, d.ADULT_PATH)}
        for raw in (b'{"kind":"a","kind":"b"}', b'not-json', b'[]', b'\xff'):
            (self.catalog / "general.json").write_bytes(raw)
            with self.subTest(raw=raw), self.assertRaises(d.MirrorError):
                d.generate(self.catalog, self.output)
            self.assertEqual(before, {path: (self.output / path).read_bytes() for path in before})

    def test_check_detects_missing_or_stale_files_without_writing(self):
        self.assertFalse(d.generate(self.catalog, self.output, check=True))
        self.assertFalse(self.output.exists())
        d.generate(self.catalog, self.output)
        self.assertTrue(d.generate(self.catalog, self.output, check=True))
        for path in (d.GENERAL_PATH, d.ADULT_PATH):
            target = self.output / path
            target.write_text("manual edit\n")
            self.assertFalse(d.generate(self.catalog, self.output, check=True))
            self.assertEqual(target.read_text(), "manual edit\n")
            d.generate(self.catalog, self.output)

    def test_generation_preserves_every_catalog_and_release_asset(self):
        before = {path.name: path.read_bytes() for path in self.catalog.iterdir()}
        d.generate(self.catalog, self.catalog)
        self.assertEqual(before, {name: (self.catalog / name).read_bytes() for name in before})
        self.assertNotIn("SOURCES.md", m.expected_assets(self.catalog))
        self.assertNotIn("docs/SOURCES_ADULT.md", m.expected_assets(self.catalog))

    def test_navigation_links_resolve_with_repo_relative_paths(self):
        documents = self.documents()
        self.assertIn("[返回 README](README.md)", documents[d.GENERAL_PATH])
        self.assertIn("[成人来源单独目录](docs/SOURCES_ADULT.md)", documents[d.GENERAL_PATH])
        self.assertIn("[返回常规目录](../SOURCES.md)", documents[d.ADULT_PATH])
        self.assertIn("[返回 README](../README.md)", documents[d.ADULT_PATH])

    def test_cli_check_exit_status_and_explicit_preview_directory(self):
        command = [sys.executable, str(ROOT / "scripts/generate_source_directory.py"),
                   "--catalog-dir", str(self.catalog), "--output-dir", str(self.output)]
        result = subprocess.run(command + ["--check"], capture_output=True, text=True, cwd=self.root)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertFalse(self.output.exists())
        for flags in ([], ["--check"]):
            result = subprocess.run(command + flags, capture_output=True, text=True, cwd=self.root)
            self.assertEqual(result.returncode, 0, result.stderr)
        (self.catalog / "general.json").unlink()
        result = subprocess.run(command, capture_output=True, text=True, cwd=self.root)
        self.assertEqual(result.returncode, 1)
        self.assertNotIn("Traceback", result.stderr)

    def test_sync_generates_after_publish_and_stages_directories_with_metadata(self):
        workflow = (ROOT / ".github/workflows/sync-release.yml").read_text()
        generate = "python3 scripts/generate_source_directory.py --catalog-dir dist"
        stage = "git add -- all.json general.json sources.json publication.json SOURCES.md docs/SOURCES_ADULT.md"
        self.assertLess(workflow.index("--output dist --publish"), workflow.index(generate))
        self.assertLess(workflow.index(generate), workflow.index('cp "dist/$file" "$file"'))
        self.assertLess(workflow.index('cp "dist/$file" "$file"'), workflow.rindex("generate_source_directory.py --check"))
        self.assertLess(workflow.rindex("generate_source_directory.py --check"), workflow.index(stage))
        self.assertLess(workflow.index(stage), workflow.index("git push origin HEAD:main"))


if __name__ == "__main__":
    unittest.main()
