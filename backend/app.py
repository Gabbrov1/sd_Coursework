from flask import Flask, request, jsonify
from flask_cors import CORS

import os,pyodbc,math
from dotenv import load_dotenv


app = Flask(__name__)
load_dotenv() # Load environment variables from .env file

# Enable Cross-Origin Resource Sharing (CORS) for the specified origin
CORS(app,resources={r"/*": {"origins": "http://localhost:4321"}})





#================= API Routes ============================
@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({"message":" Hello and welcome to [Website]! "})

@app.route('/api/games/', methods=['GET'])
def games():
    pageNr = request.args.get('pageNr', default=0, type=int)
    rows = request.args.get('rows', default=10, type=int)
    
    if pageNr < 0:
        pageNr = 0
    if rows < 1:
        rows = 1
    
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Games;")
    total_items = cursor.fetchone()[0]
    
    conn.close()
    games_list = getGamesByPage(pageNr,rows)
    total_pages = math.ceil(total_items / rows) if rows > 0 else 1
    
    return jsonify({
        "total_pages": total_pages,
        "data": games_list
        })

@app.route('/api/games/<int:id>', methods=['GET'])
def game(id):

    sql = """
        SELECT
        g.ID,
        g.GameName as Title,
        g.GameDescription AS Description,

        GA.ArticleBody,
        GA.CommentsLink,

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
        ) AS Consoles,
        
        (
            SELECT STRING_AGG(AI.ImageURL, ', ')
            FROM ArticleImages AI
            JOIN GameArticles GA ON GA.ID = AI.ArticleID
            WHERE GA.GameID = g.ID
        ) AS ImageURLs

        FROM Games g
        OUTER APPLY (
            SELECT TOP (1)
                ga.ID,
                ga.ArticleBody,
                ga.CommentsLink
            FROM GameArticles ga
            WHERE ga.GameID = g.ID
            ORDER BY ga.ID
        ) AS GA
        WHERE g.ID = ?;

    """
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(sql, (id,))

    row = cursor.fetchone()
    if row:
        game = {
            "ID": row.ID,
            "Title": row.Title,
            "Description": row.Description,
            "ArticleBody": row.ArticleBody,

            "CommentsLink": row.CommentsLink,
            "Categories": row.Categories,
            "Consoles": row.Consoles,


            "ImageURLs": row.ImageURLs.split(', ') if row.ImageURLs else []
        }
    
    else:
        
        return jsonify({"error": "Game not found"}), 404
    
    conn.close()

    return jsonify(game),200

@app.route('/api/GET', methods=['GET'])
def GET():
    return jsonify({"message": "Hello, World!"})

@app.route('/auth/login', methods=['POST'])
def LogIn():
    username = request.form.get('username')
    passwordHash = request.form.get('password')
    



    return jsonify({"message": "Received", "username": username}), 200

#================= Supporting Functions ============================

def create_connection():
    # Establish the database connection string using environment variables
    connection_string = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={os.getenv('Server', 'localhost')};"
        f"DATABASE={os.getenv('Database')};"
        f"UID={os.getenv('UserID')};"
        f"PWD={os.getenv('Password')};"
    )
    conn = pyodbc.connect(connection_string)
    return conn


def getGamesByPage(page = 0, rows_per_page=10):    
    offset = page * rows_per_page
    sql = f"""
    Select
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
    OFFSET {offset} ROWS
    FETCH NEXT {rows_per_page} ROWS ONLY;
    """
    conn = create_connection()
    print("Database connection established.")

    cursor = conn.cursor()
    cursor.execute(sql)

    #==============================================
    games_list = []
    for row in cursor.fetchall():
        game = {
            "ID": row.ID,
            "Title": row.GameName,
            "Description": row.GameDescription,
            "Categories": row.Categories,
            "Consoles": row.Consoles
        }
        games_list.append(game)

    #==============================================

    conn.close()
    return games_list

def getGamesByFilters(params):
    params.get('category', None)
    params.get('console', None)
    params.get('searchTerm', None)
    # Implement filtering logic here

    return "This is a temporary debug route."

if __name__ == '__main__':
    app.run(port=5000,debug=True)
