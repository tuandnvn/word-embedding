'''
Cannot modify dictionaries inside dictionaries using Managers from multiprocessing
See http://bugs.python.org/issue6766
result[target_word][pattern_no] is nested dict
-> not working with Manager dict

-> change to keyword = target_word + '_' + pattern_no
'''

import codecs
import json
from multiprocessing import Manager, freeze_support
import multiprocessing
from pprint import pprint, PrettyPrinter

from create_seed_vectors import TRAIN, PATTERN_SPLIT_FILE_EXTEND, \
    DEPENDENCY_FILE, TEST, DEPENDENCY, COREFERENCE
from create_seed_vectors.create_seed import PATTERN_NUMBER, FULL_EXAMPLE
from create_seed_vectors.full_example_parse import process_document
from util.dependency_parser import Parser


def _parse_one(parser, index, sentence):
    processed_full_example = process_document(sentence)
    return parser.parse_tolerant(index, processed_full_example)

class Parse(multiprocessing.Process):
    def __init__(self, begin, end, verbs, p_data, parser, index, result):
        multiprocessing.Process.__init__(self)
        self.begin = begin
        self.end = end
        self.target_words = verbs[begin: end]
        self.parser = parser
        self.index = index
        self.p_data = p_data
        self.result = result
    
    def run(self):
        for target_word in self.target_words:
            print '-----------Process %s-------------' % target_word
            for pattern in self.p_data[target_word]:
                pattern_no, full_examples = (pattern[PATTERN_NUMBER], pattern[FULL_EXAMPLE])
                print '-----------Pattern %s - %s-------------' % (target_word, pattern_no)
#                 counter = 0
                for index, full_example in enumerate(full_examples):
#                     if counter > 5:
#                         break
#                     counter += 1
                    self.result[target_word + '_' + pattern_no + '_' + str(index)] = _parse_one(self.parser, self.index, full_example)
                    
class Parse_Additional(multiprocessing.Process):
    def __init__(self, begin, end, verbs, p_data, parser, index, result):
        multiprocessing.Process.__init__(self)
        self.begin = begin
        self.end = end
        self.target_words = verbs[begin: end]
        self.parser = parser
        self.index = index
        self.p_data = p_data
        self.result = result
    
    def run(self):
        for target_word in self.target_words:
            print '-----------Process %s-------------' % target_word
            for pattern in self.p_data[target_word]:
                pattern_no, full_examples = (pattern[PATTERN_NUMBER], pattern[FULL_EXAMPLE])
                print '-----------Pattern %s - %s-------------' % (target_word, pattern_no)
#                 counter = 0
                for index, full_example in enumerate(full_examples):
#                     if counter > 5:
#                         break
#                     counter += 1
                    if target_word + '_' + pattern_no + '_' + str(index) in self.result:
                        parsed = self.result[target_word + '_' + pattern_no + '_' + str(index)]
                    else:
                        parsed = None
                        
                    if parsed == None:
                        if full_example.strip() == '':
                            continue
                        print 'Rerun for None'
                        print full_example
                        self.result['_'.join([target_word, pattern_no, str(index)])] = _parse_one(self.parser, self.index, full_example)
                    elif parsed[DEPENDENCY] == [[]]:
                        print 'Rerun for recover dependency'
                        full_example = full_examples[index]
                        print full_example
                        self.result['_'.join([target_word, pattern_no, str(index)])] = _parse_one(self.parser, self.index, full_example)
#                     elif parsed[COREFERENCE] == []:
#                         full_example = full_examples[index]
#                         parsed = _parse_one(self.parser, self.index, full_example)
#                         if parsed["dependency"] != [[]]:
#                             print 'Rerun for recover coreference'
#                             print full_example
#                             self.result['_'.join([target_word, pattern_no, str(index)])] = parsed
                
class Dependency_Parser(object):

    def __init__(self, pattern_sample_file, debug_mode, debug_verbs, begin_value = 2346, t = 10):
        '''
        Constructor
        '''
        self.pattern_sample_file = pattern_sample_file
        self.debug_mode = debug_mode
        self.debug_verbs = debug_verbs
        self.read_pattern()
        self.no_of_threads = t
        self.parser = Parser(host = '127.0.0.1', begin_value = begin_value, t = t)
        
    def read_pattern(self):
        print 'Read pattern file'
        with open(self.pattern_sample_file, "r") as filehandler:
            self.pattern_data = json.load(filehandler)
            
    def process_dependency(self, dependency_output):
        if self.debug_mode:
            target_words = self.debug_verbs
        else:
            target_words = self.pattern_data[TRAIN].keys()
        
        m = Manager()
        train_result = m.dict()
        test_result = m.dict()
        
        '''Adding multiple threads'''
        max_verbs = len(target_words)
        step = int(max_verbs / self.no_of_threads )
        threads = []
         
        for i in xrange(self.no_of_threads):
            start = i * step
            end = min([(i + 1) * step, max_verbs])
            print str(start) + " " + str(end)
             
            this_thread = Parse(start, end, target_words, self.pattern_data[TRAIN], self.parser, i, train_result)
            threads.append(this_thread)
         
        print 'thread start for training'
        for this_thread in threads:
            this_thread.start()
             
        for this_thread in threads:
            this_thread.join()
             
        print 'thread has joined for training'
        threads = []
        for i in xrange(self.no_of_threads):
            start = i * step
            end = min([(i + 1) * step, max_verbs])
            print str(start) + " " + str(end)
             
            this_thread = Parse(start, end, target_words, self.pattern_data[TEST], self.parser, i, test_result)
            threads.append(this_thread)
         
        print 'thread start for testing'
        for this_thread in threads:
            this_thread.start()
             
        for this_thread in threads:
            this_thread.join()
             
        print 'thread has joined for testing'
     
#         for target_word in target_words:
#             result[target_word] = {}
#             print '-----------Process %s-------------' % target_word
#             for pattern in self.pattern_data[TRAIN][target_word]:
#                 pattern_no, full_examples = (pattern[PATTERN_NUMBER], pattern[FULL_EXAMPLE])
#                 print '-----------Pattern %s-------------' % pattern_no
#                 result[target_word][pattern_no] = []
#         
#                 for full_example in full_examples:
#                     result[target_word][pattern_no].append( self._parse_one(full_example) )
        
        tempo = {TRAIN:{}, TEST:{}}
        for k in train_result.keys():
            tempo[TRAIN][k] = train_result[k]
        for k in test_result.keys():
            tempo[TEST][k] = test_result[k]
        
        with codecs.open(dependency_output, 'w', 'utf-8') as file_handler:
            json.dump(tempo, file_handler)
#             pp = PrettyPrinter(width=200, stream = file_handler)
#             pp.pprint(tempo)
            
    def process_dependency_remaining(self, dependency_output):
        with codecs.open(dependency_output, 'r', 'utf-8') as file_handler:
            result = json.load(file_handler)
            
        print 'Finish reading dependency'
            
        m = Manager()
        train_result = m.dict()
        test_result = m.dict()
        
        for key in result[TRAIN]:
            train_result[key] = result[TRAIN][key]
        for key in result[TEST]:
            test_result[key] = result[TEST][key]
            
        if self.debug_mode:
            target_words = self.debug_verbs
        else:
            target_words = self.pattern_data[TRAIN].keys()
        
        '''Adding multiple threads'''
        max_verbs = len(target_words)
        step = int(max_verbs / self.no_of_threads )
        threads = []
         
        for i in xrange(self.no_of_threads):
            start = i * step
            end = min([(i + 1) * step, max_verbs])
            print str(start) + " " + str(end)
             
            this_thread = Parse_Additional(start, end, target_words, self.pattern_data[TRAIN], self.parser, i, train_result)
            threads.append(this_thread)
         
        print 'thread start for training'
        for this_thread in threads:
            this_thread.start()
             
        for this_thread in threads:
            this_thread.join()
             
        print 'thread has joined for training'
        threads = []
        for i in xrange(self.no_of_threads):
            start = i * step
            end = min([(i + 1) * step, max_verbs])
            print str(start) + " " + str(end)
             
            this_thread = Parse_Additional(start, end, target_words, self.pattern_data[TEST], self.parser, i, test_result)
            threads.append(this_thread)
         
        print 'thread start for testing'
        for this_thread in threads:
            this_thread.start()
             
        for this_thread in threads:
            this_thread.join()
             
        print 'thread has joined for testing'
        
#         for target_word in target_words:
#             print '-----------Process %s-------------' % target_word
#             for pattern in self.pattern_data[TRAIN][target_word] + self.pattern_data[TEST][target_word]:
#                 pattern_no, full_examples = (pattern[PATTERN_NUMBER], pattern[FULL_EXAMPLE])
#                 if pattern_no in result[target_word]:
#                     print '-----------Recover pattern %s %s-------------' % (target_word, pattern_no)
#                     for index, parsed in enumerate(result[target_word][pattern_no]):
#                         if parsed == None:
#                             full_example = full_examples[index]
#                             if full_example.strip() == '':
#                                 continue
#                             print 'Rerun for None'
#                             print full_example
#                             result['_'.join([target_word, pattern_no, str(index)])] = _parse_one(self.parser, 0, full_example)
#                         elif parsed["dependency"] == [[]]:
#                             print 'Rerun for recover dependency'
#                             full_example = full_examples[index]
#                             print full_example
#                             result['_'.join([target_word, pattern_no, str(index)])] = _parse_one(self.parser, 0, full_example)
#                         elif parsed["coreference"] == []:
#                             full_example = full_examples[index]
#                             parsed = self._parse_one(full_example)
#                             if parsed["dependency"] != [[]]:
#                                 print 'Rerun for recover coreference'
#                                 print full_example
#                                 result['_'.join([target_word, pattern_no, str(index)])] = parsed
#                 else:
#                     print '-----------Pattern %s %s-------------' % (target_word, pattern_no)
#                      
#                     for full_example in full_examples:
#                         result['_'.join([target_word, pattern_no, str(index)])] = self._parse_one(full_example)
                                
        tempo = {TRAIN:{}, TEST:{}}
        for k in train_result.keys():
            tempo[TRAIN][k] = train_result[k]
        for k in test_result.keys():
            tempo[TEST][k] = test_result[k]
        
        with codecs.open(dependency_output, 'w', 'utf-8') as file_handler:
            json.dump(tempo, file_handler)
#             pp = PrettyPrinter(width=200, stream = file_handler)
#             pp.pprint(tempo)

    def print_to_read(self, input, output):
        with codecs.open(input, 'r', 'utf-8') as file_handler:
            result = json.load(file_handler)
            
        with codecs.open(output, 'w', 'utf-8') as file_handler:
            pp = PrettyPrinter(width=200, stream = file_handler)
            pp.pprint(result)
    
if __name__ == '__main__':
#     freeze_support()
    t = Dependency_Parser(PATTERN_SPLIT_FILE_EXTEND, debug_mode = False, debug_verbs = ['scratch', 'sleep', 'see', 'seep', 'appear', 'plant', 'pour', 'eat'], t = 4)
#     t = Dependency_Parser(PATTERN_SPLIT_FILE_EXTEND, debug_mode = True, debug_verbs = ['scratch'], t = 1)
#     t.process_dependency('scratch.json')
#     t.process_dependency_remaining('scratch.json')
#     t.print_to_read('scratch.json', 'scratch_2.json')
    t.process_dependency(DEPENDENCY_FILE)
    t.process_dependency_remaining(DEPENDENCY_FILE)