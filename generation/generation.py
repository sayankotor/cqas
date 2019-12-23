import random
import string


class diviner:
    def create_from_json(self, response_json):
        self.obj1 = response_json['object1']['name']
        self.obj2 = response_json['object2']['name']
        if self.obj1 == response_json['winner']:
            self.winner = self.obj1
            self.winner_aspects = response_json['extractedAspectsObject1']
            self.winner_aspects = [elem for elem in self.winner_aspects if 'er' in elem]
            self.other = self.obj2
            self.other_aspects = response_json['extractedAspectsObject2']
            self.other_aspects = [elem for elem in self.other_aspects if 'er' in elem]
        else:
            self.winner = self.obj2
            self.winner_aspects = response_json['extractedAspectsObject2']
            self.winner_aspects = [elem for elem in self.winner_aspects if 'er' in elem]
            self.other = self.obj1
            self.other_aspects = response_json['extractedAspectsObject1']
            self.other_aspects = [elem for elem in self.other_aspects if 'er' in elem]
            
    def generate_advice(self):
        aspect_winner_str = ', '.join(self.winner_aspects)
        aspect_other_str = ', '.join(self.other_aspects)
        templ_index = random.randint(1,3)
        print ("winnder:", self.winner, " other:", self.other)
        print ("acpect winner ",aspect_winner_str)
        print ("acpect other ", aspect_other_str)
        if (templ_index == 1):
            print('\n')
            try:
                print ('The %s is preferable,because it is %s. \n Otherwise, %s is' %(self.winner , aspect_winner_str, self.other, aspect_other_str))
            except (RuntimeError, TypeError, NameError):
                print (self.winner, self.other)
                print ("acpect winner ",aspect_winner_str)
                print ("acpect other ", aspect_other_str)
        elif (templ_index == 2):
            print('\n')
            try: 
                print ('In this context, %s are preferable to %s, as it is %s.\n %s are %s' %(self.winner, self.other, aspect_winner_str, self.other.capitalize(), aspect_other_str))
            except (RuntimeError, TypeError, NameError):
                print ("acpect winner ",aspect_winner_str)
                print ("acpect other ", aspect_other_str)
        elif (templ_index == 3):
            print('\n')
            try:
                print ('%s is better than %s, because it is %s. \n At the same time, %s is %s' %(self.winner.capitalize(), self.other, aspect_winner_str, self.other, aspect_other_str))
            except (RuntimeError, TypeError, NameError):
                print (self.winner, self.other)
                print ("acpect winner ",aspect_winner_str)
                print ("acpect other ", aspect_other_str)