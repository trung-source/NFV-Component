#!/bin/bash
echo "K8s - Create 4 OVS - with port : 1GB"
#create 4 ovs in 1 physical machine (server 1)
   sudo ovs-vsctl del-br ovs1 
   sudo ovs-vsctl del-br ovs 
   sudo ovs-vsctl del-br ovs2
   sudo ovs-vsctl del-br ovs3
   sudo ovs-vsctl del-br ovs4
   # add 4 bridges 
   sudo ovs-vsctl add-br ovs1 
   sudo ovs-vsctl add-br ovs2
   sudo ovs-vsctl add-br ovs3
   sudo ovs-vsctl add-br ovs4

   # assigned port for bridge
#    sudo ovs-vsctl add-port ovs3 enp7s0f1
#    sudo ovs-vsctl add-port ovs2 eno2
#    sudo ovs-vsctl add-port ovs3 eno3 
#    sudo ovs-vsctl add-port ovs4 eno4
 
    # create patch for ovs1 and ovs4
   sudo ovs-vsctl \
           -- add-port ovs1 patch14 \
           -- set interface patch14 type=patch options:peer=patch41 \
           -- add-port ovs4 patch41 \
           -- set interface patch41 type=patch options:peer=patch14 
   # create patch for ovs1 and ovs2
    sudo ovs-vsctl \
            -- add-port ovs1 patch12 \
            -- set interface patch12 type=patch options:peer=patch21 \
            -- add-port ovs2 patch21 \
            -- set interface patch21 type=patch options:peer=patch12 
   #  create patch for ovs2 and ovs3
   sudo ovs-vsctl \
           -- add-port ovs2 patch23 \
           -- set interface patch23 type=patch options:peer=patch32 \
           -- add-port ovs3 patch32 \
           -- set interface patch32 type=patch options:peer=patch23 
     # create patch for ovs3 and ovs4
   sudo ovs-vsctl \
           -- add-port ovs3 patch34 \
           -- set interface patch34 type=patch options:peer=patch43 \
           -- add-port ovs4 patch43 \
           -- set interface patch43 type=patch options:peer=patch34 

   # up port
   sudo ifconfig ovs1 up
   sudo ifconfig ovs2 up
   sudo ifconfig ovs3 up
   sudo ifconfig ovs4 up

   #set controller for switches 
   sudo ovs-vsctl set-controller ovs1 tcp:192.168.122.60:6653
   sudo ovs-vsctl set-controller ovs2 tcp:192.168.122.60:6653
   sudo ovs-vsctl set-controller ovs3 tcp:192.168.122.60:6653 tcp:192.168.122.190:6653
   sudo ovs-vsctl set-controller ovs4 tcp:192.168.122.60:6653


   # set dpid for each switch
   sudo ovs-vsctl set bridge ovs1 other-config:datapath-id=0000000000000002
   sudo ovs-vsctl set bridge ovs2 other-config:datapath-id=0000000000000003
   sudo ovs-vsctl set bridge ovs3 other-config:datapath-id=0000000000000004
   sudo ovs-vsctl set bridge ovs4 other-config:datapath-id=0000000000000005

   #show ovs
   sudo ovs-vsctl show 
