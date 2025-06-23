import pickle
from typing import List, Dict, Optional, Tuple
import pandas as pd
import tiktoken
import operator
import re
import openai
import os
import my_prompts
import time
import replicate
import numpy as np
import streamlit as st
os.environ["REPLICATE_API_TOKEN"]=st.secrets["REPLICATE_API_TOKEN"]

def euclidean(v1, v2):
   return sum((p - q) ** 2 for p, q in zip(v1, v2)) ** .5

def gen_agent_response(scenario, model, client, guidelines = None, temperature = 0.3): # generate the "textbook answer" for each scenario
    sys_prompt = my_prompts.AGENT_PROMPT_TICKET
    msg_list = [{"role": 'system', "content": sys_prompt}]
    msg_list.extend(extract_msg_list_from_conv(scenario))        

    if guidelines!=None:
        sys_prompt += my_prompts.AGENT_GUIDELINE_PROMPT1
        last_txt = msg_list[-1]['content']
        last_txt += "\n\n[Guidelines]:" + my_prompts.AGENT_GUIDELINE_PROMPT2.strip()
        last_txt += guidelines + "\n Now continue the conversation following the guidlines."
        msg_list[-1]['content'] = last_txt

    sys_prompt += my_prompts.AIRLINE_POLICY_TICKET
    msg_list[0]['content'] = sys_prompt
    msg_token_no = np.sum([num_tokens_from_string(item['content']) for item in msg_list])
    res_max_token = 3900 - msg_token_no
    res_max_token = int(res_max_token)
    retry = 0
    while retry < 3:
        try:
            if 'gpt' in model.lower():
                response = client.chat.completions.create(
                    model=model,
                    messages=msg_list,
                    temperature=temperature,
                    max_tokens=300,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0,
                )
                response2 = response.choices[0].message.content
            elif 'llama' in model.lower():
                prompt = convert_msg_to_prompt(msg_list)
                print(msg_list)
                print(prompt)
                if num_tokens_from_string(prompt)>3500:
                    print('\n\n The current conversation is:')
                    print(prompt)
                    print('truncating the prompt to 4000')
                    prompt = truncate_to_last_k_tokens(prompt)
                    print(f'now the length is {my_utils.num_tokens_from_string(prompt)}')
                output = replicate.run(
                    model,
                    input = {"prompt": prompt,
                                "temperature": 0.3,
                                "max_new_tokens": 300,
                                "stop_sequences": "</s>"}
                )
                response2 = ''.join(output)
                response2 = response2.split("[INST]")[0]
                response2 = response2.replace("AGENT:", "")
                response2 = response2.strip()
            else:
                response = client.chat.completions.create(
                    model=model,
                    messages=msg_list,
                )
                # print('done calling o4-mini')
                response2 = response.choices[0].message.content
            if len(response2) < 3:
                print("[db] agent gave empty response, retrying...")
                retry += 1
                continue
            return response2
        except Exception as e:
            print("\n\nException occured in generating agent response: ", e)
            print(f"the guidelines are {guidelines}")
            retry += 1
            print("retrying...", retry)
            time.sleep(1)
            continue
    print(f"no response from {model}")
    return "[no response]"

def extract_msg_list_from_conv(conversation: str) -> List[Dict[str, str]]:
    """
    Parse a single-string conversation (e.g. "Agent: Hi, Customer: Hello, AGENT: How are you?, user: I'm fine")
    and return a list of dicts:
      [
        {"role": "assistant", "content": "Hi"},
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "How are you?"},
        {"role": "user", "content": "I'm fine"}
      ]
    """
    # Find all “Agent:” or “User:” (case‐insensitive)
    pattern = re.compile(r"(Agent|Customer):", re.IGNORECASE)
    labels = list(pattern.finditer(conversation))
    total_len = len(conversation)
    messages: List[Dict[str, str]] = []

    for idx, match in enumerate(labels):
        speaker = match.group(1).lower()       # “agent” or “user”
        role = "assistant" if speaker == "agent" else "user"

        # content starts immediately after the colon
        start = match.end()
        # content ends at the next label’s start (or end of string)
        end = labels[idx + 1].start() if (idx + 1) < len(labels) else total_len

        # slice out the raw content, then strip leading commas/spaces
        raw = conversation[start:end].strip()
        content = raw.lstrip(", ").rstrip()
        if content:
            messages.append({"role": role, "content": content})

    return messages
# Define two different LLM response functions
def get_teacher_response(messages, model="gpt-4o-mini", temperature=0.3, max_tokens=500):
    try:
        response = openai.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def get_student_response(messages, model="meta/llama-2-7b-chat", temperature=0.3, max_tokens=500):
    if 'gpt' in model.lower():
        try:
            response = openai.chat.completions.create(
                # model="gpt-4",
                model=model,
                # model="meta-llama/Llama-2-7b-chat-hf",
                messages=messages,
                temperature=0.3,
                max_tokens=500,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"

    elif 'llama' in model.lower():
        try:
            prompt = convert_msg_to_prompt(messages)
            output = replicate.run(
                model,
                input = {"prompt": prompt,
                         "temperature": 0.3,
                         "max_new_tokens": 500,
                         "stop_sequences": "</s>"}
            )
            response1 = ''.join(output)
            response2 = response1.split("[INST]")[0]
            response2 = response2.replace("AGENT:", "")
            response2 = response2.strip()
            return response2
        except Exception as e:
            return f"Error: {str(e)}"

def convert_conv_to_list(conv):
    res = []
    str_list = conv.split("\n")
    curr_str = ""
    for s in str_list:
        if s.strip() == "":
            continue
        if s.startswith('CUSTOMER:') or s.startswith('AGENT:'):
            res.append(curr_str)
            curr_str = ""
        curr_str += s + " "
    res.append(curr_str)
    return res[1:]




def num_tokens_from_string(string, encoding_name = "cl100k_base") -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens
      


    
def find_k_closest_embedding(in_embed,embed_list):
    dist_dict = {}
    for i,e in enumerate(embed_list):
       dist_dict[i] = euclidean(in_embed,e)
    dist_dict_sort = sorted(dist_dict.items(), key=operator.itemgetter(1))
    closest_idx, distance = dist_dict_sort[0][0], dist_dict_sort[0][1]
    return closest_idx, distance

def find_k_closest_embedding_all(in_embed,embed_list):
    dist_dict = {}
    for i,e in enumerate(embed_list):
       dist_dict[i] = euclidean(in_embed,e)
    dist_dict_sort = sorted(dist_dict.items(), key=operator.itemgetter(1))
    closest_idx = dist_dict_sort[0][0]
    distances = [dist[1] for dist in dist_dict_sort]
    return closest_idx, distances

def convert_msg_to_prompt(msgs):
    return_prompt = ""
    for msg in msgs:
        if msg['role'] == 'system':
            return_prompt += "[INST]<<SYS>>{txt}<</SYS>>[/INST]\n\n".format(txt=msg['content'])
        elif msg['role'] == 'user':
            return_prompt += "[INST]{txt}[/INST]\n\n".format(txt=msg['content'])
        elif msg['role'] == 'assistant':
            return_prompt += msg['content'] + "\n\n"
    return return_prompt

async def get_embedding_async(text, client, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")
    response = await client.embeddings.create(input=[text], model=model)
    return response.data[0].embedding

#%%
import os
from openai import AsyncOpenAI
embedding_client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY_YALE"))
scenario = "hello"
def get_embedding_sync(text, client, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")
    response = client.embeddings.create(input=[text], model=model)
    return response.data[0].embedding
#%%



def find_ks_closest_embedding(in_embed, embed_list, k=5):
    dist_dict = {}
    for i, e in enumerate(embed_list):
        dist_dict[i] = euclidean(in_embed, e)
    dist_dict_sort = sorted(dist_dict.items(), key=operator.itemgetter(1))
    closest_ids = [e[0] for e in dist_dict_sort[:k]]
    return closest_ids

def rm_last_sent(string):
    sents = string.split(".")
    return ".".join(sents[:-1]) + "."

def process_conv(conv):
    res = ""
    conv_parts = conv.split("[CUSTOMER LEAVING THE CHAT]")
    res += conv_parts[0] + "[CUSTOMER LEAVING THE CHAT]\n\n"
    res += "AGENT: [AGENT LEAVING THE CHAT]\n"
    return res

def extract_first_number(text):
    # Using regular expression to find the first number in the string
    match = re.search(r'\d+', text)
    if match:
        return int(match.group())
    else:
        return None
