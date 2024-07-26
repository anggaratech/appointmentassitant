FROM python:3.9-bullseye

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN export OPENAI_API_KEY=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
ENV OPENAI_API_KEY=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
RUN echo "$OPENAI_API_KEY"

COPY . /app

COPY sshd_config /etc/ssh/sshd_config
RUN echo "root:Docker!" | chpasswd

RUN chmod +x /app/init.sh

EXPOSE 8000 8000
CMD [ "uvicorn","main:app","--host","0.0.0.0", "--port", "8000", "--workers","4"]