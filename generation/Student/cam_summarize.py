import numpy as np
import torch
import torch.nn.functional as F
import torch.nn as nn
from pytorch_pretrained_bert import *
import matplotlib.pyplot as plt

import os
current_directory_path = os.path.dirname(os.path.realpath(__file__))


from tokenizer_custom_bert import BertTokenizer

import networkx as nx

def init_pagerank(scores):
    weights = {}
    n_edges = {}
    for i, j, w in scores:
        prev_score, prev_n = weights.get(i, 0.0), n_edges.get(i, 0)
        weights[i] = w + prev_score
        n_edges[i] = 1 + prev_n
        prev_score, prev_n = weights.get(j, 0.0), n_edges.get(j, 0)
        weights[j] = w + prev_score
        n_edges[j] = 1 + prev_n
    for k in weights:
        v = weights[k]
        weights[k] = v/n_edges[k]
    return weights


def extract_top(scores, k = 10, weighted_init = False):
    g = nx.Graph()
    g.add_weighted_edges_from(scores)
    if weighted_init:
        pr = nx.pagerank(g, nstart = init_pagerank(scores))
    else:
        pr = nx.pagerank(g)
    idxes = sorted(pr, key = lambda x: -pr[x])[:k]
    return idxes

def write_sentences(sample, sentences = None):
    if sentences is None:
        sentences = []
    for s in sample['object1']['sentences']:
        sentences.append(s['text'] + '\n')
    for s in sample['object2']['sentences']:
        sentences.append(s['text'] + '\n')
    return sentences

def similarity(s1, s2):
    return s1.dot(s2)/np.linalg.norm(s1,2)/np.linalg.norm(s2, 2)

class RNNModel(nn.Module):
    """Container module with an encoder, a recurrent module, and a decoder."""

    def __init__(self, ntoken, ninp = 768, nhid = 512, nlayers=1, dropout=0.5, tie_weights=False):
        super(RNNModel, self).__init__()
        self.drop = nn.Dropout(dropout)
        self.encoder = nn.Embedding(ntoken, ninp)
        self.rnn = nn.LSTM(ninp, nhid, nlayers, dropout=dropout)
        self.decoder = nn.Linear( nhid, ntoken)

        self.init_weights()

        self.nhid = nhid
        self.nlayers = nlayers

    def init_weights(self):
        initrange = 0.1
        self.decoder.bias.data.zero_()
        self.decoder.weight.data.uniform_(-initrange, initrange)

    def forward(self, input, hidden, input_lengths = None):
        emb = self.drop(self.encoder(input))
        if input_lengths is not None:
            emb = torch.nn.utils.rnn.pack_padded_sequence(emb, input_lengths, enforce_sorted = True)
            outputs, hidden = self.rnn(emb, hidden)
            output, _ = torch.nn.utils.rnn.pad_packed_sequence(outputs)
        else:
            output, hidden = self.rnn(emb, hidden)
        output = self.drop(output)
        decoded = self.decoder(output)
        return decoded, hidden

    def init_hidden(self, bsz):
        weight = next(self.parameters())
        return (weight.new_zeros(self.nlayers, bsz, self.nhid),
                weight.new_zeros(self.nlayers, bsz, self.nhid))
        

def detach_hidden(hidden):
    return (hidden[0].detach(),
            hidden[1].detach())

def prune_graph(scores):
    mean = np.array([s[2] for s in scores]).mean()
    pruned = []
    for s in scores:
        if s[2] > mean:
            pruned.append(s)
    return pruned

def cam_summarize(input_json):
    print ("cam_summarize")
    #print (input_json)
    tokenizer = BertTokenizer(vocab_file = current_directory_path + 'vocab.txt')
    
    print (11)
    k = 10
    prune = True
    exclude_common = True
    weighted_init = True
    #stemmer = SnowballStemmer(language='english')
    print (11)
    device = torch.device("cuda")
    print (11)
    LM = RNNModel(30522, nlayers=2, dropout = 0.0)
    print (11)
    LM.load_state_dict(torch.load(current_directory_path + 'wikitext_lm_finetuned'))
    print (12)
    LM = LM.to(device)
    
    raw_sentences = write_sentences(input_json)
    summaries = []
    sentences = []
    for s in raw_sentences:
        s = ["[CLS]"] + tokenizer.tokenize(s) + ["[SEP]"]
        sentences.append(tokenizer.convert_tokens_to_ids(s))
    print (13)
    hiddens = []
    for s in sentences:
        hidden = LM.init_hidden(1)
        batch = torch.LongTensor([s]).transpose(0, 1).to(device)
        preds, h = LM(batch, hidden, input_lengths = None)
        hiddens.append(h[1].view(-1).cpu().detach().numpy())

    scores = []
    print (14)
    for i in range(len(sentences)):
        for j in range(len(sentences)):
            scores.append((i, j, similarity(hiddens[i], hiddens[j])))

    if prune:
        scores = prune_graph(scores)

    top_k = extract_top(scores, k = k, weighted_init = weighted_init)

    summaries.append([raw_sentences[i] for i in top_k])
    return summaries[0]