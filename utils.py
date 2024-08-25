def parse_value(str : str):
    str = str.strip()
    if (str.startswith('"') and str.endswith('"')) or (str.startswith('\'') and str.endswith('\'')):
        return str[1:-1]
    elif str.replace(',', '').isdigit() or str.replace('.', '').isdigit():
        return float(str.replace(',', '.'))
    else:
        return str

def compare_objects(input_objs, test_objs, all = False):
    all_match = True
    for tr_id in test_objs:
        if tr_id in input_objs:
            for td_id in test_objs[tr_id]:
                if td_id in input_objs[tr_id]:
                    if test_objs[tr_id][td_id] != input_objs[tr_id][td_id]:
                        print(f"Mismatch found in row[ {tr_id} ][ {td_id} ]: INPUT has '{input_objs[tr_id][td_id]}', TEST has '{test_objs[tr_id][td_id]}'")
                        return False
                else:
                    print(f"Row[ {tr_id} ][ {td_id} ]: not found in INPUT.")
                    all_match = False
        else:
            print(f"Row[ {tr_id} ]: not found in XML INPUT.")
            all_match = False

    if all_match == False:
        print("TEST OK. BUT there are mismatches between INPUT and TEST.")

    return True and ( not all or all_match )

