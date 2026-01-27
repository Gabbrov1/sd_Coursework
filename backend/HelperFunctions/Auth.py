import bcrypt
from . import Database as db



def checkDetails(username, password):
    conn = db.create_connection()
    sql = "SELECT Username, PassHash, isAdmin,MongoId FROM Users WHERE Username = %s"
    
    username = username.strip()
    with conn.cursor() as cursor:    
        cursor.execute(sql, (username,))
        row = cursor.fetchone()

        if not row:
            return False

        stored_hash = row["PassHash"].encode("utf-8")
        entered_pw = password.encode("utf-8")

    if bcrypt.checkpw(entered_pw, stored_hash):
        return {
            "MongoId": row["MongoId"],
            "Username": row["Username"],
            "isAdmin": row["isAdmin"]
        }
    else:
        return False

def setPassword(username,oldPass,newPass):
    sql = """
            UPDATE Users
            SET PasswordHash = %s 
            WHERE Username = %s
            AND PassHash = %s;
        """
    conn = db.create_connection()
    with conn.cursor() as cursor:  
         
        oldHashed = bcrypt.hashpw(oldPass.encode("utf-8"), bcrypt.gensalt())
        newHashed = bcrypt.hashpw(newPass.encode("utf-8"), bcrypt.gensalt())
        cursor.execute(sql,(newHashed,username,oldHashed))
        
    return ("Success",200)

def createAccount(username,password):
    conn = db.create_connection()
    with conn.cursor() as cursor:  
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        
        try:
            cursor.execute(
                "INSERT INTO Users (Username, PassHash, MongoId) OUTPUT INSERTED.ID VALUES (%s, %s, %s)",
                (username, hashed.decode())
            )
            conn.commit()
            userID = cursor.fetchone()[0]
            userDetails = {
                "userName": username,
                "quote":"",
                "avatarImage":"",
                "customBackground":"linear-gradient(to top, #ffffff 0%, #000000 100%)"
            }
            
            mongo_result = db.addUser(userDetails)
            
            addMongoID(userID, mongo_result)
            return (True,userID)

        except Exception as e:
            print("Insert failed:", e)
            return (False, -1)

def addMongoID(user_id, mongo_id):
    conn = db.create_connection()
    with conn.cursor() as cursor:  
        try:
            cursor.execute(
                "UPDATE Users SET MongoId = %s WHERE ID = %s",
                (str(mongo_id), user_id)
            )
            conn.commit()
            return True

        except Exception as e:
            print("Update failed:", e)
            return False 

def deleteAccount(username):
    conn = db.create_connection()
    with conn.cursor() as cursor:  
        try:
            cursor.execute(
                "DELETE FROM Users WHERE userName = %s",
                (username,)
            )
            conn.commit()
            return True

        except Exception as e:
            print("Delete failed:", e)
            return False
        
def googleLogin(googleId, email):
    conn = db.create_connection()
    with conn.cursor() as cursor:  
        try:
            # Try find user by Google ID
            user = cursor.execute("SELECT * FROM Users WHERE GoogleId = %s", (googleId,))
            if user:
                return user
            
            # No Google ID%s Try matching email
            user = cursor.execute("SELECT * FROM Users WHERE Email = %s", (email,))
            if user:
                # Link account
                cursor.execute("UPDATE Users SET GoogleId = %s WHERE Email = %s", (googleId, email))
                return cursor.execute("SELECT * FROM Users WHERE GoogleId = %s", (googleId,))
            
            # No user%s create new
            cursor.execute("INSERT INTO Users (Username,Email, GoogleId) VALUES (%s, %s, %s)", (email.split('@')[0], email, googleId))
            return cursor.execute("SELECT * FROM Users WHERE GoogleId = %s", (googleId,))

        except Exception as e:
            print("Google login failed:", e)
            return None