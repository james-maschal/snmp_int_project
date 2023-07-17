"""Module for reading index report and gathering
interface descriptions for each switch. Report
of interface descriptions is compiled for
database upload."""

import json
import os
from pysnmp.smi import error
from jns_snmp_connect import snmp_connect
from snmp_scan import dict_create


def snmp_init(config):
    """The index report is read, and an interface
    description table is gathered via snmp. It is
    then processed through dict_create to filter
    interfaces that weren't previously marked zero.
    Finally it's sent to be output to a JSON file."""

    with open(config["ini"][4], 'r', encoding="UTF-8") as draft:

        index_dict = json.load(draft)
        desc_report = []
        err_text = ["Descrption report issues:"]

        for switch_set in index_dict:

            switch_key = switch_set.keys()
            switch = switch_set["Switch"]
            desc_dict = {"Switch" : switch}

            try:
                desc_pretty = stage_1(
                                    switch,
                                    config,
                                    switch_key,
                                    err_text
                                    )

                if len(desc_pretty) > 0:
                    desc_dict.update(desc_pretty)

            except error.NoSuchObjectError:
                pass

            desc_report.append(desc_dict)

        desc_json(desc_report, config)

    return err_text



def stage_1(switch, config, switch_key, err_text):
    """interface description table is gathered
    via snmp. It is then processed through
    dict_create to filter interfaces that weren't
    previously marked zero."""

    desc, status_1 = snmp_connect.snmp_table(
                                    switch,
                                    config,
                                    config["ini"][2]
                                )
    if status_1 and len(desc) > 0:
        desc_pretty, status_2 = dict_create.var_desc(
                                            desc,
                                            switch_key
                                        )
        if status_2:
            return desc_pretty

        err = f"{switch} - Bad SNMP data (description)"
        err_text.append(err)
        return {}

    err = f"{switch} - Bad SNMP connection (description)"
    err_text.append(err)
    return {}


def desc_json(desc_report, config):
    """Takes desc report list and dumps it into a JSON
    file for uploading to a database later. Checks to see if
    "int_report.json" exists, and deletes it if so.
    """

    path_name = config["ini"][5]
    path_state = os.path.exists(path_name)

    if path_state:
        os.remove(path_name)

    json_obj = json.dumps(desc_report, indent=4)

    with open(config["ini"][5], 'a', encoding="UTF-8") as draft:

        print(json_obj, file=draft)
