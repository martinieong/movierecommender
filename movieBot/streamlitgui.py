import requests
import argparse
import os
from typing import List
from pydantic import BaseModel
import json
import time
import banana_dev as banana
import streamlit as st

from streamlit.runtime.scriptrunner import get_script_run_ctx
from cache import RedisCache

## Demographic Information
gender = 'male'
age = 80

class post_data(BaseModel):
    prompt: str = "Hello world"
    bad_words: List[str] = []
    temperature: float = 0.7
    top_k: float = 50
    top_p: float = 0.95
    min_length: int = 10
    max_length: int = 25
    repetition_penalty: float = 1.0
    early_stop: bool = False
    end_sequence: str = ""
    do_sample: bool = True
    num_beams: int = 0
    return_prompt: str = ""
    seed: int = -1


class TravelBotGui:
    def __init__(self):
        self.st = st
        self.disable_menus = True

        self.base_url = os.getenv("API_URL", "http://localhost:5556")
        print("API URL is", self.base_url)
        self.base_prompt_files = ["./movie_rec.txt", "./movie_trivia.txt"]
        self.base_prompt_files = [os.path.realpath(file) for file in self.base_prompt_files]
        self.movie_rec_file = self.base_prompt_files[0]
        self.movie_trivia_file = self.base_prompt_files[1]
        self.entry_separator = "###"

        self.prompt_options_labels = ["Give movie recommendations", "Answer movie trivia"]
        self.bad_words = []
        self.use_redis = False
        if self.use_redis:
            self.redis = self.get_redis()
        self.window()

    @st.cache(allow_output_mutation=True)
    def get_redis(self):
        return RedisCache("travel_bot_redis")

    def window(self):
        if self.use_redis:
            self.write_session_to_redis()

        server_status = self.get_status()
        if server_status == "Server not running":
            disable_buttons = True
        else:
            disable_buttons = False
        disable_buttons = False
        self.st.title("Movie Bot")

        self.st.write("This bot can both recommend new movies as well as answer movie trivia")
        self.st.write("\n")
        base_col1, base_col2 = self.st.columns(2)
        with base_col1:
            self.prompt_options = self.st.radio("What would you like to do?", self.prompt_options_labels,
                                                on_change=self.get_base_prompt, index=0)
            self.text_input = self.st.text_input("Ask a question here", value="I liked Terminator, what other movies would I like?")
            self.st.slider("Tokens to generate", min_value=10, max_value=50, value=25, key="max_length")

        with self.st.expander("Advanced Options"):
            self.st.checkbox("Do sample", value=True, key="do_sample")
            self.st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, key="temperature")
            self.st.slider("Top K", min_value=0, max_value=100, value=50, key="top_k")
            self.st.slider("Top P", min_value=0.0, max_value=1.0, value=0.95, key="top_p")
            self.st.slider("Repetition Penalty", min_value=0.0, max_value=2.0, value=1.0, key="repetition_penalty")
            self.st.number_input("Seed", min_value=-1, value=-1, key="seed")
        col1, col2, col3 = self.st.columns(3)

        with col1:
            has_generated = self.st.button("Generate All New", on_click=self.generate_all_new, disabled=disable_buttons)
        with col2:
            if "print_result" in self.st.session_state:
                disabled = False
            else:
                disabled = True
            self.st.button("Generate More", on_click=self.generate_more, disabled=disabled)
        with col3:
            self.st.button("Reset", on_click=self.clear, disabled=disable_buttons)
        with base_col2:
            if "print_result" in self.st.session_state:
                self.text_area = self.st.text_area(label="generated values",
                                                   value=self.st.session_state["print_result"],
                                                   label_visibility="hidden", height=200, key="text_area")

        if disable_buttons:
            self.st.error("API server not running")

        if self.disable_menus:
            hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                """
            self.st.markdown(hide_streamlit_style, unsafe_allow_html=True)
        id = self.get_session_id()
        self.st.write("session id", id)

    def clear(self):
        seesions_state_keys = self.st.session_state.to_dict().keys()
        for key in seesions_state_keys:
            del self.st.session_state[key]
        if self.use_redis:
            id = self.get_session_id()
            self.redis.delete_python_dict(id)

    def get_session_id(self):
        return get_script_run_ctx().session_id

    def write_session_to_redis(self):
        session_id = self.get_session_id()
        current_session_state = self.st.session_state.to_dict()

        if self.redis.redis.exists(session_id):
            redis_session_state = self.redis.get_python_dict(session_id)
            new_state = {**redis_session_state, **current_session_state}
            self.redis.set_python_dict(session_id, new_state)
        else:
            self.redis.set_python_dict(session_id, current_session_state)

    def read_session_from_redis(self):
        session_id = self.get_session_id()
        if self.redis.redis.exists(session_id):
            redis_session_state = self.redis.get_python_dict(session_id)
            new_state = {**redis_session_state, **self.st.session_state.to_dict()}
            new_state_keys = new_state.keys()
            for key in new_state_keys:
                self.st.session_state[key] = new_state[key]

    def update_prompts(self):
        new_value = self.st.session_state["text_area"]
        print_result = self.st.session_state["print_result"]
        prompt = self.st.session_state["result"]
        start = prompt.find(print_result)
        if start == -1:
            raise ValueError("Could not find print result in prompt")
        new_prompt = prompt[:start]
        new_prompt = new_prompt + new_value
        self.st.session_state["result"] = new_prompt.strip()
        self.st.session_state["print_result"] = new_value.strip()

    def generate_all_new(self):
        self.get_base_prompt()
        extra_stuff = "\nAnswer:\n1."
        with self.st.spinner("Generating..."):
            final_input = f"You are talking to a {age} old {gender}\n" + self.base_prompt + self.text_input + extra_stuff
            result = self.execute(final_input)
        self.st.success("Done!")
        print_result = result[0][len(final_input) - 3:]
        # print_result = result
        self.st.session_state["print_result"] = print_result
        self.st.session_state["result"] = result

    def generate_more(self):
        self.update_prompts()
        prompt = self.st.session_state["result"]
        next_number = self.find_next_number(prompt)
        new_prompt = prompt + "\n" + str(next_number) + "."
        next_next_number = str(next_number + 1) + "."
        try:
            existing_entries = self.get_existing_entries(prompt)
        except:
            existing_entries = []
        with self.st.spinner("Generating..."):
            result = self.execute(new_prompt, bad_words=existing_entries, end_sequence=next_next_number)
        self.st.success("Done!")
        old_print_result = self.st.session_state["print_result"]
        print_result = result[len(new_prompt) - 3:]
        new_print_result = old_print_result + print_result

        self.st.session_state["print_result"] = new_print_result.strip()
        self.st.session_state["result"] = result.strip()

    def get_base_prompt(self):
        file_to_use = self.base_prompt_files[self.prompt_options_labels.index(self.prompt_options)]
        with open(file_to_use) as f:
            self.base_prompt = f.read()

    def get_status(self):
        try:
            response = requests.get(self.base_url + "/status")
        except Exception as e:
            print(e)
            return "Server not running"
        return response.json()

    def generate_text(self, post_data):
        response = requests.post(self.base_url + "/generate", data=post_data.json())

        return response.json()

    def find_next_number(self, prompt):
        self.get_base_prompt()
        base_prompt_len = len(self.base_prompt)
        prompt = prompt[base_prompt_len:]
        last_number = 1
        number_str = str(last_number) + "."
        while prompt.find(number_str) != -1:
            last_number += 1
            number_str = str(last_number) + "."
        return last_number

    def get_existing_entries(self, prompt):
        base_prompt_len = len(self.base_prompt)
        prompt = prompt[base_prompt_len:]
        first_number_loc = prompt.find("1.")
        prompt = prompt[first_number_loc:]
        entries = prompt.split("\n")

        # split entries after the number
        entries = [entry.split(".")[1].strip() for entry in entries]
        return entries

    def execute(self, utterance, end_sequence="###", bad_words=[]):
        self.get_base_prompt()
        print("executing", self.st.session_state)

        if "max_length" not in self.st.session_state:
            self.st.session_state["max_length"] = 25
        max_length = self.st.session_state["max_length"]
        if "temperature" not in self.st.session_state:
            self.st.session_state["temperature"] = 0.7
        temperature = self.st.session_state["temperature"]
        if "top_k" not in self.st.session_state:
            self.st.session_state["top_k"] = 50
        top_k = self.st.session_state["top_k"]
        if "top_p" not in self.st.session_state:
            self.st.session_state["top_p"] = 0.95
        top_p = self.st.session_state["top_p"]
        if "repetition_penalty" not in self.st.session_state:
            self.st.session_state["repetition_penalty"] = 1.0
        repetition_penalty = self.st.session_state["repetition_penalty"]
        if "seed" not in self.st.session_state:
            self.st.session_state["seed"] = -1
        seed = self.st.session_state["seed"]
        if "do_sample" not in self.st.session_state:
            self.st.session_state["do_sample"] = True
        do_sample = self.st.session_state["do_sample"]
        data = post_data(prompt=utterance, end_sequence=end_sequence, max_length=max_length, bad_words=bad_words,
                         temperature=temperature, top_p=top_p, repetition_penalty=repetition_penalty, seed=seed,
                         top_k=top_k, do_sample=do_sample)

        response = self.generate_text(data)
        prompt = response['gen_text']
        return prompt


if __name__ == '__main__':
    TravelBotGui()