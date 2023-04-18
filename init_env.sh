#!/usr/bin

set -e

cd /home/ubuntu

# install and start jupyterlab
pip3 install jupyterlab
sudo ln -s /home/ubuntu/.local/bin/jupyter-lab /usr/local/miniconda3/bin/jupyter-lab
jupyter-lab --generate-config
jupyter-lab password
nohup jupyter-lab --no-browser --ip "0.0.0.0" --port 8089 --notebook-dir /home/ubuntu > /dev/null 2>&1 &


# Install FastChat
pip3 install fschat

# Install the latest main branch of huggingface/transformers
pip3 install git+https://github.com/huggingface/transformers


# swap file
# sudo dd if=/dev/zero of=/var/swap bs=30M count=1024
# sudo chmod 600 /var/swap
# sudo mkswap /var/swap
# sudo swapon /var/swap

# delete swap file
# swapoff /var/swap #卸载swap文件
# 并修改/etc/fstab文件 #从配置总删除
# rm -rf /var/swap #删除文件


# start web ui
nohup python3 -m fastchat.serve.controller > controller.log 2>&1 &
nohup python3 -m fastchat.serve.model_worker --model-path /home/ubuntu/vicuna-13b > model_worker.log 2>&1 &
nohup python3 -m fastchat.serve.gradio_web_server > web_server.log 2>&1 &


# start API
nohup python3 fastchat_server/app.py > app.log 2>&1 &

