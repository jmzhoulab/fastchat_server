# FastChat Server


# Deploy
## Install FastChat
```
pip3 install fschat
```

## Install the latest main branch of huggingface/transformers
```
pip3 install git+https://github.com/huggingface/transformers
```

## Start web ui
```
nohup python3 -m fastchat.serve.controller > controller.log 2>&1 &
nohup python3 -m fastchat.serve.model_worker --model-path /home/ubuntu/vicuna-13b > model_worker.log 2>&1 &
nohup python3 -m fastchat.serve.gradio_web_server > web_server.log 2>&1 &
```
web ui: http://host:7860




## Start API
```
nohup python3 fastchat_server/app.py > app.log 2>&1 &
```

## API
- method: POST
- url: http://host:8088/fastchat/query
- header
    ```
    {
        "User-Agent": "FastChat Client",
        'Content-Type': "application/json"
    }
    ```
- body
    ```
    {
        "query": "what's your name"
    }
    ```
- response
    ```
    {
        "code": "200",
        "info": "处理成功",
        "data": "I am an AI language model called Assistant. I am here to assist you with any questions or tasks you may have. I have been trained on a large dataset of text and can"
    }
    ```
