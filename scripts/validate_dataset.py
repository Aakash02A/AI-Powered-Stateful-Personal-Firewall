import pandas as pd
import json
import sys
from pathlib import Path

def validate_dataset():
    print("=== Dataset Validation ===")
    
    schema_path = Path("ml/models/feature_schema.json")
    if not schema_path.exists():
        print("FAIL: feature_schema.json not found")
        sys.exit(1)
        
    with open(schema_path, "r") as f:
        schema = json.load(f)
        
    expected_features = schema.get("features", [])
    print(f"Expected Features ({len(expected_features)}): {expected_features}")
    
    dataset_path = Path("ml/data/dataset.csv") # We'll just check one or all
    
    # We will check all dataset_pcap_*.csv
    from glob import glob
    files = glob("ml/data/dataset_pcap_*.csv")
    if not files:
        print("FAIL: No dataset files found")
        sys.exit(1)
        
    total_flows = 0
    missing_values = 0
    duplicate_rows = 0
    
    for file in files:
        print(f"\nChecking {file}...")
        df = pd.read_csv(file)
        
        # 1. Check strict feature ordering
        file_features = [col for col in df.columns if col in expected_features]
        if file_features != expected_features:
            print(f"FAIL: Feature order mismatch in {file}")
            print(f"Expected: {expected_features}")
            print(f"Got     : {file_features}")
            sys.exit(1)
            
        # 2. Check missing values
        mv = df.isnull().sum().sum()
        missing_values += mv
        if mv > 0:
            print(f"FAIL: Found {mv} missing values in {file}")
            sys.exit(1)
            
        # 3. Check data types (ensure numeric)
        for col in expected_features:
            if not pd.api.types.is_numeric_dtype(df[col]):
                print(f"FAIL: Non-numeric feature {col} in {file}")
                sys.exit(1)
                
        # 4. Check duplicates
        dupes = df.duplicated().sum()
        duplicate_rows += dupes
        
        # 5. Check constant features (zero variance)
        for col in expected_features:
            if df[col].nunique() <= 1:
                print(f"WARNING: Feature {col} is constant in {file}")
                # We won't strictly fail on constant, but we log it.
                
        total_flows += len(df)
        print(f"PASS: {file} is valid. Flows: {len(df)}")
        
    print("\n=== Validation Summary ===")
    print(f"Total Flows Validated: {total_flows}")
    print(f"Total Missing Values: {missing_values}")
    print(f"Total Duplicate Rows: {duplicate_rows}")
    print("PASS: Dataset validation completed successfully.")
    sys.exit(0)

if __name__ == "__main__":
    validate_dataset()
