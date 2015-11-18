"""
@package nodes
This package contains the desription of the nodes and services available to use

"""

from SimianPie.entity import Entity
import processors
import random
from array import *
import sys
from packet import *
import math
from load import LoadPacket, LoadData, MPIData
from random import randint

class Node(Entity):
    """
    Base class for Node. Actual nodes should derive from this. The application can add handlers to this base class.
    Simple simian simulation entity.
    """
    def __init__(self, baseInfo, *args):
        super(Node, self).__init__(baseInfo)

class GenericComputeNode(Node):
    """
    Class that represents a Cielo compute node.
    """
    def __init__(self, baseInfo, *args, **kwargs):
		"""
		@author     Mohammad Abu Obaida
		Constructor of Cielo node. A cielo node is formed of two physical AMD 8-core processors.
		Each node has a NIC card attached to it that forwards packet to its own gemini router.
		@param  args[0]     unique id of the node(nuid)
		@param  args[1]     router unique id that this node is directly connected to(self.router_id)
		@param  args[2]     final size of a MPI packet that is directly transmitted, so that we can
				            divide total load to be trans mitted in packets
		"""
		super(GenericComputeNode, self).__init__(baseInfo)
		self.memory_footprint =  0       # Number of bytes allocated in memory
		assert (len(args)>3), "Assertion error: CieloNode nuid, router uid and mpiMsgSize all required!"
		self.nuid = args[0]
		self.router_id = args[1]
		self.mpiMsgSize =  args[2] # mpi msg sizes in bytes, passed 105 KB as argument
		self.torus_dimension = args[3]


		self.interconnect_latency =  args[4]["intconnectLatency"]        # Delay in writing packet to parent router queue(in Sec)
		self.NICBps = args[4]["NICBps"]           #10 Gigabit NIC card, converted to byte
		self.delayPackaging = (1.0/self.NICBps)*self.mpiMsgSize     #delay to send 105 byte using 10gbps link

		x_max = self.torus_dimension[0]
		y_max = self.torus_dimension[1]
		z_max = self.torus_dimension[2]

		#I don't have precise number for this
		self.hop_limit = x_max + y_max + z_max +x_max  #say we have 4 x 4 x 4 torus

                # Some data structures
		self.resendQueue = []
                self.sendQ = [] 
		self.resendQ = []
                
                self.pktMaxLoad = args[4]["pktMaxLoad"]
                self.nicBuffSz = args[4]["nicBuffSz"]
    
		#I don't have precise number for this
		self.sendQLimit =  self.nicBuffSz/self.mpiMsgSize
                self.qLimit = self.nicBuffSz/self.mpiMsgSize
                #print "Send queue limit: ", self.sendQLimit
		#self.resendQlimit = self.sendQLimit
		self.iProBuff = 0

		self.resendTry = args[4]["resendTry"]
		# I don't have precise number for this. I am assuming it will spend 100micro sec max on each router
                self.timeAtRouter = args[4]["timeAtRouter"]
		self.resendTimeout = self.hop_limit*self.timeAtRouter
                
                self.packetID = 0
                self.droppedPacket = 0
                #print self.droppedPackets
                self.printStat = args[4]["statPara"]["printStat"]
                self.printRoute = args[4]["statPara"]["printRoute"]
                self.stat = {
                    "droppedPackets": 0,
                    "sentPackets": 0,
                    "receivedPackets": 0,
                    "sentBytes": 0,
                    "receivedBytes": 0
                }

                self.processList = []

                self.createProcess("sendProcess", sendProcess)
                self.startProcess("sendProcess", sendProcess)

                # This process is used to notify MPI_Recv when all packets are received in the sender
                self.createProcess("MPIRecvProcess", MPIRecvProcess)

                #kkk
                #self.createProcess("asyncSendProcess", asyncSendProcess)
                #self.startProcess("asyncSendProcess", asyncSendProcess)
                
                self.bitRate = args[4]["torus_node_bandwidths"]
        
                self.PKTSIZ = self.mpiMsgSize # TODO: check this value. this may not be the value.
                self.packetsToTransmit = 0 # this variable represents how many packets of the data are supposed to be sent by syncSendData service 
                self.ack_size = args[4]["ackSize"]
                self.seqHint = 1
    
    def MPI_Send(self, *args):
        """
        This method sends MPI data into multiple packets.
        This method calls the process syncSend() repeatedly for each packet to perform sending of data.
        @param args[0] object communication data
        """
        assert args[0] is not None, "Communication object for MPI is Null"

        MPICommData = args[0]
        transmission_type = "sync"
        #print "Data communication objects are: ", objCommData.dest_node_id, objCommData.buffer_size
        
        # Divide the data into packets and then call aSyncSend for each packet
        bufsiz = MPICommData.buffer_size
        data = MPICommData.data

        const_delay = 0.000001    #TODO: need to fix a value for this parameter
        schedule_after = const_delay
        while bufsiz > 0:
            pktsz = self.PKTSIZ
            if pktsz > bufsiz:
                pktsz = bufsiz
            bufsiz -= pktsz
            objCommPacket = LoadPacket(MPICommData.dest_node_id, pktsz, MPICommData.app_process_name, MPICommData.dest_app_name, MPICommData.flow_id, data)
            #print "Number of packets transmitted...........", self.packetsTransmitted
            #self.sendService(objCommPacket, transmission_type)
            self.reqService(schedule_after, "sendService", [objCommPacket, transmission_type], "Node", self.nuid)   # TODO: may be the request service can be deleted by creating a new process (to reduce the number of events)            
            schedule_after += const_delay
            #print "scheduling after", schedule_after, "time"
  
    def MPI_Recv(self, *args):
        """
        This method returns received data at destination node.
        """
        #TODO: if possible, return the data to the original calling application
        assert args[0] is not None, "Communication object for data is Null"

        objRecvData = args[0]
        print "status:", objRecvData.status
        
        self.startProcess("MPIRecvProcess", MPIRecvProcess)

        self.out.write("M " + str(self.engine.now) + " " + str(self.getBytesSent()) + " " + str(self.getBytesRcvd())+ "\n")
    
    def MPI_Bcast(self, *args):
        """
        This MPI method is responsible for broadcasting same data to all the other processes in the communicator "comm". Implementing this function using MPI_Send and MPI_Recv.
        @param args[0] object communication data for broadcast
        """
        assert args[0] is not None, "Communication object for data is Null"
        objCommBcastData = args[0]
        transmission_type = "sync"

        print "This is inside MPI Broadcast!!", objCommBcastData.comm[0]
        dest_ids = objCommBcastData.comm
        print "length of destination ids: ", len(dest_ids)
        
        for i in range(len(dest_ids)):
            tag = None
            MPICommData = MPIData(objCommBcastData.data, objCommBcastData.count, objCommBcastData.data_type, dest_ids[i], tag, objCommBcastData.comm, objCommBcastData.buffer_size, objCommBcastData.app_process_name, objCommBcastData.dest_app_name, objCommBcastData.flow_id)
            self.MPI_Send(MPICommData)
            #print "Now send for destination id:", dest_ids[i]
    
    def MPI_Barrier(self, *args):
        """
        This method blocks until all the other processes have completed their own tasks.
        """
        #TODO: check the defition of Barrier call
        print "Inside the barrier call!"
        objCommBarrierData = args[0]
        dest_nodes = objCommBarrierData.dest_ids
        app_process_name = objCommBarrierData.app_process_name
        # For testing purpose. Give some random work to do for each of the process and then wake up the calling process (i.e., process with source node id).
        for i in range (len(dest_nodes)):
            #print "random number:", randint(0,1000)
            temp = randint(0,100000)
            for j in range(temp):
                pass
                
        self.wakeProcess(app_process_name)

    def syncSendData(self, *args):
        """
        This method sends data into multiple packets with limited size (PKTSIZ)
        It calls the process syncSend() repeatedly for each packet to perform sending of data.
        @param args[0] Object communication data
        """
        assert args[0] is not None, "Communication object for data is Null"

        objCommData = args[0]
        transmission_type = "sync"
        #print "Data communication objects are: ", objCommData.dest_node_id, objCommData.buffer_size
        
        # Divide the data into packets and then call aSyncSend for each packet
        bufsiz = objCommData.buffer_size
        data = None

        self.packetsToTransmit = 0

        tmp_bufsiz = bufsiz
        while tmp_bufsiz > 0:
            pktsz = self.PKTSIZ
            if pktsz > tmp_bufsiz:
                pktsz = tmp_bufsiz
            tmp_bufsiz -= pktsz
            self.packetsToTransmit += 1      
        #print "packets to be transmitted: ", self.packetsToTransmit
        
        self.reqService(0.00001, "updateDestPktInfo", [self.packetsToTransmit], "Node", objCommData.dest_node_id)

        const_delay = 0.000001    #TODO: need to fix a value for this parameter
        schedule_after = const_delay
        while bufsiz > 0:
            pktsz = self.PKTSIZ
            if pktsz > bufsiz:
                pktsz = bufsiz
            bufsiz -= pktsz
            objCommPacket = LoadPacket(objCommData.dest_node_id, pktsz, objCommData.app_process_name, objCommData.dest_app_name, objCommData.flow_id, data)
            #print "Number of packets transmitted...........", self.packetsTransmitted
            #self.sendService(objCommPacket, transmission_type)
            self.reqService(schedule_after, "sendService", [objCommPacket, transmission_type], "Node", self.nuid)   # TODO: may be the request service can be deleted by creating a new process (to reduce the number of events)            
            schedule_after += const_delay
            #print "scheduling after", schedule_after, "time"

    def syncSendPacket(self, *args):
        """
        This method sends one packet.
        It calls the process syncSend() for the packet to be sent.
        @param args[0] Object communication data
        """
        assert args[0] is not None, "Communication object for data is Null"

        objCommPacket = args[0]
        transmission_type = "sync"
        self.sendService(objCommPacket, transmission_type)

    def aSyncSendData(self, *args):   
        """
        This method sends data into multiple packets with limited size (PKTSIZ)
        It calls the process syncSend() repeatedly for each packet to perform sending of data.
        @param args[0] Object communication data
        """
        assert args[0] is not None, "Communication object for data is Null"

        objCommData = args[0]
        transmission_type = "async"
        #print "Data communication objects are: ", objCommData.dest_node_id, objCommData.buffer_size
        
        # Divide the data into packets and then call aSyncSend for each packet
        bufsiz = objCommData.buffer_size
        data = None
        while bufsiz > 0:
            pktsz = self.PKTSIZ
            if pktsz > bufsiz:
                pktsz = bufsiz
            bufsiz -= pktsz
            objCommPacket = LoadPacket(objCommData.dest_node_id, pktsz, objCommData.app_process_name, data)
            self.packetsTransmitted += 1
            #print "Number of packets transmitted...........", self.packetsTransmitted
            self.sendService(objCommPacket, transmission_type)

    def aSyncSendPacket(self, *args):
        """
        This method sends one packet.
        It calls the service sendService() for the packet to be sent.
        @param args[0] Object communication data
        """
        assert args[0] is not None, "Communication object for data is Null"

        objCommPacket = args[0]
        transmission_type = "async"
        self.sendService(objCommPacket, transmission_type)


    #def sendService(self, *args):       
    def sendService(self, msg, *args):       
        """
        This method synchronously sends one packet from source to destination.
        It calls the process sendProcess() to perform sending of a packet.
        @param args[0] Object communication packet
        """
        #assert args[0] is not None, "Communication object for packet is Null"
        #'''
        assert msg[0] is not None, "Communication object for packet is Null"
        objCommPacket = msg[0]
        transmissionType = msg[1]
        #'''
    
        #objCommPacket = args[0]
        #transmissionType = args[1]
        #print "The process name............: ", objCommPacket.app_process_name
        loadType = "load"
        #print "............Sending packet of size: ", objCommPacket.data_size

        ## Create the packet here
        from_hop = - 1
        next_hop = self.router_id
        hop_count = 0
        
        #seqHint = 1     # TODO: May be remove this variable?
        src = self.nuid
        dest = objCommPacket.dest_node_id
        #TODO: check the seqHint (suggested by Obaida)
        seq = int(((((1000000+self.seqHint)*100000) + src) * 100000 ) + dest  ) # The first 3 digits of the sequence number represents process id
        self.seqHint += 1
        pkt = Packet({
            "from_hop": from_hop,
            "next_hop": next_hop,
            "hop_count": hop_count,
            "src_id": src,
            "dest_id": dest,
            "seq_no": seq,
            "pkt_size": objCommPacket.data_size,#TODO: need to change all the calculation (transmission time etc.). previously it was fixed: node.mpiMsgSize
            "type": loadType,
            "load": objCommPacket.data,
            "packet_id": 1, # TODO: This field is not really needed right now. May remove later
            "sent_time": self.engine.now,
            "routing_info": [],  # This parameter is used to print all the routes that the packet takes
            "app_process_name": objCommPacket.app_process_name,
            "dest_app_name": objCommPacket.dest_app_name,
            "transmission_type": transmissionType, # synchronous or asynchronous transmission
            "flow_id": objCommPacket.flow_id
        })
        pkt["routing_info"].append(self.nuid)

        ## Append the packet to the sendQ
        #kkk: checked both the sendQ and resendQ now:
        if(len(self.sendQ) + len(self.resendQ) >= self.qLimit):
            self.stat["droppedPackets"] += 1
            print "PKT DROPPED: SendQ full. Pkt pushed faster than NIC can process."
        else:
            self.sendQ.append({
                "la": 1,                    # last accessed time
                "seq_no": pkt["seq_no"],    
                "rc": 0,                    # resend count
                "time": self.engine.now,
                "pkt": pkt
            })
            #self.stat["sentPackets"] += 1
            #self.stat["sentBytes"] += pkt["pkt_size"]
            if(self.printStat == True):
                print "  N: pkt pushed to sendQ, len(sendQ): ", len(self.sendQ)
    
            ## Need to sleep the calling process...

            ## Wake up the process sendResend if needed
            if self.iProBuff == 0:
                self.iProBuff = 1
                self.wakeProcess("sendProcess")
            elif self.iProBuff == 1:
                if(self.printStat == True):
                    print "   N: Process is already up"
                pass
 

#--------------------------------------------------------------------------
    def receivingService(self, *args):
        """
        @author: Mohammad Abu Obaida
        This service receives the packet that comes throught the incoming link from its own router.
        Router will schedule a service on this entity for reception of packet.
        This service removes a packet from resendQ once its delivered
        @param      args[0]     packet
        """
        assert args[0] is not None, "EMPTY PACKET received by destination node"
        rcv_pkt = Packet(args[0])
        if (rcv_pkt['dest_id'] == self.nuid):
            self.stat["receivedPackets"] += 1
            self.stat["receivedBytes"] += rcv_pkt["pkt_size"]
            if(self.printStat == True):
                print "------Pkt received by dest node,", self.nuid, "type:", rcv_pkt['type'], "time:", self.engine.now, "sequence number:",  rcv_pkt['seq_no']
            if (rcv_pkt['type']== "load"):
                if (self.printRoute == True):
                # print the route of the arriving packet
                    print "A LOAD packet size: ", rcv_pkt["pkt_size"], ". Starting node id: ", rcv_pkt["routing_info"][0], "Receiving node ID: ", self.nuid, "sent time: ", rcv_pkt['sent_time'], "seq no: ", rcv_pkt['seq_no']
                    print "Routing information is as following:"
                    for i in range(1, len(rcv_pkt["routing_info"])):
                        if (i == len(rcv_pkt["routing_info"]) - 1):
                            print rcv_pkt["routing_info"][i]
                        else:
                            print rcv_pkt["routing_info"][i], "-->",
                    print "\n"
                if(self.printStat == True):
                    print "------------Sending ACK"
                hop_count = 0
                #Because we will never have load to split in packets for ack we dont need packetize
                from_hop = -1 #self.nuid will give us the nuid of the router, because its confusing
                ack = Packet({#Msg
                                   "next_hop":self.router_id,
                                   "from_hop":from_hop,
                                   "hop_count":hop_count,
                                   "src_id":self.nuid,
                                   "dest_id":rcv_pkt['src_id'],
                                   "type":"ack",
                                   "seq_no":rcv_pkt['seq_no'],
                                   "pkt_size": self.ack_size,
                                   "load":None,
                                   "packet_id": rcv_pkt['packet_id'],    # This ack id is the same as the packet id, for which ack is generated
                                   "pkt_sent_time": rcv_pkt['sent_time'],
                                   "ack_sent_time": self.engine.now,
                                   "routing_info": [],
                                   "app_process_name": rcv_pkt['app_process_name'],
                                   "transmission_type": rcv_pkt['transmission_type'],
                                   "flow_id": rcv_pkt['flow_id']
                                })
                ack["routing_info"].append(self.nuid)
                self.reqService(self.interconnect_latency, "routingFunction", ack.dict, "Router", self.router_id)
                if(self.printStat):
                    print "  Sent acknowledgement for the packet: ", rcv_pkt['packet_id'], ". With source ID: ", rcv_pkt['src_id'], ". At time: ", ack["ack_sent_time"]
                
                ### Wake up the process to let it know that data has reached its destination...
                '''###
                self.packetsToTransmit -= 1
                print "packets remaining: ", self.packetsToTransmit
                if self.packetsToTransmit == 0:
                    self.wakeProcess(rcv_pkt["dest_app_name"])
                '''###
            elif (rcv_pkt['type']== "ack"):
                if (self.printRoute == True):
                # print the route of the arriving packet
                    print "An ACK packet! size: ", rcv_pkt["pkt_size"], ". Starting node id: ", rcv_pkt["routing_info"][0], "Receiving node ID: ", self.nuid
                    print "Routing information is as following:"
                    for i in range(1, len(rcv_pkt["routing_info"])):
                        if (i == len(rcv_pkt["routing_info"]) - 1):
                            print rcv_pkt["routing_info"][i]
                        else:
                            print rcv_pkt["routing_info"][i], "-->", 
                    print "\n"
                if(self.printStat == True):
                    print "----------got ack for pkt #", rcv_pkt['packet_id'], ", Removing pkt from Array at time: ", self.engine.now, "ResendQ size: ", len(self.resendQ)
                rttTime = self.engine.now - rcv_pkt['pkt_sent_time'] 
                ###print "Total round trip time (RTT) for packet ID: ", rcv_pkt['packet_id'], " is: ", rttTime
                ###self.out.write(str(rttTime) + " ") 
                pktSeqNos = ""
                

                #kkk wakeup the process sendProcess if needed
                if self.iProBuff == 0:
                    self.iProBuff = 1
                    self.wakeProcess("sendProcess")
                elif self.iProBuff == 1:
                    if(self.printStat == True):
                        print "   N: Process is already up"
                    pass

                #kkk TODO: don't wakeup the process for asyncSendProcess  

                for item in self.resendQ:
                    if item['seq_no'] == rcv_pkt['seq_no']:
                        self.resendQ.remove (item)
                        if(self.printStat == True):
                            print "---------**-----After pkt removal len(self.resendQ) =", len(self.resendQ)
                        
                        if rcv_pkt["transmission_type"] == "sync" and len(self.resendQ) == 0 and len(self.sendQ) == 0: # None means that asyncSend 
                            #print "Waking up process: ", rcv_pkt['app_process_name'], "at time: ", self.engine.now, "destination id: ", rcv_pkt['src_id'], "ResendQ size: ", len(self.resendQ)
                            #self.iProBuff = 0
                            print "Processes: ", self.getProcessNames(), "Node id: ", self.nuid
                            #TODO: need to check and change the following...
                            #if rcv_pkt['app_process_name'] == "mpiProcessBcast1":
                            #    self.wakeProcess(rcv_pkt['app_process_name'])
                            #else:
                            #    self.wakeProcess("mpiProcessBcast1")
                            self.wakeProcess(rcv_pkt['app_process_name'])
                            self.wakeProcess("MPIRecvProcess")
                        break
            else:
                print "--!!!!!!---PKT TYPE UNKNOWN"
    
    def wakeProcessStartingNode(self, *args):
        print "waking up the starting process now!!!!!!!"
        self.wakeProcess("mpiProcessBcast1")

#-------------------------------------------------------------------------------------
    def resendService(self, *args):
        seqNo = args[0]
        #Remove packet from resendQ
        for i in xrange (len(self.resendQ)):
            if self.resendQ[i]['seq_no'] == seqNo:
                #if(self.printStat == True):
                print "Resending packet:",seqNo
                # "seq_no": pkt['seq_no'],
                # "rc": 1, #resend count
                # "pkt": pkt
                if self.resendQ[i]['rc'] <= self.resendTry:
                    pkt = self.resendQ[i]['pkt']

                    #kkk: insert the packet at the top of the queue
                    self.sendQ.insert(0, { 
                                            "la": 1,
                                            "seq_no": pkt["seq_no"],
                                            "rc": self.resendQ[i]['rc'] + 1,
                                            "time": self.engine.now,
                                            "pkt": pkt
                                        })
                    #self.reqService(self.interconnect_latency, "routingFunction", pkt.dict, "Router", self.router_id)
                    #Resend packet
                    #self.reqService(self.resendTimeout, "resendService", pkt['seq_no'], "Node", self.nuid)
                    
                    self.resendQ[i]['rc'] += 1
                    ## Wake up the process sendResend if needed
                    if self.iProBuff == 0:
                        self.iProBuff = 1
                        self.wakeProcess("sendProcess")
                    elif self.iProBuff == 1:
                        if(self.printStat == True):
                            print "   N: Process is already up"
                        pass
                else:
                    print "!!!PKT DROPPED, after maximum number of tries. Type:", self.resendQ[i]['pkt']['type'], "Node ID: ", self.nuid 
                    self.stat["droppedPackets"] += 1
                    self.resendQ.pop(i)
                break 

#---------------------------------------------------------------
    def updateDestPktInfo(self, msg, *args):
        '''
        This method updates the packets to be received by the destination node
        '''
        self.packetsToTransmit = msg[0]
        #print "Node id: ", self.nuid, "Packets to transmit: ", self.packetsToTransmit

#------------------------------------------------------------------------------------
    def getBytesSent(self):
        '''
        returns number of bytes sent by this node
        '''
        return self.stat["sentBytes"]/1024/1024 # in MB

    def getBytesRcvd(self):
        '''
        returns number of received by this node
        '''
        return self.stat["receivedBytes"]/1024 # in KB

    def getPacketsSent(self):
        '''
        returns number of packets sent by this node
        '''
        return self.stat["sentPackets"]

    def getPacketsRcvd(self):
        '''
        returns number of packets received by this node
        '''
        return self.stat["receivedPackets"]

    def nodeStatistics(self, msg, *args):
        stat_process_name = msg[0]
        wake_or_not = msg[1]
        print "##############Time now: ", self.engine.now
        print "Node", self.nuid, " statistics:"
        print "Number of sent packets:", self.getPacketsSent()
        print "Number of dropped packets:", self.stat["droppedPackets"]
        print "Number of received packets (including ACK packets):", self.getPacketsRcvd()
        print "Number of Bytes sent: (in MB)", self.getBytesSent()
        print "Number of Bytes received (in MB):", self.getBytesRcvd()
        #print "Wake or not:", wake_or_not
        self.out.write("N " + str(self.engine.now) + " " + str(self.getBytesSent()) + " " + str(self.getBytesRcvd())+ "\n")
        #self.out.write(str(self.getBytesRcvd()) + "\n")
        if wake_or_not == 1:
            #print "The processes to wake up: ", self.getProcessNames()
            self.wakeProcess(stat_process_name)

    ''' Delete these...
    ### The following service is for waking up the application process once data reaches its destination
    def wakeChildProcess()
    '''
def sendProcess(this, *args):
    """
    This function is supposed to be invoked as a process inside the scheduled event
    of an entity (node) to periodically check and send/resend packets from sendQ and
    resendQ that we didnt receive an ack for.
    """
    node = this.entity
    while True:
        #print "        N: sendResend processing loop. node.iProBuff",node.iProBuff
        if node.iProBuff == 0:
            #print "      R: ------------HIBERNATED----------"
            this.hibernate()
        elif node.iProBuff == 1:
            while (len (node.sendQ) != 0):
                # find_next_packet _to_resend
                item = node.sendQ.pop(0) #popping first item
                if node.printStat == True:
                    print "Just popped a packet from sendQ. new length=", len(node.sendQ)
                pkt = item ['pkt']
                #U can set a maximum length for the resend Q and discard oldest entry, if it overflows
                #kkk: checking and dropping packets, if there not enough space in q

                if(len(node.sendQ) + len(node.resendQ) >= node.qLimit):
                    node.stat["droppedPackets"] += 1
                    print "PKT DROPPED: SendQ/ResendQ full. Pkt pushed faster than NIC can process."
                else:
                    node.resendQ.append ({
                                                "la": 1, #last accessed time
                                                "seq_no": pkt['seq_no'],
                                                "rc": 1, #resend count
                                                "pkt": pkt
                                          })
                    transmission_time = (pkt["pkt_size"]/float(node.bitRate))
                
                    node.stat["sentPackets"] += 1
                    node.stat["sentBytes"] += pkt["pkt_size"]
                    #print "transmission time: ", transmission_time
                    this.sleep(transmission_time)
                    #print "The process names: ",node.getProcessNames()
                    if pkt["transmission_type"] == "async" and len(node.sendQ) == 0: # None means that asyncSend 
                        node.wakeProcess(pkt['app_process_name'])
                    node.reqService(node.interconnect_latency, "routingFunction", pkt.dict, "Router", node.router_id)
                    #TrafficTrace send/rcv from to pkt_type pkt_size src_id dst_id seq_no
                    
                    #kkk: TODO: was the process supposed to sleep for this resendTimeout time  
                    node.reqService(node.resendTimeout, "resendService", pkt['seq_no'], "Node", node.nuid)
            #print "    N: ! Send buffer Empty! in sendResend, hibernating process!" ## Todo: Add the prinStat functionality
            #DESIGN decision: node.delayPackaging should be way smaller than the sleep time of its caller process
            node.iProBuff = 0
            this.hibernate()

def MPIRecvProcess(this, *args):
    node = this.entity    
    while True:
        print "Inside MPI receive process: before hibernation"
        this.hibernate()    
        print "Inside MPI receive process: after hibernation"
