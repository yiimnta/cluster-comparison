def parse_value(str : str):
    str = str.strip()
    if (str.startswith('"') and str.endswith('"')) or (str.startswith('\'') and str.endswith('\'')):
        return str[1:-1]
    elif str.replace(',', '').isdigit() or str.replace('.', '').isdigit():
        return float(str.replace(',', '.'))
    else:
        return str

def compare_objects(input_objs, test_objs, all = False, debug = False):
    all_match = True
    for art_id in test_objs:
        if art_id in input_objs:
            for sec_id in test_objs[art_id]:
                if sec_id in input_objs[art_id]:
                    for td_id in test_objs[art_id][sec_id]:
                        if td_id in input_objs[art_id][sec_id]:
                            if test_objs[art_id][sec_id][td_id] != input_objs[art_id][sec_id][td_id]:
                                print(f"\033[31mFAIL::[{art_id:^15}][{sec_id:^15}][{td_id:^15}]: INPUT = '{input_objs[art_id][sec_id][td_id]}', EXPECT = '{test_objs[art_id][sec_id][td_id]}'\033[0m")
                            elif debug:
                                print(f"OK::::[{art_id:^15}][{sec_id:^15}][{td_id:^15}] = {test_objs[art_id][sec_id][td_id]}")
                        else:
                            print(f"[{[art_id]}][{sec_id}][{td_id}]: not found in INPUT.")
                            all_match = False
                else:
                    print(f"[{[art_id]}][{sec_id}]: not found in XML INPUT.")
                    all_match = False
        else:
            print(f"[{[art_id]}]: not found in XML INPUT.")
            all_match = False

    if all_match == False:
        print("TEST OK. BUT there are mismatches between INPUT and TEST.")

    return True and ( not all or all_match )

