# mPyPl - Monadic Pipeline Library for Python
# http://github.com/shwars/mPyPl

# Different services related to Face API

import requests
from ..mdict import *
from .core import CognitiveService

class FaceApi(CognitiveService):

    def __init__(self,key,location="northeurope"):
        super(FaceApi,self).__init__(key,"https://{}.api.cognitive.microsoft.com/face/v1.0/".format(location))

    def detect_url(self,url,faceId=False,faceLandmarks=False,faceAttributes="age,gender,smile,facialHair,headPose,glasses,emotion,hair,makeup,accessories,blur,exposure,noise", recognitionModel="recognition_02"):
        res = self.request_post(params={ "returnFaceId" : faceId, "returnFaceLandmarks" : faceLandmarks, "returnFaceAttributes" : faceAttributes, "recognitionModel": recognitionModel }, data={ "url" : url },method="detect", headers={'Content-Type': 'application/json'})
        return res

    def detect_image(self,data,faceId=False,faceLandmarks=False,faceAttributes="age,gender,smile,facialHair,headPose,glasses,emotion,hair,makeup,accessories,blur,exposure,noise", recognitionModel="recognition_02"):
        res = self.request_post(params={ "returnFaceId" : faceId, "returnFaceLandmarks" : faceLandmarks, "returnFaceAttributes" : faceAttributes, "recognitionModel": recognitionModel }, data=data,method="detect", headers={'Content-Type': 'application/octet-stream'})
        return res
