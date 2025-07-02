# Solaris AI

## Getting Started

### Configure AWS

You need to have an AWS account, and AWS CLI set up on your machine. You'll also need to have Bedrock enabled on AWS (and granted model access to Claude or whatever you want to use).

### Update .env File with AWS Credentials

Create a file named `.env` in `image/`. Do NOT commit the file to `.git`. The file should have content like this:

```
AWS_ACCESS_KEY_ID=XXXXX
AWS_SECRET_ACCESS_KEY=XXXXX
AWS_DEFAULT_REGION=us-east-1
TABLE_NAME=YourTableName
```

This will be used by Docker for when we want to test the image locally. The AWS keys are just your normal AWS credentials and region you want to run this in (even when running locally you will still need access to Bedrock LLM and to the DynamoDB table to write/read the data).

You'll also need a TABLE_NAME for the DynamoDB table for this to work (so you'll have to create that first).

### Installing Requirements

```sh
pip install -r image/requirements.txt
```

### Building the Vector DB

Put all the source files (dataset + ML models) you want into `image/src/data/source/`. Then go `image` and run:

```sh
# Use "--reset" if you want to overwrite an existing DB.
python populate_database.py --reset
```

### Running the App

```sh
# Execute from image/src directory
cd image/src
python -m rag_app.query_rag "What was the total solar power output on 2019-10-01?"
```


### Starting FastAPI Server

```sh
# From image/src directory.
python app_api_handler.py
```

Then go to `http://127.0.0.1:8000/docs` to try it out.

## Using Docker Image

### Build and Test the Image Locally

These commands can be run from `image/` directory to build, test, and serve the app locally.

```sh
docker build --platform linux/amd64 -t aws_rag_app .
```

This will build the image (using linux amd64 as the platform — we need this for `pysqlite3` for Chroma).

```sh
# Run the container using command `python app_work_handler.main`
docker run --rm -it --entrypoint python --env-file .env aws_rag_app app_work_handler.py


```

This will test the image, seeing if it can run the RAG/AI component with a hard-coded question (see ` app_work_handler.py`). But since it uses Bedrock as the embeddings and LLM platform, you will need an AWS account and have all the environment variables for your access set (`AWS_ACCESS_KEY_ID`, etc).

You will also need to have Bedrock's models enabled and granted for the region you are running this in.

## Running Locally as a Server

Assuming you've build the image from the previous step.

```sh


docker run --rm -p 8000:8000 --entrypoint python --env-file .env aws_rag_app app_api_handler.py

```

## Testing Locally

After running the Docker container on localhost, you can access an interactive API page locally to test it: `http://0.0.0.0:8000/docs`.

```sh
curl -X 'POST' \
  'http://0.0.0.0:8000/submit_query' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "query_text": "What was the total solar power output on 2019-10-01?"
}'
```

## Deploy to AWS

I have put all the AWS CDK files into `rag-cdk-infra/`. Go into the folder and install the Node dependencies.

```sh
npm install
```

Then run this command to deploy it (assuming you have AWS CLI already set up, and AWS CDK already bootstrapped). I recommend deploying to `us-east-1` to start with (since all the AI models are there).

```sh
cdk deploy
```
## Front End

### Install Tools to Generate API Client

```sh
npm install @openapitools/openapi-generator-cli -g
```

There is a command script in the package.json file to generate the client library for the API.

```json
{
  "generate-api-client": "openapi-generator-cli generate -i http://0.0.0.0:8000/openapi.json -g typescript-fetch -o src/api-client"
}
```

To use it, it will fetch the OpenAPI schema from `http://0.0.0.0:8000` (assuming it's a FastAPI server and makes it available). And generate a TypeScript client to `src/api-client`.

We'll need to make sure it's generated each time.

### Generate API Client

Generate the client into `src/api-client/` first.

```sh
npm run generate-api-client
```

### Component Library

Using shadcn/ui. I don't think you need to run this, it's already part of the project via Git — but here's what I had to run, just for reference.

```sh
npx shadcn-ui@latest init
```

Then install each component separately.

```sh
npx shadcn-ui@latest add button
npx shadcn-ui@latest add textarea
npx shadcn@latest add card
npx shadcn@latest add skeleton
```
