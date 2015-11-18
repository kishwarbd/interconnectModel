"""
@package    packaet
@author     Mohammad Abu Obaida
This package defines the Packet class and supported methods.
"""
class Packet:
    """
    A simple request/acknowledge/busy packet (message) object
    """
    def __init__(self, d):
        self.dict = d

    def __iter__(self):
        return self.dict.itervalues()

    def __getitem__(self, key):
        return self.dict[key]

    def __setitem__(self, key, value):
        self.dict[key] = value

    def __str__(self):
        return "Packet<" + str(self.dict) + ">"

    def __rep__(self):
        return "Packet<" + str(self.dict) + ">"

