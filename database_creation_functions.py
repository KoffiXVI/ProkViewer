import os
import sqlite3
import io
import tarfile
import shutil
import requests as req
import zipfile as zipf
from tkinter import messagebox
from global_defaults import error_handler
from database_maintenance_functions import table_operation
from database_constants import *


def create_prok_database(db_path: str=DB_STORE_PATH, db_name:str = PROK_DB_PATH, force:bool=False):
    if os.path.exists(db_path):
        if not force:
            message = "database already existing. Set force=True to proceed nonetheless"
            return (False, message)
        shutil.rmtree(db_path)
        #os.remove(db_name)
    
    if not os.path.exists(db_path):
        os.makedirs(db_path)

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute(f"CREATE TABLE IF NOT EXISTS {PROK_TABLE} (\
               {NAME} TEXT,\
               {TAXID} INT,\
               {SIZE} REAL,\
               {GENES} INT,\
               {PROTEINS} INT,\
               {RELEASE_DATE} DATE,\
               {MODIFY_DATE} DATE,\
               {ASSEMBLY} TEXT,\
               {REFERENCE} TEXT,\
               {LINK} TEXT,\
               CONSTRAINT prok_pkey PRIMARY KEY({TAXID}, {ASSEMBLY})\
               ) WITHOUT ROWID; ") 
    
    #INTEGER PRIMARY KEY must be written in full to make use of the column as ROWID (as far as i saw with my testing)
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {LOG_TABLE}(\
                   {LOG_ID} INTEGER PRIMARY KEY,\
                   {DATE} DATE DEFAULT current_date,\
                   {Q_NAME} TEXT NOT NULL,\
                   {Q_ID} INT NOT NULL,\
                   {Q_ASSEMBLY} TEXT NOT NULL,\
                   {S_NAME} TEXT NOT NULL,\
                   {S_ID} INT NOT NULL,\
                   {S_ASSEMBLY} TEXT NOT NULL,\
                   {EVALUE} TEXT NOT NULL,\
                   {WORD_SIZE} INT NOT NULL,\
                   {G_OPEN} INT NOT NULL,\
                   {G_EXTEND} INT NOT NULL,\
                   {MATRIX} TEXT NOT NULL,\
                   {LOOKUP_TABLE} REAL NOT NULL\
                   );")
    
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {RES_TABLE}(\
                   {RES_ID} INTEGER PRIMARY KEY,\
                   {LOG_ID} INTEGER REFERENCES {LOG_TABLE}({LOG_ID}) ON DELETE CASCADE,\
                   {Q_SEQID} TEXT NOT NULL,\
                   {S_SEQID} TEXT NOT NULL,\
                   {P_IDENT} REAL NOT NULL,\
                   {LENGTH} INT NOT NULL,\
                   {MISMATCH} INT NOT NULL,\
                   {GAPS} INT NOT NULL,\
                   {Q_START} INT NOT NULL,\
                   {Q_END} INT NOT NULL, \
                   {S_START} INT NOT NULL, \
                   {S_END} INT NOT NULL, \
                   {EVALUE} REAL NOT NULL,\
                   {BITSCORE} REAL NOT NULL\
                   ); ")
    
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {NODES_TABLE}(\
                   {TAXID} INT PRIMARY KEY,\
                   {PARENT_TAXID} INT\
                   ) WITHOUT ROWID; ")
    
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {NAMES_TABLE}(\
                   {TAXID} INT PRIMARY KEY REFERENCES {NODES_TABLE}({TAXID}) ON DELETE CASCADE,\
                   {NAME} TEXT\
                   ) WITHOUT ROWID; ")
    
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {COG_FUNC_TABLE}(\
                   {FUNC_CODE} VARCHAR(2) PRIMARY KEY,\
                   {FUNC_DESC} TEXT\
                   ) WITHOUT ROWID; ")
    
    
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {COG_NAMES_TABLE}(\
                   {NAME_CODE} VARCHAR(8) PRIMARY KEY,\
                   {FUNC_CODE} VARCHAR(2), \
                   {COG_DESC} TEXT\
                   ) WITHOUT ROWID; ")
    
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {COG_LOG_TABLE}(\
                   {LOG_ID} INTEGER PRIMARY KEY,\
                   {DATE} DATE DEFAULT current_date,\
                   {Q_NAME} TEXT NOT NULL,\
                   {Q_ID} INT NOT NULL,\
                   {Q_ASSEMBLY} TEXT NOT NULL,\
                   {EVALUE} TEXT NOT NULL\
                   );")
    
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {COG_RES_TABLE}(\
                   {RES_ID} INTEGER PRIMARY KEY,\
                   {LOG_ID} INTEGER REFERENCES {COG_LOG_TABLE}({LOG_ID}) ON DELETE CASCADE,\
                   {Q_ASSEMBLY} TEXT NOT NULL,\
                   {S_TITLE} TEXT NOT NULL,\
                   {EVALUE} REAL NOT NULL\
                   ); ")
    
    conn.commit()
    #conn.close()
    return conn

def create_temp_database(connector:sqlite3.Connection|None=None, db_name:str = PROK_DB_PATH):
    if not os.path.exists(db_name):
        e = FileNotFoundError("no database existing for operation")
        error_handler(e)
        raise e
    
    connector = connector if connector is not None else sqlite3.connect(db_name) 

    prokaryote_command = f"CREATE TEMPORARY TABLE {TEMP_PROK_TABLE} AS SELECT * FROM {PROK_TABLE} ;"
    nodes_command = f"CREATE TEMPORARY TABLE {TEMP_NODES_TABLE} AS SELECT * FROM {NODES_TABLE} ;"
    names_command = f"CREATE TEMPORARY TABLE {TEMP_NAMES_TABLE} AS SELECT * FROM {NAMES_TABLE} ;"
    cog_func_command = f"CREATE TEMPORARY TABLE {TEMP_COG_FUNC_TABLE} AS SELECT * FROM {COG_FUNC_TABLE} ;"
    cog_names_command = f"CREATE TEMPORARY TABLE {TEMP_COG_NAMES_TABLE} AS SELECT * FROM {COG_NAMES_TABLE} ;"

    try:
        for command in (prokaryote_command, nodes_command, names_command, cog_func_command, cog_names_command):
            table_operation(command, (), many=False, connector=connector, terminate=False)
    except Exception as e:
        return (False, error_handler(e))

    return connector

def process_text_filedata(sourcefile:bytes|str, eol:str, sep:str, interest:list[int]|None=None):
    if not isinstance(sourcefile, (str, bytes)):
        raise TypeError(f"Expected bytes or str for the source file, got {type(sourcefile).__name__} instead")
    
    if isinstance(sourcefile, bytes):
        raw_data = io.TextIOWrapper(io.BytesIO(sourcefile), errors='replace')
    else:
        raw_data = open(sourcefile)

    raw_data.seek(0)
    values = list()
    
    try:
        for line in raw_data:
            if line[0] == "#":
                continue
            
            data = line.strip(eol).split(sep)

            if not len(data): #Equivalent of len(data) == 0 
                continue
            
            if interest is not None:
                data = [data[pos] for pos in interest]
            
            values.append(data)
    except Exception as e:
        raw_data.close()
        raise e

    return values


# COG TABLES OPERATIONS
def load_disk_cog_database(sourcefile:bytes|str, target_path:str=COG_DATABASE_PATH):
    if not isinstance(sourcefile, (bytes, str)):
        raise TypeError(f"Expected bytes or str for the source file, got {type(sourcefile).__name__} instead")
    
    if isinstance(sourcefile, bytes): 
        download_content = io.BytesIO(sourcefile)
    else:
        download_content = sourcefile

    if not tarfile.is_tarfile(download_content):
        if isinstance(download_content, io.BytesIO):
            download_content.close()

        raise TypeError("Wrong file format detected, expected a .tar file type extension")
    
    if os.path.exists(target_path):
        shutil.rmtree(target_path)

    os.makedirs(target_path)

    if isinstance(download_content, io.BytesIO):
        with tarfile.open(fileobj=download_content) as f:
            f.extractall(target_path)

        download_content.close()
    
    else:
        with tarfile.open(download_content) as f:
            f.extractall(target_path)

def load_cog_names(conn:sqlite3.Connection, sourcefile:bytes|str, target_table:str=TEMP_COG_NAMES_TABLE):
    
    values = process_text_filedata(sourcefile, "\n","\t", interest=[0, 1, 2])

    command = f"INSERT INTO {target_table} VALUES (?,?,?) ON CONFLICT DO NOTHING;"

    table_operation(command, values, many=True, connector=conn, terminate=False)

def load_cog_func(conn:sqlite3.Connection, sourcefile:bytes|str, target_table:str=TEMP_COG_FUNC_TABLE):

    values = process_text_filedata(sourcefile, "\n","\t")

    command = f"INSERT INTO {target_table} VALUES (?,?) ON CONFLICT DO NOTHING;"

    table_operation(command, values, many=True, connector=conn, terminate=False)

def extract_COG_base(conn:sqlite3.Connection, db_link:str = COG_DATABASE_LINK, db_local:str|None = None, 
                     func_link:str = COG_FUNCTIONNAL_LINK, 
                     func_local:str|None = None, fam_link:str = COG_FAMILY_LINK, fam_local:str|None = None):
    
    process = [(db_link, db_local, load_disk_cog_database, False), 
               (func_link, func_local, load_cog_func, True), 
               (fam_link, fam_local, load_cog_names, True)]

    for data_link, local_ver, func, need_conn in process:
        if local_ver is not None:
            try:
                print(f"using local version of file data:{local_ver}")
                func(local_ver) if not need_conn else func(conn, local_ver)
            except Exception as e:
                return (False, error_handler(e))
                
        else:
            try:
                with req.get(data_link, stream=True) as data_download:
                    func(data_download.content) if not need_conn else func(conn, data_download.content)

            except Exception as e:
                return (False, error_handler(e))

    success = "COG information updated sucessfully"
    return (True, success)

# TAXONOMY OPERATIONS
def load_nodes(conn:sqlite3.Connection, sourcefile:bytes|str, target_table:str=TEMP_NODES_TABLE):
    values = process_text_filedata(sourcefile, "\t|\n","\t|\t", interest=[0, 1])

    command = f"INSERT INTO {target_table} VALUES (?,?) ON CONFLICT DO NOTHING;"

    table_operation(command, values, many=True, connector=conn, terminate=False)

def load_names(conn:sqlite3.Connection, sourcefile:bytes|str, target_table:str=TEMP_NAMES_TABLE):
    if not isinstance(sourcefile, (str, bytes)):
        raise TypeError(f"Expected bytes or str for the source file, got {type(sourcefile).__name__} instead")
    
    if isinstance(sourcefile, bytes):
        raw_data = io.TextIOWrapper(io.BytesIO(sourcefile), errors='replace')
    else:
        raw_data = open(sourcefile)
        
    values = list()

    interest = [0, 1]
    name_aim = "scientific name"
   
    raw_data.seek(0)
    try:
        for line in raw_data:
            if line[0] == "#":
                continue

            data = line.strip("\t|\n").split("\t|\t")

            if not len(data): #Equivalent of len(data) == 0 
                continue

            if data[3] != name_aim:
                continue

            value_line = [data[pos] for pos in interest]
            values.append(value_line)
    except Exception as e:
        raw_data.close()
        raise e
        
    command = f"INSERT INTO {target_table} VALUES (?,?) ON CONFLICT DO NOTHING;"

    table_operation(command, values, many=True, connector=conn, terminate=False)

    raw_data.close() 

def extract_tax_dump(conn:sqlite3.Connection, source:str = TAXDMP_LINK, tax_local:str|None=None, nodes_filename:str=NODES_FILE, names_filename:str=NAMES_FILE):
    
    target_files = [(nodes_filename, load_nodes),(names_filename,load_names)]
        
    if tax_local is None:
        try:
            with req.get(source, stream=True) as data_download:
                hierarchy_dump_data_zip = io.BytesIO(data_download.content)
        except Exception as e:
                return (False, error_handler(e))
    else:
        hierarchy_dump_data_zip = tax_local

    try:
        with zipf.ZipFile(hierarchy_dump_data_zip,'r') as zip_content:
            content = zip_content.namelist()
            if any(file not in content for file,_ in target_files):
                raise FileNotFoundError(f"Missing file in zip archive\n\
                                        Make sure both {nodes_filename} and {names_filename} are present")
            
            for file, file_func in target_files:
                file_func(conn, zip_content.read(file))

    except Exception as e:
        if isinstance(hierarchy_dump_data_zip, io.BytesIO):
            hierarchy_dump_data_zip.close()

        return (False, error_handler(e))
    
    success = "Taxonomy data updated sucessfully"
    return (True, success)

def extract_prok_data(conn:sqlite3.Connection, source:str = PROK_LINK, local_source:str|None=None, db_name:str = PROK_DB_PATH, target_table:str=TEMP_PROK_TABLE):
        
    if local_source is None:
        try:
            with req.get(source, stream=True) as data_download:
                raw_data = io.TextIOWrapper(io.BytesIO(data_download.content), data_download.encoding, errors="replace")
        except Exception as e:
                return (False, error_handler(e))
    else:
        raw_data = open(local_source)

    interest = [0, 1, 6, 11, 12, 13, 14, 18, 19, 20]
    #0:'#Organism/Name' | 1: 'TaxID' | 6: Size (Mb) | 11: Genes | 12: Proteins | 13: Release Date | 14: Modify Date | 
    #18: Assembly Accession | 19: Reference | 20: FTP Path

    date_values = [13, 14]

    values = list()
    try:
        for line in raw_data:
            if line[0] == "#":
                continue

            data = line.strip("\n").split("\t")

            if not len(data): #Equivalent of len(data) == 0 
                continue

            if data[15] != "Complete Genome":
                continue

            data[20] = data[20].replace("ftp:","http:")

            for pos in date_values:
                data[pos] = data[pos].replace("/","-")

            value_line = [data[pos] for pos in interest]
            values.append(value_line)
        
        command = f"INSERT INTO {target_table} VALUES (?,?,?,?,?,?,?,?,?,?) ON CONFLICT DO NOTHING;"

        table_operation(command, values, many=True,connector=conn, terminate=False)

    except Exception as e:
        raw_data.close()
        return (False, error_handler(e))
    
    raw_data.close()
    success = "Prokaryote data updated sucessfully"
    return (True, success)


def create_working_database(prok_source:str, prok_local:str|None, tax_source:str, tax_local:str|None,
                    cog_db_link:str, cog_db_local:str|None, fam_link:str, fam_local:str|None,
                    cog_func_link:str, cog_func_local:str|None, force:bool=True):
                    
    print("building_database") # Replaced by logging
    conn:sqlite3.Connection = create_prok_database(force=force)

    if not os.path.exists(GENOME_FOLDER):
        os.makedirs(GENOME_FOLDER)

    update_database(prok_source, prok_local, tax_source, tax_local,
                    cog_db_link, cog_db_local, fam_link, fam_local, 
                    cog_func_link, cog_func_local, connector = conn)

def update_database(prok_source:str, prok_local:str|None, tax_source:str, tax_local:str|None,
                    cog_db_link:str, cog_db_local:str|None, fam_link:str, fam_local:str|None,
                    cog_func_link:str, cog_func_local:str|None, connector:sqlite3.Connection|None=None):
    
    conn = create_temp_database(connector)
    processes = (
        ("extracting taxonomy data", extract_tax_dump, (tax_source, tax_local)), 
        ("extracting genomic data", extract_prok_data, (prok_source, prok_local)), 
        ("extracting COG data", extract_COG_base, (cog_db_link, cog_db_local, cog_func_link, cog_func_local,
                                                   fam_link, fam_local)),
        ("updating database", fuse_temp_database, ())
    )
    for process_message, process, vars in processes:
        print(process_message)
        valid, result = process(conn, *vars) if len(vars) else process(conn)
        if not valid:
            messagebox.showerror(message=result, icon="error")
            conn.close()
            return
        print(result) # Replaced by logging later
    
    conn.close()
    messagebox.showinfo(message=result,icon='info')

def fuse_temp_database(connector:sqlite3.Connection):
    prokaryote_command = f"INSERT OR IGNORE INTO {PROK_TABLE} SELECT * FROM {TEMP_PROK_TABLE} ;"
    nodes_command = f"INSERT OR IGNORE INTO {NODES_TABLE} SELECT * FROM {TEMP_NODES_TABLE} ;"
    names_command = f"INSERT OR IGNORE INTO {NAMES_TABLE} SELECT * FROM {TEMP_NAMES_TABLE} ;"
    cog_func_command = f"INSERT OR IGNORE INTO {COG_FUNC_TABLE} SELECT * FROM {TEMP_COG_FUNC_TABLE} ;"
    cog_names_command = f"INSERT OR IGNORE INTO {COG_NAMES_TABLE} SELECT * FROM {TEMP_COG_NAMES_TABLE} ;"

    try:
        for command in (prokaryote_command, nodes_command, names_command, cog_func_command, cog_names_command):
            table_operation(command, (), many=False, connector=connector, terminate=False)
    except Exception as e:
        return (False, error_handler(e))
    
    message = "Database fully updated"
    return (True, message)