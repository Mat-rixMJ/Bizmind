import random
import json
import os

def generate_dataset():
    intents = [
        "show", "get", "list", "find", "calculate", "give", "display", "tell me"
    ]

    entities = [
        "sales", "inventory", "profit", "expenses", "orders", "customers",
        "invoices", "stock", "revenue", "returns", "suppliers"
    ]

    filters = [
        "today", "yesterday", "this week", "last week", "this month", "last month",
        "last 3 months", "this year"
    ]

    conditions = [
        "above 1000", "below 500", "greater than 10 units",
        "less than 5 items", "pending", "completed", "cancelled",
        "with highest value", "with lowest value"
    ]

    typos = {
        "sales": ["sles", "sale", "saels"],
        "inventory": ["invntory", "inventry", "stok"],
        "profit": ["profet", "proft"],
        "expenses": ["expns", "expences"],
        "orders": ["ordrs", "odrs"],
        "customers": ["custmers", "custmr"],
    }

    def introduce_typo(word):
        if word in typos:
            return random.choice(typos[word])
        return word

    dataset = []

    for i in range(1100):
        intent = random.choice(intents)
        entity = random.choice(entities)
        time = random.choice(filters)
        condition = random.choice(conditions)

        question = f"{intent} {entity} for {time} {condition}"

        # Add typo randomly
        if random.random() < 0.2:
            words = question.split()
            words = [introduce_typo(w) for w in words]
            question = " ".join(words)

        dataset.append({
            "id": i+1,
            "question": question
        })

    # Ensure scripts directory exists
    output_path = "business_ai_dataset.json"
    with open(output_path, "w") as f:
        json.dump(dataset, f, indent=2)

    print(f"Dataset generated: {output_path}")

if __name__ == "__main__":
    generate_dataset()
