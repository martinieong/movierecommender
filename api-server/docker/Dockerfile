FROM nvidia/cuda:11.6.2-cudnn8-devel-ubuntu20.04

SHELL [ "/bin/bash","-c" ]

#GPU setup
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,video,utility

RUN apt-get update && apt-get install -y \
python3 \
python3-pip \
python-is-python3 

RUN pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu116

RUN pip install transformers fastapi pydantic uvicorn nvidia-pyindex accelerate

RUN mkdir /workspace

WORKDIR /workspace