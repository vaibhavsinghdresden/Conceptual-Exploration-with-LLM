from openai import OpenAI
import re

def set_prompt(objects, frames, examples,df, implications="", premise=[], conclusion=[]):
    return set_prompt_big(objects, frames, examples,df, implications, premise, conclusion)

def set_prompt_object(objects, frames, examples, implications="", premise=[], conclusion=[]):
    return set_prompt_big_object(objects, frames, examples, implications, premise, conclusion)

def set_prompt_small(objects, frames, examples,df, implications="", premise=[], conclusion=[]):

    if len(premise) == 0 and len(conclusion) == 0:
        implications = implications.split('=>')
        premise = [line.strip() for line in implications[0].split(',')]
        conclusion = [line.strip() for line in implications[1].split(',')]
    else:
        premise = list(premise)
        conclusion = list(conclusion)


    prompt = "Current Word Meaning List:\n"

    for i in range(len(frames)):
        prompt += f'{i+1}. "{frames[i]}"\n'

    premise_prompt = ' and '.join(f'"{word}"' for word in premise)
    conclusion_prompt = ' and '.join(f'"{word}"' for word in conclusion)

    prompt += "\nCheck the below hypothesis :\n"
    prompt += f'Every word that conveys the meaning(s) {premise_prompt} also conveys the meaning(s) {conclusion_prompt}\n\n'
    # Every word in any language that conveys the meaning "{premise_prompt}" also conveys the meanings "{conclusion_prompt}"
    # Every word in any language other than English that conveys the meaning "{premise_prompt}" also conveys the meanings "{conclusion_prompt}"

    prompt += "Return the result as a valid JSON object using the following logic : \n\n"
    prompt += f"If the hypothesis holds"
    prompt += """
{
"output": "YES"
}
"""
    prompt += f"\nOtherwise, return only one counter-example refuting the hypothesis"
    prompt += """
{
"output": "NO",
"word": "<Language of the word> : <name of the word>",
"meaning": ["""

    for premise in premise:
        prompt += f'"{premise}",'
    prompt += f'"<all other meanings from the Word Meaning List, if any apply>"],\n'
    prompt += "Respond with only a valid JSON object.Do not include markdown syntax (like triple backticks) or any explanatory text."

    return prompt


def set_prompt_mid(objects, frames, examples,df, implications="", premise=[], conclusion=[]):
    if len(premise) == 0 and len(conclusion) == 0:
        implications = implications.split('=>')
        premise = [line.strip() for line in implications[0].split(',')]
        conclusion = [line.strip() for line in implications[1].split(',')]
    else:
        premise = list(premise)
        conclusion = list(conclusion)

    prompt = ""
    prompt += "We are analyzing word meanings from different languages.\n"
    prompt += "\n"
    prompt += "Current Word Meaning List:\n"

    for i in range(len(frames)):
        prompt += f'{i}. "{frames[i]}"\n'

    prompt += "\n"
    prompt += "Hypothesis to Test:\n"

    premise_prompt = ' and '.join(f'"{word}"' for word in premise)
    conclusion_prompt = ' and '.join(f'"{word}"' for word in conclusion)
    prompt += f'Every word that conveys the meaning(s) {premise_prompt} also conveys the meaning(s) {conclusion_prompt}\n'

    prompt += f"""
Instructions:
1. Search for all words that include the meaning(s) {premise_prompt}.
2. For each word check whether it also conveys the meaning(s) {conclusion_prompt}
"""
    prompt += "3. Return the result as a valid JSON object using the following logic : \n\n"
    prompt += f"If the hypothesis holds (i.e., all relevant words have meanings {conclusion_prompt})"
    prompt += """
{
"output": "YES"
}
"""
    conclusion_prompt_or = ' or '.join(f'"{word}"' for word in conclusion)
    prompt += f"\nOtherwise, return a counter-example word that has all of the following meaning(s): {premise_prompt}, but does not have at least one of the following meaning(s): {conclusion_prompt_or}"
    prompt += """
{
"output": "NO",
"word": "<Language of the word>:<name of the word>",
"meaning": ["""

    for premise in premise:
        prompt += f'"{premise}",'
    prompt += f'"<all other meanings from the Word Meaning List, if any apply>"],\n'
    prompt += """

Respond with only a valid JSON object. Do not include markdown syntax (like triple backticks) or any explanatory text."""

    return prompt

def set_prompt_big(objects, frames, examples, df, implications="", premise=[], conclusion=[]):
    if len(premise) == 0 and len(conclusion) == 0:
        implications = implications.split('=>')
        premise = [line.strip() for line in implications[0].split(',')]
        conclusion = [line.strip() for line in implications[1].split(',')]
    else:
        premise = list(premise)
        conclusion = list(conclusion)

    prompt = ""
    prompt += "We are analyzing word meanings from different languages.\n"
    prompt += "\n"
    prompt += "Word Meaning List:\n\n"

    if examples[0] != " ":
        for i in range(len(frames)):
            prompt += f'{i+1}. "{frames[i]}" (e.g. {examples[i]})\n'

    else:
        for i in range(len(frames)):
            prompt += f'{i}. "{frames[i]}"\n'

    prompt += "\n"

    prompt += "Checked word list: \n"

    columns = list(df.columns)
    index = list(df.index)
    x, y = df.shape
    for i in range(x):
        prompt += index[i] + " has meaning(s): "
        meanings = [f'"{columns[j]}"' for j in range(y) if df.iloc[i, j] == 'X']
        if len(meanings) == 0:
            prompt += "\n"
        elif len(meanings) == 1:
            prompt += meanings[0] + "\n"
        elif len(meanings) == 2:
            prompt += " and ".join(meanings) + "\n"
        else:
            prompt += ", ".join(meanings[:-1]) + " and " + meanings[-1] + "\n"

    prompt += "\nHypothesis to Test:\n"

    premise_prompt = ' and '.join(f'"{word}"' for word in premise)
    conclusion_prompt = ' and '.join(f'"{word}"' for word in conclusion)
    prompt += f'Every word that conveys the meaning(s) {premise_prompt} also conveys the meaning(s) {conclusion_prompt}\n'
    # Every word in any language that conveys the meaning "{premise_prompt}" also conveys the meanings "{conclusion_prompt}"
    # Every word in any language other than English that conveys the meaning "{premise_prompt}" also conveys the meanings "{conclusion_prompt}"

    prompt += f"""
Instructions:
1. Search for words other then from the "checked word list" that include the meaning(s) {premise_prompt}.
2. For each word:
    - Check whether it also conveys the meaning(s) {conclusion_prompt}
"""
    prompt += "3. Return the result as a valid JSON object using the following logic : \n\n"
    prompt += f"If the hypothesis holds (i.e., all relevant words have meanings {conclusion_prompt})"
    prompt += """
{
"output": "YES"
}
"""
    conclusion_prompt_or = ' or '.join(f'"{word}"' for word in conclusion)
    prompt += f"\nOtherwise, return a word that has all of the following meaning(s): {premise_prompt}, but does not have at least one of the following meaning(s): {conclusion_prompt_or}"
    prompt += """
{
"output": "NO",
"word": "<Language of the word> : <name of the word>",
"meaning": ["""

    for premise in premise:
        prompt += f'"{premise}",'
    prompt += f'"<all other meanings from the Word Meaning List, if any apply>"],\n'
    prompt += '''"language": "<Give the language of the word>"
"explanation": "<Give a detailed explanation of your result, and also describe the general meaning of the word and also give from which language the word is taken>"
"example": "<Explain your results using some examples for all the meanings, in the same language of the word>"}"
'''
    prompt += """

Constraints:
- Ensure the returned word is not in the already checked list.
- Use all the meanings from the list that applies to this word.
- Do not include meanings not on the list.

Respond with only a valid JSON object. Do not include markdown syntax (like triple backticks) or any explanatory text."""

    return prompt

def set_prompt_small_object(objects, frames, examples, implications="", premise=[], conclusion=[]):

    if len(premise) == 0 and len(conclusion) == 0:
        implications = implications.split('=>')
        premise = [line.strip() for line in implications[0].split(',')]
        conclusion = [line.strip() for line in implications[1].split(',')]
    else:
        premise = list(premise)
        conclusion = list(conclusion)


    prompt = "Words List:\n"

    for i in range(len(objects)):
        prompt += f'{i+1}. "{objects[i]}"\n'

    premise_prompt = ' and '.join(f'"{word}"' for word in premise)
    conclusion_prompt = ' and '.join(f'"{word}"' for word in conclusion)

    prompt += "\nCheck the below hypothesis :\n"

    if len(premise) == 0:
        prompt += f'All meanings shared by all the words are also shared by the words {conclusion_prompt}\n\n'
    else:
        prompt += f'All meanings shared by the words {premise_prompt} are also shared by the words {conclusion_prompt}\n'

    # Every word in any language that conveys the meaning "{premise_prompt}" also conveys the meanings "{conclusion_prompt}"
    # Every word in any language other than English that conveys the meaning "{premise_prompt}" also conveys the meanings "{conclusion_prompt}"

    prompt += "Return the result as a valid JSON object using the following logic : \n\n"
    prompt += f"If the hypothesis holds"
    prompt += """
{
"output": "YES"
}
"""
    prompt += f"\nOtherwise, return only one counter-example refuting the hypothesis"
    prompt += """
{
"output": "NO",
"meaning": "",
"word": ["""

    for premise in premise:
        prompt += f'"{premise}",'
    prompt += f'"<all other words from the Words List, if any apply>"],\n'

    prompt += "Respond with only a valid JSON object.Do not include markdown syntax (like triple backticks) or any explanatory text."
    return prompt

def set_prompt_mid_object(objects, frames, examples, implications="", premise=[], conclusion=[]):
    if len(premise) == 0 and len(conclusion) == 0:
        implications = implications.split('=>')
        premise = [line.strip() for line in implications[0].split(',')]
        conclusion = [line.strip() for line in implications[1].split(',')]
    else:
        premise = list(premise)
        conclusion = list(conclusion)

    prompt = ""
    prompt += "We are analyzing word meanings from different languages.\n"
    prompt += "\n"
    prompt += "Words List:\n"

    for i in range(len(objects)):
        prompt += f'{i}. "{objects[i]}"\n'

    prompt += "\n"
    prompt += "Hypothesis to Test:\n"

    premise_prompt = ' and '.join(f'"{word}"' for word in premise)
    conclusion_prompt = ' and '.join(f'"{word}"' for word in conclusion)

    if len(premise) == 0:
        prompt += f'All meanings shared by all the words are also shared by the words {conclusion_prompt}\n\n'
    else:
        prompt += f'All meanings shared by the words {premise_prompt} are also shared by the words {conclusion_prompt}\n'

    prompt += f"""
Instructions:
1. Search for all meanings other then the "meanings list" that is shared by the words {premise_prompt}.
2. For each meaning check whether if these words also share the same meaning: {conclusion_prompt}
"""
    prompt += "3. Return the result as a valid JSON object using the following logic : \n\n"
    prompt += f"If the hypothesis holds (i.e., all relevant words have meanings {conclusion_prompt})"
    prompt += """
{
"output": "YES"
}
"""
    conclusion_prompt_or = ' or '.join(f'"{word}"' for word in conclusion)
    prompt += f"\nOtherwise, return a counter-example word that has all of the following meaning(s): {premise_prompt}, but does not have at least one of the following meaning(s): {conclusion_prompt_or}"
    prompt += """
{
"output": "NO",
"meaning": "",
"word": ["""

    for premise in premise:
        prompt += f'"{premise}",'
    prompt += f'"<all other words from the Words List, if any apply>"],\n'
    prompt += """

Respond with only a valid JSON object. Do not include markdown syntax (like triple backticks) or any explanatory text."""

    return prompt


# Sets prompt for object exploration
def set_prompt_big_object(objects, frames, examples, implications="", premise=[], conclusion=[]):
    if len(premise) == 0 and len(conclusion) == 0:
        implications = implications.split('=>')
        premise = [line.strip() for line in implications[0].split(',')]
        conclusion = [line.strip() for line in implications[1].split(',')]
    else:
        premise = list(premise)
        conclusion = list(conclusion)

    prompt = ""
    prompt += "We are analyzing word meanings from different languages.\n"
    prompt += "Meanings List:\n\n"

    for i in range(len(frames)):
        prompt += f'{i+1}. "{frames[i]}"\n'

    prompt += "\n"

    prompt += "Words list: \n"
    for i in range(len(objects)):
        prompt += f'{i+1}. "{objects[i]}"\n'


    prompt += "\n"
    prompt += "\nHypothesis to Test:\n"

    premise_prompt = ' and '.join(f'"{word}"' for word in premise)
    conclusion_prompt = ' and '.join(f'"{word}"' for word in conclusion)

    if len(premise) == 0:
        prompt += f'All meanings shared by all the words are also shared by the words {conclusion_prompt}\n\n'
    else:
        prompt += f'All meanings shared by the words {premise_prompt} are also shared by the words {conclusion_prompt}\n'
    # Every word in any language that conveys the meaning "{premise_prompt}" also conveys the meanings "{conclusion_prompt}"
    # Every word in any language other than English that conveys the meaning "{premise_prompt}" also conveys the meanings "{conclusion_prompt}"

    prompt += f"""
    Instructions:
    1. Search for all meanings other then the "meanings list" that is shared by the words {premise_prompt}.
    2. For each meaning:
        - Check whether if these words also share the same meaning: {conclusion_prompt}
    """
    prompt += "3. Return the result as a valid JSON object using the following logic : \n\n"
    prompt += f"If the hypothesis holds (i.e., all relevant meanings are shared by {conclusion_prompt})"
    prompt += """
    {
    "output": "YES"
    }
    """
    conclusion_prompt_or = ' or '.join(f'"{word}"' for word in conclusion)
    prompt += f"\nOtherwise, return a meaning that is shared by all of the following words(s): {premise_prompt}, but does not by least one of the following words(s): {conclusion_prompt_or}"
    prompt += """
    {
    "output": "NO",
    "meaning": "<New discovered meaning>",
    "word": ["""

    for premise in premise:
        prompt += f'"{premise}",'
    prompt += f'"<all other words from the Words List, if any apply>"],\n'
    prompt += '''"explanation": "<Give a detailed explanation of your result, and also describe the general meaning of the word and also give from which language the word is taken>"
    "example": "<Explain your results using some examples for all the words>"}"
    '''
    prompt += """

    Constraints:
    - Ensure the returned meaning is not in the already checked list.
    - Use all the words from the list that applies to this meaning.
    - Do not include words not on the "Words list".

    Respond with only a valid JSON object. Do not include markdown syntax (like triple backticks) or any explanatory text."""

    return prompt

def evaluate_prompt(prompt):
    try:
        my_api_key = ""

        client = OpenAI(base_url="https://llm.scads.ai/v1", api_key=my_api_key)
        model_name = "meta-llama/Llama-3.3-70B-Instruct"
        response = client.chat.completions.create(messages=prompt, model=model_name)
        response_content = response.choices[0].message.content
        return response_content
    except Exception as e:
        return "CLIENT_ERROR"

