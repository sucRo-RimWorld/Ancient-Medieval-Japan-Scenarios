#!/usr/bin/env python3
"""Authenticated Steamworks tag synchronization for a GitHub-approved AMJ upload."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from urllib import parse, request

from publisher import config_from, inspect_source, require

APPID = 294100


def tags(checkout: Path) -> list[str]:
    metadata = ET.parse(checkout / "About/About.xml").getroot()
    versions = [(n.text or "").strip() for n in metadata.findall("./supportedVersions/li")]
    require(bool(versions) and len(set(versions)) == len(versions)
            and all(re.fullmatch(r"1\.\d+", v) for v in versions),
            "Missing/duplicate RimWorld compatibility versions")
    extra_path = checkout / "About/WorkshopTags.xml"
    if extra_path.exists():
        root = ET.parse(extra_path).getroot()
        require(root.tag == "WorkshopTags", "Wrong custom tags file root")
        extra = [(n.text or "").strip() for n in root.findall("li")]
    else:
        extra = []
    result = ["Mod", *versions, *extra]
    require(len(result) == len(set(v.casefold() for v in result)),
            "Duplicate Workshop tags")
    require(all(t and len(t) <= 255 and "," not in t and "\n" not in t for t in result),
            "Invalid Workshop tag")
    return result


def agent_call(path: Path, arguments: list[str], timeout: int = 240) -> dict:
    process = subprocess.run([str(path), *arguments], stdin=subprocess.DEVNULL,
                             capture_output=True, text=True, check=False, timeout=timeout)
    require(process.returncode == 0, "Authenticated Steamworks agent failed (host log required)")
    obj = json.loads(process.stdout)
    require(isinstance(obj, dict) and obj.get("status") == "ok"
            and isinstance(obj.get("data"), dict), "Invalid Steamworks response")
    return obj["data"]


def private_receipt(checkout: Path, cfg: dict) -> Path:
    """Separate idempotency receipts for each publisher, under one private profile."""
    raw = os.environ.get("AMJ_STEAM_TAG_RECEIPT_DIR", "")
    home = os.environ.get("LOCALAPPDATA", "")
    require(bool(raw and home), "Private Windows tag receipt directory is not provisioned")
    directory = Path(raw)
    require(directory.is_absolute() and directory.is_dir() and not directory.is_symlink(),
            "Invalid private Windows tag receipt directory")
    require(directory.resolve().is_relative_to(Path(home).resolve())
            and not directory.resolve().is_relative_to(checkout.resolve()),
            "Receipt directory must be in the Windows publisher profile, outside checkout")
    receipt = directory / (cfg["repository"].split("/", 1)[1] + ".json")
    require(not receipt.is_symlink(), "Receipt may not be a symlink")
    return receipt


def verify_public_item(item_id: str, expected_title: str) -> None:
    endpoint = "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/"
    body = parse.urlencode({"itemcount": "1", "publishedfileids[0]": item_id}).encode("ascii")
    with request.urlopen(request.Request(endpoint, data=body, method="POST"), timeout=25) as res:
        obj = json.load(res)
    records = obj["response"]["publishedfiledetails"]
    require(len(records) == 1 and str(records[0].get("publishedfileid")) == item_id
            and records[0].get("result") == 1 and records[0].get("title") == expected_title
            and records[0].get("visibility") == 0,
            "Existing public Workshop identity/title/visibility differs from source")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=("probe", "sync"))
    p.add_argument("--checkout", type=Path, required=True)
    p.add_argument("--repo", required=True)
    p.add_argument("--item-id", default="")
    p.add_argument("--after-upload-run-id", default="")
    a = p.parse_args()
    cfg = config_from(a.checkout, a.repo)
    meta = inspect_source(a.checkout, cfg)
    desired = tags(a.checkout)
    raw_agent = os.environ.get("AMJ_STEAMWORKS_AGENT_BIN", "")
    require(bool(raw_agent), "Windows Steamworks agent not provisioned")
    agent = Path(raw_agent).resolve()
    require(agent.is_file() and os.access(agent, os.X_OK)
            and not agent.is_relative_to(a.checkout.resolve()), "Invalid host agent")
    receipt = private_receipt(a.checkout, cfg)
    probe = agent_call(agent, ["steam-session-probe"], timeout=90)
    require(probe.get("ready") is True and probe.get("steamUserLoggedOn") is True
            and probe.get("steamAppId") == APPID, "Steamworks session not authenticated for RimWorld")
    if a.action == "probe":
        print("TAG_AGENT_READY; no Workshop mutation")
        return
    require(re.fullmatch(r"[1-9]\d{8,19}", a.item_id) is not None, "Invalid uploaded item ID")
    require(re.fullmatch(r"[1-9]\d{0,19}", a.after_upload_run_id) is not None,
            "Tag sync requires exact successful upload-run context")
    require(cfg["workshop_id"] is None or cfg["workshop_id"] == a.item_id,
            "Attempt to tag a different existing item")
    if cfg["visibility_policy"] == "preserve_public":
        verify_public_item(a.item_id, meta["title"])
    context = a.after_upload_run_id + ":" + a.item_id
    if receipt.exists():
        old = json.loads(receipt.read_text(encoding="utf-8"))
        require(old.get("repository") == cfg["repository"] and old.get("item_id") == a.item_id,
                "Tag receipt belongs to another Mod/item")
        require(old.get("status") != "PENDING", "Ambiguous earlier tag submission; inspect Steam")
        if old.get("status") == "OK" and old.get("context") == context and old.get("tags") == desired:
            print("TAGS_ALREADY_SUBMITTED for this exact upload run; no duplicate")
            return
    def record(status: str) -> None:
        receipt.write_text(json.dumps({"repository": cfg["repository"], "item_id": a.item_id,
                                       "context": context, "tags": desired, "status": status},
                                      ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    record("PENDING")
    changed = agent_call(agent, ["set-tags", a.item_id, *desired, "--confirm",
                                 "--changenote", "Workshop tag sync / タグ更新"])
    require(changed.get("success") is True and changed.get("steamAppId") == APPID
            and str(changed.get("publishedFileId")) == a.item_id
            and changed.get("submitResult") == "OK"
            and changed.get("timedOut") is False
            and changed.get("userNeedsToAcceptWorkshopLegalAgreement") is False
            and changed.get("tags") == desired,
            "Steamworks tag result unverified; do not retry blindly")
    if cfg["visibility_policy"] == "preserve_public":
        verify_public_item(a.item_id, meta["title"])
    record("OK")
    print("STEAMWORKS_TAGS_SUBMITTED item=" + a.item_id + "; external page display still unverified")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError,
            ET.ParseError, subprocess.TimeoutExpired) as exc:
        print("STEAM_TAGS_BLOCKED: " + str(exc), file=sys.stderr)
        sys.exit(2)
