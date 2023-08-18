# zosma-llama2-worker

Docker container for LLaMA 2 inference engine and a REST API wrapper.  
The docker image does not contain the model. The container can load the model from  a mounted volume.

REST API wrapper is based on the following inference sample code form the llama-recipes:    
https://github.com/facebookresearch/llama-recipes/blob/main/inference/inference.py

## Setup Ubuntu-22.04 host for Cuda RTX3090 drivers and docker container toolkit

https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html

## Obtaining the LLaMA 2 Model
https://ai.meta.com/llama/  
https://huggingface.co/meta-llama/Llama-2-7b-hf

## Convert Pytorch model to Huggingface frmat
Either you can download the model from Huggingface or convert using the instructions here:
https://github.com/facebookresearch/llama-recipes#model-conversion-to-hugging-face

## Configuration
Model and max output tokens can be configured in the configuration file config.ini
Example:  
```
[model]
name = /models_hf/7B
max_tokens = 256
```

## Build and Run

```
docker build -t <image_name> .

docker run -it --runtime=nvidia --gpus all -p 3000:3000 -v <models_hf_path>:/models_hf <image_name>
```
Example:
```
docker pull mcntech/zosma-llama2-worker:latest
docker run -it --runtime=nvidia --gpus all -p 3000:3000 -v $PWD/models_hf:/models_hf mcntech/zosma-llama2-worker:latest
```

## How to Prompt Llama 2 
https://huggingface.co/blog/llama2#how-to-prompt-llama-2

Singe question/query:
```
<s>[INST] <<SYS>>
{{ system_prompt }}
<</SYS>>

{{ user_message }} [/INST]
```

Continuous conversation:
```
<s>[INST] <<SYS>>
{{ system_prompt }}
<</SYS>>

{{ user_msg_1 }} [/INST] {{ model_answer_1 }} </s><s>[INST] {{ user_msg_2 }} [/INST]

```

Following default system prompt is used, if not supplied:
```
DEFAULT_SYSTEM_PROMPT = """\
You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe.  Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.

If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information."""
```
## Test the REST Chat API using Curl

```
curl -X POST http://localhost:3000/api/query \
   -H 'Content-Type: application/json' \
   -d '[[{"role": "user", "content": "I would like to know about Ayurveda."}]]'
```

```
curl -X POST http://localhost:3000/api/query \
   -H 'Content-Type: application/json' \
   -d '[[{"role": "system", "content": "You are a GDPR chatbot, only answer the question by using the provided context. If your are unable to answer the question using the provided context, say Please rephrase your question"}, {"role": "user", "content": "The careful, critical and unbiased study of the classical Ayurveda texts show that by the time compendiums (Samhita-granthas) were compiled, the Science and Art of Ayurveda had already passed through the stage of specialization and, knowledge flowing from different specialized fields of medicine and allied sciences generalized, simplified and principles enunciated. The Vedic medicine is developed in India during the period 2000-1000 B.C. and considered as one of the oldest systems of medicine in the world.[1] There are four major ancient Indian compendiums of knowledge (veda) named Rigveda, Yajurveda, Samaveda, and Atharvaveda. Rigveda is the oldest recorded document regarding use of plants as medicine in India, and this tradition continued in another ancient text, Atharvaveda (1500-1000 BC), which described more plants and introduced basic concepts\n\n --- \n\nWhat is  Ayurveda."}]]'
```