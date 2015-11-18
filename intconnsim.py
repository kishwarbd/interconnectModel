#/usr/bin/env python

from copy import deepcopy
import math
import random
import array
from load import Load, LoadPacket, LoadData, IntervalData, MPIData, MPIRecvData, MPIBcastData, MPIBarrierData #zzz

from SimianPie.simian import Simian
import clusters
import nodes
import router
import interface
import sys

from parameters import *
from genconfig import topologyGenerator

simName, startTime, endTime, minDelay, useMPI = "intconnsim", 0.0, 100.0, 0.000000001, True
simianEngine = Simian(simName, startTime, endTime, minDelay, useMPI)

print "Generating torus topology..."
topologyGenerator(interconnect_type, topology_file_name, torus_dim_size_0, torus_dim_size_1, torus_dim_size_2)
print "Finished topology generation..."


debug_parameters = {    # need to work on this parameter and concise it...
    "printStat": DEBUG_PRINT_INFO,
    "printRoute": DEBUG_PACKET_ROUTE,
    "linkStat": DEBUG_LINK_STATS 
}

router_parameters = {
    "bufferSize": torus_inbuf_size,
    "bwX": torus_bandwidth_0,
    "bwY": torus_bandwidth_1,
    "bwZ": torus_bandwidth_2,
    "bwLN": torus_node_bandwidths,
    "interconnectLatency": torus_prop_delay,
    "bufCheckDelay": torus_proc_time,
    "numOfLinks": torus_num_of_links,
    "statPara": debug_parameters # Need to work on it
}

node_parameters = {
    "pktMaxLoad": node_packet_max_load,
    "ackSize": ack_size,
    "nicBuffSz": torus_node_outbuf_size,
    "torus_node_bandwidths": torus_node_bandwidths,
    "intconnectLatency": torus_node_prop_delay, #TODO: need to check
    "NICBps": torus_node_prop_delay_0,          #TODO: need to check
    "timeAtRouter": node_time_to_resend_packet,
    "resendTry": node_resend_try,
    "statPara": debug_parameters # Need to work on it
}

interconnect_torus_dim_values = {
    "torusX": torus_dim_size_0,
    "torusY": torus_dim_size_1,
    "torusZ": torus_dim_size_2
}

cluster_properties = {
    "torus": interconnect_torus_dim_values,
    "mpiMsgSize": mpiMsgSize,
    "node_para": node_parameters,
    "router_para": router_parameters,
    "no_of_flows": no_of_flows
}

temp_variable = 0
load_size = packet_load_size
time_window = misc_time_window
distribution_type = misc_distribution_type 
no_of_nodes = 2 * torus_dim_size_0*torus_dim_size_1*torus_dim_size_2 #TODO: make it generic. That is, indepenedent of whether the variable names are changed or not...

### 1. Choose anid instantiate the Cluster that we want to simulate

cluster = clusters.ClusterFromTopo(simianEngine, topology_file_name, cluster_properties)

# Synchronously send one data...
def appProcess(this, *args):

    entity = this.entity
    node_id_this_process = args[0]
    while True:
        flow_id = 0
        source_node_id = 1
        dest_node_id = 7
        buffer_size = 2*1024*1024*1024   # 1MB. A good value: 4GB
        app_process_name = this.name
        dest_app_name = this.name[0:len(this.name)-1] + str(dest_node_id) # e.g., appProcess46
        #print "Destination application name: ", dest_app_name
        #print "The process name: ", this.name 
        objCommData  = LoadData(dest_node_id, buffer_size, app_process_name, dest_app_name, flow_id) #TODO: may be no necessity of creating using LoadPacket after all...
        ###if(node_id_this_process == source_node_id):
        entity.reqService(50.2, "syncSendData", objCommData, "Node", source_node_id) #TODO: check whether this should really be a request service or not. A good value: 50.1
        ###if(node_id_this_process == dest_node_id):
        this.hibernate() # TODO: need to check the placement of the hibernation.
        ###print "The data reached its destination", this.entity.engine.now
        
        #print "The data reached its destination at time: ", this.entity.engine.now
        ###if(node_id_this_process == source_node_id):
        ###this.hibernate()
        ###print "The ACK reached its destination at time: ", this.entity.engine.now

# Create another application process to create some congestion through some links
# Synchronously send one data...
def appProcess_2(this, *args):
    entity = this.entity
    node_id_this_process = args[0]
    while True:
        flow_id = 1
        source_node_id = 2
        dest_node_id = 7
        buffer_size = 2*1024*1024*1024   # 1MB. A good value: 8GB
        app_process_name = this.name
        dest_app_name = this.name[0:len(this.name)-1] + str(dest_node_id) # e.g., appProcess46
        #print "Destination application name: ", dest_app_name
        #print "The process name: ", this.name 
        objCommData  = LoadData(dest_node_id, buffer_size, app_process_name, dest_app_name, flow_id) #TODO: may be no necessity of creating using LoadPacket after all...
        ###if(node_id_this_process == source_node_id):
        entity.reqService(51, "syncSendData", objCommData, "Node", source_node_id) #TODO:check whether this should really be a request service or not. A good value: 50.5
      
        ###if(node_id_this_process == dest_node_id):
            ###this.hibernate() # TODO: need to check the placement of the hibernation.
            #print "The data reached its destination", this.entity.engine.now
        #print "The data reached its destination at time: ", this.entity.engine.now
        ###if(node_id_this_process == source_node_id):
        this.hibernate()
            #print "The ACK reached its destination at time: ", this.entity.engine.now

# This process collects all the statistics for node. Must specify the start time, end time and so on...    
def statProcessNode(this, *args):
    entity = this.entity
    #TODO: create assert for args[0]
    intervalObj = args[0]
    start_time = intervalObj.start_time
    end_time = intervalObj.end_time
    collection_interval = intervalObj.collection_interval
    source_node_id = intervalObj.entity_id
    stat_process_name = this.name
    
    # The main process goes here...
    wake_or_not = 0
    entity.engine.schedService(start_time, "nodeStatistics", [stat_process_name, wake_or_not], "Node", source_node_id)

    this.sleep(start_time)
    wake_or_not = 1
    while True:
        if(entity.engine.now + collection_interval > end_time):
            wake_or_not = 0
            break
        #print "\nInside statistics collection process. At time: ", entity.engine.now        #source_node_id = 1
        entity.reqService(collection_interval, "nodeStatistics", [stat_process_name, wake_or_not], "Node", source_node_id)
        this.hibernate()
        if(entity.engine.now > end_time):
            wake_or_not = 0
            break

# This process collects all the statistics for router. Must specify the start time, end time and so on...    
def statProcessRouter(this, *args):
    entity = this.entity
    #TODO: create assert for args[0]
    intervalObj = args[0]
    start_time = intervalObj.start_time
    end_time = intervalObj.end_time
    collection_interval = intervalObj.collection_interval
    router_id = intervalObj.entity_id
    stat_process_name = this.name
    
    # The main process goes here...
    wake_or_not = 0
    entity.engine.schedService(start_time, "routerStatistics", [stat_process_name, wake_or_not], "Router", router_id)

    this.sleep(start_time)
    wake_or_not = 1
    while True:
        if(entity.engine.now + collection_interval > end_time):
            wake_or_not = 0
            break
        #print "\nInside Router statistics collection process. At time: ", entity.engine.now 
        #source_node_id = 1
        entity.reqService(collection_interval, "routerStatistics", [stat_process_name, wake_or_not], "Router", router_id)
        this.hibernate()
        if(entity.engine.now > end_time):
            wake_or_not = 0
            break

# This process collects all the statistics for an interface. Must specify the start time, end time and so on...    
def statProcessInterface(this, *args):
    entity = this.entity
    #TODO: create assert for args[0]
    intervalObj = args[0]
    start_time = intervalObj.start_time
    end_time = intervalObj.end_time
    collection_interval = intervalObj.collection_interval
    interface_id = intervalObj.entity_id
    stat_process_name = this.name
    
    # The main process goes here...
    wake_or_not = 0
    entity.engine.schedService(start_time, "linkStatistics", [stat_process_name, wake_or_not], "Interface", interface_id)

    this.sleep(start_time)
    wake_or_not = 1
    while True:
        if(entity.engine.now + collection_interval > end_time):
            wake_or_not = 0
            break
        #print "\nInside INTERFACE statistics collection process. At time: ", entity.engine.now 
        #source_node_id = 1
        entity.reqService(collection_interval, "linkStatistics", [stat_process_name, wake_or_not], "Interface", interface_id)
        this.hibernate()
        if(entity.engine.now > end_time):
            wake_or_not = 0
            break

# Synchronously send MPI data...
def mpiProcess(this, *args):
    entity = this.entity
    node_id_this_process = args[0]
    while True:
        flow_id = 0
        source_node_id = 1
        dest_node_id = 7
        buffer_size = 2*1024*1024   # 1MB. A good value: 4GB
        app_process_name = this.name
        dest_app_name = this.name[0:len(this.name)-1] + str(dest_node_id) # e.g., appProcess46
        #print "Destination application name: ", dest_app_name
        data = None         # initial address of send buffer
        count = None        # number of elements in send buffer
        data_type = None     # datatype of each send buffer element
        dest = dest_node_id
        tag = None          # message tag
        comm = [1, 2, 3, 4, 5, 6, 7]         # TODO: group of nodes (communicator)
        MPICommData = MPIData(data, count, data_type, dest, tag, comm, buffer_size, app_process_name, dest_app_name, flow_id) #TODO: may be no necessity of creating using LoadPacket after all...
        ###if(node_id_this_process == source_node_id):
        entity.reqService(50.2, "MPI_Send", MPICommData, "Node", source_node_id) #TODO: check whether this should really be a request service or not. A good value: 50.1
        ###if(node_id_this_process == dest_node_id):
        this.hibernate() # TODO: need to check the placement of the hibernation.
        ###print "The data reached its destination", this.entity.engine.now
        
        #print "The data reached its destination at time: ", this.entity.engine.now
        ###if(node_id_this_process == source_node_id):
        ###this.hibernate()
        ###print "The ACK reached its destination at time: ", this.entity.engine.now

# Synchronously receive MPI data...
def mpiProcessRecv(this, *args):
    entity = this.entity
    node_id_this_process = args[0]
    while True:
        flow_id = 0
        #source_node_id = 1
        dest_node_id = 1
        buffer_size = 2*1024*1024   # 1MB. A good value: 4GB
        app_process_name = this.name
        dest_app_name = this.name[0:len(this.name)-1] + str(dest_node_id) # e.g., appProcess46
        #print "Destination application name: ", dest_app_name
        data = None         # initial address of send buffer
        count = None        # number of elements in send buffer
        data_type = None     # datatype of each send buffer element
        dest = dest_node_id
        tag = None          # message tag
        comm = None         # TODO: group of nodes (communicator)
        status = None       # TODO
        MPIRecvCommData = MPIRecvData(data, count, data_type, dest, tag, comm, status, buffer_size, app_process_name, dest_app_name, flow_id) #TODO: may be no necessity of creating using LoadPacket after all...
        ###if(node_id_this_process == source_node_id):
        entity.reqService(50.2, "MPI_Recv", MPIRecvCommData, "Node", dest_node_id) #TODO: check whether this should really be a request service or not. A good value: 50.1
        ###if(node_id_this_process == dest_node_id):
        this.hibernate() # TODO: need to check the placement of the hibernation.

# Broadcast MPI data...
def mpiProcessBcast(this, *args):
    entity = this.entity
    BcastObj = args[0]
    node_id_this_process = BcastObj.source_node_id
    end_time = BcastObj.end_time
    
    buffer_size = 2*1024*1024   # 1MB. A good value: 4GB
    data = None         # initial address of send buffer
    count = None        # number of elements in send buffer
    data_type = None     # datatype of each send buffer element
    comm = [3, 4, 5, 6]         # TODO: group of nodes (communicator)       
    tag = None          # This variable is for communication data on MPI_Send
    
    #print "Topology file name: ", topology_file_name
    files = open(topology_file_name)
    file_list = files.readlines()

    source_node_ids = []
    router_ids = []
    root_id = 1
    source_node_ids.append(root_id)
    temp_list = [1, 0, 0]
    flow_id = 0
    #source_node_id = 1
    #buffer_size = 2*1024*1024   # 1MB. A good value: 4GB
    app_process_name = this.name
    #print "Destination application name: ", dest_app_name

   
    print "************For x-axis: find the destination node ids"
    dest_node_ids = []
    next_source_ids = []
    for i in range(len(source_node_ids)):
        router_ids.append(source_node_ids[i]/2)
    for eachLine in file_list:
        for i in range(len(router_ids)):
            router_id = router_ids[i]
            words = eachLine.split(' ')
            tmpRouterID = int(words[0])
            if tmpRouterID == router_id:
                #print eachLine
                dest_router_id = int(words[4])
                dest_node_id = dest_router_id * 2 # convert the router id to node id
                dest_node_ids.append(dest_node_id)
                next_source_ids.append(dest_node_id)
    print "Destination node ids: ", dest_node_ids
    print "Source node ids: ", source_node_ids
    #print "Next source ids..........", next_source_ids
    
    
    print "************For y-axis"
    #print "Source node ids: ", source_node_ids
    dest_node_ids_1 = []
    router_ids_1 = []
    source_node_ids_1 = []
    next_source_ids_1 = []
    for i in range(len(source_node_ids)):
        source_node_ids_1.append(source_node_ids[i])
    for i in range(len(next_source_ids)):
        source_node_ids_1.append(next_source_ids[i])
    for i in range(len(source_node_ids_1)):
        router_ids_1.append(source_node_ids_1[i]/2)
    for eachLine in file_list:
        for i in range(len(router_ids_1)):
            router_id = router_ids_1[i]
            words = eachLine.split(' ')
            tmpRouterID = int(words[0])
            #print "*******source node ids: ", source_node_ids
            if tmpRouterID == router_id:
                #print eachLine
                dest_router_id = int(words[5])
                dest_node_id = dest_router_id * 2
                #print "Router id: ", router_id
                #print "destination node id:", dest_node_id
                dest_node_ids_1.append(dest_node_id)
                next_source_ids_1.append(dest_node_id)
    #print "Source node ids: ", source_node_ids   
    print "Source node ids_1: ", source_node_ids_1
    print "Destination node ids: ", dest_node_ids_1
    #print "App process name: ", this.name    

    print "************For z-axis"
    print "Source node ids: ", source_node_ids
    dest_node_ids_2 = []
    router_ids_2 = []
    source_node_ids_2 = []
    #next_source_ids = []
    for i in range(len(source_node_ids_1)):
        source_node_ids_2.append(source_node_ids_1[i])
    for i in range(len(next_source_ids_1)):
        source_node_ids_2.append(next_source_ids_1[i])
    for i in range(len(source_node_ids_2)):
        router_ids_2.append(source_node_ids_2[i]/2)
    for eachLine in file_list:
        for i in range(len(router_ids_2)):
            router_id = router_ids_2[i]
            words = eachLine.split(' ')
            tmpRouterID = int(words[0])
            #print "*******source node ids: ", source_node_ids
            if tmpRouterID == router_id:
                #print eachLine
                dest_router_id = int(words[6])
                dest_node_id = dest_router_id * 2
                #print "Router id: ", router_id
                #print "destination node id:", dest_node_id
                dest_node_ids_2.append(dest_node_id)
                #next_source_ids.append(dest_node_id)
    #print "Source node ids: ", source_node_ids   
    print "*********z-axis: Source node ids: ", source_node_ids_2
    print "*********z-axis: Destination node ids: ", dest_node_ids_2  

    while True:
        if temp_list[0] == 1:           
            dest_ids = dest_node_ids
            if (len(source_node_ids) != len(dest_node_ids)):
                print "ERROR!!! Length of source node ids and length of destination node ids should be same!!!"
            for i in range(len(source_node_ids)):
                source_node_id = source_node_ids[i]
                dest = dest_node_ids[i]
                dest_app_name = this.name[0:len(this.name)-1] + str(dest) # e.g., appProcess46
                MPICommData = MPIData(data, count, data_type, dest, tag, comm, buffer_size, app_process_name, dest_app_name, flow_id) #TODO: may be no necessity of creating using LoadPacket after all...
                entity.reqService(0.0000001, "MPI_Send", MPICommData, "Node", source_node_id) #TODO: check whether this should really be a request service or not. A good value: 50.1
                print "hibernate at time:", this.entity.engine.now, "Destination node: ", dest
                this.hibernate() # TODO: need to check the placement of the hibernation.
                print "woke up at time:", this.entity.engine.now, "Destination node: ", dest    
                if i == len(source_node_ids) - 1:
                    temp_list[0] = 0
                    temp_list[1] = 1
        
        #this.sleep(10)

        if temp_list[1] == 1:           
            print "Now inside y-axis update method.............."
            dest_ids = dest_node_ids_1
            if (len(source_node_ids_1) != len(dest_node_ids_1)):
                print "ERROR!!! Length of source node ids and length of destination node ids should be same!!!"
            for i in range(len(source_node_ids_1)):
                source_node_id = source_node_ids_1[i]
                print "Source node ID:", source_node_id
                dest = dest_node_ids_1[i]
                print "Destination node ID: ", dest
                dest_app_name = this.name[0:len(this.name)-1] + str(dest) # e.g., appProcess46
                MPICommData = MPIData(data, count, data_type, dest, tag, comm, buffer_size, app_process_name, dest_app_name, flow_id) #TODO: may be no necessity of creating using LoadPacket after all...
                if source_node_id == 1:
                    entity.reqService(0.0000001, "MPI_Send", MPICommData, "Node", source_node_id) #TODO: check whether this should really be a request service or not. A good value: 50.1
                    print "hibernate at time:", this.entity.engine.now, "Destination node: ", dest, "App process name: ", app_process_name
                    this.hibernate() # TODO: need to check the placement of the hibernation.
                    print "woke up at time:", this.entity.engine.now, "Destination node: ", dest    
               
                elif source_node_id == 2:
                    MPICommData = MPIData(data, count, data_type, dest, tag, comm, buffer_size, "mpiProcessBcast_22", dest_app_name, flow_id) #TODO: may be no necessity of creating using LoadPacket after all...
                    entity.reqService(0.0000001, "MPI_Send", MPICommData, "Node", source_node_id) #TODO: check whether this should really be a request service or not. A good value: 50.1
                #    this.wake("mpiProcessBcast_22")
                    #mpiServiceBcast_2("test")     
                    temp_variable = 1
                    print "hibernate at time:", this.entity.engine.now, "Destination node: ", dest, "App process name: ", app_process_name, "temp variable: ", temp_variable
                    this.hibernate() # TODO: need to check the placement of the hibernation.
                    temp_variable = 0
                    print "woke up at time:", this.entity.engine.now, "Destination node: ", dest    
                if i == len(source_node_ids_1) - 1:
                    print "changing temp list value now...."
                    temp_list[1] = 0
                    temp_list[2] = 1      
        
        if temp_list[2] == 1:           
            print "Now inside z-axis update method.............."
            dest_ids = dest_node_ids_2
            if (len(source_node_ids_2) != len(dest_node_ids_2)):
                print "ERROR!!! Length of source node ids and length of destination node ids should be same!!!"
            for i in range(len(source_node_ids_2)):
                source_node_id = source_node_ids_2[i]
                print "Source node ID:", source_node_id
                dest = dest_node_ids_2[i]
                print "Destination node ID: ", dest
                dest_app_name = this.name[0:len(this.name)-1] + str(dest) # e.g., appProcess46
                MPICommData = MPIData(data, count, data_type, dest, tag, comm, buffer_size, app_process_name, dest_app_name, flow_id) #TODO: may be no necessity of creating using LoadPacket after all...
                if source_node_id == 1:
                    entity.reqService(0.0000001, "MPI_Send", MPICommData, "Node", source_node_id) #TODO: check whether this should really be a request service or not. A good value: 50.1
                elif source_node_id == 2:
                    MPICommData = MPIData(data, count, data_type, dest, tag, comm, buffer_size, "mpiProcessBcast_22", dest_app_name, flow_id) #TODO: may be no necessity of creating using LoadPacket after all...
                    entity.reqService(0.0000001, "MPI_Send", MPICommData, "Node", source_node_id) #TODO: check whether this should really be a request service or not. A good value: 50.1
                #    this.wake("mpiProcessBcast_22")
                    #mpiServiceBcast_2("test") 
                elif source_node_id == 8:
                    MPICommData = MPIData(data, count, data_type, dest, tag, comm, buffer_size, "mpiProcessBcast_28", dest_app_name, flow_id) #TODO: may be no necessity of creating using LoadPacket after all...
                    entity.reqService(0.0000001, "MPI_Send", MPICommData, "Node", source_node_id) #TODO: check whether this should really be a request service or not. A good value: 50.1
                elif source_node_id == 10:
                    MPICommData = MPIData(data, count, data_type, dest, tag, comm, buffer_size, "mpiProcessBcast_210", dest_app_name, flow_id) #TODO: may be no necessity of creating using LoadPacket after all...
                    entity.reqService(0.0000001, "MPI_Send", MPICommData, "Node", source_node_id) #TODO: check whether this should really be a request service or not. A good value: 50.1

                print "hibernate at time:", this.entity.engine.now, "Destination node: ", dest, "App process name: ", app_process_name
                this.hibernate() # TODO: need to check the placement of the hibernation.
                print "woke up at time:", this.entity.engine.now, "Destination node: ", dest    
                if i == len(source_node_ids_2) - 1:
                    print "changing temp list value now...."
                    #temp_list[1] = 0
                    temp_list[2] = 0

        if temp_list[2] == 0:       
            break
        
        #if temp_list[2] == 1:       
        #    break
        print "This is strange...."
        #this.sleep(end_time - this.entity.engine.now)
            #this.sleep(end_time - this.entity.engine.now)
        print "This is strange2....", this.entity.engine.now
        '''
        print "************For y-axis"
        print "Source node ids: ", source_node_ids
        dest_node_ids = []
        router_ids = []
        for i in range(len(source_node_ids)):
            router_ids.append(source_node_ids[i]/2)
        for eachLine in file_list:
            for i in range(len(router_ids)):
                router_id = router_ids[i]
                words = eachLine.split(' ')
                tmpRouterID = int(words[0])
                if tmpRouterID == router_id:
                    print eachLine
                    dest_router_id = int(words[5])
                    dest_node_id = dest_router_id * 2
                    dest_node_ids.append(dest_node_id)
                    source_node_ids.append(dest_node_id)
        #print "Source node ids: ", source_node_ids
        print "Destination node ids: ", dest_node_ids
       
        print "************For z-axis"
        print "Source node ids: ", source_node_ids
        dest_node_ids = []
        router_ids = []
        for i in range(len(source_node_ids)):
            router_ids.append(source_node_ids[i]/2)
        for eachLine in file_list:
            for i in range(len(router_ids)):
                router_id = router_ids[i]
                words = eachLine.split(' ')
                tmpRouterID = int(words[0])
                if tmpRouterID == router_id:
                    print eachLine
                    dest_router_id = int(words[6])
                    dest_node_id = dest_router_id * 2
                    dest_node_ids.append(dest_node_id)
                    #source_node_ids.append(dest_node_id)
        print "Destination node ids: ", dest_node_ids
        '''

    '''
    while True:
        flow_id = 0
        source_node_id = 1
        #dest_node_id = 7
        buffer_size = 2*1024*1024   # 1MB. A good value: 4GB
        app_process_name = this.name
        #print "Destination application name: ", dest_app_name
        data = None         # initial address of send buffer
        count = None        # number of elements in send buffer
        data_type = None     # datatype of each send buffer element
        comm = [3, 4, 5, 6]         # TODO: group of nodes (communicator)       
        tag = None          # This variable is for communication data on MPI_Send
        
        dest_ids = comm     
        for i in range(len(dest_ids)):
            dest = dest_ids[i]
            dest_app_name = this.name[0:len(this.name)-1] + str(dest) # e.g., appProcess46
            MPICommData = MPIData(data, count, data_type, dest, tag, comm, buffer_size, app_process_name, dest_app_name, flow_id) #TODO: may be no necessity of creating using LoadPacket after all...
            entity.reqService(0.0000001, "MPI_Send", MPICommData, "Node", source_node_id) #TODO: check whether this should really be a request service or not. A good value: 50.1
            #print "hibernate at time:", this.entity.engine.now, "Destination node: ", dest
            this.hibernate() # TODO: need to check the placement of the hibernation.
            #print "woke up at time:", this.entity.engine.now, "Destination node: ", dest
    
        this.sleep(end_time - this.entity.engine.now)
    '''
    # PLEASE comment the following line if you uncomment the above 
    # this.sleep(end_time - this.entity.engine.now)

#************* MPI broadcast with other node ids
def mpiProcessBcast_2(this, *args):
    entity = this.entity
    print "inside service broadcast 2 function..."
    dataObj = args[0]
    end_time = dataObj.source_node_id
    while True:
        print "Before hibernation....", dataObj.source_node_id, "Temp variable: ", temp_variable, "process name: ", this.name
        this.hibernate()
        #if temp_variable == 1:
        #this.wake("mpiProcessBcast1")

        # Now wake up the original process....
        entity.reqService(0.0000001, "wakeProcessStartingNode", None, "Node", 1) #TODO: check whether this should really be a request service or not. A good value: 50.1
                #    this.wake("mpiProcessBcast_22")
        print "After hibernation.....", dataObj.source_node_id, "Time: ", this.entity.engine.now
        '''
        flow_id = 0
        source_node_id = 1
        app_process_name = this.name
        #print "Destination application name: ", dest_app_name
        comm = [3, 4, 5, 6]         # TODO: group of nodes (communicator)       
        dest_ids = comm     
        final_barrier_obj = MPIBarrierData(node_id_this_process, end_time, app_process_name, dest_ids)
        entity.reqService(0.0000001, "MPI_Barrier", final_barrier_obj, "Node", source_node_id) #TODO: check whether this should really be a request service or not. A good value: 50.1
        print "hibernate at time:", this.entity.engine.now
        this.hibernate() # TODO: need to check the placement of the hibernation.
        print "woke up at time:", this.entity.engine.now
        '''
        

# MPI barrier call...
def mpiProcessBarrier(this, *args):
    entity = this.entity
    barrierObj = args[0]
    node_id_this_process = barrierObj.source_node_id
    end_time = barrierObj.end_time
    while True:
        flow_id = 0
        source_node_id = 1
        app_process_name = this.name
        #print "Destination application name: ", dest_app_name
        comm = [3, 4, 5, 6]         # TODO: group of nodes (communicator)       
        dest_ids = comm     
        final_barrier_obj = MPIBarrierData(node_id_this_process, end_time, app_process_name, dest_ids)
        entity.reqService(0.0000001, "MPI_Barrier", final_barrier_obj, "Node", source_node_id) #TODO: check whether this should really be a request service or not. A good value: 50.1
        print "hibernate at time:", this.entity.engine.now
        this.hibernate() # TODO: need to check the placement of the hibernation.
        print "woke up at time:", this.entity.engine.now
        this.sleep(end_time - this.entity.engine.now)


def appService(self, *args):
    node_id = args[0]
    processName = "appProcess" + str(node_id)   #TODO the processName should be like this at the moment, otherwise destination node process might malfunction...
    self.createProcess(processName, appProcess)
    self.startProcess(processName, node_id)

def mpiService(self, *args):
    node_id = args[0]
    processName = "mpiProcess" + str(node_id)   #TODO the processName should be like this at the moment, otherwise destination node process might malfunction...
    self.createProcess(processName, mpiProcess)
    self.startProcess(processName, node_id)

def mpiServiceRecv(self, *args):
    node_id = args[0]
    processName = "mpiProcessRecv" + str(node_id)   #TODO the processName should be like this at the moment, otherwise destination node process might malfunction...
    self.createProcess(processName, mpiProcessRecv)
    self.startProcess(processName, node_id)

def mpiServiceBcast(self, *args):
    bcastObj = args[0]
    node_id = bcastObj.source_node_id
    print "Node id: ", node_id
    #node_id = 0
    processName = "mpiProcessBcast" + str(node_id)   #TODO the processName should be like this at the moment, otherwise destination node process might malfunction...
    self.createProcess(processName, mpiProcessBcast)
    self.startProcess(processName, bcastObj)


########################### The following method is for testing a temporary node 2 packet sending...
def mpiServiceBcast_2(self, *args):
    bcastObj = args[0]
    node_id = bcastObj.source_node_id
    processName = "mpiProcessBcast_2" + str(node_id)   #TODO the processName should be like this at the moment, otherwise destination node process might malfunction...
    print processName
    self.createProcess(processName, mpiProcessBcast_2)
    self.startProcess(processName, bcastObj)

def mpiServiceBarrier(self, *args):
    node_id = args[0]
    processName = "mpiProcessBarrier" + str(node_id)   #TODO the processName should be like this at the moment, otherwise destination node process might malfunction...
    self.createProcess(processName, mpiProcessBarrier)
    self.startProcess(processName, node_id)

### The following creates another application service. TODO: may be merge this service with the original service(e.g., appService)
def appService_2(self, *args):
    print "Inside app service 2"
    node_id = args[0]
    processName = "appProcess_2" + str(node_id)   #TODO the processName should be like this at the moment, otherwise destination node process might malfunction...
    self.createProcess(processName, appProcess_2)
    self.startProcess(processName, node_id)

def statServiceNode(self, *args):
    node_id = args[0]
    self.createProcess("statProcessNode", statProcessNode)
    self.startProcess("statProcessNode", node_id)

def statServiceRouter(self, *args):
    router_id = args[0]
    self.createProcess("statProcessRouter", statProcessRouter)
    self.startProcess("statProcessRouter", router_id)

def statServiceInterface(self, *args):
    interface_id = args[0]
    #print "Inside service interface statistics collection..."
    self.createProcess("statProcessInterface", statProcessInterface)
    self.startProcess("statProcessInterface", interface_id)


simianEngine.attachService(nodes.Node, "appService", appService)
simianEngine.attachService(nodes.Node, "statServiceNode", statServiceNode)
simianEngine.attachService(router.Router, "statServiceRouter", statServiceRouter)
simianEngine.attachService(interface.Interface, "statServiceInterface", statServiceInterface)
simianEngine.attachService(nodes.Node, "appService_2", appService_2)
simianEngine.attachService(nodes.Node, "mpiService", mpiService)
simianEngine.attachService(nodes.Node, "mpiServiceRecv", mpiServiceRecv)
simianEngine.attachService(nodes.Node, "mpiServiceBcast", mpiServiceBcast)
simianEngine.attachService(nodes.Node, "mpiServiceBarrier", mpiServiceBarrier)
simianEngine.attachService(nodes.Node, "mpiServiceBcast_2", mpiServiceBcast_2)

source_node_id = 1
simianEngine.schedService(0, "mpiService", source_node_id, "Node", source_node_id)# TODO: check the last parameter: 1... may be this value would have to be changed

# destination node:
dest_node_id = 1
simianEngine.schedService(0, "mpiServiceRecv", dest_node_id, "Node", dest_node_id)# TODO: check the last parameter: 1... may be this value would have to be changed


# The followings are for MPI_Bcast
'''
end_time = endTime
source_node_id = 1
BcastObj = MPIBcastData(source_node_id, end_time)
simianEngine.schedService(50, "mpiServiceBcast", BcastObj, "Node", source_node_id)

end_time = endTime
source_node_id = 2
BcastObj = MPIBcastData(source_node_id, end_time)
simianEngine.schedService(50, "mpiServiceBcast_2", BcastObj, "Node", source_node_id)

source_node_id = 8
BcastObj = MPIBcastData(source_node_id, end_time)
simianEngine.schedService(50, "mpiServiceBcast_2", BcastObj, "Node", source_node_id)

source_node_id = 10
BcastObj = MPIBcastData(source_node_id, end_time)
simianEngine.schedService(50, "mpiServiceBcast_2", BcastObj, "Node", source_node_id)
'''

'''
end_time = endTime
source_node_id = 1
barrierObj = MPIBarrierData(source_node_id, end_time, None, None)
simianEngine.schedService(50, "mpiServiceBarrier", barrierObj, "Node", source_node_id)
'''
'''
# source node:
source_node_id = 1
simianEngine.schedService(0, "appService", source_node_id, "Node", source_node_id)# TODO: check the last parameter: 1... may be this value would have to be changed
'''
'''
# destination node:
dest_node_id = 7
simianEngine.schedService(0, "appService", dest_node_id, "Node", dest_node_id)# TODO: check the last parameter: 1... may be this value would have to be changed
'''
'''
# source node:
source_node_id = 2
simianEngine.schedService(0, "appService_2", source_node_id, "Node", source_node_id)# TODO: check the last parameter: 1... may be this value would have to be changed
'''

'''
# destination node:
dest_node_id = 7
simianEngine.schedService(0, "appService_2", dest_node_id, "Node", dest_node_id)# TODO: check the last parameter: 1... may be this value would have to be changed
'''

'''
start_time = 50
end_time = 55
collection_interval = 0.1

# statistics collectiion for nodes:
node_id_for_stat = 1
intervalObj = IntervalData(start_time, end_time, collection_interval, node_id_for_stat)
simianEngine.schedService(0, "statServiceNode", intervalObj, "Node", node_id_for_stat)

# statistics collection for routers:
router_id_for_stat = 1
intervalObj = IntervalData(start_time, end_time, collection_interval, router_id_for_stat)
simianEngine.schedService(0, "statServiceRouter", intervalObj, "Router", router_id_for_stat)

# statistics collection for interfaces:
interface_id_for_stat = 6
intervalObj = IntervalData(start_time, end_time, collection_interval, interface_id_for_stat)
simianEngine.schedService(0, "statServiceInterface", intervalObj, "Interface", interface_id_for_stat)
'''

simianEngine.run()       
simianEngine.exit()


'''
### Asynchronously sending data (i.e., some packets)...
def appProcess(this):
    entity = this.entity
    entity.out.write("Process app started\n")
    while True:
        source_node_id = 1
        dest_node_id = 46
        buffer_size =1*1024*1024   # 1MB
        app_process_name = this.name
        objCommData = LoadData(dest_node_id, buffer_size, app_process_name) #TODO: may be no necessity of creating using LoadPacket after all...
        entity.reqService(10, "aSyncSendData", objCommData, "Node", source_node_id) #TODO: check whether this should really be a request service or not. source_node_id should be 1 at the moment.
        this.hibernate()
'''
'''
### Asynchronously send one packet...
def appProcess(this):
    entity = this.entity
    #entity.out.write("Process app started\n")
    while True:
        source_node_id = 1
        dest_node_id = 46
        data_size = 64*1024   # 1MB
        data = None
        app_process_name = this.name

        ### The following is done to let this process know when data reaches its destination...   

        #entity.reqService(minDelay, )

        objCommPacket = LoadPacket(dest_node_id, data_size, app_process_name, data) #TODO: may be no necessity of creating using LoadPacket after all...
        entity.reqService(10, "aSyncSendPacket", objCommPacket, "Node", source_node_id) #TODO: check whether this should really be a request service or not
        print "The process should wake up here to let know that the data has reached it's destination..."    
        ## An assumption: data will reach its destination, before ACK returns back to source..,
        this.hibernate()
        print "The packet has reached its destination..."
        this.hibernate()
        print "The source has received its ACK..."
'''

'''# Delete the following later....
# This process is spawn by application process. This child process wakes up the application process (which is hibernating), once the data reaches its destination.
def childAppProcess(this):
    while True:
        print "Inside the child application process..."
        this.hibernate()

class ApplicationClass():
'''
'''
# Synchronously send one packet...
def appProcess(this, *args):
    entity = this.entity
    entity.out.write("Process app started\n")
    #print "Application process for node id: ", args[0]
    #print "Process name: ", this.name
    node_id_this_process = args[0]
    while True:
        source_node_id = 1
        dest_node_id = 46
        data_size = 64*1024   # 1MB
        data = None
        app_process_name = this.name
        dest_app_name = this.name[0:len(this.name)-1] + str(dest_node_id) # e.g., appProcess46
        #print "Destination application name: ", dest_app_name
        #print "The process name: ", this.name 
        objCommPacket = LoadPacket(dest_node_id, data_size, app_process_name, dest_app_name, data) #TODO: may be no necessity of creating using LoadPacket after all...
        if(node_id_this_process == source_node_id):
            entity.reqService(50, "syncSendPacket", objCommPacket, "Node", source_node_id) #TODO: check whether this should really be a request service or not
      
        if(node_id_this_process == dest_node_id):
            this.hibernate() # TODO: need to check the placement of the hibernation.
            print "The data reached its destination", this.entity.engine.now
        #print "The data reached itis destination at time: ", this.entity.engine.now
        if(node_id_this_process == source_node_id):
            this.hibernate()
            print "The ACK reached its destination at time: ", this.entity.engine.now
'''

'''
for i in range(len(node_source_IDs)):
    objComm = Load(node_destination_IDs, load_size, time_window, distribution_type)            
    simianEngine.schedService(0, "sendService", objComm, "Node", node_source_IDs[i])
'''

'''
# The following schedules multiple sources multiple destinations file transmission 
for i in range(len(node_source_IDs)):
    for j in range(len(node_destination_IDs)):
        single_destination = []
        single_destination.append(node_destination_IDs[j])
        objComm = Load(single_destination, load_size, time_window, distribution_type)            
        simianEngine.schedService(0, "sendService", objComm, "Node", node_source_IDs[i])
'''        

'''
# The following creates and sends variable-size packet from a source to destination
source_node_id = 0
dest_node_id = 46
data_size = 64*1024 # 64KB
data = None
    
    
objCommPacket = LoadPacket(dest_node_id, data_size, data)
simianEngine.schedService(0, "syncSend", objCommPacket, "Node", source_node_id)
'''
'''
for i in range(9):
    source_node_id = 0
    dest_node_id = 46
    data_size = 64*1024 # 64KB
    data = None
    objCommPacket = LoadPacket(dest_node_id, data_size, data)
    simianEngine.schedService(10, "sendPacket", objCommPacket, "Node", source_node_id)

for i in range(10):
    source_node_id = 10
    dest_node_id = 46
    data_size = 60 # 64KB
    data = None
    objCommPacket = LoadPacket(dest_node_id, data_size, data)
    simianEngine.schedService(50, "sendPacket", objCommPacket, "Node", source_node_id)
'''

'''
# The following creates and send variable-size data from a source to destination
source_node_id = 10
dest_node_id = 46
buffer_size = 1*1024*1024   # 1MB

objCommData = LoadData(dest_node_id, buffer_size)
simianEngine.schedService(0, "syncSendData", objCommData, "Node", source_node_id)
'''

'''
# The following tests the "asynchronous" send of packets to destination 
source_node_id = 10
dest_node_id = 46
data_size = 64*1024   # 1MB
data = None

objCommPacket = LoadPacket(dest_node_id, data_size, data)
simianEngine.schedService(0, "asyncSend", objCommPacket, "Node", source_node_id)
'''


'''
# This service is scheduled at the end of the simulation to collect node related statistics
if(DEBUG_NODE_STATS == 1):
    for i in range(len(node_source_IDs)):
        simianEngine.schedService(endTime - 0.00001, "nodeStatistics", None, "Node", node_source_IDs[i])
    
    for i in range(len(node_destination_IDs)):
        simianEngine.schedService(endTime - 0.00001, "nodeStatistics", None, "Node", node_destination_IDs[i])
        
if(DEBUG_ROUTER_STATS == 1):
    simianEngine.schedService(endTime - 0.00001, "routerStatistics", None, "Router", 23)
'''
'''
if(DEBUG_LINK_STATS == 1):
    simianEngine.schedService(endTime - 0.00001, "linkStatistics", None, "Interface", 5)
#simianEngine.schedService(endTime - 0.00001, "changeInterfaceVariable", None, "Router", 0)
'''

'''
### Synchronously sending data (i.e., some packets)...
def appProcess(this):
    entity = this.entity
    entity.out.write("Process app started\n")
    while True:
        source_node_id = 1
        dest_node_id = 46
        buffer_size =1*1024*1024   # 1MB
        #data = None
        app_process_name = this.name
        #print "The process name: ", this.name 
        objCommData = LoadData(dest_node_id, buffer_size, app_process_name) #TODO: may be no necessity of creating using LoadPacket after all...
        entity.reqService(10, "syncSendData", objCommData, "Node", source_node_id) #TODO: check whether this should really be a request service or not. source_node_id should be 1 at the moment.
        print "............................before hibernation", this.entity.engine.now
        this.hibernate() # TODO: need to check the placement of the hibernation.
        print "..............................after hibernation. Time: ", this.entity.engine.now 
'''
