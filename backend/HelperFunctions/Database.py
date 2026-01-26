from datetime import datetime
import os,pymssql

from pymongo import MongoClient
from bson import ObjectId


def create_connection():
    conn = pymssql.connect(
    server=os.getenv("Server"),  # e.g., tcp://0.tcp.ngrok.io
    user=os.getenv("UserID"),
    password=os.getenv("Password"),
    database=os.getenv("Database"),
    port=int(os.getenv("MSSQL_PORT", 1433))
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

client = MongoClient(f"{os.getenv('MongoServer','mongodb://localhost:27017')}")
MongoDb = client[f"{os.getenv('MongoDb','SysDevComments')}"]  

usersCol = MongoDb["users"]
gamesCol = MongoDb["games"]
commentsCol = MongoDb["comments"]


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
    
def to_objId(str):
    if isinstance(str, dict):
        return {k: to_objId(v) for k, v in str.items()}
    elif isinstance(str, list):
        return [to_objId(v) for v in str]
    elif str is None:
        return None
    else:
        return ObjectId(str)

def buildCommentTree(comments):
    comments = [to_str(comment) for comment in comments]

    for comment in comments:
        comment["children"] = []

    nodes_by_id = {comment["_id"]: comment for comment in comments}
    roots = []

    for comment in nodes_by_id.values():
        parent_id = comment.get("parentCommentID")

        if parent_id is None:
            roots.append(comment)
            continue

        parent = nodes_by_id.get(parent_id)
        if parent:
            parent["children"].append(comment)
        else:
            roots.append(comment)

    return roots
