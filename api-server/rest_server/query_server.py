from api_typings import post_data
import requests
import argparse
import json

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5556)
    parser.add_argument("--url", type=str, default="http://localhost")
    parser.add_argument("-i", "--input", type=str, default="recommend me an action movie")
    parser.add_argument("-t", "--temperature", type=float, default=0.7)
    parser.add_argument("-k", "--top_k", type=int, default=50)
    parser.add_argument("-p", "--top_p", type=float, default=0.95)
    parser.add_argument("-min", "--min_length", type=int, default=10)
    parser.add_argument("-max", "--max_length", type=int, default=50)
    parser.add_argument("-g","--greedy", action="store_true")
    

    args = parser.parse_args()
    if args.greedy:
        do_sample = False
    else:
        do_sample = True
    data = post_data(prompt=args.input, temperature=args.temperature, top_k=args.top_k, top_p=args.top_p, min_length=args.min_length, max_length=args.max_length, do_sample=do_sample)
    response = requests.post(f"{args.url}:{args.port}/generate", data=data.json())
    gen_text = response.json()["gen_text"][0]
    print(gen_text)