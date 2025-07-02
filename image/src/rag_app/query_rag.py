from dataclasses import dataclass
from typing import List
from langchain.prompts import ChatPromptTemplate
from langchain_aws import ChatBedrock
from rag_app.get_chroma_db import get_chroma_db

from rag_app.prompts import PROMPT_TEMPLATE

BEDROCK_MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"

@dataclass
class QueryResponse:
    query_text: str
    response_text: str
    sources: List[str]

def query_rag(query_text: str) -> QueryResponse:
    db = get_chroma_db()
    results = db.similarity_search_with_score(query_text, k=10)  # get more candidates

    # Try to extract a date from the query
    import re
    date_match = re.search(r"\d{4}-\d{2}-\d{2}", query_text)
    date_str = date_match.group(0) if date_match else None

    # Filter results for the date
    filtered_results = []
    if date_str:
        for doc, score in results:
            if date_str in doc.page_content or date_str in str(doc.metadata.get("datetime", "")):
                filtered_results.append((doc, score))
        # If we found any, use them; else fallback to original results
        if filtered_results:
            results = filtered_results

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _ in results])
    context_text = context_text[:4000]
    sources = [doc.metadata.get("id", "unknown") for doc, _ in results]

    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE).format(
        context=context_text,
        question=query_text,
    )
    print(prompt)

    # Generate response from Claude
    model = ChatBedrock(model_id=BEDROCK_MODEL_ID)
    response = model.invoke(prompt)

    # Display and return the result
    response_text = response.content
    print(f"\n🧠 Response:\n{response_text}\n📄 Sources: {sources}\n")

    return QueryResponse(
        query_text=query_text,
        response_text=response_text,
        sources=sources
    )

# Example use
if __name__ == "__main__":
    # query = "Why is solar power output lower on 2019-02-07 at 12:00:00. Wouldn't it be higher since solar radiation intensity is highest around noon?"
    # query = "What was the total solar power output on 2017-10-01?"
    query = "What time of the day usually has the most solar power output?"
    # query = "What model is being used to forecast solar power?"
    query_rag(query)



