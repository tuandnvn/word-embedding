'''
Created on May 24, 2015

@author: Tuan Do
'''
import codecs
import glob
import json
from multiprocessing import Manager
import multiprocessing
import os
import re

from Cython.Debugger.DebugWriter import etree
from gensim import utils
import numpy

from bnc import BNC_DIR
from bnc.bnc_process import get_w_and_c_in
from bnc.util import process_document, process_sentence
from create_seed_vectors import TEST, TRAIN, PATTERN_FILE, PATTERN_PICKLE_FILE, \
    PATTERN_SPLIT_FILE, PATTERN_FILE_EXTEND
from create_seed_vectors.create_seed import PATTERN_NUMBER, EXAMPLES, REF, LEFT, \
    TARGET, RIGHT, FULL_EXAMPLE


class Process_Text(multiprocessing.Process):
    def __init__(self, begin, end, all_xml_files, data):
        multiprocessing.Process.__init__(self)
        self.begin = begin
        self.end = end
        self.all_xml_files = all_xml_files
        self.data = data
    
    def run(self):
        for index in xrange(self.begin, self.end):
            xml_file = self.all_xml_files[index]
            if index % 10 == 0:
                print index
            xml_doc = etree.parse(xml_file)
            try:
                sentences = xml_doc.findall('.//s')
            except AttributeError:
                print 'Error ' + xml_file
            self.data[index] = ' '.join([' '.join([word.text for word in get_w_and_c_in(sentence) if word.text != None]) for sentence in sentences])
            
class Process_For_Full_Text(object):
    '''
    '''

    def __init__(self, pattern_sample_file, directory):
        '''
        pattern_sample_file: pattern file as processed
        directory: directory of BNC data, should be something like
        \bnc\2554\download\Texts
        '''
        self.pattern_sample_file = pattern_sample_file
        self.directory = directory
    
    def read_all_files(self):
        all_xml_files = glob.glob(self.directory + '/*/*/*.xml')
        
        max_doc = len(all_xml_files)
        no_of_thread = 32
        step = int(max_doc / (no_of_thread - 1))
        threads = []
        
        manager = Manager()

        data = manager.dict()
        
        for i in xrange(no_of_thread):
            start = i * step
            end = numpy.min([(i + 1) * step, max_doc])
            print str(start) + " " + str(end)
            this_thread = Process_Text(start, end, all_xml_files, data)
            threads.append(this_thread)
        
        print 'thread start'
        for this_thread in threads:
            this_thread.start()
            
        for this_thread in threads:
            this_thread.join()
            
        print 'thread has joined'
        self.data = {}
        for i in xrange(max_doc):
            xml_file = all_xml_files[i]
            '''
            rel_name = 'AOJ.xml'
            ref = 'AOJ'
            '''
            rel_name = xml_file.split('\\')[-1]
            ref = rel_name[:rel_name.rfind('.xml')]
            self.data[ref] = data[i]
        
    def read_pattern(self, pattern_file ):
        with codecs.open(pattern_file, "r", 'utf-8') as filehandler:
            self.pattern_data = json.load(filehandler)
            
    def save_pattern(self, pattern_file ):
        with codecs.open(pattern_file, "w", 'utf-8') as filehandler:
            json.dump(self.pattern_data, filehandler)
    
    def preprocess_bnc(self):
        for document_name in self.data:
            self.data[document_name] = process_document(self.data[document_name])
            
    def process_for_one_pattern(self, verb, pattern, process_doc = False):
        with codecs.open(os.path.join('debug', verb), 'a', 'utf-8') as file_handler:
            _, examples = (pattern[PATTERN_NUMBER], pattern[EXAMPLES])
            pattern[FULL_EXAMPLE] = []
            for example in examples:
                try:
                    ref = example[REF]
                    
                    '''If document is not yet processed'''
                    if process_doc:
                        document = process_document(self.data[ref])
                    else:
                        document = self.data[ref]
                    
                    sentence = ' '.join([example[LEFT], example[TARGET], example[RIGHT]])
                    sentence = process_sentence(sentence)
                    index = document.find(sentence)
                    
                    file_handler.write(ref)
                    file_handler.write('\n')
                    file_handler.write(sentence)
                    file_handler.write('\n')
                    
                    if index == -1:
                        file_handler.write('Problem finding document for full sentence, back to substring\n')
                        short_left = ' '.join(example[LEFT].split()[-3:])
                        short_right = ' '.join(example[RIGHT].split()[:3])
                        sentence = ' '.join([short_left, example[TARGET], short_right])
                        sentence = process_sentence(sentence)
                        index = document.find(sentence)
                        if index == -1:
                            file_handler.write('Problem finding document for full sentence, back to target string only\n')
                            sentence = process_sentence(example[TARGET])
                            index = document.find(sentence)
                            if index == -1:
                                print 'Example not found!'
                                file_handler.write('No way to find the example in the document\n')
                                file_handler.write('===============================================================\n')
                    if index != -1:
                        l = document[:index].rfind('.')
                        r = document[index + len(sentence):].find('.') + index + len(sentence)
                        extract = document[l + 1 : r]
                        file_handler.write ('============Extract============\n')
                        file_handler.write (extract)
                        file_handler.write ('\n')
                        pattern[FULL_EXAMPLE].append(extract)
                    else:
                        pattern[FULL_EXAMPLE].append('')
                except:
                    pattern[FULL_EXAMPLE].append('')
            if len(pattern[FULL_EXAMPLE]) != len(examples):
                print '======================Big problem======================='
                
                    
    def process_pattern_to_get_full(self, is_split = False, process_doc = False):
        counter = 0
        if is_split:
            for target_word in self.pattern_data[TRAIN]:
                if counter > 1:
                    break
                counter += 1
                for pattern in self.pattern_data[TRAIN][target_word]:
                    self.process_for_one_pattern(target_word, pattern, process_doc)
                        
                for pattern in self.pattern_data[TEST][target_word]:
                    self.process_for_one_pattern(target_word, pattern, process_doc)
        else:
            for target_word in self.pattern_data:
#                 if counter > 10:
#                     break
                print 'Process for target word %s ' % target_word
                counter += 1
                for pattern in self.pattern_data[target_word]:
                    self.process_for_one_pattern(target_word, pattern, process_doc)
        
if __name__ == '__main__':
    if not os.path.exists(PATTERN_PICKLE_FILE):
        print 'Creating Pickle file for pattern data'
         
        t = Process_For_Full_Text(PATTERN_FILE, BNC_DIR)
        t.read_all_files()
        utils.pickle(t, PATTERN_PICKLE_FILE)
    else:
        print 'Load Pickle file for pattern data'
        t = utils.unpickle(PATTERN_PICKLE_FILE)
        
    '''Process all documents first'''
#     t.read_pattern(PATTERN_FILE)
#     t.preprocess_bnc()
#     utils.pickle(t, PATTERN_PICKLE_FILE)
    
    t.process_pattern_to_get_full(process_doc = False)
    t.save_pattern(PATTERN_FILE_EXTEND)
    
#     xml_file = os.path.join(BNC_DIR, 'C' , 'CG', 'CGE.xml')
#     print xml_file
#     xml_doc = etree.parse(xml_file)
#     try:
#         sentences = xml_doc.findall('.//s')
#     except AttributeError:
#         print 'Error ' + xml_file
#     with codecs.open('debug.txt', 'w', 'utf-8') as file_handler:
#         file_handler.write (' '.join([' '.join([word.text for word in get_w_and_c_in(sentence) if word.text != None]) for sentence in sentences]))