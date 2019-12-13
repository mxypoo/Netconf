#! /usr/bin/env python
#-*-coding:utf-8-*

from ncclient import manager
import xml.dom.minidom


# 基本配置
host="10.20.80.139"
user="admin"
password = "admin"
switchName="h3c"

#连接交换机
def connectSwitch():
    return manager.connect(host=host, port=830, username=user, password=password, hostkey_verify=False,device_params={'name':switchName})

def test():
    netconf_manager=connectSwitch()

    vlans_filter = '''
                      <top xmlns="http://www.h3c.com/netconf/data:1.0">
                         <Ifmgr>
                            <Interfaces>
                              <Interface>   
                                <IfIndex></IfIndex>
                                <Name></Name>
                              </Interface>    
                            </Interfaces>
                         </Ifmgr>
                      </top>
                     '''
    data = netconf_manager.get(('subtree', vlans_filter))

    # Pretty print


    xmlstr = xml.dom.minidom.parseString(str(data))
    pretty_xml_as_string = xmlstr.toprettyxml()
    print pretty_xml_as_string;

test()