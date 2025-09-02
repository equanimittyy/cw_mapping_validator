import os
import pandas as pd
import xml.etree.ElementTree as ET
import sys
import re

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)

# Identify working directories
working_dir = application_path
export_dir = os.path.join(working_dir, 'attila_exports','db','main_units_tables')
mapper_dir = '../unit mappers'
settings_dir = '../settings'
settings_paths_file = os.path.join(settings_dir,'Paths.xml')
os.chdir(working_dir)

if os.path.exists(export_dir):
    if not any(file.endswith('.tsv') for file in os.listdir(export_dir)):
        print(f'== Mapping directory exists, but no .tsv mapping were files found! ==')
        print(f'DEBUG: CWD = {working_dir}')
        print(f'DEBUG: EXPORT_DIR = {export_dir}')
        input("Press Enter to quit...")
        quit()
    else:
        print(f'== Mapping files found! ==')
else:
    print(f'== No mapping files directory found in attila_exports. Please ensure you export .tsv files from RPFM/PFM to "attila_exports/db/main_units_tables" ==')
    print(f'DEBUG: CWD = {working_dir}')
    print(f'DEBUG: EXPORT_DIR = {export_dir}')
    input("Press Enter to quit...")
    quit()

# Declare data frame for Attila unit mapping, and merge
df_attila = pd.DataFrame()
for file in os.listdir(export_dir):
    if file.endswith('.tsv'):
        # Define source of file if ends with .tsv
        source_file = os.path.join(export_dir,file)
        source_name = os.path.basename(source_file)
                
        df = pd.read_csv(source_file, header=None, names=['attila_map_key']
                         ,sep='\t', usecols=[0])
        df = df.iloc[2:]
        df['attila_source'] = source_name
        # Append loop
        df_attila = pd.concat([df_attila, df])

# Print merged Attila unit mapping
print(df_attila)
print()
print(f'== Found mapping directories: {os.listdir(mapper_dir)} ==')
print()

# Declare data frame for cultures from Crusader Kings 3 and obtain cultures from Crusader Kings installation.
df_ck3_cultures = pd.DataFrame() 
ck3_dir_path = os.path.dirname(os.path.dirname(ET.parse(settings_paths_file).getroot().find('CrusaderKings').attrib.get('path')))
ck3_culture_dir = os.path.join(ck3_dir_path,'game','common','culture','cultures')
ck3_rows = []
print(f'== Found CK3 culture files: {os.listdir(ck3_culture_dir)} ==')
print()
for file in os.listdir(ck3_culture_dir):
    if file.endswith('.txt'):
        source_file = os.path.join(ck3_culture_dir,file)
        source_name = os.path.basename(source_file)

        with open (source_file, 'r', encoding="utf-8-sig") as culture_txt_file:
            data = culture_txt_file.read()

        culture_txt = re.findall(r"^(\w+)\s*=", data, re.M)
        for culture in culture_txt:
            ck3_rows.append({
                "ck3_culture":culture,
                "ck3_source":source_name
            })
        
df_ck3_cultures = pd.concat([df_ck3_cultures,pd.DataFrame(ck3_rows)],ignore_index=True)
print(df_ck3_cultures)

# Declare data frame for processed cw mapping
df_cultures = pd.DataFrame()
cultures_rows = []
df_factions = pd.DataFrame()
faction_rows = []
df_titles = pd.DataFrame()
titles_rows = []

for mapping in os.listdir(mapper_dir):
        cultures = os.path.join(mapper_dir,mapping,'Cultures')
        factions = os.path.join(mapper_dir,mapping,'Factions')
        titles = os.path.join(mapper_dir,mapping,'Titles')

        # Processing loop for cultures
        if os.path.exists(cultures):
            print(f'== ✝ Cultures found in {mapping}. ==')
            for x in os.listdir(cultures):
                if x.endswith('.xml'):
                    print(f'// ✝ Processing {x}.')
                    cultures_tree = ET.parse(os.path.join(cultures,x))
                    cultures_root = cultures_tree.getroot()
                    for cultures_parent in cultures_root:
                        for cultures_child in cultures_parent:
                            # Update rows
                            cultures_rows.append({
                                "cw_category": 'Culture',
                                "ck3_culture": cultures_child.attrib.get('name'),
                                "cw_culture": cultures_child.attrib.get('faction'),
                                "cw_source_file": x,
                                "cw_source_folder": mapping
                            })              

        # Processing loop for factions
        if os.path.exists(factions):
            print(f'== ⚔ Factions found in {mapping}. ==')
            for x in os.listdir(factions):
                if x.endswith('.xml'):
                    print(f'// ⚔ Processing {x}.')
                    faction_tree = ET.parse(os.path.join(factions,x))
                    faction_root = faction_tree.getroot()
                    for faction_parent in faction_root:
                        for faction_child in faction_parent:
                            # Update rows
                            faction_rows.append({
                                "cw_type": faction_child.tag,
                                "cw_category": 'Faction',
                                "cw_unit_parent": faction_parent.attrib.get('name'),
                                "cw_unit": faction_child.attrib.get('type'),
                                "attila_map_key": faction_child.attrib.get('key'),
                                "cw_source_file": x,
                                "cw_source_folder": mapping
                            })              
                  
        # Processing loop for titles
        if os.path.exists(titles):
            print(f'== ♠ Titles found in {mapping}. ==')
            for x in os.listdir(titles):
                if x.endswith('.xml'):
                    print(f'// ♠ Processing {x}.')
                    titles_tree = ET.parse(os.path.join(titles,x))
                    titles_root = titles_tree.getroot()
                    for titles_parent in titles_root:
                        for titles_child in titles_parent:
                            # Update rows
                            titles_rows.append({
                                "cw_type": titles_child.tag,
                                "cw_category": 'Title',
                                "cw_unit_parent": titles_parent.attrib.get('name'),
                                "cw_unit": titles_child.attrib.get('type'),
                                "attila_map_key": titles_child.attrib.get('key'),
                                "cw_source_file": x,
                                "cw_source_folder": mapping
                            })     

# Append processing results to df
df_cultures = pd.concat([df_cultures,pd.DataFrame(cultures_rows)],ignore_index=True)
df_factions = pd.concat([df_factions,pd.DataFrame(faction_rows)],ignore_index=True)     
df_titles = pd.concat([df_titles,pd.DataFrame(titles_rows)],ignore_index=True)


# Validate df from CW and Attila, and produce report/log
df_attila.to_csv('report_merged_attila_mapping.csv')
df_ck3_cultures.to_csv('report_merged_ck3_cultures.csv')

df_cultures = pd.merge(df_cultures,df_ck3_cultures, on='ck3_culture', how ='left')
df_cultures.to_csv('report_cultures.csv')
df_cultures_error = pd.DataFrame(df_cultures[df_cultures['ck3_source'].isna()])
df_cultures_error.to_csv('report_cultures_error.csv')
print(f'Report produced for culture files.')

df_factions = pd.merge(df_factions,df_attila, on='attila_map_key', how ='left')
df_factions.to_csv('report_factions.csv')
df_factions_error = pd.DataFrame(df_factions[df_factions['attila_source'].isna()])
df_factions_error.to_csv('report_factions_error.csv')
print(f'Report produced for faction files.')

df_titles = pd.merge(df_titles,df_attila, on='attila_map_key', how ='left')
df_titles.to_csv('report_titles.csv')
df_titles_error = pd.DataFrame(df_titles[df_titles['attila_source'].isna()])
df_titles_error.to_csv('report_titles_error.csv')
print(f'Report produced for title files.')
input("Press Enter to quit...")
quit()