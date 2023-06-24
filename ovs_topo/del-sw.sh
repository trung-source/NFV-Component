#!/bin/bash
echo "K8s - Create 4 OVS - with port : 1GB"
#create 4 ovs in 1 physical machine (server 1)
   sudo ovs-vsctl del-br ovs1 
   sudo ovs-vsctl del-br ovs 
   sudo ovs-vsctl del-br ovs2
   sudo ovs-vsctl del-br ovs3
   sudo ovs-vsctl del-br ovs4
   sudo ovs-vsctl del-br ovs5
   sudo ovs-vsctl del-br ovs6
   sudo ovs-vsctl del-br router
   sudo ovs-vsctl del-br s2
   sudo ovs-vsctl show 
