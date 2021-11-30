# encoding:utf-8
# !/usr/bin/env python
from werkzeug.utils import secure_filename
from flask import Flask, render_template, jsonify, request, make_response, send_from_directory, abort,redirect,send_file
import time
import os
import cv2
import base64
from pandas.core.frame import DataFrame
import mediapipe as mp
import matplotlib.pyplot as plt
from io import BytesIO
from utility import *


mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# 导入模型
# pose = mp_pose.Pose(static_image_mode=True,
#                     model_complexity=2,
#                     smooth_landmarks=True,
#                     enable_segmentation = True,
#                     min_detection_confidence=0.5,
#                     min_tracking_confidence=0.5)

pose = mp_pose.Pose(static_image_mode=True, 
                    smooth_landmarks=True, 
                    min_detection_confidence=0.5)


def LandmarkPlotting(landmarks, connections):
    fig = plt.figure(figsize=(10, 10))
    ax = plt.axes(projection='3d')
    ax.view_init(elev=10, azim=10)
    plotted_landmarks = {}
    for idx, landmark in enumerate(landmarks):
        ax.scatter3D(
            xs=[-landmark.z],
            ys=[landmark.x],
            zs=[-landmark.y],
            color="#FF0000",
            linewidth=5)
        plotted_landmarks[idx] = (-landmark.z, landmark.x, -landmark.y)

    for connection in connections:
        start_idx = connection[0]
        end_idx = connection[1]

        landmark_pair = [
            plotted_landmarks[start_idx], plotted_landmarks[end_idx]
        ]
        ax.plot3D(
            xs=[landmark_pair[0][0], landmark_pair[1][0]],
            ys=[landmark_pair[0][1], landmark_pair[1][1]],
            zs=[landmark_pair[0][2], landmark_pair[1][2]],
            color="#000000")
    return fig




app = Flask(__name__)
UPLOAD_FOLDER = 'upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
basedir = os.path.abspath(os.path.dirname(__file__))
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'JPG', 'PNG', 'gif', 'GIF'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/')
def upload_test():
    return render_template('index_post.html')


# 上传文件
@app.route('/up_photo', methods=['POST'], strict_slashes=False)
def api_upload():
    file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    f = request.files['photo']

    if f and allowed_file(f.filename):
        fname = secure_filename(f.filename)
        ext = fname.rsplit('.', 1)[1]
        new_filename = fname
        # new_filename = Pic_str().create_uuid() + '.' + ext
        f.save(os.path.join(file_dir, new_filename))
        # return jsonify({"success": 0, "msg": "上传成功"})
        return redirect ('/show/%s'%fname)
    else:
        return jsonify({"error": 1001, "msg": "上传失败"})


@app.route('/download/<string:filename>', methods=['GET'])
def download(filename):
    if request.method == "GET":
        if os.path.isfile(os.path.join('upload', filename)):
            return send_from_directory('upload', filename, as_attachment=True)
        pass


# show photo
@app.route('/show/<string:filename>', methods=['GET'])
def show_photo(filename):
    file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
    if request.method == 'GET':
        if filename is None:
            pass
        else:
            img = cv2.imread(os.path.join(file_dir, filename))

            img_RGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = pose.process(img_RGB)
            mp_drawing.draw_landmarks(img, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)


            ext = os.path.splitext(filename)[1]
            renewname = os.path.splitext(filename)[0]+'_2D'+ext
            renewname_3D = os.path.splitext(filename)[0] + '_3D' + ext
            cv2.imwrite(os.path.join(file_dir, renewname), img)


            fig_3D = LandmarkPlotting(results.pose_world_landmarks.landmark,mp_pose.POSE_CONNECTIONS)
            fig_3D.savefig(os.path.join(file_dir, renewname_3D))

            image_data = open(os.path.join(file_dir, '%s' % renewname), "rb").read()
            response = make_response(image_data)
            response.headers['Content-Type'] = 'image/png'

            joint_angle = angle_process(results)
            joint_angle = DataFrame(joint_angle)
            joint_angle = joint_angle.T
            joint_angle.columns = ['right_shoulder', 'right_elbow', 'right_wrist',
                         'left_shoulder', 'left_elbow', 'left_wrist']

            csv_name = os.path.splitext(filename)[0] + '.' + 'csv'
            csv_path = os.path.join(file_dir, csv_name)
            joint_angle.to_csv(csv_path)


        return response
    else:
        pass
# analysis
@app.route('/get/<string:filename>', methods=['GET'])

def analysis_photo(filename):
    file_dir = './upload/'
    filename = secure_filename(filename)
    filename_w = file_dir + filename
    ext = os.path.splitext(filename)[1]
    renewname = file_dir + os.path.splitext(filename)[0] + '_2D' + ext
    renewname3d = file_dir + os.path.splitext(filename)[0] + '_3D' + ext
    csv_dir = file_dir + os.path.splitext(filename)[0] + '.' + 'csv'
    data_list = [filename_w, renewname, renewname3d,csv_dir]
    zip_name = file_dir + os.path.splitext(filename)[0] + '.' + 'zip'

    make_zip(zip_name, data_list)

    return send_file(zip_name)
  

if __name__ == '__main__':
   # app.run(debug=True,port=40055)
   app.run(debug=True,host='172.18.115.247',port=40055)  