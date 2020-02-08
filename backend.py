#!/usr/bin/env python3

"""be.py: Description."""
from flask import Flask, jsonify, request
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flask_restful import Api, Resource, reqparse
from flask import make_response
from nltk.tokenize import sent_tokenize, word_tokenize
import random
import json
from flask import jsonify
import json

"""Models"""

from generation.generation import diviner
from my_functions import extractor
from my_functions import responser

GPT2Big = diviner('big')

GPT2Small = diviner('small')

Templ = diviner('templates')

Cam = diviner('cam')

extractor = extractor()

class ReverseProxied(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)


app = Flask(__name__)
app.json_encoder = LazyJSONEncoder

reversed = True

if(reversed):
	app.wsgi_app = ReverseProxied(app.wsgi_app)
	template2 = dict(swaggerUiPrefix=LazyString(lambda : request.environ.get('HTTP_X_SCRIPT_NAME', '')))
	swagger = Swagger(app, template=template2)
else:
	swagger = Swagger(app)

api = Api(app)

class Extractor(Resource):
    def post(self):
        input_string   = request.get_data().decode('UTF-8')
        my_extractor = extractor
        my_extractor.from_string(input_string)
        print ("9")
        my_responser = responser()
        print ("9")
        obj1, obj2, predicates = my_extractor.get_params()
        print ("9")
        print ("len(obj1), len(obj2)", len(obj1), len(obj2))
        print ("obj1, obj2, predicates", obj1, obj2, predicates)
        response = make_response(jsonify(first_object = obj1, second_object = obj2, preds = predicates))
        return response
    

class Answerer_cam(Resource):
    def post(self):
        input_string   = request.get_data().decode('UTF-8')
        my_extractor = extractor
        my_extractor.from_string(input_string)
        print ("9")
        my_responser = responser()
        print ("9")
        obj1, obj2, predicates = my_extractor.get_params()
        print ("9")
        print ("len(obj1), len(obj2)", len(obj1), len(obj2))
        print ("obj1, obj2, predicates", obj1, obj2, predicates)
        if (len(obj1) > 0 and len(obj2) > 0):
            response =  my_responser.get_response(first_object = obj1, second_object = obj2, fast_search=True, aspects = predicates, weights = [1 for predicate in predicates])
            try:
                response_json = response.json()
            except:
                del my_extractor, my_responser
                return ("smth wrong in response, please try again")
            try:
                my_diviner = Cam
                print (1)
                my_diviner.create_from_json(response_json, predicates)
                print (2)
            except:
                del my_extractor, my_responser, my_diviner
                return ("smth wrong in diviner, please try again")
            try:
                answer = my_diviner.generate_advice()
                print ("answer0", answer)
            except:
                del my_extractor, my_responser, my_diviner
                answer = "smth wrong in answer generation, please try again"
        elif (len(obj1) > 0 and len(obj2) == 0):
            print ("len(obj1) > 0 and len(obj2) == 0")
            response =  my_responser.get_response(first_object = obj1, second_object = 'and', fast_search=True, aspects = predicates, weights = [1 for predicate in predicates])
            try:
                response_json = response.json()
                my_diviner = Cam
                my_diviner.create_from_json(response_json, predicates)
                answer = my_diviner.generate_advice(is_object_single = True)
                print ("answer1", answer)  
            except:
                del my_extractor, my_responser, my_diviner
                answer = "smth wrong in response, please try again"
        else:
            answer = "We can't recognize objects for comparision"
        response = make_response(jsonify(full_answer = answer))
        response.headers['content-type'] = 'application/json'
        del my_extractor, my_responser, my_diviner
        return response


class AnswererGPT2_big(Resource):
    def post(self):
        input_string   = request.get_data().decode('UTF-8')
        print ("input string ", input_string)
        my_extractor = extractor
        my_extractor.from_string(input_string)
        my_responser = responser()
        obj1, obj2, predicates = my_extractor.get_params()
        print ("len(obj1), len(obj2)", len(obj1), len(obj2))
        print ("obj1, obj2, predicates", obj1, obj2, predicates)
        if (len(obj1) > 0 and len(obj2) > 0):
            response =  my_responser.get_response(first_object = obj1, second_object = obj2, fast_search=True, aspects = predicates, weights = [1 for predicate in predicates])
            try:
                response_json = response.json()
            except:
                del my_extractor, my_responser
                return ("smth wrong in response, please try again")
            try:
                my_diviner = GPT2Big
                print (1)
                my_diviner.create_from_json(response_json, predicates)
                print (2)
            except:
                del my_extractor, my_responser, my_diviner
                return ("smth wrong in diviner, please try again")
            try:
                answer = my_diviner.generate_advice()
                print ("answer0", answer)
            except:
                del my_extractor, my_responser, my_diviner
                answer = "smth wrong in answer generation, please try again"
        elif (len(obj1) > 0 and len(obj2) == 0):
            print ("len(obj1) > 0 and len(obj2) == 0")
            response =  my_responser.get_response(first_object = obj1, second_object = 'and', fast_search=True, aspects = predicates, weights = [1 for predicate in predicates])
            try:
                response_json = response.json()
                my_diviner = GPT2Big
                my_diviner.create_from_json(response_json, predicates)
                answer = my_diviner.generate_advice(is_object_single = True)
                print ("answer1", answer)  
            except:
                del my_extractor, my_responser, my_diviner
                answer = "smth wrong in response, please try again"
        else:
            answer = "We can't recognize objects for comparision"
        response = make_response(jsonify(full_answer = answer))
        del my_extractor, my_responser, my_diviner
        response.headers['content-type'] = 'application/json'
        return response
    
#class extract_objects(Resource)
    
class AnswererGPT2_small(Resource):
    def post(self):
        input_string   = request.get_data().decode('UTF-8')
        print ("input string ", input_string)
        my_extractor = extractor
        my_extractor.from_string(input_string)
        print ("9")
        my_responser = responser()
        print ("9")
        obj1, obj2, predicates = my_extractor.get_params()
        print ("9")
        print ("len(obj1), len(obj2)", len(obj1), len(obj2))
        print ("obj1, obj2, predicates", obj1, obj2, predicates)
        if (len(obj1) > 0 and len(obj2) > 0):
            response =  my_responser.get_response(first_object = obj1, second_object = obj2, fast_search=True, aspects = predicates, weights = [1 for predicate in predicates])
            try:
                response_json = response.json()
                print ("response in small ", response_json)
            except:
                del my_extractor, my_responser
                return ("smth wrong in response, please try again")
            try:
                my_diviner = GPT2Small
                print (1)
                my_diviner.create_from_json(response_json, predicates)
                print (2)
            except:
                del my_extractor, my_responser, my_diviner
                return ("smth wrong in diviner, please try again")
            try:
                answer = my_diviner.generate_advice()
                print ("answer0", answer)
            except:
                del my_extractor, my_responser, my_diviner
                answer = "smth wrong in answer generation, please try again"
        elif (len(obj1) > 0 and len(obj2) == 0):
            print ("len(obj1) > 0 and len(obj2) == 0")
            response =  my_responser.get_response(first_object = obj1, second_object = 'and', fast_search=True, aspects = predicates, weights = [1 for predicate in predicates])
            try:
                response_json = response.json()
                my_diviner = GPT2Small
                my_diviner.create_from_json(response_json, predicates, tp = "small")
                answer = my_diviner.generate_advice(is_object_single = True)
                print ("answer1", answer)  
            except:
                del my_extractor, my_responser, my_diviner
                answer = "smth wrong in response, please try again"
        else:
            answer = "We can't recognize objects for comparision"
        response = make_response(jsonify(full_answer = answer))
        response.headers['content-type'] = 'application/json'
        del my_extractor, my_responser, my_diviner
        return response

class Answerer_templates(Resource):
    def post(self):
        input_string   = request.get_data().decode('UTF-8')
        print ("input string ", input_string)
        my_extractor = extractor
        my_extractor.from_string(input_string)
        print ("9")
        my_responser = responser()
        obj1, obj2, predicates = my_extractor.get_params()
        print ("len(obj1), len(obj2)", len(obj1), len(obj2))
        print ("obj1, obj2, predicates", obj1, obj2, predicates)
        if (len(obj1) > 0 and len(obj2) > 0):
            response =  my_responser.get_response(first_object = obj1, second_object = obj2, fast_search=True, aspects = predicates, weights = [1 for predicate in predicates])
            try:
                response_json = response.json()
            except:
                del my_extractor, my_responser
                return ("smth wrong in response, please try again")
            try:
                my_diviner = Templ
                print (1)
                my_diviner.create_from_json(response_json, predicates)
                print (2)
            except:
                del my_extractor, my_responser, my_diviner
                return ("smth wrong in diviner, please try again")
            try:
                answer = my_diviner.generate_advice()
                print ("answer0", answer)
            except:
                del my_extractor, my_responser, my_diviner
                answer = "smth wrong in answer generation, please try again"
        elif (len(obj1) > 0 and len(obj2) == 0):
            print ("len(obj1) > 0 and len(obj2) == 0")
            response =  my_responser.get_response(first_object = obj1, second_object = 'and', fast_search=True, aspects = predicates, weights = [1 for predicate in predicates])
            try:
                response_json = response.json()
                my_diviner = Templ
                my_diviner.create_from_json(response_json, predicates)
                answer = my_diviner.generate_advice(is_object_single = True)
                print ("answer1", answer)  
            except:
                del my_extractor, my_responser, my_diviner
                answer = "smth wrong in response, please try again"
        else:
            answer = "We can't recognize objects for comparision"
        response = make_response(jsonify(full_answer = answer))
        response.headers['content-type'] = 'application/json'
        del my_extractor, my_responser, my_diviner
        return response


api.add_resource(AnswererGPT2_big, '/gpt_big')
api.add_resource(AnswererGPT2_small, '/gpt_small')
api.add_resource(Answerer_templates, '/templates')
api.add_resource(Answerer_cam, '/cam')
api.add_resource(Extractor, '/extractor')


app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.run(host='0.0.0.0', port=6001,debug=True)


