import os
import json
import pandas as pd
from openai import OpenAI
from tqdm import tqdm
import time
import re


# ==============================================================================
# 1. API call and data extraction function
# ==============================================================================

def generate_response(prompt, system_prompt, max_new_tokens=8, temperature=0.1, top_p=0.9):
    """
    Generate a single model response (adapted for ModelScope API).
    """
    try:
        client = OpenAI(
            base_url='https://api-inference.modelscope.cn/v1',
            api_key='xxxxxxxxx',  #  Replace with your ModelScope Token here
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
        print(f"Error during API call or processing: {e}")
        return "API_ERROR"


def extract_code_from_response(response):
    """Extract the encoded numbers from the model response."""
    if response is None or "ERROR" in response:
        return response
    response = response.strip()
    digits = re.findall(r'\b\d+\b', response)
    if digits:
        return int(digits[0])
    return "EXTRACT_FAIL"


# ==============================================================================
# 2. Hinting engineering 
# ==============================================================================

def create_help_strategy_prompt(dialogue_turn, context_shangwen, context_xiawen, framework):
    """
    Create prompt for parental help strategy coding.
    """
    # Only code parent utterances
    speaker = dialogue_turn.get("speaker", "Unknown")
    if speaker != 'parent':
        return None  # Return None if not parent; main flow will skip coding

    content = dialogue_turn.get("content", "")
    text_to_code = f"{speaker}: {content}"

    prompt = f"""You are an expert in parent-child education and communication analysis. Please classify the parental help-giving behavior in <text2code></text2code> using the "Parental Help Strategy Taxonomy" framework, and provide its corresponding strategy code.

        This is the coding framework:
        {framework}

        Please follow these steps strictly:
        1. Read the full dialogue context within <context></context> tags to understand the parent's intention.
        2. Locate the utterance to be coded within <text2code></text2code> tags.
        3. Match precisely with the coding manual based on context, selecting the strategy code that best describes the parental behavior.
        4. Reply with only a single number, e.g., `11` or `20` or `33`. Do not output any other explanation or text. If the utterance does not fit any help strategy, reply with `0`.

        Here's the conversation you need to code and its context:
        <context>{context_shangwen}<text2code>{text_to_code}</text2code>{context_xiawen}</context>
    """
    return prompt


# ==============================================================================
# 3. Main processing flow
# ==============================================================================

def process_and_code_dialogue_files(root_directory="."):
    """
Traverse JSON dialogue files, code help strategies for each parent utterance, and save results to new JSON files.
    """
    # --- Parental Help Strategy Taxonomy Framework ---
    parental_help_framework = """
# Macro Dimension: Autonomy Support - Codes start with 1
## Meso/Micro Strategies:
- 10: Socratic: Guiding child to find answers through questioning. (e.g., "What are your thoughts on this problem?")
- 11: Nurturant: Handling child's frustration through empathy and rapport-building. (e.g., "I can see you're a bit frustrated. This problem is indeed challenging.")
- 12: Indirect: Hinting at mistakes through questions rather than direct criticism. (e.g., "Would you like to double-check this calculation?")
- 13: Reflective: Prompting child to articulate their thinking process clearly. (e.g., "Can you walk me through how you arrived at this answer?")
- 14: Encouraging: Using motivational language to build child's confidence and perseverance. (e.g., "Don't give up, you're almost there!")
- 15: Labelled Praise: Praising specific behaviors or efforts. (e.g., "You checked your homework again, that's great.")
- 16: Guided Inquiry: Asking questions to guide child's thinking. (e.g., "What should we do next?")
- 17: Sensitive Response: Recognizing and responding to child's emotional state. (e.g., "Let's take a break. You look a bit tired.")

# Macro Dimension: Cognitive/Content Support - Codes start with 2
## Meso/Micro Strategies:
- 20: Direct Instruction: Directly telling child the solution, steps, or answer. (e.g., "You should add these two numbers first.")
- 21: Information Teaching: Explaining concepts or providing background knowledge. (e.g., "The meaning of this word is...")
- 22: Modeling: Demonstrating how to perform a task or solve a problem. (e.g., "Look, this is how I do it...")
- 23: Providing Analogies: Using real-world examples to make abstract concepts concrete. (e.g., "It's like dividing a pie into pieces.")
- 24: Error Correction: Explicitly pointing out mistakes. (e.g., "You made a mistake here.")

# Macro Dimension: Control - Codes start with 3
## Meso/Micro Strategies:
- 30: Intrusive Monitoring: Checking or correcting homework without being asked. (e.g., leaning over to look at child's work and pointing)
- 31: Pressuring: Using commands or disappointed expressions to force child to act. (e.g., "Hurry up and write!")
- 32: Task Takeover: Completing part or all of the homework for the child. (e.g., "Let me write this for you.")
- 33: Criticism and Blame: Making negative evaluations of child or their work. (e.g., "How could you get such a simple question wrong?")
- 34: Forcing and Threatening: Using coercive tactics. (e.g., "No TV until you finish your homework.")
- 35: Belittling and Doubting: Undermining child's confidence. (e.g., "You can't even do this?")
- 36: Impatience and Irritation: Expressing impatience with child's progress or performance. (e.g., "Are you done yet? Why so slow!")
# Other
- 0: Not Applicable / No Help-Giving: Dialogue unrelated to homework assistance, or cannot be categorized into any of the above.
    """
    # --- Updated system prompt to match new framework ---
    system_prompt = "You are an expert in parent-child education and communication analysis. Please code parent dialogue using the provided Parental Help Strategy Taxonomy framework."

    try:
        all_items = os.listdir(root_directory)
    except FileNotFoundError:
        print(f"Error: Directory '{root_directory}' not found.")
        return

    date_folders = [item for item in all_items if
                    os.path.isdir(os.path.join(root_directory, item)) and re.match(r'^\d{8}', item)]

    if not date_folders:
        print(f"No date-formatted folders (YYYYMMDD) found in directory '{root_directory}'.")
        return

    for folder_name in sorted(date_folders):
        folder_path = os.path.join(root_directory, folder_name)
        json_files = [f for f in os.listdir(folder_path) if
                      f.endswith('.json') and not f.startswith('coding_Help_Strategy_')]  # Prevent reprocessing

        for json_file in sorted(json_files):
            file_path = os.path.join(folder_path, json_file)
            print(f"\n--- Processing file: {file_path} ---")

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    transcript_data = json.load(f)

                coded_transcript_data = []

                for i, entry in enumerate(tqdm(transcript_data, desc=f"Encoding{json_file}")):

                    coded_entry = entry.copy()

                    # Check if speaker is parent
                    if entry.get("speaker") == 'parent':
                        shangwen_list = [f"{t.get('speaker')}: {t.get('content')}" for t in
                                         transcript_data[max(0, i - 3):i]]  # Expanded context window
                        context_shangwen = " ".join(shangwen_list)
                        xiawen_list = [f"{t.get('speaker')}: {t.get('content')}" for t in
                                       transcript_data[i + 1:i + 4]]  # Expanded context window
                        context_xiawen = " ".join(xiawen_list)

                        # --- Call updated prompt function ---
                        prompt = create_help_strategy_prompt(entry, context_shangwen, context_xiawen,
                                                             parental_help_framework)
                        # print(prompt)

                        # --- Print debug info (comment out if not needed) ---
                        print("\n######## PROMPT ########")
                        print(prompt)

                        response_text = generate_response(prompt, system_prompt)

                        print("######## RESPONSE ########")
                        print(response_text)

                        code = extract_code_from_response(response_text)

                        print("######## EXTRACTED CODE ########")
                        print(code)

                        # --- Update output key name ---
                        coded_entry["Help_Strategy_Code"] = str(code) if code is not None else "ERROR"
                    else:
                        # If not parent, skip coding and assign empty value
                        coded_entry["Help_Strategy_Code"] = "N/A"  # Not Applicable

                    coded_transcript_data.append(coded_entry)
                    time.sleep(0.5)  # Respect API rate limits

                output_filename = f"Qwen3-235B-A22B-2507_coding_Help_Strategy_{json_file}"
                output_filepath = os.path.join(folder_path, output_filename)

                with open(output_filepath, 'w', encoding='utf-8') as f_out:
                    json.dump(coded_transcript_data, f_out, ensure_ascii=False, indent=4)

                print(f"File processing complete. Saved to:{output_filepath}")

            except (json.JSONDecodeError, KeyError) as e:
                print(f"Skipping file {file_path}，format error: {e}")
            except Exception as e:
                print(f"Error processing{file_path} : {e}")

    print("\n🎉 All file processing and coding complete!")


if __name__ == "__main__":
    # Modify the path below to your data root directory
    # Example: process_and_code_dialogue_files("/path/to/your/data")
    process_and_code_dialogue_files()