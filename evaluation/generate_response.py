import csv
import pandas as pd
import pickle

from gen import generate_one_answer

import sys
import torch
sys.path.insert(0, "/notebook/cqas")
sys.path.insert(0, "/notebook/cqas/generation/gpt-2-Pytorch")
sys.path.insert(0, "/notebook/cqas/generation/Student")
sys.path.insert(0, "/notebook/cqas/generation/pytorch_transformers")

from generation.generation import diviner
from my_functions1 import extractor
from my_functions import responser

from cam_summarize import load_cam_model
from text_gen_big import load_big_model
from text_gen import load_small_model

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
LM_CAM = load_cam_model(device)
Cam = diviner(tp = 'cam', model = LM_CAM, device = device)
print ("loaded cam")

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
LM_SMALL = load_small_model(device)
GPT2Small = diviner(tp = 'small', model = LM_SMALL, device = device)
print ("loaded gpt2")

#device = torch.device("cuda:6" if torch.cuda.is_available() else "cpu")
#LM_BIG, tokenizer_big = load_big_model(device)
#GPT2Big = diviner(tp = 'big', model = LM_BIG, tokenizer = tokenizer_big, device = device)

Templ = diviner(tp = 'templates', model = '', device = device)

my_extractor = extractor(my_device = 0)
print ("loaded extractor")


def main():
    df = pd.DataFrame(columns=['Object 1', 'Object 2', 'Question', 'Best Answer',  'Answers'])

    with open('yahoo_answers_positive_questions.csv', 'r') as file:
        reader = csv.reader(file)
        for ind, row in enumerate(reader):
            d = {'Object 1': row[0], 'Object 2': row[1], 'Question': row[2], 'Best Answer': row[3],  'Answers': [elem for elem in row[3:]]}
            if (ind > 0):
                df = df.append(d, ignore_index=True)
            
    templ_answ_list = []
    for ind, qw in enumerate(df['Question'].values):
        print (ind, '\n\n')
        answ = generate_one_answer(qw, my_extractor, Cam)
        print (answ)
        templ_answ_list.append(answ)
        
    with open('cam_answers1.pkl', 'wb') as f:
        pickle.dump(templ_answ_list, f)
        
    templ_answ_list = []
    for ind, qw in enumerate(df['Question'].values):
        print (ind, '\n\n')
        answ = generate_one_answer(qw, my_extractor, Templ)
        print (answ)
        templ_answ_list.append(answ)
        
    with open('templ_answers1.pkl', 'wb') as f:
        pickle.dump(templ_answ_list, f)
        
    templ_answ_list = []
    for ind, qw in enumerate(df['Question'].values):
        print (ind, '\n\n')
        answ = generate_one_answer(qw, my_extractor, GPT2Small)
        print (answ)
        templ_answ_list.append(answ)
        
    with open('gpt_answers1.pkl', 'wb') as f:
        pickle.dump(templ_answ_list, f)
                

if __name__ == "__main__":
    main()