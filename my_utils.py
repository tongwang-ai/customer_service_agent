import pickle
import pandas as pd
import tiktoken
import operator
import sentencepiece
import re
import openai
import my_prompts
import replicate

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

def get_embedding_sync(text, client, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")
    response = client.embeddings.create(input=[text], model=model)
    return response.data[0].embedding

def llama2_count_tokens(prompt):
    sp = sentencepiece.SentencePieceProcessor(model_file='tokenizer.model')
    prompt_tokens = sp.encode_as_ids(prompt)
    return len(prompt_tokens)



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
