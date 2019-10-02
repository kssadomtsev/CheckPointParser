from database import db_worker
from model import network_objects
from importer import api_worker, output
import logging

logging.getLogger('').handlers = []
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                    filename="..\\logs\\parser_log.log",
                    level=logging.DEBUG, filemode='w')

list_services = []
success_added_services = []
error_added_services = {}

def get_members(group, cur):
    cur.execute("SELECT members FROM service_groups WHERE name='%s'" % (group,))
    rows = cur.fetchone()
    row_str = str(rows).strip("()',")
    return row_str.split(",")


def create_service_group(group, cur):
    n = 0
    for row in get_members(group, cur):
        logging.info(row)
        cur.execute("SELECT type FROM service_index WHERE name =(?)", (row,))
        rows_ = cur.fetchone()
        #       logging.info(rows_)
        row_str = str(rows_).strip("()',")
        logging.info(row_str)
        if row_str == "services" and row not in list_services:
            list_services.append(row)
            logging.info("Creating service " + row)
            create_service(row, cur)
        elif row_str == "service_groups" and row not in list_services:
            list_services.append(row)
            create_service_group(row, cur)
        n = n + 1
        if n == 100:
            api_worker.publish_changes(True)
            api_worker.login(True)
            n = 0
    list_services.append(group)
    logging.info("Creating service group " + group)
    cur.execute("SELECT * FROM service_groups WHERE name='%s'" % (group,))
    rows = cur.fetchone()
    print(rows)
    service_group_obj = network_objects.service_group(rows[0], rows[1], rows[2].lower(), rows[3])
    logging.info("Trying to add to SMS service group " + service_group_obj.name)
    print("Trying to add to SMS service group " + service_group_obj.name)
    response = api_worker.create_object("add-service-group",
                                        {"name": service_group_obj.name, "comments": service_group_obj.comments,
                                         "color": api_worker.choose_color(service_group_obj),
                                         "members": service_group_obj.members.split(","),
                                         "ignore-warnings": "true"})
    if response is None:
        success_added_services.append(service_group_obj.name)
    else:
        error_added_services[service_group_obj.name] = response


def create_service(service, cur):
    cur.execute("SELECT * FROM services WHERE name='%s'" % (service,))
    rows = cur.fetchone()
    service_obj = network_objects.service(rows[0], rows[1], rows[2], rows[3].lower(), rows[4])
    if service_obj.type == "tcp":
        #        print("TCP servcie!!")
        service_obj.print_service()
        logging.info("Trying to add to SMS service " + service_obj.name)
        response = api_worker.create_object("add-service-tcp",
                                            {"name": service_obj.name, "comments": service_obj.comments,
                                             "port": service_obj.port,
                                             "color": api_worker.choose_color(service_obj),
                                             "ignore-warnings": "true"})
        if response is None:
            success_added_services.append(service_obj.name)
        else:
            error_added_services[service_obj.name] = response
    elif service_obj.type == "udp":
        service_obj.print_service()
        logging.info("Trying to add to SMS service " + service_obj.name)
        response = api_worker.create_object("add-service-udp",
                                            {"name": service_obj.name, "comments": service_obj.comments,
                                             "port": service_obj.port,
                                             "color": api_worker.choose_color(service_obj),
                                             "ignore-warnings": "true"})
        if response is None:
            success_added_services.append(service_obj.name)
        else:
            error_added_services[service_obj.name] = response
    else:
        logging.info("Other service " + service_obj.name)
        service_obj.print_service()


def create_services():
    conn = db_worker.create_connection()
    api_worker.login(True)
    if conn is not None:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT services FROM global_policy")
        rows = cur.fetchall()
        s = set()
        list = []
        for row in rows:
            row_str = str(row).strip("()',")
            list.extend(row_str.split(","))
        logging.info("Total number of services in rules " + str(len(list)))
        s.update(list)
        logging.info("Total number of unique services in rules " + str(len(s)))
        logging.info("Those services are " + str(s))
        n = 0
        for s_ in s:
            cur.execute("SELECT type FROM service_index WHERE name =(?)", (s_,))
            rows = cur.fetchone()
            if rows is not None:
                row_str_ = str(rows).strip("()',")
                if row_str_ == "services" and s_ not in list_services:
                    list_services.append(s_)
                    logging.info("Creating service " + s_)
                    create_service(s_, cur)
                elif row_str_ == "service_groups" and s_ not in list_services:
                    logging.info("SERVICE GROUP " + s_)
                    create_service_group(s_, cur)
                #           if rows is None:
                #               api_worker.publish_changes()
                n = n + 1
                if n == 100:
                    api_worker.publish_changes(True)
                    api_worker.login(True)
                    n = 0
        api_worker.publish_changes(True)
        logging.info("Total number of analazed service " + str(len(list_services)))
        # logging.info("Those services are " + str(list_services))
        logging.info("Result of adding new services to new SMS:")
        logging.info("Without errors was added following count of services: " + str(len(success_added_services)))
        logging.info("With errors wasn't added following count of services: " + str(len(error_added_services)))
        output.print_to_xlsx(error_added_services, "service_error.xlsx")
    else:
        print("Error! cannot create the database connection.")
        logging.warning("Error! cannot create the database connection.")
