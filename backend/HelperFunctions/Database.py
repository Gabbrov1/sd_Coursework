import os,pyodbc
from dotenv import load_dotenv

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
    ) AS Consoles
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
            "Consoles": row.Consoles
        }
        games_list.append(game)

    conn.close()
    return games_list
