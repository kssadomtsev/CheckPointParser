from database import db_worker
from model import network_objects
from importer import api_worker, output
import logging
import ipaddress

logging.getLogger('').handlers = []
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                    filename="..\\logs\\parser_log.log",
                    level=logging.DEBUG, filemode='w')
list_network_objects = []
success_added_obj = []
error_added_obj = {}
n = 0
groups_list = {}

obj_should_be_fake = (
    "cluster_member", "connectra", "gateway_ckp", "gateway_plain", "sofaware_gateway", "gateway_cluster",
    "host_ckp", "group_with_exception")


def response_analyze(response, obj_name):
    if response is None:
        success_added_obj.append(obj_name)
    else:
        error_added_obj[obj_name] = response


def get_modified_members(members, cur):
    result = []
    for member in members:
        cur.execute("SELECT type FROM network_object_index WHERE name =(?)", (member,))
        rows = cur.fetchone()
        row_str_ = str(rows).strip("()',")
        logging.info(row_str_)
        if row_str_ == "host_plain":
            result.append(db_worker.del_g_host(member))
        elif row_str_ == "network":
            result.append(db_worker.del_g_net(member))
        elif row_str_ == "address_range":
            result.append(member)
        elif row_str_ in obj_should_be_fake:
            result.append("F_" + member)
        elif row_str_ == "network_object_group":
            result.append(db_worker.del_g_group(member))
    return result


def get_members(group, cur):
    cur.execute("SELECT members FROM network_object_group WHERE name='%s'" % (group,))
    rows = cur.fetchone()
    row_str = str(rows).strip("()',")
    return row_str.split(",")


def create_host_plain(host_plain, cur):
    cur.execute("SELECT * FROM host_plain WHERE name='%s'" % (host_plain,))
    rows = cur.fetchone()
    host_plain_obj = network_objects.host_plain(db_worker.del_g_host(rows[0]), rows[1], rows[2].lower(), rows[3])
    logging.info("Trying to add to SMS host_plain " + host_plain_obj.name)
    response = api_worker.create_object("add-host", {"name": host_plain_obj.name, "comments": host_plain_obj.comments,
                                                     "ip-address": host_plain_obj.ip_address,
                                                     "color": api_worker.choose_color(host_plain_obj),
                                                     "ignore-warnings": "true"})
    response_analyze(response, host_plain_obj.name)


def create_network(network, cur):
    cur.execute("SELECT * FROM network WHERE name='%s'" % (network,))
    rows = cur.fetchone()
    network_obj = network_objects.network(db_worker.del_g_net(rows[0]), rows[1], rows[2].lower(), rows[3])
    logging.info("Trying to add to SMS network " + network_obj.name + " " + network_obj.ip_address)
    ip = ipaddress.ip_network(network_obj.ip_address)
    response = api_worker.create_object("add-network", {"name": network_obj.name, "comments": network_obj.comments,
                                                        "subnet": str(ip.network_address),
                                                        "mask-length": str(ip.prefixlen),
                                                        "color": api_worker.choose_color(network_obj),
                                                        "ignore-warnings": "true"})
    response_analyze(response, network_obj.name)


def create_address_range(address_range, cur):
    cur.execute("SELECT * FROM address_range WHERE name='%s'" % (address_range,))
    rows = cur.fetchone()
    address_range_obj = network_objects.address_range(rows[0], rows[1], rows[2].lower(), rows[3], rows[4])
    logging.info("Trying to add to SMS address_range " + address_range_obj.name)
    response = api_worker.create_object("add-address-range",
                                        {"name": address_range_obj.name, "comments": address_range_obj.comments,
                                         "ip-address-first": address_range_obj.ipaddr_first,
                                         "ip-address-last": address_range_obj.ipaddr_last,
                                         "color": api_worker.choose_color(address_range_obj),
                                         "ignore-warnings": "true"})
    response_analyze(response, address_range_obj.name)


def create_fake_object(host_plain):
    logging.info("Trying to add to SMS fake object " + host_plain)
    response = api_worker.create_object("add-host",
                                        {"name": host_plain, "ip-address": "1.1.1.1", "color": "green",
                                         "ignore-warnings": "true"})
    response_analyze(response, host_plain)


def create_network_object_group(network_object_group, cur):
    global n
    for s_ in get_members(network_object_group, cur):
        logging.info(s_)
        cur.execute("SELECT type FROM network_object_index WHERE name =(?)", (s_,))
        rows = cur.fetchone()
        #       logging.info(rows_)
        row_str_ = str(rows).strip("()',")
        logging.info(row_str_)
        print(s_ + " " + row_str_)
        if row_str_ == "host_plain" and db_worker.del_g_host(s_) not in list_network_objects:
            s2_ = db_worker.del_g_host(s_)
            list_network_objects.append(s2_)
            logging.info("Creating host_plain " + s2_)
            create_host_plain(s_, cur)
        elif row_str_ == "network" and db_worker.del_g_net(s_) not in list_network_objects:
            s2_ = db_worker.del_g_net(s_)
            list_network_objects.append(s2_)
            logging.info("Creating network " + s2_)
            create_network(s_, cur)
        elif row_str_ == "address_range" and s_ not in list_network_objects:
            list_network_objects.append(s_)
            logging.info("Creating address_range " + s_)
            create_address_range(s_, cur)
        elif row_str_ in obj_should_be_fake and "F_" + s_ not in list_network_objects:
            list_network_objects.append("F_" + s_)
            logging.info("Creating " + row_str_ + " " + "F_" + s_)
            create_fake_object("F_" + s_)
        elif row_str_ == "network_object_group" and db_worker.del_g_group(s_) not in list_network_objects:
            s2_ = db_worker.del_g_group(s_)
            list_network_objects.append(s2_)
            logging.info("Creating network_object_group " + s2_)
            create_network_object_group(s_, cur)
        n = n + 1
        if n == 100:
            api_worker.publish_changes(False)
            api_worker.login(False)
            n = 0
    cur.execute("SELECT * FROM network_object_group WHERE name='%s'" % (network_object_group,))
    rows = cur.fetchone()
    print(rows)
    network_object_group_obj = network_objects.network_object_group(db_worker.del_g_group(rows[0]), rows[1],
                                                                    rows[2].lower(), rows[3])
    logging.info("Trying to add to SMS network_object_group " + network_object_group_obj.name)
    print("Trying to add to SMS network_object_group " + network_object_group_obj.name)
    response = api_worker.create_object("add-group",
                                        {"name": network_object_group_obj.name,
                                         "comments": network_object_group_obj.comments,
                                         "color": api_worker.choose_color(network_object_group_obj),
                                         "members": get_modified_members(network_object_group_obj.members.split(","),
                                                                         cur),
                                         "ignore-warnings": "true"})
    response_analyze(response, network_object_group_obj.name)
    groups_list[network_object_group_obj.name] = len(network_object_group_obj.members.split(","))


def create_network_objects():
    global n
    conn = db_worker.create_connection()
    api_worker.login(False)
    if conn is not None:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT src FROM security_policy")
        rows1 = cur.fetchall()
        cur.execute("SELECT DISTINCT dst FROM security_policy")
        rows2 = cur.fetchall()
        rows = rows1 + rows2
        s = set()
        list = []
        for row in rows:
            row_str = str(row).strip("()',")
            list.extend(row_str.split(","))
        logging.info("Total number of network objects in rules " + str(len(list)))
        s.update(list)
        logging.info("Total number of unique network objects  in rules " + str(len(s)))
        logging.info("Those network objects  are " + str(s))
        for s_ in s:
            cur.execute("SELECT type FROM network_object_index WHERE name =(?)", (s_,))
            rows = cur.fetchone()
            if rows != None:
                row_str_ = str(rows).strip("()',")
                print(s_ + " " + row_str_)
                if row_str_ == "host_plain" and db_worker.del_g_host(s_) not in list_network_objects:
                    s2_ = db_worker.del_g_host(s_)
                    list_network_objects.append(s2_)
                    logging.info("Creating host_plain " + s2_)
                    create_host_plain(s_, cur)
                elif row_str_ == "network" and db_worker.del_g_net(s_) not in list_network_objects:
                    s2_ = db_worker.del_g_net(s_)
                    list_network_objects.append(s2_)
                    logging.info("Creating network " + s2_)
                    create_network(s_, cur)
                elif row_str_ == "address_range" and s_ not in list_network_objects:
                    list_network_objects.append(s_)
                    logging.info("Creating address_range " + s_)
                    create_address_range(s_, cur)
                elif row_str_ in obj_should_be_fake and "F_" + s_ not in list_network_objects:
                    list_network_objects.append("F_" + s_)
                    logging.info("Creating " + row_str_ + " " + "F_" + s_)
                    create_fake_object("F_" + s_)
                elif row_str_ == "network_object_group" and db_worker.del_g_group(s_) not in list_network_objects:
                    s2_ = db_worker.del_g_group(s_)
                    list_network_objects.append(s2_)
                    logging.info("Creating network_object_group " + s2_)
                    create_network_object_group(s_, cur)
                n = n + 1
                if n == 100:
                    api_worker.publish_changes(False)
                    api_worker.login(False)
                    n = 0
        api_worker.publish_changes(False)
        logging.info("Total number of analazed network_object " + str(len(list_network_objects)))
        # logging.info("Those network_object are " + str(list_network_objects))
        logging.info("Result of adding new network objects to new SMS:")
        logging.info("Without errors was added following count of network objects: " + str(len(success_added_obj)))
        logging.info("With errors wasn't added following count of network objects: " + str(len(error_added_obj)))
        output.print_to_xlsx(error_added_obj, "network_objects_error.xlsx")
        output.print_to_xlsx(groups_list, "groups_r80_local.xlsx")

    else:
        print("Error! cannot create the database connection.")
        logging.warning("Error! cannot create the database connection.")
