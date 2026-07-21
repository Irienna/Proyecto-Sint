import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules

MIN_ENTRIES_FOR_ANALYSIS = 10


def find_food_symptom_rules(entries, top_n=15):
    if len(entries) < MIN_ENTRIES_FOR_ANALYSIS:
        return {"not_enough_data": True, "count": len(entries), "needed": MIN_ENTRIES_FOR_ANALYSIS}

    all_foods = set()
    all_symptoms = set()
    for entry in entries:
        all_foods.update(entry["foods"])
        all_symptoms.update(entry["symptoms"])

    rows = []
    for entry in entries:
        row = {item: False for item in all_foods | all_symptoms}
        for item in entry["foods"]:
            row[item] = True
        for item in entry["symptoms"]:
            row[item] = True
        rows.append(row)

    df = pd.DataFrame(rows)
    min_support = max(0.1, 2 / len(entries))
    frequent_itemsets = apriori(df, min_support=min_support, use_colnames=True)

    if frequent_itemsets.empty:
        return {"not_enough_data": False, "rules": []}

    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.5)

    food_symptom_rules = rules[
        rules["antecedents"].apply(lambda items: items.issubset(all_foods))
        & rules["consequents"].apply(lambda items: items.issubset(all_symptoms) and len(items) > 0)
    ]

    food_symptom_rules = food_symptom_rules.sort_values(
        by=["confidence", "support"], ascending=False
    ).head(top_n)

    result = []
    for _, rule in food_symptom_rules.iterrows():
        antecedent_count = int(rule["antecedent support"] * len(entries))
        both_count = int(rule["support"] * len(entries))
        result.append(
            {
                "antecedent": sorted(rule["antecedents"]),
                "consequent": sorted(rule["consequents"]),
                "support": round(rule["support"], 3),
                "confidence": round(rule["confidence"], 3),
                "cases": both_count,
                "total_matching_antecedent": antecedent_count,
            }
        )

    return {"not_enough_data": False, "rules": result}
