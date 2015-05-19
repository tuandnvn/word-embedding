'''

@author: Tuan Do
'''
import os

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "data")
TYPEDM_DIR = os.path.join(DATA_DIR, "TypeDM")
VERBNET_DIR = os.path.join(DATA_DIR, "verbnet")
VERBCLASS_DIR = os.path.join(VERBNET_DIR, "verbclass")
LENCI_DIR = os.path.join(DATA_DIR, "Lenci")

LENCI_ANTONYM_FILE = os.path.join(LENCI_DIR, "EN_ant_verb.txt")
LENCI_SYNONYM_FILE = os.path.join(LENCI_DIR, "EN_syn_verb.txt")
LENCI_BLESS = os.path.join(LENCI_DIR, "BLESS.txt")
LENCI_NOUNS =  os.path.join(LENCI_DIR, "lenci_nouns.txt")
LENCI_HYPONYMS =  os.path.join(LENCI_DIR, "hyponym.txt")
LENCI_HYPERNYMS =  os.path.join(LENCI_DIR, "hypernym.txt")
LENCI_WORD_RANKS =  os.path.join(LENCI_DIR, "ranks.txt")

GOOGLE_DIR = os.path.join(DATA_DIR, "google")
GOOGLE_DATA_FILE = os.path.join(GOOGLE_DIR, 'trunk', "GoogleNews-vectors-negative300.bin")
GOOGLE_DATA_300K = os.path.join(GOOGLE_DIR, 'trunk', "most_frequent_300k.bin")
GOOGLE_VERB_VECTOR_FILE = os.path.join(GOOGLE_DIR, 'google.verb.vector.json')
GOOGLE_VERB_SIMILAR = os.path.join(GOOGLE_DIR, 'google.verb.similar.txt')
GOOGLE_VERB_SIMILAR_JSON = os.path.join(GOOGLE_DIR, 'google.verb.similar.json')
GOOGLE_VERB_ADJECTIVE_SIMILAR = os.path.join(GOOGLE_DIR, 'google.verb.adjective.similar.txt')
GOOGLE_VERB_ADJECTIVE_SIMILAR_JSON = os.path.join(GOOGLE_DIR, 'google.verb.adjective.similar.json')
GOOGLE_VERB_ADVERB_SIMILAR = os.path.join(GOOGLE_DIR, 'google.verb.adverb.similar.txt')
GOOGLE_VERB_ADVERB_SIMILAR_JSON = os.path.join(GOOGLE_DIR, 'google.verb.adverb.similar.json')
GOOGLE_VERB_NOUN_SIMILAR = os.path.join(GOOGLE_DIR, 'google.verb.noun.similar.txt')
GOOGLE_VERB_NOUN_SIMILAR_JSON = os.path.join(GOOGLE_DIR, 'google.verb.noun.similar.json')
GOOGLE_VERB_ARTICLE_SIMILAR = os.path.join(GOOGLE_DIR, 'google.verb.article.similar.txt')
GOOGLE_CONJUNC_VERB_SIMILAR = os.path.join(GOOGLE_DIR, 'google.conjunc.verb.similar.txt')
GOOLGE_VERB_SIMILAR_INTERCEPT_INDEX = os.path.join(GOOGLE_DIR, 'google.verb.similar.intercept.json')
GOOGLE_ADJECTIVE_VECTOR_FILE = os.path.join(GOOGLE_DIR, 'google.adjective.vector.json')
GOOGLE_ADVERB_VECTOR_FILE = os.path.join(GOOGLE_DIR, 'google.adverb.vector.json')
GOOGLE_NOUN_VECTOR_FILE = os.path.join(GOOGLE_DIR, 'google.noun.vector.json')
GOOGLE_ARTICLE_VECTOR_FILE = os.path.join(GOOGLE_DIR, 'google.article.vector.json')
GOOGLE_CONJUNC_VECTOR_FILE = os.path.join(GOOGLE_DIR, 'google.conjunct.vector.json')

GOOGLE_NOUN_SIMILAR = os.path.join(GOOGLE_DIR, 'google.noun.similar.txt')
GOOGLE_NOUN_SIMILAR_JSON = os.path.join(GOOGLE_DIR, 'google.noun.similar.json')
GOOGLE_NOUN_ADJECTIVE_SIMILAR = os.path.join(GOOGLE_DIR, 'google.noun.adjective.similar.txt')
GOOGLE_NOUN_ADJECTIVE_SIMILAR_JSON = os.path.join(GOOGLE_DIR, 'google.noun.adjective.similar.json')
GOOGLE_NOUN_ADVERB_SIMILAR = os.path.join(GOOGLE_DIR, 'google.noun.adverb.similar.txt')
GOOGLE_NOUN_ADVERB_SIMILAR_JSON = os.path.join(GOOGLE_DIR, 'google.noun.adverb.similar.json')
GOOGLE_NOUN_VERB_SIMILAR = os.path.join(GOOGLE_DIR, 'google.noun.verb.similar.txt')
GOOGLE_NOUN_VERB_SIMILAR_JSON = os.path.join(GOOGLE_DIR, 'google.noun.verb.similar.json')

TENSOR_FILENAME = os.path.join(TYPEDM_DIR, 'typedm.txt')
SVD_FILENAME = os.path.join(TYPEDM_DIR, 'ri.w-lw.txt')
VERB_SVD_FILENAME = os.path.join(TYPEDM_DIR, 'verb.ri.w-lw.txt')
ADJECTIVE_SVD_FILENAME = os.path.join(TYPEDM_DIR, 'adjective.ri.w-lw.txt')
NEAREST_NEIGHBOR_FILENAME = os.path.join(TYPEDM_DIR, 'ri.w-lw_nn_10.txt')

NOUNS = os.path.join(DATA_DIR, 'nouns.txt')
VERBS = os.path.join(DATA_DIR, 'verbnet.txt')
VERB_DICT = os.path.join(DATA_DIR, 'verbnet-dict.txt')
ADJECTIVES = os.path.join(DATA_DIR, 'adjectives.txt')
ADVERBS = os.path.join(DATA_DIR, 'adverbs.txt')
ARTICLES = os.path.join(DATA_DIR, 'articles.txt')
CONJUNCS = os.path.join(DATA_DIR, 'conjuncs.txt')

TYPEDM_VERB_VECTOR_FILE = os.path.join(TYPEDM_DIR, 'typedm.verb.vector.json')
TYPEDM_ADJECTIVE_VECTOR_FILE = os.path.join(TYPEDM_DIR, 'typedm.adjective.vector.json')
TYPEDM_VERB_SIMILAR = os.path.join(TYPEDM_DIR, 'typedm.verb.similar.txt')
TYPEDM_VERB_SIMILAR_JSON = os.path.join(TYPEDM_DIR, 'typedm.verb.similar.json')
TYPEDM_VERB_ADJECTIVE_SIMILAR = os.path.join(TYPEDM_DIR, 'typedm.verb.adjective.similar.txt')
TYPEDM_VERB_ADJECTIVE_SIMILAR_JSON = os.path.join(TYPEDM_DIR, 'typedm.verb.adjective.similar.json') 

FRAMENET_VERB_CLASS = os.path.join(TYPEDM_DIR, 'verb.framenet.class.txt')
FRAMENET_VERB_VECTOR = os.path.join(TYPEDM_DIR, 'verb.framenet.vector.txt')
FRAMENET_SELECTED_FEATURES_VERB_VECTOR = os.path.join(TYPEDM_DIR, 'verb.framenet.vector.selected.1000.txt')
# FRAMENET_SELECTED_FEATURES_VERB_VECTOR = os.path.join(TYPEDM_DIR, 'verb.framenet.vector.selected.500.txt')

AGG_AVERAGE = os.path.join(TYPEDM_DIR, 'agg_average.txt')
VERB_SIMILAR_FRAMENET_ONLY = os.path.join(TYPEDM_DIR, 'verb.framenet.vector.similar.verb.txt')
VERB_SIMILAR_FRAMENET_ONLY_JSON = os.path.join(TYPEDM_DIR, 'verb.framenet.vector.similar.verb.json') 
VERB_SIMILAR_FRAMENET_ONLY_SELECTED_FEATURES = os.path.join(TYPEDM_DIR, 'verb.framenet.vector.selected.1000.similar.verb.txt')
VERB_SIMILAR_FRAMENET_ONLY_JSON_SELECTED_FEATURES = os.path.join(TYPEDM_DIR, 'verb.framenet.vector.selected.1000.similar.verb.json')


WORD = "word"
RANKS = "ranks"
SEMANTIC_TYPE = 'semantic_type'
RANDOM_N = 'random-n'
RANDOM_V = 'random-v'
RANDOM_J = 'random-j'
MERO = 'mero'
HYPER = 'hyper'
EVENT = 'event'
COORD = 'coord'
ATTRI = 'attri'
ANTONYMS = "antonyms"
SYNONYMS = "synonyms"
VERB = "verb"
ADJ = "adj"
NOUN = "noun"
ADV = "adv"

ANALOGY_FILE = os.path.join(DATA_DIR, 'word-test.v1.txt')
CAPITAL_COMMON_COUNTRIES = 'capital-common-countries'

SCALE_ADJ = os.path.join(DATA_DIR, 'scale adj.txt')
ORDERED_SCALE_ADJ = os.path.join(DATA_DIR, 'scale_adj_order.txt')

ADDTIONAL_RELATION = os.path.join(DATA_DIR, 'other_relations.txt')
ADDTIONAL_ANALOGY_QUESTION_FILE = os.path.join(DATA_DIR, 'additional_questions.txt')
