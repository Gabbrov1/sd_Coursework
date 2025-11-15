from flask import Flask, request, jsonify
from flask_cors import CORS
app = Flask(__name__)

#=======================================================================================
# Specific route with CORS enabled example. DELETE
#@app.route("/api/data")
#@cross_origin(origin="http://localhost:4321")
#def data():
#    return {"msg": "Hello"}
#=======================================================================================


# Enable Cross-Origin Resource Sharing (CORS) for the specified origin
CORS(app,resources={r"/*": {"origins": "http://localhost:4321"}})

@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({"message":" Hello from Flask!"})

@app.route('/api/GET', methods=['GET'])
def GET():
    return jsonify({"message": "Hello, World!"})

@app.route('/api/POST', methods=['POST'])
def POST():
    return (formatText,200)

def formatText():
    return "This is a temporary debug route."

if __name__ == '__main__':
    app.run(port=5000,debug=True)