import database
from score_extractor import compute_score,correct

#Creates object
db = database.Database()
#Load database
db.load_from_DB_folder()
#Correct known mistakes from xlsx files
correct(db)
#Compute scores
compute_score(db)
#Save
db.save("db.p")
