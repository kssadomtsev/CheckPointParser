#!/usr/bin/python
import ipaddress

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

    def is_in_nets_list(self, nets):
        print(self.name)
        ip_address_v4 = ipaddress.IPv4Address(self.ip_address)
        print(ip_address_v4)
        for net in nets:
            if ip_address_v4 in net:
                return 1
        return 0


# Define class "network"
class network:
    def __init__(self, name, comments, color, ip_address):
        self.name = name
        self.comments = comments
        self.color = color
        self.ip_address = ip_address

    def is_in_nets_list(self, nets):
        print(self.name)
        ip_address_v4 = ipaddress.IPv4Network(self.ip_address)
        print(ip_address_v4)
        for net in nets:
            if ip_address_v4.overlaps(net):
                return 1
        return 0


# Define class "address_range"
class address_range:
    def __init__(self, name, comments, color, ipaddr_first, ipaddr_last):
        self.name = name
        self.comments = comments
        self.color = color
        self.ipaddr_first = ipaddr_first
        self.ipaddr_last = ipaddr_last

    def is_in_nets_list(self, nets):
        ip_address_v4_first = ipaddress.IPv4Address(self.ipaddr_first)
        ip_address_v4_last = ipaddress.IPv4Address(self.ipaddr_last)
        for net in nets:
            if ip_address_v4_first <= net.network_address <= ip_address_v4_last:
                return 1
        return 0


# Define class "network_object_group"
class network_object_group:
    def __init__(self, name, comments, color, members):
        self.name = name
        self.comments = comments
        self.color = color
        self.members = members

    def is_in_nets_list(self, nets):
        for member in self.members:
            if not member.name.startswith("F_"):
                if member.is_in_nets_list(nets) == 1:
                    return 1
        return 0




# Define class "rule"
class security_rule:
    def __init__(self, number, name, src, src_neg, dst, dst_neg, services, action, comments):
        self.number = number
        self.name = name
        self.src = src
        self.src_neg = src_neg
        self.dst = dst
        self.dst_neg = dst_neg
        self.services = services
        self.action = action
        self.comments = comments
