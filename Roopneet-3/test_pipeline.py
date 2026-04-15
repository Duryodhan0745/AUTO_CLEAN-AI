#!/usr/bin/env python3
"""Test script to verify the pipeline works correctly"""

import pandas as pd
from execution_engine import run_pipeline

# Create a simple test dataset
df = pd.DataFrame({
    'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
    'Age': [25, 30, None, 28, 35],
    'Salary': [50000, 60000, 75000, 55000, None],
    'Department': ['IT', 'HR', 'IT', 'Finance', 'HR'],
    'Score': [85, None, 90, 88, 92]
})

print("Original DataFrame:")
print(df)
print("\n" + "="*50 + "\n")

# Test config 
config = {
    'remove_columns': [],
    'missing_global': 'mean',
    'missing': {},
    'outliers': {'strategy': 'cap'},
    'encoding': {'strategy': 'onehot'},
    'scaling': {'strategy': 'standard'},
    'vif': {'enabled': False, 'threshold': 10},
    'rfe': {'enabled': False},
    'pca': {'enabled': False}
}

try:
    print("Running pipeline with config:")
    print(config)
    print("\n" + "-"*50 + "\n")
    
    cleaned_df, logs = run_pipeline(df, config)
    
    print("Cleaned DataFrame:")
    print(cleaned_df)
    print("\n" + "="*50 + "\n")
    
    print("Pipeline Logs:")
    for i, log in enumerate(logs):
        print(f"\n[Step {i+1}] {log.get('step')}:")
        print(f"  Action: {log.get('action')}")
    
    print("\n✅ Pipeline completed successfully!")
    
except Exception as e:
    import traceback
    print(f"❌ Pipeline failed with error:")
    print(traceback.format_exc())
