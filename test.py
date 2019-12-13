#! /usr/bin/env python
#-*-coding:utf-8-*

from ncclient import manager
import xml.dom.minidom
from pprint import pprint

# 基本配置
host="192.168.1.2"
user="admin"
password = "admin"
switchName="h3c"


with manager.connect(host=host, port=830, username=user, password=password, hostkey_verify=False,device_params={'name':switchName}) as m:
    #c = m.get_config(source='running').data_xml
    # with open("%s.xml" % host, 'w') as f:
    #    f.write(c)

    vlans_filter = '''
                    <top xmlns="http://www.h3c.com/netconf/data:1.0" xmlns:base="http://www.h3c.com/netconf/base:1.0">
                        <VLAN>
                        </VLAN>
                    </top>
                   '''

    vlans = m.get(('subtree', vlans_filter))
    print vlans

    vlans_change_filter = '''
<config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
    <top xmlns="http://www.h3c.com/netconf/config:1.0">
        <VLAN>
            <VLANs>
                <VLANID>
                    <ID>999</ID>
                    <Description>test</Description>
                    <Name>test</Name>
                    <Ipv4>
                        <Ipv4Address>192.168.222.1</Ipv4Address>
                        <Ipv4Mask>255.255.255.0</Ipv4Mask>
                    </Ipv4>
                </VLANID>
            </VLANs>
        </VLAN>
    </top>
</config>
                          '''
    c= m.edit_config(target='running',config=vlans_change_filter,default_operation='replace');


