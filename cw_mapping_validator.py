import os
import pandas as pd
import xml.etree.ElementTree as ET

# Identify working directories
working_dir = os.path.dirname(__file__)
export_dir = os.path.join(working_dir, 'attila_exports/db/main_units_tables')
mapper_dir = '../unit mappers'
os.chdir(working_dir)

if os.path.exists(export_dir):
    print(f'== Mapping files found! ==')
else:
    print(f'== No mapping files found in attila_exports. Please ensure you export the .tsv files to "attila_exports/db/main_units_tables" ==')
    input("Press Enter to quit...")
    sys.exit()

# Declare data frame for Attila unit mapping
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
print(os.listdir(mapper_dir))

# Declare data frame for combined cw unit mapping
# df_cultures = pd.DataFrame() -- Not necessary, as cultures do not have Attila unit keys.
df_factions = pd.DataFrame()
df_titles = pd.DataFrame()

for mapping in os.listdir(mapper_dir):
        # culture = os.path.join(mapper_dir,mapping,'Cultures') -- Not necessary, as cultures do not have Attila unit keys.
        factions = os.path.join(mapper_dir,mapping,'Factions')
        titles = os.path.join(mapper_dir,mapping,'Titles')

        # # Appending loop for culture  -- Not necessary, as cultures do not have Attila unit keys.
        # if os.path.exists(culture):
        #     print(f'Culture found in {mapping}.')
        #     for x in os.listdir(culture):
        #         if x.endswith('.xml'):
        #             culture_tree = ET.parse(os.path.join(culture,x))
        #             culture_root = culture_tree.getroot()
        #             print(culture_root)

        # Appending loop for factions
        if os.path.exists(factions):
            print(f'== 🛡 Factions found in {mapping}. ==')
            for x in os.listdir(factions):
                if x.endswith('.xml'):
                    print(f'// 🛡 Processing {x}.')
                    faction_tree = ET.parse(os.path.join(factions,x))
                    faction_root = faction_tree.getroot()
                    for faction_parent in faction_root:
                        for faction_child in faction_parent:
                            # Create new row
                            df_faction_new_row = pd.DataFrame([{
                                "cw_type": faction_child.tag,
                                "cw_category": 'Faction',
                                "cw_unit_parent": faction_parent.attrib.get('name'),
                                "cw_unit": faction_child.attrib.get('type'),
                                "attila_map_key": faction_child.attrib.get('key'),
                                "cw_source_file": x,
                                "cw_source_folder": mapping
                            }])

                            # Append new row
                            df_factions = pd.concat([df_factions,df_faction_new_row])
                  
        # Appending loop for titles
        if os.path.exists(titles):
            print(f'== 👑 Titles found in {mapping}. ==')
            for x in os.listdir(titles):
                if x.endswith('.xml'):
                    print(f'// 👑 Processing {x}.')
                    titles_tree = ET.parse(os.path.join(titles,x))
                    titles_root = titles_tree.getroot()
                    for titles_parent in titles_root:
                        for titles_child in titles_parent:
                            # Create new row
                            df_titles_new_row = pd.DataFrame([{
                                "cw_type": titles_child.tag,
                                "cw_category": 'Title',
                                "cw_unit_parent": titles_parent.attrib.get('name'),
                                "cw_unit": titles_child.attrib.get('type'),
                                "attila_map_key": titles_child.attrib.get('key'),
                                "cw_source_file": x,
                                "cw_source_folder": mapping
                            }])

                            # Append new row
                            df_titles = pd.concat([df_titles,df_titles_new_row])

# Validate data frames from CW and Attila, and produce report/log
df_attila.to_csv('report_merged_attila_mapping.csv')

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
sys.exit()