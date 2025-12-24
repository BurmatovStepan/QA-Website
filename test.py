a = {"1": (1, 2), "2": (1, 2)}
b, c = a.get("3", (None, None))
print(b, c)
