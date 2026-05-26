import subprocess
import os
from database_constants import BLAST_TEMP_DB, RPS_DABASE_PATH
import numpy as np
from analysis_classes import *

def makedb(src, title:str|None=None, dbtype:str = "prot"):
    return subprocess.run(["makeblastdb","-in",f"{src}","-dbtype",dbtype, "-title",
                           f"{src if title is None else title}","-out",f"{src if title is None else title}"])


def protein_blast(src:str,target_db:str=BLAST_TEMP_DB, evalue=1e-10, ws=3, gapopen=11, gapextend=1, matrix:str="BLOSUM62",threshold=11):
    potential_matrices = ["PAM30", "PAM70", "PAM250", "BLOSUM90", "BLOSUM80","BLOSUM62","BLOSUM50","BLOSUM45"]
    
    assert matrix in potential_matrices, f"{matrix} is an invalid matrix type. Accepted matrices:{potential_matrices}"

    return subprocess.run(["blastp", "-query", f"{src}", "-db", f"{target_db}", "-evalue", f"{evalue}","-word_size",f"{ws}",
                           "-gapopen",f"{gapopen}","-gapextend",f"{gapextend}","-matrix",f"{matrix}","-threshold",f"{threshold}",
                             "-outfmt",'6 qseqid sseqid pident length mismatch gaps qstart qend sstart send evalue bitscore'], 
                            text=True, stdout=subprocess.PIPE).stdout

def rps_blast(src:str,target_db:str=RPS_DABASE_PATH, evalue=1e-10):

    if not os.path.exists(src):
        return None
    
    return subprocess.run(["rpsblast","-query",f"{src}","-db",f"{target_db}","-num_alignments","1","-evalue",f"{evalue}",
                           "-outfmt",'6 qaccver stitle evalue'], text=True, stdout=subprocess.PIPE).stdout