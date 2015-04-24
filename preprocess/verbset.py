'''
Created on Feb 5, 2015

@author: Tuan Do
'''

class Verbset(object):
    '''
    classdocs
    '''


    def __init__(self, typeDM_processor ):
        '''
        typeDM_processor: TypeDM: processor that would store the tensor and distributional data
        '''
        self.all_verbs = []
        self.verbclass_dict = {}
    
    def intersection(self, other_verbset):
        '''
        other_verbset : Verbset
        '''
        result_verbset = Verbset()
        result_verbset.all_verbs = self.all_verbs.intersection(other_verbset.all_verbs)
        for rel_name in self.verbclass_dict:
            new_list_of_verbs = [verb for verb in self.verbclass_dict[rel_name] if verb in self.all_verbs]
            result_verbset.verbclass_dict[rel_name] = new_list_of_verbs
        return result_verbset
