import json
from collections import defaultdict
from csv import DictReader
from datetime import date

##### COLLECT DATA #####

# Get new references
with open("update_v7/new_refs.json", "r") as json_file:
    new_refs: dict = json.load(json_file)
    for segment, references in new_refs.items():
        for reference in references:
            if reference["subtype"] in ("H5", "N1", "NS allele A"):
                references.remove(reference)

# Get mutation mappings for HA, NA, NS
mappings = defaultdict(list)
with open("flumut_db.sql", "r") as sql:
    for line in sql:
        if not line.startswith('INSERT INTO "mutation_mappings" VALUES'):
            continue
        id, mut_name, ref_name, pos, ref, alt = (
            line.strip()[40:-2].replace("'", "").split(",")
        )
        if ref_name not in ("HA", "NA", "NS"):
            continue
        mappings[ref_name].append(
            {"mut_name": mut_name, "pos": pos, "ref": ref, "alt": alt}
        )


# Get NA, HA1 and HA2 numbering conversion dict
def get_conversion_dict(file, subtype):
    with open(file, "r") as tsv:
        dict_reader = DictReader(tsv, delimiter="\t")
        numbering = {}
        for pos_dict in dict_reader:
            numbering[pos_dict[subtype]] = pos_dict
            pos_dict.pop(subtype)
    return numbering


na_numbering = get_conversion_dict("update_v7/na_numbering.tsv", "N1")
ha1_numbering = get_conversion_dict("update_v7/ha1_numbering.tsv", "H5")
ha2_numbering = get_conversion_dict("update_v7/ha2_numbering.tsv", "H5")


# Get HA numbering conversion


# Init
print("PRAGMA foreign_keys = 1;")
print("BEGIN TRANSACTION;")

##### STRUCTURAL CHANGES #####

# Add segment number
print("ALTER TABLE segments ADD COLUMN number INTEGER;")
print("UPDATE segments SET number = 1 WHERE name == 'PB2';")
print("UPDATE segments SET number = 2 WHERE name == 'PB1';")
print("UPDATE segments SET number = 3 WHERE name == 'PA';")
print("UPDATE segments SET number = 4 WHERE name == 'HA';")
print("UPDATE segments SET number = 5 WHERE name == 'NP';")
print("UPDATE segments SET number = 6 WHERE name == 'NA';")
print("UPDATE segments SET number = 7 WHERE name == 'NS';")
print("UPDATE segments SET number = 8 WHERE name == 'MP';")

# Add sequence id column to track references origin
print("ALTER TABLE references ADD COLUMN sequence_id TEXT;")
print("UPDATE references SET sequence_id = 'EPI2414998' WHERE name == 'PB2';")
print("UPDATE references SET sequence_id = 'EPI2414999' WHERE name == 'PB1';")
print("UPDATE references SET sequence_id = 'EPI2414997' WHERE name == 'PA';")
print("UPDATE references SET sequence_id = 'EPI2415001' WHERE name == 'HA';")
print("UPDATE references SET sequence_id = 'EPI2415015' WHERE name == 'NP';")
print("UPDATE references SET sequence_id = 'EPI2415000' WHERE name == 'NA';")
print("UPDATE references SET sequence_id = 'EPI2414996' WHERE name == 'MP';")
print("UPDATE references SET sequence_id = 'EPI2414995' WHERE name == 'NS';")

# Remove unused view
print("DROP VIEW markers_summary;")


##### CLEAN DATA #####

# Remove NA-1:D199G (wrong mutation, coreccted one is NA-1:D199G)
print("DELETE FROM mutations WHERE name = 'NA-5:D199G';")


##### INSERT DATA #####

# Insert new references and annotations
for segment, refs in new_refs.items():
    for ref in refs:
        print(
            f"INSERT INTO 'references' (name, segment_name, sequence, sequence_id) VALUES ('{ref['subtype']}','{segment}','{ref['sequence']}','{ref['sequence_id']}');"
        )
        for annotation in ref["proteins"]:
            print(
                f"INSERT INTO 'annotations' (start, end, protein_name, reference_name) VALUES ('{annotation['start']}','{annotation['end']}','{annotation['name']}','{ref['subtype']}');"
            )


# Insert mutations mappings for new references
def print_insert_mapping(mapping, refs, converter):
    for ref in refs:
        pos = converter[mapping["pos"]][ref["subtype"]]
        if not pos:
            continue
        print(
            f"INSERT INTO 'mutation_mappings' (mutation_name, reference_name, position, ref_seq, alt_seq) VALUES ('{mapping['mut_name']}', '{ref['subtype']}', {pos}, '{mapping['ref']}', '{mapping['alt']}');"
        )


## NS
for mapping in mappings["NS"]:
    print(
        f"INSERT INTO 'mutation_mappings' (mutation_name, reference_name, position, ref_seq, alt_seq) VALUES ('{mapping['mut_name']}', 'NS allele B', {mapping['pos']}, '{mapping['ref']}', '{mapping['alt']}');"
    )
## NA
for mapping in mappings["NA"]:
    print_insert_mapping(mapping, new_refs["NA"], na_numbering)

## HA
for mapping in mappings["HA"]:
    if mapping["mut_name"].startswith("HA1"):
        converter = ha1_numbering
    else:
        converter = ha2_numbering
    print_insert_mapping(mapping, new_refs["HA"], converter)


##### UNIFORM DATA #####

# Update reference names
print('UPDATE "references" SET name = "H5" WHERE name = "HA";')
print('UPDATE "references" SET name = "N1" WHERE name = "NA";')
print('UPDATE "references" SET name = "NS allele A" WHERE name = "NS";')

# Uniforming mutation names
print("UPDATE mutations SET name = replace(name, 'HA1-5', 'HA1');")
print("UPDATE mutations SET name = replace(name, 'HA2-5', 'HA2');")
print("UPDATE mutations SET name = replace(name, 'NA-1', 'NA');")
print("UPDATE mutations SET name = replace(name, 'NS-1', 'NS1');")
print("UPDATE mutations SET name = replace(name, 'NS-2', 'NS2');")

# Rename mutations with pattern PROT:POSAA
print(
    "UPDATE OR REPLACE mutations SET name = substr(name, 1, instr(name, ':')) || substr(name, instr(name, ':') + 2);"
)

# Replace H3 numbering in mutations
print(
    "UPDATE OR IGNORE mutations SET name = substr(name, 1, 4) || (SELECT position FROM mutation_mappings WHERE mutation_name == name AND reference_name == 'H3') || substr(name, length(name)) || '_tmp' WHERE name like 'HA%';"
)
print("UPDATE mutations SET name = replace(name, '_tmp', '');")
print("UPDATE mutations SET name = 'HA1:129V (H5 numbering)' WHERE name == 'HA1:129V';")

# Add column with default position to mutations
print("ALTER TABLE mutations ADD COLUMN default_position INTEGER;")
print(
    "UPDATE mutations SET default_position = substr(name, instr(name, ':') + 1, length(name) - instr(name, ':') - 1);"
)
print(
    "UPDATE mutations SET default_position = 129 WHERE name == 'HA1:129V (H5 numbering)';"
)

# Bump version
print("UPDATE db_version SET major = 7;")
print("UPDATE db_version SET minor = 0;")
print(f"UPDATE db_version SET date = '{date.today():%Y-%m-%d}';")

print("COMMIT;")
