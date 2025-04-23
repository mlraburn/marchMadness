FROM python:3.13-slim
LABEL authors="MLR"

# working directory of the container
WORKDIR /app

# copy requirments file into directory
COPY requirements.txt .

# install requirements for python environment
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY bracket.py .
COPY dataDownLoad.py .
COPY MattsMarchMadness.py .

# Copy neccessary data
COPY analysis.csv .
COPY config.csv .
COPY 03-16-2025-cbb-season-team-feed.xlsx .
COPY marchMadTable_2025.csv .
COPY other-data.csv .

# copy templates and static files for the web

COPY templates ./templates/
COPY static/ ./static/

# Make port 5000 available
EXPOSE 5000

# ENV variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run the Flask Application when container launches
CMD ["flask", "run"]

