import math,os
from flask import Flask, request, jsonify, redirect, session
from flask_cors import CORS

import HelperFunctions.Database as db
import HelperFunctions.Auth  as auth
from HelperFunctions.Database import create_connection

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Enable Cross-Origin Resource Sharing (CORS) for the specified origin
CORS(app,resources={r"/*": {"origins": "http://localhost:4321"}},supports_credentials=True)

# Set a secret key for session management
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")

#================= API Routes ============================
#Test route, returns message
@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({"message":" Hello and welcome to [Website]! "})

#Returns Paginated list of games
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
    games_list = db.getGamesByPage(pageNr,rows)
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

#===============================================
#AUTH
@app.route('/auth/login', methods=['POST'])
def log_in():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    user = auth.checkDetails(username, password)

    if not user:
        # Invalid username or password
        return jsonify({"error": "Invalid username or password"}), 401
    
    # Store in session
    session['user_id'] = user["ID"]
    session['username'] = user["Username"]
    session['is_admin'] = user.get("isAdmin", False)

    # Successful login
    return jsonify({"message": "Login successful", "user": user}), 200

@app.route('/auth/register', methods=['POST'])
def newAccount():    
    username = request.form.get('username')
    passwordHash = request.form.get('password')
    
    response = auth.createAccount(username,passwordHash)
    
    
    if response==True:
        return redirect('http://localhost:4321/login')
    else:
        return jsonify({"message": "Error", "username": response})
    

@app.route('/auth/logout', methods=['POST'])
def log_out():
    session.clear()
    return redirect('http://localhost:4321/')

@app.route('/auth/status', methods=['GET'])
def auth_status():
    if 'user_id' in session:
        return jsonify({
            "logged_in": True,
            "user": {
                "ID": session['user_id'],
                "Username": session['username'],
                "isAdmin": session.get('is_admin', False)
            }
        }), 200
    else:
        return jsonify({"logged_in": False}), 200

#===============================================
#Comments
@app.route("/api/games/<int:gameID>/comments", methods=['GET','POST'])
def comments(gameID):
    if request.method == 'POST':
        
        db.setComment()
        
        return jsonify({"message": "Comment added successfully"}), 201

    elif request.method == 'GET':  # GET request
            
        comments = db.getComments(gameID)
        return jsonify({"comments": comments}), 200
    else:
        return jsonify({"error": "Invalid request method"}), 405

@app.route('/api/users', methods=['GET'])
def get_users():
    users = db.getAllUsers()
    return jsonify({"users": users}), 200

@app.route('/api/user/<int:userID>', methods=['GET'])
def get_user(userID):
    user = db.getUser(userID)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user), 200

if __name__ == '__main__':
    app.run(port=5000,debug=True)
