"""Synthetic XML tooling regressions, never a RimWorld save/runtime PASS."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('save_contract', ROOT / 'Scripts/scenario_save_contract.py')
save = importlib.util.module_from_spec(spec)
spec.loader.exec_module(save)


def synthetic_xml(scenarios=False):
    # Deliberately not shipped as .rws fixture: real engine provenance is unavailable.
    root = ET.fromstring('''<savegame><meta><gameVersion>1.6.4633 rev1</gameVersion><modIds>
    <li>ludeon.rimworld</li><li>sucro.ancientmedievaljapan.core</li><li>dankpyon.medieval.overhaul</li>
    </modIds></meta><game><tickManager><ticksGame>100</ticksGame></tickManager>
    <scenario><playerFaction Class="ScenPart_PlayerFaction"><factionDef>AMJC_PlayerVillage</factionDef></playerFaction>
    <parts><li Class="ScenPart_StartingThing_Defined"><thingDef>AMJC_Millet</thingDef><count>200</count></li></parts></scenario>
    <world><factionManager><allFactions><li><def>AMJC_PlayerVillage</def><loadID>1</loadID></li></allFactions></factionManager></world>
    <maps><li><things><thing Class="ThingWithComps"><def>AMJC_Millet</def><id>11</id><stackCount>120</stackCount></thing>
    </things></li></maps><researchManager><progress><keys><li>DankPyon_Smithing</li></keys><values><li>100</li></values></progress></researchManager>
    </game></savegame>''')
    if scenarios:
        ET.SubElement(root.find('meta/modIds'), 'li').text = save.SCENARIOS
    for i in range(5):
        p = ET.SubElement(root.find('game/maps/li/things'), 'thing', {'Class': 'Pawn'})
        for tag, value in [('def', 'Human'), ('id', str(100 + i)), ('kindDef', save.KIND), ('faction', 'Faction_1')]:
            ET.SubElement(p, tag).text = value
        if i == 0:
            inventory = ET.SubElement(p, 'inventory')
            t = ET.SubElement(inventory, 'innerContainer')
            item = ET.SubElement(t, 'li')
            for tag, value in [('def', 'AMJC_Millet'), ('id', '200'), ('stackCount', '80')]:
                ET.SubElement(item, tag).text = value
    return root


def inspect(root):
    return save.inspect_bytes(ET.tostring(root))


class SaveContracts(unittest.TestCase):
    def setUp(self):
        self.root = synthetic_xml()
        self.before = inspect(self.root)

    def test_three_transition_types_never_claim_runtime(self):
        add = inspect(synthetic_xml(True))
        for a, b, transition in [(self.before, self.before, 'same-providers'),
                                  (self.before, add, 'add-scenarios'),
                                  (add, self.before, 'remove-scenarios')]:
            result = save.compare(a, b, transition)
            self.assertEqual(result['status'], 'xml-contracts-checked')
            self.assertFalse(result['runtimeVerified'])

    def test_nested_stock_count(self):
        self.assertEqual(self.before['mapThingCounts']['AMJC_Millet'], 200)
        self.assertNotIn('RawRice', self.before['mapThingCounts'])

    def test_contract_losses_and_redistribution_rejected(self):
        mutations = [('stocks', 'game/maps/li/things/thing/stackCount', '220'),
                     ('research', 'game/researchManager/progress/values/li', '200'),
                     ('scenario', 'game/scenario/parts/li/count', '300'),
                     ('tick', 'game/tickManager/ticksGame', '101'),
                     ('pawn', 'game/maps/li/things/thing[@Class="Pawn"]/id', '900')]
        for label, path, value in mutations:
            with self.subTest(label=label):
                after = deepcopy(self.root)
                after.find(path).text = value
                with self.assertRaises(save.ContractError):
                    save.compare(self.before, inspect(after), 'same-providers')

    def test_unsupported_missing_and_duplicate_data_rejected(self):
        for path in ['game/researchManager', 'game/maps', 'game/scenario/parts',
                     'game/world/factionManager/allFactions/li/loadID', 'game/tickManager/ticksGame']:
            with self.subTest(path=path):
                after = deepcopy(self.root)
                parents = {c: p for p in after.iter() for c in p}
                target = after.find(path)
                parents[target].remove(target)
                with self.assertRaises(save.ContractError): inspect(after)
        after = deepcopy(self.root)
        after.find('game/world/factionManager/allFactions').append(deepcopy(after.find('game/world/factionManager/allFactions/li')))
        with self.assertRaises(save.ContractError): inspect(after)
        after = deepcopy(self.root)
        after.find('game/maps/li/things').append(deepcopy(after.find('game/maps/li/things/thing[@Class="Pawn"]')))
        with self.assertRaises(save.ContractError): inspect(after)

    def test_faction_and_pawn_kind_change_rejected(self):
        for path, text in [('game/maps/li/things/thing[@Class="Pawn"]/faction', 'Faction_999'),
                           ('game/maps/li/things/thing[@Class="Pawn"]/kindDef', 'Tribal'),
                           ('game/world/factionManager/allFactions/li/def', 'Tribe')]:
            after = deepcopy(self.root)
            after.find(path).text = text
            with self.assertRaises(save.ContractError): inspect(after)

    def test_provider_removal_alias_leak_and_unrelated_change_rejected(self):
        for mod in [save.CORE, save.MO]:
            after = deepcopy(self.before)
            after['modIds'].remove(mod)
            with self.assertRaises(save.ContractError): save.compare(self.before, after, 'same-providers')
        after = inspect(synthetic_xml(True))
        after['modIds'].append('unrelated.mod')
        with self.assertRaises(save.ContractError): save.compare(self.before, after, 'add-scenarios')
        root = deepcopy(self.root)
        ET.SubElement(root.find('meta/modIds'), 'li').text = save.SCENARIOS + '.e2etarget'
        with self.assertRaises(save.ContractError): inspect(root)
        with self.assertRaises(save.ContractError): save.compare(self.before, self.before, 'add-scenarios')
        with self.assertRaises(save.ContractError): save.compare(self.before, self.before, 'remove-scenarios')

    def test_version_xml_and_entities_rejected(self):
        for data in [b'<broken>', '<savegame/>'.encode('utf-16'), b'<!DOCTYPE savegame [<!ENTITY x "x">]><savegame/>']:
            with self.assertRaises(save.ContractError): save.inspect_bytes(data)
        root = deepcopy(self.root)
        root.find('meta/gameVersion').text = '1.5.0000'
        with self.assertRaises(save.ContractError): inspect(root)

    def test_preparation_preserves_source_and_case_dependencies(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'original.rws'
            data = ET.tostring(self.root)
            source.write_bytes(data)
            out = Path(directory) / 'bundle'
            plan = save.prepare(source, out, 'a'*40, 'b'*40, 'c'*40)
            self.assertEqual(source.read_bytes(), data)
            self.assertEqual((out/'baseline.rws').read_bytes(), data)
            self.assertEqual((out/'add-scenarios/input.rws').read_bytes(), data)
            self.assertFalse((out/'remove-scenarios/input.rws').exists())
            self.assertFalse((out/'reload-scenarios/input.rws').exists())
            self.assertFalse(plan['runtimeVerified'])
            self.assertEqual(plan['cases'][3]['input'], 'add-scenarios/resaved.rws')
            self.assertEqual(json.loads((out/'plan.json').read_text())['status'], 'prepared-not-run')
            with self.assertRaises(save.ContractError): save.prepare(source, out, 'a'*40, 'b'*40, 'c'*40)
            for old, new in [('bad', 'b'*40), ('b'*40, 'b'*40)]:
                missing = Path(directory)/'must-not-exist'
                with self.assertRaises(save.ContractError): save.prepare(source, missing, old, new, 'c'*40)
                self.assertFalse(missing.exists())

    def test_cli_failure_is_nonzero(self):
        result = subprocess.run([sys.executable, str(ROOT/'Scripts/scenario_save_contract.py'),
                                 'compare', '--before', 'missing.rws', '--after', 'missing.rws',
                                 '--transition', 'add-scenarios'], capture_output=True)
        self.assertEqual(result.returncode, 2)


if __name__ == '__main__':
    unittest.main()
