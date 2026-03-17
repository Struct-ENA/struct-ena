import os
import json
import pandas as pd
from openai import OpenAI 
from tqdm import tqdm
import time


# ==============================================================================
# 1. API invocation and data extraction functions
# ==============================================================================

def generate_response(prompt, system_prompt, max_new_tokens=8, temperature=0.1, top_p=0.9):
    """
    Generate a single model response using ModelScope API (direct connection, no proxy).
    """
    try:
        client = OpenAI(
            base_url='https://api-inference.modelscope.cn/v1',
            api_key='xxxxxxxxxx',  # Please replace this with your ModelScope Token.
        )


        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        
        response = client.chat.completions.create(
            model='Qwen/Qwen3-235B-A22B-Instruct-2507',
            messages=messages,
            max_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            stream=False
        )

        
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"An error occurred during API call or processing: {e}")
        return "API_ERROR"


def extract_code_from_response(response):
    if response is None or "ERROR" in response:
        return response
    response = response.strip()
    import re
    digits = re.findall(r'\b\d+\b', response)
    if digits:
        return int(digits[0])
    return "EXTRACT_FAIL"


# ==============================================================================
# 2. Hinting engineering function 
# ==============================================================================

def create_conflict_prompt(dialogue_turn, context_shangwen, context_xiawen, framework):
    """Create prompts for coding conflicts in parent-child homework."""
    speaker = dialogue_turn.get("speaker", "未知")
    content = dialogue_turn.get("content", "")
    text_to_code = f"{speaker}: {content}"

    prompt = f"""You are a seasoned expert in parenting education and communication analysis. Please, based on the "Parent-Child Homework Conflict" coding framework, determine the following<text2code></text2code>Does the dialogue contain any conflicts and what is the corresponding conflict type code?

        This is the coding framework:
        {framework}

       Please follow the following steps precisely to complete the task:
        1. Read the entire context of<context></context>the dialogue within the marked section.
        2. Identify<text2code></text2code>the unencoded dialogue in the marking.
        3. Based on the precise matching of the context and the coding manual, the most appropriate code is determined.
        4. Reply with a single number, for example: '0' or '1' or '2'... Or '7'. Do not output any other explanation or text.

        Here's the conversation you need to code and its context:
        <context>{context_shangwen}<text2code>{text_to_code}</text2code>{context_xiawen}</context>
    """
    return prompt


# ==============================================================================
# 3. Main processing procedure 
# ==============================================================================

def process_and_code_dialogue_files(root_directory="."):
    """
    We iterate over the JSON dialog file, encode the conflict for each dialog, and save the result to a new JSON file.
    """
    conflict_framework = """
    - 0: No Conflict
    - 1: Knowledge Conflict
    - 2: Expectation Conflict
    - 3: Communication Conflict
    - 4: Learning Method Conflict
    - 5: Rule Conflict
    - 6: Time Management Conflict
    - 7: Focus Conflict
    """
    system_prompt = "You are an expert in parent-child education and communication analysis. Please code the type of conflict for parent-child conversations according to the provided "parent-child Homework Conflict" coding framework."

    try:
        all_items = os.listdir(root_directory)
    except FileNotFoundError:
        print(f"Error: Directory not found '{root_directory}'。")
        return

    date_folders = [item for item in all_items if
                    os.path.isdir(os.path.join(root_directory, item)) and 'month' in item and 'day' in item]

    if not date_folders:
        print(f"No folder'{root_directory}' with the format 'X month Y day 'was found in the directory.")
        return

    for folder_name in sorted(date_folders):
        folder_path = os.path.join(root_directory, folder_name)
        json_files = [f for f in os.listdir(folder_path) if
                      f.endswith('.json') and not f.startswith('coding_Conflict_Type_')]

        for json_file in sorted(json_files):
            file_path = os.path.join(folder_path, json_file)
            print(f"\n--- The file is currently being processed.: {file_path} ---")

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    transcript_data = json.load(f)

                coded_transcript_data = []

                for i, entry in enumerate(tqdm(transcript_data, desc=f"Encoding {json_file}")):
                    shangwen_list = [f"{t.get('speaker')}: {t.get('content')}" for t in
                                     transcript_data[max(0, i - 2):i]]
                    context_shangwen = " ".join(shangwen_list)
                    xiawen_list = [f"{t.get('speaker')}: {t.get('content')}" for t in transcript_data[i + 1:i + 3]]
                    context_xiawen = " ".join(xiawen_list)

                    prompt = create_conflict_prompt(entry, context_shangwen, context_xiawen, conflict_framework)
                    print("########prompt########")
                    print(prompt)
                    response_text = generate_response(prompt, system_prompt)
                    print("########response_text########")
                    print(response_text)
                    code = extract_code_from_response(response_text)
                    print("########code########")
                    print(code)
                    coded_entry = entry.copy()
                    coded_entry["Conflict Type"] = str(code) if code is not None else "ERROR"

                    coded_transcript_data.append(coded_entry)
                    time.sleep(0.5)

                output_filename = f"Qwen3-235B-A22B-2507_coding_Conflict_Type_{json_file}"
                output_filepath = os.path.join(folder_path, output_filename)

                with open(output_filepath, 'w', encoding='utf-8') as f_out:
                    json.dump(coded_transcript_data, f_out, ensure_ascii=False, indent=4)

                print(f"File processing complete. Saved to: {output_filepath}")

            except (json.JSONDecodeError, KeyError) as e:
                print(f"Skipping file {file_path}，format error: {e}")
            except Exception as e:
                print(f"Error processing{file_path}: {e}")

    print("\n🎉 All file processing and coding complete!")


if __name__ == "__main__":
    process_and_code_dialogue_files()