# zosma-llama2-worker

**Repository Description: zosma-llama2-worker**

This repository houses the Docker container setup for deploying the LLaMA 2 inference engine complemented by a REST API wrapper, facilitating advanced natural language processing tasks. The Docker setup is specifically designed to not include the model itself but rather load it dynamically from a mounted volume, offering flexibility and ease of updates or model swaps.

The REST API, foundational to this setup, is adapted from sample inference code provided in the LLaMA-recipes on GitHub, ensuring that it remains aligned with the latest recommended practices for LLaMA model utilization. The API allows users to interact with the LLaMA model seamlessly, submitting queries and receiving responses formatted according to user specifications.

Key features of this repository include:
- **Model Flexibility**: Users have the ability to configure the model name and the maximum number of output tokens via a `config.ini` file, allowing for customized setup based on specific requirements.
- **Advanced Configuration**: This setup is intended for use on systems equipped with Nvidia RTX 3090 GPUs, supporting intensive computational tasks required by large models like LLaMA 2.
- **Dynamic Model Loading**: The architecture supports dynamic loading of the LLaMA model from a mounted volume, making it easy to update or change the model without rebuilding the Docker image.
- **API-Driven Interaction**: The REST API built around the OpenAPI 3.0 specification offers a robust interface for developers to integrate LLaMA-based NLP capabilities into their applications or services.

This Docker container is ideal for developers looking to deploy a scalable, efficient NLP service with the power of LLaMA 2, providing a foundation for building complex, AI-driven applications.
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
## API

[API Schema based on OpenAPI 3.0](./zosma_llama_api.yaml)
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