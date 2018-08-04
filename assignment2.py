from time import *
import subprocess
import matplotlib.pyplot as plt
import numpy as np
import sys
import shlex

SPLIT_NO = 3

def make_lp_file(X, Y, Z):
    """create lp file"""
    file_name = "assignment2.lp"
    with open(file_name, "w") as f:
        my_string = "Minimize\n\tload\nSubject to\n"
        for i in range(1, X+1):
            for j in range(1 ,Z+1):
                for k in range(1, Y+1):
                    if k == 1:
                        my_string += "\tx{}{}{} ".format(i, k, j)
                    else:
                        my_string += "+ x{}{}{} ".format(i, k, j)
                my_string += "= " + str(i+j) + "\n"
        for i in range(1, X+1):
            for j in range(1 ,Z+1):
                for k in range(1, Y+1): 
                    if k == 1:
                        my_string += "\tu{}{}{} ".format(i, k, j)
                    else:
                        my_string += "+ u{}{}{} ".format(i, k, j)
                my_string += "= {}\n".format(SPLIT_NO)
        for i in range(1, X+1):
            for j in range(1 ,Z+1):
                for k in range(1, Y+1):
                    my_string += "\t3 x{}{}{} - {} u{}{}{} = 0\n".format(i, k, j, i+j, i, k, j)
        for i in range(1, X+1):
            for k in range(1 ,Y+1):
                for j in range(1, Z+1):            
                    if j == 1:
                        my_string += "\tx{}{}{} ".format(i, k, j)
                    else:
                        my_string += "+ x{}{}{} ".format(i, k, j)
                my_string += "- c{}{} <= 0\n".format(i, k)                
        for k in range(1, Y+1):
            for j in range(1 ,Z+1):
                for i in range(1, X+1):            
                    if i == 1:
                        my_string += "\tx{}{}{} ".format(i, k, j)
                    else:
                        my_string += "+ x{}{}{} ".format(i, k, j)
                my_string += "- d{}{} <= 0\n".format(k, j)
        for k in range(1, Y+1):
            for j in range(1, Z+1):
                for i in range(1, X+1):
                    if i == 1 and j ==1:
                        my_string += "\tx{}{}{} ".format(i, k, j)
                    else:
                        my_string += "+ x{}{}{} ".format(i, k, j)
            my_string += "- load <= 0\n"
        my_string += "Bounds\n"
        for i in range(1, X+1):
            for k in range(1 ,Y+1):
                for j in range(1, Z+1):
                    my_string += "\tx{}{}{} >= 0\n".format(i, k, j)
        my_string += "\tload >= 0\nBINARY\n"
        for i in range(1, X+1):
            for k in range(1 ,Y+1):
                for j in range(1, Z+1):
                    my_string += "\tu{}{}{}\n".format(i, k ,j)
        my_string += "END\n"
        f.write(my_string)
    return file_name
        
def process(file, Y):
    """read lp file, calculate optimized result, print the result on console"""
    cplex = "/home/cosc/student/ycu20/cosc364/cplex/bin/x86-64_linux/cplex"
    command = "time " + cplex +" -c read " + file + " optimize display solution variables -"
    args = shlex.split(command)
    proc = subprocess.Popen(command, stdout = subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash', shell=True)
    stdout, stderr = proc.communicate()
    time_str = str(stderr)
    msg_str = str(stdout)
    real_index = time_str.index('real')
    cplex_time = time_str[real_index+8 : real_index+14]
    # if no feasible solution, print an error message
    try:
        start_index = msg_str.index('Solution Value') + 16
    except ValueError: 
        return print('No integer feasible solution exists.')
    # if there is no zero variables, a value error will be caught
    # the result message is caught by a different way from result with zero variables
    try:
        end_index = msg_str.index('All other variables in the range') - 2
    except ValueError: 
        end_index = -10
    msgs = msg_str[start_index:end_index].split("\\n")
    x_msg = {}
    max_c = 0.0
    capacity_count = 0
    max_load = 0.0
    for msg in msgs:
        results = msg.split("                          ")
        if results[0].startswith('x'):
            x_msg[results[0]] = results[1]
        elif (results[0].startswith('c') or results[0].startswith('d')): 
            capacity_count += 1
            if float(results[1]) > max_c:
                max_c = float(results[1])
        elif (results[0].startswith('load')):
            max_load = results[0].strip().replace('load', '')
    loads = {}
    for i in range(1, Y+1):    
        for k,v in x_msg.items():
            if int(k[2]) == i:
                if str(i) not in loads:
                    loads[str(i)] = float(v)
                else:
                    loads[str(i)] += float(v)
    #~ # sort list make output ordered
    for k, v in sorted(loads.items()):
        print('Router{}\'s load is {}.'.format(k, v))     
    print("Cplex running time: {}".format(cplex_time))
    print('The maximum load accross the transit node is {:.3f}'.format(float(max_load)))
    print('The number of links with non-zero capacities is {}'.format(capacity_count))
    print('The capacity of the link with highest capacity is {}.'.format(max_c))
         
    
def main():
    # catch all invalid input
    try:
        X = int(sys.argv[1])
        Y = int(sys.argv[2])
        Z = int(sys.argv[3])
    except ValueError:
        print("Invalid argument(s)")
        return
    # automatically generate lp file
    file_name = make_lp_file(X, Y ,Z)
    # because we need to generate a lp file with 2 transit nodes.
    # so that this check is moved down to make_lp_file function.
    if Y <= SPLIT_NO -1:
        return print("Invalid arguments on number of transit nodes.\n The number of transit nodes must be larger than split number")   
    # process lp file by cplex through pipline and display result
    process(file_name, Y)

if __name__ == "__main__":
    main()
