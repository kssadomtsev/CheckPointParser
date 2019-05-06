#!/usr/bin/python
import sys
from xmlformat import formatXML
from database import service_worker, network_worker
import logging

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='../logs/parser_log.log',
                    level=logging.DEBUG)


def run_parser():
    print()
    print("1. Format XML file ")
    print("2. Create services database from XML file ")
    print("3. Create network database from XML file ")
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
            logging.info("Option 2 was selected")
            network_worker.create_list_network_object(input("Enter full path to formated XML files: "))
        elif option == "exit":
            sys.exit(1)
        else:
            logging.info("Invalid option was selected")
            print("Invlid option")


def main():
    run_parser()


if __name__ == '__main__':
    main()
