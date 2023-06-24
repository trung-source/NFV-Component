from crypt import methods
import json
import requests
from struct import pack
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib.packet import ipv4, tcp, ether_types, in_proto


class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.mac_to_port = {}

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # install table-miss flow entry
        #
        # We specify NO BUFFER to max_len of the output action due to
        # OVS bug. At this moment, if we specify a lesser number, e.g.,
        # 128, OVS will send Packet-In with invalid buffer_id and
        # truncated packet data. In that case, we cannot output packets
        # correctly.  The bug has been fixed in OVS v2.1.0.
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # If you hit this you might want to increase
        # the "miss_send_length" of your switch
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        dst = eth.dst
        src = eth.src

        dpid = format(datapath.id, "d").zfill(16)
        self.mac_to_port.setdefault(dpid, {})

        # self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)
        
        if eth.ethertype == ether_types.ETH_TYPE_IP:
            packet_ipv4= pkt.get_protocol(ipv4.ipv4)
            ip_src = packet_ipv4.src
            ip_dst = packet_ipv4.dst
            protocol_ipv4 = packet_ipv4.proto
            if protocol_ipv4 == in_proto.IPPROTO_TCP:
                packet_tcp= pkt.get_protocol(tcp.tcp)
                port_src = packet_tcp.src_port
                port_dst = packet_tcp.dst_port

                self.logger.info("packet in %s %s %s %s", ip_src, ip_dst, port_src, port_dst)
                dict_key = ["ip_src", "ip_dst","port_src", "port_dst"]
                dict_value = [ip_src, ip_dst, port_src, port_dst]
                mydict = {k:v for k,v in zip(dict_key,dict_value)}
                json_merge = json.dumps(mydict)

                post = requests.post(url = "http://127.0.0.1:5000/read", data = json_merge)

                result_post = post.text 
                self.logger.info("type %s %s", type(result_post),result_post)
                # check ton tai
                # thi minh cho củl updateroute


                
            # dump cac thong tin ip dich, nguon; port dich, nguon thanh cau truc json
            # su dung thu vien request // search google de gui len web server tai dia chi /read 127.0.0.1:5000/read
            # 200: thanh cong, 404: loi webserver
        
        

            # Phia ben webserver em tao func doc tai dia chi /read roi doc duoc file json
            # get du lieu tu file json roi luu vao bien(o ben webserver)
            # Gui phan hoi ve: "Toi da nhan thanh cong"







        # # learn a mac address to avoid FLOOD next time.
        # self.mac_to_port[dpid][src] = in_port

        # if dst in self.mac_to_port[dpid]:
        #     out_port = self.mac_to_port[dpid][dst]
        # else:
        #     out_port = ofproto.OFPP_FLOOD

        # actions = [parser.OFPActionOutput(out_port)]

        # # install a flow to avoid packet_in next time
        # if out_port != ofproto.OFPP_FLOOD:
        #     match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
        #     # verify if we have a valid buffer_id, if yes avoid to send both
        #     # flow_mod & packet_out
        #     if msg.buffer_id != ofproto.OFP_NO_BUFFER:
        #         self.add_flow(datapath, 1, match, actions, msg.buffer_id)
        #         return
        #     else:
        #         self.add_flow(datapath, 1, match, actions)
        # data = None
        # if msg.buffer_id == ofproto.OFP_NO_BUFFER:
        #     data = msg.data

        # out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
        #                           in_port=in_port, actions=actions, data=data)
        # datapath.send_msg(out)