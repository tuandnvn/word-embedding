'''
Created on Jun 9, 2015

@author: Tuan Do
'''
from _collections import defaultdict
import codecs
import glob
import json


SPLIT_SUFFIX = ".spl"

def split_up_json_file( file_name, depth, no_of_split):
    '''Depth is supported = 1 or 2'''
    with codecs.open(file_name, "r", 'utf-8') as filehandler:
        data = json.load(filehandler)
    
    if depth == 1:
        keys = sorted(data.keys())
        if len(keys) < no_of_split:
            depth = 2
        else:
            step = int(len(keys) /no_of_split) + 1
            for i in xrange(no_of_split):
                begin = step * i 
                end = min(len(keys), step *  (i + 1))
                new_data = {}
                for key in keys[begin: end]:
                    new_data[key] = data[key]
                
                with codecs.open(file_name + str(i) + SPLIT_SUFFIX, "w", 'utf-8') as filehandler:
                    json.dump(new_data, filehandler)
            return
    
    if depth == 2:
        keys = sorted(data.keys())
        new_data = defaultdict(dict)
        for key in keys:
            subkeys = sorted(data[key].keys())
            step = int(len(subkeys) /no_of_split) + 1
            for i in xrange(no_of_split):
                begin = step * i 
                end = min(len(subkeys), step *  (i + 1))
                
                if key not in new_data[i].keys():
                    new_data[i][key] = {}
                    
                for subkey in subkeys[begin: end]:
                    new_data[i][key][subkey] = data[key][subkey]
                    
        for i in xrange(len(new_data)):
            with codecs.open(file_name + '.' + str(i) + SPLIT_SUFFIX, "w", 'utf-8') as filehandler:
                json.dump(new_data[i], filehandler, sort_keys=True)
            
def read_splitted_json_files(file_name_prefix):
    '''Supported to 2 levels'''
    file_names = glob.glob(file_name_prefix + "*" + SPLIT_SUFFIX)
    
    data = {}
    for file_name in file_names:
        with codecs.open(file_name, "r", 'utf-8') as filehandler:
            splitted_data = json.load(filehandler)
            for key in splitted_data.keys():
                if not key in data.keys():
                    data[key] = splitted_data[key]
                else:
                    for subkey in splitted_data[key].keys():
                        data[key][subkey] = splitted_data[key][subkey]
    return data

def join_splitted_json_files(file_name_prefix, output_file):
    data = read_splitted_json_files(file_name_prefix)
    with codecs.open(output_file, "w", 'utf-8') as filehandler:
        json.dump(data, filehandler, sort_keys=True)
    
if __name__ == '__main__':
#     split_up_json_file('allocate.json', 2, 5)
    join_splitted_json_files('allocate.json', 'allocate2.json')