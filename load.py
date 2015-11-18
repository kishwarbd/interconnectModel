"""
@package    load
@author     Mohammad Abu Obaida    
"""


class Load:
    """
    @author Mohammad Abu Obaida
    This class defines the application load that we can pass to the etity as we schedService. 
    Take note that we can pass objects to entities when we schedule service.
    """
    def __init__ (self, destList, loadSize,timeWindow = 1, distribution="uniform"):
        """
        Constructor for Load class. Assigns destinations, loadSize, timeWindow, distribution to object of the class
        """
        assert len (destList) >=0, "Destination list empty"
        assert (loadSize >=0), "Enter a positive value as loadSize"
        assert (timeWindow >= 0), "Enter a positive value as timeWindow"
        self.destinations = destList
        self.loadSize = loadSize
        self.timeWindow = timeWindow
        self.distribution = distribution#inter arrival time distribution

class LoadPacket:
    """
    This class defines the application load for a single packet.
    """
    def __init__(self, destNodeID, dataSize,  appProcessName, destAppName, flowID, data = None):
        """
        Constructor for LoadPacket class.
        """
        assert (dataSize >= 0), "Enter a positive value as for data size"
        self.dest_node_id = destNodeID
        self.data_size = dataSize
        self.data = data
        self.app_process_name = appProcessName
        self.dest_app_name = destAppName
        self.flow_id = flowID

class LoadData:
    """
    This class defines the application load for a single data.
    """
    def __init__(self, destNodeID, bufSize, appProcessName, destAppName, flowID):
        """
        Constructor for LoadPacket class.
        """
        assert (bufSize >= 0), "Enter a positive value as for data size"
        self.dest_node_id = destNodeID
        self.buffer_size = bufSize
        self.app_process_name = appProcessName
        self.dest_app_name = destAppName
        self.flow_id = flowID

class IntervalData:
    #TODO: enter class information later...
    def __init__(self, startTime, endTime, collectionInterval, entityID):
        #TODO: enter constructor information later...
        self.start_time = startTime
        self.end_time = endTime
        self.collection_interval = collectionInterval
        self.entity_id = entityID

class MPIData:
    """
    This class defines the MPI load for a single data.
    """
    def __init__(self, data, count, data_type, destNodeID, tag, comm, bufSize, appProcessName, destAppName, flowID):
        """
        Contructor for MPIData class.
        """
        assert (bufSize >= 0), "Enter a positive value as for data size"
        self.data = data
        self.count = count
        self.data_type = data_type
        self.dest_node_id = destNodeID
        self.tag = tag
        self.comm = comm
        self.buffer_size = bufSize
        self.app_process_name = appProcessName
        self.dest_app_name = destAppName
        self.flow_id = flowID

class MPIRecvData:
    """
    This class defines the MPI load for a single data.
    """
    def __init__(self, data, count, data_type, destNodeID, tag, comm, status, bufSize, appProcessName, destAppName, flowID):
        """
        Contructor for MPIData class.
        """
        assert (bufSize >= 0), "Enter a positive value as for data size"
        self.data = data
        self.count = count
        self.data_type = data_type
        self.dest_node_id = destNodeID
        self.tag = tag
        self.comm = comm
        self.status = status        # This variable provides information about the received message
        self.buffer_size = bufSize
        self.app_process_name = appProcessName
        self.dest_app_name = destAppName
        self.flow_id = flowID

class MPIBcastData:
    """
    This class defines the MPI broadcast single data.
    """
    def __init__(self, sourceNodeID, endTime):
        """
        Contructor for MPI broadcast data class.
        """
        self.source_node_id = sourceNodeID
        self.end_time = endTime

class MPIBarrierData:
    """
    This class defines the MPI broadcast single data.
    """
    def __init__(self, sourceNodeID, endTime, appProcessName, destIDs):
        """
        Contructor for MPI broadcast data class.
        """
        self.source_node_id = sourceNodeID
        self.end_time = endTime
        self.app_process_name = appProcessName
        self.dest_ids = destIDs        
