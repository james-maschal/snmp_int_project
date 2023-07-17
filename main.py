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
        'ini' : [
            str(config["oid"]["c_string"]),
            str(config["oid"]["inter_desc"]),
            str(config["oid"]["inter_name"]),
            str(config["oid"]["inter_octet"]),
            str(config["file_path"]["index_path"]),
            str(config["file_path"]["int_path"]),
            str(config["oid"]["uptime"]),
            str(config["user"]["name"]),
            str(config["user"]["pass"]),
            str(config["file_path"]["log_path"])
            ]
        }

    log_path = config_v["ini"][9]

    print("Creating index report...")
    log_text = index_report.index(cisco_devices.interface_buildings(),
                       config_v)

    print("Gathering interface descriptions")
    err_text = snmp_command.snmp_init(config_v)

    try:
        cnx = mysql.connector.connect(
                user=config_v["ini"][7],
                password=config_v["ini"][8],
                host= "MYSQL SERVER IP HERE",
                database="int_reclaim",
                port= 3306
                )

        please = cnx.cursor()

        print("Creating index tables....")
        index_table.json_load(config_v["ini"][4], please)

        print("Creating description tables....")
        desc_table.json_load(config_v["ini"][5], please)

        print("Compiling data into final tables....")
        final_table.json_load(config_v["ini"][4], please)

        cnx.commit()
        cnx.close()

        date = datetime.datetime.now()

        with open(f"{log_path}", 'w', encoding="UTF-8") as log:

            print(f"{date} - INT COUNTER - "
                    "DATABASE CONNECTION SUCCESS", file=log)
            try:
                print(log_text, file=log)
                print(err_text, file=log)
            except:
                #only for debug purposes
                pass

    except mysql.connector.Error as err:
        err_num = err.errno
        err_check(err_num, log_path, log_text, err_text)

    print("Complete!")



def err_check(err, log_path, log_text, err_text):
    """Checks Mysql error codes for database
    connection issues. logs to file if so,
    otherwise prints to console."""

    conn_err_list = [1045, 1049, 2003, 2005]
    err_check = [i for i in conn_err_list if i == err]

    if err_check:
        date = datetime.datetime.now()

        with open(f"{log_path}", 'w', encoding="UTF-8") as log:

            print(f"{date} - INT COUNTER - "
                "DATABASE CONNECTION FAILURE", file=log)
            print(log_text, file=log)
            print(err_text, file=log)
            print(err, file=log)



if __name__ == "__main__":
    main()
