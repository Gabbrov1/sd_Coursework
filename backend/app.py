from flask import Flask, request, jsonify, redirect
from flask_cors import CORS

import os,pyodbc,math,bcrypt
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
            JOIN GamesArticles GA ON GA.ID = AI.ArticleID
            WHERE GA.GameID = g.ID
        ) AS ImageURLs

        FROM Games g
        OUTER APPLY (
            SELECT TOP (1)
                ga.ID,
                ga.ArticleBody,
                ga.CommentsLink
            FROM GamesArticles ga
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
def log_in():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    user = checkDetails(username, password)

    if not user:
        # Invalid username or password
        return jsonify({"error": "Invalid username or password"}), 401

    # Successful login
    return jsonify({"message": "Login successful", "user": user}), 200

@app.route('/auth/register/', methods=['POST'])
def newAccount():    
    username = request.form.get('username')
    passwordHash = request.form.get('password')
    
    response = createAccount(username,passwordHash)
    if response==True:
        
        return redirect('http://localhost:4321/login')
    else:
        return jsonify({"message": "Error", "username": response})
    
@app.route('/auth/pass-controll/<option>/', methods = ['POST'])
def passManagement():
    username = request.form.get("Username")
    password = request.form.get("password")
    
    
    

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


def checkDetails(username, password):
    conn = create_connection()
    cursor = conn.cursor()

    sql = "SELECT ID, Username, PassHash, isAdmin FROM Users WHERE Username = ?"
    cursor.execute(sql, (username,))
    row = cursor.fetchone()

    if not row:
        return False

    stored_hash = row.PassHash.encode("utf-8")  # bcrypt needs bytes
    entered_pw = password.encode("utf-8")

    if bcrypt.checkpw(entered_pw, stored_hash):
        return {
            "ID": row.ID,
            "Username": row.Username,
            "isAdmin": row.isAdmin
        }
    else:
        return False
    
def setPassword(username,oldPass,newPass):
    sql = """
                UPDATE Users
                SET PasswordHash = ? 
                WHERE Username = ?
                AND PassHash = ?;
            """
    with create_connection as conn:
        with conn.cursor() as cursor:   
            oldHashed = bcrypt.hashpw(oldPass.encode(), bcrypt.gensalt())
            newHashed = bcrypt.hashpw(newPass.encode(), bcrypt.gensalt())
            cursor.execute(sql,(newHashed,username,oldHashed))
    return ("Success",200)

def createAccount(username,password):
    conn = create_connection()
    with conn.cursor() as cursor:  
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        try:
            cursor.execute(
                "INSERT INTO Users (Username, PassHash) VALUES (?, ?)",
                (username, hashed.decode())
            )
            conn.commit()
            return True

        except Exception as e:
            print("Insert failed:", e)
            return False
            
    
             
            

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
