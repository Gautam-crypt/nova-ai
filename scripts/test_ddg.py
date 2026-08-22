from duckduckgo_search import DDGS

try:
    results = DDGS().text("who is chief minister of uttar pradesh", max_results=3)
    print("Direct DDGS().text() results:")
    for r in results:
        print(r)
except Exception as e:
    print("Error:", e)
