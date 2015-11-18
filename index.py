##
#@mainpage
#
#@author Mohammad Abu Obaida, Graduate Intern, LANL & PhD Student, Computer Science, Florida Intl University
#
#
#Summary
#=======
#This technical documentation discusses the design objective and usage of InterconenctSim,
#which is a packet based HPC interconnection simulator. We have a detailed implementation of
#Cielo interconnection topology, the supercomputer at LANL from Cray Systems.
#However, with fair amount of effort the interconnection simulator can be extented
#to simulate other future systems such as Trinity. Taking advantage of simplistic design of
#Simian Parallel Discrete Event Simulator (PDES), we interpreted the task of interconnection
#modeling as modeling of properly orchestrated queuing system. We extended the simian entity to
#better represent the nodes and routers as they are present in a Gemini torus interconnect.
#One can take the advantage of the configurable parameters and play with different test scenerios.
#
#Cielo is a supercomputer cluster serving LANL. The system was developed by Cray Systems.
#For high performance interconnection among the compute nodes cray exploited
#Gemini torus wrap-around, a Cray proprietary HPC interconnection topology for Supercomputers.
#The dimension of the topology is 16 x 12 x 24 (X x Y x Z). Each node
#in the torus topology is forrmed by grouping two compute nodes that are physically
#located in the same blade. In other words, each blade contains two compute
#node and a gemini router. The gemini router is the primary contact for the compute
#nodes to send or receive data to and from other nodes. Multiple physical manycore
#processors lying in the same compute node are directly connected with one NIC
#card connecting it to the gemini router. The NIC card supports Fast Memory
#Access (FMA), Block Transfer and few other access modes. This are basically different
#priority modes for transferring that enables either low latency or higher bandwidth
#transfer modes. More on Gemini network can be found in Cray's Gemini
#whitepaper
#
#
#
#
#HPC Gemini Torus Interconnection Simulation
#
#Usage
#-----
#Open up the intconnsim.py file and lets walk through how the cluster is initialized and data 
#transmission is scheduled.
#
#The code snippet is divided into five numbered blocks. At the beginning we import the
#necessary libraries and define engine parameters. 
#   - In block 1, a cluster of clusters.PrototypeGeminiTorusCielo type is created with supplied
#     torus dimensions. Here we are initiating all the nodes and routers along with the interconnection. 
#     Details of cluster formation can be found is clusters package and prototypeGeminiTorusCielo 
#     class. 
#   - In block 2, we assigned some random nodes of the cluster to an application. Traffic from 
#      different applications can be simulated at the same time. 
#   - After that in lock 3, a data communication object objComm (load.Load) is created 
#   - In block 4 the object from block 3 will further be passed (in block 4) to one of the 
#     allocated nodes of the application to schedule the packets destined to node(s) in the 
#     machineList of the objComm over a time window. Time window is a mechanism to allows imitation of
#     the request generation in a physical processor.
#   - Block 5 simply runs the simian simulation engine.
#
#
#
#
#
#
#Trace
#-----
#Traffic trace is wrriten to the file using the simian.out.write from the nodes and from the routers.
# An example Trace record:
#   - Fields
#       1. tt : Traffic Trace, each trace line starts with TT 
#       2. n  : This trace record is written from a node, or r: Router
#       3. now(float): current simulation time
#       4. operation: s=send, re=resend, rc = receive, d = drop
#       5. from_hop : Whoever reports the message or the trace. Modifies from_hop first before sending
#       6. next_hop : This hop gets the packet next
#       7. ldType: type of load
#       8. packet_size: size of the total packet (in bytes), size is fake size if you don't have load
#       9. src_id : Main sender of the packet
#       10. dest_id : destination of the message
#       11. seq_no: unique sequence numerber of this packet. Sequence number is formed with src_id+dest_id+msg_uid
#
#
#*Content of this html or tex file is generated from index.py file.
