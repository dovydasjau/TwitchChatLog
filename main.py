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


def run_filter_menu(logs):
    while True:
        print(f"\nTotal logs count: {len(logs)}")

        print("\nHow would you like to sort/filter the chat logs?")
        print("1 - Sort by time")
        print("2 - Filter by username")
        print("3 - Filter by text in message")
        print("4 - Exit")
        choice = input("Enter your choice (1/2/3/4): ").strip()

        filtered_logs = logs

        if choice == "1":
            filtered_logs = sort_by_time(filtered_logs)
        elif choice == "2":
            username = input("Enter the username to filter by: ").strip()
            filtered_logs = filter_by_user(filtered_logs, username)
        elif choice == "3":
            text = input("Enter the text to filter messages by: ").strip()
            filtered_logs = filter_by_text(filtered_logs, text)
        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Try again.")
            continue

        print(f"Filtered logs count: {len(filtered_logs)}\n")
        print("--- Filtered/Sorted Logs ---")
        print_logs(filtered_logs)

        again = input("\nWould you like to run another filter/sort on the same file? (y/n): ").strip().lower()
        if again != 'y':
            print("Goodbye!")
            break


def main():
    file_path = input("Enter the path to your .log file: ").strip()
    try:
        logs = load_logs(file_path)
        run_filter_menu(logs)
    except FileNotFoundError:
        print("File not found. Please check the path and try again.")


if __name__ == "__main__":
    main()
