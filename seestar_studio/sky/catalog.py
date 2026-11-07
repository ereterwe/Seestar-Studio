"""Read the bundled, attributed OpenNGC snapshot without network access."""
from ..i18n import source as ui_text, tr
import csv
import math
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
DATA = Path(__file__).resolve().parents[1] / 'catalog_data'
TYPES = {'G': ui_text('m0405'), 'GPair': ui_text('m0406'), 'GTrpl': ui_text('m0407'), 'GGroup': ui_text('catalog.group'), 'OCl': ui_text('m0340'), 'GCl': ui_text('m0411'), 'Cl+N': ui_text('m0341'), 'PN': ui_text('m0342'), 'HII': 'H-II-Region', 'Neb': ui_text('m0412'), 'RfN': ui_text('m0413'), 'EmN': ui_text('m0414'), 'DrkN': ui_text('catalog.dark'), 'SNR': ui_text('m0343'), '*': ui_text('m0408'), '**': ui_text('m0409'), '*Ass': ui_text('catalog.association'), 'Dup': ui_text('m0344'), 'NonEx': ui_text('m0345'), 'Other': ui_text('catalog.other')}

def normalized(text):
    text = ''.join((c for c in unicodedata.normalize('NFKD', text.casefold()) if not unicodedata.combining(c)))
    text = re.sub('\\b(messier|caldwell)\\s*', lambda m: 'm' if m[1] == 'messier' else 'c', text)
    text = re.sub('\\b(ngc|ic|m|c)\\s*0*(\\d+)', '\\1\\2', text)
    return re.sub('[^a-z0-9]', '', text)

def number(value):
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (ValueError, TypeError):
        return None

def sexagesimal(text, hours=False):
    if not text:
        return None
    pieces = text.lstrip('+-').split(':')
    value = sum((float(part) / 60 ** i for i, part in enumerate(pieces)))
    return value * (-1 if text.startswith('-') else 1) * (15 if hours else 1)

@dataclass(frozen=True)
class Target:
    id: str
    aliases: tuple[str, ...]
    kind: str
    ra: float | None
    dec: float | None
    constellation: str
    major: float | None
    minor: float | None
    magnitude: float | None
    band: str
    position_angle: float | None
    note: str = ''

    @property
    def title(self):
        preferred = next((a for a in self.aliases if re.fullmatch('M\\d+', a)), self.id)
        name = next((a for a in self.aliases if ' ' in a and (not a.startswith('Caldwell'))), '')
        return f'{preferred} · {name}' if name else preferred

    @property
    def valid(self):
        return self.ra is not None and self.dec is not None and (self.kind not in ('Dup', 'NonEx'))

    @property
    def description(self):
        return ui_text('m0351').format(p0=f'{TYPES.get(self.kind, self.kind)}', p1=f"{self.constellation or 'unbekannt'}", p2=f'{self.note}').strip()

    @property
    def suitability(self):
        if not self.valid:
            return ui_text('m0347')
        if self.major is None:
            return ui_text('m0348')
        size = ui_text('m0349') if self.major > 60 else ui_text('m0352') if self.major < 5 else ui_text('m0353')
        return size + ui_text('m0350')

class Catalog:

    def __init__(self, directory=DATA):
        self.targets = []
        for filename in ('NGC.csv', 'addendum.csv'):
            with (Path(directory) / filename).open(encoding='utf-8', newline='') as source:
                for row in csv.DictReader(source, delimiter=';'):
                    aliases = [row['Name']]
                    if row['M']:
                        aliases.append(f"M{int(row['M'])}")
                    for ident in row['Identifiers'].split(','):
                        match = re.fullmatch('C\\s*0*(\\d+)', ident)
                        if match:
                            aliases.append(f'C{int(match[1])}')
                    aliases += [n.strip() for n in row['Common names'].split(',') if n.strip()]
                    note = ''
                    if row['Name'] == 'NGC5866':
                        aliases.append('M102')
                        note = ui_text('m0354')
                    if row['Name'] == 'NGC7000':
                        aliases += ['North America Nebula', 'Nordamerikanebel']
                    if row['M'] == '045':
                        aliases += ['Pleiades', 'Plejaden']
                    v = number(row['V-Mag'])
                    self.targets.append(Target(row['Name'], tuple(dict.fromkeys(aliases)), row['Type'], sexagesimal(row['RA'], True), sexagesimal(row['Dec']), row['Const'], number(row['MajAx']), number(row['MinAx']), v if v is not None else number(row['B-Mag']), 'V' if v is not None else 'B', number(row['PosAng']), note))
        self.by_id = {t.id: t for t in self.targets}
        self._search = [(t, tuple((normalized(a) for a in t.aliases))) for t in self.targets]

    def search(self, query='', collection=ui_text('m0346'), limit=300):
        query = normalized(query)
        results = []
        for target, aliases in self._search:
            if collection != ui_text('m0346') and target.kind in ('Dup', 'NonEx'):
                continue
            if collection != ui_text('m0346') and (not any((re.fullmatch(('m' if collection == 'Messier' else 'c') + '\\d+', a) for a in aliases))):
                continue
            if not query or any((query in alias for alias in aliases)):
                results.append(((0 if query in aliases else 1) + (2 if not target.valid else 0), target))
        results.sort(key=lambda pair: (pair[0], normalized(pair[1].title)))
        return [t for _, t in results[:limit]]
