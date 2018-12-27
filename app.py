import json

from flask import Flask

from analyze import get_variants
from parse_results import parse

app = Flask(__name__)

parsed_return = parse('RS_Via-3.xml')
parsed_oneway = parse('RS_ViaOW.xml')


@app.route('/', methods=['GET'])
def index():
    return 'Welcome to our DXB-BKK flights API'


@app.route('/flights/oneway', methods=['GET'])
def get_oneway():
    return json.dumps(parsed_oneway)


@app.route('/flights/return', methods=['GET'])
def get_return():
    return json.dumps(parsed_return)


@app.route('/variants/oneway', methods=['GET'])
def oneway_variants():
    return json.dumps(get_variants(parsed_oneway))


@app.route('/variants/return', methods=['GET'])
def return_variants():
    return json.dumps(get_variants(parsed_return))


@app.route('/difference/', methods=['GET'])
def difference():
    return '"RS_ViaOW.xml" includes only oneway flights from DXB to BKK both direct and indirect with different ' \
           'fares for an adult, a child, an infant on 2018-10-27. "RS_Via-3.xml" includes return option for dates: ' \
           '2018-10-22 and 2018-10-30, route DXB - BKK, BKK - DXB. For all return itineraries fare per adult only is ' \
           'given therefore we can assume that the fare is fixed (is the same for a child and free for an infant).' \
           'So, overall difference: oneway - return, dates of flights, pricing terms.'


if __name__ == '__main__':
    app.run(debug=True)
