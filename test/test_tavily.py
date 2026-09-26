import sys

sys.path.insert(0, "src")

from tools.web_search import web_search


result = web_search.invoke({
    "query": "latest developments in AI agents 2026"
})

print("\nTAVILY RESULT:\n")
print(result)