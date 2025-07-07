# Solaris AI

**Solaris AI** is a hybrid solar energy forecasting and analytics system that combines Deep Learning and Generative AI to deliver accurate, explainable, and multilingual insights about solar power output. It integrates time-series forecasting models like **ANN** and **LSTM** with a **Retrieval-Augmented Generation (RAG)** pipeline powered by OpenAI models via AWS Bedrock.

Users can interact with Solaris AI through a natural language interface to retrieve real-time insights about solar generation, backed by both raw data and AI predictions. The application is containerized using Docker and deployed on AWS (Lambda, DynamoDB) for scalability and cost-efficiency.

> 🧠 Solaris AI is designed for researchers, policymakers, grid operators, and businesses aiming to make data-driven, transparent, and scalable decisions in the clean energy domain.

## 📦 Getting Started

### 1. Configure AWS

You’ll need:
- An AWS account.
- AWS CLI set up and authenticated.
- Bedrock enabled (with access granted to models like Claude, DeepSeek, etc.).
- A DynamoDB table created.

### 2. Set Up `.env` File

Create a `.env` file in the `image/` directory **(Do NOT commit this file)**:

```
AWS_ACCESS_KEY_ID=XXXXX
AWS_SECRET_ACCESS_KEY=XXXXX
AWS_DEFAULT_REGION=us-east-1
TABLE_NAME=YourTableName
```

This will be used by Docker for when we want to test the image locally. The AWS keys are just your normal AWS credentials and region you want to run this in (even when running locally you will still need access to Bedrock LLM and to the DynamoDB table to write/read the data).

## 🧪 Installing Dependencies

```sh
pip install -r image/requirements.txt
```

## 🧠 Build the Vector DB
Place your dataset and ML models into `image/src/data/source/`.
Then go `image` and run:

```sh
cd image
python populate_database.py --reset  # Add --reset to overwrite existing DB
```

## 💬 Query the App (RAG System)
# Execute from image/src directory

```sh
cd image/src
python -m rag_app.query_rag "What was the total solar power output on 2019-10-01?"
```

![Working RAG Application](images/rag_application.png)

## 🚀 Starting FastAPI Server (Local)
# From image/src directory.
```sh
cd image/src
python app_api_handler.py
```

Then go to `http://127.0.0.1:8000/docs` to try it out.

## 🐳 Docker Usage

### Build Docker Image
```sh
cd image
docker build --platform linux/amd64 -t aws_rag_app .
```

### Test the Image Locally
```sh
docker run --rm -it --entrypoint python --env-file .env aws_rag_app app_work_handler.py
```

This will build the image (using linux amd64 as the platform — we need this for `pysqlite3` for Chroma).

### Run the App Locally as a Server
# Run the container using command `python app_work_handler.main`

```sh
docker run --rm -p 8000:8000 --entrypoint python --env-file .env aws_rag_app app_api_handler.py



```

## 🧪 Test API Locally (with curl)

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

## ☁️ Deploy to AWS

Deployment is inspired by Pixegami’s tutorial on deploying RAG apps to AWS. Highly recommended if you're new to AWS CDK or deploying containerised FastAPI apps to Lambda.

![Backend AWS DynamoDB Query List](images/dynamodb.png)

*Figure: DynamoDB table storing user queries and AI-generated responses.*

1. Install Dependencies
```sh
cd rag-cdk-infra/
npm install
```

2. Deploy
```sh
cdk deploy
```
📝 Make sure AWS CDK is bootstrapped and your AWS CLI is authenticated. Region: us-east-1 is recommended for Bedrock model access.
You will also get an AWS Lambda Function URL that lets you invoke your Lambda function directly (which is the function that handles the RAG logic in our case)

## 🌐 Front End

![Frontend Application UI](images/working_frontend.png)

This is the main UI where users can ask questions and get real-time solar forecasting responses.

### Install OpenAPI Generator

```sh
cd rag-app-frontend
npm install @openapitools/openapi-generator-cli -g
```

### Generate API Client
Replace http://0.0.0.0:8000/ with an AWS Lambda Function URL in package.json 
```json
"scripts": {
  "generate-api-client": "openapi-generator-cli generate -i http://0.0.0.0:8000/openapi.json -g typescript-fetch -o src/api-client"
}
```

### Generate API Client

Then run:

```sh
npm run generate-api-client
```

## 🧩 Component Library (UI)

Using shadcn/ui:

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

## Compile Typescript to js
Once you're done with setting up the frontend, run:
```sh
npm run build
```

🙏 Acknowledgements
Special thanks to [Pixegami](https://github.com/pixegami) for the clear tutorial on deploying RAG apps to AWS Lambda. This project’s deployment approach and architecture are deeply inspired by their video:
📺 [Deploying RAG to AWS Lambda](https://www.youtube.com/watch?v=ldFONBo2CR0)

