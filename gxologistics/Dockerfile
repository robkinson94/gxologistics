# 1. Use an official Python runtime as a parent image
FROM python:3.10-slim

# 2. Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Set the working directory in the container
WORKDIR /app

# 4. Copy the requirements file into the container
COPY requirements.txt /app/

# 5. Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of your application code into the container
COPY . /app/

# 7. Expose the port your application runs on
EXPOSE 8000

# 8. Command to run when the container starts
CMD ["gunicorn", "gxologistics.wsgi:application", "--bind", "0.0.0.0:8000"]
