# Copyright (c) Meta Platforms, Inc. and affiliates.
# This software may be used and distributed according to the terms of the Llama 2 Community License Agreement.

# from accelerate import init_empty_weights, load_checkpoint_and_dispatch

# Changes: modified to add REST API wrapper 

import torch
import os
import sys
import warnings
from typing import List
import configparser

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

from peft import PeftModel, PeftConfig
from transformers import LlamaConfig, LlamaTokenizer, LlamaForCausalLM
from safety_utils import get_safety_checker
from model_utils import load_model, load_peft_model
from chat_utils import read_dialogs_from_file, format_tokens


origins = [
    "*",
    "http://localhost:3000",
]


model = None
tokenizer = None
g_max_tokens = 512

def main(
    model_name,
    max_new_tokens = 512,
    peft_model: str=None,
    quantization: bool=True,
    seed: int=42, #seed value for reproducibility
    **kwargs
):
    global model
    global tokenizer
    global g_max_tokens
    # Set the seeds for reproducibility
    torch.cuda.manual_seed(seed)
    torch.manual_seed(seed)
    model = load_model(model_name, quantization)
    g_max_tokens = max_new_tokens
    if peft_model:
        model = load_peft_model(model, peft_model)
    tokenizer = LlamaTokenizer.from_pretrained(model_name)
    tokenizer.add_special_tokens(
        {
         
            "pad_token": "<PAD>",
        }
    )


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def run_query(
    model, 
    queries,
    max_new_tokens=512, #The maximum numbers of tokens to generate
    seed: int=42, #seed value for reproducibility
    do_sample: bool=True, #Whether or not to use sampling ; use greedy decoding otherwise.
    use_cache: bool=True,  #[optional] Whether or not the model should use the past last key/values attentions Whether or not the model should use the past last key/values attentions (if applicable to the model) to speed up decoding.
    top_p: float=1.0, # [optional] If set to float < 1, only the smallest set of most probable tokens with probabilities that add up to top_p or higher are kept for generation.
    temperature: float=1.0, # [optional] The value used to modulate the next token probabilities.
    top_k: int=50, # [optional] The number of highest probability vocabulary tokens to keep for top-k-filtering.
    repetition_penalty: float=1.0, #The parameter for repetition penalty. 1.0 means no penalty.
    length_penalty: int=1, #[optional] Exponential penalty to the length that is used with beam-based generation.
    **kwargs
):
    results =[]
    chats = format_tokens(queries, tokenizer)

    with torch.no_grad():
        for idx, chat in enumerate(chats):
            tokens= torch.tensor(chat).long()
            tokens= tokens.unsqueeze(0)
            tokens= tokens.to("cuda:0")
            outputs = model.generate(
                tokens,
                max_new_tokens=max_new_tokens,
                do_sample=do_sample,
                top_p=top_p,
                temperature=temperature,
                use_cache=use_cache,
                top_k=top_k,
                repetition_penalty=repetition_penalty,
                length_penalty=length_penalty,
                **kwargs
            )

            #output_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            output_text = tokenizer.batch_decode(outputs[:, tokens.shape[1]:])[0]
            results.append(output_text)
            print(f"Model output:\n{output_text}")

    return results

@app.get("/")
def read_root():
    return {"text": "SSBot Service"}


@app.post("/api/query")
async def QueryApi(query : Request):
    query = await query.json()
    print("Processing query={}".format(query))
    results = run_query(model, query, g_max_tokens)
    return results


if __name__ == "__main__":
    config = configparser.ConfigParser()
    try:
        config.read('config.ini')
        model_name = config['model']['name']
        max_new_tokens = int(config['model']['max_tokens'])
        print(f"model_name: {model_name}")
        print(f"max_tokens: {max_new_tokens}")
    except:
        print(f"Configuration error")
    main(model_name = model_name, max_new_tokens = max_new_tokens)
    uvicorn.run(app, host="0.0.0.0", port=os.environ.get('PORT', 3000))

