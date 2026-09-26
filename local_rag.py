import os

def search_local_documents(query: str, docs_folder="documents"):
    if not os.path.exists(docs_folder):
        os.makedirs(docs_folder)
        return "No 'documents' folder found."

    query_words = query.lower().split()
    relevant_snippets = []

    for filename in os.listdir(docs_folder):
        if filename.endswith((".txt", ".md")):
            file_path = os.path.join(docs_folder, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    score = sum(1 for word in query_words if word in content.lower())
                    if score > 0:
                        relevant_snippets.append(f"--- File: {filename} ---\n{content[:1000]}")
            except Exception as e:
                print(f"Error reading {filename}: {e}")

    if not relevant_snippets:
        return "No matching local documents found for that query."

    return "\n\n".join(relevant_snippets)

def search_memory(query: str):
    return search_local_documents(query)

def save_memory(user_input: str, assistant_response: str, docs_folder="documents"):
    if not os.path.exists(docs_folder):
        os.makedirs(docs_folder)
    
    memory_file = os.path.join(docs_folder, "chat_history.txt")
    log_entry = f"User: {user_input}\nJarvis: {assistant_response}\n---\n"
    
    with open(memory_file, "a", encoding="utf-8") as f:
        f.write(log_entry)