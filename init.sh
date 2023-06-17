sudo yum install -y nodejs
sudo yum install -y python3-pip

cd /opt/aws-sample-project

python3 -m venv venv

cd venv/bin

source activate

cd /opt/aws-sample-project/frontend

npm install

npm run build

python3 -m pip install --upgrade pip

pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip3 install bcrypt boto3 opencv-python Flask gunicorn ultralytics 

cd /opt/aws-sample-project/
