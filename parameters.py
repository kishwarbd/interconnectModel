
# TODO: change the following to bit mask
DEBUG_PACKET_ROUTE = 0  # show each packet's routing information
DEBUG_OVERALL_STATS = 0 # To be used later 
DEBUG_NODE_STATS = 0    # To show statistics of node
DEBUG_ROUTER_STATS = 0 # To show statistics of router
DEBUG_LINK_STATS = 1    # To show statistics of link
DEBUG_PRINT_INFO = 0    # This parameter is responsible for printing all the detail info

#------------------------ interconnect parameters
interconnect_type = "torus_3D"

#------------------------ Torus specific parameters
torus_dims = 3 # Number of dimension of the torus network. For torus_3D, the value is "3".  TODO: make provision for using this variable. currently not used
torus_dim_size = 4       # Number of routers at each direction. TODO: use this parameter
torus_dim_size_0 = 2     # Dimension along X-axis
torus_dim_size_1 = 2     # Dimension along y-axis
torus_dim_size_2 = 2     # Dimension along z-axis

### Router parameters
torus_bandwidth = 6.8*1024*1024*1024 # Bandwidth between routers. TODO: make provision for this variable

torus_bandwidth_0 = 1.8*1024*1024*1024 # bandwidth along x-axis
torus_bandwidth_1 = 4.7*1024*1024*1024 # bandwidth along y-axis
torus_bandwidth_2 = 6.8*1024*1024*1024 # bandwidth along z-axis

torus_inbuf_size = 10*1024*1024*1024 # input buffer size(in bytes) between routers.  
torus_inbuf_size_0 = 1*1024*1024 # TODO: make provision for this variable. buffer size along x-axis
torus_inbuf_size_1 = 1*1024*1024 # TODO.buffer size along x-axis
torus_inbuf_size_2 = 1*1024*1024 # TODO.buffer size along x-axis

torus_outbuf_size = 1*1024*1024 # output buffer size (in bytes) between routers. TODO: make provision for this variable
torus_outbuf_size_0 = 1*1024*1024 # TODO
torus_outbuf_size_1 = 1*1024*1024 # TODO
torus_outbuf_size_2 = 1*1024*1024 # TODO

torus_prop_delay = 1*10**-6     # propagation delay (in seconds) between routers
torus_prop_delay_0 = 1*10**-6 # TODO: make provision for this variable
torus_prop_delay_1 = 1*10**-6 # TODO.
torus_prop_delay_2 = 1*10**-6 # TODO.

torus_proc_time = 10e-9# router's packet processing time (in seconds)

### Node parameters
torus_node_per_router = 2 # number of nodes connected to each router. TODO

#TODO************************::: torus node bandwidth is now very very large...
torus_node_bandwidths = 20*(10.0*1024*1024*1024/8.0) * 2.0 # bandwidth of the link between node and it's attached router. TODO: value check. BW of local nodes, 10Gbps
torus_node_bandwidth_0 = 10.0*1024*1024*1024/8.0 #TODO.
torus_node_bandwidth_1 = 10.0*1024*1024*1024/8.0 #TODO.

torus_node_inbuf_size = None          # Not used now
#TODO*******************: torus node output buffer size is also a large value now...
torus_node_outbuf_size = 10*1024*1024*1024 # the output buffer size of the node

torus_node_prop_delay = 1.24*10**-6 
torus_node_prop_delay_0 = 1.24*10**-6 #TODO: make provision for this variable
torus_node_prop_delay_1 = 1.24*10**-6 #TODO: make provision for this variable

#--------------------------------- Some misc parameters
# Need to work on these parameters:
ack_size = 100  # TODO: currently, the ack size is of some minimum length for correct interface statistics collection...
packet_load_size = 100*1024*1024 # TODO: The parameter may not be needed now. Need to check though. 

# Some misc parameters: need to work on these too...(may be not needed)
misc_time_window = 0.1 
misc_distribution_type = "uniform"

# Need to remove these parameters later:
node_time_to_resend_packet = 0.2 
node_resend_try = 3
node_packet_max_load = 64*1024
torus_num_of_links = 8
topology_file_name = "configuration.txt" # This is the file where the generated topology is temporarily stored (just for saving purpose!) TODO: make provision such that this file is not needed
mpiMsgSize = 128*1024      # This is the packet size that is sent by syncSendData() process
no_of_flows = 2

#--------------------------------- Application parameters

application_type = None

type_random = None # random destination
type_random_nearest_neighbor = None
type_unicast = None
type_reduce = None
type_all_to_all = None
type_snap = None

### Application specific parameters
app_random_iat = None # inter-arrival time for packets
app_random_data_size = None
