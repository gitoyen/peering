#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ipaddr
import yaml
import sys
import os
import glob
from jinja2 import Environment, FileSystemLoader
from termcolor import colored


def parse_peers(peer_file, version):
    """parse_peers: Just a simple function for peers parsing
    :peer_file: The YAML peer file to parse
    :returns: Just a return code if the file is correctly parsed or not

    """

    peering_flat = open(peer_file).read()
    ixp = os.path.splitext(os.path.basename(peer_file))[0]

    try:
        peerings = yaml.safe_load(peering_flat)
    except:
        print colored('ERROR', 'red') + ": the peers.yaml file could not be parsed.. please check \
    your syntax"
        sys.exit(2)

    for asn in peerings:
        for keyword in ['export', 'import', 'description']:
            if keyword not in peerings[asn]:
                print colored('ERROR', 'red') + ": missing %s statement in stanza %s" % (keyword, asn)
                sys.exit(2)

        acceptable_exports = ['AS-GITOYEN', 'NOT ANY', 'ANY']
        if not peerings[asn]['export'] in acceptable_exports:
            print colored('ERROR', 'red') + ": export must be one of the following: %s" \
            % " ".join(acceptable_exports)
            sys.exit(2)

        session = 0
        for peer in peerings[asn]['peerings']:
            try:
                peer_ip = ipaddr.IPAddress(peer)
                if type(ipaddr.IPAddress(peer_ip)) is ipaddr.IPv4Address and version == 4:
                    neighbor_ipv4 = peer_ip
                    session += 1
                elif type(ipaddr.IPAddress(peer_ip)) is ipaddr.IPv6Address and version == 6:
                    neighbor_ipv6 = peer_ip
                    session += 1
            except ValueError:
                print colored('ERROR', 'red') + ": %s in %s is not a valid IP" % (peer, asn)
                sys.exit(2)

            try:
                limit_ipv4 = peerings[asn]['limit_ipv4']
            except:
                limit_ipv4 = False

            try:
                limit_ipv6 = peerings[asn]['limit_ipv6']
            except:
                limit_ipv6 = False

            env = Environment(loader=FileSystemLoader('./'))

            if version == 6 and 'neighbor_ipv6' in locals() and type(ipaddr.IPAddress(peer_ip)) is ipaddr.IPv6Address:
                #Generate IPV6
                tpl = env.get_template('templates/bird_v6.j2')

                print tpl.render(neighbor_as=asn, description=
                peerings[asn]['description'], export_as=peerings[asn]['export'],
                           import_as=peerings[asn]['import'],
                           neighbor_ipv6=neighbor_ipv6, ix_name=
                           ixp, limit_ipv6=limit_ipv6, session_num=session).encode('utf-8').strip()
            else:
                if 'neighbor_ipv4' in locals() and type(ipaddr.IPAddress(peer_ip)) is ipaddr.IPv4Address:
                    #Generate IPV4
                    tpl = env.get_template('templates/bird_v4.j2')

                    print tpl.render(neighbor_as=asn, description=
                    peerings[asn]['description'], export_as=peerings[asn]['export'],
                               import_as=peerings[asn]['import'], neighbor_ipv4=
                               neighbor_ipv4,ix_name=ixp,
                               limit_ipv4=limit_ipv4, session_num=session).encode('utf-8').strip()


#Basicly check arg
if len(sys.argv) == 2:
    for peer_files in glob.glob('peers/*.yml'):
        parse_peers(peer_files, int(sys.argv[1]))
else:
    print("Invalide argument number, You must specify IP version 4 or 6")
