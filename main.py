import re
import os

# Define the log entry format
LOG_PATTERN = re.compile(r"\[(\d{2}:\d{2}:\d{2})] (\w+): (.+)")


def load_single_log(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    logs = []
    for line in lines:
        match = LOG_PATTERN.match(line.strip())
        if match:
            time, user, message = match.groups()
            logs.append({"time": time, "user": user, "message": message})
    return logs


def load_logs_from_path(path):
    all_logs = []
    if os.path.isfile(path) and path.endswith(".log"):
        print(f"Loading log file: {path}")
        all_logs.extend(load_single_log(path))
    elif os.path.isdir(path):
        print(f"Loading all .log files from folder: {path}")
        for filename in os.listdir(path):
            if filename.endswith(".log"):
                full_path = os.path.join(path, filename)
                print(f" - {filename}")
                all_logs.extend(load_single_log(full_path))
    else:
        raise FileNotFoundError("Invalid file or folder path.")
    return all_logs


def filter_by_user(logs, username):
    return [log for log in logs if log["user"].lower() == username.lower()]


def filter_by_exact_text(logs, text):
    filtered = []
    count = 0
    pattern = r'(?:(?<=^)|(?<=\s))' + re.escape(text) + r'(?:(?=\s)|(?=$))'
    for log in logs:
        matches = re.findall(pattern, log["message"], re.IGNORECASE)
        if matches:
            count += len(matches)
            filtered.append(log)
    return filtered, count


def filter_by_fuzzy_text(logs, text):
    filtered = []
    count = 0
    for log in logs:
        matches = re.findall(re.escape(text), log["message"], re.IGNORECASE)
        if matches:
            count += len(matches)
            filtered.append(log)
    return filtered, count


def sort_by_time(logs):
    return sorted(logs, key=lambda x: x["time"])


def print_logs(logs):
    for log in logs:
        print(f"[{log['time']}] {log['user']}: {log['message']}")


def run_filter_menu(logs):
    while True:
        print(f"\nTotal logs count: {len(logs)}")

        print("\nWhat would you like to do with the chat logs?")
        print("1 - Sort by time")
        print("2 - Filter by exact username")
        print("3 - Filter by exact phrase/emote")
        print("4 - Filter by general text match")
        print("5 - Exit")
        choice = input("Enter your choice (1/2/3/4/5): ").strip()

        filtered_logs = logs

        if choice == "1":
            filtered_logs = sort_by_time(filtered_logs)
            print(f"Sorted logs count: {len(filtered_logs)}")
        elif choice == "2":
            username = input("Enter the username to filter by: ").strip()
            filtered_logs = filter_by_user(filtered_logs, username)
            print(f"Filtered logs count: {len(filtered_logs)}")
        elif choice == "3":
            text = input("Enter the exact phrase/emote to search: ").strip()
            filtered_logs, word_count = filter_by_exact_text(logs, text)
            print(f"Filtered logs count: {len(filtered_logs)}")
            print(f'The word/phrase "{text}" appeared {word_count} time(s) (exact match only).')
        elif choice == "4":
            text = input("Enter the general text to search (will match anything containing this): ").strip()
            filtered_logs, word_count = filter_by_fuzzy_text(logs, text)
            print(f"Filtered logs count: {len(filtered_logs)}")
            print(f'The text "{text}" appeared {word_count} time(s) (partial match).')
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Try again.")
            continue

        print("\n--- Filtered/Sorted Logs ---")
        print_logs(filtered_logs)

        again = input("\nWould you like to run another filter/sort on the same file(s)? (y/n): ").strip().lower()
        if again != 'y':
            print("Goodbye!")
            break


def main():
    path = input("Enter the path to your .log file or folder: ").strip()
    try:
        logs = load_logs_from_path(path)
        if logs:
            run_filter_menu(logs)
        else:
            print("No valid log entries found.")
    except FileNotFoundError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()

