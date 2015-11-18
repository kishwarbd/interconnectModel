class topologyGenerator(object):
    def __init__(self, *args):
        assert (len(args)>=1), "Assertion Error: "
        self.topology = args[0]
	self.outputFile = args[1]
        if(self.topology == "torus_3D"):
            assert (len(args)>=5), "Assertion Error: Torus dimension"
            self.torus_x = args[2]
            self.torus_y = args[3]
            self.torus_z = args[4]
            self.total_torus_nodes = self.torus_x * self.torus_y * self.torus_z
            #print "Opening the file..."
            target = open(self.outputFile, 'w')
            #print "Truncating the file.  Goodbye!"
            target.truncate()
            for i in xrange (self.total_torus_nodes):
                connected_to = []
                local_nodes = []    #nodes that are in the same physical blade and/or forms a torus node
                #Adding nodes- a torus nodes contains two CieloNode
                #One torus node contains a gemini router and two compute nodes(can be in same physical blade)
                # For now im considering Total torus node = total compute node, which may not be the case.
                # We have to consider service nodes as well
                node1_nid = i * 2
                node2_nid = i * 2 + 1
                local_nodes.append(node1_nid)
                local_nodes.append(node2_nid)
                ruid = i #ruid is the router id that a node is connected to
                #We will find the other end of the links here, i.e. another router or torus node
                connected_to = self.find_neighboring_router (i)
                #add router_base_addr to all of the connected to routers
                ruid = i
                        
                #print(str(ruid) + " " + str(len(local_nodes)) + " " +  ' '.join(str(x) for x in local_nodes) + " " + ' '.join(str(x) for x in connected_to))
                target.write(str(ruid) +  " " + str(len(local_nodes)) + " " +  ' '.join(str(x) for x in local_nodes) + " " + ' '.join(str(x) for x in connected_to))

                target.write("\n")


    def find_neighboring_router (self, *args):
        """
        Function that finds id of all the directly connected routers with the supplied router (router_id)
        @param router_id Router unique ID from the perspective of a torus interconnect 
        @retval list of router id's that is connected
        """
        #We will find the other end of the links here, i.e. another router or torus node

        if(self.topology == "torus_3D"):
            router_id = args[0]
            connected_to = []
            torus_xyz = self.find_torus_xyz_from_uid(router_id)
            x_plus = (torus_xyz[0] + 1) % self.torus_x
            y_plus = (torus_xyz[1] + 1) % self.torus_y
            z_plus = (torus_xyz[2] + 1) % self.torus_z
            x_minus = (torus_xyz[0] - 1) % self.torus_x
            y_minus = (torus_xyz[1] - 1) % self.torus_x
            z_minus = (torus_xyz[2] - 1) % self.torus_x
            """ 
            ROUTING: We are making one routing decision here.
                     A torus node (GeminiRouter) is connected to 6 other routers.
                     We create the array based on the direction order routing.
                     i.e. if +X is the first rule to follow then we append it at connected to[0]. 
                     Higher index means lower priority
            """
            connected_to.append(self.find_torus_uid_by_xyz( x_plus, torus_xyz[1], torus_xyz[2] )) #link_x_plus same y,z
            connected_to.append(self.find_torus_uid_by_xyz( torus_xyz[0], torus_xyz[1], z_plus )) #link_z_plus same x,y
            connected_to.append(self.find_torus_uid_by_xyz( torus_xyz[0], y_plus, torus_xyz[2] )) #link_y_plus same x,z
            connected_to.append(self.find_torus_uid_by_xyz( x_minus, torus_xyz[1], torus_xyz[2] )) #link_x_minus same y,z
            connected_to.append(self.find_torus_uid_by_xyz( torus_xyz[0], torus_xyz[1], z_minus )) #link_z_minus same x,y
            connected_to.append(self.find_torus_uid_by_xyz( torus_xyz[0], y_minus, torus_xyz[2] )) #link_y_minus same x,z
            
            '''
            print "The router id: ", router_id
            print "The connected routers are: "
            for i in range(len(connected_to)):
                print " ", connected_to[i]
            print "\n"
            '''
            return (connected_to)


    def find_torus_uid_by_xyz (self, x, y, z):                       #Finding unique id of a torus node.                                                
        return (z * self.torus_x * self.torus_y + y*self.torus_x + x)
        
        
    def find_torus_xyz_from_uid (self, tuid):    
        # assuming bottom left front node is tuid 0, and right rear up point is max tuid
        # x increses from left to right, y increases from bottom to up
        # z increases from front to rear. tuid has to be an ineger
        depth = int ( tuid / (self.torus_x * self.torus_y) )   #z
        width = int ( (tuid % (self.torus_x * self.torus_y)) / self.torus_x ) #y
        length = int ( (tuid % (self.torus_x * self.torus_y)) % self.torus_x ) #x
        #we dont need to use math.floor since we need the floor every time
        return (length, width, depth)

