import os
import json
import pandas as pd
from openai import OpenAI
from tqdm import tqdm
import time
import re
from datetime import datetime

# 1. Add all your API keys to this list
# INSTRUCTION: Replace with your own API keys from ModelScope (https://www.modelscope.cn/)
# Format: ['ms-xxxx', 'ms-yyyy', ...]
api_keys = [
    # Add your API keys here, e.g.:
    # 'ms-your-key-1',
    # 'ms-your-key-2',
]
# api_keys = [
# Add your API keys here.
# ]
# api_keys = [
# Add your API keys here.
# ]
# --- 2. Other configurations ---
ROOT_DIRECTORY = "."
MODEL_ID = 'Qwen/Qwen3-235B-A22B-Instruct-2507'
MAX_TOKENS = 30
TEMPERATURE = 0.0
API_BASE_URL = 'https://api-inference.modelscope.cn/v1'

# 3. API Call and Data Extraction Functions
key_manager = {"current_index": -1, "bad_keys": set()}

# get valid keys
def get_next_valid_key():
    if len(key_manager["bad_keys"]) == len(api_keys): return None
    start_index = (key_manager["current_index"] + 1) % len(api_keys)
    for i in range(len(api_keys)):
        check_index = (start_index + i) % len(api_keys)
        next_key = api_keys[check_index]
        if next_key not in key_manager["bad_keys"]:
            key_manager["current_index"] = check_index
            return next_key
    return None
# generate response by LLMs
def generate_response(prompt, system_prompt):
    max_attempts = len(api_keys)
    for _ in range(max_attempts):
        api_key = get_next_valid_key()
        if api_key is None:
            print("All API keys have failed.")
            return "API_ERROR_ALL_KEYS_FAILED"
        try:
            client = OpenAI(base_url=API_BASE_URL, api_key=api_key)
            messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
            response = client.chat.completions.create(
                model=MODEL_ID, messages=messages, max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE, top_p=1.0, stream=False
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            error_message = str(e)
            if "401" in error_message or "Unauthorized" in error_message or "invalid api key" in error_message.lower():
                print(f"\n❌ Key ...{api_key[-4:]} is invalid. Removing from pool.")
                key_manager["bad_keys"].add(api_key)
            else:
                print(f"\n⚠️ API call with key ...{api_key[-4:]} failed: {e}")
                print("   Retrying with the next key in 3 seconds...")
                time.sleep(3)
    return "API_ERROR_ALL_ATTEMPTS_FAILED"


# extract codes from response
def extract_codes_from_response(response):
    """extract one or many behavior codes and a conflict code"""
    if response is None or "ERROR" in response: return [], 0
    try:
        # use "findall" extract all behavior codes
        behavior_matches = re.findall(r"B_(\d+)", response, re.IGNORECASE)
        b_codes = [int(code) for code in behavior_matches]

        # use "search" extract an only conflict code
        conflict_match = re.search(r"C_(\d+)", response, re.IGNORECASE)
        c_code = int(conflict_match.group(1)) if conflict_match else 0

        # if not find B_codes，answer is B_0，return [0]
        if not b_codes and "B_0" in response:
            b_codes = [0]

        return b_codes, c_code
    except Exception as e:
        print(f"extract failed: '{response}'. Error: {e}")
        return [], 0

# 4. Prompt Engineering Function
ultimate_prompt_framework = """
# Task Description
You are a family education expert, and your task is to analyze the specific behaviors of parents during homework assistance. You need to carefully review the provided dialogue content, identify and capture dialogue segments that reflect parental behavior, and classify these behaviors using predefined behavior categories. You must also identify if the parent's utterance is part of a conflict.

# Behavior Categories
## Positive Behaviors
B_1: **Encouragement (ENC)**
- Code Definition: The parent actively supports the child's efforts and progress through words or actions, boosting the child's confidence and motivation to learn, helping them overcome difficulties.
- Usage Guidelines: Use when the parent provides positive support and encouragement, especially when the child encounters difficulties, and the parent maintains a positive attitude regardless of the outcome.
- Example:
- Parent: "You've worked really hard, keep it up! I believe in you!"
- Parent: "Don’t worry, we’ll take it step by step, you’ll definitely get it."

B_2: **Labelled Praise (LP)**
- Code Definition: The parent explicitly points out specific behaviors or achievements of the child and offers praise, helping the child recognize their concrete progress and strengths.
- Usage Guidelines: Use when the parent clearly identifies a specific behavior, achievement, or performance of the child and provides positive feedback.
- Example:
- Parent: "You did this addition problem perfectly, no mistakes at all!"
- Parent: "Your handwriting is really neat this time, keep it up!"

B_3: **Unlabelled Praise (UP)**
- Code Definition: The parent offers general praise to the child but does not point out any specific behaviour or achievement.
- Usage Guidelines: Use when the parent gives unlabelled praise without mentioning specific details or actions.
- Example:
- Parent: "You're doing great, keep going!"
- Parent: "Wow, amazing!"

B_4: **Guided Inquiry (GI)**
- Code Definition: The parent guides the child to think independently and solve problems through questions or hints, rather than directly providing the answer, encouraging the child to explore and think critically.
- Usage Guidelines: Use when the parent helps the child find solutions through questions or hints rather than directly giving the answer.
- Example:
- Parent: "Where do you think this letter should go?"
- Parent: "What strategy can we use to solve this problem? Think about a few ways."

B_5: **Setting Rules (SR)**
- Code Definition: The parent sets clear rules or requirements for the child to complete their homework, helping the child establish good study habits and time management skills.
- Usage Guidelines: Use when the parent sets specific rules and requires the child to follow them, typically related to the order of tasks, time, or completion standards.
- Example:
- Parent: "You need to finish your language homework first before you can watch cartoons."
- Parent: "You have to finish all your homework before dinner, then you can go out to play."

B_6: **Sensitive Response (SRS)**
- Code Definition: The parent responds to the child's emotions, needs, and behaviors in a timely, appropriate, and empathetic manner. The parent perceives the child's feelings and provides emotional support.
- Usage Guidelines: Use when the parent recognizes the child’s emotions and offers understanding and emotional comfort or support.
- Example:
- Parent: "I know you're feeling tired, let's take a break and continue later, okay?"
- Parent: "Are you finding this problem difficult? It’s okay, we’ll go over it together."

## Neutral Behaviors
B_7: **Direct Instruction (DI)**
- Code Definition: The parent directly tells the child how to complete a task or solve a problem without using an exploratory or guided approach.
- Example:
- Parent: "You should do it like this, add 4 to 6, and it equals 10."
- Parent: "Just copy the answer directly, don’t overthink it."

B_8: **Information Teaching (IT)**
- Code Definition: The parent imparts new knowledge or skills to the child through explanations, such as explaining concepts or lessons, to help the child understand new study material.
- Example:
- Parent: "The word ‘tree’ is written with a wood radical on the left and ‘inch’ on the right, let’s write it together."
- Parent: "The multiplication table goes like this, two times two equals four, two times three equals six. Let’s memorize these first."

B_9: **Error Correction (EC)**
- Code Definition: The parent points out mistakes in the child’s homework and guides them to make corrections.
- Example:
- Parent: "You missed the ‘wood’ radical here, write it again."
- Parent: "This addition is wrong, redo it, and make sure to align the columns."

B_10: **Monitoring (MON)**
- Code Definition: The parent periodically checks the child’s homework progress or completion to ensure tasks are done on time.
- Example:
- Parent: "How many pages have you written? Let me check for mistakes."
- Parent: "I’ll check your pinyin homework today to see if there are any issues."

B_11: **Direct Command (DC)**
- Code Definition: The parent uses clear, direct language to command the child to perform a task or behavior, often with a strong, imperative tone.
- Example:
- Parent: "Go do your math homework right now, no more delays!"
- Parent: "Stop playing with your toys and finish copying your pinyin."

B_12: **Indirect Command (IC)**
- Code Definition: The parent uses a more indirect approach to convey a request to the child, such as a suggestion or implication, rather than giving a direct order.
- Example:
- Parent: "Have you finished your homework? Maybe it's time to get it done?"
- Parent: "Let’s finish the homework first, so we don’t have to worry about it later."

## Negative Behaviors
B_13: **Criticism & Blame (CB)**
- Code Definition: The parent expresses negative evaluations of the child’s mistakes or behavior, directly blaming the child for their shortcomings, potentially using belittling language.
- Example:
- Parent: "How could you get such an easy character wrong?"
- Parent: "I’ve told you a thousand times, why can't you remember?"

B_14: **Forcing & Threatening (FT)**
- Code Definition: The parent applies pressure or threatens consequences to force the child to comply with their demands, aiming to achieve the desired behavior.
- Example:
- Parent: "If you don’t finish your homework, you won’t get to play with your blocks!"
- Parent: "If you don’t finish it, I’ll take away your toys!"

B_15: **Neglect & Indifference (NI)**
- Code Definition: The parent shows disregard or indifference to the child’s needs or emotions, providing no attention or response.
- Example:
- Child: "Mom, can you help me with this problem?"
- Parent (ignores the child and continues using the phone).

B_16: **Belittling & Doubting (BD)**
- Code Definition: The parent belittles or doubts the child’s abilities, directly undermining the child’s confidence and motivation.
- Example:
- Parent: "How can you be so dumb, you can’t even do simple addition?"
- Parent: "With grades like yours, there’s no way you’ll get into a good school."

B_17: **Frustration & Disappointment (FD)**
- Code Definition: The parent expresses feelings of frustration or disappointment due to the child’s performance not meeting expectations.
- Example:
- Parent: "I didn’t expect you to do so poorly, you really let me down."
- Parent: "I thought you would do better, I guess I was wrong."

B_18: **Impatience & Irritation (II)**
- Code Definition: The parent shows impatience or irritation with the child’s performance not meeting expectations.
- Example:
- Parent: "Why are you so slow? I’ve been waiting forever!"
- Parent: "How come you still haven’t finished? You’re always dragging your feet!"

## Additional Codes
B_19: **Child Response/Question**: Use for simple child responses, questions, or statements of fact that don't fit other parental behavior categories. (e.g., "Okay," "I don't know," "This is hard.").
B_0: **Not Applicable**: Use if the utterance is unrelated to the homework task or too fragmented to classify.

# Parent-Child Conflict Identification Task
You must also identify if the utterance is part of an ongoing conflict.

## Conflict Categories
C_1: **Expectation Conflict (EC)**: Discrepancy between parent's high expectations and child's performance.
- Example:
- Parent: "You should score full marks like your classmates. How can you make mistakes on such easy questions?"
- Child: "I've done my best! Why do you always think I'm worse than others?"

C_2: **Communication Conflict (CC)**: Conflict arising from negative communication styles like yelling or belittling.
- Example:
- Parent: "What's wrong with you? I've explained this so many times, and you still don't get it!"
- Child: "I don't want to listen to you anymore! You always yell at me like this!"

C_3: **Learning Method Conflict (LMC)**: Disagreements on how to do the homework.
- Example:
- Parent: "You can't study like this; you should finish all the questions first and then check them!"
- Child: "This is how I like to do it! Why should I follow your way?”

C_4: **Rule Conflict (RC)**: Conflict over rules, boundaries, and autonomy.
- Example:
- Parent: "You must do your homework right after dinner; no more procrastinating!"
- Child: "I want to play a little longer! You always control everything!"

C_5: **Time Management Conflict (TMC)**: Disagreement on allocation of time and energy.
- Example:
- Parent: "You always leave your homework until late at night. Your efficiency is too low!"
- Child: "I prefer studying later. I can't focus in the morning!"

C_6: **Knowledge Conflict (KC)**: Conflict caused by a mismatch in knowledge or understanding.
- Example:
- Parent: "This problem is so simple; how can you not get it?"
- Child: "What you’re explaining is different from what the teacher said. I don’t understand."

C_7: **Focus Conflict (FC)**: Conflict arising from the parent's dissatisfaction with the child's focus.
- Example:
- Parent: "What are you daydreaming about? Focus and do your homework!"
- Child: "I'm not daydreaming; I'm thinking about how to solve the problem!"

C_0: **No Conflict**
- Usage Guidelines: Use this if the interaction is neutral, positive, or does not show signs of tension or disagreement.

# FINAL INSTRUCTIONS
An utterance can have one or more behaviors. You MUST identify all applicable codes.

You MUST return your answer in the following strict format, and nothing else:
`Behavior Code: B_CODE_1, B_CODE_2, ..., Conflict Code: C_CODE`

- Example 1 (Single behavior): `Behavior Code: B_4, Conflict Code: C_0`
- Example 2 (Multiple behaviors and a conflict): `Behavior Code: B_9, B_13, Conflict Code: C_2`
- Example 3 (Child response): `Behavior Code: B_19, Conflict Code: C_0`
- Example 4 (No specific behavior): `Behavior Code: B_0, Conflict Code: C_0`

---
Now, code the utterance from the speaker in `<text2code>` within the following dialogue.
"""

def create_coding_prompt(dialogue_turn, context_shangwen, context_xiawen):
    text_to_code = f"{dialogue_turn.get('speaker', 'Unknown')}: {dialogue_turn.get('content', '')}"
    final_prompt = (
        f"{ultimate_prompt_framework}\n"
        "<context>\n"
        f"{context_shangwen}\n"
        f"<text2code>{text_to_code}</text2code>\n"
        f"{context_xiawen}\n"
        "</context>"
    )
    print("need to code")
    print(text_to_code)
    return final_prompt



# 5. Main Processing Logic
def process_and_code_to_excel(root_directory=ROOT_DIRECTORY):
    system_prompt = "You are an expert AI assistant specializing in communication analysis."

    behavior_codes = [f"B_{i}" for i in range(1, 20)]
    conflict_codes = [f"C_{i}" for i in range(1, 8)]
    all_code_columns = behavior_codes + conflict_codes

    try:
        all_items = os.listdir(root_directory)
    except FileNotFoundError:
        print(f"Error: Directory not found at '{root_directory}'.")
        return

    date_folders = [item for item in all_items if
                    os.path.isdir(os.path.join(root_directory, item)) and re.match(r'^\d{8}', item)]
    if not date_folders:
        print(f"No date-formatted folders (YYYYMMDD) found in '{root_directory}'.")
        return

    for folder_name in sorted(date_folders):
        folder_path = os.path.join(root_directory, folder_name)
        json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]

        # ✅ UPDATED: Loop moved to process and save one file at a time.
        for json_file in sorted(json_files):
            file_path = os.path.join(folder_path, json_file)

            # --- New Filename Logic ---
            match = re.search(r'(\d{4})(\d{2})(\d{2})', folder_name)
            if not match:
                print(f"Skipping folder with unexpected name: {folder_name}")
                continue
            month, day = match.groups()

            json_basename = os.path.splitext(json_file)[0]
            excel_filename = f"{year}{month}{day}_{json_basename}.xlsx"
            excel_filepath = os.path.join(folder_path, excel_filename)

            # --- Resume Logic: Check if this specific Excel file already exists ---
            if os.path.exists(excel_filepath):
                print(f"Skipping {json_file}, corresponding Excel file already exists: {excel_filename}")
                continue

            print(f"\nProcessing file: {json_file}. Output will be saved to {excel_filename}")

            all_dialogues_data = []  # Reset for each new file

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    transcript_data = json.load(f)

                progress_bar = tqdm(enumerate(transcript_data), total=len(transcript_data), desc=f"Coding {json_file}")

                for i, entry in progress_bar:
                    one_hot_entry = {col: 0 for col in all_code_columns}
                    one_hot_entry.update({
                        'file_id': json_basename, 'dialogue_id': entry.get('id', i),
                        'speaker': entry.get('speaker', 'Unknown'), 'content': entry.get('content', '')
                    })

                    active_key_index = key_manager['current_index']
                    active_key = api_keys[active_key_index] if active_key_index != -1 else api_keys[0]
                    progress_bar.set_postfix_str(f"ID: {entry.get('id', i)}, Key...{active_key[-4:]}")

                    context_shangwen = " ".join([f"{t.get('speaker', 'N/A')}: {t.get('content', '')}" for t in
                                                 transcript_data[max(0, i - 3):i]])
                    context_xiawen = " ".join(
                        [f"{t.get('speaker', 'N/A')}: {t.get('content', '')}" for t in transcript_data[i + 1:i + 4]])
                    prompt = create_coding_prompt(entry, context_shangwen, context_xiawen)
                    # print("######prompt########")
                    # print(prompt)
                    response_text = generate_response(prompt, system_prompt)
                    print("######response_text########")
                    print(response_text)
                    if "API_ERROR_ALL_KEYS_FAILED" in response_text:
                        print("🚨 Stopping due to all API keys failing.")
                        break

                    b_codes, c_code = extract_codes_from_response(response_text)
                    print("######b_code########")
                    print(b_codes)
                    print("######c_code########")
                    print(c_code)
                    # Loop through the list of behavior codes
                    for code in b_codes:
                        if code != 0:
                            # Check if the column exists to prevent errors
                            column_name = f"B_{code}"
                            if column_name in one_hot_entry:
                                one_hot_entry[column_name] = 1

                    # Handle the single conflict code
                    if c_code != 0:
                        column_name = f"C_{c_code}"
                        if column_name in one_hot_entry:
                            one_hot_entry[f"C_{c_code}"] = 1
                    print("one_hot_entry")
                    print(one_hot_entry)
                    all_dialogues_data.append(one_hot_entry)

                if 'response_text' in locals() and "API_ERROR_ALL_KEYS_FAILED" in response_text:
                    break

            except Exception as e:
                print(f"An error occurred while processing {file_path}: {e}")

            # --- Save the collected data for the current file to its Excel file ---
            if all_dialogues_data:
                df = pd.DataFrame(all_dialogues_data)
                info_cols = ['file_id', 'dialogue_id', 'speaker', 'content']
                ordered_cols = info_cols + [col for col in all_code_columns if col in df.columns]
                df = df[ordered_cols]
                df.to_excel(excel_filepath, index=False, engine='openpyxl')
                print(f"✅ File {json_file} processed. Data saved to: {excel_filepath}")
            else:
                print(f"No data processed for file {json_file}.")

        if len(key_manager["bad_keys"]) == len(api_keys):
            print("🚨 Stopping script as all API keys have failed.")
            break

    print("\n🎉 All processing complete!")


# --- Execution Entry Point ---
if __name__ == "__main__":
    process_and_code_to_excel()