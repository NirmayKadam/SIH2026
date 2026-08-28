import csv
import os
from pathlib import Path

def main():
    raw_dir = Path("data/raw/icij_offshore_leaks")
    sub_dir = raw_dir / "subsampled"
    samples_dir = Path("data/samples/icij")
    
    sub_dir.mkdir(parents=True, exist_ok=True)
    samples_dir.mkdir(parents=True, exist_ok=True)

    india_ids = set()
    node_files = [
        "nodes-entities.csv",
        "nodes-officers.csv",
        "nodes-intermediaries.csv",
        "nodes-addresses.csv",
        "nodes-others.csv"
    ]

    # 1. Filter nodes
    for fname in node_files:
        in_path = raw_dir / fname
        out_path = sub_dir / fname
        sample_path = samples_dir / fname
        
        if not in_path.exists():
            continue
            
        with open(in_path, encoding='utf-8') as fin, \
             open(out_path, 'w', encoding='utf-8', newline='') as fout, \
             open(sample_path, 'w', encoding='utf-8', newline='') as fsample:
            
            reader = csv.DictReader(fin)
            writer = csv.DictWriter(fout, fieldnames=reader.fieldnames)
            writer.writeheader()
            
            sample_writer = csv.DictWriter(fsample, fieldnames=reader.fieldnames)
            sample_writer.writeheader()
            
            sample_count = 0
            for row in reader:
                if 'IND' in row.get('country_codes', ''):
                    india_ids.add(row['node_id'])
                    writer.writerow(row)
                    if sample_count < 20:
                        sample_writer.writerow(row)
                        sample_count += 1

    print(f"Extracted {len(india_ids)} India nodes.")

    # 2. Filter relationships
    rel_in = raw_dir / "relationships.csv"
    rel_out = sub_dir / "relationships.csv"
    rel_sample = samples_dir / "relationships.csv"

    if rel_in.exists():
        with open(rel_in, encoding='utf-8') as fin, \
             open(rel_out, 'w', encoding='utf-8', newline='') as fout, \
             open(rel_sample, 'w', encoding='utf-8', newline='') as fsample:
             
            reader = csv.DictReader(fin)
            writer = csv.DictWriter(fout, fieldnames=reader.fieldnames)
            writer.writeheader()
            
            sample_writer = csv.DictWriter(fsample, fieldnames=reader.fieldnames)
            sample_writer.writeheader()
            
            rel_count = 0
            sample_count = 0
            for row in reader:
                if row['node_id_start'] in india_ids and row['node_id_end'] in india_ids:
                    writer.writerow(row)
                    rel_count += 1
                    if sample_count < 30:
                        sample_writer.writerow(row)
                        sample_count += 1
                        
        print(f"Extracted {rel_count} relationships.")

if __name__ == "__main__":
    main()
