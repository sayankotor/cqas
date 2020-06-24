#!/usr/bin/env python3

"""be.py: Description."""
from flask import Flask, request
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flask_restful import Api
import json
import sys
import configparser
import urllib.parse

"""Front-End"""
from flask import render_template
from json import JSONDecodeError
import requests
from elasticsearch import Elasticsearch
import re
import json
sys.path.insert(0, "/notebook/cqas/")
#from my_functions import answerer

"""Spacy"""
import spacy

# nlp = spacy.load('xx')
# path = "/argsearch/"
path = "./"

config_parser = configparser.ConfigParser()
config_parser.read('config.ini')
config = config_parser['DEV']


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

ES_SERVER = {"host": config["es_host"], "port": int(config["es_port"])}
INDEX_NAME = 'arguments'
es = Elasticsearch(hosts=[ES_SERVER])

reversed = True

if (reversed):
    app.wsgi_app = ReverseProxied(app.wsgi_app)
    template2 = dict(swaggerUiPrefix=LazyString(lambda: request.environ.get('HTTP_X_SCRIPT_NAME', '')))
    swagger = Swagger(app, template=template2)
else:
    swagger = Swagger(app)

api = Api(app)


def create_api_url(endpoint):
    return 'http://' + config["backend_host"] + ":" + config["backend_port"] + "/" + endpoint


class Sender:
    def send(self, text, generation_type):
        print ("generation type", generation_type)
        if generation_type == "template":
            url = create_api_url("templates")
        elif generation_type == "gpt_small":
            url = create_api_url("gpt_small")
        elif generation_type == "gpt_big":
            url = create_api_url("gpt_big")
        elif generation_type == "CAM summarize":
            url = create_api_url("cam")
        elif generation_type == "extractor":
            url = create_api_url("extractor")        

        try:
            print ("url in sender try ", url)
            print ("text in sender try ", text)
            r = requests.post(url, data=text)
            print ("reqerss")
            return r.json()
        except JSONDecodeError:
            print("!!!!", len(text), text)
            pass


sender = Sender()


@app.route('/')
def index():
    if request.url[-1] != '/':
        return redirect(request.url + '/')
    return render_template('template_main.html', title="Argument Entity Visualizer", page="index", path=path)


@app.route('/label_text', methods=['POST', 'GET'])
def background_process_arg():
    print ("answer the question...")
    text = request.form.get('username')
    print ("text", text)
    data = []

    # choose text generation type
    generator = request.form.get('classifier')
    print ("classifier", generator)
    answer = sender.send(text, generator)
    #doc = sender.send(text, classifier)
    print ("doc ttt !!!!", answer)

    return answer


if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host=config["publish_host"], port=int(config["publish_port"]), debug=False)
