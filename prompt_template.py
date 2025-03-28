ZERO_SHOT_TEMPLATE = """
The following are multiple choice questions ( with answers ) about software development .
Question : {question}
{multiple_choices}
Answer :
"""


FEW_SHOT_TEMPLATE = """
The following are multiple choice questions (with answers) about software development.

Question: If a sorted array of integers is guaranteed to not contain duplicate values, in order to search for a specific value which of the following algorithms is the most efficient for this task?
(A) Bubble Sort
(B) Linear Search
(C) Insertion Sort
(D) Binary Search

Answer: The answer is (D).

Question: {question}
{multiple_choices}

Answer:
"""
