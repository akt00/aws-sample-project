import base64
import bcrypt
import boto3
import cv2 as cv
import flask
import io
import numpy as np
import os
from PIL import Image
from ultralytics import YOLO
import uuid


def create_app():
    app = flask.Flask(__name__)
    aws_region = os.getenv('AWS_REGION') if os.getenv('AWS_REGION') else 'us-east-1'
    build_path = '../frontend/dist'
    app.static_folder = build_path
    model = YOLO('yolov8n.pt')
    
    def xywh_to_p1p2(xywh: tuple) -> tuple:
        """
        :param xywh: un-normalized coords and length of xywh
        :return: tuple containing points(x, y) for top-left and bottom-right.
        """
        x, y, w, h = xywh
        p1 = (int(x-w/2), int(y-h/2))
        p2 = (int(x+w/2), int(y+h/2))
        return p1, p2
    
    def draw_bbox(img: np.ndarray, labels: np.ndarray) -> np.ndarray:
        """
        draws bouding boxes based on the inference result of the YOLO model
        :param img: input image in numpy
        :param labels: numpy array containing the inference result
        """
        for label in labels:
            xywh = (int(i) for i in label)
            p1, p2 = xywh_to_p1p2(xywh)
            img = cv.rectangle(img, pt1=p1, pt2=p2, color=(0, 0, 255), thickness=2)
        
        return img
    
    @app.route('/')
    def index():
        dynamo = boto3.resource('dynamodb', region_name=aws_region)
        session_table = dynamo.Table('Session')

        user_name = flask.request.cookies.get('username')
        session_id = flask.request.cookies.get('session')
        
        res = session_table.get_item(
            Item={'username': user_name}
            )
        
        if 'Item' in res and str(session_id) == str(res['Item'].get('session_id')):
            return flask.redirect('https://aws-project-akt00.com/content', code=302)


        return flask.send_from_directory(app.static_folder, 'index.html')
    
    @app.route('/<path:path>')
    def serve_frontend(path):
        user_name = flask.request.cookies.get('username')
        session_id = flask.request.cookies.get('session')
        print(user_name, session_id)
        if path != "" and os.path.exists(app.static_folder + '/' + path):
            return flask.send_from_directory(app.static_folder, path)
        else:
            return flask.send_from_directory(app.static_folder, 'index.html')
    
    @app.route('/login', methods=['POST'])
    def user_login():
        user_data = flask.request.get_json()
        # print(user_data)
        user_name = user_data['username']
        user_passwd = user_data['password']

        res = flask.make_response(flask.jsonify({'message': 'OK'}), 404)
        res.set_cookie('username', user_data['username'])
        res.set_cookie('session', str(uuid.uuid4()))
        return res
    
    @app.route('/signup', methods=['POST'])
    def user_signup():
        dynamo = boto3.resource('dynamodb', region_name='us-east-1')

        user_data = flask.request.get_json()
        # print(user_data)
        user_name = user_data['username']
        user_passwd = user_data['password']

        res = flask.make_response(flask.jsonify({'message': 'OK'}), 200)
        res.set_cookie('username', user_data['username'])
        res.set_cookie('session', str(uuid.uuid4()))
        return res
    
    @app.route('/inference', methods=['POST'])
    def inference():
        # s3 = boto3.client('s3')
        # s3_bucket = 'aws-sample-project'
        
        # dynamo = boto3.resource('dynamodb', region_name='us-east-1')
        

        data = flask.request.get_json()
        user_name = flask.request.cookies.get('username')
        session_id = flask.request.cookies.get('session')
        image_data = data['image']
        # remove prefix:image/jpeg;base64, data
        image_data = image_data.split(',')[1]
        image_byte = base64.b64decode(image_data)
        image_rgba = Image.open(io.BytesIO(image_byte))
        image = image_rgba.convert('RGB')

        image_np = np.array(image)
        image_np = cv.cvtColor(image_np, cv.COLOR_RGB2BGR)

        image_io = io.BytesIO()
        image = Image.fromarray(image_np)
        image.save(image_io, format='png')
        image_io.seek(0)
        image_png = image_io.getvalue()

        # s3.put_object(Body=image_png, Bucket=s3_bucket, Key=str(user_name) + str(uuid.uuid4()) + '.png')
        # inference
        res = model.predict(image_np)
        labels = res[0].boxes.xywh.to('cpu').numpy()
        # print(labels.shape)
        assert labels.ndim == 2

        image_np = draw_bbox(image_np, labels)
        image_np = cv.cvtColor(image_np, cv.COLOR_BGR2RGB)

        image_io = io.BytesIO()
        image = Image.fromarray(image_np)
        image.save(image_io, format='PNG')
        image_io.seek(0)
        image_png = image_io.getvalue()

        image_str = base64.b64encode(image_png).decode('utf-8')

        return flask.jsonify({'image': image_str}), 200
    
    return app


app = create_app()


if __name__ == '__main__':
    app.run()
    