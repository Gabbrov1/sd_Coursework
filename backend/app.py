from flask import Flask, request, jsonify
from flask_cors import CORS

import os,pyodbc
from dotenv import load_dotenv


app = Flask(__name__)
load_dotenv() # Load environment variables from .env file
#=======================================================================================
# Specific route with CORS enabled example. DELETE
#@app.route("/api/data")
#@cross_origin(origin="http://localhost:4321")
#def data():
#    return {"msg": "Hello"}
#=======================================================================================


# Enable Cross-Origin Resource Sharing (CORS) for the specified origin
CORS(app,resources={r"/*": {"origins": "http://localhost:4321"}})

global conn

connection_string = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={os.getenv('Server', 'localhost')};"
    f"DATABASE={os.getenv('Database')};"
    f"UID={os.getenv('UserID')};"
    f"PWD={os.getenv('Password')};"
)# Establish the database connection using environment variables

conn = pyodbc.connect(connection_string)
print("Database connection established.")


@app.route('/api/hello', methods=['GET'])
def hello(username):

    return jsonify({"message":" Hello Chicken Nugget! "})

@app.route('/api/games', methods=['GET'])
def games():
    return getGamesByPage(0)


def getGamesByPage(page):
    sql = f"""
    SELECT TOP 10
    g.ID,
    g.GameName,
    g.GameDescription,
    (
        SELECT STRING_AGG(c.name, ', ')
        FROM Categories c
        JOIN GamesCategories gc ON gc.CategoryID = c.ID
        WHERE gc.GameID = g.ID
    ) AS Categories,
    (
        SELECT STRING_AGG(con.name, ', ')
        FROM Consoles con
        JOIN GamesConsoles gcon ON gcon.ConsoleID = con.ID
        WHERE gcon.GameID = g.ID
    ) AS Consoles
    FROM Games g
    ORDER BY g.ID
    OFFSET {page*10} ROWS
    FETCH NEXT 10 ROWS ONLY;
    """
    conn.open()
    cursor = conn.cursor()
    cursor.execute(sql)

    #==============================================
    games_list = []
    for row in cursor.fetchall():
        game = {
            "ID": row.ID,
            "Title": row.Name,
            "Description": row.GameDescription,
            "Categories": row.Categories,
            "Consoles": row.Consoles
        }
        games_list.append(game)

    #==============================================

    conn.close()
    return jsonify( games_list)

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
