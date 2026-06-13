import boto3
import random
import json
import logging
import os
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
DYNAMODB_TABLE_NAME = os.environ.get("DYNAMODB_TABLE_NAME", "CloudFacts")
BEDROCK_MODEL_ID = os.environ.get(
    "BEDROCK_MODEL_ID",
    "YOUR_BEDROCK_MODEL_OR_INFERENCE_PROFILE_ID"
)
ALLOWED_ORIGIN = os.environ.get("ALLOWED_ORIGIN", "*")
MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "200"))

dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
table = dynamodb.Table(DYNAMODB_TABLE_NAME)
bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name=AWS_REGION
)


def build_response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": ALLOWED_ORIGIN,
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "GET,OPTIONS"
        },
        "body": json.dumps(body)
    }


def lambda_handler(event, context):
    logger.info("Received request")

    http_method = (
        event.get("requestContext", {}).get("http", {}).get("method")
        or event.get("httpMethod")
    )

    if http_method == "OPTIONS":
        return build_response(200, {"message": "CORS preflight successful."})

    if BEDROCK_MODEL_ID == "YOUR_BEDROCK_MODEL_OR_INFERENCE_PROFILE_ID":
        logger.error("BEDROCK_MODEL_ID is not configured")
        return build_response(500, {
            "error": "Server configuration error.",
            "message": "BEDROCK_MODEL_ID must be configured as a Lambda environment variable."
        })

    try:
        response = table.scan()
        items = response.get("Items", [])

        if not items:
            return build_response(200, {
                "original_fact": None,
                "fun_fact": "No facts were found in DynamoDB."
            })

        fact = random.choice(items).get("FactText", "")

        if not fact:
            logger.warning("Selected DynamoDB item did not include FactText")
            return build_response(500, {
                "error": "Data format error.",
                "message": "DynamoDB items must include a FactText attribute."
            })

        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": MAX_TOKENS,
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Rewrite this cloud computing fact as a fun, witty "
                        f"1-2 sentence fact:\n\n{fact}"
                    )
                }
            ]
        }

        bedrock_response = bedrock.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=json.dumps(request_body),
            contentType="application/json",
            accept="application/json"
        )

        result = json.loads(bedrock_response["body"].read())
        ai_text = result["content"][0]["text"]

        return build_response(200, {
            "original_fact": fact,
            "fun_fact": ai_text
        })

    except (ClientError, BotoCoreError) as error:
        logger.exception("AWS service call failed")
        return build_response(502, {
            "error": "AWS service error.",
            "message": "The application could not retrieve or generate a fact."
        })
    except (KeyError, IndexError, json.JSONDecodeError) as error:
        logger.exception("Unexpected Bedrock response format")
        return build_response(502, {
            "error": "AI response error.",
            "message": "The AI response could not be parsed."
        })
    except Exception as error:
        logger.exception("Unhandled Lambda error")
        return build_response(500, {
            "error": "Internal server error.",
            "message": "An unexpected error occurred."
        })
