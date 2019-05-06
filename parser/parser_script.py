#!/usr/bin/python
import sys
from xmlformat import formatXML
from database import service_worker, network_worker


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
            formatXML.iterate_dir(
                input("Enter full path to XML files. Files with _new suffix will be overwrited: "))
        elif option == "2":
            service_worker.create_list_service(input("Enter full path to formated XML files: "))
        elif option == "3":
            network_worker.create_list_network_object(input("Enter full path to formated XML files: "))
        elif option == "exit":
            sys.exit(1)
        else:
            print("Invlid option")


def main():
    run_parser()


if __name__ == '__main__':
    main()
