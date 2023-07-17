"""Module for creating and filling the Index table.
Loads the index_report JSON file and creates an index
table for each switch.
"""

import json
from mysql.connector import errors

def json_load(file, please):
    """Loads the JSON file and creates the index table for each
    switch if not already created. It then iterates over each
    switch's interface, adding it to the table.
    """

    with open(f"{file}", 'r', encoding="UTF-8") as draft:

        interfaces = json.load(draft)

        for switch in interfaces:

            switch_name = switch["Switch"]

            if "-" in switch_name:
                switch_name = switch_name.replace("-", "_")

            index_table_init(switch_name,
                             please,
                             )

            for index, data in switch.items():

                if index != "Switch":

                    index_table_fill(please,
                                     switch_name,
                                     index,
                                     data
                                     )



def index_table_init(switch, please):
    """SQL command executor for creating the index
    table for each switch.
    """

    alt_statement = f"""
    ALTER TABLE desc_{switch} DROP FOREIGN KEY desc_{switch}_fk"""

    del_statement = f"""
    DROP TABLE IF EXISTS index_{switch} CASCADE;"""

    statement = f"""
    CREATE TABLE IF NOT EXISTS index_{switch}
    (int_id int,
    index_num int,
    int_name varchar(80),
    PRIMARY KEY (int_id))"""

    try:
        please.execute(alt_statement)

    except errors.ProgrammingError:
        pass

    please.execute(del_statement)
    please.execute(statement)



def index_table_fill(please, switch, index, data):
    """SQL command executor for filling in the index table
    with each switch's interface.
    """

    i_ignore_list = ["Ten", "Fo", "Twenty", "App", "Fast"]
    i_ignore = [i for i in i_ignore_list if i in data]

    if not i_ignore:
        statement = f"""
        INSERT INTO index_{switch} (int_id, index_num, int_name)
        VALUES ({index}, {index}, '{str(data)}')"""

        try:
            please.execute(statement)

        except errors.ProgrammingError:
            pass
