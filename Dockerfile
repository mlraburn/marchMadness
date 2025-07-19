FROM python:3.13-slim
LABEL authors="MLR"

# working directory of the container
WORKDIR /app

# copy requirments file into directory
COPY marchMadnessReact/requirements.txt .

# install requirements for python environment
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY marchMadnessReact/backend/app.py .
COPY marchMadnessReact/backend/bracket.py .
COPY marchMadnessReact/backend/dataDownLoad.py .
COPY marchMadnessReact/backend/MattsMarchMadness.py .

# Copy neccessary data
COPY marchMadnessReact/backend/analysis.csv .
COPY config.csv .
COPY 03-16-2025-cbb-season-team-feed.xlsx .
COPY marchMadnessReact/backend/marchMadTable_2025.csv .
COPY other-data.csv .

# copy templates and static files for the web

COPY templates ./templates/
COPY static/ ./static/

# create static directory for simulation brackets
RUN mkdir -p /app/static

# allow app to be able to write generated files
RUN chmod -R 777 /app

# make port environmental variable
ENV PORT=8080

# Expose Port
EXPOSE $PORT

# run the flask app when container launches
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app

