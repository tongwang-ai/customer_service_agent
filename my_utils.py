import pickle
import pandas as pd
import tiktoken
import operator
import sentencepiece
import re
import my_prompts

def euclidean(v1, v2):
   return sum((p - q) ** 2 for p, q in zip(v1, v2)) ** .5

def cosine(v1,v2):
   return spatial.distance.cosine(v1, v2)

def split_batch(inp_list,no_of_batch):
    batch_size = len(inp_list)//no_of_batch
    return [inp_list[i*batch_size:(i+1)*batch_size] for i in range(no_of_batch)]


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

def process_guideline(guideline):
    sents = guideline.split("\n")
    res = ""
    add = False
    for sent in sents:
        if add:
            res += sent + "\n"
        if sent.startswith("DO") and not sent.startswith("DON'T"):
            res += sent + "\n"
            add = True
    return res

def process_guideline1(guideline):
    new_guideline = (guideline.replace("Agent 1","the agent").replace("agent 1","the agent")
                     .replace("AGENT 1","the agent"))
    new_guideline = (new_guideline.replace("Agent 2", "a good agent").replace("agent 2","the agent")
                     .replace("AGENT 2", "a good agent"))
    return new_guideline

def process_guideline2(guideline):
    para_list = guideline.split("\n")
    res = ""
    for para in para_list[:-1]:
        res += para + "\n"
    return res

def num_tokens_from_string(string, encoding_name = "cl100k_base") -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens
      

def combine_k_guidelines(guidelines):
    sys_txt = """You are provided with many DO lists and DON'T lists that a customer support agent from an airline company should follow. The 'DO List' outlines what you must follow, and the 'DONT List' details what you should avoid. Your task is to combine all the DO lists into one general DO list and all the DONT Lists into one general DONT List. The new lists should be more general. Try to summarize both the main information and the examples, and eliminate repetitive items. Call the new lists 'DO List' and 'DONT List' in the output."""
    msg_list = [{"role": 'system', "content": sys_txt}]
    total_token_no = num_tokens_from_string(sys_txt)
     
    user_msg = "\n\n".join(guidelines) 
    #print("db user_msg: ",user_msg )
    new_msg = {"role": 'user', "content": user_msg}
    msg_list.append(new_msg)
    total_token_no += num_tokens_from_string(user_msg)
    res_max_token = 4050 - total_token_no
    # print("max token allowed = ", res_max_token)
    try:
        response = client.chat.completions.create(
            # model="ft:gpt-3.5-turbo-0613:yale-university::87p0vJIx",
            model="gpt-3.5-turbo-0125",
            # model="gpt-4",
            messages=msg_list,
            temperature=0.3,
            max_tokens=res_max_token,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0)
        new_response = response.choices[0].message.content
        #print("db new_response = ",new_response)
        # new_response = process_guideline2(raw_response)
    except Exception as e:
        print("Exception occured: ", e)
        new_response = guideline
    return new_response
    
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


async def combine_k_guidelines(guidelines, client):
    sys_txt = my_prompts.MERGE_GUIDELINES
    msg_list = [{"role": 'system', "content": sys_txt}]
    total_token_no = num_tokens_from_string(sys_txt)

    user_msg = "\n\n".join(guidelines)
    # print("db user_msg: ",user_msg )
    new_msg = {"role": 'user', "content": user_msg}
    msg_list.append(new_msg)
    total_token_no += num_tokens_from_string(user_msg)
    res_max_token = 4050 - total_token_no
    # print("max token allowed = ", res_max_token)
    try:
        response = await client.chat.completions.create(
            # model="ft:gpt-3.5-turbo-0613:yale-university::87p0vJIx",
            model="gpt-3.5-turbo-0125",
            # model="gpt-4",
            messages=msg_list,
            temperature=0.3,
            max_tokens=res_max_token,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0)
        new_response = response.choices[0].message.content
        # print("db new_response = ",new_response)
        # new_response = process_guideline2(raw_response)
    except Exception as e:
        print("Exception occured: ", e)
        new_response = "Guidelines for agent: "
    return new_response


# def find_k_closest_embedding(in_embed,embed_list):
#     dist_dict = {}
#     for i,e in enumerate(embed_list):
#        dist_dict[i] = euclidean(in_embed,e)
#     dist_dict_sort = sorted(dist_dict.items(), key=operator.itemgetter(1))
#     closest_idx = dist_dict_sort[0][0]
#     return closest_idx

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
