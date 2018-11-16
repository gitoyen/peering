import requests
import yaml

GITOYEN_ASN = 20766
PEER_ASN_LIST = [20940,
                 26496,
                 714,
                 13768,
                 8359,
                 2119,
                 36236,
                 36692,
                 14340,
                 2635,
                 19679,
                 6507,
                 3265,
                 14413,
                 36459,
                 25459,
                 39386,
                 29686,
                 55818,
                 3262,
                 42459,
                 7500,
                 200020
                 ]

gitoyen_peering_factory = []
ses = requests.session()
peer = dict()

# List Gitoyen Factory with IPv6 avaidable
factory_request = ses.get("https://peeringdb.com//api/netixlan?asn=" + str(GITOYEN_ASN))
for factory in factory_request.json()['data']:
    if factory['ipaddr6'] is not None:
        gitoyen_peering_factory.append(factory)

for factory in gitoyen_peering_factory:
    name = (str(factory['name'])).split(' ')[0].lower()
    print("Generation en cours pour " + name)
    peer[name] = dict()
    for asn in PEER_ASN_LIST:
        info_request = ses.get(
            "https://peeringdb.com/api/netixlan?asn=" + str(asn) + "&ix_id=" + str(factory['ix_id']))
        result = info_request.json()['data']
        name_request = ses.get('https://peeringdb.com/api/net?asn=' + str(asn))
        peer[name][asn] = dict()
        peer[name][asn]['description'] = name_request.json()['data'][0]['name']
        peer[name][asn]['import'] = "AS" + str(asn)
        peer[name][asn]['export'] =  "AS-GITOYEN"
        peer[name][asn]['peerings'] = []
        delete = True
        for routeur in result:
            if routeur['ipaddr4'] is not None:
                peer[name][asn]['peerings'].append(routeur['ipaddr4'])
            if routeur['ipaddr6'] is not None:
                peer[name][asn]['peerings'].append(routeur['ipaddr6'])
            delete = False
        if delete:
            peer[name].pop(asn, None)

for gix in peer:
    with open("peers/"+gix+'.yml', 'w') as outfile:
        yaml.dump(peer[gix], outfile, default_flow_style=False)
        outfile.close()
