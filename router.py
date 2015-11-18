"""
@package    router
@author     Mohammad Abu Obaida
This package implements the Router and GeminiRouter Classes.
"""

from SimianPie.entity import Entity
from packet import *
from ringBuffer import *
from SimianPie.utils import SimianError
import sys #zzz


class Router(Entity):
	"""
    @author     Mohammad Abu Obaida
	Base class for Router. All other router classes will derive from this.
    It inherits simian Entity class.
	"""
	def __init__(self, baseInfo, *args):
		super(Router, self).__init__(baseInfo)

class GenericHPCRouter(Router):
    """
    @author     Mohammad Abu Obaida
    This class defines the details of a gemini router, the Router sitting between Torus nodes.
    Each of the torus node has one of such routers.
    It implements 7 queues for +X, +y, +Z, -X, -Y, -Z links and one for its local nodes. It applies
    propagation delays and processing delays to the packet before forwarding it.
    It is responsible for casuing packets to drop and make routing decisions.
    We are initiating router in an entity.
    """
    def __init__(self, baseInfo, *args, **kwargs):
        """
        Constructor for the GeminiRouter class.
        """
        super(GenericHPCRouter, self).__init__(baseInfo)
        assert (len(args)>3), "Assertion error: GeminiRouter uid, node1_id, node2_id, connected_routers_list  Required!"
        self.ruid = args[0] 			# router unique id, 1 router per physical blade
        self.local_nodes = args[1]		# nodes that are local to a router.
        self.local_links = args[2]	    # List of 6 + 1 integer-ids for the neighbors
        self.mpiMsgSize = args[3]           # MPI message size or transfer size
        
        self.torus_dimension = args[4]  # (Max_X, Max_Y, Max_Z)

        self.bwX =  args[5]["bwX"]  #BW in Bytes/s
        self.bwY =  args[5]["bwY"]
        self.bwZ =  args[5]["bwZ"]
        self.bwLN = args[5]["bwLN"] #Bandwidth of two local node, 10 Gbps

        self.buffer_size = args[5]["bufferSize"]            	#Buffer size in Bytes (1 MB here)

        self.hop_limit = 2*(self.torus_dimension[0]+self.torus_dimension[2])+self.torus_dimension[1] # (Worst case hop limit: 2*(X+Z) + Y. Should be taken as argument during assignment.
        self.interconnect_latency = args[5]["interconnectLatency"]         # Delay in writing packet to next router
        ###For round robin servicing discipline
        self.lastServedBuffer = len(self.local_links) - 1
        totalProcessByte = 2.0*self.bwX + 2.0*self.bwY + 2.0*self.bwZ + self.bwLN #Total BW into the router from 7 links
        self.bufAccessTime = (1.0/totalProcessByte)*self.mpiMsgSize
        self.bufCheckDelay = args[5]["bufCheckDelay"] #10 nano second to check a queue for packet packet: This time is the overhead
        
        self.bitRate = self.bwX     # This is the BW in Bytes/s (Currently assumed that the value is same for all the links: X, Y, or Z)
        self.transmissionTime = self.mpiMsgSize/float(self.bitRate)# The calulcation is from Wiki 
        #print "Transmission time in microseconds: ", self.transmissionTime*10**6
        self.numOfLinks = args[5]["numOfLinks"]
        self.t = [0]*self.numOfLinks # This is the time for finishing transmission of last packet for each of the links

        ###Create link buffers    #7 queues + 1 short-message queue
        self.link = []
        for i in range (len(self.local_links)):
            self.link.append(InputBuffer(self.buffer_size, self.mpiMsgSize, self.ruid, self.local_links[i]))
        #One more link for the local_nodes
        self.link.append(InputBuffer(self.buffer_size, self.mpiMsgSize, self.ruid, -1)) #Local
        
        #kkk: short-message queue TODO: what woulde be the buffer size?
        self.link.append(InputBuffer(self.buffer_size, self.mpiMsgSize, self.ruid, -2))
	###Creating process
        self.createProcess("bufferProcessing", buffferProcessing)
        self.iProBuff = 0            #0 - hibernate, initial load, nothing
                                     #1 - working on packets. dont wake up if sleeping. Wake if hobernated only
        
        self.printStat = args[5]["statPara"]["printStat"]
        self.linkStatistics = args[5]["statPara"]["linkStat"]
        #print self.printStat
        self.droppedPacketRouter = 0
        self.startProcess("bufferProcessing" )
    
        # Dictionary for statistics collection
        self.stat = {
            "sentBytes": 0,
            "receivedBytes": 0,
            "sentPackets": 0,
            "receivedPackets": 0
        }

        self.interfaceVariable = 0 # This variable indicates when return statistics
        ### create a process to return the interface
        
        #self.createProcess("getBytesSent", getBytesSent)
        #self.startProcess("getBytesSent")
        
        self.interface_IDs = args[6]
        
        #kkk: smq
        self.short_msg_size = 64    # 

    def routingFunction(self, *args):
        """
        @author     Mohammad Abu Obaida
        This function is used as a reqService from the nodes or other routers to receive a packet
        It queues the packet into the appropriate queue and wakes up bufferProcessing if it is hibernated
        Doesnt wake up "bufferProcessing" if its sleeping, because that process will run continuously
        as long as there is a packet to be processed.
        self.iProBuff is a flag that is used fior tracking the bufferProcessing processes's sleep or
        hibernation status.
        @param      args[0]     incoming packet
        """
        pkt= Packet(args[0])
        prev_hop = pkt['from_hop']
        
        if(self.printStat == True):
            print "    R: [XXX] Routing request received. at Router:", self.ruid, " from_hop = ", prev_hop,  "next hop = ", pkt['next_hop'], "dest node:", pkt['dest_id']," type:", pkt['type'], " pkt seq no:", pkt['seq_no']
        
        self.stat["receivedBytes"] += pkt["pkt_size"]
        self.stat["receivedPackets"] += 1
            
        
        #self.reqService(0, "modifyRecvInfo", None, "Interface", self.router)

        #print "Router ID: ", self.ruid, ".First interface: ", self.getInterface(0) 

        if pkt['next_hop'] == self.ruid and pkt['hop_count'] <=self.hop_limit:
            if(self.printStat == True):
                print "      R: pkt received, Queuing now. Router:",self.ruid
            #if(pkt["type"] != "ack"):
            pkt["routing_info"].append(self.ruid)
                #print pkt["routing_info"]
            final_dest = pkt['dest_id']
            final_router = final_dest %2            # we can take final router as a field in packet header as well
            
            if prev_hop == -1 :                     #Case 1: packet came from a local node of this router    
                if(self.printStat == True):
                    print "      R: Local pkt. Q space : ", self.link[0].FIFO_queue.space() #,", pkt  length = ", sys.getsizeof(pkt)
                
                #kkk smq
                if(pkt["pkt_size"] <= self.short_msg_size): 
                    status = self.link[self.numOfLinks-1].FIFO_queue.push(pkt) #TODO: always pushing the packet, without checking any buffer size. Is it right? 
                    #print "!!!! indside smq"
                elif self.link[self.numOfLinks-2].FIFO_queue.space()>=pkt['pkt_size']:  # we could do sys.getsizeof(pkt) here
                    status = self.link[self.numOfLinks-2].FIFO_queue.push(pkt)      # status = self.link[6].FIFO_queue.push(pkt)
                    if(self.printStat == True):
                        print "      R:Packet pushed status:", status,",  Q space after:", self.link[self.numOfLinks-2].FIFO_queue.space()
                else:
                    self.droppedPacketRouter += 1
                    #self.out.write("R. Dropped a packet with ID: " + str(pkt["packet_id"]) + "\n")
                    print "!!! [PKT DROPPED]!!! by initial Router. from_hop=", pkt['from_hop'], " pkt size=", pkt['pkt_size']
            
            else:                        #case 2: packet came from a different router
                if(pkt["pkt_size"] <= self.short_msg_size): 
                    status = self.link[self.numOfLinks-1].FIFO_queue.push(pkt) #TODO: always pushing the packet, without checking any buffer size. Is it right? 
                else:
                    for i in range(len(self.link)-2) : # iterate 0 to 5; 6th is local nodes link
                        if self.link[i].queue_end_b == prev_hop:
                            if(self.printStat == True):
                                print "          This is our Q! Writing pkt. Q Space:", self.link[i].FIFO_queue.space()
                            if self.link[i].FIFO_queue.space()>=pkt['pkt_size']:  # we could do sys.getsizeof(pkt) here
                                status  = self.link[i].FIFO_queue.push(pkt)
                                # update the receive information for the interface
                                if self.linkStatistics == 1:
                                    link_index = i
                                    interface_id = self.getInterface(link_index)
                                    self.reqService(0.000000001,"modifyRecvInfo", pkt["pkt_size"], "Interface", interface_id)    # TODO: need to check last two parameters. Also the first parameter

                                if(self.printStat == True):
                                    print "         Packet pushed status:", status,",  Q space after:", self.link[i].FIFO_queue.space()
                            else:
                                # update the lost information of interface
                                if self.linkStatistics == 1:
                                    link_index = i
                                    interface_id = self.getInterface(link_index)
                                    self.reqService(0.000000001,"modifyLostInfo", pkt["pkt_size"], "Interface", interface_id)    # TODO: need to check last two parameters. Also the first parameter
                                #self.out.write("R. Dropped a packet with ID: " + str(pkt["packet_id"]) + "\n")
                                print " !!! [PKT DROPPED] by intermediate node"
            
            ###We already pushed packet.
            ###Recall: we hibernated bufferProcessing because there was no pkt to consume, we are awaking it
            if self.iProBuff == 0:        #process hibernating need to wake u
                self.iProBuff = 1            #its working on packets
                if(self.printStat == True):
                    print "      R: Router buffProc is hibernated, wake it. Pkt pushed"
                self.wakeProcess("bufferProcessing")
            elif self.iProBuff == 1:
                if(self.printStat == True):
                    print "     R: Process is already up and sleeping"
                pass
            else:
                pass
        else:
            for i in range(len(self.link)-2) : #iterate 0 to 5; 6th is local nodes link
                if self.link[i].queue_end_b == prev_hop:
                    # update the lost information for the interface
                    if self.linkStatistics == 1:
                        link_index = i
                        interface_id = self.getInterface(link_index)
                        self.reqService(0.000000001,"modifyLostInfo", pkt["pkt_size"], "Interface", interface_id)    # TODO: need to check last two parameters. Also the first parameter
            self.droppedPacketRouter += 1
            #self.out.write("R. Dropped a packet with ID: " + str(pkt["packet_id"]) + "\n")                            
            print " !!! [PKT DROPPED] GeminiRouter forwarding error. Check hop_limit, routingFunction!" + " hop count: ", pkt["hop_count"], "Time: ", self.engine.now, "Seq number:", pkt["seq_no"], "At router: ", self.ruid, "Path:", ", ", str(pkt["routing_info"] ), pkt["from_hop"]

    def buffferChecker(self):
        """
        Check all the links if there is contents in buffer and returns True if there is.
        """
        for selected in self.link:
            if not selected.FIFO_queue.isEmpty():
                if(self.printStat == True):
                    print "     There is packet in queue.", selected.FIFO_queue.space(), "of ", self
                return True
        return False

    def forwardNextPriorityPkt (self):
        """
        This method finds the packet from the queue with lowest arrival time. It implements round robin service discipline
        """
        ttl_links = len(self.link)
        st = 0.0                     #sleep timer, function of number of queues processed
        pkt = None
        #print "inside forwardNextPriorityPkt!!!!!!!!!!!"
        # we will search all the links one pass
        for j in range (ttl_links):                                 ###Service Discipline
            # kkk smq
            if not self.link[ttl_links - 1].FIFO_queue.isEmpty():
                nextTurn = ttl_links - 1
                pkt = self.link[nextTurn].FIFO_queue.pop()
                #print "!!!! inside smq while popping"
                break
            else:
                nextTurn = (self.lastServedBuffer + 1) % ttl_links
                #st = st + self.bufCheckDelay                  #VVI time to check a buffer
                
                #if self.ruid == 1:
                #    print "Next turn candidates: ", nextTurn
                if not self.link[nextTurn].FIFO_queue.isEmpty():
                    #TODO: WARNING: we need to get the first item of the queue not the last
                    #st = st + self.bufAccessTime # time to read that 105 Kbyte
                    #if self.ruid == 1:
                    #    print "Now turn for the following link: ", nextTurn
                    pkt = self.link[nextTurn].FIFO_queue.pop()
                    self.lastServedBuffer = nextTurn
                    break       # we stop after picking one packet for forwarding
                self.lastServedBuffer = nextTurn
        if pkt is None:
            print "  [!!!PKT DROPPED] How did the packet manage to vanish?"
            self.droppedPacketRouter += 1
        else: #Now we will modify packer header and forward it
            pkt['hop_count'] += 1
            dest_id = pkt['dest_id']
            # find best path to dest
            if(self.printStat == True):
                print "       previous from_hop",pkt['from_hop'] ,"next_hop:", pkt['next_hop'], ", this ruid", self.ruid
            pkt['from_hop'] = self.ruid

            if dest_id in self.local_nodes:
                #self.stat["sentBytes"] += pkt["pkt_size"]  # Router stat
                #self.stat["sentPackets"] += 1              # Router stat 
                if(self.printStat == True):
                    print "----RECEIVED BY DEST ROUTER for ", pkt['dest_id'], ", type:",pkt['type']
                self.reqService(self.interconnect_latency, "receivingService", pkt.dict, "Node", dest_id)
            else:
                excludeDir = []
                #excludeI = None
                next_hop = self.directionOrderRouting(self.ruid, dest_id, excludeDir)
                pkt['next_hop'] = next_hop['router']
                #print "Router id: ", self.ruid, "Next hop::::::", next_hop['router']
                sent = False
                #temp = 0
                #for i in range(self.numOfLinks-1):
                #if(self.link[i].queue_end_b == next_hop['router']):
                if (self.t[next_hop['dir']] < self.engine.now):
                    
                    #TODO: Commented it later. It seems the followings are not needed. But need to check.
                    ''' 
                    ### Statistics related updates
                    self.stat["sentBytes"] += pkt["pkt_size"]  # Router stat
                    self.stat["sentPackets"] += 1              # Router stat
                    if self.linkStatistics == 1:
                        interface_id = self.getInterface(next_hop['dir'])
                        self.reqService(0.000000001,"modifySentInfo", pkt["pkt_size"], "Interface", interface_id)    # TODO: need to check last two parameters. Also the first parameter
                    '''
                    self.reqService(self.transmissionTime + self.interconnect_latency, "routingFunction", pkt.dict, "Router", next_hop['router'])
                    # kkk:
                    st = st + self.transmissionTime
                    sent = True
                else:
                    excludeDir.append(next_hop['dir'])
                    while True:
                        if (len(excludeDir) == 6 ):
                            break
                        else:
                            next_hop = self.directionOrderRouting(self.ruid, dest_id, excludeDir)
                            if (self.t[next_hop['dir']] < self.engine.now):
                                self.t[next_hop['dir']] = self.engine.now + self.transmissionTime
                                sent = True
                                self.reqService(self.transmissionTime + self.interconnect_latency, "routingFunction", pkt.dict, "Router", next_hop['router'])
                                # kkk
                                st = st  + self.transmissionTime
                                break
                            else:
                                excludeDir.append(next_hop['dir'])
                                
                if (sent == False):
                    print "PKT DROPPED BY intermediate router due to rate control"
                    #write trace
                elif(sent == True):
                    ### Update statistics information
                    self.stat["sentBytes"] += pkt["pkt_size"]  # Router stat
                    self.stat["sentPackets"] += 1              # Router stat 
                    if self.linkStatistics == 1:
                        interface_id = self.getInterface(next_hop['dir'])              
                        #kkk for new flow id...
                        #self.reqService(0.000000001,"modifySentInfo", pkt["pkt_size"], "Interface", interface_id)    # TODO: need to check last two parameters. Also the first parameter
                        self.reqService(0.000000001,"modifySentInfo", [pkt["pkt_size"], pkt["flow_id"]], "Interface", interface_id)    # TODO: need to check last two parameters. Also the first parameter

                #if(temp == 0):      # The packet is not supposed to be sent at a local router and so send the packet at the local node link
                #TODO: Node already got the data
                #    print "Local node!"
                #    self.t[self.numOfLinks - 1] = max(self.t[self.numOfLinks-1], self.engine.now) + self.transmissionTime         
                #    savedTime = self.t[self.numOfLinks - 1]
                #self.reqService(savedTime + self.interconnect_latency, "routingFunction", pkt.dict, "Router", next_hop)#kkk
                #self.reqService( self.interconnect_latency, "routingFunction", pkt.dict, "Router", next_hop)

        return st
    def directionOrderRouting (self, src, dest, exclude):
        """
        This method finds the next best hop to forward a packet using the direction ordet routing.
        src is this node and dest is final destination
        """
        ##print "          called direction order routing for src = ",src, " dest node=",dest
        #def find_torus_xyz_from_uid (self, tuid):
        x_max = self.torus_dimension[0]
        y_max = self.torus_dimension[1]
        z_max = self.torus_dimension[2]

        excludeDir = exclude

        dest = dest/len(self.local_nodes) # we are finding the router that is handling that specific destination node

        # Converting final destination ruid to x,y,z
        dz = int ( dest / (x_max * y_max) )   #z
        dy = int ( (dest % (x_max * y_max)) / x_max) #y
        dx = int ( (dest % (x_max * y_max)) % x_max ) #x

        # Converting this nodes ruid to x,y,z 
        sz = int ( src / (x_max * y_max) )   #z
        sy = int ( (src % (x_max * y_max)) / x_max) #y
        sx = int ( (src % (x_max * y_max)) % x_max ) #x

        # next_ hop x,y,z: initially points to this router
        nx = sx
        ny = sy
        nz = sz

        next_hop = {}
        next_hop['dir'] = -1
        while True:
            #next hop# This is where we have to consider CONGESTION
            if (len(excludeDir)<1):
                if (dx != sx):                            #directionOrder is decided here
                    nx = ( sx + 1 ) % x_max
                    next_hop['dir'] = 0 # meaning +X
                    break 
                elif (dz != sz) :
                    nz = (sz + 1 ) % z_max
                    next_hop['dir'] = 1 # meaning +Z
                    break
                elif(dy != sy) :
                    ny = (sy +1) % y_max
                    next_hop['dir'] = 2 # meaning +Y
                    break
            else:
                valid_choices = [0,1,2,3,4,5]
                #add for as many links u have say 7 then add 0 to 6
                try_dir = list(set(valid_choices)- set(excludeDir))
                print "   *** TRYing this directions: ", try_dir
                #for i in len(try_dir):
                if (try_dir[0]==0):
                    #if (dx != sx):                            #directionOrder is decided here
                    nx = ( sx + 1 ) % x_max
                    next_hop['dir'] = 0 # meaning +X
                    break 
                elif (try_dir[0]==1):
                    # if (dz != sz):                            #directionOrder is decided here
                    nz = ( sz + 1 ) % z_max
                    next_hop['dir'] = 1 # meaning +Y
                    break 
                elif (try_dir[0]==2):
                    #if (dy != sy):                            #directionOrder is decided here
                    ny = ( sy + 1 ) % y_max
                    next_hop['dir'] = 2 # meaning +Z
                    break 
                elif (try_dir[0]==3):
                    #if (dx != sx):                            #directionOrder is decided here
                    nx = ( sx - 1 ) % x_max
                    next_hop['dir'] = 3 # meaning -X
                    break 
                elif (try_dir[0]==4):
                    #if (dz != sz):                            #directionOrder is decided here
                    nz = ( sz - 1 ) % z_max
                    next_hop['dir'] = 4 # meaning -Y
                    break 
                elif (try_dir[0]==5):
                    #if (dy != sy):                            #directionOrder is decided here
                    ny = ( sy - 1 ) % y_max
                    next_hop['dir'] = 5 # meaning -Z
                    break 
                else:
                    print "SERIOUS PROBLEM WITH ROUTING means our routing algorithm isnt implemented correctly"
        n_ruid = nz * self.torus_dimension[0] * self.torus_dimension[1] + ny *self.torus_dimension[0] + nx
        next_hop['router'] = n_ruid
        return next_hop

#--------------------------------------------------------------
### Statistics collection
    def getBytesSent(self):
        return self.stat["sentBytes"]/1024/1024

    def getPacketsSent(self):
        return self.stat["sentPackets"]

    def getBytesRcvd(self):
        return self.stat["receivedBytes"]/1024/1024
    
    def getPacketsRcvd(self):
        return self.stat["receivedPackets"]
    
    def routerStatistics(self, msg, *args):
        stat_process_name = msg[0]
        wake_or_not = msg[1]
        print "############## Time now: ", self.engine.now
        print "Router", self.ruid, "statistics:"
        print "Number of Bytes sent (in MB):", self.getBytesSent()
        print "Number of packets sent:", self.getPacketsSent()
        print "Number of Bytes received (in MB):", self.getBytesRcvd()
        print "Number of packets received:", self.getPacketsRcvd()
        self.out.write("R "+ str(self.engine.now) + " "+ str(self.getBytesSent()) + "\n")
        #print "Wake or not: ", wake_or_not
        if wake_or_not == 1:
            self.wakeProcess(stat_process_name)

#--------------------------------------------------------------
### Find and return the interface
    def getInterface(self, link_index):
        """
        This method returns the interface ID
        @parameter: index of the link. 
        e.g., +X = 0, +Y = 1, +Z = 2, -X = 3, -Y = 4, -Z = 5
        """
        return self.interface_IDs[link_index]
'''    
    def changeInterfaceVariable(self, *args):
        self.interfaceVariable = 1
        print "The variable is changed..."
        self.wakeProcess("getBytesSent")

def getBytesSent(this):
    router = this.entity
    while True:
        #print "Inside the process: getBytesSent"
        if router.interfaceVariable == 0:
            this.hibernate()
        elif router.interfaceVariable == 1:
            print "Going to print the local links..."
            local_link_list = router.getInterface()
            print local_link_list
            router.interfaceVariable = 0
            this.hibernate()
'''
#--------------------------------------------------------------
### Some processes related to routers
def buffferProcessing(this):
    """
    @author     Mohammad Abu Obaida
    This method is a process that goes through all the buffers to check if there is any packet wating for service
    If all the queues aer empty it automatically goes to hibernate.
    When a packet arrives it can be woken up from hibernation.
    However it sleeps in between serving packets which is the processing delay. It cant be disturbed when sleeping.
    Once it gets up from sleep it will check all the queues again before going to sleep.

    """
    #Check all the links for contents in buffer
    router = this.entity
    while True:
        #print "        R: buff Processing loop. router.iProBuff",router.iProBuff
        if router.iProBuff == 0:
            #print "      R: ------------HIBERNATED----------"
            #print "How I am inside here!!!!!!!!!!"
            this.hibernate()
        elif router.iProBuff == 1:
            #print "Inside buffer processing!!!!!!!!!!"
            while router.buffferChecker():   # returns True if there is a pkt in queue
                #print "Inside buffer processing!!!!!!11"
                ###forward next priority packet and sleep for number of queues
                st = router.forwardNextPriorityPkt()
                #print "      R: Router Sleeping before forwarding. Now:",router.engine.now," Sleep Time:",st
                this.sleep (st) #advance absolute simulation time by twice minDelay
                #print "      R: Checking for more item. Now:",router.engine.now

            router.iProBuff = 0
            #print "      R: Router buffers empty. Now:",router.engine.now
            this.hibernate()
        #print "Dropped packet at router: ", router.droppedPacketRouter

class InputBuffer:
    """
    One basic bufffer implementation. Its a Circular FIFO queue.
    These are bidirectional queues. A Torus Node(two cielo node) will have 7
        (1  towards each of X,Y,Z +/- direction	 and one connecting to nodes.)
    """
    def __init__(self, maxBuffSz, pktSz, end_a, end_b ):
        self.queue_len = maxBuffSz
        self.pktSz = pktSz
        self.queue_end_a = end_a
        self.queue_end_b = end_b
        self.FIFO_queue = RingBuffer(self.queue_len, self.pktSz)
    def __str__(self):
        return str(self.queue_end_b)
