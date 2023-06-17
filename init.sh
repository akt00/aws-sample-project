sudo yum install -y nodejs

if [$? -ne 0]; then
    exit 1
fi

sudo yum install -y python3-pip

if [$? -ne 0]; then
    exit 1
fi

cd /opt/aws-sample-project

if [$? -ne 0]; then
    exit 1
fi

sudo python3 -m venv venv

if [$? -ne 0]; then
    exit 1
fi

cd venv/bin

if [$? -ne 0]; then
    exit 1
fi

source activate

if [$? -ne 0]; then
    exit 1
fi

cd /opt/aws-sample-project/frontend

if [$? -ne 0]; then
    exit 1
fi

npm install

if [$? -ne 0]; then
    exit 1
fi

npm run build

if [$? -ne 0]; then
    exit 1
fi

python3 -m pip install --upgrade pip

if [$? -ne 0]; then
    exit 1
fi

pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cpu

if [$? -ne 0]; then
    exit 1
fi

pip3 install bcrypt boto3 opencv-python Flask gunicorn ultralytics

if [$? -ne 0]; then
    exit 1
fi

cd /opt/aws-sample-project/
