#-------------------------------------------------------------------------
# This class is responsible for showing different output statistics 
#-------------------------------------------------------------------------

import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import numpy as np
#import scipy.stats as stats

class Output(object):
	def __init__(self):
		# graph properties
		self.color = [164.0/255, 221.0/255, 243.0/255]
		self.figsize = [9, 7.5]
		self.fontsize = {'font.size': 24}

		# Line graph properties
		self.linewidth = 3

		# bar graph properties
		self.width = 0.5
		self.xlimit = 0.5

		# error bar properties
		self.elineWidth = 2.5
		self.capsize = 10
		
		# Histogram properties
		self.binlength = 16
		self.noOfBins = 25
		#print "Inside output stat..."

	def plotRTTBufDelay(self, RTTmean):
		locXCoordinates = np.arange(len(RTTmean))		 # the x locations for the groups
		xvals = locXCoordinates+self.width/2
		plt.figure(figsize=self.figsize)
		plt.rcParams.update(self.fontsize)
		p1 = plt.bar(locXCoordinates, RTTmean, self.width, color = self.color)
		plt.ylabel('Average round trip time (ms)')
		plt.xlabel('Buffer check delay (ns)')
		plt.xticks(locXCoordinates+self.width/2., ('0.01', '1', '100'))
		plt.xlim([min(xvals) - self.xlimit, max(xvals) + self.xlimit])
		plt.ylim([0.9, 1.1])		
		plt.grid(True)
		plt.show()

	def plotRTTBufDelayIntLatency(self, RTTDelayLatency):
		locXCoordinates = np.arange(len(RTTDelayLatency))		 # the x locations for the groups
		xvals = locXCoordinates+self.width/2
		plt.figure(figsize=self.figsize)
		plt.rcParams.update(self.fontsize)
		p1 = plt.bar(locXCoordinates, RTTDelayLatency, self.width, color = self.color)
		plt.ylabel('Average round trip time (ms)')
		plt.xlabel('Transmission delay (ms)')
		plt.xticks(locXCoordinates+self.width/2., ('0.01', '1', '100'))
		plt.xlim([min(xvals) - self.xlimit, max(xvals) + self.xlimit])
		plt.grid(True)
		plt.show()

	def plotRTTDelayMPISize(self, RTTDelayMPISize):
		locXCoordinates = np.arange(len(RTTDelayMPISize))		 # the x locations for the groups
		xvals = locXCoordinates+self.width/2
		plt.figure(figsize=self.figsize)
		plt.rcParams.update(self.fontsize)
		p1 = plt.bar(locXCoordinates, RTTDelayMPISize, self.width, color = self.color)
		plt.ylabel('Average round trip time (ms)')
		plt.xlabel('MPI message size (KB)')
		plt.xticks(locXCoordinates+self.width/2., ('50', '150', '250'))
		plt.xlim([min(xvals) - self.xlimit, max(xvals) + self.xlimit])
		plt.ylim([0.9, 1.1])		
		plt.grid(True)
		plt.show()

	def plotRTTBandwidth(self, RTTBandwidth):
		locXCoordinates = np.arange(len(RTTBandwidth))		 # the x locations for the groups
		xvals = locXCoordinates+self.width/2
		plt.figure(figsize=self.figsize)
		plt.rcParams.update(self.fontsize)
		p1 = plt.bar(locXCoordinates, RTTBandwidth, self.width, color = self.color)
		plt.ylabel('Average round trip time (ms)')
		plt.xlabel('Bandwidth of routers (GB)')
		plt.xticks(locXCoordinates+self.width/2., ('1', '10', '100'))
		plt.xlim([min(xvals) - self.xlimit, max(xvals) + self.xlimit])
		plt.ylim([0.9, 1.1])		
		plt.grid(True)
		plt.show()

	def plotDroppedPacketsRatio(self, droppedPacketsRatio):
		locXCoordinates = np.arange(len(droppedPacketsRatio))		 # the x locations for the groups
		xvals = locXCoordinates+self.width/2
		plt.figure(figsize=self.figsize)
		plt.rcParams.update(self.fontsize)
		p1 = plt.bar(locXCoordinates, droppedPacketsRatio, self.width, color = self.color)
		plt.ylabel('Percentage of dropped packets')
		plt.xlabel('MPI message size (KB)')
		plt.xticks(locXCoordinates+self.width/2., ('100', '150', '200', '250'))
		plt.xlim([min(xvals) - self.xlimit, max(xvals) + self.xlimit])
		# plt.ylim([0.9, 1.1])		
		plt.grid(True)
		plt.show()

	def plotDroppedPacketsNICRatio(self, droppedPacketsNICRatio):
		locXCoordinates = np.arange(len(droppedPacketsNICRatio))		 # the x locations for the groups
		xvals = locXCoordinates+self.width/2
		plt.figure(figsize=self.figsize)
		plt.rcParams.update(self.fontsize)
		p1 = plt.bar(locXCoordinates, droppedPacketsNICRatio, self.width, color = self.color)
		plt.ylabel('Percentage of dropped packets')
		plt.xlabel('NIC buffer size (KB)')
		plt.xticks(locXCoordinates+self.width/2., ('64', '128', '258', '512'))
		plt.xlim([min(xvals) - self.xlimit, max(xvals) + self.xlimit])
		plt.ylim([0, 120])		
		plt.grid(True)
		plt.show()

	def plotDroppedPacketsRouter(self, droppedPacketsRouter):
		locXCoordinates = np.arange(len(droppedPacketsRouter))		 # the x locations for the groups
		xvals = locXCoordinates+self.width/2
		plt.figure(figsize=self.figsize)
		plt.rcParams.update(self.fontsize)
		p1 = plt.bar(locXCoordinates, droppedPacketsRouter, self.width, color = self.color)
		plt.ylabel('Percentage of dropped packets')
		plt.xlabel('MPI message size (KB)')
		plt.xticks(locXCoordinates+self.width/2., ('200', '400', '600'))
		plt.xlim([min(xvals) - self.xlimit, max(xvals) + self.xlimit])
		plt.ylim([0, 100])		
		plt.grid(True)
		plt.show()

	def plotDroppedPacketsRouterBufferSize(self, droppedPacketsRatioBuffer):
		locXCoordinates = np.arange(len(droppedPacketsRatioBuffer))		 # the x locations for the groups
		xvals = locXCoordinates+self.width/2
		plt.figure(figsize=self.figsize)
		plt.rcParams.update(self.fontsize)
		p1 = plt.bar(locXCoordinates, droppedPacketsRatioBuffer, self.width, color = self.color)
		plt.ylabel('Percentage of dropped packets')
		plt.xlabel('Router buffer size (KB)')		# 
		plt.xticks(locXCoordinates+self.width/2., ('300', '400', '500'))
		plt.xlim([min(xvals) - self.xlimit, max(xvals) + self.xlimit])
		plt.ylim([0, 25])		
		plt.grid(True)
		plt.show()

	def bytesSentInterfaceGraph(self, times, all_bytes_sent):
		plt.figure(figsize=self.figsize)
		plt.rcParams.update(self.fontsize)
		#(quantiles, values), (slope, intercept, r)  = stats.probplot(arrivals, dist = distribution_type)
		plt.plot(times, all_bytes_sent, linewidth = self.linewidth)
		#plt.plot(quantiles, quantiles * slope + intercept, 'r--', linewidth = self.linewidth, label = "Theoretical")
		plt.xlabel('Time (s)')
		plt.ylabel('Bytes sent (MB)')
		plt.title('')
		#plt.yticks(np.arange(-10,31,5))
		#plt.legend("Observed", "Theoretical")
		plt.grid(True)
		plt.show()	

	def bytesSentNodeGraph(self, times, all_bytes_sent):
		plt.figure(figsize=self.figsize)
		plt.rcParams.update(self.fontsize)
		#(quantiles, values), (slope, intercept, r)  = stats.probplot(arrivals, dist = distribution_type)
		plt.plot(times, all_bytes_sent, linewidth = self.linewidth)
		plt.xlabel('Time (s)')
		plt.ylabel('Bytes sent (MB)')
		plt.title('')
		#plt.yticks(np.arange(-10,31,5))
		#plt.legend("Observed", "Theoretical")
		plt.grid(True)
		plt.show()

	def bytesSentRouterGraph(self, times, all_bytes_sent):
		plt.figure(figsize=self.figsize)
		plt.rcParams.update(self.fontsize)
		#(quantiles, values), (slope, intercept, r)  = stats.probplot(arrivals, dist = distribution_type)
		plt.plot(times, all_bytes_sent, linewidth = self.linewidth)
		plt.xlabel('Time (s)')
		plt.ylabel('Bytes sent (MB)')
		plt.title('')
		#plt.yticks(np.arange(-10,31,5))
		#plt.legend("Observed", "Theoretical")
		plt.grid(True)
		plt.show()

	def bytesACKNodeGraph(self, times, all_bytes_rcvd):
		plt.figure(figsize=self.figsize)
		plt.rcParams.update(self.fontsize)
		#(quantiles, values), (slope, intercept, r)  = stats.probplot(arrivals, dist = distribution_type)
		plt.plot(times, all_bytes_rcvd, linewidth = self.linewidth)
		#plt.plot(times, all_bytes_rcvd, 'ob', label = "Received")
		#plt.plot(quantiles, quantiles * slope + intercept, 'r--', linewidth = self.linewidth, label = "Theoretical")
		plt.xlabel('Time (s)')
		plt.ylabel('Bytes received (KB)')
		plt.title('')
		#plt.yticks(np.arange(0,10,2))
		#plt.yticks(np.arange(-10,31,5))
		#plt.legend("Observed", "Theoretical")
		plt.grid(True)
		plt.show()

	def throughputInterfaceGraph(self, times_interface, flow0_throughput_interface, flow1_throughput_interface):
		plt.figure(figsize=self.figsize)
		plt.rcParams.update(self.fontsize)
		#(quantiles, values), (slope, intercept, r)  = stats.probplot(arrivals, dist = distribution_type)
		plot1, = plt.plot(times_interface, flow0_throughput_interface, linewidth = self.linewidth, label = 'Flow 0')
		#plt.plot(times, all_bytes_rcvd, 'ob', label = "Received")
		plot2, = plt.plot(times_interface, flow1_throughput_interface, 'r--', linewidth = self.linewidth, label = 'Flow 1')
		plt.xlabel('Time (s)')
		plt.ylabel('Throughput (MB/s)')
		#plt.xticks(np.arange(50,52,0.2))
		plt.title('')
		plt.legend([plot1, plot2], ["Flow 0", "Flow 1"])
		#plt.yticks(np.arange(-10,31,5))
		#plt.legend("Flow 0", "Flow 1")
		plt.grid(True)
		plt.show()

outputObj = Output()
outputObj = Output()

files = open("intconnsim.0.out")

file_list =  files.readlines()

times_node = []
times_router = []
times_interface = []

node_sent_packets = []
node_rcvd_packets = []
router_sent_packets = []
flow0_interface_sent_packets = []
flow1_interface_sent_packets = []
flow0_interface_sent_packets_MB = []
flow1_interface_sent_packets_MB = []

for each_line in file_list:
	words = each_line.split()
	if words[0] == 'N':
		times_node.append(float(words[1]))
		node_sent_packets.append(float(words[2]))
		node_rcvd_packets.append(float(words[3]))
	if words[0] == 'R':
		times_router.append(float(words[1]))
		router_sent_packets.append(float(words[2]))
	if words[0] == 'I':
		if words[1] == '0':	#TODO: '0' should be converted to a number, not a string...
			times_interface.append(float(words[2]))
			flow0_interface_sent_packets.append(float(words[3]))
			flow0_interface_sent_packets_MB.append(float(words[3])/1024/1024)
		if words[1] == '1':
			flow1_interface_sent_packets.append(float(words[3]))
			flow1_interface_sent_packets_MB.append(float(words[3])/1024/1024)

flow0_throughput_interface = []
flow1_throughput_interface = []
times_interface_actual = []
for i in range(len(times_interface)):
	if i == len(times_interface) - 1:
		continue
	time_difference = times_interface[i+1] - times_interface[i]
	times_interface_actual.append(times_interface[i+1])
	flow0_throughput_interface.append(((flow0_interface_sent_packets[i+1] - flow0_interface_sent_packets[i])/time_difference)/1024.0/1024.0)
	flow1_throughput_interface.append(((flow1_interface_sent_packets[i+1] - flow1_interface_sent_packets[i])/time_difference)/1024.0/1024.0)
#print len(times_interface_actual)
#print len(flow0_throughput_interface)
#print len(flow1_throughput_interface)
outputObj.throughputInterfaceGraph(times_interface_actual, flow0_throughput_interface, flow1_throughput_interface)

#outputObj.bytesSentNodeGraph(times_node, node_sent_packets)
#outputObj.bytesACKNodeGraph(times_node, node_rcvd_packets)
#outputObj.bytesSentRouterGraph(times_router, router_sent_packets)

#outputObj.bytesSentInterfaceGraph(times_interface, flow0_interface_sent_packets_MB)
#outputObj.bytesSentInterfaceGraph(times_interface, flow1_interface_sent_packets_MB)

#print interface_sent_packets
### previous version of time-series graph
'''
#Create time-series graph...
start_time = 50
end_time = 52

files = open("output_interface6.out")
file_list =  files.readlines()
all_bytes_sent = []
for each_line in file_list:
	bytes_sent = int(each_line)
	all_bytes_sent.append(bytes_sent)
print len(all_bytes_sent)
times = np.linspace(start_time, end_time, len(all_bytes_sent))
outputObj.bytesSentInterfaceGraph(times, all_bytes_sent)


files = open("output_node2_sent.out")
file_list =  files.readlines()
all_bytes_sent = []
for each_line in file_list:
	bytes_sent = int(each_line)/1024/1024
	all_bytes_sent.append(bytes_sent)

files = open("output_node2_rcvd.out")
file_list =  files.readlines()
all_bytes_rcvd = []
for each_line in file_list:
	bytes_rcvd = int(each_line)/1024
	all_bytes_rcvd.append(bytes_rcvd)

times = np.linspace(start_time, end_time, len(all_bytes_sent))
outputObj.bytesSentNodeGraph(times, all_bytes_sent, all_bytes_rcvd)
outputObj.bytesACKNodeGraph(times, all_bytes_sent, all_bytes_rcvd)
'''
'''
droppedPacketsRatioBuffer = [504, 66, 0]
for i in range(len(droppedPacketsRatioBuffer)):
	droppedPacketsRatioBuffer[i] = (droppedPacketsRatioBuffer[i]/4000.0) * 100 
outputObj.plotDroppedPacketsRouterBufferSize(droppedPacketsRatioBuffer)

droppedPacketsRouter = [0, 546, 1854]
for i in range(len(droppedPacketsRouter)):
	droppedPacketsRouter[i] = (droppedPacketsRouter[i]/4000.0) * 100 # 4000 packets are transmitted inside the system (i.e., each node 1000 packets)
#print droppedPacketsNICRatio
outputObj.plotDroppedPacketsRouter(droppedPacketsRouter)

droppedPacketsNICRatio = [4000, 0, 0, 0]
for i in range(len(droppedPacketsNICRatio)):
	droppedPacketsNICRatio[i] = (droppedPacketsNICRatio[i]/4000.0) * 100 
#print droppedPacketsNICRatio
outputObj.plotDroppedPacketsNICRatio(droppedPacketsNICRatio)

droppedPacketsRatio = [0, 295, 1470, 2180]
for i in range(len(droppedPacketsRatio)):
	droppedPacketsRatio[i] = (droppedPacketsRatio[i]/4000.0) * 100 
outputObj.plotDroppedPacketsRatio(droppedPacketsRatio)

#[0.00104203970554, 0.00103812749123, 0.00103261651018]
RTTDelay = [0.00103261651018, 0.00103812749123, 0.00104203970554]
for i in range(len(RTTDelay)):
	RTTDelay[i] = RTTDelay[i] * 1000
outputObj.plotRTTBufDelay(RTTDelay) 
'''
'''
RTTDelayLatency = [0.00101266523881, 0.00102189774183, 0.00288275806849]
for i in range(len(RTTDelayLatency)):
	RTTDelayLatency[i] = RTTDelayLatency[i] * 1000
outputObj.plotRTTBufDelayIntLatency(RTTDelayLatency) 

RTTDelayMPISize = [0.00102291498892, 0.00103537124316, 0.00103752317887]
for i in range(len(RTTDelayMPISize)):
	RTTDelayMPISize[i] = RTTDelayMPISize[i] * 1000
outputObj.plotRTTDelayMPISize(RTTDelayMPISize) 

RTTBandwidth = [0.00105961473342, 0.00103038102123, 0.00102189360391]
for i in range(len(RTTBandwidth)):
	RTTBandwidth[i] = RTTBandwidth[i] * 1000
outputObj.plotRTTBandwidth(RTTBandwidth)
'''
