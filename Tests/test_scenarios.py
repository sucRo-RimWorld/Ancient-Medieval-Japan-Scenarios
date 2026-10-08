"""Explicit scenario XML only; not RimWorld inheritance, runtime or save tests."""
from copy import deepcopy
from pathlib import Path
import unittest
import fnmatch
import io
import subprocess
import zipfile
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
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
    if grains:assert items.get('AMJC_Millet')==200 and items.get('AMJC_RawMillet')==100 and 'RawRice' not in items
    else:assert items.get('RawRice')==300 and not any(x.startswith('AMJC_') for x in items)
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
    def test_patch_order_is_required(self):
        loader=ET.parse(ROOT/'loadFolders.xml').getroot();v=loader.find('v1.6');a,b=list(v)[1:];v.remove(a);v.remove(b);v.extend([b,a])
        with self.assertRaises(AssertionError):project(True,True,loader)
    def test_metadata_and_localization(self):
        about=ET.parse(ROOT/'About/About.xml').getroot()
        self.assertEqual(about.findtext('packageId'),'sucro.ancientmedievaljapan.scenarios')
        self.assertFalse(about.findall('modDependencies/li'))
        self.assertFalse(any(c in about.findtext('name') for c in ':：'))
        self.assertEqual([n.text.lower() for n in about.findall('loadAfter/li')],[MO,GRAINS])
        for lang in ('English','Japanese'):
            dialog=ET.parse(ROOT/f'Languages/{lang}/Keyed/AMJC_Scenarios.xml').getroot()
            self.assertIsNotNone(dialog.find('AMJC_GameStart_NewVillage'))

class Packaging(unittest.TestCase):
    def test_subscriber_archive_matches_rimignore(self):
        rules=[x.strip() for x in (ROOT/'.rimignore').read_text().splitlines() if x.strip() and not x.startswith('#')]
        tracked=subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines()
        expected={p for p in tracked if not any(fnmatch.fnmatch(part,rule) for part in Path(p).parts for rule in rules)}
        data=subprocess.check_output(['git','archive','--format=zip','HEAD'],cwd=ROOT)
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            actual={p for p in archive.namelist() if not p.endswith('/')}
            self.assertEqual(actual,expected)
            self.assertTrue({"About/About.xml", "About/Manifest.xml", "About/Changelog.txt"}.issubset(actual))
            for path in actual:self.assertEqual(archive.read(path),(ROOT/path).read_bytes())

if __name__=='__main__':unittest.main()
