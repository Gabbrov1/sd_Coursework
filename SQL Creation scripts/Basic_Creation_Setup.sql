use sysDevDB


DECLARE @username NVARCHAR(32) = 'webUserAdmin';
DECLARE @password NVARCHAR(32) = '';


CREATE TABLE Users(
	ID INT IDENTITY(0,1) PRIMARY KEY,
	Username NVARCHAR(32) NOT NULL,
	PassHash NVARCHAR(32) NOT NULL,
	ProfileImgLink NVARCHAR(MAX) NULL,
	isAdmin BIT NOT NULL DEFAULT 0

);

CREATE TABLE Categories(
	ID INT IDENTITY(0,1) PRIMARY KEY,
	name NVARCHAR(32) NOT NULL
);

CREATE TABLE Consoles(
	ID INT IDENTITY(0,1) PRIMARY KEY,
	name NVARCHAR(32) NOT NULL
);

CREATE TABLE Games(
	ID INT IDENTITY(0,1) PRIMARY KEY,
	GameName NVARCHAR(64) NOT NULL,
	GameDescription NVARCHAR(MAX) NULL,
);

/* =============| LINK TABLES |=============*/

CREATE TABLE GamesCategories(
	GameID INT NOT NULL,
	CategoryID INT NOT NULL,

	PRIMARY KEY(GameID,CategoryID),

	FOREIGN KEY (GameID) REFERENCES Games(ID),
    FOREIGN KEY (CategoryID) REFERENCES Categories(ID)

);

CREATE TABLE GamesConsoles(
	GameID INT NOT NULL,
	ConsoleID INT NOT NULL,

	PRIMARY KEY(GameID,ConsoleID),

	FOREIGN KEY (GameID) REFERENCES Games(ID),
    FOREIGN KEY (ConsoleID) REFERENCES Consoles(ID)

);

CREATE TABLE GamesArticles(
	ID INT IDENTITY(0,1) PRIMARY KEY,
	GameID INT NOT NULL,
	ArticleBody NVARCHAR(MAX) NOT NULL,
	CommentsLink NVARCHAR(MAX) NULL
);

CREATE TABLE ArticleImages(
	ID INT IDENTITY(0,1) PRIMARY KEY,
	ArticleID INT NOT NULL,
	ImageURL NVARCHAR(MAX) NOT NULL,

	FOREIGN KEY (ArticleID) REFERENCES GamesArticles(ID)

);


----------------------------------------
--   SQL User Creation Script		  --
----------------------------------------

DECLARE @username NVARCHAR(32) = '';
DECLARE @password NVARCHAR(32) = '';
DECLARE @sql NVARCHAR(MAX);


-- 1. Create SQL Login
SET @sql = 'CREATE LOGIN [' + @username + '] WITH PASSWORD = ''' + @password + ''';';
EXEC(@sql);


-- 2. Create User in Database and Assign Roles
SET @sql = '
USE sysDevDB;
CREATE USER [' + @username + '] FOR LOGIN [' + @username + '];
ALTER ROLE db_datareader ADD MEMBER [' + @username + '];
ALTER ROLE db_datawriter ADD MEMBER [' + @username + '];';

EXEC(@sql);

ALTER TABLE Users ADD MongoId VARCHAR(24);