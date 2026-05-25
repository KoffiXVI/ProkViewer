import os 
import sqlite3
import numpy as np
from database_constants import *

class Database_Ops_Handler():
    def __init__(self, db_name:str = PROK_DB_PATH):
        
        self.db_name = db_name
        self.res = None
        self.connection:sqlite3.Connection = None

    @staticmethod
    def error_handler(e:Exception):
        #Will later handle proper error logging
        err = f"Failure to continue operation. Cause:{e}"
        print(err)

        return err

    def table_operation(self, command:str, data:list|tuple, many:bool, returning:bool=False, terminate:bool=True):
        if not os.path.exists(self.db_name):
            e = FileNotFoundError("no database existing for operation")
            self.error_handler(e)
            raise e
        
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_name)
            
        cursor = self.connection.cursor()

        cursor.execute('PRAGMA foreign_keys = ON')

        if many:
            cursor.executemany(command, data)
        else:
            cursor.execute(command, data)

        if returning:
            self.res = cursor.fetchall()

        self.connection.commit()
        cursor.close()

        if terminate:
            self.terminate_connection()

    def terminate_connection(self):
        self.connection.close()
        self.connection = None
    
    def get_res(self):
        res = self.res
        self.res = None
        return res
    
    # RPS BLAST OPS
    def log_rpsblast_op(self, *args:tuple[str], target_table:str=COG_LOG_TABLE):

        command = f"INSERT INTO {target_table} ({Q_NAME}, {Q_ID}, {Q_ASSEMBLY}, {EVALUE}) VALUES (?,?,?,?) RETURNING {LOG_ID} ;"

        self.table_operation(command, args, many=False, returning=True, terminate=False)
        
        return self.get_res()[0][0]
    
    def log_rpsblast_res(self, index:int, rpsblast_data:np.ndarray[str], target_table:str=COG_RES_TABLE):
        col_injection = np.full(rpsblast_data.shape[0], index, dtype=rpsblast_data.dtype)
        values = np.column_stack((col_injection, rpsblast_data))

        command = f'INSERT INTO {target_table} ({LOG_ID}, {Q_ASSEMBLY}, {S_TITLE}, {EVALUE}) VALUES (?,?,?,?) ;'

        self.table_operation(command, values, many=True)

    def delete_rpsblast_log_record(self, index:str|int, target_table:str=COG_LOG_TABLE):

        command = f"DELETE FROM {target_table} WHERE {LOG_ID} = ? ;"

        self.table_operation(command, (str(index),), many=False)
    
    def check_rpsblast_log(self, Q_acc:str, E_value:str, target_table:str=COG_LOG_TABLE):
        command = f"SELECT {LOG_ID}, {Q_NAME}, {Q_ID}, {Q_ASSEMBLY} \
            FROM {target_table} WHERE {Q_ASSEMBLY} = ? AND {EVALUE} = ? ; "
        
        values = (Q_acc, E_value)

        self.table_operation(command, values, many=False, returning=True, terminate=False)

        return self.get_res()
    
    def load_previous_rpsblast(self, Log_id:str|int, target_table:str=COG_RES_TABLE):
        command = f"SELECT {Q_ASSEMBLY}, {S_TITLE}, {EVALUE} FROM {target_table} WHERE {LOG_ID} = ?"

        self.table_operation(command, (str(Log_id),), many=False, returning=True, terminate=False)

        res = np.array([[*element] for element in self.get_res()])

        return res
    
    def retrieve_cog_func(self, target:int|str, rpsblast_data:np.ndarray[str], target_table:str=COG_RES_TABLE, names_table:str =COG_NAMES_TABLE):
        command = f"SELECT {FUNC_CODE} FROM {names_table} NATURAL JOIN \
            (SELECT {S_TITLE} as {NAME_CODE} FROM {target_table} WHERE {LOG_ID} = ?)\
            as temp WHERE {names_table}.{NAME_CODE} = temp.{NAME_CODE};"

        self.table_operation(command, (str(target),), many=False, returning = True)

        res = np.column_stack((rpsblast_data, self.get_res()))

        return res
    
    # BLATSP OPS
    def log_blast_op(self, *args:tuple[str|int|float], target_table:str=LOG_TABLE):
        
        command = f"INSERT INTO {target_table} ({Q_NAME}, {Q_ID}, {Q_ASSEMBLY}, {S_NAME}, {S_ID}, {S_ASSEMBLY},\
            {EVALUE}, {WORD_SIZE}, {G_OPEN}, {G_EXTEND}, {MATRIX}, {LOOKUP_TABLE}) \
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?) RETURNING {LOG_ID} ;"
        
        self.table_operation(command, args, many=False, returning=True, terminate=False)
        
        return self.get_res()[0][0]
    
    def log_blast_res(self, index:int, blast_data:np.ndarray[str], target_table:str=RES_TABLE):
        col_injection = np.full(blast_data.shape[0], index, dtype=blast_data.dtype)
        values = np.column_stack((col_injection, blast_data))

        command = f'INSERT INTO {target_table}({LOG_ID}, {Q_SEQID}, {S_SEQID}, {P_IDENT}, {LENGTH}, {MISMATCH}, {GAPS}, \
            {Q_START}, {Q_END}, {S_START}, {S_END}, {EVALUE}, {BITSCORE}) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)'
        
        self.table_operation(command, values, many=True)

    def delete_blast_log_record(self, index:str|int, target_table:str=LOG_TABLE):
        
        command = f"DELETE FROM {target_table} WHERE {LOG_ID} = ? ;"

        self.table_operation(command, (str(index),), many=False)

    def check_blast_log(self, Q_acc:str, S_acc:str, *args:tuple[str|int|float], target_table:str=LOG_TABLE):
        
        command = f"SELECT {LOG_ID}, {Q_NAME}, {Q_ID}, {Q_ASSEMBLY}, \
            {S_NAME}, {S_ID}, {S_ASSEMBLY} FROM {target_table} \
                WHERE ({Q_ASSEMBLY} = ? AND {S_ASSEMBLY} = ? OR {Q_ASSEMBLY} = ? AND {S_ASSEMBLY} = ?)\
                AND {EVALUE} = ? AND {WORD_SIZE} = ? AND {G_OPEN} = ? \
                    AND {G_EXTEND} = ? AND {MATRIX} = ? AND {LOOKUP_TABLE} = ?;"
        
        values = (Q_acc, S_acc, S_acc, Q_acc, *args)

        self.table_operation(command, values, many=False, returning=True, terminate=False)

        return self.get_res()

    def load_previous_blast(self, Log_id, target_table:str=RES_TABLE):
        command = f"SELECT {Q_SEQID}, {S_SEQID}, {P_IDENT}, {LENGTH}, \
            {MISMATCH}, {GAPS}, {Q_START}, {Q_END}, \
            {S_START}, {S_END}, {EVALUE}, {BITSCORE} FROM {target_table} WHERE {LOG_ID} = ?"

        self.table_operation(command, (str(Log_id),), many=False, returning=True)

        res = np.array([[*element] for element in self.get_res()])

        return res 

    def get_max_log_rows(self, target_table:str):

        command = f"SELECT MAX(row) FROM (SELECT ROW_NUMBER() OVER(ORDER BY {DATE}) row FROM {target_table});"

        self.table_operation(command, (), many=False, returning=True, terminate=False)

        return self.get_res()[0][0]

    def navigate_logs(self, command:str, target_table:str, view_window:int=0, max_view:int=10):
        max_log_rows = self.get_max_log_rows(target_table)
        if max_log_rows is None:
            return []
        
        max_pages = max_log_rows//max_view
        view_window = max(min(view_window, max_pages),0)

        self.table_operation(command,(max_view, view_window, max_view), many=False, returning=True, terminate=True)

        page_text = f"page {view_window+1}/{max_pages+1}"

        return (self.get_res(), page_text)
    
    def navigate_rpsblast_logs(self, target_table:str = COG_LOG_TABLE, view_window:int=0, max_view:int=10):

        command = f"SELECT ROW_NUMBER() OVER(ORDER BY {DATE}), {DATE}, {Q_NAME}, {Q_ID}, \
            {Q_ASSEMBLY}, {EVALUE}, {LOG_ID} FROM {target_table} LIMIT 0+?*? ,?"

        res, page_text = self.navigate_logs(command, target_table, view_window, max_view)

        return (res, page_text)

    def navigate_blast_logs(self, target_table:str=LOG_TABLE, view_window:int=0, max_view:int=10):
        command = f"SELECT ROW_NUMBER() OVER(ORDER BY {DATE}), {DATE}, {Q_NAME}, {Q_ID}, {Q_ASSEMBLY},\
            {S_NAME}, {S_ID}, {S_ASSEMBLY}, {EVALUE}, {WORD_SIZE}, {G_OPEN}, {G_EXTEND}, {MATRIX},\
                {LOOKUP_TABLE}, {LOG_ID} FROM {target_table} LIMIT 0+?*? ,?"
        
        res, page_text = self.navigate_logs(command, target_table, view_window, max_view)

        return (res, page_text)



"""
def dtable_operation(command:str, data:list|tuple, many:bool, returning:bool=False, connector:sqlite3.Connection=None, terminate:bool=True, db_name:str = PROK_DB_PATH):
    if not os.path.exists(db_name):
        e = FileNotFoundError("no database existing for operation")
        error_handler(e)
        raise e
    
    conn = connector if connector is not None else sqlite3.connect(db_name) 
    cursor = conn.cursor()

    cursor.execute('PRAGMA foreign_keys = ON')

    res = None

    if many:
        cursor.executemany(command, data)
    else:
        cursor.execute(command, data)

    if returning:
        res = cursor.fetchall()

    conn.commit()
    cursor.close()

    if terminate:
        conn.close()
        return res
    
    return res, conn

# RPS BLAST OPS
def log_rpsblast_op(*args:tuple[str], target_table:str=COG_LOG_TABLE):

    command = f"INSERT INTO {target_table} ({Q_NAME}, {Q_ID}, {Q_ASSEMBLY}, {EVALUE}) VALUES (?,?,?,?) RETURNING {LOG_ID} ;"

    res = table_operation(command, args, many=False, returning=True)[0][0]
    
    return res

def log_rpsblast_res(index:int, rpsblast_data:np.ndarray[str], target_table:str=COG_RES_TABLE):
    col_injection = np.full(rpsblast_data.shape[0], index, dtype=rpsblast_data.dtype)
    values = np.column_stack((col_injection, rpsblast_data))

    command = f'INSERT INTO {target_table} ({LOG_ID}, {Q_ASSEMBLY}, {S_TITLE}, {EVALUE}) VALUES (?,?,?,?)'

    table_operation(command, values, many=True)

def delete_rpsblast_log_record(index:str|int, target_table:str=COG_LOG_TABLE):

    command = f"DELETE FROM {target_table} WHERE {LOG_ID} = ? ;"

    table_operation(command, (str(index),), many=False)

def check_rpsblast_log(Q_acc:str, E_value:str, target_table:str=COG_LOG_TABLE):
    command = f"SELECT {LOG_ID}, {Q_NAME}, {Q_ID}, {Q_ASSEMBLY} \
        FROM {target_table} WHERE {Q_ASSEMBLY} = ? AND {EVALUE} = ? ; "
    
    values = (Q_acc, E_value)

    res = table_operation(command, values, many=False, returning=True)

    return res

def load_previous_rpsblast(Log_id:str|int, target_table:str=COG_RES_TABLE):
    command = f"SELECT {Q_ASSEMBLY}, {S_TITLE}, {EVALUE} FROM {target_table} WHERE {LOG_ID} = ?"

    res = table_operation(command, (str(Log_id),), many=False, returning=True)

    res = np.array([[*element] for element in res])

    return res 

def retrieve_cog_func(target:int|str, rpsblast_data:np.ndarray[str], target_table:str=COG_RES_TABLE, names_table:str =COG_NAMES_TABLE):
    command = f"SELECT {FUNC_CODE} FROM {names_table} NATURAL JOIN \
        (SELECT {S_TITLE} as {NAME_CODE} FROM {target_table} WHERE {LOG_ID} = ?)\
          as temp WHERE {names_table}.{NAME_CODE} = temp.{NAME_CODE};"

    res = table_operation(command, (str(target),), many=False, returning = True)

    res = np.column_stack((rpsblast_data, res))
    return res

# BLATSP OPS
def log_blast_op(*args:tuple[str|int|float], target_table:str=LOG_TABLE):
    
    command = f"INSERT INTO {target_table} ({Q_NAME}, {Q_ID}, {Q_ASSEMBLY}, {S_NAME}, {S_ID}, {S_ASSEMBLY},\
        {EVALUE}, {WORD_SIZE}, {G_OPEN}, {G_EXTEND}, {MATRIX}, {LOOKUP_TABLE}) \
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?) RETURNING {LOG_ID} ;"
    
    res = table_operation(command, args, many=False, returning=True)[0][0]
    
    return res

def log_blast_res(index:int, blast_data:np.ndarray[str], target_table:str=RES_TABLE):
    col_injection = np.full(blast_data.shape[0], index, dtype=blast_data.dtype)
    values = np.column_stack((col_injection, blast_data))

    command = f'INSERT INTO {target_table}({LOG_ID}, {Q_SEQID}, {S_SEQID}, {P_IDENT}, {LENGTH}, {MISMATCH}, {GAPS}, \
        {Q_START}, {Q_END}, {S_START}, {S_END}, {EVALUE}, {BITSCORE}) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)'
    
    table_operation(command, values, many=True)

def delete_blast_log_record(index:str|int, target_table:str=LOG_TABLE):
    
    command = f"DELETE FROM {target_table} WHERE {LOG_ID} = ? ;"

    table_operation(command, (str(index),), many=False)

def check_blast_log(Q_acc:str, S_acc:str, *args:tuple[str|int|float], target_table:str=LOG_TABLE):
    
    command = f"SELECT {LOG_ID}, {Q_NAME}, {Q_ID}, {Q_ASSEMBLY}, \
        {S_NAME}, {S_ID}, {S_ASSEMBLY} FROM {target_table} \
            WHERE ({Q_ASSEMBLY} = ? AND {S_ASSEMBLY} = ? OR {Q_ASSEMBLY} = ? AND {S_ASSEMBLY} = ?)\
            AND {EVALUE} = ? AND {WORD_SIZE} = ? AND {G_OPEN} = ? \
                AND {G_EXTEND} = ? AND {MATRIX} = ? AND {LOOKUP_TABLE} = ?;"
    
    values = (Q_acc, S_acc, S_acc, Q_acc, *args)

    res = table_operation(command, values, many=False, returning=True)

    return res

def load_previous_blast(Log_id, target_table:str=RES_TABLE):
    command = f"SELECT {Q_SEQID}, {S_SEQID}, {P_IDENT}, {LENGTH}, \
        {MISMATCH}, {GAPS}, {Q_START}, {Q_END}, \
        {S_START}, {S_END}, {EVALUE}, {BITSCORE} FROM {target_table} WHERE {LOG_ID} = ?"

    res = table_operation(command, (str(Log_id),), many=False, returning=True)

    res = np.array([[*element] for element in res])

    return res 


# RESULTS TABLE OPS
def get_max_log_rows(target_table:str):

    command = f"SELECT MAX(row) FROM (SELECT ROW_NUMBER() OVER(ORDER BY {DATE}) row FROM {target_table});"

    res = table_operation(command, (), many=False, returning=True)[0][0]

    return res

def navigate_logs(command:str, target_table:str, view_window:int=0, max_view:int=10):
    max_log_rows = get_max_log_rows(target_table)
    if max_log_rows is None:
        return []
    
    max_pages = max_log_rows//max_view
    view_window = max(min(view_window, max_pages),0)

    res = table_operation(command,(max_view, view_window, max_view), many=False, returning=True)

    page_text = f"page {view_window+1}/{max_pages+1}"

    return (res, page_text)

def navigate_rpsblast_logs(target_table:str = COG_LOG_TABLE, view_window:int=0, max_view:int=10):

    command = f"SELECT ROW_NUMBER() OVER(ORDER BY {DATE}), {DATE}, {Q_NAME}, {Q_ID}, \
        {Q_ASSEMBLY}, {EVALUE}, {LOG_ID} FROM {target_table} LIMIT 0+?*? ,?"

    res, page_text = navigate_logs(command, target_table, view_window, max_view)

    return (res, page_text)

def navigate_blast_logs(target_table:str=LOG_TABLE, view_window:int=0, max_view:int=10):
    command = f"SELECT ROW_NUMBER() OVER(ORDER BY {DATE}), {DATE}, {Q_NAME}, {Q_ID}, {Q_ASSEMBLY},\
          {S_NAME}, {S_ID}, {S_ASSEMBLY}, {EVALUE}, {WORD_SIZE}, {G_OPEN}, {G_EXTEND}, {MATRIX},\
              {LOOKUP_TABLE}, {LOG_ID} FROM {target_table} LIMIT 0+?*? ,?"
    
    res, page_text = navigate_logs(command, target_table, view_window, max_view)

    return (res, page_text)

"""