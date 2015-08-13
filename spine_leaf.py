#!/usr/bin/python

'''
  Copyright (c) 2015 Ciena Corporation.
  All rights reserved. This program and the accompanying materials
  are made available under the terms of the Eclipse Public License v1.0
  which accompanies this distribution, and is available at
  http://www.eclipse.org/legal/epl-v10.html
'''

'''
Usage example: sudo python spine_leaf.py <number_of_spine_switches> <number_of_leaf_switches> <primary_controller_IP> <secondary_controller_IP>
               sudo python spine_leaf.py 2 4 172.17.0.1 172.17.0.2

You can also configure the link Bandwidth, Delay, Loss, Max Queue_size for the spine-to-leaf links and host-to-leaf 
connections by changing the link_spine_leaf and link_host_leaf global variables in the script.

Default is: Bandwidth=100, Delay=1ms, Loss=0, Max Queue Size=10000

'''

from optparse import OptionParser
import os
import sys
import time
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import irange,dumpNodeConnections
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.node import OVSSwitch, Controller, RemoteController

######################################
######### Global Variables ###########
######################################
spineList = [ ]
leafList = [ ]
switchList = [ ]

link1 = dict(bw=100, delay='1ms', loss=0, max_queue_size=10000, use_htb=True)
link2 = dict(bw=15, delay='2ms', loss=0, max_queue_size=1000, use_htb=True)
link3 = dict(bw=10, delay='5ms', loss=0, max_queue_size=1000, use_htb=True)
link4 = dict(bw=5, delay='10ms', loss=0, max_queue_size=500, use_htb=True)
link5 = dict(bw=1, delay='15ms', loss=0, max_queue_size=100, use_htb=True)

link_spine_leaf = link1
link_host_leaf = link1

######################################
###### Define topologies here ########
######################################

#Data center Spine Leaf Network Topology
class dcSpineLeafTopo(Topo):
   "Linear topology of k switches, with one host per switch."

   def __init__(self, k, l, **opts):
       """Init.
           k: number of switches (and hosts)
           hconf: host configuration options
           lconf: link configuration options"""

       super(dcSpineLeafTopo, self).__init__(**opts)

       self.k = k
       self.l = l 

       for i in irange(0, k-1):
           spineSwitch = self.addSwitch('s%s%s' % (1,i+1))

           spineList.append(spineSwitch)

       for i in irange(0, l-1):
           leafSwitch = self.addSwitch('l%s%s' % (2, i+1))

           leafList.append(leafSwitch)
           host1 = self.addHost('h%s' % (i+1))
           #host12 = self.addHost('h%s' % (i+1))
           #hosts1 = [ net.addHost( 'h%d' % n ) for n in 3, 4 ]

           "connection of the hosts to the left tor switch "
           self.addLink(host1, leafSwitch, **link_host_leaf)
           #self.addLink(host12, leafSwitch)

       for i in irange(0, k-1):
           for j in irange(0, l-1): #this is to go through the leaf switches
                 self.addLink(spineList[i], leafList[j], **link_spine_leaf)

def simpleTest():

   # argument to put in either remote or local controller

   "Create and test a simple network"
   c0 = RemoteController( 'c0', ip=str(sys.argv[3]) )
   c1 = RemoteController( 'c1', ip=str(sys.argv[4]) )


   class MultiSwitch( OVSSwitch ):
            "Custom Switch() subclass that connects to different controllers"
   def start( self, controllers ):
          return OVSSwitch.start( self, [ cmap[ self.name ] ] )

   topo = dcSpineLeafTopo(k=int(sys.argv[1]), l=int(sys.argv[2]))
   switchList = spineList + leafList
   net = Mininet(  topo=topo, switch=MultiSwitch, build=False, link=TCLink )

   print "connecting all SWITCHES to controller with cmap"
   cString = "{"
   for i in irange(0, len(switchList)-1):
        if i != len(switchList)-1:
           tempCString = "'" + switchList[i] + "'" + " : [c0,c1] "
        else:
           tempCString = "'" + switchList[i] + "'" + " : [c0,c1] "
        cString += tempCString

   cmapString = cString + "}"

   cmap = cmapString


   net.addController(c0)
   net.addController(c1)

   net.build()

   c0.start()
   c1.start()
   #switchList[1].start([c0, c1])
   #switchList[2].start([c0, c1])

   '''
    for s in switchList:
    print s
    #s.start([c0, c1])
    print ("starting" + s + " with c0 and c1") 
   '''



   net.start()
   print "Dumping host connections"
   dumpNodeConnections(net.hosts)

   CLI( net )
   net.stop()

if __name__ == '__main__':
   setLogLevel('info')
   simpleTest()
