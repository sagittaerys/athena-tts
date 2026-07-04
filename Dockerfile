FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    espeak-ng \
    git \
    && rm -rf /var/lib/apt/lists/*


RUN pip install --no-cache-dir torch torchaudio --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN git clone --depth 1 https://github.com/Ashish-Patnaik/kokoclone.git kokoclone_src

RUN mkdir -p voice_profiles audio_output

EXPOSE 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]