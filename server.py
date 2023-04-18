from collections import defaultdict
import datetime
import json
import os
import time
import uuid

import gradio as gr
import requests

from fastchat.conversation import (default_conversation, conv_templates,
                                   SeparatorStyle)
from fastchat.constants import LOGDIR
from fastchat.utils import (build_logger, server_error_msg,
    violates_moderation, moderation_msg)
from fastchat.serve.gradio_patch import Chatbot as grChatbot
from fastchat.serve.gradio_css import code_highlight_css

from flask import Blueprint, url_for, request


logger = build_logger("gradio_web_server", "gradio_web_server.log")

headers = {"User-Agent": "fastchat Client"}

no_change_btn = gr.Button.update()
enable_btn = gr.Button.update(interactive=True)
disable_btn = gr.Button.update(interactive=False)

priority = {
    "vicuna-13b": "aaaaaaa",
    "koala-13b": "aaaaaab",
}


def get_conv_log_filename():
    t = datetime.datetime.now()
    name = os.path.join(LOGDIR, f"{t.year}-{t.month:02d}-{t.day:02d}-conv.json")
    return name


def post_process_code(code):
    sep = "\n```"
    if sep in code:
        blocks = code.split(sep)
        if len(blocks) % 2 == 1:
            for i in range(1, len(blocks), 2):
                blocks[i] = blocks[i].replace("\\_", "_")
        code = sep.join(blocks)
    return code


def http_bot(state, controller_url, model_selector, temperature, max_new_tokens, client_host):
    logger.info(f"http_bot. ip: {client_host}")
    start_tstamp = time.time()
    model_name = model_selector

    # Query worker address
    ret = requests.post(controller_url + "/get_worker_address",
            json={"model": model_name})
    worker_addr = ret.json()["address"]
    logger.info(f"model_name: {model_name}, worker_addr: {worker_addr}")

    # Construct prompt
    prompt = state.get_prompt()

    # Make requests
    pload = {
        "model": model_name,
        "prompt": prompt,
        "temperature": temperature,
        "max_new_tokens": min(max_new_tokens, 1536),
        "stop": state.sep if state.sep_style == SeparatorStyle.SINGLE else state.sep2,
    }
    
    state.messages[-1][-1] = "▌"

    try:
        # Stream output
        response = requests.post(worker_addr + "/worker_generate_stream",
            headers=headers, json=pload, stream=True, timeout=10)
        for chunk in response.iter_lines(decode_unicode=False, delimiter=b"\0"):
            if chunk:
                data = json.loads(chunk.decode())
                if data["error_code"] == 0:
                    output = data["text"][len(prompt) + 1:].strip()
                    output = post_process_code(output)
                    state.messages[-1][-1] = output + "▌"
                else:
                    output = data["text"] + f" (error_code: {data['error_code']})"
                    state.messages[-1][-1] = output
                    return
                time.sleep(0.02)
    except requests.exceptions.RequestException as e:
        state.messages[-1][-1] = server_error_msg + f" (error_code: 4)"
        return

    state.messages[-1][-1] = state.messages[-1][-1][:-1]

    finish_tstamp = time.time()
    logger.info(f"{output}")

    with open(get_conv_log_filename(), "a") as fout:
        data = {
            "tstamp": round(finish_tstamp, 4),
            "type": "chat",
            "model": model_name,
            "start": round(start_tstamp, 4),
            "finish": round(finish_tstamp, 4),
            "state": state.dict(),
            "ip": client_host,
        }
        fout.write(json.dumps(data) + "\n")

        

if __name__ == "__main__":
    import yaml
    settings = yaml.load(open(f"{os.path.dirname(os.path.abspath(__file__))+'/conf/settings.yaml'}"), Loader=yaml.loader.SafeLoader)
    
    print(settings)
    state = conv_templates['v1'].copy()
    state.conv_id = uuid.uuid4().hex
    state.append_message(state.roles[0], "中国汽车品牌有哪些？")
    state.append_message(state.roles[1], None)
    
    print(state.messages)
    print(state.roles[0])
    print(state.messages[-2][1])
    print(len(state.messages))
    print("state.offset: ", state.offset)
    
    http_bot(state=state,
             controller_url=settings['controller_url'],
             model_selector=settings['model_name'],
             temperature=settings['temperature'],
             max_new_tokens=settings['max_new_tokens'],
             client_host='None')
    print('-'*60)
    print(state.messages[-1])
    
    state.append_message(state.roles[0], "哪个发展比较好？")
    state.append_message(state.roles[1], None)
    
    http_bot(state=state,
             controller_url=settings['controller_url'],
             model_selector=settings['model_name'],
             temperature=settings['temperature'],
             max_new_tokens=settings['max_new_tokens'],
             client_host='None')
    print('='*60)
    print(state.messages[-1])