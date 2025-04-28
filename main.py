import re
import os

LOG_PATTERN = re.compile(r"\[(\d{2}:\d{2}:\d{2})] (\w+): (.+)")


# System messages that shouldn't be counted as real chat messages
SYSTEM_MESSAGES = [
    ("connected", "connected"),
    ("joined", "joined channel"),
    ("disconnected", "disconnected"),
    ("server", "server connection timed out, reconnecting"),
    ("twitch", "twitch servers requested us to reconnect, reconnecting"),
]

def is_system_message(log):
    user = log['user'].strip().lower()
    message = log['message'].strip().lower()
    for sys_user, sys_message in SYSTEM_MESSAGES:
        if user == sys_user and message == sys_message:
            return True
    return False


def load_single_log(file_path, source=None):
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    logs = []
    for line in lines:
        line = line.strip()
        time_match = re.match(r"\[(\d{2}:\d{2}:\d{2})] (.+)", line)
        if time_match:
            time, rest = time_match.groups()
            msg_match = re.match(r"(\w+): (.+)", rest)
            if msg_match:
                user, message = msg_match.groups()
            else:
                user_match = rest.split(' ', 1)[0]
                user = user_match
                message = rest
            logs.append({
                "time": time,
                "user": user,
                "message": message,
                "source": source or os.path.splitext(os.path.basename(file_path))[0]
            })
    return logs


def load_logs_from_path(path):
    all_logs = []
    sources = []
    if os.path.isfile(path) and path.endswith(".log"):
        print(f"Loading log file: {path}")
        logs = load_single_log(path)
        all_logs.extend(logs)
        sources.append(os.path.basename(path))
    elif os.path.isdir(path):
        print(f"Loading all .log files from folder: {path}")
        for filename in os.listdir(path):
            if filename.endswith(".log"):
                full_path = os.path.join(path, filename)
                print(f" - {filename}")
                logs = load_single_log(full_path, source=os.path.splitext(filename)[0])
                all_logs.extend(logs)
                sources.append(filename)
    else:
        raise FileNotFoundError("Invalid file or folder path.")
    return all_logs, len(set(sources)) > 1  # True if multiple files


def filter_by_user(logs, username):
    return [log for log in logs if log["user"].lower() == username.lower()]


def filter_by_exact_text(logs, text, case_sensitive=False):
    filtered = []
    count = 0
    if case_sensitive:
        pattern = r'(?:(?<=^)|(?<=\s))' + re.escape(text) + r'(?:(?=\s)|(?=$))'
        flags = 0
    else:
        pattern = r'(?:(?<=^)|(?<=\s))' + re.escape(text) + r'(?:(?=\s)|(?=$))'
        flags = re.IGNORECASE

    for log in logs:
        matches = re.findall(pattern, log["message"], flags)
        if matches:
            count += len(matches)
            filtered.append(log)
    return filtered, count



def filter_by_time_range(logs, start_time=None, end_time=None):
    def in_range(time_str):
        return (not start_time or time_str >= start_time) and (not end_time or time_str <= end_time)

    return [log for log in logs if in_range(log["time"])]


def print_logs(logs, show_source=False):
    for log in logs:
        if show_source and log['source']:
            # Remove everything before the last dash to get just the date
            if '-' in log['source']:
                source_display = f"[{log['source'].split('-', 1)[-1]}] "
            else:
                source_display = f"[{log['source']}] "
        else:
            source_display = ""
        print(f"[{log['time']}] {source_display}{log['user']}: {log['message']}")


def print_summary(original_count, filtered_count, filters_used, search_text=None, word_count=None):
    print("\n--- Summary ---")
    print(f"Original logs count: {original_count}")
    print(f"Filtered logs count: {filtered_count}")
    print(f"Applied filters: {', '.join(filters_used) if filters_used else 'None'}")
    if search_text:
        print(f'Searched for word/emote: "{search_text}"')
    if word_count is not None:
        print(f'Matches found: {word_count} exact match(es)')


def run_filter_menu(logs, show_source=False):
    while True:
        print(f"\nTotal logs count: {len(logs)}")
        print("\nChoose one or more filters to apply:")
        print("1 - Filter by username")
        print("2 - Filter by exact emote/word")
        print("3 - Filter by time range")
        print("4 - Exit")
        choice = input("Enter your filter option(s) (e.g., 1 2 3 or 1 2y 3): ").strip()

        if choice == "4":
            print("Exiting...")
            break

        options = choice.split()
        filters = set()
        case_sensitive = False

        # Handle case sensitivity for exact match
        for opt in options:
            if opt == "2y":
                filters.add("2")
                case_sensitive = True
            else:
                filters.add(opt)

        filtered_logs = [log for log in logs if not is_system_message(log)]
        word_count = 0
        search_text = None
        filters_used = []

        if "1" in filters:
            username = input("Enter the username to filter by: ").strip()
            filtered_logs = filter_by_user(filtered_logs, username)
            filters_used.append(f'Username = "{username}"')

        if "2" in filters:
            search_text = input("Enter the exact emote/word to search for: ").strip()
            filtered_logs, word_count = filter_by_exact_text(filtered_logs, search_text, case_sensitive=case_sensitive)
            filters_used.append(f'Exact word = "{search_text}"' + (" (case-sensitive)" if case_sensitive else ""))

        if "3" in filters:
            print("Enter time range (24h format HH:MM:SS). Leave blank to skip either.")
            start = input("Start time (e.g., 14:00:00): ").strip() or None
            end = input("End time (e.g., 15:30:00): ").strip() or None
            filtered_logs = filter_by_time_range(filtered_logs, start, end)
            time_desc = f"Time Range: "
            if start: time_desc += f"From {start} "
            if end: time_desc += f"To {end}"
            filters_used.append(time_desc.strip())

        print("\n--- Filtered Logs ---")
        print_logs(filtered_logs, show_source)

        print_summary(len(logs), len(filtered_logs), filters_used, search_text, word_count)

        again = input("\nWould you like to apply another filter set on the same file(s)? (y/n): ").strip().lower()
        if again != 'y':
            print("Goodbye!")
            break



def main():
    path = input("Enter the path to your .log file or folder: ").strip()
    try:
        logs, multi_file_mode = load_logs_from_path(path)
        if logs:
            run_filter_menu(logs, show_source=multi_file_mode)
        else:
            print("No valid log entries found.")
    except FileNotFoundError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
