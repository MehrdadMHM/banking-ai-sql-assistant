
max_attempts = 3

for attempt in range(1, max_attempts + 1):
    print(f"Attempt {attempt}")

    validation_passed = False

    if validation_passed:
        print("SQL validated")
        break
else:
    print("All repair attempts failed")
