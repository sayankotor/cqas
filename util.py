import json
import requests

import numpy as np

URL = 'http://ltdemos.informatik.uni-hamburg.de/cam-api'

proxies = {
  "http": "http://165.225.66.34:10015/",
  "https": "https://165.225.66.34:10015/",
}

def get_response(first_object, second_object, fast_search=True, 
               aspects=None, weights=None):
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
    response = requests.get(url=URL, params=params, proxies=proxies)
    return response