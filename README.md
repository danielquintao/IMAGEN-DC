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
    db.load_from_pickle("db.p")  # or db.load_from_DB_folder()
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
* All the files reporting observations for a time point finish with -bas, -fu1, -fu2, or -fu3 (for baseline, followup 1, followup2, followup3 resp.). Constant data should be put in files without those terminations (data will be repeated for all the timesteps).
* The first column of each file corresponds to the individuals ID (numeric)
* The first row of each file contains headers for each column (AKA question name). The header of the first column will be overwirrten to 'ID' no matter what is its original content.

## Other relevant stuff to know  (or not)
* Since the final table only contains numbers, ```nan```s and ```inf```s, we make it possible to predefine a convention for some categorical values in the argument ```known_words``` of ```load_from_DB_folder()```. The default convention is: {'t': 1, 'f': 0, 'fr': 0, 'en': 1, 'de': 2, 'PARIS': 0, 'NOTTINGHAM': 1, 'BERLIN': 2, 'HAMBURG': 3, 'DRESDEN': 4, 'DUBLIN': 5, 'MANNHEIM': 6, 'LONDON': 7, 'Y': 1, 'N': 0, 'female': 1, 'male': 0, 'E-': 0, 'E': 1, 'E+': 2, 'D-': 3, 'D': 4, 'D+': 5, 'C-': 6, 'C': 7, 'C+': 8, 'B-': 9, 'B': 10, 'B+': 11, 'A-': 12, 'A': 13, 'A+': 14}
