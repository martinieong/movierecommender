from transformers import AutoTokenizer,AutoModelForCausalLM
from pydantic import BaseModel
from fastapi import FastAPI
from typing import List
import numpy as np
import torch
from fastapi.responses import JSONResponse
from fastapi import HTTPException
import uvicorn
import argparse
from api_typings import post_data


app = FastAPI()

parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, default=5556)
parser.add_argument("--model", type=str, default="EleutherAI/gpt-j-6B")
parser.add_argument("--cpu", action="store_true")
args = parser.parse_args()



@app.on_event("startup")
def load_model():
    globals()
    global gpt_model
    global tokenizer
    global args
    if not args.cpu:
        try:
            if torch.cuda.is_bf16_supported():
                gpt_model = AutoModelForCausalLM.from_pretrained(args.model,torch_dtype=torch.bfloat16,low_cpu_mem_usage=True).cuda()
                gpt_model.bfloat16()
            else:
                gpt_model = AutoModelForCausalLM.from_pretrained(args.model,torch_dtype=torch.float16,low_cpu_mem_usage=True).cuda()
                gpt_model.float16()
        except:
            gpt_model = AutoModelForCausalLM.from_pretrained(args.model).cuda()
    else:
        gpt_model = AutoModelForCausalLM.from_pretrained(args.model)

        
    gpt_model.eval()
    tokenizer = AutoTokenizer.from_pretrained(args.model)

@app.post("/generate")
def generate(data:post_data):
    globals()
    global gpt_model
    global tokenizer
    global args

    post_data = data.dict()
  
    temp_input = float(post_data["temperature"])
    top_k_input = int(post_data["top_k"])
    top_p_input = float(post_data["top_p"])
    min_length_input = int(post_data["min_length"])
    max_length_input = int(post_data["max_length"])
    do_sample = post_data["do_sample"]
    prompt = post_data["prompt"]

    prompt = "<|endoftext|>" + prompt

    with torch.no_grad():
        input_ids = tokenizer(prompt, return_tensors="pt").input_ids
        if not args.cpu:
            input_ids = input_ids.cuda()
        tokens_size = np.shape(input_ids)[-1] - 1
        total_max_length = min(2048,max_length_input + tokens_size)
        gen_tokens = gpt_model.generate(input_ids, do_sample=do_sample, temperature=temp_input, top_k=top_k_input,top_p=top_p_input,min_length=min_length_input, max_length=total_max_length)
        gen_text = tokenizer.batch_decode(gen_tokens,skip_special_tokens=True)
    
    context = {"prompt":prompt,"gen_text":gen_text}
    return JSONResponse(status_code=200,content=context)       


if __name__ == '__main__':

    uvicorn.run(
    app="server:app",
    host="0.0.0.0",
    port=5556,
    log_level="info"
    )