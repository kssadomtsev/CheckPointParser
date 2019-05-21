#!/usr/bin/python
import sys, os
from xmlformat import formatXML
from database import service_worker, network_worker, policy_worker
from importer import import_servces, import_network_objects, import_rules
import logging
import config

logging.getLogger('').handlers = []
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                    filename="..\\logs\\parser_log.log",
                    level=logging.DEBUG, filemode='w')


def run_parser():
    logging.info("Programm was started")
    print()
    print("1. Format XML file ")
    print("2. Create services database from XML file ")
    print("3. Create network database from XML file ")
    print("4. Create security policy database from XML file ")
    print("5. Import related services and service groups to new SMS ")
    print("6. Import related network objects and groups to new SMS ")
    print("7. Import related rules to new SMS ")
    print("Exit")
    print()
    while True:
        option = input("Please enter needed option as number without dot or exit:").lower()
        if option == "1":
            logging.info("Option 1 was selected")
            formatXML.iterate_dir(
                input("Enter full path to XML files. Files with _new suffix will be overwrited: "))
        elif option == "2":
            logging.info("Option 2 was selected")
            service_worker.create_list_service(input("Enter full path to formated XML files: "))
        elif option == "3":
            logging.info("Option 3 was selected")
            network_worker.create_list_network_object(input("Enter full path to formated XML files: "))
        elif option == "4":
            logging.info("Option 4 was selected")
            policy_worker.create_list_security_policy(
                input("Enter full path (include file itself) to formated security policy file: "))
        elif option == "5":
            logging.info("Option 5 was selected")
            config.api_server = input("Enter MDS IP: ")
            config.username = input("Enter username: ")
            config.password = input("Enter password: ")
            config.domain = input("Enter domain name: ")
            import_servces.create_services()
        elif option == "6":
            logging.info("Option 6 was selected")
            config.api_server = input("Enter MDS IP: ")
            config.username = input("Enter username: ")
            config.password = input("Enter password: ")
            config.domain = input("Enter domain name: ")
            import_network_objects.create_network_objects()
        elif option == "7":
            logging.info("Option 7 was selected")
            config.api_server = input("Enter MDS IP: ")
            config.username = input("Enter username: ")
            config.password = input("Enter password: ")
            config.domain = input("Enter domain name: ")
            config.package = input("Enter package name: ")
            config.layer = input("Enter layer name: ")
            import_rules.create_rules()
        elif option == "exit":
            logging.info("Exit")
            sys.exit(1)
        else:
            logging.info("Invalid option was selected")
            print("Invalid option was selected")


def main():
    run_parser()


if __name__ == '__main__':
    main()
