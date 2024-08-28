def fixSkippedKey(data: dict):
    newData = {}
    i = 1
    for key, value in data.items():
        newKey = f"rule-{i}"
        newData[newKey] = value
        i += 1
    return newData