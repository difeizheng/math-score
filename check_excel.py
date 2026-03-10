import pandas as pd
import os

data_dir = r'D:\openclaw\workspace\projects\study\data'
files_list = [f for f in os.listdir(data_dir) if f.endswith('.xlsx')]

print('Checking Excel file structure...')
print(f'Found {len(files_list)} files\n')

if files_list:
    test_file = files_list[0]
    file_path = os.path.join(data_dir, test_file)
    
    print(f'File: {test_file}')
    print()
    
    df = pd.read_excel(file_path)
    
    print('Columns (列名):')
    for i, col in enumerate(df.columns):
        print(f'  {i+1}. [{col}]')
    
    print(f'\nFirst row (前 3 行):')
    print(df.head(3).to_string())
