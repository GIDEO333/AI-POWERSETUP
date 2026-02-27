from server import search_memory

print("Testing search_memory with a vague, locally-phrased query containing typos:")
query = "recal memori yg kmrin kita setvp app proxy enteng di terminal buat antigravity"
print(f"Query: {query}\n")

result = search_memory(query, n_results=2)
print("Result:")
print(result)
