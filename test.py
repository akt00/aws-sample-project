import bcrypt
import uuid
from datetime import datetime
import os
import boto3


print(os.getenv('REGION'))

now = datetime.now()
ts = datetime.timestamp(now)
print(now.strftime('%Y-%M-%D %H:%M:%S'))


pwd = 'hello world'

s1, s2 = bcrypt.gensalt(), bcrypt.gensalt()
h1 = bcrypt.hashpw(pwd.encode(), s1)
h2 = bcrypt.hashpw(pwd.encode(), s2)
print(h1, h1.decode())
print(bcrypt.checkpw(pwd.encode(), h1))
print(bcrypt.checkpw(pwd.encode(), h2))


dynamo = boto3.client('dynamodb', 'us-east-1')

res = dynamo.put_item(
    TableName='Users',
    Item={
        'username': {
            'S': 'admin'
        },
        'password': {
            'S': 'admin1'
        },
    }
)

print(res)

res = dynamo.get_item(
    TableName='Users',
    Item={
        'username': {
            'S': 'admin'
        },
    }
)

print(res)