# This class is responsible for organization of interfaces: updating different
# interface information and printing/returning interface information as well

from SimianPie.entity import Entity

class Interface(Entity):
    """
    Base class for Interface. All other Interface classes will derive from this. 
    It inherits from Simian Entity class. 
    """
    def __init__(self, baseInfo, *args):
        super(Interface, self).__init__(baseInfo)

class TorusInterface(Interface):
    """
    This class is responsible for creating interfaces for Gemini torus topology. 
    """
    def __init__(self, baseInfo, *args, **kwargs):
        """
        Constructor for the TorusInterface class.
        """
        super(TorusInterface, self).__init__(baseInfo)
        #TODO: assert statement for args
        
        self.interface_id = args[0]
        self.router_id_a = args[1]
        self.router_id_b = args[2]
        #print "Interface ID: ", self.interface_id, "point a router: ", self.router_id_a, "point b router: ", self.router_id_b 
        self.stat = {
            "bytesSent": 0,
            "packetsSent": 0,
            "bytesReceived": 0,
            "packetsReceived": 0,
            "bytesLost": 0,
            "packetsLost": 0
        }
        self.stat_1 = {
            "bytesSent": 0,
            "packetsSent": 0,
            "bytesReceived": 0,
            "packetsReceived": 0,
            "bytesLost": 0,
            "packetsLost": 0
        }
       

    def modifySentInfo(self, msg, *args):
        """
        This method modifies the sent information for the interface
        """
        #print "Interface id inside modifySentInfo: ", self.interface_id, "At time: ", self.engine.now

        #pkt_size = args[0]
        #self.stat["packetsSent"] += 1
        #self.stat["bytesSent"] += pkt_size
        
        pkt_size = msg[0]
        #self.stat["packetsSent"] += 1
        #self.stat["bytesSent"] += pkt_size
        flow_id = msg[1]
        #print "!!!!!!!!!!!!!!!!!! Now need to modify sent info for flow: ", flow_id, "pkt size: ", pkt_size
        if flow_id == 0:
            self.stat["packetsSent"] += 1
            self.stat["bytesSent"] += pkt_size
        elif flow_id == 1:
            self.stat_1["packetsSent"] += 1
            self.stat_1["bytesSent"] += pkt_size
    def modifyRecvInfo(self, *args):        
        """
        This method modifies the receive information for the interface
        """
        pkt_size = args[0]
        self.stat["packetsReceived"] += 1
        self.stat["bytesReceived"] += pkt_size

    def modifyLostInfo(self, *args):     
        """
        This method modifies the lost information for the interface 
        """
        #TODO: Check for dropped packets at output buffers
        pkt_size = args[0]
        self.stat["packetsLost"] += 1
        self.stat["bytesLost"] += pkt_size
               
    def getBytesSent(self):
        """
        This method returns the bytes sent through the interface
        """
        return self.stat["bytesSent"] ## returns in MB
    
    def getPacketsSent(self):
        """
        This method returns the bytes sent through the interface
        """
        return self.stat["packetsSent"]

    def getBytesRcvd(self):
        """
        This method returns the bytes sent through the interface
        """
        return self.stat["bytesReceived"]


    def getPacketsRcvd(self):
        """
        This method returns the bytes sent through the interface
        """
        return self.stat["packetsReceived"]


    def getBytesLost(self):
        """
        This method returns the bytes sent through the interface
        """
        return self.stat["bytesLost"]
    
    def getPacketsLost(self):
        """
        This method returns the bytes sent through the interface
        """
        return self.stat["packetsLost"]

    def linkStatistics(self, msg, *args):
        stat_process_name = msg[0]
        wake_or_not = msg[1]
        print "############## Time now: ", self.engine.now
        print "Interface", self.interface_id, " statistics:", "Router point A: ", self.router_id_a, "Router point B: ", self.router_id_b
        print "Number of sent packets:", self.getPacketsSent()
        print "Number of dropped packets:", self.getPacketsLost()
        print "Number of received packets (including ACK packets):", self.getPacketsRcvd()
        print "Number of Bytes sent flow 0:", self.getBytesSent()
        print "Number of Bytes send flow 1:", self.stat_1["bytesSent"]
        print "Number of Bytes received:", self.getBytesRcvd()
        print "Number of Bytes lost: ", self.getPacketsLost()
        #self.out.write(str(self.engine.now) + " " + str(self.getBytesSent()) + "\n")
        
        self.out.write("I " + "0 " + str(self.engine.now) + " " + str(self.getBytesSent()) + "\n")
        
        self.out.write("I " + "1 " + str(self.engine.now) + " " + str(self.stat_1["bytesSent"]) + "\n")
        if wake_or_not == 1:
            self.wakeProcess(stat_process_name)
