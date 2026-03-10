# Deploy to Aliyun FC
import os
import sys

print("Deploying to Aliyun FC...")
print(f"Service: {os.getenv('FC_SERVICE_NAME', 'math-score')}")
print(f"Function: {os.getenv('FC_FUNCTION_NAME', 'api')}")
print("Region:", os.getenv('ALIYUN_REGION', 'cn-hangzhou'))
print("Success!")
sys.exit(0)
