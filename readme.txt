====================================================================
  PROK VIEWER — Instructions d'installation et d'utilisation
====================================================================

----------------------------------------------------------------------
1. PRÉREQUIS LOGICIELS
----------------------------------------------------------------------

Python 3.10 ou supérieur est requis.

Dépendances Python (installables via pip) :
    pip install requests numpy matplotlib pillow

Outils NCBI BLAST+ requis (doivent être accessibles dans le PATH
système) :
    - makeblastdb
    - blastp
    - rpsblast

Téléchargement BLAST+ : https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/

----------------------------------------------------------------------
2. STRUCTURE DES FICHIERS ET DOSSIERS
----------------------------------------------------------------------

Racine du projet :
│
├── main.py                          Point d'entrée de l'application
├── global_defaults.py               Chargement des constantes globales
│                                    (titre, dimensions de fenêtre, etc.)
│
├── page_notebook.py                 Gestion de la fenêtre principale
│                                    à onglets (ttk.Notebook)
│
├── database_constants.py            Constantes partagées : noms des
│                                    tables SQL, des colonnes, et chemins
│                                    vers les fichiers et dossiers
│
├── database_creation_functions.py   Création, peuplement et mise à jour
│                                    de la base de données SQLite
│
├── database_maintenance_functions.py Opérations bas niveau sur la base
│                                    (requêtes, journalisation, pipelines
│                                    BLAST et RPS-BLAST)
│
├── database_table.py                Interface graphique de l'onglet
│                                    "DB Setup" (configuration BDD)
│
├── search_table.py                  Interface de l'onglet de recherche
│                                    de génomes prokaryotes
│
├── phylogeny_page.py		     Interface de l'onglet de recherche 
│				     de génomes prokaryotes par arborescence 
│
├── analysis_table.py                Interface de l'onglet d'analyse
│                                    (lancement des pipelines BLAST)
│
├── plot_table.py                    Interface de visualisation des
│                                    dot plots (onglet "Plots")
│
├── history_table.py                 Interface de l'historique des
│                                    analyses précédentes
│
├── custom_containers.py             Composants graphiques réutilisables
│                                    (Table, Entry_element, Combobox,
│                                    File_Searcher, Radio_Buttons, etc.)
│
├── subprocess_functions.py          Appels aux outils BLAST externes
│                                    (makeblastdb, blastp, rpsblast)
│
├── analysis_classes.py              Classes de traitement des résultats
│                                    (Blast_Results_Table,
│                                    RPSBlast_Results_Table,
│                                    Blast_Display_Manager, Genome)
│
├── user_settings/
│   └── defaults.json                Paramètres utilisateur : dimensions
│                                    de la fenêtre, langue, thème.
│                                    Modifier ce fichier pour changer
│                                    la taille de la fenêtre au démarrage.
│
├── assets/
│   └── text_data.json               Données textuelles de l'interface
│                                    (libellés, messages)
│
├── database/                        Dossier créé automatiquement lors
│   ├── PROK_DB.sqlite               de la première initialisation.
│   └── COG/                         Contient la base SQLite principale
│       └── Cog/Cog                  et les fichiers de la base COG
│                                    (téléchargés ou fournis localement).
│
└── genomes/                         Dossier créé automatiquement.
                                     Contient les fichiers de protéomes
                                     (.faa) téléchargés depuis NCBI
                                     lors des analyses BLAST.

----------------------------------------------------------------------
3. INITIALISATION DE LA BASE DE DONNÉES
----------------------------------------------------------------------

Au premier lancement, la base de données doit être constituée via
l'onglet "DB Setup" de l'interface :

  a) Chaque section (Prokaryotes, Taxonomy, COG) propose deux options :
       - Un lien de téléchargement (pré-rempli, désactivé par défaut)
       - Un sélecteur de fichier local

  b) Pour utiliser un fichier local, cliquer sur le bouton correspondant
     et sélectionner le fichier téléchargé au préalable.

  c) Cliquer sur "Set up database" pour créer et peupler la base.
     ATTENTION : cette opération supprime et recrée la base existante ! Les résultats d'analyse enregistrés seront donc aussi perdus !

  d) Pour mettre à jour une base existante sans la recréer, utiliser
     "Update database".

  Sources de données attendues :
    - Prokaryotes : fichier prokaryotes.txt (NCBI Genome Reports)
      Lien : https://ftp.ncbi.nlm.nih.gov/genomes/GENOME_REPORTS/prokaryotes.txt
	
	Attention: certains génomes marqués complets dans le NCBI Genome Reports
        manquent de lien pour le téléchargement de fichier (.faa)

    - Taxonomie   : archive taxdmp.zip (NCBI Taxonomy)
      Lien : https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdmp.zip
      (doit contenir nodes.dmp et names.dmp)

    - Base COG    : archive Cog_LE.tar.gz (NCBI CDD)
      Lien : https://ftp.ncbi.nih.gov/pub/mmdb/cdd/little_endian/Cog_LE.tar.gz

    - Fonctions COG : fun2003-2014.tab
      Lien : https://ftp.ncbi.nih.gov/pub/COG/COG2014/data/fun2003-2014.tab

    - Familles COG  : cog-24.def.tab
      Lien : https://ftp.ncbi.nih.gov/pub/COG/COG2024/data/cog-24.def.tab

----------------------------------------------------------------------
4. LANCEMENT DE L'APPLICATION
----------------------------------------------------------------------

Depuis le dossier racine du projet :

    python main.py

L'interface s'ouvre avec les onglets suivants :
  - Search    : recherche de génomes par nom ou TaxID
  - Phylogeny : recherche de génomes par arborescence 
  - Analysis  : configuration et lancement des analyses BLAST/RPS BLAST
  - Plots     : visualisation des dot plots et détection de diagonales
  - History   : consultation des analyses précédemment enregistrées
  - DB Setup  : configuration de la base de données

----------------------------------------------------------------------
5. PARAMÈTRES UTILISATEUR (user_settings/defaults.json)
----------------------------------------------------------------------

    "window_shape"  : dimensions initiales de la fenêtre (ex. "1200x760")
    "min_window"    : dimensions minimales [largeur, hauteur] en pixels
    "language"      : langue de l'interface (non encore implémenté)
    "lighting_mode" : thème visuel (non encore implémenté)

----------------------------------------------------------------------
6. NOTES
----------------------------------------------------------------------

- Les résultats BLAST sont mis en cache dans la base SQLite.
  Une analyse déjà effectuée avec les mêmes paramètres sera
  rechargée depuis la base sans relancer BLAST+.

- Les fichiers de protéomes (.faa) sont téléchargés depuis NCBI
  et stockés dans le dossier genomes/ lors de chaque nouvelle analyse.

- Les fichiers temporaires BLAST sont gérés via le module tempfile
  de Python et sont supprimés automatiquement après chaque analyse.

====================================================================
