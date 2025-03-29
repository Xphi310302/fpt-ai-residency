import os
import re
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
from prompt_template import (
    FEW_SHOT_TEMPLATE,
    CORRECT_FORMAT_PROMPT,
    ZERO_SHOT_TEMPLATE,
    SYSTEM_MESSAGE,
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


def get_option_probabilities(client, question, options):
    """Query the LLM to get probabilities for each option."""
    from datetime import datetime

    instruction = f"""
    Date (ignore the date): {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    You are given a multiple-choice question. 
    Identify the option that is least likely to be correct.  
    Return a JSON object with the final probabilities for each option.
    Outputformat should be in ```json\n{{alphabet: probability}}``` brackets
    alphabet should be one of [A, B, C, D ,E, F]. 
    Note: output final probability only
    """

    options_text = "\n".join([f"{letter}: {text}" for letter, text in options.items()])
    input_text = f"Question: {question}\nOptions:\n{options_text}"

    # probabilities = eval(response.choices[0].message.content)
    response = client.responses.create(
        model="gpt-4o-mini",
        instructions=instruction,
        input=input_text,
    )
    print(response.output_text)
    match = re.search(r"```json\s*({.*?})\s*```", response.output_text, re.DOTALL)
    probabilities = match.group(1) if match else None
    print(probabilities)
    return eval(probabilities)


def poe_id2_elimination(client, question, options_list):
    """Implements PoE_ID² to eliminate two least likely options and select the best answer."""

    # Convert list of options into a dictionary {letter: value}
    options = {opt.split(": ")[0]: opt.split(": ")[1] for opt in options_list}

    probabilities = get_option_probabilities(client, question, options)

    # Sort options by probability
    sorted_options = sorted(probabilities.items(), key=lambda x: x[1])

    # Eliminate two options with the lowest probability
    remaining_options = {letter: options[letter] for letter, _ in sorted_options[2:]}

    # Recompute probabilities with the remaining options
    probabilities = get_option_probabilities(client, question, remaining_options)

    # Select the option with the highest probability
    final_answer = max(probabilities, key=probabilities.get)
    print("Answer: ", final_answer)
    return final_answer


def get_answer(client, row, max_attempts=2):
    """Get answer using PoE ID² elimination method"""
    for attempt in range(max_attempts):
        try:
            question = row["question"]
            options = row["choices"]

            answer = poe_id2_elimination(client, question, options)
            return answer

        except Exception as e:
            print(
                f"Warning: Error occurred: {e}. (Attempt {attempt + 1}/{max_attempts})"
            )

    print(f"Warning: Failed to get a valid answer after {max_attempts} attempts")
    return None


def process_answers(df, client):
    choices_answer = []
    wrong_format_answer = {}

    # Check if temporary file exists and load previously processed answers
    temp_file_path = "output/temp_choices_answer_gpt_poe.csv"
    start_index = 0
    os.makedirs("output", exist_ok=True)

    if os.path.exists(temp_file_path):
        print(f"Found existing file {temp_file_path}, loading previous answers...")
        temp_df = pd.read_csv(temp_file_path, header=None, names=["index", "answer"])

        # Convert index to integer for proper comparison
        temp_df["index"] = temp_df["index"].astype(int)

        # Get the last processed index
        if not temp_df.empty:
            last_processed_index = temp_df["index"].max()
            start_index = last_processed_index + 1

            # Load previous answers
            for _, row in temp_df.iterrows():
                idx = row["index"]
                answer = row["answer"]

                # Extend choices_answer list if needed
                while len(choices_answer) <= idx:
                    choices_answer.append(None)

                choices_answer[idx] = answer

                # Check if answer is in wrong format
                if answer not in i2choices.values():
                    wrong_format_answer[idx] = answer

            print(
                f"Loaded {len(temp_df)} previous answers. Continuing from index {start_index}."
            )
        else:
            # File exists but is empty
            print("Temporary file exists but is empty. Starting from the beginning.")
            # Clear the file to start fresh
            open(temp_file_path, "w").close()
    else:
        # Create a new file
        open(temp_file_path, "w").close()
        print("Starting new inference process.")

    # Continue processing from where we left off
    for i, row in df.iloc[start_index:].iterrows():
        print(f"Processing index {i}")
        answer = get_answer(client, row)

        # Extend choices_answer list if needed
        while len(choices_answer) <= i:
            choices_answer.append(None)

        choices_answer[i] = answer

        # Write answers to temporary CSV file
        with open(temp_file_path, "a") as f:
            f.write(f"{i},{answer}\n")

        if answer not in i2choices.values():
            print(f"Wrong format answer at index {i}")
            wrong_format_answer[i] = answer

    return choices_answer, wrong_format_answer


def main():
    # Initialize OpenAI client
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    # Load and preprocess data
    test_df = load_and_preprocess_data("data/b6_test_data.csv")

    # Process answers using PoE ID² elimination
    choices_answer, wrong_format_answer = process_answers(test_df, client)

    # Create submission dataframe
    submission = pd.DataFrame({"task_id": test_df["task_id"], "answer": choices_answer})

    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)

    # Save submission to CSV
    submission.to_csv("output/submission_gpt_poe.csv", index=False)
    print("Submission saved to output/submission_gpt_poe.csv")


if __name__ == "__main__":
    main()
