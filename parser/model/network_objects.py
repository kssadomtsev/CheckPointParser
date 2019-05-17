#!/usr/bin/python
import sys


# Define class "service"
class service:
    def __init__(self, name, comments, color, type, port):
        self.name = name
        self.comments = comments
        self.color = color
        self.type = type
        self.port = port

    def print_service(self):
        print(self.name, self.comments, self.color, self.type, self.port)


# Define class "service group"
class service_group:
    def __init__(self, name, comments, color, members):
        self.name = name
        self.comments = comments
        self.color = color
        self.members = members


# Define class "host plain"
class host_plain:
    def __init__(self, name, comments, color, ip_address):
        self.name = name
        self.comments = comments
        self.color = color
        self.ip_address = ip_address


# Define class "network"
class network:
    def __init__(self, name, comments, color, ip_address):
        self.name = name
        self.comments = comments
        self.color = color
        self.ip_address = ip_address


# Define class "network"
class address_range:
    def __init__(self, name, comments, color, ipaddr_first, ipaddr_last):
        self.name = name
        self.comments = comments
        self.color = color
        self.ipaddr_first = ipaddr_first
        self.ipaddr_last = ipaddr_last
