### This script analyzes a Whatsapp chat export file and returns the raw data as csv plus output files (html & json) with the following statistics:
### - Total number of messages per person
### - Average message length per person (in characters)
### - Total number of characters per person
### - Total number of characters for all messages

# Wat hebben we allemaal nodig?
import re
from collections import defaultdict
import pandas as pd
import json
from datetime import datetime
import argparse
import os

def analyze_chat(file_path):
    # Generate timestamp
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')

    # Create output directory in the same location as the input file
    output_dir = os.path.join(os.path.dirname(file_path), os.path.splitext(os.path.basename(file_path))[0], 'output')
    os.makedirs(output_dir, exist_ok=True)

    # Regex to match each line of the chat (separate individual messages, but considering multi-line / line break messages)
    line_pattern = re.compile(r"^\d{2}-\d{2}-\d{4} \d{2}:\d{2} - (.*?): (.*)$")

    # Initialize dicts for counts and char length
    message_count = defaultdict(int)
    total_char_count_per_person = defaultdict(int)
    total_char_count_all = 0

    # Initialize list for raw data
    raw_data = []

    # Process the file
    with open(file_path, 'r', encoding='utf-8') as file:
        previous_line = ''
        for line in file:
            match = line_pattern.match(line)
            if match:
                # If the previous line is not empty, add it to the raw data
                if previous_line:
                    date_time, person_message = previous_line.split(' - ', 1)
                    date, time = date_time.split(' ', 1)
                    if ': ' in person_message:
                        person_name, message = person_message.split(': ', 1)
                        raw_data.append([date, time, person_name, message])
                        # Update the dictionaries
                        message_count[person_name] += 1
                        total_char_count_per_person[person_name] += len(message)
                        total_char_count_all += len(message)
                previous_line = line
            else:
                # If the line does not match the pattern, concat it to the previous line
                previous_line += line

        # Add last line to the raw data
        if previous_line:
            date_time, person_message = previous_line.split(' - ', 1)
            date, time = date_time.split(' ', 1)
            if ': ' in person_message:
                person_name, message = person_message.split(': ', 1)
                raw_data.append([date, time, person_name, message])
                # Update the dictionaries
                message_count[person_name] += 1
                total_char_count_per_person[person_name] += len(message)
                total_char_count_all += len(message)

    # Create DataFrame for raw data
    raw_data_df = pd.DataFrame(raw_data, columns=['Date', 'Time', 'Person', 'Message'])

    # Calculate avg. char length / message / person
    average_char_length_per_person = {person: total_char_count_per_person[person] / message_count[person] 
                                     for person in message_count}

    # Create DataFrame for chat stats
    chat_stats_df = pd.DataFrame({
        'Person': list(message_count.keys()),
        'Total Messages': list(message_count.values()),
        'Average Message Length (chars)': [round(avg, 2) for avg in average_char_length_per_person.values()],
        'Total Characters': list(total_char_count_per_person.values())
    })

    # Calculate total number of messages and overall average message length
    total_messages = sum(message_count.values())
    overall_average_message_length = total_char_count_all / total_messages

    # Adding a row for the total character count for all messages
    total_row = {'Person': 'Total (All Persons)', 'Total Messages': total_messages, 
                 'Average Message Length (chars)': round(overall_average_message_length, 2), 
                 'Total Characters': total_char_count_all}
    chat_stats_df = chat_stats_df.append(total_row, ignore_index=True)

    # Convert DataFrame to JSON
    chat_stats_json = chat_stats_df.to_json(orient='records')

    # Print formatted text to stdout / console (returned to n8n for optional interface with Google drive)
    print(chat_stats_df.to_string(index=False))

    # Save the raw data to a CSV file (used by WA-graphs.py)
    raw_data_csv_filename = os.path.join(output_dir, f'raw-data.csv')
    raw_data_df.to_csv(raw_data_csv_filename, index=False)

    # Write formatted HTML to output directory
    html_output_filename = os.path.join(output_dir, f'summary.html')
    chat_stats_df.to_html(html_output_filename, index=False)

    # Save JSON data to file
    json_output_filename = os.path.join(output_dir, f'summary.json')
    with open(json_output_filename, 'w') as json_file:
        json_file.write(chat_stats_json)

    return chat_stats_json

# CLI path argument config, defaults to ./data/chat.txt file (no example in repo, bring your own!).
parser = argparse.ArgumentParser(description='Analyze a Whatsapp chat export file (txt).')
parser.add_argument('file_path', nargs='?', default='./data/chat.txt', 
                    help='the path to the chat export file')

# Parse CLI arguments
args = parser.parse_args()

# Use the function with the path to the txt chat export file
chat_statistics = analyze_chat(args.file_path)
