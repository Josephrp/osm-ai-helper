FROM nvidia/cuda:12.2.2-cudnn8-devel-ubuntu22.04

RUN apt-get update && apt-get install --no-install-recommends -y \
  libgl1 \
  libglib2.0-0 \
  build-essential \
  python3.10 \
  python3.10-dev \
  python3-pip \
  git \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 user

USER user

ENV HOME=/home/user \
	PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

RUN pip3 install --upgrade pip
RUN pip3 install git+https://github.com/mozilla-ai/osm-ai-helper.git
RUN pip3 install folium streamlit streamlit-folium

COPY --chown=user . $HOME/app

EXPOSE 8501
ENTRYPOINT ["streamlit", "run", "app.py", "--server.enableXsrfProtection", "false"]
