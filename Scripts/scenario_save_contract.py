"""Prepare immutable save-test inputs and check narrow XML conservation contracts.

No game launch, save repair, package remapping or runtime PASS is performed here.
Only a real engine roundtrip with separate runtime evidence can prove migration.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

CORE = 'sucro.ancientmedievaljapan.core'
SCENARIOS = 'sucro.ancientmedievaljapan.scenarios'
MO = 'dankpyon.medieval.overhaul'
FACTION = 'AMJC_PlayerVillage'
KIND = 'AMJC_Villager'


class ContractError(ValueError):
    pass


def require(value, message):
    if not value:
        raise ContractError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(node):
    """Ignore indentation/attribute order, retain child order and all values."""
    return [node.tag, sorted(node.attrib.items()), (node.text or '').strip(),
            [canonical(child) for child in node]]


def inspect_bytes(data):
    # Do not accept entities/DTDs or a partially recognised save as an empty PASS.
    try:
        text = data.decode('utf-8-sig')
    except UnicodeDecodeError as error:
        raise ContractError('Only UTF-8 save XML is supported.') from error
    require('\x00' not in text, 'Only UTF-8 save XML is supported.')
    require('<!DOCTYPE' not in text.upper() and '<!ENTITY' not in text.upper(),
            'DTD/entity declarations are not supported.')
    try:
        root = ET.fromstring(data)
    except ET.ParseError as error:
        raise ContractError(f'Invalid save XML: {error}') from error
    require(root.tag == 'savegame', 'Expected savegame root; unsupported save shape.')
    game = root.find('game')
    require(game is not None, 'Missing game; unsupported save shape.')
    version = root.findtext('meta/gameVersion')
    require(version and version.startswith('1.6.'), 'Only recorded RimWorld 1.6 saves are supported.')
    mod_nodes = root.findall('meta/modIds/li')
    mods = [(n.text or '').strip().lower() for n in mod_nodes]
    require(mods and all(mods) and len(mods) == len(set(mods)), 'Missing/duplicate recorded modIds.')
    require('ludeon.rimworld' in mods, 'Base-game modId missing.')
    require(not any('e2e' in m or 'fixture' in m or 'extractiontest' in m for m in mods),
            'Test aliases require a separate fixture path; production-save inspector rejects them.')
    scenario = game.find('scenario')
    require(scenario is not None and scenario.find('parts') is not None,
            'Scenario parts missing; unsupported save shape.')
    require(scenario.findtext('playerFaction/factionDef') == FACTION,
            'Save must contain the New Village player faction scenario part.')
    factions = game.findall('world/factionManager/allFactions/li')
    village = [f for f in factions if f.findtext('def') == FACTION]
    require(len(village) == 1, 'Exactly one saved New Village faction is required.')
    faction_id = village[0].findtext('loadID')
    require(faction_id and faction_id.isdigit(), 'Saved faction loadID missing/unsupported.')
    maps = game.find('maps')
    require(maps is not None and len(maps) > 0, 'Saved maps missing.')
    pawns = []
    stocks = Counter()
    thing_ids = set()
    # Includes nested inventories, equipment and containers; counts are never generated.
    for node in maps.iter():
        if node.findtext('kindDef') == KIND:
            pawn_id = node.findtext('id')
            faction = node.findtext('faction')
            require(pawn_id and faction == 'Faction_' + faction_id,
                    'Villager pawn ID/faction reference missing or inconsistent.')
            pawns.append({'id': pawn_id, 'kind': KIND, 'faction': faction})
        thing_def = node.findtext('def')
        # A persisted thing has an id; Scenario parts and other Def refs have none.
        if thing_def and node.findtext('id'):
            thing_id = node.findtext('id')
            require(thing_id not in thing_ids, 'Duplicate persisted map thing ID.')
            thing_ids.add(thing_id)
            text = node.findtext('stackCount', '1')
            require(text.isdigit() and int(text) > 0, 'Invalid persisted thing stackCount.')
            stocks[thing_def] += int(text)
    require(len(pawns) >= 5 and len({p['id'] for p in pawns}) == len(pawns),
            'At least five distinct saved AMJC villagers required.')
    research = game.find('researchManager')
    require(research is not None, 'researchManager missing; unsupported save shape.')
    ticks = game.findtext('tickManager/ticksGame')
    require(ticks is not None and ticks.isdigit(), 'ticksGame missing; unsupported save shape.')
    return {'sha256': digest(data), 'gameVersion': version, 'modIds': mods,
            'scenario': canonical(scenario), 'faction': canonical(village[0]),
            'villagers': sorted(pawns, key=lambda p: p['id']),
            'mapThingCounts': dict(sorted(stocks.items())),
            'research': canonical(research), 'ticksGame': int(ticks)}


def inspect(path):
    path = Path(path)
    require(path.suffix.lower() == '.rws', 'Input must be a .rws save.')
    return inspect_bytes(path.read_bytes())


def compare(before, after, transition):
    require(transition in {'same-providers', 'add-scenarios', 'remove-scenarios'}, 'Unknown transition.')
    require(before['gameVersion'] == after['gameVersion'], 'Game version changed during roundtrip.')
    old, new = set(before['modIds']), set(after['modIds'])
    require(CORE in old and CORE in new and MO in old and MO in new,
            'This gate retains Grains and MO; provider removal is outside its scope.')
    added, removed = new - old, old - new
    if transition == 'add-scenarios':
        require(SCENARIOS not in old and SCENARIOS in new and added == {SCENARIOS} and not removed,
                'Expected only Scenarios addition.')
    elif transition == 'remove-scenarios':
        require(SCENARIOS in old and SCENARIOS not in new and removed == {SCENARIOS} and not added,
                'Expected only Scenarios removal.')
    else:
        require(not added and not removed, 'Unexpected mod-list change for same-provider roundtrip.')
    # Pause before load/save: elapsed simulation invalidates inventory/research comparison.
    for key in ('ticksGame', 'scenario', 'faction', 'villagers', 'mapThingCounts', 'research'):
        require(before[key] == after[key], f'Conservation contract changed: {key}')
    return {'schemaVersion': 1, 'status': 'xml-contracts-checked', 'runtimeVerified': False,
            'transition': transition, 'beforeSha256': before['sha256'],
            'afterSha256': after['sha256'], 'limits':
            'No loader/rendering/reference/ERROR evidence. Not safe Grains/MO removal or a release gate.'}


def prepare(save, output, legacy_commit, grains_commit, scenarios_commit):
    for name, value in [('legacy', legacy_commit), ('grains', grains_commit), ('scenarios', scenarios_commit)]:
        require(bool(re.fullmatch('[0-9a-f]{40}', value)), f'{name} source requires a full commit SHA.')
    source = Path(save).resolve()
    data = source.read_bytes()
    require(source.suffix.lower() == '.rws', 'Input must be a .rws save.')
    baseline = inspect_bytes(data)
    require(CORE in baseline['modIds'] and MO in baseline['modIds'] and SCENARIOS not in baseline['modIds'],
            'Legacy fixture requires recorded production Grains/Core + MO, without Scenarios.')
    require(legacy_commit != grains_commit, 'Legacy and updated Grains source commits must differ.')
    target = Path(output).resolve()
    require(not target.exists(), 'Output must be a new directory; existing evidence is never overwritten.')
    # All checks above precede writing. Never rewrite the source save or metadata.
    target.mkdir(parents=True)
    (target / 'baseline.rws').write_bytes(data)
    plan = {'schemaVersion': 1, 'status': 'prepared-not-run', 'runtimeVerified': False,
            'sourceSaveSha256': digest(data), 'sourceCommits':
            {'legacyGrains': legacy_commit, 'updatedGrains': grains_commit, 'scenarios': scenarios_commit},
            'provenanceLimit': 'Commit IDs supplied by caller; actual originating game/source not attested.',
            'baseline': baseline, 'cases': [
                {'name': 'guarded-legacy', 'input': 'baseline.rws', 'transition': 'same-providers',
                 'scenarios': False},
                {'name': 'add-scenarios', 'input': 'baseline.rws', 'transition': 'add-scenarios',
                 'scenarios': True},
                {'name': 'reload-scenarios', 'input': 'add-scenarios/resaved.rws',
                 'transition': 'same-providers', 'scenarios': True},
                {'name': 'remove-scenarios', 'input': 'add-scenarios/resaved.rws',
                 'transition': 'remove-scenarios', 'scenarios': False}],
            'requiredRuntimeEvidence': ['source/DLL/provider hashes', 'paused load and re-save',
                                        'fresh exact Pickle summary', 'rendering retained', 'every ERROR = 0']}
    for case in plan['cases']:
        folder = target / case['name']
        folder.mkdir()
        if case['input'] == 'baseline.rws':
            (folder / 'input.rws').write_bytes(data)
        # Dependent inputs are intentionally absent until add-scenarios actually re-saves.
    (target / 'plan.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    require(source.read_bytes() == data, 'Source save changed while preparing; discard this bundle.')
    return plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('prepare')
    p.add_argument('--save', required=True)
    p.add_argument('--output', required=True)
    for key in ('legacy-commit', 'grains-commit', 'scenarios-commit'):
        p.add_argument('--' + key, required=True)
    p = sub.add_parser('compare')
    p.add_argument('--before', required=True)
    p.add_argument('--after', required=True)
    p.add_argument('--transition', choices=['same-providers', 'add-scenarios', 'remove-scenarios'], required=True)
    args = parser.parse_args()
    try:
        if args.command == 'prepare':
            result = prepare(args.save, args.output, args.legacy_commit, args.grains_commit, args.scenarios_commit)
            print(json.dumps({'status': result['status'], 'runtimeVerified': False}, indent=2))
        else:
            print(json.dumps(compare(inspect(args.before), inspect(args.after), args.transition), indent=2))
    except (ContractError, OSError) as error:
        print(f'[FAIL] {error}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
