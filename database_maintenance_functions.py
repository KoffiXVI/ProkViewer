import os 
import sqlite3
import numpy as np
from database_constants import *
from analysis_classes import *
from subprocess_functions import *
import tempfile
from tkinter import messagebox

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

        self.table_operation(command, values, many=True, terminate=False)

    def delete_rpsblast_log_record(self, index:str|int, target_table:str=COG_LOG_TABLE):

        command = f"DELETE FROM {target_table} WHERE {LOG_ID} = ? ;"

        self.table_operation(command, (str(index),), many=False, terminate=False)
    
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

        self.table_operation(command, (str(target),), many=False, returning = True, terminate=False)

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

        self.table_operation(command, (str(index),), many=False, terminate=False)

    def check_blast_log(self, Q_acc:str, S_acc:str, *args:tuple[str|int|float], target_table:str=LOG_TABLE):
        
        command = f"SELECT {LOG_ID}, {Q_NAME}, {Q_ID}, {Q_ASSEMBLY}, \
            {S_NAME}, {S_ID}, {S_ASSEMBLY} FROM {target_table} \
                WHERE ({Q_ASSEMBLY} = ? AND {S_ASSEMBLY} = ? OR {Q_ASSEMBLY} = ? AND {S_ASSEMBLY} = ?)\
                AND {EVALUE} = ? AND {WORD_SIZE} = ? AND {G_OPEN} = ? \
                    AND {G_EXTEND} = ? AND {MATRIX} = ? AND {LOOKUP_TABLE} = ?;"
        
        values = (Q_acc, S_acc, S_acc, Q_acc, *args)

        self.table_operation(command, values, many=False, returning=True, terminate=False)

        return self.get_res()

    def load_previous_blast(self, Log_id:str, target_table:str=RES_TABLE):
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
            return None, ("No record in database", True)
        
        max_pages = max_log_rows//max_view
        view_window = max(min(view_window, max_pages),0)

        self.table_operation(command,(max_view, view_window, max_view), many=False, returning=True, terminate=True)

        page_text = f"page {view_window+1}/{max_pages}"

        return (self.get_res(), (page_text, view_window+1==max_pages))
    
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

    def download_blast_res(self, filename:str, Log_id:str):
        header = f"{Q_SEQID} {S_SEQID} {P_IDENT} {LENGTH} {MISMATCH} {GAPS} {Q_END} {S_START} {S_END} {EVALUE} {BITSCORE}"
        
        res = self.load_previous_blast(Log_id)

        np.savetxt(filename, res, delimiter="\t", header=header, fmt="%s")

    def download_rps_blast_res(self, filename:str, Log_id:str):
        header = f"{Q_ASSEMBLY} {S_TITLE} {P_IDENT} {EVALUE} {FUNC_CODE}"
        
        res = self.load_previous_rpsblast(Log_id)
        res = self.retrieve_cog_func(Log_id, res)

        np.savetxt(filename, res, delimiter="\t", header=header, fmt="%s")

    #QUERY OPS
    def process_query(self, data:str, target:str|int, target_table:str=PROK_TABLE):
        if target not in [NAME, TAXID]:
            self.error_handler(ValueError(f"expectected {NAME} or {TAXID}, got '{target}' instead"))
            return None 
        
        if target == NAME:
            data = f"%{data}%"
            command = f"SELECT DISTINCT {NAME}, {TAXID}, COUNT({TAXID}) \
                        AS counter, {ASSEMBLY}, {LINK} FROM {target_table} WHERE {NAME} LIKE ? GROUP BY {TAXID};"
        else:
            command = f"SELECT DISTINCT {NAME}, {TAXID}, COUNT({TAXID}) \
                        AS counter, {ASSEMBLY}, {LINK} FROM {target_table} WHERE {TAXID} = ?;"
        
        self.table_operation(command, (str(data),), many=False, returning=True)

        return self.get_res()
    
    def advanced_process_query(self, target_name:str, target_id:str, target_table:str=PROK_TABLE):

        target_name = f"%{target_name}%"

        command = f"SELECT {NAME},{REFERENCE},{RELEASE_DATE}, \
                        {MODIFY_DATE}, {SIZE}, {GENES}, ROUND({GENES}/{SIZE},2) as gene_ratio, {PROTEINS}, \
                        ROUND({PROTEINS}/{SIZE},2) as protein_ratio, {ASSEMBLY}, {LINK} FROM {target_table} \
                        WHERE {NAME} LIKE ? AND {TAXID} = ?;"
        
        self.table_operation(command, (target_name, target_id), many=False, returning=True)

        
        return self.get_res()
    
    #BLASTP PIPELINE
    def blast_pipeline(self, target_genomes:list[Genome],evalue=1e-10, ws=3, gapopen=11, gapextend=1, matrix:str="BLOSUM62",threshold=11, temp_db=BLAST_TEMP_DB):
        query, subject = target_genomes
        
        for genome in target_genomes:
            if not isinstance(genome, Genome):
                e = TypeError(f'expected {Genome.__name__} for genome, got {type(genome).__name__} instead')
                message = self.error_handler(e)
                messagebox.showerror(message=message, icon="error")
                self.terminate_connection()
                return None, None, None
            
        existing = self.check_blast_log(query.assembly, subject.assembly, evalue, ws,gapopen,gapextend,matrix,threshold)

        print("here is the actual matrix:", threshold)
        
        if len(existing) > 0:
            res_table = self.load_previous_blast(existing[0][0])
            print("results loaded from a previous blast operation")

        else:
            for genome in target_genomes: 
                dowload_res, cause = genome.download_genome()
                if not dowload_res:
                    message = self.error_handler(cause)
                    messagebox.showerror(message=message, icon="error")
                    self.terminate_connection()
                    return None, None, None
            
            with tempfile.TemporaryDirectory() as temp_db:
                makedb(subject.get_faa(), temp_db)

                res = protein_blast(src=query.get_faa(), target_db=temp_db, evalue=evalue, 
                                    ws=ws,gapopen=gapopen,gapextend=gapextend,matrix=matrix,threshold=threshold)

                res_table = np.array([line.split('\t') for line in res.splitlines()])

                log_index = self.log_blast_op(*query.log_info(), *subject.log_info(),evalue, ws,gapopen,gapextend,matrix,threshold)

                self.log_blast_res(log_index, res_table)

        messagebox.showinfo(message="Blastp executed successfully")

        return query.display_name, subject.display_name, Blast_Results_Table(res_table, evalue)
    
    #RPS BLAST PIPELINE
    def rpsblast_pipeline(self, target_genome:Genome,evalue=1e-10):
        if not isinstance(target_genome, Genome):
            e = TypeError(f'expected {Genome.__name__} for genome parameter, got {type(genome).__name__} instead')
            message = self.error_handler(e)
            messagebox.showerror(message=message, icon="error")
            self.terminate_connection()
            return None
            
        existing = self.check_rpsblast_log(target_genome.assembly, evalue)
        if len(existing) > 0:
            res_table = self.load_previous_rpsblast(existing[0][0])

            res_table = self.retrieve_cog_func(existing[0][0],res_table)
            print("results loaded from a previous rpsblast operation")
            
        else:
            dowload_res, cause = target_genome.download_genome()
            if not dowload_res:
                message = self.error_handler(cause)
                messagebox.showerror(message=message, icon="error")
                self.terminate_connection()
                return None
            
            res = rps_blast(target_genome.get_faa())
            res_table = np.array([line.split('\t') for line in res.splitlines()])
            res_table[:,1] = [line[:line.index(',')] for line in res_table[:,1]]
            
            log_index = self.log_rpsblast_op(*target_genome.log_info(),evalue)
            self.log_rpsblast_res(log_index, res_table)

            res_table = self.retrieve_cog_func(log_index,res_table) #adding the function

        return RPSBlast_Results_Table(res_table, evalue)
    
    def sequenced_rps_blast(self, target_genomes:list[Genome], evalue=1e-10):
        results = list()
        for genome in target_genomes:
            res = self.rpsblast_pipeline(genome, evalue)
            if res is None:
                self.terminate_connection()
                return None, None
            results.append(res)

        self.terminate_connection()
        messagebox.showinfo(message="Sequence RPSBlast executed successfully")
        return res
    
    def prepare_alignment_object():

        #TBA

        return