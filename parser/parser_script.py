#!/usr/bin/python
import sys
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
    logging.info("Program was started")
    print()
    print("1. Format XML file and create internal database for store objects ")
    print("2. Apply subnet filter and create new database ")
    print("3. Import related services and service groups, network objects and groups to new SMS ")
    print("4. Import related rules to new SMS ")
    print("Exit")
    print()
    while True:
        option = input("Please enter needed option as number without dot or exit:").lower()
        if option == "1":
            logging.info("Option 1 was selected")
            #formatXML.iterate_dir(config.xml_dir)
            service_worker.create_list_service(config.xml_dir)
            network_worker.create_list_network_object(config.xml_dir)
            policy_worker.create_list_security_policy(config.xml_policy_file)
        elif option == "2":
            logging.info("Option 1 was selected")
            print("Under construction...")
        elif option == "3":
            logging.info("Option 3 was selected")
            import_servces.create_services()
            import_network_objects.create_network_objects()
        elif option == "4":
            logging.info("Option 4 was selected")
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
