from photon_register_policy import PhotonRawInfo, PhotonType, FluorescentLine
import numpy as np

print('hello world')

photonRawInfo = PhotonRawInfo(
    hv=6404.7,
    theta=0.1,
    phi=0.1,
    photonType=PhotonType('1'),
    line=FluorescentLine('13'),
    numOfScatterings=1,
    totalPathLength=1e12,
    numOfClouds=3,
    escapePosition=np.array([1,2,3]),
    effectiveLength=1e8
    )
