# IMAGEN-DC
IMAGEN - Data Compiler

Install instruction :

1 - Clone the git in your git folder :
```$ git clone https://github.com/Nicolas-Yax/IMAGEN-DC ```

2 - Fill your DB/folder with .xlsx / .xlsm files.

3 - Compile the DB/ folder into a pickle 3d array :
```$ python compile.py ```

4 - Access the database :
```python
    import database as db
    db = database.Database()
    db.load_from_pickle("db.p") 
    #Questions names
    db.q
    #Ind ids
    db.ind
    #Timesteps
    db.time
    #Full data table
    db.tf
```
    
## Some assumptions on the files:
* All the files finish with -bas, -fu1, -fu2, or -fu3 (for baseline, followup 1, followup2, followup3 resp.)
* The first column of each file corresponds to the individuals ID (numeric)
* The first row of each file contains headers for each column (AKA question name). The header of the first column will be overwirrten to 'ID' no matter what is its original content.

## Other relevant stuff to know  (or not)
* Some pre-defined categorical values (like "B-", "B", "B+") are replaced by itntegers according to some pre-chosen rule. Take a look at ```get_table.py``` for more details.
