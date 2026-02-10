import requests

texts = [
    "Hyundai mileage is poor in Pune",
    "BMW engine performance amazing",
    "Tata service bad in Mumbai",
    "Toyota comfort very good",
    "Kia design looks premium",
    "Audi price too high",
    "Mahindra SUV power great",
    "Honda maintenance costly"
]

for t in texts:
    requests.post("http://127.0.0.1:8000/ai/analyze", json={"text": t})

print("Demo data added 👍")
