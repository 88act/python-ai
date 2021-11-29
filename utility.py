import numpy as np
import zipfile
import os

def angle (x,y):
    x_=np.sqrt(x.dot(x))
    y_=np.sqrt(y.dot(y))
    dot_=x.dot(y)
    cos_=dot_/(x_*y_)
    angle_arc=np.arccos(cos_)
    angle_d=angle_arc*180/np.pi
    return angle_d


def angle_process(results):
    lmlist = []

    for id, lm in enumerate(results.pose_landmarks.landmark):
        lmlist.append([lm.x, lm.y])

    lmlist = np.array(lmlist)

    right_arm = lmlist[14] - lmlist[12]
    right_ver = lmlist[24] - lmlist[12]
    right_forearm = lmlist[16] - lmlist[14]
    right_hand = (lmlist[18] + lmlist[20]) / 2 - lmlist[16]

    left_arm = lmlist[13] - lmlist[11]
    left_ver = lmlist[23] - lmlist[11]
    left_forearm = lmlist[15] - lmlist[13]
    left_hand = ((lmlist[19] + lmlist[17]) / 2) - lmlist[15]

    right_shoulder = angle(right_arm, right_ver)
    right_elbow = angle(right_forearm, right_arm)
    right_wrist = angle(right_forearm, right_hand)

    left_shoulder = angle(left_arm, left_ver)
    left_elbow = angle(left_forearm, left_arm)
    left_wrist = angle(left_forearm, left_hand)

    angle_collect = [right_shoulder, right_elbow, right_wrist, left_shoulder, left_elbow, left_wrist]


    # angle_collect = np.array(angle_collect)

    return angle_collect

def make_zip(zip_file_name, file_names):
    with zipfile.ZipFile(zip_file_name, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        for fn in file_names:
            parent_path, name = os.path.split(fn)
            zf.write(fn, arcname=name)

