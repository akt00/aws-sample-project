# aws-sample-project

![Architecture](/docs/architecture_diagram.jpg)

## Application Summary
A simple web application on AWS that returns the inference result of objecte detection on the image uploaded by the user. Users must sing up or log in to use the application.

## How to set up the web server

### 1. Install Git
```rb
sudo yum install -y git
```

### 2. Clone the repository in /opt directory
```rb
git clone https://github.com/akt00/aws-sample-project.git
```

### 3. Run the bash script in the root directory
```rb
cd aws-sample-project
```
```rb
source init.sh
```

### 4. Export the environmental variable for AWS_REGION
```rb
export AWS_REGION="us-east-1"
```

### 5. Run the WSGI Flask application with Gunicorn
```rb
nohup gunicorn -w 2 -b 0.0.0.0:8080 'main:create_app()' &
```
