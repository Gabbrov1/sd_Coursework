import math, os, bson
import HelperFunctions.Database as db
import HelperFunctions.Auth  as auth


from flask import Flask, request, jsonify, redirect, session,url_for
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Enable Cross-Origin Resource Sharing (CORS) for the specified origin
CORS(app,resources={r"/*": {"origins": r"https://.*\.pages\.dev"}},supports_credentials=True)

# Set a secret key for session management
app.secret_key = os.getenv("SECRET_KEY")

oauth = OAuth(app)

google = oauth.register(
    name="google",
    client_id="GOOGLE_CLIENT_ID",
    client_secret="GOOGLE_CLIENT_SECRET",
    access_token_url="https://oauth2.googleapis.com/token",
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    api_base_url="https://www.googleapis.com/oauth2/v2/",
    client_kwargs={
        "scope": "openid email profile"
    }
)

#================= API Routes ============================

#Returns Paginated list of games
@app.route('/api/games/', methods=['GET'])
def games():
    pageNr = request.args.get('pageNr', default=0, type=int)
    rows = request.args.get('rows', default=10, type=int)
    
    if pageNr < 0:
        pageNr = 0
    if rows < 1:
        rows = 1
    
    conn = db.create_connection()
    with conn.cursor() as cursor:  
        cursor.execute("SELECT COUNT(*) as Total FROM Games;")
        total_items = cursor.fetchone()["Total"]
    conn.close()
        
    games_list = db.getGamesByPage(pageNr,rows)
    total_pages = math.ceil(total_items / rows) if rows > 0 else 1
    
    return jsonify({
        "total_pages": total_pages,
        "data": games_list
        })

@app.route('/api/games/<int:id>', methods=['GET'])
def game(id):
    #TODO: Move function to Database.py and call it here
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
        WHERE g.ID = %s;

    """
    conn = db.create_connection()
    cursor = conn.cursor()
    cursor.execute(sql, (id,))

    row = cursor.fetchone()
    if row:
        game = {
            "ID": row["ID"],
            "Title": row["Title"],
            "Description": row["Description"],
            "ArticleBody": row["ArticleBody"],

            "CommentsLink": row["CommentsLink"],
            "Categories": row["Categories"],
            "Consoles": row["Consoles"],

            "ImageURLs": row["ImageURLs"].split(', ') if row["ImageURLs"] else []
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
    session['user_id'] = user["MongoId"]
    session['username'] = user["Username"]
    session['is_admin'] = user.get("isAdmin", False)

    # Successful login
    return jsonify({"message": "Login successful", "user": user}), 200

@app.route('/auth/register', methods=['POST'])
def newAccount():    
    username = request.form.get('username')
    passwordHash = request.form.get('password')
    
    response = auth.createAccount(username,passwordHash)
    
    if response[0]==True:
        return redirect('/login')
    else:
        return jsonify({"message": "Error", "username": response})
    
@app.route('/auth/delete-account', methods=['POST'])
def delete_account():
    if 'user_id' in session:
        user_id = session['user_id']
        auth.deleteAccount(user_id)
        db.deleteUser(user_id)
        session.clear()
        return jsonify({"message": "Account deleted successfully"}), 200
    else:
        return jsonify({"error": "Not authenticated"}), 401

@app.route('/auth/logout', methods=['POST'])
def log_out():
    session.clear()
    return redirect('/')

@app.route('/auth/status', methods=['GET'])
def auth_status():
    if 'user_id' in session:
        return jsonify({
            "logged_in": True,
            "user": {
                "ID": session['user_id'],
                "Username": session['username'],
                "isAdmin": session.get('is_admin')
            }
        }), 200
    else:
        return jsonify({"logged_in": False}), 200

#===============================================
#Comments
@app.route("/api/games/<int:gameID>/comments", methods=['GET','POST'])
def comments(gameID):
    # Only changing this function to use single return statement due to confusion with multiple return statements and status codes.
    # Other functions can be changed later if needed. Priority Low.
    status={}
    code=0
    
    if request.method == 'POST':
        if session.get("user_id") is None:
            status["error"]="Authentication required"
            code=401
            return jsonify(status),code 
        
         
        commentData = {
            "gameID": gameID,
            "userID": db.to_objId(session.get("user_id")),
            "parentCommentID": db.to_objId(request.json.get("parentCommentID")),
            "commentText": request.json.get("commentText"),
            "createdAt": request.json.get("createdAt")
        }
        db.addComment(commentData)
        status["message"]="Comment added successfully"
        code=201

    elif request.method == 'GET':  # GET request
            
        comments = db.getComments(gameID)
        if comments is None or len(comments) == 0:
            status["error"]="No comments found"
            code=404
        status={"comments":comments}
        code=200
    else:
        status["error"]="Invalid request method"
        code=405
    
    # New method of returning response with status code. Changed due to confusion with multiple return statements.
    return jsonify(status),code 

@app.route('/api/users', methods=['GET'])
def get_users():
    users = db.getAllUsers()
    return jsonify({"users": users}), 200

@app.route('/api/user/<userId>', methods=['GET'])
def get_user(userId):
    user = db.getUser(userId)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user), 200

if __name__ == '__main__':
    app.run(port=5000,debug=True)
