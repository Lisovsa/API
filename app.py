import json

from flask import Flask

from analyze import get_variants, compare
from parse_results import parse

app = Flask(__name__)

ONE_WAY_FILE = 'RS_ViaOW.xml'
RETURN_FILE = 'RS_Via-3.xml'
PARSED_ONE_WAY = parse('RS_ViaOW.xml')
PARSED_RETURN = parse('RS_Via-3.xml')
COMPARE_VALUES = [PARSED_ONE_WAY, PARSED_RETURN, ONE_WAY_FILE, RETURN_FILE]


@app.route('/', methods=['GET'])
def index():
    return 'Welcome to our DXB-BKK flights API'


@app.route('/flights/one_way', methods=['GET'])
def get_one_way():
    return json.dumps(PARSED_ONE_WAY)


@app.route('/flights/return', methods=['GET'])
def get_return():
    return json.dumps(PARSED_RETURN)


@app.route('/variants/one_way', methods=['GET'])
def one_way_variants():
    return json.dumps(get_variants(PARSED_ONE_WAY))


@app.route('/variants/return', methods=['GET'])
def return_variants():
    return json.dumps(get_variants(PARSED_RETURN))


@app.route('/difference/', methods=['GET'])
def get_difference():
    return json.dumps(compare(*COMPARE_VALUES))


if __name__ == '__main__':
    app.run(debug=True)
