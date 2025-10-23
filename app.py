def ask_research_agent(question):
    docs = retriever.get_relevant_documents(question)
    context = "\n".join([doc.page_content for doc in docs])

    prompt = f"""Use the following research notes to answer the question clearly and concisely.

Research Notes:
{context}

Question:
{question}
"""

    response = llm(prompt, max_new_tokens=300)[0]["generated_text"]
    return response