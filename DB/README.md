*DB FOLDER*

Put your files here with the following format

ID   | nameA | nameB | nameC | nameD | ... \n
id1  |  dA1  |  dB1  |  dC1  |  dD1  | ...
id2  |  dA2  |  dB2  |  dC2  |  dD2  | ...
id3  |  dA3  |  dB3  |  dC3  |  dD3  | ...
...  |  ...  |  ...  |  ...  |  ...  | ...

where rows are ids of people (int), columns are names of questions or volumetric regions. Data can be anything but will be transformed into
float values (will first try to cast it to float, if it fails it will check in the conv dictionnary [get_table.py file] and if the value
isn't in it it will put np.nan in this spot). Blank values will be put to np.inf (np.inf semantics is similar to a missing value semantics).

Names of files are very important : the format need to be [questionnaire-name]-[timestep](.xlsx|.xlsm) where questionnaire-name is the name
of your questionnaire and timestep is among ['bas','fu1','fu2','fu3'].

The compiler will load all files (get numpy array from excel files et cast non float values), join everything all arrays and align names.
Names of questions in the database will slightly change from questionnaire file original names :

questionnaire original name   ->  database_name
        nameA                 ->  nameA_[questionnaire_name]
        
 This way even if several questions among questionnaires have the same name, database question names are different.
 
 The alignment process aligns questions with the same database name which come from different timesteps. Thus if you have 3 files qn1 qn2 
 and qn3 where qn1 represents baseline data, qn2 fu2 data and qn2 fu3 data you can rename them :
 qn1 -> qn-bas
 qn2 -> qn-fu2
 qn3 -> qn-fu3
 and if qA is the name of the first question in qn-bas it will be renamed qA_qn in the database as the question qA comig from qn questionnaire.
 Once all files are processed and joint the alignment process begins and it will try to check if qA column also exists in qn-fu2 and qn-fu3.
 If it does it will align columns else it will fill missing timesteps from [bas,fu1,fu2,fu3] by np.inf (missing data).
 
 At the end you get a 3d array with all your data aligned and np.inf where you miss data.
