from photon_register_policy import PhotonRawInfo, PhotonType, FluorescentLine
import numpy as np

print('hello world')

photonRawInfo = PhotonRawInfo.build_photon_raw_info(raw_info='6404.7 0.1 0.1 3 13 1 1e13 2 1e12 1e12 1e12 1e9')

print(photonRawInfo)
