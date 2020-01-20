import random
import string
import sys
sys.path.insert(0, "/home/vika/cqas_flask/generation/gpt-2-Pytorch")
from text_gen import text_generator_for_out


class diviner:
    def create_from_json(self, response_json, predicates):
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
        if (is_object_single):
            answer_begin = str(self.obj1) + " has undeniable advantages."
            answer_middle = "They are " + aspect_winner_str + '.'
            answer_end = text_generator_for_out(answer_begin)
            return answer
        if (len(aspect_winner_str) == 0 and len(aspect_other_str) == 0):
            answer_begin = self.winner + " is better"
            answer_end = text_generator_for_out(answer_begin)
            answer_end_str = ''.join([answer_end.splitlines()][:3])
            print ("full answer single ", answer_begin + answer_middle + answer_end)
            return answer_begin + answer_middle + answer_end
        
        templ_index = random.randint(1,3)
        print ("winnder:", self.winner, " other:", self.other)
        print ("acpect winner ", aspect_winner_str)
        print ("acpect other ", aspect_other_str)
        
        if (len(self.predicate) == 0):
            self.predicate = 'better'
        
        if (len(self.predicate) > 0):
            print ("self predicate ", self.predicate)
            answer_begin = str('The %s is %s than %s.' %(self.winner, self.predicate, self.other))
            answer_middle = ''
            if (len(aspect_winner_str) > 1):
                answer_middle = 'The reason are ' + aspect_winner_str + '.'
            if (len(aspect_winner_str) > 1):
                answer_middle = 'The reason is ' + aspect_winner_str + '.'
            print ("answer begin: ", answer_begin)
            answer_end = text_generator_for_out(answer_begin)
            print ("answer end str: ", answer_end)
            answer_end_str = ''.join(answer_end.splitlines()[:7])
            print ("answer end str: ", answer_end_str)
            print ("full answer ", answer_begin + answer_middle + answer_end_str)
            return answer_begin + answer_middle + answer_end_str
        
        templ_index = 2
        if (templ_index == 1):
            print('\n')
            error_answer = str(self.winner) + " " + str(self.other) + " acpect winner " + str(self.other) + " acpect other " + str(aspect_other_str)
            try:
                answer_begin = str('The %s is preferable than %s.' %(self.winner, self.other))
                return answer_begin
            except (RuntimeError, TypeError, NameError):
                return error_answer
        elif (templ_index == 2):
            print('\n')
            try: 
                answer = str('In this context, %s is preferable to %s, as it is %s.\n %s is %s.' %(self.winner, self.other, aspect_winner_str, self.other, aspect_other_str))
                return answer
            except (RuntimeError, TypeError, NameError):
                return error_answer
        elif (templ_index == 3):
            print('\n')
            try:
                answer = str('%s is better than %s, because it is %s. \n At the same time, %s is %s.' %(self.winner.capitalize(), self.other, aspect_winner_str, self.other, aspect_other_str))
                return answer
            except (RuntimeError, TypeError, NameError):
                return error_answer