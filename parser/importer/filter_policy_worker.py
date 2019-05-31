import ipaddress
from database import db_worker
import logging
import config
from importer import import_rules, import_network_objects
from model import network_objects

logging.getLogger('').handlers = []
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                    filename="..\\logs\\parser_log.log",
                    level=logging.DEBUG, filemode='w')

nets = []

obj_should_be_fake = (
    "cluster_member", "connectra", "gateway_ckp", "gateway_plain", "sofaware_gateway", "gateway_cluster",
    "host_ckp", "group_with_exception")


def get_host_plain(host_plain, cur):
    cur.execute("SELECT * FROM host_plain WHERE name='%s'" % (host_plain,))
    rows = cur.fetchone()
    return network_objects.host_plain(rows[0], rows[1], rows[2].lower(), rows[3])


def get_fake_host(host_plain):
    return network_objects.host_plain("F_" + host_plain, "", "", "")


def get_network(network, cur):
    cur.execute("SELECT * FROM network WHERE name='%s'" % (network,))
    rows = cur.fetchone()
    return network_objects.network(rows[0], rows[1], rows[2].lower(), rows[3])


def get_address_range(address_range, cur):
    cur.execute("SELECT * FROM address_range WHERE name='%s'" % (address_range,))
    rows = cur.fetchone()
    return network_objects.address_range(rows[0], rows[1], rows[2].lower(), rows[3], rows[4])


def get_filter_nets(nets_list):
    for str in nets_list.splitlines():
        nets.append(ipaddress.IPv4Network(str.strip()))
    print(nets)


def get_network_object_group(network_object_group, cur):
    members = []
    for obj in import_network_objects.get_members(network_object_group, cur):
        cur.execute("SELECT type FROM network_object_index WHERE name =(?)", (obj,))
        rows = cur.fetchone()
        #       logging.info(rows_)
        row_type = str(rows).strip("()',")
        logging.info(row_type)
        # print(obj + " " + row_type)
        if row_type == "host_plain":
            members.append(get_host_plain(obj, cur))
        elif row_type == "network":
            members.append(get_network(obj, cur))
        elif row_type == "address_range":
            members.append(get_address_range(obj, cur))
        elif row_type in obj_should_be_fake:
            members.append(get_fake_host(obj))
        elif row_type == "network_object_group":
            members.append(get_network_object_group(obj, cur))
    cur.execute("SELECT * FROM network_object_group WHERE name='%s'" % (network_object_group,))
    rows = cur.fetchone()
    # print(rows)
    print(members)
    return network_objects.network_object_group(rows[0], rows[1],
                                                rows[2].lower(), members)


def get_field_as_obj_list(field, cur):
    result = []
    # print(field)
    for obj in field:
        cur.execute("SELECT type FROM network_object_index WHERE name =(?)", (obj,))
        row_type = str(cur.fetchone()).strip("()',")
        # print(row_type)
        if row_type == "host_plain":
            result.append(get_host_plain(obj, cur))
        elif row_type == "network":
            result.append(get_network(obj, cur))
        elif row_type == "address_range":
            result.append(get_address_range(obj, cur))
        elif row_type in obj_should_be_fake:
            result.append(get_fake_host(obj))
        elif row_type == "network_object_group":
            result.append(get_network_object_group(obj, cur))
    return result


def filter_rules(flag):
    count_new_rules = 0
    if flag == "1":
        get_filter_nets(config.filter_network)
    else:
        get_filter_nets(r"192.168.0.0/255.255.0.0,10.0.0.0/255.0.0.0,172.16.0.0/255.240.0.0")
    sql_create_security_policy_table = """ CREATE TABLE IF NOT EXISTS security_policy_filtered (
                                          Rule_Number text PRIMARY KEY,
                                          section text,
                                          name text,
                                          comments text,
                                          src text,
                                          src_neg text,
                                          dst text,
                                          dst_neg text,
                                          services text,
                                          action text                                         
                                      ); """
    sql_security_policy = ''' (Rule_Number,section,name,comments,src,src_neg,dst,dst_neg,services,action)
                  VALUES(?,?,?,?,?,?,?,?,?,?) '''
    conn = db_worker.create_connection()
    if conn is not None:
        db_worker.create_table(conn, sql_create_security_policy_table)
        cur = conn.cursor()
        cur.execute("SELECT * FROM security_policy")
        rows = cur.fetchall()
        for row in rows:
            print(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])
            # row[0] - Rule_Number
            # row[1] - section
            # row[2] - name
            # row[3] - comments
            # row[4] - src
            # row[5] - src_neg
            # row[6] - dst
            # row[7] - dst_neg
            # row[8] - services
            # row[9] - action
            if row[2] is not None:
                rule_name = row[2].strip()
            else:
                rule_name = ""
            if row[1] == "True":
                net_obj = (str(count_new_rules), "True", rule_name, "", "", "", "", "", "", "")
                db_worker.create_net_obj(conn, net_obj, 'security_policy_filtered', sql_security_policy)
                count_new_rules += 1
                logging.info(rule_name + " is a title, import without modification")
            else:
                logging.info("Start analyze rule number, name " + str(row[0]) + "," + rule_name)
                temp_src = []
                temp_dst = []
                src_fil = 0
                dst_fil = 0
                if row[4] == "Any":
                    temp_src.append("Any")
                    src_fil = 1
                else:
                    src = get_field_as_obj_list(row[4].split(","), cur)
                    # print(src)
                    for src_obj in src:
                        if src_obj.name.startswith("F_"):
                            temp_src.append(src_obj.name)
                            src_fil = 1
                        elif src_obj.is_in_nets_list(nets) == 1 and row[5] == "False":
                            temp_src.append(src_obj.name)
                            src_fil = 1
                        elif src_obj.is_in_nets_list(nets) == 0 and row[5] == "True":
                            logging.info("Inverting source status")
                            temp_src.append(src_obj.name)
                            src_fil = 1
                if row[6] == "Any":
                    temp_dst.append("Any")
                    dst_fil = 1
                else:
                    dst = get_field_as_obj_list(row[6].split(","), cur)
                    # print(src)
                    for dst_obj in dst:
                        if dst_obj.name.startswith("F_"):
                            temp_dst.append(dst_obj.name)
                            dst_fil = 1
                        elif dst_obj.is_in_nets_list(nets) == 1 and row[7] == "False":
                            temp_dst.append(dst_obj.name)
                            dst_fil = 1
                        elif dst_obj.is_in_nets_list(nets) == 0 and row[7] == "True":
                            logging.info("Inverting destination status")
                            temp_dst.append(dst_obj.name)
                            dst_fil = 1
                if dst_fil == 1 and src_fil == 1 and flag == "1":
                    logging.info("Rule with number, name " + str(
                        row[0]) + "," + rule_name + " has matched source and destination and should be fully copied")
                    rule = network_objects.security_rule(str(count_new_rules), row[2], row[4], row[5], row[6], row[7],
                                                         row[8], row[9], row[3])
                    print(str(count_new_rules), rule.name, rule.src, rule.src_neg, rule.dst, rule.dst_neg,
                          rule.services,
                          rule.action, rule.comments)
                    net_obj = (
                        str(count_new_rules), row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])
                    db_worker.create_net_obj(conn, net_obj, 'security_policy_filtered', sql_security_policy)
                    logging.info(net_obj)
                    count_new_rules += 1
                elif dst_fil == 0 and src_fil == 1:
                    logging.info("Rule with number, name " + str(
                        row[0]) + "," + rule_name + " has matched only source and should be particialy copied")
                    rule = network_objects.security_rule(str(count_new_rules), row[2], ",".join(temp_src), row[5],
                                                         row[6], row[7], row[8], row[9], row[3])
                    print(str(count_new_rules), rule.name, rule.src, rule.src_neg, rule.dst, rule.dst_neg,
                          rule.services,
                          rule.action, rule.comments)
                    net_obj = (
                        str(count_new_rules), row[1], row[2], row[3], ",".join(temp_src), row[5], row[6], row[7],
                        row[8], row[9])
                    db_worker.create_net_obj(conn, net_obj, 'security_policy_filtered', sql_security_policy)
                    logging.info(net_obj)
                    count_new_rules += 1
                elif dst_fil == 1 and src_fil == 0 and flag == "1":
                    logging.info("Rule with number, name " + str(
                        row[0]) + "," + rule_name + " has matched only destination and should be particialy copied")
                    rule = network_objects.security_rule(str(count_new_rules), row[2], row[4], row[5],
                                                         ",".join(temp_dst), row[7], row[8], row[9], row[3])
                    print(str(count_new_rules), rule.name, rule.src, rule.src_neg, rule.dst, rule.dst_neg,
                          rule.services,
                          rule.action, rule.comments)
                    net_obj = (
                        str(count_new_rules), row[1], row[2], row[3], row[4], row[5], ",".join(temp_dst), row[7],
                        row[8], row[9])
                    db_worker.create_net_obj(conn, net_obj, 'security_policy_filtered', sql_security_policy)
                    logging.info(net_obj)
                    count_new_rules += 1
        logging.info(count_new_rules)
        conn.commit()
        cur.execute("DROP TABLE IF EXISTS security_policy;")
        conn.commit()
        cur.execute("""ALTER TABLE security_policy_filtered 
  RENAME TO security_policy;""")
        conn.commit()
    else:
        print("Error! cannot create the database connection.")
        logging.warning("Error! cannot create the database connection.")
