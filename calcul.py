from math import *
import mediapipe as mp
import settings
from google.protobuf.json_format import MessageToDict

# Computes the euclidian length between 2 points
def eucli_length(P1,P2):
    x1, y1, z1 = P1
    x2, y2, z2 = P2
    return sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)

# Computes the cosinus opposed to the 'a' segment with Alkashi's method
def cos_alkashi(a,b,c):
    return (b**2 + c**2 - a**2)/(2*b*c)

# Converts degrees into radians
def radian(x):
    return x*2*pi/360

# Creates an array composed of the 21 hand's landmarks 
def pos_hand_landmarks(image, results):
    for hand_landmarks in results.multi_hand_landmarks : 
        pos = []
        for i in range(21):
            xi, yi, zi = hand_landmarks.landmark[i].x*settings.sw, hand_landmarks.landmark[i].y*settings.sh, hand_landmarks.landmark[i].z*1500
            pos.append((xi, yi, zi))
    return pos

# Right or Left hand ? 
def handedness(results):
    for idx, hand_handedness in enumerate(results.multi_handedness):
                    handedness_dict = MessageToDict(hand_handedness)
                    whichHand =(handedness_dict['classification'][0]['label'])
                    return whichHand

def little_wrap(pos): # level 1 of wrapping your fingers
    if pos[8][1] > pos[6][1] and pos[12][1] > pos[10][1] and pos[16][1] > pos[14][1] and pos[20][1] > pos[18][1]:
        return True
    else :
        return False

def really_wrap(pos): # level 2 of wrapping your fingers
    if pos[8][1] > pos[5][1] and pos[12][1] > pos[9][1] and pos[16][1] > pos[13][1] and pos[20][1] > pos[17][1]:
        return True
    else :
        return False

def spread(pos):
    # distances to the wrist
    thumb = eucli_length(pos[0],pos[4])
    ind_fing = eucli_length(pos[0],pos[8])
    mid_fing = eucli_length(pos[0],pos[12])
    ring_fing = eucli_length(pos[0],pos[16])
    little_fing = eucli_length(pos[0],pos[20])

    # distances between fingers
    thumb_to_ind = eucli_length(pos[4],pos[8])
    ind_to_mid = eucli_length(pos[8],pos[12])
    mid_to_ring = eucli_length(pos[12],pos[16])
    ring_to_little = eucli_length(pos[16],pos[20])

    if cos_alkashi(thumb_to_ind,thumb,ind_fing) < cos(radian(10)) and cos_alkashi(thumb_to_ind,thumb,ind_fing) > cos(radian(45)) :
            if cos_alkashi(ind_to_mid,mid_fing,ind_fing) < cos(radian(10)) and cos_alkashi(ind_to_mid,mid_fing,ind_fing) > cos(radian(45)) :
                    if cos_alkashi(mid_to_ring,mid_fing,ring_fing) < cos(radian(10)) and cos_alkashi(mid_to_ring,mid_fing,ring_fing) > cos(radian(45)) :
                            if cos_alkashi(ring_to_little,ring_fing,little_fing) < cos(radian(10)) and cos_alkashi(ring_to_little,ring_fing,little_fing) > cos(radian(45)) :
                                if abs(pos[4][2]-pos[0][2])<=85 and abs(pos[8][2]-pos[0][2])<=95 and abs(pos[12][2]-pos[0][2])<=105 and abs(pos[16][2]-pos[0][2])<=125 and abs(pos[20][2]-pos[0][2])<=140 : #straight hand
                                    return True
    

    

#     # distances of the phalanxes 
#     a_thumb = calcul.eucli_length(pos[3],pos[1])
#     b_thumb = calcul.eucli_length(pos[3],pos[2])
#     c_thumb = calcul.eucli_length(pos[2],pos[1])
#     a_ind_fing = calcul.eucli_length(pos[7],pos[5])
#     b_ind_fing = calcul.eucli_length(pos[7],pos[6])
#     c_ind_fing = calcul.eucli_length(pos[6],pos[5])
#     a_mid_fing = calcul.eucli_length(pos[11],pos[9])
#     b_mid_fing = calcul.eucli_length(pos[11],pos[10])
#     c_mid_fing = calcul.eucli_length(pos[10],pos[9])
#     a_ring_fing = calcul.eucli_length(pos[15],pos[13])
#     b_ring_fing = calcul.eucli_length(pos[15],pos[14])
#     c_ring_fing = calcul.eucli_length(pos[14],pos[13])
#     a_little_fing = calcul.eucli_length(pos[19],pos[17])
#     b_little_fing = calcul.eucli_length(pos[19],pos[18])
#     c_little_fing = calcul.eucli_length(pos[18],pos[17])
    
#     # cosinus of the angles of the fingers
#     thumb_angle = calcul.cos_alkashi(a_thumb,b_thumb,c_thumb)
#     ind_angle = calcul.cos_alkashi(a_ind_fing,b_ind_fing,c_ind_fing)
#     mid_angle = calcul.cos_alkashi(a_mid_fing,b_mid_fing,c_mid_fing)
#     ring_angle = calcul.cos_alkashi(a_ring_fing,b_ring_fing,c_ring_fing)
#     little_angle = calcul.cos_alkashi(a_little_fing,b_little_fing,c_little_fing)