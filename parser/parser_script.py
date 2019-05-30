#!/usr/bin/python
import sys, os
from xmlformat import formatXML
from database import service_worker, network_worker, policy_worker
from importer import import_servces, import_network_objects, import_rules, filter_policy_worker
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
    print("2. Clear database ")
    print("3. Apply subnet filter and create new database for VS migration(custom) ")
    print("4. Apply subnet filter and create new database for OUT gateway ")
    print("5. Import related services and service groups, network objects and groups to new SMS ")
    print("6. Import related rules to new SMS ")
    print("Exit")
    print()
    while True:
        option = input("Please enter needed option as number without dot or exit:").lower()
        if option == "1":
            logging.info("Option 1 was selected")
            formatXML.iterate_dir(config.xml_dir)
            service_worker.create_list_service(config.xml_dir)
            network_worker.create_list_network_object(config.xml_dir)
            policy_worker.create_list_security_policy(config.xml_policy_file)
        elif option == "2":
            logging.info("Option 2 was selected")
            logging.info("Try to delete database...")
            if os.path.isfile("..\\data\\pythonsqlite.db"):
                os.remove("..\\data\\pythonsqlite.db")
                logging.info("Database was deleteted")
            else:
                logging.info("Error: %s file not found" % "..\\data\\pythonsqlite.db")
        elif option == "3":
            logging.info("Option 3 was selected")
            filter_policy_worker.filter_rules("1")
        elif option == "4":
            logging.info("Option 4 was selected")
            filter_policy_worker.filter_rules("0")
        elif option == "5":
            logging.info("Option 5 was selected")
            import_servces.create_services()
            import_network_objects.create_network_objects()
        elif option == "6":
            logging.info("Option 6 was selected")
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
