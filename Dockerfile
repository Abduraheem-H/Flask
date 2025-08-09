FROM python:3.13-slim
EXPOSE 5000
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Set the environment variable to run Flask in development mode
ENV FLASK_ENV=development

CMD [ "flask", "run", "--host=0.0.0.0" ]