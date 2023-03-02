import os
path = "E:/Tensorflow Object Detection/TFODCourse/Tensorflow/workspace/images/test/"

dirs = os.listdir( path )
for file in [f for f in dirs if f.endswith(".xml")]:
    with open(path+file, "r") as f:
        s = " ".join(f)
    with open(path + file, "w") as f:
        f.write(s.replace('<depth>1</depth>', '<depth>3</depth>'))
