# Systen Development Coursework
---
This project has been the assignment completed for Bournemouth university, under the system development Assignment.

For this project, we were assigned the task of designing and developing a full website from end to end, with custom REST API and implementation of at least 1 Google services API integration.

This website was done using:
 - Astro and React frameworks, in order to provide a finished project that would be static yet still interactive. Typescript has been used mostly due to my more extensive experience in strongly typed languages.
 - The backend of the application has been made using Flask in combination with MongoDB and MSSQL. Another requirement for the successfull completion of this project has been the use of 2 differing database types, namely SQL and NoSQL database types. in my project, the SQL Databse is used to store user details as well as general project information and the MongoDB database is used in order to store customisable aspects of the website.
 - In terms of API usage, this Project uses a standard Flask, REST API, to communicate with the databses and website.


Release:
One of the optional requirements for our assignment was the public release of the final projects.

 - This was accomplished by using NGrok to expose the local databases by port, which was done in order to allow for cheap/ free hosting of the databses, since MSSQL databses tend to be quite expensive to host.
 - The frontend website was released using CloudFlare pages, which allowed for free hosting.
 - The backend of the website was hosted using Render free hosting.

The API used for this implementation was the Google OAuth method, which allowed for users to sign up/ sign in using their Google accounts. This was chosen due to its compatibility with the website and since it would allow for easy access to their accounts, as it has become the default practice to allow users to sign in with their google/Apple accounts.

The biggest issue I have encountered during the development of this project has been the Login system and allowing it to work correctly with the CORS system. Due to the time limitations on the project, I wasn't able to solve this issue. The current issue makes the webpage reset itself immediately after login, esesntially reseting logins.
