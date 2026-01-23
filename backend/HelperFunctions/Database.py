from datetime import datetime
import os,pyodbc

from pymongo import MongoClient
from bson import ObjectId


def create_connection():
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={os.getenv('Server', 'localhost')};"
        f"DATABASE={os.getenv('Database')};"
        f"UID={os.getenv('UserID')};"
        f"PWD={os.getenv('Password')};",
    )
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
    with conn.cursor() as cursor:
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


#NoSQL changed from Firestore to Mongo DB due to cost.

client = MongoClient("mongodb://localhost:27017")
db = client["SysDevComments"]  

usersCol = db["users"]
gamesCol = db["games"]
commentsCol = db["comments"]


def getGames(gameID):

    game = gamesCol.find_one({"gameID": gameID})
    if not game:
        print(f"Game with gameID={gameID} not found.")
        return None
    
    return game
    
def getComments(gameID: int):
    cursor = commentsCol.find({"gameID": gameID})
    print(cursor)
    comments = list(cursor)

    structured = buildCommentTree(comments)
    return structured

def addComment(commentData: dict):
    commentsCol.insert_one(commentData)
    return True
def updateComment(commentID: str, newContent: str):
    now = datetime.now()
    try:
        commentsCol.update_one(
            {"_id": ObjectId(commentID)},
            {"$set": {
                "commentText": newContent,
                "updatedAt": now
                }
             }
        )
        return True
    except Exception as e:
        print(f"Error updating comment:{commentID} Reason: {e}")
        return False

# MAJOR RESTRUCTURE. Now instead of using custom value userID, switching to MongoDB's _id for user identification.
def getUser(userId: str = ""): #prev used ID now uses userName
    if not userId:
        return None
    try:
        obj_id = ObjectId(userId)
    except Exception:
        return None  # invalid ID format
    user = usersCol.find_one({"_id": obj_id})
    user["_id"] = str(user["_id"])
    return user
        
def addUser(userData: dict):
    
    result = usersCol.insert_one(userData)
    newID = result.inserted_id
    return newID

def deleteUser(userID: int):
    try:
        usersCol.delete_one({"userID": userID})
        return True
    except Exception as e:
        print(f"Error deleting user:{userID} Reason: {e}")
        return False

def getAllUsers():
    cursor = usersCol.find({}, {"_id": 0})

    users = list(cursor)
    return users


#Helpers 
def to_str(obj):
    if isinstance(obj, dict):
        return {k: to_str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [to_str(v) for v in obj]
    elif obj is None:
        return None
    else:
        return str(obj)

def buildCommentTree(comments):
    """
    Params:
        Comments List
    Outputs:
        Tree of roots with expanding "Children" if there are any
        
        
    """
    
    # convert ObjectId to string


    comments = [to_str(c) for c in comments]

    # add children array
    for c in comments:
        c["children"] = []

    nodes = {c["_id"]: c for c in comments}
    roots = []

    

    for node in nodes.values():
        parent_id = node.get("parentID")  # get the parentID

        if parent_id is None:
            # Root comment
            roots.append(node)
        else:
            # Find the parent node
            parent = nodes.get(parent_id)
            if parent:
                parent["children"].append(node)
            else:
                # Parent not found, treat as root
                roots.append(node)
                
    return roots