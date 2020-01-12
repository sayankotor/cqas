def do_sum(number1, number2):
    return number1 + number2

import os.path
import torch
import sys

# for extractor class
#sys.path.append('/home/vika/targer')
from src.factories.factory_tagger import TaggerFactory
from src.layers import layer_context_word_embeddings_bert

# for responser class
import json
import requests

# for generate answer
from generation.generation import diviner

# pathes to pretrained extraction model

PATH_TO_PRETRAINED = './external_pretrained_models/'
MODEL_NAMES = ['bert_simple1.hdf5']

def load(checkpoint_fn, gpu=-1):
    if not os.path.isfile(PATH_TO_PRETRAINED + checkpoint_fn):
        raise ValueError('Can''t find tagger in file "%s". Please, run the main script with non-empty \
                         "--save-best-path" param to create it.' % checkpoint_fn)
    tagger = torch.load(PATH_TO_PRETRAINED + checkpoint_fn)
    tagger.gpu = gpu

    tagger.word_seq_indexer.gpu = gpu # hotfix
    tagger.tag_seq_indexer.gpu = gpu # hotfix
    if hasattr(tagger, 'char_embeddings_layer'):# very hot hotfix
        tagger.char_embeddings_layer.char_seq_indexer.gpu = gpu # hotfix
    tagger.self_ensure_gpu()
    return tagger

def create_sequence_from_sentence(str_sentences):
    return [str_sentence.lower().split() for str_sentence in str_sentences]

class extractor:
    def __init__(self, input_sentence, model_name = 'bert_simple1.hdf5', model_path = './external_pretrained_models/'):
        self.input_str = input_sentence
        self.answ = "UNKNOWN ERROR"
        self.model_name = model_name
        self.model_path = model_path
        self.first_object = ''
        self.second_object = ''
        self.predicates = ''
        
    def get_objects_predicates(self, list_words, list_tags):
        obj_list = []
        pred_list = []
        for ind, elem in enumerate(list_tags):
            if elem == 'B-OBJ':
                obj_list.append(list_words[ind])
            if elem == 'B-PREDFULL':
                pred_list.append(list_words[ind])    
        return obj_list, pred_list
    
    def extract_objects_predicates(self, input_sentence):
        words = create_sequence_from_sentence([input_sentence])
        print (words)
        model = TaggerFactory.load(self.model_path + self.model_name, -1)
        print (model.gpu)
        #model.cuda(device=2)
        #model.gpu = 2
        tags = model.predict_tags_from_words(words)
        print (tags)
        objects, predicates = self.get_objects_predicates(words[0], tags[0])
        print (objects)
        print (predicates)
        self.predicates = predicates
        if len(objects) >= 2:
            self.first_object = objects[0]
            self.second_object = objects[1]
        else:
            print("We have %d objects to compare %s" %(len(objects), objects))
            print ("sentense", words)
            split_sent = words[0]
            print ("split sent", split_sent)
            if 'or' in split_sent:
                print ("have or")
                or_index = split_sent.index('or')
                print (or_index)
                try:
                    obj1 = split_sent[or_index - 1]
                    print ("obj1", obj1)
                    obj2 = split_sent[or_index + 1]
                    print ("obj2", obj2)
                    self.first_object = obj1
                    self.second_object = obj2
                    print ("self.first_object", self.first_object)
                    print ("self.second_object", self.second_object)
                except:
                    self.answ = "We can't recognize two objects for compare" 
            elif 'vs' in split_sent:
                print ("have vs")
                or_index = split_sent.index('vs')
                print (or_index)
                try:
                    obj1 = split_sent[or_index - 1]
                    obj2 = split_sent[or_index + 1]
                    print (obj1, obj2)
                    self.first_object = obj1
                    self.second_object = obj2
                    print ("self.first_object", self.first_object)
                    print ("self.second_object", self.second_object)
                except:
                    self.answ = "We can't recognize two objects for compare" 
            elif 'vs.' in split_sent:
                print ("have vs")
                or_index = split_sent.index('vs')
                print (or_index)
                try:
                    obj1 = split_sent[or_index - 1]
                    obj2 = split_sent[or_index + 1]
                    print (obj1, obj2)
                    self.first_object = obj1
                    self.second_object = obj2
                    print ("self.first_object", self.first_object)
                    print ("self.second_object", self.second_object)
                except:
                    self.answ = "We can't recognize two objects for compare" 
            elif (self.first_object == '' and len(objects) == 1):
                print ("elif len obj", len(objects))
                self.first_object = objects[0]
            else:
                self.answ = "We can't recognize two objects for compare" 
    def get_params(self):
        self.extract_objects_predicates(self.input_str)
        return self.first_object, self.second_object, self.predicates
    
class responser:
    def __init__(self):
        self.URL = 'http://ltdemos.informatik.uni-hamburg.de/cam-api'
        self.proxies = {"http": "http://185.46.212.97:10015/","https": "https://185.46.212.98:10015/",}
        
    def get_response(self, first_object, second_object, fast_search=True, 
               aspects=None, weights=None):
        print ("aspects", aspects)
        print ("weights", weights)
        num_aspects = len(aspects) if aspects is not None else 0
        num_weights = len(weights) if weights is not None else 0
        if num_aspects != num_weights:
            raise ValueError(
                "Number of weights should be equal to the number of aspects")
        params = {
            'objectA': first_object,
            'objectB': second_object,
            'fs': str(fast_search).lower()
        }
        if num_aspects:
            params.update({'aspect{}'.format(i + 1): aspect 
                           for i, aspect in enumerate(aspects)})
            params.update({'weight{}'.format(i + 1): weight 
                           for i, weight in enumerate(weights)})
        print ("get url")
        response = requests.get(url=self.URL, params=params)
        return response
    
def answerer(input_string):
    my_extractor = extractor(input_string)
    my_responser = responser()
    obj1, obj2, predicates = my_extractor.get_params()
    print ("len(obj1), len(obj2)", len(obj1), len(obj2))
    print ("obj1, obj2, predicates", obj1, obj2, predicates)
    if (len(obj1) > 0 and len(obj2) > 0):
        response =  my_responser.get_response(first_object = obj1, second_object = obj2, fast_search=True, aspects = predicates, weights = [1 for predicate in predicates])
        try:
            response_json = response.json()
            my_diviner = diviner()
            my_diviner.create_from_json(response_json)
            answer = my_diviner.generate_advice()
            print ("answer", answer)
            return answer
        except:
            return ("smth wrong in response, please try again")
    elif (len(obj1) > 0 and len(obj2) == 0):
        print ("len(obj1) > 0 and len(obj2) == 0")
        response =  my_responser.get_response(first_object = obj1, second_object = 'and', fast_search=True, aspects = predicates, weights = [1 for predicate in predicates])
        try:
            response_json = response.json()
            my_diviner = diviner()
            my_diviner.create_from_json(response_json)
            answer = my_diviner.generate_advice(is_object_single = True)
            print ("answer", answer)
            return answer  
        except:
            return ("smth wrong in response, please try again")
    else:
        return ("We can't recognize objects for comparision")