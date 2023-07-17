"""Module for creating and filling the desc. table.
Loads the desc_report JSON file and creates an desc
table for each switch.
"""

import json
import mysql.connector

def json_load(file, please):
    """Loads the JSON file and deletes/creates the desc table
    for each switch if not already created. It then iterates
    over each switch's interface, adding it to the table.
    """

    with open(f"{file}", 'r', encoding="UTF-8") as draft:

        interfaces = json.load(draft)

        for switch in interfaces:

            switch_name = switch["Switch"]

            if "-" in switch_name:
                switch_name = switch_name.replace("-", "_")

            desc_table_init(switch_name,
                            please,
                            )

            for index, data in switch.items():

                if index != "Switch":

                    desc_table_fill(please,
                                    switch_name,
                                    index,
                                    data
                                    )



def desc_table_init(switch, please):
    """SQL command executor for creating the desc
    table for each switch. Deletes table first if it already
    exists. Date column is auto-generated on insert.
    """

    del_statement = f"""
    DROP TABLE IF EXISTS desc_{switch};"""

    statement = f"""
    CREATE TABLE IF NOT EXISTS desc_{switch}
    (id SERIAL,
    int_index int,
    switch varchar(80),
    int_desc varchar(80),
    report_date date,
    PRIMARY KEY (id),
    CONSTRAINT desc_{switch}_fk
        FOREIGN KEY (int_index)
        REFERENCES index_{switch} (int_id))"""

    try:
        please.execute(del_statement)
        please.execute(statement)

    except mysql.connector.Error as err:
        print(err.msg)



def desc_table_fill(please, switch, index, data):
    """SQL command executor for filling in the desc
    table with each switch's interface.
    """

    statement = f"""
    INSERT INTO desc_{switch}
    (int_index, switch, int_desc, report_date)
    VALUES ({index}, '{switch}', '{data}', CURDATE())"""

    try:
        please.execute(statement)

    except mysql.connector.Error as err:

        if err.errno==1452:
            pass

        else:
            print(err.msg)
