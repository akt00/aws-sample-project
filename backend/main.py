import base64
import bcrypt
import boto3
import cv2 as cv
from datetime import datetime
import flask
import io
import numpy as np
import os
from PIL import Image
import re
from ultralytics import YOLO
import uuid


# factory module
def create_app():
    app = flask.Flask(__name__)
    aws_region = os.getenv('AWS_REGION') if os.getenv('AWS_REGION') else 'us-east-1'
    build_path = '../frontend/dist'
    app.static_folder = build_path
    model = YOLO('yolov8n.pt')
    
    
    def validate_input(user_input: str) -> bool:
        """
        validate user inputs with Regex
        :param user_input: user input string
        :return: True if user_input only contians alphanumeric or hyphen, False otherwise
        """
        pattern = '[^a-zA-Z0-9-]+'
        match = re.search(pattern=pattern, string=user_input)

        return True if match is None else False


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
        """
        The default http route. Redicrects users to content page if a valid session token is present
        """
        dynamo = boto3.client('dynamodb', region_name=aws_region)
        username = str(flask.request.cookies.get('username'))
        session_id = str(flask.request.cookies.get('session'))

        if validate_input(username) and validate_input(session_id):
            query_res = dynamo.get_item(
                TableName='Session',
                Key={
                    'username': {
                        'S': username,
                        },
                    'session_id': {
                        'S': session_id
                        },
                }
                )
            
            if 'Item' in query_res:
                query_res = query_res['Item']

                if query_res.get('session_id') is not None or query_res.get('username') is not None:
                    return flask.redirect('https://aws-project-akt00.com/content', code=302)
            
        return flask.send_from_directory(app.static_folder, 'index.html')
    

    @app.route('/<path:path>')
    def serve_static(path):
        """
        Servers the static content. Stays in the same page on reload
        """
        if path != "" and os.path.exists(app.static_folder + '/' + path):
            return flask.send_from_directory(app.static_folder, path)
        else:
            return flask.send_from_directory(app.static_folder, 'index.html')
    

    @app.route('/login', methods=['POST'])
    def user_login():
        """
        /login endpoint for user login
        1. Valdates user input
        2. Validate user identiy
        3. Issue sessoin token, then redirects to the content page
        """
        dynamo = boto3.client('dynamodb', region_name=aws_region)

        user_data: dict = flask.request.get_json()
        # print(user_data)
        username = str(user_data['username'])
        password = str(user_data['password'])

        if validate_input(username) is False or validate_input(password) is False:
            return flask.make_response(flask.jsonify({'message': 'invalid user request'}), 400)

        query_res = dynamo.get_item(
            TableName='Users',
            Key={
                'username': {
                    'S': username
                },
            }
        )

        if 'Item' in query_res:
            query_res = query_res['Item']
            hashed_pwd: bytearray = query_res.get('password')['S'].encode()
            # print('hashed_pwd', hashed_pwd)
            if bcrypt.checkpw(password.encode(), hashed_pwd):
                session_id = str(uuid.uuid4())

                _ = dynamo.put_item(
                    TableName='Session',
                    Item={
                        'session_id': {
                            'S': session_id
                        },
                        'username': {
                            'S': username
,                        }
                    },
                )
                
                res = flask.make_response(flask.jsonify({'message': 'OK'}), 200)
                res.set_cookie('username', username)
                res.set_cookie('session', session_id)
                return res
            else:
                return flask.make_response(flask.jsonify({'message': 'Login failed'}), 401)
        else:
            res = flask.make_response(flask.jsonify({'message': 'An error occured'}), 500)
            return res
        
    

    @app.route('/signup', methods=['POST'])
    def user_signup():
        """
        HTTP /singpu endpoint for user sign-up
        1. Validates the user inputs
        2. Validates the user identity against dynamodb
        3. Creates the new user identity, then issue the ssession token
        """
        dynamo = boto3.client('dynamodb', region_name=aws_region)

        user_data = flask.request.get_json()
        # print(user_data)
        username = str(user_data['username'])
        password = str(user_data['password'])

        if validate_input(username) is False or validate_input(password) is False:
            return flask.make_response(flask.jsonify({'message': 'invalid user request'}), 400)

        query_res = dynamo.get_item(
            TableName='Users',
            Key={
                'username': {
                    'S': username
                },
            }
        )

        if 'Item'in query_res:
            username = query_res['Item'].get('username')
            # print(username)
            if username is not None:
                return flask.make_response(flask.jsonify({'message': 'Sign-up failed'}), 401)

        salt = bcrypt.gensalt()
        hashed_password: str = bcrypt.hashpw(password.encode(), salt).decode()

        _ = dynamo.put_item(
            TableName='Users',
            Item={
                'username': {
                    'S': username
                },
                'password': {
                    'S': hashed_password
                },
            }
        )

        sessino_id = str(uuid.uuid4())

        _ = dynamo.put_item(
            TableName='Session',
            Item={
                'username': {
                    'S': username
                },
                'session_id': {
                    'S': sessino_id
                },
            }
        )

        res = flask.make_response(flask.jsonify({'message': 'OK'}), 200)
        res.set_cookie('username', user_data['username'])
        res.set_cookie('session', sessino_id)
        
        return res
    

    @app.route('/logout', methods=['POST'])
    def user_logout():
        """
        HTTP /logout endponit that handles user logout.
        Removes the userssion registered in the dynamodb
        """
        dynamo = boto3.client('dynamodb', region_name=aws_region)

        username = str(flask.request.cookies.get('username'))
        session_id = str(flask.request.cookies.get('session'))
        # print(username, session_id)

        if validate_input(username) is False or validate_input(session_id) is False:
            return flask.make_response(flask.jsonify({'message': 'invalid user request'}), 400)
        
        if username is not None and session_id is not None:
            res = dynamo.delete_item(
                TableName='Session',
                Key={
                    'session_id': {
                        'S': session_id
                    },
                    'username': {
                        'S': username
                    },
                }
            )
        
        return flask.make_response(flask.jsonify({'message': 'OK'}), 200)


    @app.route('/inference', methods=['POST'])
    def inference():
        """
        HTTP /inference endpoint that does object detection on user uploaded images
        1. Validates the user identity
        2. Receives the image
        3. Process the image and store it in S3
        4. Runs the ML model on the image
        5. Stores the result to the dynamodb
        6. Returns the result image with bounding boxes to the user
        """
        s3 = boto3.client('s3')
        s3_bucket = 'aws-sample-project'
        
        dynamo = boto3.client('dynamodb', region_name=aws_region)

        data = flask.request.get_json()
        username: str = flask.request.cookies.get('username')
        session_id: str = flask.request.cookies.get('session')
        assert type(username) is str
        assert type(session_id) is str

        if validate_input(username) is False or validate_input(session_id) is False:
            return flask.make_response(flask.jsonify({'message': 'invalid user request'}), 400)
        
        if username is None and session_id is None:
            return flask.make_response(flask.jsonify({'message': 'session expired'}), 401)

        query_res = dynamo.get_item(
            TableName='Session',
            Key={
                'session_id': {
                    'S': session_id
                },
                'username': {
                    'S': username
                }
            }
        )

        # print(query_res)
        if 'Item' in query_res:
            _session_id: str = query_res['Item'].get('session_id')['S']
            _username: str = query_res['Item'].get('username')['S']
            if username != _username or session_id != _session_id:
                return flask.make_response(flask.jsonify({'message': 'invalid session credentials'}), 401)
        else:
            return flask.make_response(flask.jsonify({'message': 'failed to validate session'}), 500)
        
        image_data = data['image']
        # remove prefix:image/jpeg;base64, data
        image_data = image_data.split(',')[1]
        image_byte = base64.b64decode(image_data)
        image_rgba = Image.open(io.BytesIO(image_byte))
        image = image_rgba.convert('RGB')

        image_np = np.array(image)

        image_io = io.BytesIO()
        image = Image.fromarray(image_np)
        image.save(image_io, format='png')
        image_io.seek(0)
        image_png = image_io.getvalue()

        object_path = username + str(uuid.uuid4()) + '.png'
        _ = s3.put_object(Body=image_png, Bucket=s3_bucket, Key=object_path)
        
        image_np = cv.cvtColor(image_np, cv.COLOR_RGB2BGR)
        # inference
        res = model.predict(image_np)
        labels = res[0].boxes.xywh.to('cpu').numpy()
        # print(labels.shape)
        assert labels.ndim == 2

        
        now = datetime.now()
        timestamp = str(now.strftime('%Y-%M-%D %H:%M:%S'))

        _ = dynamo.put_item(
            TableName='Inferences',
            Item={
                'username': {
                    'S': username
                },
                'timestamp': {
                    'S': timestamp
                },
                'object_path': {
                    'S': object_path 
                },
                'prection': {
                    'S': str(labels.tolist())
                }
            }
        )

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



if __name__ == '__main__':
    runner = create_app()
    runner.run()
    