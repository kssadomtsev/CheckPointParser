from __future__ import print_function

import json
import sys, os
import logging

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='../logs/parser_log.log',
                    level=logging.DEBUG)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cpapi import APIClient, APIClientArgs


def choose_color(object):
    colors = (
        "aquamarine", "black", "blue", "crete blue", "burlywood", "cyan", "dark green", "khaki", "orchid",
        "dark orange",
        "dark sea green", "pink",
        "turquoise", "dark blue", "firebrick", "brown", "forest green", "gold", "dark gold", "gray", "dark gray",
        "light green", "lemon chiffon",
        "coral", "sea green", "sky blue", "magenta", "purple", "slate blue", "violet red", "navy blue", "olive",
        "orange",
        "red", "sienna", "yellow")
    if object.color in colors:
        return object.color
    else:
        return "black"


# Get all defined tcp services
def get_tcp_services(client):
    show_tcp_services = client.api_query("show-services-tcp", "standard")
    tcp_services_ports = []
    if show_tcp_services.success is False:
        print("Failed to get the list of all TCP service: {}".format(show_tcp_services.error_message))
        exit(1)
    for tcp_service in show_tcp_services.data:
        tcp_services_ports.append(tcp_service.get("port"))
        print(tcp_service.get("name") + " " + tcp_service.get("port"))
    return tcp_services_ports


def create_object(command, parametrs):
    #    api_server = "192.168.248.103"
    #   username = "admin"
    #   password = "Passw0rd!"
    api_server = "194.85.142.18"
    username = "sadomtsev"
    password = "ckjegjr228"
    domain = "DCE-RPC-test"
    client_args = APIClientArgs(server=api_server)
    with APIClient(client_args) as client:
        client.debug_file = "api_calls.json"
        if client.check_fingerprint() is False:
            print("Could not get the server's fingerprint - Check connectivity with the server.")
            logging.warning("Could not get the server's fingerprint - Check connectivity with the server.")
            sys.exit(1)
        login_res = client.login(username, password, "False", domain)
        if login_res.success is False:
            print("Login failed: {}".format(login_res.error_message))
            logging.warning("Login failed: {}".format(login_res.error_message))
            sys.exit(1)
        add_serv_response = client.api_call(command, parametrs)
        #        print(add_serv_response)
        logging.info(add_serv_response)
        #        print(add_serv_response.data)
        print(add_serv_response.data.get("code"))
        logging.info("Response is :")
        logging.info(add_serv_response.data.get("code"))
        if add_serv_response is False:
            print(format(add_serv_response.error_message))
            logging.warning(format(add_serv_response.error_message))
            sys.exit(1)
        elif add_serv_response.data.get("code") != "err_validation_failed":
            publish_res = client.api_call("publish", {})
            if publish_res.success:
                print("The changes were published successfully.")
                logging.info("The changes were published successfully.")
            else:
                print("Failed to publish the changes.")
                logging.warning("Failed to publish the changes.")