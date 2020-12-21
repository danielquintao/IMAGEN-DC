# IMAGEN-DC
IMAGEN - Data Compiler

Install instruction :

1 - Clone the git in your git folder :
```$ git clone https://github.com/Nicolas-Yax/IMAGEN-DC ```

2 - Fill your DB/folder with .xlsx / .xlsm files.

3 - Compile the DB/ folder into a pickle 3d array :
```$ python compile.y ```

4 - Access the database :
``` import database as db
    db = database.Database()
    db.load_from_pickle("db.p") 
    #Questions names
    db.q
    #Ind ids
    db.ind
    #Timesteps
    db.time
    #Full data table
    db.tf ```
    
