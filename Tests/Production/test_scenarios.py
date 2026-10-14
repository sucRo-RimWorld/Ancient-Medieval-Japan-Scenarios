"""Explicit scenario XML only; not RimWorld inheritance, runtime or save tests."""
from copy import deepcopy
from pathlib import Path
import unittest
import fnmatch
import io
import subprocess
import zipfile
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]
MO='dankpyon.medieval.overhaul';GRAINS='sucro.ancientmedievaljapan.core'
OWNED={'ScenarioDef':'AMJC_NewVillage','FactionDef':'AMJC_PlayerVillage','PawnKindDef':'AMJC_Villager'}

def project(mo,grains,loader=None):
    active=({MO} if mo else set())|({GRAINS} if grains else set())
    loader=loader if loader is not None else ET.parse(ROOT/'loadFolders.xml').getroot()
    doc=ET.Element('Defs');patches=[]
    for li in loader.findall('v1.6/li'):
        guard=li.get('IfModActive')
        if guard and guard.lower() not in active:continue
        folder=ROOT if li.text=='/' else ROOT/li.text
        for file in sorted((folder/'Defs').glob('**/*.xml')):doc.extend(deepcopy(list(ET.parse(file).getroot())))
        for file in sorted((folder/'Patches').glob('**/*.xml')):patches.extend(deepcopy(list(ET.parse(file).getroot())))
    for op in patches:
        targets=doc.findall('./'+op.findtext('xpath')[len('/Defs/'):]);assert len(targets)==1
        target=targets[0];children=deepcopy(list(op.find('value')))
        if op.get('Class')=='PatchOperationAdd':target.extend(children)
        else:
            assert op.get('Class')=='PatchOperationReplace'
            parents={c:p for p in doc.iter() for c in p};parent=parents[target];index=list(parent).index(target);parent.remove(target)
            for offset,c in enumerate(children):parent.insert(index+offset,c)
    defs={n.findtext('defName'):n for n in doc}
    assert len(doc)==len(defs)==3
    assert {n.tag:name for name,n in defs.items()}==OWNED
    scenario=defs['AMJC_NewVillage'];faction=defs['AMJC_PlayerVillage'];pawn=defs['AMJC_Villager']
    assert scenario.findtext('scenario/playerFaction/factionDef')=='AMJC_PlayerVillage'
    assert faction.findtext('basicMemberKind')=='AMJC_Villager'
    assert pawn.findtext('defaultFactionDef')=='AMJC_PlayerVillage'
    stocks=scenario.findall('scenario/parts/li[@Class="ScenPart_StartingThing_Defined"]')
    items={n.findtext('thingDef'):int(n.findtext('count')) for n in stocks};assert len(items)==len(stocks)
    expected={'Pemmican':1080,'RawRice':300,'MedicineHerbal':20,
              'WoodLog':400,'Steel':30,'Cloth':80,'Silver':150,'Bow_Short':2,
              'MeleeWeapon_Knife':2,'MeleeWeapon_Club':1}
    if mo:
        expected.pop('Pemmican');expected['DankPyon_MealRations']=60
        expected['WoodLog']=200;expected['DankPyon_RawWood']=200
        expected.pop('Steel');expected['DankPyon_IronIngot']=30
    if grains:
        expected.pop('RawRice')
        expected.update({'AMJC_Millet':200,'AMJC_RawMillet':100})
    assert items==expected, 'Full four-profile starting supply inventory differs'
    stuff={n.findtext('thingDef'):n.findtext('stuff') for n in stocks}
    assert stuff['MeleeWeapon_Knife']==('DankPyon_IronIngot' if mo else 'Steel')
    assert stuff['MeleeWeapon_Club']=='WoodLog'
    assert {x.findtext('project') for x in scenario.findall('scenario/parts/li[@Class="ScenPart_StartingResearch"]')} == (
        {'DankPyon_Lumber','DankPyon_RusticFurniture','DankPyon_BasicCooking'} if mo else set())
    assert sum(x.get('Class')=='ScenPart_StartingResearch' for x in scenario.findall('scenario/parts/li')) == (3 if mo else 0)
    assert bool(scenario.findall('scenario/parts/li[@Class="ScenPart_StartingResearch"]'))==mo
    assert ('DankPyon_Peasant' in [n.text for n in pawn.findall('apparelTags/li')])==mo
    if not mo:assert all(not (n.text or '').strip().startswith('DankPyon_') for n in doc.iter())
    return doc

class Contracts(unittest.TestCase):
    def test_four_profiles(self):
        for mo in (False,True):
            for grains in (False,True):
                with self.subTest(mo=mo,grains=grains):project(mo,grains)
    def test_guard_loss_is_rejected(self):
        loader=ET.parse(ROOT/'loadFolders.xml').getroot();loader.findall('v1.6/li')[2].attrib.clear()
        with self.assertRaises(AssertionError):project(False,False,loader)
    def test_mo_and_grains_patches_are_order_independent(self):
        original=project(True,True)
        loader=ET.parse(ROOT/'loadFolders.xml').getroot()
        v=loader.find('v1.6');a,b=list(v)[1:];v.remove(a);v.remove(b);v.extend([b,a])
        reversed_order=project(True,True,loader)
        self.assertEqual(ET.tostring(original),ET.tostring(reversed_order))
    def test_whole_scenario_replacement_is_forbidden(self):
        patch=ET.parse(ROOT/'Compatibility/MedievalOverhaul/Patches/StartingScenarios.xml').getroot()
        self.assertFalse(any(op.findtext('xpath')==
            '/Defs/ScenarioDef[defName="AMJC_NewVillage"]/scenario/parts' for op in patch))
    def test_metadata_and_localization(self):
        about=ET.parse(ROOT/'About/About.xml').getroot()
        self.assertEqual(about.findtext('packageId'),'sucro.ancientmedievaljapan.scenarios')
        self.assertFalse(about.findall('modDependencies/li'))
        self.assertFalse(any(c in about.findtext('name') for c in ':：'))
        self.assertEqual([n.text.lower() for n in about.findall('loadAfter/li')],[MO,GRAINS])
        for lang in ('English','Japanese'):
            dialog=ET.parse(ROOT/f'Languages/{lang}/Keyed/AMJC_Scenarios.xml').getroot()
            self.assertIsNotNone(dialog.find('AMJC_GameStart_NewVillage'))


if __name__=='__main__':unittest.main()
