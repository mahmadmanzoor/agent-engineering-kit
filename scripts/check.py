#!/usr/bin/env python3
"""Checks for agent-engineering-kit. Standard library only.

    python3 scripts/check.py            run every check
    python3 scripts/check.py links      run one check

Checks
  manifests  marketplace.json and each plugin.json parse, match folders, names and versions
  skills     SKILL.md frontmatter (name = folder, description <= 1024, license, metadata.version/model/effort)
             and, for engineering plugins, the required sections from docs/skill-format.md
  agents     agent files have name, description and model
  links      relative Markdown links point at real files
  stack      no framework/language/vendor names in engineering SKILL.md files
  privacy    no home paths, emails, or key-shaped strings anywhere
Exit code 1 if anything fails.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGINS = ROOT / "plugins"
ENGINEERING = {"ship", "check", "server", "web", "mobile", "kit"}
SECTIONS = ("**Run on:**", "## Use it when", "## Before you start", "## Steps", "## Done when", "## Never", "## Next")
MODELS = {"haiku", "sonnet", "opus", "fable"}
EFFORTS = {"low", "medium", "high"}
SKIP_DIRS = {".git", "node_modules", "library"}

problems: list[str] = []


def bad(msg: str) -> None:
    problems.append(msg)


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def walk(pattern: str):
    for p in ROOT.rglob(pattern):
        if not SKIP_DIRS.intersection(p.relative_to(ROOT).parts):
            yield p


def frontmatter(path: Path) -> tuple[dict, str] | None:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    if not m:
        bad(f"{rel(path)}: no frontmatter block")
        return None
    data: dict = {}
    parent = None
    for line in m.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indented = line.startswith((" ", "\t"))
        key, _, value = line.strip().partition(":")
        value = value.split(" #")[0].strip().strip('"').strip("'")
        if indented and parent is not None:
            data[parent][key] = value
        elif value == "":
            parent = key
            data[key] = {}
        else:
            parent = None
            data[key] = value
    return data, m.group(2)


def check_manifests() -> None:
    try:
        market = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
    except Exception as e:  # noqa: BLE001
        bad(f"marketplace.json: {e}")
        return
    listed = {p["name"]: p for p in market.get("plugins", [])}
    on_disk = {p.name for p in PLUGINS.iterdir() if p.is_dir()}
    for name in sorted(on_disk ^ set(listed)):
        bad(f"plugin '{name}' is on disk or in marketplace.json, not both")
    for name in sorted(on_disk & set(listed)):
        try:
            pj = json.loads((PLUGINS / name / ".claude-plugin/plugin.json").read_text())
        except Exception as e:  # noqa: BLE001
            bad(f"plugins/{name}/.claude-plugin/plugin.json: {e}")
            continue
        if pj.get("name") != name:
            bad(f"plugins/{name}: plugin.json name is '{pj.get('name')}'")
        if pj.get("version") != listed[name].get("version"):
            bad(f"plugins/{name}: version differs from marketplace.json")
        for dep in pj.get("dependencies", []):
            if dep not in on_disk:
                bad(f"plugins/{name}: depends on missing plugin '{dep}'")


def plugin_version(plugin: str) -> str | None:
    try:
        return json.loads((PLUGINS / plugin / ".claude-plugin/plugin.json").read_text()).get("version")
    except Exception:  # noqa: BLE001
        return None


def check_skills() -> None:
    for path in sorted(walk("SKILL.md")):
        parts = path.relative_to(PLUGINS).parts  # <plugin>/skills/<name>/SKILL.md
        if len(parts) != 4 or parts[1] != "skills":
            continue
        plugin, folder = parts[0], parts[2]
        parsed = frontmatter(path)
        if not parsed:
            continue
        fm, body = parsed
        where = rel(path)
        name = fm.get("name", "")
        if name != folder:
            bad(f"{where}: name '{name}' does not match folder '{folder}'")
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) or len(name) > 64:
            bad(f"{where}: name must be kebab-case, max 64 chars")
        desc = fm.get("description", "")
        if not desc or len(desc) > 1024:
            bad(f"{where}: description missing or over 1024 chars ({len(desc)})")
        if fm.get("license") != "MIT":
            bad(f"{where}: license must be MIT")
        meta = fm.get("metadata") if isinstance(fm.get("metadata"), dict) else {}
        if meta.get("version") != plugin_version(plugin):
            bad(f"{where}: metadata.version must equal the plugin version")
        if meta.get("model") not in MODELS:
            bad(f"{where}: metadata.model must be one of {sorted(MODELS)}")
        if meta.get("effort") not in EFFORTS:
            bad(f"{where}: metadata.effort must be one of {sorted(EFFORTS)}")
        if plugin in ENGINEERING:
            for s in SECTIONS:
                if s not in body:
                    bad(f"{where}: missing section '{s}'")


def check_agents() -> None:
    for path in sorted(walk("*.md")):
        if path.parent.name != "agents" or "plugins" not in path.parts:
            continue
        parsed = frontmatter(path)
        if parsed:
            fm = parsed[0]
            for key in ("name", "description", "model"):
                if not fm.get(key):
                    bad(f"{rel(path)}: agent frontmatter needs '{key}'")
            if fm.get("name") and fm["name"] != path.stem:
                bad(f"{rel(path)}: agent name must equal the file name")


LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")


def check_links() -> None:
    for path in sorted(walk("*.md")):
        text = re.sub(r"```.*?```", "", path.read_text(encoding="utf-8"), flags=re.S)
        text = re.sub(r"`[^`\n]*`", "", text)
        for target in LINK.findall(text):
            if re.match(r"[a-z]+:|#|/", target):
                continue
            file = (path.parent / target.split("#")[0]).resolve()
            if not file.exists():
                bad(f"{rel(path)}: broken link '{target}'")


def check_stack() -> None:
    terms = [t.strip() for t in (ROOT / "scripts/framework-terms.txt").read_text().splitlines()
             if t.strip() and not t.startswith("#")]
    pats = [(t, re.compile(r"(?<![\w.#-])" + re.escape(t) + r"(?![\w#+-])")) for t in terms]
    for plugin in sorted(ENGINEERING):
        for path in sorted((PLUGINS / plugin).rglob("SKILL.md")):
            for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                for term, pat in pats:
                    if pat.search(line):
                        bad(f"{rel(path)}:{n}: stack name '{term}' belongs in references/")


PRIVATE = [
    (re.compile(r"/Users/[A-Za-z0-9_.-]+|/home/[a-z][a-z0-9_-]+/"), "home directory path"),
    (re.compile(r"[A-Za-z0-9._%+-]+@(gmail|yahoo|outlook|hotmail)\.com"), "personal email"),
    (re.compile(r"AKIA[0-9A-Z]{16}|gh[pousr]_[0-9A-Za-z]{36}|sk-[A-Za-z0-9_-]{32,}|xox[baprs]-[0-9A-Za-z-]{10,}"), "key-shaped string"),
]
PRIVACY_SKIP = {"scripts/check.py", "plugins/guard/scripts"}


def check_privacy() -> None:
    for path in sorted(walk("*")):
        r = rel(path)
        if not path.is_file() or any(r.startswith(s) for s in PRIVACY_SKIP) or path.suffix in {".png", ".jpg", ".mp3", ".mp4", ".woff2"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for n, line in enumerate(text.splitlines(), 1):
            for pat, what in PRIVATE:
                if pat.search(line):
                    bad(f"{r}:{n}: {what}")


CHECKS = {
    "manifests": check_manifests,
    "skills": check_skills,
    "agents": check_agents,
    "links": check_links,
    "stack": check_stack,
    "privacy": check_privacy,
}


def main(argv: list[str]) -> int:
    chosen = argv or list(CHECKS)
    for name in chosen:
        if name not in CHECKS:
            print(f"unknown check '{name}'. Choose from: {', '.join(CHECKS)}")
            return 2
        CHECKS[name]()
    for p in problems:
        print(p)
    print(f"{len(problems)} problem(s) in: {', '.join(chosen)}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
