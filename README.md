## Overview

This repo contains two things:

1.  Code to generate a REST server which hosts a large language model and allows the user to query the API for text generation.

2.  Code to create a streamlit web app for movie recommendations in natural language, i.e. "Recommend me an action movie similar to John Wick". 

The web app has two versions: streamlitgui.py, which uses the included API (if the user has access to enough compute resources to host an LLM) or banana-gui.py that uses a third-party website called banana.dev which itself hosts an API of an LLM called GPT-J for users with less compute resources.

There is also a testing script which operates as a simple CLI tool that I used to play around with different prompts for few-shot learning.

