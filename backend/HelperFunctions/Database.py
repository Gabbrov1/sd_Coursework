import os,pyodbc
from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()

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
    ) AS Consoles,
    (
        SELECT STRING_AGG(AI.ImageURL, ', ')
        FROM ArticleImages AI
        JOIN GamesArticles GA ON GA.ID = AI.ArticleID
        WHERE GA.GameID = g.ID
    ) AS ImageURLs
    FROM Games g
    ORDER BY g.ID
    OFFSET {offset} ROWS
    FETCH NEXT {rows_per_page} ROWS ONLY;
    """
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(sql)

    games_list = []
    for row in cursor.fetchall():
        game = {
            "ID": row.ID,
            "Title": row.GameName,
            "Description": row.GameDescription,
            "Categories": row.Categories,
            "Consoles": row.Consoles,
            "Images": row.ImageURLs.split(', ') if row.ImageURLs else []
        }
        games_list.append(game)

    conn.close()
    return games_list


#NoSQL changed from Firestore to Mongo DB


client = MongoClient("mongodb://localhost:27017")
db = client["SysDevComments"]  

def getGamesMongo(gameID):
        
    games = db["games"]

    print(f"Fetching game with gameID: {gameID} and type: {type(gameID)}")

    game = games.find_one({"gameId": gameID})
    print("Fetched game:", game)
    if not game:
        print(f"Game with gameId={gameID} not found.")
        return None
    
    return game
    

def getComments(gameID: int):
    commentsCol = db["comments"]

    cursor = commentsCol.find({"gameID": gameID}, {"_id": 0})

    comments = list(cursor)

    structured = buildCommentTree(comments)
    return structured


def buildCommentTree(comments):
    
    # Map commentID -> comment dict (with an added children list)
    nodes = {
        c["commentID"]: {**c, "children": []}
        for c in comments
    }

    roots = []

    # Link children to parents
    for node in nodes.values():
        parent_id = node.get("parentID")
        if parent_id is None:
            # Root comment
            roots.append(node)
        else:
            # Reply to another comment
            parent = nodes.get(parent_id)
            if parent:
                parent["children"].append(node)
            else:
                # Parent not found, treat as root (optional behaviour)
                roots.append(node)

    return roots


def getUser(userID: int,username: str = ""):
    usersCol = db["users"]
    user = usersCol.find_one({"userID": userID}, {"_id": 0})
    return user
        
def getAllUsers():
    usersCol = db["users"]

    cursor = usersCol.find({}, {"_id": 0})

    users = list(cursor)
    return users