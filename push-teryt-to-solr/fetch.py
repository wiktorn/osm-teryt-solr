#!/usr/bin/env python3

from urllib.request import urlopen
from bs4 import BeautifulSoup
from collections import namedtuple
import io
import json
import lxml.etree
import zipfile

# TODO - add names to TERC dictionary




# structure:
# województwo:
#   - id == terc
#   - terc == terc
#   - value == nazwa
# powiat:
#   - id == terc
#   - parent == województwo.terc
#   - terc == terc
#   - value == nazwa
# gmina:
#   - id == terc
#   - parnet == powiat.terc
#   - terc == terc
#   - value == nazwa
# miejscowość:
#   - id == simc
#   - parent == gmina.terc lub miejscowość.simc
#   - simc
#   - value - nazwa
#   - wojeództwo, powiat, gmina
# ulica:
#   - id = symul
#   - sim = lista [simc]
#   - nazwa

def groupby(lst, keyfunc=lambda x: x, valuefunc=lambda x: x):
    ret = {}
    for i in lst:
        key = keyfunc(i)
        try:
            entry = ret[key]
        except KeyError:
            entry = []
            ret[key] = entry
        entry.append(valuefunc(i))
    return ret


def terc_key(dct):
    return dct.get('woj') + dct.get('pow', '') + dct.get('gmi', '') + dct.get('rodz', '')

conf = {
    'WMRODZ':
        {
            'key': lambda x: x.get('rm'),
            'value': lambda x: x.get('nazwa_rm')
        },
    'TERC':
        {
            'key': terc_key,
            'value': lambda x: x.get('nazwadod') + ' ' + x.get('nazwa') 
        },
    'SIMC':
        {
            'key': lambda x: (x.get('sym'), x.get('sym_ul')),
            'value': lambda x: {
                'terc': db['TERC'][terc_key(x)],

            }
        }
}

terc_rodz_map = {
    '1': 'gmina miejska',
    '2': 'gmina wiejska',
    '3': 'gmina miejsko-wiejska',
    '4': 'miasto w gminie miejsko-wiejskiej',
    '5': 'obszar wiejski w gminie miejsko-wiejskiej',
    '8': 'dzielnica m.st. Warszawa',
    '9': 'delegatury w gminach miejskich',
}

ulic_cecha_map = {
   'UL.'  : 'Ulica', 
   'AL.'  : 'Aleja', 
   'PL.'  : 'Plac', 
   'SKWER': 'Skwer', 
   'BULW.': 'Bulwar', 
   'RONDO': 'Rondo', 
   'PARK' : 'Park', 
   'RYNEK': 'Rynek', 
   'SZOSA': 'Szosa', 
   'DROGA': 'Droga',
   'OS.'  : 'Osiedle',
   'OGRÓD': 'Ogród', 
   'WYSPA': 'Wyspa', 
   'WYB.' : 'Wybrzeże', 
   'INNE' : ''
}

class TercEntry(object):
    def __init__(self, dct):
        self.woj = dct.get('woj')
        self.powiat = dct.get('pow')
        self.gmi = dct.get('gmi')
        self.rodz = dct.get('rodz')
        self.rodz_nazwa = terc_rodz_map.get(dct.get('rodz'), '') if self.rodz else {2: 'województwo', 4: 'powiat'}[len(self.terc)]
        self.nazwadod = dct.get('nazwadod', '')
        self.nazwa = dct.get('nazwa')

    @property
    def terc_base(self):
        return (y for y in 
            (self.woj, self.powiat) + ((self.gmi, self.rodz) if self.gmi else ())
            if y
        )
    @property
    def terc(self):
        return "".join(y for y in 
            (self.woj, self.powiat) + ((self.gmi, self.rodz) if self.gmi else ())
            if y
        )

    @property
    def parent_terc(self):
        if self.gmi:
            return "".join((self.woj, self. powiat))
        if self.powiat:
            return "".join((self.woj,))
        return ""

    @property
    def json(self):
        return (
            "add", {
                "doc": {
                    'id': "terc_" + self.terc,
                    'parent': ("terc_" + self.parent_terc) if self.parent_terc else '',
                    'terc': self.terc,
                    'rodzaj': self.rodz_nazwa ,
                    'value': (self.nazwadod + ' ' + self.nazwa).strip(),
                    'typ': 'terc',
                },
            'boost': 7 - len(self.parent_terc) 
            }
        )

class SimcEntry(object):
    def __init__(self, dct):
        self.woj = teryt[dct.get('woj')]
        self.powiat = teryt[dct.get('woj') + dct.get('pow')]
        self.terc = dct.get('woj') + dct.get('pow') + dct.get('gmi') + dct.get('rodz_gmi')
        self.gmi = teryt[dct.get('woj') + dct.get('pow') + dct.get('gmi') + dct.get('rodz_gmi')]
        self.rm = wmrodz[dct.get('rm')]
        self.nazwa = dct.get('nazwa')
        self.sym = dct.get('sym')
        self.parent = None
        if dct.get('sym') != dct.get('sympod'):
            self.parent = dct.get('sympod')

    @property
    def json(self):
        return (
            "add", {
                "doc": {
                    'id': 'simc_' + self.sym,
                    'parent': ('simc_' + self.parent) if self.parent else ('terc_' + self.terc),
                    #'terc': self.terc,
                    'rodzaj': self.rm,
                    'value': self.nazwa,
                    'simc': self.sym,
                    'wojewodztwo': self.woj,
                    'powiat': self.powiat,
                    'gmina': self.gmi,
                    'typ': 'simc',
                }
            }
        )

class BasicEntry(object):
    def __init__(self, dct):
        for i in dct.keys():
            setattr(self, i, dct[i])

def mapstreet(cecha, nazwa1, nazwa2):
    def mapper(s, c):
        if s.casefold().startswith(c.casefold()):
            return s[len(c):].strip()
        elif s.casefold().startswith(ulic_cecha_map[c.upper()].casefold()):
            return s[len(ulic_cecha_map.get(c.upper())):].strip()
        return s
    nazwa1 = mapper(nazwa1, cecha)
    nazwa2 = mapper(nazwa2, cecha)
    return " ".join((x for x in (ulic_cecha_map.get(cecha.upper()), nazwa1, nazwa2) if x))

class UlicEntry(object):
    def __init__(self, dct):
        self.woj = teryt[dct.get('woj')]
        self.powiat = teryt[dct.get('woj') + dct.get('pow')]
        self.terc = dct.get('woj') + dct.get('pow') + dct.get('gmi') + dct.get('rodz_gmi')
        self.gmi = teryt[dct.get('woj') + dct.get('pow') + dct.get('gmi') + dct.get('rodz_gmi')]
        self.miejscowosc = simc[dct.get('sym')]
        self.sym = dct.get('sym')
        self.symul = dct.get('sym_ul')
        self.cecha = ulic_cecha_map[dct.get('cecha').upper()]
        self.nazwa = mapstreet(dct.get('cecha', ''), dct.get('nazwa_2', ''), dct.get('nazwa_1', ''))

    @property
    def json(self):
        return (
            "add", {
                "doc": {
                    'id': 'ulic:' + self.sym + self.symul,
                    'parent': 'simc_' + self.sym,
                    'terc': self.terc,
                    'value': self.nazwa,
                    'cecha': self.cecha,
                    'symul': self.symul,
                    'wojewodztwo': self.woj,
                    'powiat': self.powiat,
                    'gmina': self.gmi,
                    'miejscowosc': self.miejscowosc
                }
            }
        )


teryt = {}
wmrodz = {}
simc = {}

def zip_read(url, fname):
    dictionary_zip = zipfile.ZipFile(io.BytesIO(urlopen(url).read()))
    return dictionary_zip.read(fname)

def row_as_dict(elem):
    return dict(
        (x.get('name').lower(), x.text.strip()) for x in elem.iter('col') if x.text
    )



def init_teryt_page():
    soup = BeautifulSoup(urlopen("http://www.stat.gov.pl/broker/access/prefile/listPreFiles.jspa"))

    files = dict(
            (
                x+'.xml', 
                'http://www.stat.gov.pl/broker/access/prefile/' + soup.find('td', text=x).parent.find_all('a')[1]['href']
            ) for x in ('ULIC', 'TERC', 'SIMC', 'WMRODZ')
    )
    def get_dict(name, cls):
        tree = lxml.etree.XML(zip_read(files[name], name))
        return tuple(cls(row_as_dict(x)) for x in tree.find('catalog').iter('row'))

    data_terc = get_dict('TERC.xml', TercEntry)
    teryt.update((x.terc, ' '.join((z for z in (x.rodz_nazwa, x.nazwa) if z))) for x in data_terc)

    data_wmrodz = get_dict('WMRODZ.xml', BasicEntry)
    wmrodz.update((x.rm, x.nazwa_rm) for x in data_wmrodz)

    data_simc = get_dict('SIMC.xml', SimcEntry)
    simc.update((x.sym, x.nazwa) for x in data_simc)

    data_ulic = get_dict('ULIC.xml', UlicEntry)
    data_groupped = groupby(data_ulic, lambda x: x.symul)
    
    def get_min(field, lst):
        return min(map(lambda x: getattr(x, field), lst))

    data_ulic = tuple(
        (
            "add", {
                "doc": {
                    'id':     'ulic:' + get_min('symul', x), 
                    'parent': [('simc_' + entry.sym) for entry in x],
                    'miejscowosc': [entry.miejscowosc for entry in x],
                    #'terc': [entry.terc for entry in x],
                    'value': x[0].nazwa, # belive that TERC is consistent
                    'symul': x[0].symul,
                    'typ': 'ulic',
                }
            }
        ) for x in (sorted(z, key=lambda o: o.miejscowosc) for z in data_groupped.values())
    )
        
    data = tuple(x.json for x in (data_terc + data_simc)) + data_ulic + (('commit' ,{}),)

    # http://stackoverflow.com/questions/17991391/python-json-encode-with-same-keys-solr
    output = '{%s}' % ',\n'.join(['"{}": {}'.format(action, json.dumps(dictionary)) for action, dictionary in data])
    
    with open('terc.json', 'w+') as f:
        f.write(output)
    #json.dump(data, open('terc.json', 'w+'), indent=4)

def main():
    wmrodz = init_teryt_page()

if __name__ == '__main__':
    main()
