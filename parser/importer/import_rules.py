from database import db_worker
from model import network_objects
from importer import api_worker
import logging

logging.getLogger('').handlers = []
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                    filename="..\\logs\\parser_log.log",
                    level=logging.DEBUG, filemode='w')
obj_should_be_fake = (
    "cluster_member", "connectra", "gateway_ckp", "gateway_plain", "sofaware_gateway", "gateway_cluster",
    "host_ckp", "group_with_exception")


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


def get_modified_service_members(members):
    result = []
    for member in members:
        result.append(db_worker.del_g(member))
    return result


def create_rules():
    conn = db_worker.create_connection()
    if conn is not None:
        cur = conn.cursor()
        cur.execute("SELECT * FROM security_policy")
        rows = cur.fetchall()
        for row in rows:
            print(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
            if row[1] is not None:
                rule_name = row[1].strip()
            else:
                rule_name = ""
            if row[3] == "Any":
                src = "Any"
            else:
                src = get_modified_members(row[3].split(","), cur)
            if row[4] == "Any":
                dst = "Any"
            else:
                dst = get_modified_members(row[4].split(","), cur)
            if row[5] == "Any":
                srv = "Any"
            else:
                srv = get_modified_service_members(row[5].split(","))
            rule = network_objects.security_rule(row[0], rule_name, src, dst, srv, row[6].lower(), row[2])
            print(rule.number, rule.name, rule.src, rule.dst, rule.services, rule.action, rule.comments)
            api_worker.create_new_rule(rule)
    else:
        print("Error! cannot create the database connection.")
        logging.warning("Error! cannot create the database connection.")
