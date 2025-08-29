// An executible to validate CW's Unit Mappers to Attila's db files. //

## ⚠ ENSURE THE 'cw_mapping_validator' FOLDER IS PLACED IN THE CW INSTALLATION FOLDER

# Workflow
1. Use PFM/RPFM to export the unit db's from Attila as .tsv, and place in the "attila_exports" folder, allowing it to create subfolders as necessary. 
You will may need to rename the .tsv's to ensure you don't overwrite it when you repeat it for each of the Attila sources for unit keys.

2. Run 'cw_mapping_validator.exe'. It will process all of the Attila unit key .tsv's and compare that to the CW-to-Attila mapping files in the 
CW installation directory. 