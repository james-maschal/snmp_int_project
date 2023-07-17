"""Module for formatting/filtering all SNMP data."""

def var_zero(vartable):
    """This takes the output SNMP table for
    each switch and checks for interfaces that have
    zero Inoctets since switch was last booted."""

    snmp_info = {}

    for i in vartable:
        for oid, val in i:

            oid_old = oid.prettyPrint()
            val_old = val.prettyPrint()

            if int(val_old) == 0:

                index = oid_old.split("1.3.6.1.2.1.2.2.1.10.")[-1]
                snmp_info[index] = 0

    return snmp_info, True



def var_interface(index_dict):
    """Takes inventory output table gathered from
    SNMP poll and strips any items that aren't
    'Ethernet' interfaces."""

    new_index = {}

    for i in index_dict:

        for oid, val in i:

            oid_old = oid.prettyPrint()
            val_old = val.prettyPrint()

            if "Ethernet" in val_old:
                index = oid_old.split("1.3.6.1.2.1.2.2.1.2.")[-1]
                new_index[index] = val_old

    return new_index, True



def var_desc(desc, index):
    """Takes interface description output table
    and strips it of interfaces that weren't marked
    zero earlier. If there is no description on the
    interface, 'NO DESC' is appended to it."""

    desc_dict = {}

    for i in desc:

        for oid, val in i:

            oid_old = oid.prettyPrint()
            val_old = val.prettyPrint()

            index_check = oid_old.split("1.3.6.1.2.1.31.1.1.1.18.")[-1]
            compare = [i for i in index if i == index_check]

            if compare:
                if val_old == "":
                    val_old = "NO DESC"
                elif "'" in val_old:
                    val_old = val_old.replace("'", "''")
                elif '"' in val_old:
                    val_old = val_old.replace("'", '""')

                desc_dict[index_check] = val_old

    return desc_dict, True
