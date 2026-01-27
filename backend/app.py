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
CORS(
    app,
    resources={r"/*": {"origins": [r"https://.*\.pages\.dev", "http://localhost:4321"]}},
    supports_credentials=True
)

# Set a secret key for session management
app.secret_key = os.getenv("SECRET_KEY","dev-secret-key")

app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE="None",
)

oauth = OAuth(app)

google = oauth.register(
    name="google",
    client_id=os.getenv("Google_Client"),
    client_secret=os.getenv("Google_Secret"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile"
    }
)

#================= API Routes ============================

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "OK"}), 200

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
    session['user_id'] = user.get("MongoId")
    session['username'] = user.get("Username")
    session['is_admin'] = user.get("isAdmin", False)

    # Successful login
    return jsonify({"message": "Login successful", "user": user}), 200

@app.route('/auth/register', methods=['POST'])
def newAccount():    
    username = request.form.get('username')
    passwordHash = request.form.get('password')
    
    response = auth.createAccount(username,passwordHash)
    
    if response[0]==True:
        return redirect(url_for('log_in'), code=307)  # Use 307 to preserve the POST method
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
    session.pop("user", None)
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
    
@app.route('/auth/google', methods=['GET'])
def google_login():
    redirect_uri = url_for("google_authorize", _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route("/auth/google/authorize")
def google_authorize():
    token = google.authorize_access_token()
    user_info = token["userinfo"]

    
    googleLogin = auth.googleLogin(
        user_info["sub"],
        user_info["email"]
    )
    if googleLogin is None:
        return jsonify({"error": "Google login failed"}), 401
    
    
    
    session["user"] = {
        "id": googleLogin.get("MongoId"),
        "email": user_info.get("email"),
        "name": user_info.get("name"),
        "picture": user_info.get("picture"),
        "username": googleLogin.get("Username")
    }
    session["logged_in"]=True
    
    return redirect("https://sd-bu25.pages.dev/auth/Account")
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
