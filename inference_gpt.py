import os
import re
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from prompt_template import (
    FEW_SHOT_TEMPLATE,
    CORRECT_FORMAT_PROMPT,
    ZERO_SHOT_TEMPLATE,
)

load_dotenv()


i2choices = {i: chr(65 + i) for i in range(7)}  # A to G


def load_and_preprocess_data(file_path):
    df = pd.read_csv(file_path)
    df["choices"] = df["choices"].apply(lambda x: eval(x))
    df["choices"] = df["choices"].apply(
        lambda x: [f"{i2choices[i]}: {x[i]}" for i in range(len(x))]
    )
    return df


def get_answer(input_text, client, model="gpt-4o-mini", max_attempts=2):
    for attempt in range(max_attempts):
        try:
            response = client.responses.create(
                model=model,
                instructions="You are a coding assistant that helps to answer multiple choice questions about software development. Extract the final answer as a single alphabet option (A,B,C,D,E,F).",
                input=input_text,
            )
            match = re.search(
                r'```json\s*{\s*"answer"\s*:\s*"([^"]+)"\s*}\s*```',
                response.output_text,
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


def correct_format(question, choices, llm_output, client):
    input_text = CORRECT_FORMAT_PROMPT.format(
        question=question, choices=choices, answer=llm_output
    )
    response = client.responses.create(
        model="gpt-4o-mini",
        instructions="The answer selected from the multiple choice options should be one alphabet option (A,B,C,D,E,F).",
        input=input_text,
    )
    match = re.search(
        r'```json\s*{\s*"answer"\s*:\s*"([^"]+)"\s*}\s*```', response.output_text
    )
    return match.group(1) if match else None


def process_answers(df, client, prompt_template=FEW_SHOT_TEMPLATE):
    choices_answer = []
    wrong_format_answer = {}
    for i, row in df.iterrows():
        print(i)
        input_text = prompt_template.format(
            question=row["question"], multiple_choices=row["choices"]
        )
        answer = get_answer(input_text, client)
        choices_answer.append(answer)
        if answer not in i2choices.values():
            print(f"Wrong format answer at index {i}")
            wrong_format_answer[i] = answer
    return choices_answer, wrong_format_answer


def correct_wrong_formats(df, wrong_format_answer, client):
    correct_format_answer = {}
    successful_corrections = 0
    none_corrections = 0
    for index, llm_output in wrong_format_answer.items():
        question = df.iloc[index]["question"]
        choices = df.iloc[index]["choices"]
        corrected_output = correct_format(question, choices, llm_output, client)
        if corrected_output:
            correct_format_answer[index] = corrected_output
            successful_corrections += 1
        else:
            correct_format_answer[index] = "A"
            none_corrections += 1
    print(f"Successfully corrected: {successful_corrections}")
    print(f"Defaulted to 'A': {none_corrections}")
    return correct_format_answer


def main(template):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    test_df = load_and_preprocess_data("data/b6_test_data.csv")

    choices_answer, wrong_format_answer = process_answers(
        test_df, client, prompt_template=template
    )
    correct_format_answer = correct_wrong_formats(test_df, wrong_format_answer, client)

    for i, answer in correct_format_answer.items():
        choices_answer[i] = answer

    submission = pd.DataFrame({"task_id": test_df["task_id"], "answer": choices_answer})
    submission.to_csv("output/submission.csv", index=False)
    print("Submission saved to output/submission.csv")


if __name__ == "__main__":
    main(ZERO_SHOT_TEMPLATE)
