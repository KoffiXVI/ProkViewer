import os

#Database table name constants
PROK_TABLE = "prokaryotes"
LOG_TABLE = "blast_log"
RES_TABLE = "blast_results"
NODES_TABLE = "tax_nodes"
NAMES_TABLE = "tax_names"
COG_LOG_TABLE = "cog_log"
COG_RES_TABLE = "cog_res"
COG_FUNC_TABLE = "cog_functions"
COG_NAMES_TABLE = "cog_names"

#Database name constants
NAME = "Name"
TAXID = "taxid"
SIZE = "size"
GENES = "genes"
PROTEINS = "protein"
RELEASE_DATE = "release_date"
MODIFY_DATE = "modify_date"
ASSEMBLY = "assembly"
REFERENCE = "reference"
LINK = "link"
LOG_ID = "Log_id"
DATE = "Date"
Q_NAME = "Q_name"
Q_ID = "Q_id"
Q_ASSEMBLY = "Q_acc"
S_NAME = "S_name"
S_ID = "S_id"
S_ASSEMBLY = "S_acc"
EVALUE = "Evalue"
WORD_SIZE = "Word_size"
G_OPEN = "G_open"
G_EXTEND = "G_extend"
MATRIX = "Matrix"
LOOKUP_TABLE = "Lookup_t"
RES_ID = "Res_id"
Q_SEQID = "qseqid"
S_SEQID = "sseqid"
P_IDENT = "pident"
LENGTH = "length"
MISMATCH = "mismatch"
GAPS = "gaps"
Q_START = "qstart"
Q_END = "qend"
S_START = "ssrart"
S_END = "ssend"
BITSCORE = "bitscore"
PARENT_TAXID = "parent_taxid"
FUNC_CODE = "func_code"
FUNC_DESC = "func_desc"
NAME_CODE = "name_code"
COG_DESC = "cog_desc"
S_TITLE = "stitle"

#PATHS

PROK_DB_NAME = "PROK_DB.sqlite"

#Database paths
DB_STORE_PATH = os.path.abspath("database")
PROK_DB_PATH = os.path.join(DB_STORE_PATH, PROK_DB_NAME)
GENOME_FOLDER = os.path.join(DB_STORE_PATH, "genomes")
BLAST_TEMP_DB = "subject_data" #"Project_data/genomes/temp/database_genome/subject_data"

#Taxonomy data
TAXDMP_LINK = "https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdmp.zip"
NODES_FILE = 'nodes.dmp'
NAMES_FILE = 'names.dmp'

#Prokaryote database source
PROK_LINK = "https://ftp.ncbi.nlm.nih.gov/genomes/GENOME_REPORTS/prokaryotes.txt"

#Cog related paths and links
COG_DIRECTORY = os.path.join(DB_STORE_PATH, "COG") #"Project_data/COG"
COG_DATABASE_PATH = os.path.join(COG_DIRECTORY, "Cog") 
RPS_DABASE_PATH = os.path.join(COG_DATABASE_PATH, "Cog") 
COG_DATABASE_LINK = "https://ftp.ncbi.nih.gov/pub/mmdb/cdd/little_endian/Cog_LE.tar.gz"
COG_FUNCTIONNAL_LINK = "https://ftp.ncbi.nih.gov/pub/COG/COG2014/data/fun2003-2014.tab"
COG_FAMILY_LINK = "https://ftp.ncbi.nih.gov/pub/COG/COG2024/data/cog-24.def.tab"