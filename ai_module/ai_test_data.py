from ai_module import analyze_sentiment

TEST_SENTENCES = [
    "Hyundai mileage is great",
    "Toyota service is expensive",
    "BMW launched new car",
    "Honda engine performance amazing",
    "Tata build quality good",
    "Audi maintenance costly",
    "Kia design attractive",
    "Mahindra SUV powerful"
]

for text in TEST_SENTENCES:
    print(text)
    print(analyze_sentiment(text))
    print("-----")
