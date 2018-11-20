#!/usr/bin/env python3
import os
from datetime import datetime, timedelta

# globals variables
script = os.path.realpath(__file__)
script_dir = os.path.dirname(script)
datavm_number = 2
procs_number = datavm_number * 17
time_delta = timedelta(minutes=20)
threshold = 80
log_dir = os.path.join(script_dir, "logs")


def parse_file(file_name: str) -> (tuple, tuple):
    """
    file_name: str; input file
    return: ("vmme001-data-0/3160", "vmme001-data-0/3232"), (30, 0)
    """
    vm_list = []
    load_list = []
    with open(os.path.join(log_dir, file_name)) as file:
        for line in file:
            # Applying 'sdControl showContextStats' to vmme001-data-0/3160.
            if line.startswith("Applying"):
                vm_proces = line.strip().split(" ")[-1][:-1]
                vm_list.append(vm_proces)
            # Common session:  Session container size: 0  session container max size: 778240  SD load: 30
            if  line.startswith("Common session:"):
                load = line.strip().split(": ")[-1]
                load = int(load)
                load_list.append(load)
    result = (tuple(vm_list), tuple(load_list))

    # major tests for  result
    if len(result[0]) != len(result[1]):
        return ("ERROR: len of tups is not equal", ), (1, )
    if len(result[0]) != procs_number:
        return ("ERROR: len is less than {}".format(procs_number),), (1,)
    return result


def select_log() -> str:
    """
    vmdate_2018-11-18_13-25.log
    return: str or None; filename of log to parse 
    """
    current_time = datetime.now()
    try:
        log_files = [ file for file in os.listdir(log_dir) if os.path.isfile(os.path.join(log_dir, file)) 
                        and file.endswith(".log") and file.startswith("vmdata_") ]
    except IndexError:
        return None
    
    log_files.sort(reverse=True)
    for file in log_files:

        try:
            file_date = datetime.strptime(file, "vmdata_%Y-%m-%d_%H-%M.log")
        except ValueError:
            continue
        if current_time > file_date > current_time - time_delta:
            return file 

    return None

def main():
    """
    main executer
    """
    file = select_log()
    if file is not None:
        # section to execute
        result = parse_file(file)
        print(result)
        max_load = max(result[1])
        if max_load > threshold:
            # do smth
            print("ERROR:", "one process has load=", max_load)
        return "OK"
    else:
        # section to return ERROR
        print("ERROR:", "log file is not available")
        return None


if __name__ == "__main__":
    main()

 