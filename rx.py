#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import cv2, time, cv, datetime, os, code
import numpy as np
import operator


BLUE_SIGNAL_THRESHOLD = 150
PREVIEW = False
SAVE = False


class VLC():
    def __init__(self):
        self.dirname = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        os.mkdir("img/" + self.dirname)
        # 第幾張照片，用來存照片用的編號
        self.imgcount = 0
        # 收到的訊息
        self.sequence = []
        self.capture()


    def capture(self):
        vc = cv2.VideoCapture(0)
        rval = True
        while rval and vc.isOpened():
            rval, frame = vc.read()
            self.save(frame)
            frame = self.crop(frame)
            result = self.decode_frame(frame)

    # 對每個frame做decode
    def decode_frame(self, frame):
        if frame == None:
            return
        global BLUE_SIGNAL_THRESHOLD
        frame = (frame[:,:,0] >= BLUE_SIGNAL_THRESHOLD).astype('uint8')
        strips = np.any(frame, axis=1)
        self.preview(frame, strips)
        pixel = self.decode_strip(strips)
        self.sequence_add(int(round((pixel-3.00)/2.525)))
        return None

    # 每收到一個字就加進sequence
    def sequence_add(self, number):
        self.sequence.append(number)
        if self.sequence[-2:] == [0,0]:
            self.sequence = self.sequence[:-2]
            line = self.assemblebyte()
            if line:
                print line
            else:
                print "<checksum error>"
            self.sequence = []

    def assemblebyte(self):
        if len(self.sequence) %2 != 0:
            return None
        # assemble
        line = ""
        for i in range(0, len(self.sequence), 2):
            line += chr(self.sequence[i]*16+self.sequence[i+1])
        # checksum
        checksum = 0
        for i in range(len(line)-1):
            checksum = (checksum*256 + ord(line[i])) % 255
        if checksum == ord(line[-1]):
            return line[:-1]
        return None

    # debug用，預覽取得的畫面，加上解出的線條
    # 每張花0.2秒，在production的時候無法使用
    def preview(self, frame, strips):
        global PREVIEW
        if PREVIEW:
            img = np.zeros((frame.shape[0], frame.shape[1]+40), 'uint8')
            img[:, 0:frame.shape[1]] = frame
            img[:, frame.shape[1]+20:] = strips.reshape((strips.shape[0], 1))
            cv2.imshow("preview", img*255)







    # 解出每一條的pixel value
    def decode_strip(self, strip):
        # 後項-前項
        def minus_previous(L):
            L = np.array(L, dtype='float')
            return list(L[1:]*.5 + L[:-1]*.5)
        # 黑線中點，及白線中點距離，取中位數
        bw_mix = []
        for i in range(strip.shape[0]):
            if i > 0 and strip[i]==strip[i-1]:
                bw_mix[-1] += 1
            else:
                if i > 0:
                    halflastlength = bw_mix[-1]*0.5
                else:
                    halflastlength = 0
                bw_mix.append(1)
        # 頭尾可能是不完整的線條，不要
        bw_mix = bw_mix[1:-1]
        b2w = minus_previous(bw_mix)
        # 中位數
        return np.median(b2w)

    # 存檔，耗時0.03s，最後跑的時候不會存否則無法realtime
    def save(self, frame):
        global SAVE
        if SAVE and frame != None:
            self.imgcount += 1
            cv2.imwrite("img/%s/capture_%s_%04d.png" % (self.dirname,
                                                        datetime.datetime.now().strftime("%H%M%S_%f"),
                                                        self.imgcount), frame)

    # 依照blue channel把不需要的黑色部份裁掉
    def crop(self, frame):
        global BLUE_SIGNAL_THRESHOLD
        frame_blue = (frame[:, :, 0] >= BLUE_SIGNAL_THRESHOLD)
        axis0 = np.any(frame_blue, axis = 0)
        if not np.any(axis0):
            return None
        axis1 = np.any(frame_blue, axis = 1)
        ymin, ymax, xmin, xmax = (0, frame.shape[0], 0, frame.shape[1])
        while not axis1[ymin]:
            ymin += 1
        while not axis0[xmin]:
            xmin += 1
        while not axis1[ymax-1]:
            ymax -= 1
        while not axis0[xmax-1]:
            xmax -= 1
        return frame[ymin:ymax, xmin:xmax, :]






if __name__ == "__main__":
   v = VLC()
