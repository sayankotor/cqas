import random
import string
import sys
sys.path.insert(0, "/notebook/cqas/generation/gpt-2-Pytorch")
sys.path.insert(0, "/notebook/cqas/generation/Student")
sys.path.insert(0, "/notebook/cqas/generation/pytorch_transformers")
#from text_gen import text_generator_for_out
from text_gen_big import text_generator_for_out_big
from text_gen import text_generator_for_out
from cam_summarize import cam_summarize
from template_generation import generate_template


class diviner:
    def __init__(self, model, device, tp = "big", tokenizer = ''):
        self.type = tp
        self.model = model
        self.device = device
        self.tokenizer = tokenizer
    
    def create_from_json(self, response_json, predicates):
        self.json = response_json
        self.obj1 = response_json['object1']['name']
        self.obj2 = response_json['object2']['name']
        print ("create fro json predicates", predicates)
        if (len(predicates) > 0):
            self.predicate = predicates[0]
        else:
            self.predicate =''
        print ("create fro json self.predicates", self.predicate)
        if self.obj1 == response_json['winner']:
            self.winner = self.obj1
            self.winner_aspects = response_json['extractedAspectsObject1'][:4]
            #self.winner_aspects = [elem for elem in self.winner_aspects if 'er' in elem]
            self.other = self.obj2
            self.other_aspects = response_json['extractedAspectsObject2'][:4]
            #self.other_aspects = [elem for elem in self.other_aspects if 'er' in elem]
        else:
            self.winner = self.obj2
            self.winner_aspects = response_json['extractedAspectsObject2'][:4]
            #self.winner_aspects = [elem for elem in self.winner_aspects if 'er' in elem]
            self.other = self.obj1
            self.other_aspects = response_json['extractedAspectsObject1'][:4]
            #self.other_aspects = [elem for elem in self.other_aspects if 'er' in elem]
        print ("aspects ", self.winner_aspects, self.other_aspects)
            
    def generate_advice(self, is_object_single = False):
        aspect_winner_str = ', '.join(self.winner_aspects)
        aspect_other_str = ', '.join(self.other_aspects)
        
        print ("winnder:", self.winner, " other:", self.other)
        print ("acpect winner ", aspect_winner_str)
        print ("acpect other ", aspect_other_str)
        print ("type ", self.type)
        
        if (is_object_single):
            answer_begin = str(self.obj1) + " has undeniable advantages. "
            answer_begin = answer_begin + "They are " + aspect_winner_str + '.'
        
            if (len(aspect_winner_str) == 0 and len(aspect_other_str) == 0):
                answer_begin = self.winner + " is better"
        
        templ_index = random.randint(1,3)
        print ("winnder:", self.winner, " other:", self.other)
        print ("acpect winner ", aspect_winner_str)
        print ("acpect other ", aspect_other_str)
        
        if (not is_object_single):
            if (len(self.predicate) == 0):
                self.predicate = 'better'

            if (len(self.predicate) > 0):
                print ("self predicate ", self.predicate)
                answer_begin = str('The %s is %s than %s. ' %(self.winner, self.predicate, self.other))
                answer_middle = ''
                if (len(aspect_winner_str) > 1):
                    answer_middle = 'The reason are ' + aspect_winner_str + '. '
                if (len(aspect_winner_str) > 1):
                    answer_middle = 'The reason is ' + aspect_winner_str + '. '
                answer_begin = answer_begin + answer_middle
                print ("answer begin: ", answer_begin)
                print ("self type", self.type)

                if (self.type == "templates"):
                    response_json = self.json
                    print ("gen templates")
                    comparing_pair = {}
                    if (response_json['object1']['name'] == response_json['winner']):
                        comparing_pair['winner_aspects'] = response_json['extractedAspectsObject1'][:4]
                        comparing_pair['loser_aspects'] = response_json['extractedAspectsObject2'][:4]
                        comparing_pair['winner'] = response_json['object1']['name']
                        comparing_pair['loser'] = response_json['object2']['name']
                    else:
                        comparing_pair['winner_aspects'] = response_json['extractedAspectsObject2'][:4]
                        comparing_pair['loser_aspects'] = response_json['extractedAspectsObject1'][:4]
                        comparing_pair['winner'] = response_json['object2']['name']
                        comparing_pair['loser'] = response_json['object1']['name']
                    print ("gen templates 2")
                    answer_begin = generate_template(comparing_pair, mode="extended")
                    print ("gen templates 2", answer_begin)
                    answer_end = ''
                    answer_end_str = ''
                
                    
                elif (self.type == "small"):
                    print ("answer_begin small", answer_begin)
                    answer_end = text_generator_for_out(answer_begin, self.model, device = self.device)
                    answer_end_str = ''.join(answer_end.splitlines()[:7])
                    print ("answer_end", answer_end)
                elif (self.type == "big"):
                    print ("answer_begin big", answer_begin)
                    answer_end = text_generator_for_out_big(answer_begin, self.model, self.tokenizer)
                    print ("answer_end", answer_end)
                    answer_end_str = ''.join(answer_end.splitlines()[:7])
                    print ("answer_end", answer_end_str)
                elif (self.type == 'cam'):
                    print ("answer_begin cam", answer_begin)
                    answer_end = cam_summarize(self.json, self.model, self.device)[:7]
                    answer_end_str = ''.join(answer_end)
                    print ("answer_end cam", answer_end)

                print ("full answer ", answer_begin + answer_middle + answer_end_str)
        return answer_begin + answer_end_str
