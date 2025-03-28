ZERO_SHOT_TEMPLATE = """
The following are multiple choice questions (with answers) about software development.
Question: {question}
{multiple_choices}
Answer in JSON format:
```json
{{"answer": "Your selected option here"}}
```
"""


FEW_SHOT_TEMPLATE = """
The following are multiple choice questions (with answers) about software development.

Question: If a sorted array of integers is guaranteed to not contain duplicate values, in order to search for a specific value which of the following algorithms is the most efficient for this task?
(A) Bubble Sort
(B) Linear Search
(C) Insertion Sort
(D) Binary Search

Answer: {{"answer": "D"}}

Question: {question}
{multiple_choices}

Answer in JSON format:
```json
{{"answer": "Your selected option here"}}
``` 
"""

CORRECT_FORMAT_PROMPT = """
You are given the available choices and the chosen choice by the LLM, but it is not in the desired format. The desired format should be only the JSON with an alphabetic answer. Please convert the given answer to the correct format.

Example:
Given:
Choices: ["Option A", "Option B", "Option C", "Option D"]
LLM's answer: "The correct answer is Option B"

Desired output:
```json
{{"answer": "B"}}
```

Your task is to extract the correct letter (A, B, C, or D) from the LLM's answer and format it as shown in the example above.

Choices: {choices}
LLM's answer: {answer}
Desired output:
"""
