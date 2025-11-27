import bcrypt
from .Database import create_connection

def checkDetails(username, password):
    conn = create_connection()
    cursor = conn.cursor()

    sql = "SELECT ID, Username, PassHash, isAdmin FROM Users WHERE Username = ?"
    cursor.execute(sql, (username,))
    row = cursor.fetchone()

    if not row:
        return False

    stored_hash = row.PassHash.encode("utf-8")
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
    conn = create_connection()
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