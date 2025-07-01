FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Explicitly copy the Data folder to the right path
COPY services/Data ./Data

# Copy the rest of your code
COPY . .

ENTRYPOINT [ "nitric", "start" ]
