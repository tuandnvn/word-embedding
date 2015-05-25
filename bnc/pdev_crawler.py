from _collections import defaultdict
import codecs
import glob
import json
from multiprocessing import freeze_support, Manager
import multiprocessing
import os
import urllib2

from pyreadline.logger import file_handler

from create_seed_vectors import PATTERN_FILE
from create_seed_vectors.create_seed import RIGHT, TARGET, LEFT, REF, \
    PATTERN_NUMBER, PATTERN, IMPLICATURE, EXAMPLES, PERCENTAGE
from utils import DATA_DIR


RAWDICT_DIR = os.path.join(DATA_DIR, "raw_dicts")
PATTERN_DIR = os.path.join(RAWDICT_DIR, "pattern")
PERCENTAGE_DIR = os.path.join(RAWDICT_DIR, "per")
VERB_DIR = os.path.join(RAWDICT_DIR, "verb")

class Crawl_Verb(multiprocessing.Process):
    def __init__(self, begin, end, verbs, store, processed):
        multiprocessing.Process.__init__(self)
        self.begin = begin
        self.end = end
        self.verbs = verbs[begin: end]
        self.store = store
        self.processed = processed
    
    def run(self):
        for verb in self.verbs:
            if verb in self.processed:
                continue
            # if index%10 == 0:
            print 'Send query to pdev action=pattern with verb %s' % verb
            # patterns and implicatures
            url = "http://pdev.org.uk/proxy.php?action=patterns&query=" + verb
            # frequency percentage (not included first line)
            url1 = 'http://pdev.org.uk/proxy.php?action=percents2&query=' + verb
            content = urllib2.urlopen(url).readlines()
            percentList = urllib2.urlopen(url1).readlines()
            percentList = [(e.split()[0], e.split()[1]) for e in percentList[1:]]
            
            with codecs.open(os.path.join(VERB_DIR, "%s.txt" %verb) , 'w', 'utf-8') as file_handler:
                for line in content:
                    file_handler.write(str(line))
            with codecs.open(os.path.join(PERCENTAGE_DIR, "%s.json" %verb), 'w', 'utf-8') as file_handler:
                json.dump(percentList, file_handler)
                
class Crawl_Verb_Pattern(multiprocessing.Process):
    def __init__(self, begin, end, verbs, store, processed):
        multiprocessing.Process.__init__(self)
        self.begin = begin
        self.end = end
        self.verbs = verbs[begin: end]
        self.store = store
        self.processed = processed
    
    def run(self):
        for verb in self.verbs:
            content = []
            with codecs.open(os.path.join(VERB_DIR, "%s.txt" %verb) , 'r', 'utf-8') as file_handler:
                for line in file_handler:
                    content.append(line.strip())
            with codecs.open(os.path.join(PERCENTAGE_DIR, "%s.json" %verb), 'r', 'utf-8') as file_handler:
                percentList = json.load(file_handler)
                
            percents = dict((x, y) for x, y in percentList)
            
            retry_time = 3
            # Build a dictionary for each pattern
            for line in content:
                fields = line.split('\t')
                pattern_no = fields[1]
                if verb + '_' + pattern_no in self.processed:
                    continue
                if self.store == True:
                    try:
                        store_patt_dict(verb, pattern_no)
                        continue
                    except:
                        print "Problem"
                        for i in xrange(retry_time):
                            print "Retry %d " %i
                            try:
                                store_patt_dict(verb, fields[1])
                                break
                            except:
                                continue
                        continue
                try:
                    info_dict = {'pattNum' : fields[1],
                                 'patt' : fields[6],
                                 'impl' : fields[2],
                                 'examples' : get_patt_examples(verb, fields[1], 'par')}
                except:
                    print "some error"
                    print verb
                    print fields[1]
                    continue
                # Take into account missing frequencies
                if len(percents.keys()) < int(fields[1]):
                    info_dict['per'] = ""
                else:
                    try:
                        info_dict['per'] = percents[fields[1]]
                    except:
                        print "another missing frequency..."
                        continue
#                 verb_info_dict[verb].append(info_dict)
        
def create_verb_list(raw_file):
    out = open('verb_list', 'w')
    lines = open(raw_file).readlines()
    for line in lines:
        verb = line.split()[0]
        out.write(verb + '\n')


def store_patt_dict(v, pNum):
    try:
        print 'Query for v %s and pattern number %s' % (v, pNum)
        url = "http://pdev.org.uk/conc.php?verb=" + v + "&patnum=" + pNum + "&expl=both&ssize=1000"
        raw = urllib2.urlopen(url).read()
        # Find dict with right-left-kwic in raw text
        beg_i = raw.find('var data = ')
        if beg_i == -1:
            print "Could not find beginning of dictionary in example page."
        raw_dict = raw[beg_i + 11:]
        end_i = raw_dict.find('$(document).ready(function ()')
        if end_i == -1:
            print "Could not find end of dictionary in example page."
        raw_dict = raw_dict[:end_i - 3]
        raw_dict = eval(raw_dict)
        
        pattern_file = os.path.join(PATTERN_DIR, '%s_%s' % ( v, pNum) )
        with codecs.open(pattern_file, 'w', 'utf-8') as file_handler:
            json.dump(raw_dict, file_handler)
        return True
    except:
        return False

# get examples for a specifis verb v in pattern no. pNum
# Output: a list of example dictionaries
# m = 'par'/'full' for either partial or full sentences.
def get_patt_examples_all_verbs():
    verb_info_dict = defaultdict(list)
    all_verb_files = glob.glob(os.path.join(VERB_DIR, "*.txt"))
    for f in all_verb_files:
        content = []
        verb = f.split(os.path.sep)[-1][:-4]
        with codecs.open(os.path.join(VERB_DIR, "%s.txt" %verb) , 'r', 'utf-8') as file_handler:
            for line in file_handler:
                content.append(line.strip())
        with codecs.open(os.path.join(PERCENTAGE_DIR, "%s.json" %verb), 'r', 'utf-8') as file_handler:
            percentList = json.load(file_handler)
            
        percents = dict((x, y) for x, y in percentList)
        
        print 'Get pattern example for verb %s and # pattern %s ' % (verb, len(content))
        for line in content:
            fields = line.split('\t')
            pattern_no, pattern_form, implicature = fields[1], fields[6], fields[2]
        
            pattern_file = os.path.join(PATTERN_DIR, '%s_%s' % ( verb, pattern_no) )
            with codecs.open(pattern_file, 'r', 'utf-8') as file_handler:
                raw_dict = json.load(file_handler)
            info_dict = {PATTERN_NUMBER : pattern_no,
                         PATTERN : pattern_form,
                         IMPLICATURE : implicature,
                         EXAMPLES : get_patt_examples(raw_dict, verb, pattern_no, 'par')}
    #         except:
    #             print "some error"
    #             print verb
    #             print fields[1]
    #             continue
            # Take into account missing frequencies
            if len(percents.keys()) < int(fields[1]):
                info_dict[PERCENTAGE] = ""
            else:
                try:
                    info_dict[PERCENTAGE] = percents[fields[1]]
                except:
                    print "another missing frequency..."
                    continue
        
            verb_info_dict[verb].append(info_dict)
        
    with codecs.open(PATTERN_FILE, 'w', 'utf-8') as file_handler:
        json.dump(verb_info_dict, file_handler)
            
def get_processed(processed):
    all_files = glob.glob(os.path.join(PATTERN_DIR, "*"))
    for f in all_files:
        v, pNum = f.split(os.path.sep)[-1].split('_')
        processed[v + '_' + pNum] = 1
        
    all_files = glob.glob(os.path.join(VERB_DIR, "*.txt"))
    for f in all_files:
        v = f.split(os.path.sep)[-1][:-4]
        processed[v] = 1
        
def get_patt_examples(raw_dict, v, pNum, m):
#     print 'Get pattern for verb %s and pNum = %s ' %(v , pNum)
    try:
        lines = raw_dict['Lines']
    except:
        print v, pNum
        print raw_dict
        return []

    example_list = []

    i = 0
    # Build output dictionary
    for line in lines:
        # There is an error in "call" example pages, where a specific sub-dictionary occurs
        # in all pages. The list of all toknums in this dictionary is read, and those
        # toknums are ignored.
        if v == "call":
            wrong_toknums = open('wrong_toknums').readlines()
            wrong_toknums = [t.strip() for t in wrong_toknums]
            if str(line['toknum']) in wrong_toknums:
                continue
        if m == 'par':
            ex_dict = {LEFT : ''.join([line['Left'][i]['str'].strip() for i in xrange(len(line['Left']))]),
                       RIGHT : ''.join([line['Right'][i]['str'].strip() for i in xrange(len(line['Right']))]),
                       TARGET : line['Kwic'][0]['str'].strip(),
                       REF : line[REF]}
            
        elif m == 'full':
            url_full = 'http://pdev.org.uk/proxy.php?action=widectx&pos=' + str(line['toknum'])
            raw = urllib2.urlopen(url_full).readlines()
            left = ""
            right = ""
            vic = ""
            pass_mid = 0
            for l in raw:
                if '<i class="strc"' in l or '<a' in l or '</a>' in l:
                    continue
                elif '<i class="coll"' in l:
                    v = l.split()[1][13:]
                    vic += v
                    pass_mid += 1
                else:
                    if pass_mid == 0:
                        left += l[:len(l) - 1]
                    else:
                        right += l[:len(l) - 1]

            if pass_mid > 1:
                print "Too many verbs in vic string!"
            if pass_mid == 0:
                print "No verb in vic string!"
            if vic.strip() != line['Kwic'][0]['str'].strip():
                print "vic is wrong! vic!=kwic"

            ex_dict = {'left' : left.strip(),
                       'right' : right.strip(),
                       'kwic' : vic.strip()}

            if i % 100 == 0:
                print i
            i = i + 1

        example_list.append(ex_dict)
    return example_list
    
    
    
# Creates a json file:
# keys: verbs
# values: lists
# Each element of the list is a dictionary with info. on each pattern
# Keys of this info. dictionary are:
# 'pattNum' - the pattern number (as a string)
# 'patt' - the pattern
# 'impl' - the implicature
# 'per' - frequency percentage
# 'examples' - a list of examples for this pattern
# Each example in the list is a dictionary with keys: 'left','right','kwic'
 
def get_verb_info(processed, store=False, pattern = False):
    verbs = [v.strip() for v in open('verb_list - Copy').readlines()]
    # each verb will have a list of info (patt, impl, num, per)
    # each info is a dictionary
    verb_info_dict = dict([(v, []) for v in verbs])
    print "There are ", len(verbs), "verbs" 
    
    '''Adding multiple threads'''
    no_of_thread = 16
    max_verbs = len(verbs)
    step = int(max_verbs / no_of_thread )
    threads = []
    
    for i in xrange(no_of_thread):
        start = i * step
        end = min([(i + 1) * step, max_verbs])
        print str(start) + " " + str(end)
        
        if pattern:
            this_thread = Crawl_Verb_Pattern(start, end, verbs, store, processed)
        else:
            this_thread = Crawl_Verb(start, end, verbs, store, processed)
        threads.append(this_thread)
    
    print 'thread start'
    for this_thread in threads:
        this_thread.start()
        
    for this_thread in threads:
        this_thread.join()
        
    print 'thread has joined'
    
    out = open('corpusnull.json', 'w')
    json.dump(verb_info_dict, out)
    out.close()
        
if __name__ == '__main__':
    freeze_support()
    
#     manager = Manager()
#     processed = manager.dict()
#     get_processed(processed)
#     get_verb_info(processed, store=True, pattern = True)
    
    get_patt_examples_all_verbs()
