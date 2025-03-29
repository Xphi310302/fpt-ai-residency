import os
import re
import json
import requests
import pandas as pd
from dotenv import load_dotenv
from prompt_template import (
    FEW_SHOT_TEMPLATE,
    CORRECT_FORMAT_PROMPT,
    ZERO_SHOT_TEMPLATE,
)

# Replace with your actual localtunnel URL
LOCALTUNNEL_URL = "https://yummy-buses-behave.loca.lt"

load_dotenv()


i2choices = {i: chr(65 + i) for i in range(7)}  # A to G


def load_and_preprocess_data(file_path):
    df = pd.read_csv(file_path)
    df["choices"] = df["choices"].apply(lambda x: eval(x))
    df["choices"] = df["choices"].apply(
        lambda x: [f"{i2choices[i]}: {x[i]}" for i in range(len(x))]
    )
    return df


def chat_completion(
    prompt,
    system_message="You are a helpful coding assistant.",
    max_tokens=512,
    temperature=0.01,
):
    response = requests.post(
        f"{LOCALTUNNEL_URL}/chat/completions",
        headers={"Content-Type": "application/json"},
        json={
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ],
            "max_new_tokens": max_tokens,
            "temperature": temperature,
        },
    )

    return response.json()["generated_text"]


def get_answer(input_text, max_attempts=2):
    system_message = "You are a coding assistant that helps to answer multiple choice questions about software development. Extract the final answer as a single alphabet option (A,B,C,D,E,F)."

    for attempt in range(max_attempts):
        try:
            response = chat_completion(
                prompt=input_text,
                system_message=system_message,
                max_tokens=512,
                temperature=0.01,
            )

            # Extract the answer from the response
            print("Response:", response)
            content = response
            match = re.search(
                r'```json\s*{\s*"answer"\s*:\s*"([^"]+)"\s*}\s*```',
                content,
            )
            if match:
                return match.group(1)
            print(
                f"Warning: No match found in the response (Attempt {attempt + 1}/{max_attempts})"
            )
        except Exception as e:
            print(
                f"Warning: Error occurred: {e}. (Attempt {attempt + 1}/{max_attempts})"
            )
    print(f"Warning: Failed to get a valid answer after {max_attempts} attempts")
    return None


def correct_format(question, choices, llm_output):
    input_text = CORRECT_FORMAT_PROMPT.format(
        question=question, choices=choices, answer=llm_output
    )

    system_message = "The answer selected from the multiple choice options should be one alphabet option (A,B,C,D,E,F)."

    response = chat_completion(
        prompt=input_text,
        system_message=system_message,
        max_tokens=512,
        temperature=0.01,
    )

    content = response
    match = re.search(r'```json\s*{\s*"answer"\s*:\s*"([^"]+)"\s*}\s*```', content)
    return match.group(1) if match else None


# def correct_format(question, choices, llm_output, client):
#     input_text = CORRECT_FORMAT_PROMPT.format(
#         question=question, choices=choices, answer=llm_output
#     )
#     response = client.responses.create(
#         model="gpt-4o-mini",
#         instructions="The answer selected from the multiple choice options should be one alphabet option (A,B,C,D,E,F).",
#         input=input_text,
#     )
#     match = re.search(
#         r'```json\s*{\s*"answer"\s*:\s*"([^"]+)"\s*}\s*```', response.output_text
#     )
#     return match.group(1) if match else None


def process_answers(df, prompt_template=FEW_SHOT_TEMPLATE):
    choices_answer = []
    wrong_format_answer = {}
    for i, row in df.iterrows():
        print(i)
        input_text = prompt_template.format(
            question=row["question"], multiple_choices=row["choices"]
        )
        answer = get_answer(input_text)

        # Handle None answers
        if answer is None:
            answer = "A"  # Default to A if no answer could be extracted
            print(f"No answer extracted at index {i}, defaulting to 'A'")

        choices_answer.append(answer)
        # Write answers to temporary CSV file
        with open("output/temp_choices_answer.csv", "a") as f:
            f.write(f"{i},{answer}\n")

        if answer not in i2choices.values():
            print(f"Wrong format answer at index {i}")
            wrong_format_answer[i] = answer
    return choices_answer, wrong_format_answer


def correct_wrong_formats(df, wrong_format_answer):
    correct_format_answer = {}
    successful_corrections = 0
    none_corrections = 0
    for index, llm_output in wrong_format_answer.items():
        try:
            question = df.iloc[index]["question"]
            choices = df.iloc[index]["choices"]
            corrected_output = correct_format(question, choices, llm_output)
            if corrected_output:
                correct_format_answer[index] = corrected_output
                successful_corrections += 1
            else:
                correct_format_answer[index] = "A"
                none_corrections += 1
        except IndexError:
            print(f"Warning: Index {index} is out of bounds. Defaulting to 'A'")
            correct_format_answer[index] = "A"
            none_corrections += 1
    print(f"Successfully corrected: {successful_corrections}")
    print(f"Defaulted to 'A': {none_corrections}")
    return correct_format_answer


def main(template):
    test_df = load_and_preprocess_data("data/b6_test_data.csv")

    choices_answer, wrong_format_answer = process_answers(
        test_df, prompt_template=template
    )
    correct_format_answer = correct_wrong_formats(test_df, wrong_format_answer)

    for i, answer in correct_format_answer.items():
        choices_answer[i] = answer

    submission = pd.DataFrame({"task_id": test_df["task_id"], "answer": choices_answer})

    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)

    submission.to_csv("output/submission.csv", index=False)
    print("Submission saved to output/submission.csv")


if __name__ == "__main__":
    main(FEW_SHOT_TEMPLATE)
