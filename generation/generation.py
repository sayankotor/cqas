import random
import string


class diviner:
    def create_from_json(self, response_json):
        self.obj1 = response_json['object1']['name']
        self.obj2 = response_json['object2']['name']
        if self.obj1 == response_json['winner']:
            self.winner = self.obj1
            self.winner_aspects = response_json['extractedAspectsObject1'][:4]
            #self.winner_aspects = [elem for elem in self.winner_aspects if 'er' in elem]
            self.other = self.obj2
            self.other_aspects = response_json['extractedAspectsObject2'][:4]
            #self.other_aspects = [elem for elem in self.other_aspects if 'er' in elem]
        else:
            self.winner = self.obj2
            self.winner_aspects = response_json['extractedAspectsObject2']
            #self.winner_aspects = [elem for elem in self.winner_aspects if 'er' in elem]
            self.other = self.obj1
            self.other_aspects = response_json['extractedAspectsObject1']
            #self.other_aspects = [elem for elem in self.other_aspects if 'er' in elem]
        print ("aspects ", self.winner_aspects, self.other_aspects)
            
    def generate_advice(self, is_object_single = False):
        aspect_winner_str = ', '.join(self.winner_aspects)
        aspect_other_str = ', '.join(self.other_aspects)
        if (is_object_single):
            answer = str(self.obj1) + " has undeniable advantages." + "It is " + aspect_winner_str 
            return answer
        if (len(aspect_winner_str) == 0 and len(aspect_other_str) == 0):
            return self.winner + " is better. " + "we don't know why"
        
        elif (len(aspect_winner_str) != 0 and len(aspect_other_str) == 0):
            return self.winner + " is better. " + self.winner + " is " + aspect_winner_str
            
        elif (len(aspect_winner_str) == 0 and len(aspect_other_str) != 0):
            return self.winner + " is better. But " + self.other + " is " + aspect_other_str
        
        templ_index = random.randint(1,3)
        print ("winnder:", self.winner, " other:", self.other)
        print ("acpect winner ", aspect_winner_str)
        print ("acpect other ", aspect_other_str)
        if (templ_index == 1):
            print('\n')
            error_answer = str(self.winner) + " " + str(self.other) + " acpect winner " + str(self.other) + " acpect other " + str(aspect_other_str)
            try:
                answer = str('The %s is preferable,because it is %s. \n Otherwise, %s is %s .' %(self.winner , aspect_winner_str, self.other, aspect_other_str))
                return answer
            except (RuntimeError, TypeError, NameError):
                return error_answer
        elif (templ_index == 2):
            print('\n')
            try: 
                answer = str('In this context, %s is preferable to %s, as it is %s.\n %s is %s .' %(self.winner, self.other, aspect_winner_str, self.other, aspect_other_str))
                return answer
            except (RuntimeError, TypeError, NameError):
                return error_answer
        elif (templ_index == 3):
            print('\n')
            try:
                answer = str('%s is better than %s, because it is %s. \n At the same time, %s is %s' %(self.winner.capitalize(), self.other, aspect_winner_str, self.other, aspect_other_str))
                return answer
            except (RuntimeError, TypeError, NameError):
                return error_answer