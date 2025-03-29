SYSTEM_MESSAGE = """You are a coding assistant that help to answer multiple choices of software development and Extract final answer.
The answer selected from the multiple choice options. Should be one alphabet option (A,B,C,D,E,F).
Do not try to correct, adjust or change the question of choices, just choose option base on provided question."""


ZERO_SHOT_TEMPLATE = """
The following are multiple choice questions (with answers) about software development.
Note: Alphabet should be one option in (A,B,C,D,E,F,G)
Question: {question}
{multiple_choices}
Answer in JSON format (in ```json``` brackets):
```json
{{"answer": "Your selected option here"}}
``` 
"""


FEW_SHOT_TEMPLATE = """
The following are multiple choice questions (with answers) about software development.
## Here is an example, do not answer this sample question again
Sample Question: If a sorted array of integers is guaranteed to not contain duplicate values, in order to search for a specific value which of the following algorithms is the most efficient for this task?
(A) Bubble Sort
(B) Linear Search
(C) Insertion Sort
(D) Binary Search

Sample Answer in JSON format:
```json
{{"answer": "D"}}
``` 
Question: {question}
{multiple_choices}

Answer in JSON format (in ```json``` brackets):
```json
{{"answer": "Your selected option here"}}
``` 
"""

CORRECT_FORMAT_PROMPT = """
You are given the question available choices and the chosen choice by the LLM, but it is not in the desired format. 
The desired format should be only the JSON with an alphabetic answer. Please reanswer the question again and convert the given answer to the correct format.
You can consider llm output as reference, should think step by step

Example:
Given:
Question: This is a sample question
Choices: ["Option A", "Option B", "Option C", "Option D"]
LLM's answer: "The correct answer is Option B"

Desired output:
```json
{{"answer": "B"}}
```

Your task is to extract the correct letter (A, B, C, or D) from the LLM's answer and format it as shown in the example above.

Question: {question}
Choices: {choices}
LLM's answer: {answer}
Desired output:
NOTE: Only one option is selected
"""
