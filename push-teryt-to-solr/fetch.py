#!/usr/bin/env python3
import itertools
import json

from borders.converters import teryt


def main():
    terc = teryt.teryt()
    data_terc = [terc.get(k).solr_json for k in terc.keys()]
    simc = teryt.simc()
    data_simc = [simc.get(k).solr_json for k in simc.keys()]
    ulic = teryt.ulic()
    data_ulic = [ulic.get(k).solr_json for k in ulic.keys()]
    data = tuple(itertools.chain(data_terc, data_simc, data_ulic)) + (('commit', {}),)
    # http://stackoverflow.com/questions/17991391/python-json-encode-with-same-keys-solr
    output = '{%s}' % ',\n'.join(['"{}": {}'.format(action, json.dumps(dictionary)) for action, dictionary in data])
    with open('terc.json', 'w+') as f:
        f.write(output)


if __name__ == '__main__':
    main()
