#!/usr/bin/env python3
"""AMJ GitHub-approved SteamCMD package builder and isolated existing/private publisher.

Source preparation needs no Steam credentials.  Publication requires a protected,
repo-scoped runner and its already provisioned host-only account/state.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile

APPID = "294100"
ALLOWED_DIRS = frozenset({
    "About", "Assemblies", "Defs", "Patches", "Languages", "Textures",
    "Compatibility", "Sounds", "Resources", "LoadFolders", "BaseWithoutMO",
    "1.6", "1.7", "Royalty", "Ideology", "Biotech", "Anomaly", "Odyssey",
})
ALLOWED_FILES = frozenset({"loadFolders.xml"})
NAME_PATTERN = re.compile(r"^sucRo-RimWorld/[A-Za-z0-9._-]+$")
VERSION_PATTERN = re.compile(r"^\d+(?:\.\d+){1,3}(?:-[A-Za-z0-9.-]+)?$")
CHANGE_PATTERN = re.compile(r"^(\d+(?:\.\d+){1,3}(?:-[A-Za-z0-9.-]+)?)\s+-\s+\S")
ID_PATTERN = re.compile(r"^[1-9]\d{8,19}$")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def config_from(checkout: Path, expected_repo: str) -> dict:
    config_file = checkout / "Publishing/SteamWorkshop.json"
    cfg = json.loads(config_file.read_text(encoding="utf-8"))
    require(isinstance(cfg, dict) and cfg.get("schema") == 1, "Invalid publisher config schema")
    require(cfg.get("repository") == expected_repo and NAME_PATTERN.fullmatch(expected_repo) is not None,
            "Publisher repository identity mismatch")
    require(isinstance(cfg.get("package_id"), str) and cfg["package_id"].startswith("sucro."),
            "Package ID must be explicitly pinned")
    item_id = cfg.get("workshop_id")
    require(item_id is None or (isinstance(item_id, str) and ID_PATTERN.fullmatch(item_id) is not None),
            "Workshop ID must be a pinned decimal string or null")
    require(cfg.get("visibility_policy") in ("private_only", "preserve_public"),
            "Invalid visibility policy")
    require(item_id is not None or cfg["visibility_policy"] == "private_only",
            "A new item may only be creator-private")
    return cfg


def validate_mode(cfg: dict, operation: str) -> None:
    require(operation in ("create_private", "update_existing"), "Unknown publishing operation")
    if operation == "create_private":
        require(cfg["workshop_id"] is None and cfg["visibility_policy"] == "private_only",
                "A new item cannot overwrite an existing Workshop identity")
    else:
        require(cfg["workshop_id"] is not None, "Existing update requires pinned Workshop ID")


def changenote(raw: str, version: str) -> str:
    lines = raw.splitlines()
    headings = [(i, m.group(1)) for i, line in enumerate(lines)
                if (m := CHANGE_PATTERN.match(line))]
    current = [i for i, label in headings if label == version]
    require(len(current) == 1, "Exactly one changelog heading must match the Mod version")
    start = current[0]
    end = next((i for i, _ in headings if i > start), len(lines))
    note = "\n".join(line for line in lines[start:end] if not line.startswith("#")).strip()
    require(len(note.splitlines()) >= 2, "Changelog needs a nonempty current-version description")
    require(len(note.encode("utf-8")) <= 8000, "Changenote exceeds size limit")
    return note


def inspect_source(checkout: Path, cfg: dict) -> dict:
    about = ET.parse(checkout / "About/About.xml").getroot()
    require(about.tag == "ModMetaData" and about.findtext("packageId") == cfg["package_id"],
            "Actual Mod packageId differs from approved publisher configuration")
    title = (about.findtext("name") or "").strip()
    version = (about.findtext("modVersion") or "").strip()
    require(0 < len(title) <= 128 and VERSION_PATTERN.fullmatch(version) is not None,
            "Invalid Mod title/version")
    manifest = ET.parse(checkout / "About/Manifest.xml").getroot()
    require(manifest.tag == "Manifest" and (manifest.findtext("version") or "").strip() == version,
            "About/Manifest.xml version mismatch")
    note = changenote((checkout / "About/Changelog.txt").read_text(encoding="utf-8"), version)
    desc_file = checkout / "Docs/SteamWorkshopDescription.txt"
    if desc_file.exists():
        description = desc_file.read_text(encoding="utf-8")
    else:
        description = (about.findtext("description") or "").strip()
    require(0 < len(description.encode("utf-8")) <= 8000, "Missing/oversized Workshop description")
    current_id = checkout / "About/PublishedFileId.txt"
    if current_id.exists():
        require(current_id.read_text(encoding="ascii").strip() == cfg["workshop_id"],
                "Tracked PublishedFileId differs from approved existing item")
    return {"title": title, "version": version, "description": description, "changenote": note}


def candidate_files(checkout: Path) -> list[Path]:
    result = []
    for root in sorted(ALLOWED_DIRS | ALLOWED_FILES):
        target = checkout / root
        if not target.exists():
            continue
        require(not target.is_symlink(), "Symlink publication root prohibited: " + root)
        paths = target.rglob("*") if target.is_dir() else [target]
        for path in paths:
            require(not path.is_symlink(), "Symlink inside release payload prohibited: " + str(path))
            if path.is_file():
                rel = path.relative_to(checkout)
                require(not any(p.startswith(".") or p in ("__pycache__",) for p in rel.parts),
                        "Unexpected developer file inside distribution: " + str(rel))
                result.append(rel)
    require(Path("About/About.xml") in result, "Release payload must include About/About.xml")
    require(Path("About/Manifest.xml") in result and Path("About/Changelog.txt") in result,
            "Release metadata must survive staging")
    require(not any(p.suffix.lower() in (".pdb", ".cs", ".py", ".ps1", ".bat", ".log", ".md")
                    for p in result), "Development-only file in subscriber payload")
    require(any(p.parts[0] != "About" for p in result), "No playable payload in selected release roots")
    require(len(result) <= 15000, "Unexpected file count in distribution")
    return sorted(set(result))


def build(checkout: Path, output: Path, cfg: dict, operation: str) -> None:
    validate_mode(cfg, operation)
    meta = inspect_source(checkout, cfg)
    files = candidate_files(checkout)
    if operation == "create_private":
        require(Path("About/Preview.png") in files,
                "Private first item requires accepted About/Preview.png in source")
    root = "mod/"
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest = {"schema": 1, "repository": cfg["repository"], "package_id": cfg["package_id"],
                "operation": operation, "workshop_id": cfg["workshop_id"],
                "visibility_policy": cfg["visibility_policy"], "metadata": meta, "files": {}}
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            blob = (checkout / path).read_bytes()
            require(len(blob) <= 150_000_000, "Abnormal single-file size: " + str(path))
            manifest["files"][path.as_posix()] = hashlib.sha256(blob).hexdigest()
            archive.writestr(root + path.as_posix(), blob)
        if cfg["workshop_id"] and Path("About/PublishedFileId.txt") not in files:
            item = cfg["workshop_id"].encode("ascii") + b"\n"
            archive.writestr(root + "About/PublishedFileId.txt", item)
            manifest["files"]["About/PublishedFileId.txt"] = hashlib.sha256(item).hexdigest()
    output.with_suffix(".json").write_text(json.dumps(manifest, sort_keys=True, ensure_ascii=False, indent=2) + "\n",
                                            encoding="utf-8")
    output.with_suffix(".sha256").write_text(hashlib.sha256(output.read_bytes()).hexdigest() + "\n",
                                              encoding="ascii")
    print("SOURCE_CANDIDATE_READY: " + cfg["repository"] + " " + operation +
          " (" + str(len(manifest["files"])) + " subscriber files). No Steam operation.")


def quote(value: str) -> str:
    require(not any(ord(char) < 32 and char not in "\r\n\t" for char in value),
            "Disallowed control character in SteamCMD VDF")
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"').replace("\r\n", "\n").replace("\r", "\n").replace("\t", "\\t") + '"'


def state_file() -> Path:
    raw = os.environ.get("AMJ_STEAM_STATE", "")
    require(bool(raw), "Isolated per-Mod AMJ_STEAM_STATE host variable is missing")
    path = Path(raw).expanduser()
    require(path.is_absolute() and not path.is_symlink(), "Unsafe host state path")
    require(path.parent.is_dir() and not path.parent.is_symlink()
            and not (stat.S_IMODE(path.parent.stat().st_mode) & 0o077),
            "Host state parent must already be a private 0700 directory")
    if path.exists():
        require(path.is_file() and not (stat.S_IMODE(path.stat().st_mode) & 0o077),
                "Host state must be a private 0600 file")
    return path


def state_load(path: Path, cfg: dict, operation: str) -> None:
    if operation == "create_private":
        require(not path.exists(), "First upload already has a saved state; refuse duplicate item")
        return
    require(path.exists(), "Existing item must have separately provisioned per-Mod host state")
    data = json.loads(path.read_text(encoding="utf-8"))
    require(data.get("schema") == 1 and data.get("appid") == APPID
            and data.get("repository") == cfg["repository"]
            and data.get("publishedfileid") == cfg["workshop_id"],
            "Existing host state conflicts with approved Workshop identity")
    require(data.get("visibility_policy") == cfg["visibility_policy"],
            "Publisher host visibility policy mismatch")
    require(data.get("identity_verified") is True,
            "Owner/visibility must be independently verified before an existing update")


def state_save(path: Path, cfg: dict, item_id: str) -> None:
    obj = {"schema": 1, "appid": APPID, "repository": cfg["repository"],
           "publishedfileid": item_id, "visibility_policy": cfg["visibility_policy"],
           "identity_verified": False}
    fd, temp = tempfile.mkstemp(prefix=".steam-workshop-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as output:
            json.dump(obj, output, sort_keys=True)
            output.write("\n")
        os.chmod(temp, 0o600)
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def upload(checkout: Path, candidate: Path, cfg: dict, operation: str) -> None:
    validate_mode(cfg, operation)
    meta = inspect_source(checkout, cfg)
    saved = json.loads(candidate.with_suffix(".json").read_text(encoding="utf-8"))
    require(saved["repository"] == cfg["repository"] and saved["package_id"] == cfg["package_id"]
            and saved["workshop_id"] == cfg["workshop_id"] and saved["operation"] == operation
            and saved["visibility_policy"] == cfg["visibility_policy"] and saved["metadata"] == meta,
            "Approved preflight manifest mismatch")
    require(hashlib.sha256(candidate.read_bytes()).hexdigest()
            == candidate.with_suffix(".sha256").read_text(encoding="ascii").strip(),
            "Candidate ZIP checksum mismatch")
    state = state_file()
    require(checkout.resolve() not in state.resolve().parents, "State must be outside checkout")
    state_load(state, cfg, operation)
    executable = Path(os.environ.get("AMJ_STEAMCMD_BIN", ""))
    account = os.environ.get("AMJ_STEAM_ACCOUNT", "")
    require(executable.is_file() and os.access(executable, os.X_OK),
            "Isolated publisher SteamCMD binary absent")
    require(re.fullmatch(r"[A-Za-z0-9_]{1,64}", account) is not None, "Publisher account not provisioned")
    with tempfile.TemporaryDirectory(prefix="amj-steam-release-") as temp:
        folder = Path(temp) / "mod"
        folder.mkdir()
        with zipfile.ZipFile(candidate) as archive:
            expected = {"mod/" + p for p in saved["files"]}
            require(set(archive.namelist()) == expected, "ZIP extra/missing file rejected")
            for rel, digest in saved["files"].items():
                blob = archive.read("mod/" + rel)
                require(hashlib.sha256(blob).hexdigest() == digest, "ZIP entry hash mismatch: " + rel)
                path = folder / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(blob)
        preview = folder / "About/Preview.png"
        if operation == "create_private":
            require(preview.is_file(), "First private upload needs an approved Preview.png")
        item_id = cfg["workshop_id"] or "0"
        fields = [("appid", APPID), ("publishedfileid", item_id),
                  ("contentfolder", str(folder.resolve())),
                  ("title", meta["title"]), ("description", meta["description"]),
                  ("changenote", meta["changenote"])]
        if preview.is_file():
            fields.append(("previewfile", str(preview.resolve())))
        if operation == "create_private":
            fields.append(("visibility", "2"))
        vdf = Path(temp) / "upload.vdf"
        vdf.write_text('"workshopitem"\n{\n' +
                       "".join("  " + quote(k) + " " + quote(v) + "\n" for k, v in fields) +
                       "}\n", encoding="utf-8")
        os.chmod(vdf, 0o600)
        with (Path(temp) / "steamcmd.log").open("wb") as output:
            proc = subprocess.run([str(executable.resolve()), "+login", account,
                                   "+workshop_build_item", str(vdf), "+quit"],
                                  cwd=temp, stdin=subprocess.DEVNULL, stdout=output,
                                  stderr=subprocess.STDOUT, check=False, timeout=900)
        match = re.search(r'^\s*"publishedfileid"\s+"([0-9]+)"',
                          vdf.read_text(encoding="utf-8"), re.MULTILINE)
        after = match.group(1) if match else ""
        if operation == "create_private" and ID_PATTERN.fullmatch(after):
            # Even nonzero SteamCMD can allocate an item: preserve ID before throwing.
            state_save(state, cfg, after)
        require(proc.returncode == 0, "SteamCMD failed; consult protected host-local log")
        require(ID_PATTERN.fullmatch(after) is not None, "SteamCMD did not return an item ID")
        if operation == "update_existing":
            require(after == item_id, "SteamCMD changed existing item identity")
            # Preserve separately verified item identity; the VDF omits visibility.
        target_output = os.environ.get("GITHUB_OUTPUT")
        if target_output:
            with open(target_output, "a", encoding="utf-8") as stream:
                stream.write("published_id=" + after + "\n")
        print("STEAMCMD_UPLOADED item=" + after + "; visibility not changed on updates")
        print("CHANGELOG_SUBMITTED; actual Steam History and subscriber payload require read-back")
        print("TAGS_NOT_SYNCED: independent authenticated Steamworks tag submission required")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("build", "upload"))
    parser.add_argument("--checkout", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--operation", choices=("create_private", "update_existing"), required=True)
    args = parser.parse_args()
    checkout = args.checkout.resolve()
    cfg = config_from(checkout, args.repo)
    if args.action == "build":
        build(checkout, args.output, cfg, args.operation)
    else:
        upload(checkout, args.output, cfg, args.operation)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, ET.ParseError, zipfile.BadZipFile,
            subprocess.TimeoutExpired) as exc:
        print("PUBLISHER_BLOCKED: " + str(exc), file=sys.stderr)
        sys.exit(2)
