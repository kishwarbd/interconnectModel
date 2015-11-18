""""
@package ringBuffer
@author Mohammad Abu Obaida
"""

from collections import deque

class RingBuffer:
    """   
    RingBuffer class implements a buffer that allows push, pop and other basic queue operations
    """
    #This implements an efficient fixed size circular-FIFO
    def __init__(self, maxBuffSz, pktSz):
        """
        Constructor of RingBuffer class.
        """
        self.maxBuffSz = maxBuffSz #buffer size in bytes
        self.Q = deque([], maxBuffSz)
        assert pktSz >0, "Packet size to be a positive integer"
        self.pktSize = pktSz #say in bytes

    def size(self):
        """
        @retval     length of the stored items.
        """
        return len(self.Q)

    def space(self):
        """
        @retval     Returns the difference of the Max Size of the queue and the length of the stored entries.
        """
        return self.maxBuffSz - len(self.Q)*self.pktSize

    def push(self, elem):
        """
        Pushes an element to the top of the queue
        """

        if len(self.Q) < self.maxBuffSz: #need to check the space before push
            self.Q.appendleft(elem)
            return True
        else:
            #Returns false when buffer is full
            return False

    def pop(self):
        """
        @retval     Returns the topmost item from the queue. 
        """
        return self.Q.popleft()

    def clear(self):
        """
        Clears the queue
        """
        self.Q.clear()

    def isEmpty(self):
        """
        @retval     Returns true if the queue is empty
        """
        if self.space() == self.maxBuffSz:
            return True
        else:
            return False
