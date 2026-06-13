# CloudFunFacts AI

CloudFunFacts AI is a beginner-friendly serverless AWS project that returns a random cloud computing fact and uses Amazon Bedrock with Claude to rewrite it into a more engaging, conversational response.

The project is designed as a small portfolio application that demonstrates how a static frontend can call an API Gateway endpoint, trigger an AWS Lambda function, read data from DynamoDB, and use a foundation model through Amazon Bedrock.

## Features

- Static web frontend for generating cloud facts
- Serverless API with Amazon API Gateway and AWS Lambda
- DynamoDB table for storing source facts
- Amazon Bedrock Claude integration for AI-enhanced responses
- CORS-ready JSON responses for browser-based requests
- Safe placeholder configuration for public GitHub sharing

## Architecture

```text
User Browser
    |
    v
AWS Amplify Hosting
    |
    v
Amazon API Gateway
    |
    v
AWS Lambda
    |
    +--> Amazon DynamoDB
    |
    +--> Amazon Bedrock Claude
```

## AWS Services Used

**AWS Amplify Hosting**

Hosts the static `index.html` frontend. Amplify is a simple way to deploy a static site directly from a GitHub repository.

**Amazon API Gateway**

Provides the public HTTPS endpoint used by the browser. The frontend sends a request to API Gateway when the user clicks the button.

**AWS Lambda**

Runs the backend Python code in `lambda_function.py`. Lambda retrieves a random fact from DynamoDB, sends it to Claude through Bedrock, and returns a JSON response to the frontend.

**Amazon DynamoDB**

Stores the original cloud computing facts. This project expects a table with a text attribute named `FactText`.

**Amazon Bedrock with Claude**

Rewrites the original fact into a short, fun explanation. Bedrock provides managed access to foundation models without storing model credentials in the frontend.

## Project Structure

```text
.
├── .gitignore
├── README.md
├── index.html
└── lambda_function.py
```

## How the AI Flow Works

1. The user clicks **Generate Fun Fact** in the browser.
2. The frontend calls the API Gateway endpoint.
3. API Gateway invokes the Lambda function.
4. Lambda scans the DynamoDB table and selects one fact.
5. Lambda sends the selected fact to Claude through Amazon Bedrock.
6. Claude returns a rewritten version of the fact.
7. Lambda returns both the original fact and the AI-enhanced fact to the frontend.

## Lambda Configuration

The Lambda function uses environment variables so real AWS values do not need to be committed to GitHub.

| Variable | Required | Example | Purpose |
| --- | --- | --- | --- |
| `AWS_REGION` | No | `us-east-1` | AWS Region for DynamoDB and Bedrock. Defaults to `us-east-1`. |
| `DYNAMODB_TABLE_NAME` | No | `CloudFacts` | DynamoDB table name. Defaults to `CloudFacts`. |
| `BEDROCK_MODEL_ID` | Yes | `YOUR_BEDROCK_MODEL_OR_INFERENCE_PROFILE_ID` | Bedrock model ID or inference profile ID. |
| `ALLOWED_ORIGIN` | No | `https://YOUR_AMPLIFY_DOMAIN` | Browser origin allowed by CORS. Defaults to `*` for demos. |
| `MAX_TOKENS` | No | `200` | Maximum tokens requested from Claude. |

Do not commit real AWS account IDs, ARNs, API Gateway URLs, access keys, or secrets.

## DynamoDB Setup

Create a DynamoDB table for the source facts.

Recommended beginner setup:

- Table name: `CloudFacts`
- Partition key: `FactId`
- Partition key type: `String`

Example item:

```json
{
  "FactId": "fact-001",
  "FactText": "Amazon S3 is designed for 99.999999999% durability."
}
```

The Lambda function reads the `FactText` attribute.

## API Gateway and CORS

The browser calls API Gateway directly, so CORS must be configured correctly.

Recommended setup:

- API type: HTTP API or REST API
- Method: `GET`
- Route path: `/funfact`
- Integration: Lambda proxy integration
- CORS allowed origin: your Amplify URL for production, or `*` for a public demo
- CORS allowed methods: `GET, OPTIONS`
- CORS allowed headers: `Content-Type`

The Lambda response also includes CORS headers:

```json
{
  "Access-Control-Allow-Origin": "YOUR_ALLOWED_ORIGIN",
  "Access-Control-Allow-Headers": "Content-Type",
  "Access-Control-Allow-Methods": "GET,OPTIONS"
}
```

For a public portfolio demo, `*` is easy to test. For a more secure deployment, set `ALLOWED_ORIGIN` to your deployed Amplify domain.

## Bedrock Setup

Before the Lambda function can call Claude, make sure your AWS account has access to the selected Claude model in Amazon Bedrock.

High-level steps:

1. Open Amazon Bedrock in the AWS Console.
2. Enable access to the Claude model you want to use.
3. Copy the model ID or inference profile ID.
4. Add that value to the Lambda environment variable `BEDROCK_MODEL_ID`.
5. Make sure the Lambda IAM role has permission to call `bedrock:InvokeModel`.

Keep model IDs or inference profile IDs out of the committed source code if they include account-specific details.

## IAM Permissions

The Lambda execution role needs permissions for DynamoDB, Bedrock, and CloudWatch Logs.

Minimum permission areas:

- `dynamodb:Scan` for the facts table
- `bedrock:InvokeModel` for the chosen Bedrock model or inference profile
- `logs:CreateLogGroup`
- `logs:CreateLogStream`
- `logs:PutLogEvents`

Use least-privilege permissions when deploying beyond a demo.

## Frontend Setup

The frontend is a single static file: `index.html`.

Before deploying, replace the placeholder API URL:

```javascript
const API_URL = "https://YOUR_API_ID.execute-api.YOUR_REGION.amazonaws.com/funfact";
```

Use your own API Gateway invoke URL. Do not commit a private or production URL if you do not want it public.

## Deployment Steps

### 1. Deploy DynamoDB

Create the `CloudFacts` table and add several items with a `FactText` attribute.

### 2. Deploy Lambda

Create a Python Lambda function and upload `lambda_function.py`.

Set these environment variables:

```text
DYNAMODB_TABLE_NAME=CloudFacts
BEDROCK_MODEL_ID=YOUR_BEDROCK_MODEL_OR_INFERENCE_PROFILE_ID
ALLOWED_ORIGIN=https://YOUR_AMPLIFY_DOMAIN
MAX_TOKENS=200
```

For early local testing, `ALLOWED_ORIGIN=*` is acceptable. Replace it with your Amplify domain before presenting the project as production-like.

### 3. Connect API Gateway

Create an API Gateway route such as:

```text
GET /funfact
```

Connect the route to the Lambda function and enable CORS.

### 4. Update the Frontend

Replace the placeholder `API_URL` in `index.html` with your API Gateway invoke URL.

### 5. Deploy with Amplify

Push the project to GitHub and connect the repository to AWS Amplify Hosting. Amplify can serve the static `index.html` file directly.

## Testing

### Test Lambda in AWS

Use a basic Lambda test event:

```json
{
  "requestContext": {
    "http": {
      "method": "GET"
    }
  }
}
```

Expected successful response shape:

```json
{
  "statusCode": 200,
  "body": "{\"original_fact\":\"...\",\"fun_fact\":\"...\"}"
}
```

### Test API Gateway

After deployment, call your endpoint in a browser or with curl:

```bash
curl https://YOUR_API_ID.execute-api.YOUR_REGION.amazonaws.com/funfact
```

### Test the Frontend

Open `index.html` in a browser or deploy it through Amplify. Click **Generate Fun Fact** and confirm that both the original fact and AI-enhanced fact appear.

## Troubleshooting

**The page says the API Gateway URL is not configured.**

Replace the placeholder `API_URL` in `index.html` with your deployed API Gateway endpoint.

**The browser shows a CORS error.**

Confirm API Gateway CORS settings and the Lambda `ALLOWED_ORIGIN` environment variable. For production-style demos, use the exact Amplify domain.

**Lambda returns a server configuration error.**

Set the `BEDROCK_MODEL_ID` environment variable.

**Lambda cannot find facts.**

Confirm the DynamoDB table name and make sure items include the `FactText` attribute.

**Bedrock returns an access error.**

Confirm model access is enabled in Amazon Bedrock and the Lambda execution role has `bedrock:InvokeModel` permission.

**API Gateway returns 502.**

Check CloudWatch Logs for the Lambda function. The code logs AWS service failures and unexpected Bedrock response formats.

## Security Notes

- Do not commit AWS access keys, secret keys, account IDs, ARNs, or private endpoint URLs.
- Use Lambda environment variables for deployment-specific values.
- Restrict CORS to your Amplify domain for production-style deployments.
- Give the Lambda execution role only the permissions it needs.
- Keep Bedrock access server-side in Lambda, never in browser JavaScript.

## Screenshots

Add screenshots before publishing the repository:

- Frontend home screen before generating a fact
- Frontend result after generating a fact
- Optional AWS architecture diagram

Suggested folder:

```text
docs/screenshots/
```

## Future Improvements

- Add AWS SAM, CDK, Terraform, or CloudFormation for repeatable infrastructure deployment
- Replace the DynamoDB table scan with a more scalable random-selection strategy
- Add automated tests for Lambda response handling
- Add request throttling or API keys for public demos
- Add a loading state and improved accessibility styles in the frontend
- Add a small architecture diagram image to the README

## Author

Mark-Anthony Williams
