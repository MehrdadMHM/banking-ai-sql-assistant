max_attempts = 2

for attempt in range(1, max_attempts + 1):
    print(f"Repair attempt: {attempt}")

    success = attempt == 1

    if success:
        print("Repair successful")
        break