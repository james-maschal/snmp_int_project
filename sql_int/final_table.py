"""Module for combining each desc and index table
into a single main table for each switch for
ease of querying and tracking.
"""

import json
import mysql.connector

def json_load(file, please):
    """Loads the JSON file and creates the table,
    then iterates over each switch's tables, adding
    it to the table.
    """

    with open(f"{file}", 'r', encoding="UTF-8") as draft:

        interfaces = json.load(draft)

        final_table_init(please)

        for switch in interfaces:

            switch_name = switch["Switch"]

            if "-" in switch_name:
                switch_name = switch_name.replace("-", "_")

            final_table_fill(please, switch_name)



def final_table_init(please):
    """SQL command executor for creating the reclaim
    table.
    """

    del_statement = """
    DROP TABLE IF EXISTS jns_interfacecounters;"""

    statement = """
    CREATE TABLE IF NOT EXISTS jns_interfacecounters
    (id SERIAL,
    switch varchar(80),
    int_name varchar(80),
    int_desc varchar(80),
    report_date date,
    PRIMARY KEY (id))"""

    try:
        please.execute(del_statement)
        please.execute(statement)

    except mysql.connector.Error as err:
        print(err.msg)



def final_table_fill(please, switch):
    """SQL command executor for filling the reclaim
    table. Combines the desc and index table by
    linking the index number between them.
    """

    statement = f"""
    INSERT INTO jns_interfacecounters
    (switch, int_name, int_desc, report_date)
    SELECT switch, int_name, int_desc, report_date
    FROM desc_{switch} a, index_{switch} b
    WHERE a.int_index = b.index_num"""

    try:
        please.execute(statement)

    except mysql.connector.Error as err:
        print(err.msg)
