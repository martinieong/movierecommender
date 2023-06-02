import banana_dev as banana
import click
import argparse

"""
this is to help iterate on prompts for prompt engineering by quickly making calls to the banana API instead of going through 
the trouble of setting up the REST server."""

api_key='asd' # Not the actual API key, masked for privacy
model_key="gptj"

## Demographic Information
gender = 'male'
age = 80

def get_base_prompt(self):
    with open(self) as f:
        return f.read()

def get_answer(utterance, base_prompt):
    final_prompt = f"You are talking to a {age} old {gender}\n" + base_prompt + utterance + "\nAnswer:\n"
    model_inputs = {"text": f"{final_prompt}", "length": 50, "temperature": 0.8, "topK": 75, "topP": 0.95}
    out = banana.run(api_key, model_key, model_inputs)
    result = out['modelOutputs'][0]['output']
    return result

def execution_loop():
    func = click.prompt('Would you like movie trivia or recommendations?', type=str)
    if func == 'trivia':
        base_prompt = get_base_prompt('movie_gen.txt')
    elif func == 'recommendations':
        base_prompt = get_base_prompt('movie_rec.txt')

    while True:
        question = click.prompt('What do you want to ask?', type = str)
        result = get_answer(question, base_prompt)
        print(result)
        if not click.confirm('Do you want to ask another question?'):
            break

if __name__ == '__main__':



    execution_loop()


"""TODO
1. add functionality to ask whether or not you want movie trivia or movie recommendation
2. add an argparse such that the bot behaves differently depending on user intent

Afterwards,
make a Streamlit GUI to make this more interactive"""