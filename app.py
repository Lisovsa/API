from flask import Flask

from parse_results import display

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return 'Welcome to our DXB-BKK flights API'


@app.route('/flights/oneway', methods=['GET'])
def get_oneway():
    return display('RS_ViaOW.xml')


@app.route('/flights/return', methods=['GET'])
def get_return():
    return display('RS_Via-3.xml')


@app.route('/variants/oneway', methods=['GET'])
def oneway_variants():
    functions_list = []
    for function in functions_list:
        return function()


@app.route('/variants/return', methods=['GET'])
def return_variants():
    functions_list = []
    for function in functions_list:
        return function()


@app.route('/difference/', methods=['GET'])
def difference():
    return 'Oneway itinireries fare is different for adult, child, infant. \
            Return itineraries fare per person is fixed (is the same for a child and free for infant).'


if __name__ == '__main__':
    app.run(debug=True)
