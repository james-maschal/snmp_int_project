"""This program is designed to collect interfaces
that have not been used in at least 90 days, and
provide this information to a database for later
retreival."""

import configparser
import datetime
import mysql.connector
from jns_cisco_devices import cisco_devices
from snmp_scan import snmp_command
from snmp_scan import index_report
from sql_int import desc_table
from sql_int import index_table
from sql_int import final_table


def main():
    """Main logic."""

    config = configparser.ConfigParser()
    config.read("/[YOUR DIRECTORY HERE]/snmp_int_project/info.ini")
    config_v = {
        "log_path"      : str(config["file_path"]["log_path"]),
        "int_path"      : str(config["file_path"]["int_path"]),
        "index_path"    : str(config["file_path"]["index_path"]),
        "index_dir"     : str(config["file_path"]["index_dir"]),
        "server_passwd" : str(config["sql_user"]["pass"]),
        "server_user"   : str(config["sql_user"]["name"]),
        "server_IP"     : str(config["sql_user"]["server"]),
        "server_port"   : str(config["sql_user"]["port"]),
        "server_db"     : str(config["sql_user"]["db_name"]),
        "int_desc"      : str(config["oid"]["inter_desc"]),
        "int_name"      : str(config["oid"]["inter_name"]),
        "int_octet"     : str(config["oid"]["inter_octet"]),
        "device_uptime" : str(config["oid"]["uptime"]),
        "comm_string"   : str(config["oid"]["c_string"]),
        }

    print("Creating index report...")
    log_text = index_report.index(cisco_devices.interface_buildings(),
                       config_v)

    print("Gathering interface descriptions")
    err_text = snmp_command.snmp_init(config_v)

    try:
        cnx = mysql.connector.connect(
            user        = config_v["server_user"],
            password    = config_v["server_passwd"],
            host        = config_v["server_IP"],
            database    = config_v["server_db"],
            port        = config_v["server_port"]
            )

        please = cnx.cursor()

        print("Creating index tables....")
        index_table.json_load(config_v["index_path"], please)

        print("Creating description tables....")
        desc_table.json_load(config_v["int_path"], please)

        print("Compiling data into final tables....")
        final_table.json_load(config_v["index_path"], please)

        cnx.commit()
        cnx.close()

        date = datetime.datetime.now()

        with open(f"{config_v['log_path']}", 'w', encoding="UTF-8") as log:

            print(f"{date} - INT COUNTER - "
                    "DATABASE CONNECTION SUCCESS", file=log)

            print(log_text, file=log)
            print(err_text, file=log)


    except mysql.connector.Error as err:
        err_num = err.errno
        err_check(err_num, config_v['log_path'], log_text, err_text)

    print("Complete!")



def err_check(err, log_path, log_text, err_text):
    """Checks Mysql error codes for database
    connection issues. logs to file if so,
    otherwise prints to console."""

    conn_err_list = [1045, 1049, 2003, 2005]
    err_checklist = [i for i in conn_err_list if i == err]

    if err_checklist:
        date = datetime.datetime.now()

        with open(f"{log_path}", 'w', encoding="UTF-8") as log:

            print(f"{date} - INT COUNTER - "
                "DATABASE CONNECTION FAILURE", file=log)
            print(log_text, file=log)
            print(err_text, file=log)
            print(err, file=log)



if __name__ == "__main__":
    main()
