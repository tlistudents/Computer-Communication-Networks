# This is one of the project for ECE463 at Purdue University
# It's for academic and educational purpose only
# Please read only, do not share, post, or copy this code
# Especially if you are a student who is taking this course  

# Student name: Tingzhang Li

import _thread
import sys
import queue
import time
import threading


class Link:
    """Link class represents link between two switches/clients
       handles sending and receiving packets using
       threadsafe queues"""

    # Access these constants from other files
    # as Link.Active or Link.INACTIVE
    ACTIVE = 1 # link is in the spanning tree
    INACTIVE = 2 # link is not in spanning tree

    def __init__(self, e1, e2, l, latency):
        """Create queues. e1 & e2 are addresses of the 2 endpoints of
           the link. l is the latency (or cost)"""
        self.q12 = queue.Queue()
        self.q21 = queue.Queue()
        self.l = l*latency
        self.latencyMultiplier = latency
        self.e1 = e1
        self.e2 = e2
        self.status = Link.ACTIVE


    def get_e2(self, e1):
        """Returns the other endpoint of the link"""
        if self.e1 == e1:
            return self.e2
        else:
            return self.e1


    def get_cost(self):
        """Returns the cost (latency) of the link"""
        return self.l/self.latencyMultiplier


    def send_helper(self, packet, src):
        """Run in a separate thread and sends packet on
           link FROM src after waiting for the appropriate latency"""
        if src == self.e1:
            packet.addToRoute(self.e2)
            time.sleep(self.l/float(1000))
            self.q12.put(packet)
        elif src == self.e2:
            packet.addToRoute(self.e1)
            time.sleep(self.l/float(1000))
            self.q21.put(packet)
        sys.stdout.flush()


    def send(self, packet, src):
        """Sends packet on link FROM src. Checks that packet content is
           a string and starts a new thread to send it.
           (src must be equal to self.e1 or self.e2)"""
        if packet.content:
            assert isinstance((packet.content), str), "Packet content must be a string"
        p = packet.copy()
        _thread.start_new_thread(self.send_helper, (p, src))


    def recv(self, dst, timeout=None):
        """Checks whether a packet is ready to be received by dst on this link.
           dst must be equal to self.e1 or self.e2.  If packet is ready, returns
           the packet, else returns None."""
        if dst == self.e1:
            try:
                packet = self.q21.get_nowait()
                return packet
            except queue.Empty:
                return None
        elif dst == self.e2:
            try:
                packet = self.q12.get_nowait()
                return packet
            except queue.Empty:
                return None


    def changeLatency(self, src, c):
        """Update the latency of sending on the link from src"""
        if src == self.e1:
            self.l = c*self.latencyMultiplier
        elif src == self.e2:
            self.l = c*self.latencyMultiplier
