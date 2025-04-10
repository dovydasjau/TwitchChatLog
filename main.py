import re

# Define the log entry format
LOG_PATTERN = re.compile(r"\[(\d{2}:\d{2}:\d{2})] (\w+): (.+)")


def load_logs(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    logs = []
    for line in lines:
        match = LOG_PATTERN.match(line.strip())
        if match:
            time, user, message = match.groups()
            logs.append({"time": time, "user": user, "message": message})
    return logs


def filter_by_user(logs, username):
    return [log for log in logs if log["user"].lower() == username.lower()]


def filter_by_text(logs, text):
    return [log for log in logs if text.lower() in log["message"].lower()]


def sort_by_time(logs):
    return sorted(logs, key=lambda x: x["time"])


def print_logs(logs):
    for log in logs:
        print(f"[{log['time']}] {log['user']}: {log['message']}")


def main():
    file_path = input("Enter the path to your .log file: ").strip()
    logs = load_logs(file_path)

    print("\nHow would you like to sort the chat logs?")
    print("1 - Sort by time")
    print("2 - Filter by username")
    print("3 - Filter by text in message")
    choice = input("Enter your choice (1/2/3): ").strip()

    if choice == "1":
        logs = sort_by_time(logs)
    elif choice == "2":
        username = input("Enter the username to filter by: ").strip()
        logs = filter_by_user(logs, username)
    elif choice == "3":
        text = input("Enter the text to filter messages by: ").strip()
        logs = filter_by_text(logs, text)
    else:
        print("Invalid choice. Showing unsorted logs.")

    print("\n--- Filtered Logs ---")
    print_logs(logs)


if __name__ == "__main__":
    main()
