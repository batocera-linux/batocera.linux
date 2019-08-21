#!/usr/bin/env python

class Command:
    def __init__(self, array, env=dict()):
        self.array = array
        self.env = env
        
    def __str__(self):
        str = list()

        for varName, varValue in self.env.items():
            str.append("%s=%s" % (varName, varValue))
            
        for value in self.array:
            str.append(value)

        return " ".join(str)
