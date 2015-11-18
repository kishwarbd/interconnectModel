"""
@package    cluster
This package creates Clusters of nodes(simian entities) of different size.
PrototypeGeminiTorusCielo creates gemini torus clusters with router and node(two types of entities).

"""

from SimianPie.simian import Simian
import nodes
import router
import interface
from collections import namedtuple #zzz


class Cluster(object):
    """
    Class that represents a supercomputer cluster. It consists of a number of nodes.
    """
    def __init__(self, simianEngine):
        self.num_nodes = 100 # number of compute nodes
        for i in xrange(self.num_nodes):
            simianEngine.addEntity("Node", nodes.Node, i)
     
class ClusterFromTopo(object):
    """
    @author     Mohammad Abu Obaida
    @param      x, y, z     Dimension of the torus topology
    This class represents Cielo or Hopper supercomputer cluster. It consists of a number of nodes
    connected in a gemini torus interconncetion with routers . All the axes are wrapped around
    in the topology. Basically it creates all the simulation entities.
    """
	
    def __init__(self, simianEngine, *args):
        """
        Default constructor of PrototypeGeminiTorusCielo. It takes dimension of x, y and z
        axes to initialize cluster consisting a total of x*y*z torus nodes.
        Each torus node has 1 router and 2 compute nodes connected to that router.
        @param  args[0]     torus x dimension
        @param  args[1]     torus y dimenstion   
        @param  args[2]     torus z dimenstion   
        """
        print "==========================================="
        print "-----------Initiating Cluster--------------"
        assert (len(args)>=2), "Assertion Error: Arguments missing"
        self.fileName = args[0]
        self.clusterProperties = args[1]      
        files = open(self.fileName)
        file_list =  files.readlines()
        self.totalRouters = 0

        interface_id = 0

        for eachLine in file_list:
               
            self.totalRouters += 1
            #print eachLine, self.totalRouters
            
            connected_to = []
            local_nodes = []  	#nodes that are in the same physical blade and/or forms a torus node
            words = eachLine.split(' ')
            tmpRouterID = int(words[0])
            tmptotalLocalNodes = int(words[1])
            
            for i in range(tmptotalLocalNodes):
                local_nodes.append(int(words[i+2]))               
            
            totalRouters = len(words) - len(local_nodes) - 2
            firstRouterIndex = len(local_nodes) + 2 # Verify later
            
            # first router: higher priority and so on
            for i in range(totalRouters):
                connected_to.append(int(words[firstRouterIndex + i]))
            #print "Connected to ", tmpRouterID, "routers are", connected_to            
            routerProperties = self.clusterProperties
            Point3D = namedtuple("Point3D", "x y z")
            torus_x = routerProperties["torus"]["torusX"]
            torus_y = routerProperties["torus"]["torusY"]
            torus_z = routerProperties["torus"]["torusZ"]
            torus_dimension = Point3D (x = torus_x, y = torus_y, z = torus_z)
            """
            We will add the simian entities here
            """
                        
            #mpiMsgSize  = self.clusterProperties['router']['mpiMsgSize']
            for i in range(tmptotalLocalNodes):
                simianEngine.addEntity("Node", nodes.GenericComputeNode, local_nodes[i], local_nodes[i], tmpRouterID, routerProperties["mpiMsgSize"], torus_dimension, self.clusterProperties["node_para"]) # sending  'nuid' arg            
            
        # Creating the interfaces for ROUTERS
            no_of_interfaces = len(connected_to)
            interface_id_list = []
            for i in range(no_of_interfaces):
                simianEngine.addEntity("Interface", interface.TorusInterface, interface_id, interface_id, tmpRouterID, connected_to[i])
                interface_id_list.append(interface_id)
                interface_id += 1
            #print "Router id: ", tmpRouterID, "Interfaces: ", interface_id_list 

            simianEngine.addEntity("Router", router.GenericHPCRouter, tmpRouterID, tmpRouterID, local_nodes, connected_to, routerProperties["mpiMsgSize"], torus_dimension, routerProperties["router_para"], interface_id_list) 

        print "-------------------------------------------"
        print "------Cluster Initiated Successfully-------"
        print "==========================================="

