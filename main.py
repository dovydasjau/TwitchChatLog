import re
import os

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


def filter_by_time_range(logs, start_time=None, end_time=None):
    def in_range(time_str):
        return (not start_time or time_str >= start_time) and (not end_time or time_str <= end_time)

    return [log for log in logs if in_range(log["time"])]


def print_logs(logs):
    for log in logs:
        print(f"[{log['time']}] {log['user']}: {log['message']}")


def run_filter_menu(logs):
    while True:
        print(f"\nTotal logs count: {len(logs)}")
        print("\nChoose one or more filters to apply:")
        print("1 - Filter by username")
        print("2 - Filter by exact emote/word")
        print("3 - Filter by time range")
        print("4 - Exit")
        choice = input("Enter your filter option(s) (e.g., 1 2 3): ").strip()

        if choice == "4":
            print("Exiting...")
            break

        options = choice.split()
        filters = set(options)
        filtered_logs = logs
        word_count = 0

        if "1" in filters:
            username = input("Enter the username to filter by: ").strip()
            filtered_logs = filter_by_user(filtered_logs, username)

        if "2" in filters:
            text = input("Enter the exact emote/word to search for: ").strip()
            filtered_logs, word_count = filter_by_exact_text(filtered_logs, text)

        if "3" in filters:
            print("Enter time range (24h format HH:MM:SS). Leave blank to skip either.")
            start = input("Start time (e.g., 14:00:00): ").strip() or None
            end = input("End time (e.g., 15:30:00): ").strip() or None
            filtered_logs = filter_by_time_range(filtered_logs, start, end)

        print(f"\nFiltered logs count: {len(filtered_logs)}")
        if "2" in filters:
            print(f'The word/phrase "{text}" appeared {word_count} time(s) (exact match only).')

        print("\n--- Filtered Logs ---")
        print_logs(filtered_logs)

        again = input("\nWould you like to apply another filter set on the same file(s)? (y/n): ").strip().lower()
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
