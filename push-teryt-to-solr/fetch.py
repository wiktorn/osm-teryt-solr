import itertools
import json
import tqdm

from converters import teryt


def main():
    ulic = teryt.UlicCache().get_cache()
    simc = teryt.SimcCache().get_cache()
    trt = teryt.TerytCache().get_cache()

    teryt_data = (trt.get(x).solr_json for x in trt.keys())
    simc_data = (simc.get(x).solr_json for x in simc.keys())
    ulic_data = (ulic.get(x).solr_json for x in ulic.keys())

    data = itertools.chain(teryt_data, simc_data, ulic_data, (('commit', {}),))

    # http://stackoverflow.com/questions/17991391/python-json-encode-with-same-keys-solr
    output = '{%s}' % ',\n'.join(['"{}": {}'.format(action, json.dumps(dictionary)) for action, dictionary in
                                  tqdm.tqdm(data, total=(len(trt.keys()) + len(simc.keys()) + len(ulic.keys())))])

    with open('terc.json', 'w+') as f:
        f.write(output)


if __name__ == '__main__':
    main()
