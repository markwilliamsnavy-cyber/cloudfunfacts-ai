import boto3
import random
import json

# DynamoDB connection
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("CloudFacts")

# Bedrock Runtime client
bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1"
)

def lambda_handler(event, context):

    # Get all facts from DynamoDB
    response = table.scan()
    items = response.get("Items", [])

    if not items:
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "fact": "No facts found in DynamoDB."
            })
        }

    # Select a random fact
    fact = random.choice(items).get("FactText", "")

    # Claude request payload
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 200,
        "messages": [
            {
                "role": "user",
                "content": f"Rewrite this cloud computing fact as a fun, witty 1-2 sentence fact:\n\n{fact}"
            }
        ]
    }

    # Invoke Claude 4.1 through inference profile
    response = bedrock.invoke_model(
        modelId="arn:aws:bedrock:us-east-1:723300665527:inference-profile/us.anthropic.claude-opus-4-1-20250805-v1:0",
        body=json.dumps(request_body)
    )

    # Parse Claude response
    result = json.loads(response["body"].read())

    ai_text = result["content"][0]["text"]

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({
            "original_fact": fact,
            "fun_fact": ai_text
        })
    }