import boto3 

client= boto3.client("s3","us-east-1") 

response = client.list_buckets() 

print("Buckets en tu cuenta de S3:")  

for bucket in response['Buckets']:  

    print(f"- {bucket['Name']}")