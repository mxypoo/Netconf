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

#增加VLAN
def addVLAN(vlan_id,vlan_name,vlan_des,ip,mask):
    m=connectSwitch() #创建对象
    vlans_change_filter = '''
                          <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
                             <top xmlns="http://www.h3c.com/netconf/config:1.0">
                                 <VLAN>
                                    <VLANs>
                                       <VLANID>
                                          <ID>%s</ID>
                                          <Name>%s</Name>
                                          <Description>%s</Description>
                                          <Ipv4>
                                             <Ipv4Address>%s</Ipv4Address>
                                             <Ipv4Mask>%s</Ipv4Mask>
                                          </Ipv4>                                         
                                       </VLANID>
                                    </VLANs>
                                 </VLAN>
                             </top>
                          </config> 
                          ''' % (vlan_id,vlan_name,vlan_des,ip,mask)
    data= m.edit_config(target='running',config=vlans_change_filter,default_operation='replace');
    # 格式化输出响应
    xmlstr = xml.dom.minidom.parseString(str(data))
    pretty_xml_as_string = xmlstr.toprettyxml()
    print pretty_xml_as_string;

addVLAN(100,"test100","it's a test vlan100","1.1.1.1","255.255.255.0")

#将接口配置为trunk口，并放通vlan
def port2trunk(port_index,vlan_id):
    m=connectSwitch() #创建对象
    vlans_change_filter = '''
                          <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
                             <top xmlns="http://www.h3c.com/netconf/config:1.0">
                                 <VLAN>
                                          <TrunkInterfaces>
                                                  <Interface>
                                                         <IfIndex>%s</IfIndex>
                                                         <PermitVlanList>%s</PermitVlanList>
                                                          <PVID>1</PVID>
                                                  </Interface>
                                           </TrunkInterfaces>
                                 </VLAN>
                             </top>
                          </config> 
                          ''' % (port_index,vlan_id)
    data= m.edit_config(target='running',config=vlans_change_filter,default_operation='replace');
    # 格式化输出响应
    xmlstr = xml.dom.minidom.parseString(str(data))
    pretty_xml_as_string = xmlstr.toprettyxml()
    print pretty_xml_as_string;

port2trunk(2,888)

#创建ACL,分别匹配出入方向流量。默认为ip类型流量
def createACL(aclNubmer,ip):
    m=connectSwitch() #创建对象
    vlans_change_filter = '''
                          <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
                             <top xmlns="http://www.h3c.com/netconf/config:1.0">
                                <ACL>
                                   <Groups>
                                       <Group>
                                           <GroupType>1</GroupType>
                                           <GroupID>%s</GroupID>
                                       </Group>
                                       <Group>
                                           <GroupType>1</GroupType>
                                           <GroupID>%s</GroupID>
                                       </Group>
                                   </Groups>
                                   <IPv4AdvanceRules>
                                       <Rule>
                                           <GroupID>%s</GroupID>
                                           <RuleID>0</RuleID>
                                           <Action>2</Action>
                                           <ProtocolType>256</ProtocolType>
                                           <SrcAny>false</SrcAny>
                                           <SrcIPv4>
                                               <SrcIPv4Addr>%s</SrcIPv4Addr>
                                               <SrcIPv4Wildcard>0.0.0.0</SrcIPv4Wildcard>
                                           </SrcIPv4>
                                       </Rule>
                                       <Rule>
                                           <GroupID>%s</GroupID>
                                           <RuleID>0</RuleID>
                                           <Action>2</Action>
                                           <ProtocolType>256</ProtocolType>
                                           <DstAny>false</DstAny>
                                           <DstIPv4>
                                               <DstIPv4Addr>%s</DstIPv4Addr>
                                               <DstIPv4Wildcard>0.0.0.0</DstIPv4Wildcard>
                                           </DstIPv4>  
                                       </Rule>  
                                   </IPv4AdvanceRules>  
                                </ACL>
                             </top>
                          </config> 
                          ''' % (aclNubmer,aclNubmer +1,aclNubmer,ip,aclNubmer+1,ip)
    data= m.edit_config(target='running',config=vlans_change_filter,default_operation='replace');
    # 格式化输出响应
    xmlstr = xml.dom.minidom.parseString(str(data))
    pretty_xml_as_string = xmlstr.toprettyxml()
    print pretty_xml_as_string;

createACL(3100,'20.20.20.20')

#创建pbr
def createPBR(pbrName,aclNumber,nexthopIP):
    m=connectSwitch() #创建对象
    vlans_change_filter = '''
                          <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
                             <top xmlns="http://www.h3c.com/netconf/config:1.0">
                                <PBR>
                                   <PBRPolicyNode> 
                                       <PolicyNode> 
                                         <AddressType>0</AddressType>  
                                         <PolicyName>%sout</PolicyName>  
                                         <NodeID>0</NodeID>
                                         <ACLNumber>%s</ACLNumber>  
                                         <Mode>1</Mode> 
                                       </PolicyNode> 
                                       <PolicyNode> 
                                         <AddressType>0</AddressType>  
                                         <PolicyName>%sin</PolicyName>  
                                         <NodeID>0</NodeID>
                                         <ACLNumber>%s</ACLNumber>  
                                         <Mode>1</Mode> 
                                       </PolicyNode> 
                                   </PBRPolicyNode>
                                   <PBRApplyNexthop>
                                     <ApplyNexthop>
                                       <AddressType>0</AddressType>  
                                       <PolicyName>%sout</PolicyName>  
                                       <NodeID>0</NodeID>  
                                       <Mode>0</Mode>
                                       <VrfIndex>0</VrfIndex>  
                                       <IpAddress>%s</IpAddress>
                                     </ApplyNexthop>
                                     <ApplyNexthop>
                                       <AddressType>0</AddressType>  
                                       <PolicyName>%sin</PolicyName>  
                                       <NodeID>0</NodeID>  
                                       <Mode>0</Mode>
                                       <VrfIndex>0</VrfIndex>  
                                       <IpAddress>%s</IpAddress>
                                     </ApplyNexthop>
                                   </PBRApplyNexthop>
                                 </PBR>
                             </top>
                          </config> 
                          ''' % (pbrName,aclNumber,pbrName,aclNumber+1,pbrName,nexthopIP,pbrName,nexthopIP)
    data= m.edit_config(target='running',config=vlans_change_filter,default_operation='replace');
    # 格式化输出响应
    xmlstr = xml.dom.minidom.parseString(str(data))
    pretty_xml_as_string = xmlstr.toprettyxml()
    print pretty_xml_as_string;

createPBR('pbr100',3100,'1.1.1.206')

#应用PBR到上下行接口
def applyPBR(pbrName,vlan1Ifindex,vlan2Ifindex):
    m=connectSwitch() #创建对象
    vlans_change_filter = '''
                          <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
                             <top xmlns="http://www.h3c.com/netconf/config:1.0">
                                <PBR> 
                                   <PBRIfPolicy>
                                      <IfPolicy>
                                          <AddressType>0</AddressType>
                                          <IfIndex>%s</IfIndex>
                                          <PolicyName>%sin</PolicyName>
                                      </IfPolicy>
                                      <IfPolicy>
                                          <AddressType>0</AddressType>
                                          <IfIndex>%s</IfIndex>
                                          <PolicyName>%sout</PolicyName>
                                      </IfPolicy>
                                   </PBRIfPolicy>
                                </PBR>
                             </top>
                          </config> 
                          ''' % (vlan1Ifindex,pbrName,vlan2Ifindex,pbrName)
    data= m.edit_config(target='running',config=vlans_change_filter,default_operation='replace');
    print data
    # 格式化输出响应
    xmlstr = xml.dom.minidom.parseString(str(data))
    pretty_xml_as_string = xmlstr.toprettyxml()
    print pretty_xml_as_string;

applyPBR('pbr100',637,636)





