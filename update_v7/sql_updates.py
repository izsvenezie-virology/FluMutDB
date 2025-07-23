import json

print("PRAGMA foreign_keys = 1;")
print("BEGIN TRANSACTION;")

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

# Update reference names
print('UPDATE "references" SET name = "H5" WHERE name = "HA";')
print('UPDATE "references" SET name = "N1" WHERE name = "NA";')
print('UPDATE "references" SET name = "NS allele A" WHERE name = "NS";')

# Get new references
with open("update_v7/new_refs.json", "r") as json_file:
    new_refs: dict = json.load(json_file)

for segment, refs in new_refs.items():
    for ref in refs:
        if not ref.get("sequence"):
            print(f"-- [!] Skipping {ref['subtype']}")
            continue
        print(
            f"INSERT INTO 'references' (name, segment_name, sequence, sequence_id) VALUES ('{ref['subtype']}','{segment}','{ref['sequence']}','{ref['sequence_id']}')"
        )
        for annotation in ref["proteins"]:
            print(
                f"INSERT INTO 'annotations' (start, end, protein_name, reference_name) VALUES ('{annotation['start']}','{annotation['end']}','{annotation['name']}','{ref['subtype']}')"
            )
