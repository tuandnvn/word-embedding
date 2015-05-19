'''
Created on May 18, 2015

@author: Tuan Do
'''
import codecs
import glob
from multiprocessing import Manager
import multiprocessing

from gensim.utils import to_unicode, deaccent, PAT_ALPHABETIC
from lxml import etree
import numpy
from spacy.en import English

from bnc import BNC_DIR, BNC_RAW_TEXT


nlp = English()

def simple_process(text, lowercase=False):
    """
    Iteratively yield tokens as unicode strings, optionally also lowercasing them
    and removing accent marks.
    Input text may be either unicode or utf8-encoded byte string.
    The tokens on output are maximal contiguous sequences of alphabetic
    characters (no digits!).
    """
    text = to_unicode(text)
    if lowercase:
        text = text.lower()
    keep_alphabetic_text = ' '.join([m.group() for m in PAT_ALPHABETIC.finditer(text)])
    return keep_alphabetic_text
    
def parse_sentence(sentence):
    result = []
    pos_results = nlp(sentence)
    for token_struct in pos_results:
        token, pos = token_struct.orth_, token_struct.tag_
        pos = pos.lower()
        if pos[-1:] == '$':
            pos = pos[:-1]
        if pos[:2] == 'jj':
            pos = 'j'
        if pos[:2] == 'nn':
            pos = 'n'
        if pos[:2] == 'vb':
            pos = 'v'
        if pos[:1] == 'w':
            pos = 'w'
        if pos[:2] == 'rb':
            pos = 'r'
        token = token.lower()
        result.append(token + '-' + pos)
    return result

def get_w_and_c_in(element):
    if element == None:
        return
    if element.tag == 'w' or element.tag == 'c':
        yield element
    for e in element:
        for t in get_w_and_c_in(e):
            yield t
                    
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
            doc_text = ''
            for sentence in sentences:
                for word in get_w_and_c_in(sentence):
                    text = word.text
                    if text != None:
                        doc_text += text + ' '
            doc_text = simple_process(doc_text, lowercase = True)
            doc_text_parsed = ' '.join(parse_sentence(doc_text))
            self.data[index] = doc_text_parsed
            
class BNC(object):
    '''
    classdocs
    '''


    def __init__(self, directory):
        '''
        Constructor
        '''
        self.directory = directory
    
    def process_to_file(self, output_file):
        all_xml_files = glob.glob(self.directory + '/*/*/*.xml')
        
        max_doc = 1000
        print len(all_xml_files)
        no_of_thread = 6
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
        
        print 'Begin save file'
        with codecs.open(output_file, 'w', 'utf-8') as file_handler:
            for index in xrange(max_doc):
                if index in data.keys():
                    file_handler.write(data[index])
                    file_handler.write('\n')
                    
        print 'Finish save file'
#             for index, xml_file in enumerate(all_xml_files):
#                 if index % 100 == 0:
#                     print index
#                 xml_doc = etree.parse(xml_file)
#                 w_text = xml_doc.find('wtext')
#                 sentences = w_text.findall('.//s')
#                 doc_text = ''
#                 for sentence in sentences:
#                     for word in get_w_and_c_in(sentence):
#                         text = word.text
#                         if text != None:
#                             doc_text += text + ' '
#                 doc_text = simple_process(doc_text, lowercase = True)
#                 doc_text_parsed = ' '.join(parse_sentence(doc_text))
#                 file_handler.write(doc_text_parsed)
        
if __name__ == '__main__':
    t = BNC(BNC_DIR)
    t.process_to_file(BNC_RAW_TEXT)