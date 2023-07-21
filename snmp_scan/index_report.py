"""Module for checking for switch uptime, and
creating the index report. This report contains
all interfaces that are port reclaim ready."""

import os
import json
from jns_snmp_connect import snmp_connect
from snmp_scan import dict_create

def index(buildings, config):
    """Polls each switch for its interface Inoctet table using SNMP.
    It then passes this to the dictionary creator for filtering any
    interfaces that aren't 0. It then grabs the inventory list of all
    interfaces and cross refrences the ones that are at 0. Finally, it
    sends the info to the json file function."""

    index_report = []
    log_text = ["Index report issues:"]

    for i in buildings:

        for switch in i:

            uptime, log = uptime_check(switch, config)

            if uptime:

                try:
                    final_dict = stage_1(switch, config, log_text)

                    if len(final_dict.keys()) > 0:

                        updict = {"Switch" : switch}
                        updict.update(final_dict)

                        index_report.append(updict)

                except ValueError:
                    pass

            else:
                if log.isspace():
                    pass
                else:
                    log_text.append(log)

    index_json(index_report, config)

    return log_text



def stage_1(switch, config, log_text):
    """Collects inOctet SNMP data, and filters for '0'.
    data is passed on to stage 2."""

    z_vtable, status_1 = snmp_connect.snmp_table(
                                        switch,
                                        config,
                                        config["int_octet"]
                                    )

    if status_1 and len(z_vtable) > 0:
        z_dict, status_2 = dict_create.var_zero(z_vtable)

        if status_2:

            filtered_index = stage_2(switch, config, z_dict, log_text)

            return filtered_index

        log_text.append(f"{switch} - Bad SNMP data (inOctet).")
        return ({}, {})

    log_text.append(f"{switch} - Bad SNMP connection (inOctet).")
    return ({}, {})



def stage_2(switch, config, z_dict, log_text):
    """Collects interface names, and passes that
    and data from stage 1 to stage 3."""

    inter_dict, status_3 = snmp_connect.snmp_table(
                                            switch,
                                            config,
                                            config["int_desc"]
                                            )

    if status_3 and len(inter_dict) > 0:
        filtered_index, status_4 = dict_create.var_interface(inter_dict)

        if status_4:
            final_dict = stage_3(z_dict, filtered_index)
            return final_dict

        log_text.append(f"{switch} - Bad SNMP data (index).")
        return ({}, {})

    log_text.append(f"{switch} - Bad SNMP connection (index).")
    return ({}, {})



def stage_3(z_dict, filtered_index):
    """compares both sets of dictionaries to
    create a final dictionary with interfaces
    that have "zero" inOctet data."""

    final_dict = {}

    if len(z_dict) > 0:

        if len(filtered_index) > 0:

            for index_num, int_name in filtered_index.items():

                reference = z_dict.keys()
                compare = [i for i in reference if i == index_num]

                if compare:

                    final_dict[index_num] = int_name

    return final_dict


def index_json(index_report, config):
    """Prints out results from index report into
    a JSON file, to be read for later uploading
    to database."""

    json_obj = json.dumps(index_report, indent=4)

    path_name = config["index_dir"]
    path_state = os.path.exists(path_name)

    if not path_state:
        os.makedirs(config["index_dir"])

    with open(config["index_path"], 'w', encoding="UTF-8") as draft:
        print(json_obj, file=draft)



def uptime_check(switch, config):
    """Attempts to get the current uptime of the switch.
    If the uptime is at least 90 days, the switch can be
    further polled for snmp data. If less, the switch is
    skipped. If the switch doesn't connect or no longer
    exists, uptime is set to zero."""

    uptime, u_status = snmp_connect.snmp_table(
                                    switch,
                                    config,
                                    config["device_uptime"]
                                )

    if u_status and len(uptime) > 0:

        for i in uptime:

            for oid, val in i:

                val_new = val.prettyPrint()

                try:
                    uptime_days = int(val_new) / 86400

                except ValueError:
                    return (False, f"{switch} - bad uptime value.")

            if uptime_days > 90:
                return (True, " ")

            return (False, " ")

    return (False, f"{switch} - Bad SNMP connect (OID/Community String)")
