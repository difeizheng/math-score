import requests
import os

url = 'http://localhost:8808/api/import/excel'

data_dir = r'D:\openclaw\workspace\projects\study\data'
files_list = [f for f in os.listdir(data_dir) if f.endswith('.xlsx')]

print('Testing import API...')
print(f'Found {len(files_list)} Excel files')

if files_list:
    test_file = files_list[0]
    file_path = os.path.join(data_dir, test_file)
    
    print(f'Testing with: {test_file}')
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (test_file, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            response = requests.post(url, files=files, timeout=30)
            
        print(f'Status Code: {response.status_code}')
        print(f'Response: {response.json()}')
    except Exception as e:
        print(f'Error: {type(e).__name__}: {e}')
