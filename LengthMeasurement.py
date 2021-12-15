import cv2 as cv
import numpy as np
from math import atan2
from math import degrees


def getContours(img, steps='5', canny_thresh=(100, 100), min_area=1000, filter=0, draw=False):
    imgGray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    imgBlur = cv.GaussianBlur(imgGray, (5, 5), 1)
    imgCanny = cv.Canny(imgBlur, canny_thresh[0], canny_thresh[1])

    kernel = np.ones((5, 5))

    img_dilate = cv.dilate(imgCanny, kernel, iterations=3)
    img_thresh = cv.erode(img_dilate, kernel, iterations=2)

    contours, heirarchy = cv.findContours(img_thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    if steps == '1':
        return img_thresh, contours

    final_contours = []

    for i in contours:
        area = cv.contourArea(i)
        if area > min_area:
            perimeter = cv.arcLength(i, True)
            approx = cv.approxPolyDP(i, 0.02 * perimeter, True)
            bbox = cv.boundingRect(approx)
            if filter > 0:
                if len(approx) == filter:
                    final_contours.append([len(approx), area, approx, bbox, i])
            else:
                final_contours.append([len(approx), area, approx, bbox, i])


    final_contours = sorted(final_contours, key=lambda x: x[1], reverse=True)

    if draw:
        for con in final_contours:
            cv.drawContours(img, con[4], -1, (0, 0, 255), 3)


    return img, final_contours




def reorder(points):
    points_new = np.zeros_like(points)
    points = points.reshape((4,2))
    add = points.sum(1)
    points_new[0] = points[np.argmin(add)]
    points_new[3] = points[np.argmax(add)]
    diff = np.diff(points, axis=1)
    points_new[1] = points[np.argmin(diff)]
    points_new[2] = points[np.argmax(diff)]
    return points_new




def warpImg(img, points, width, height):

    points = reorder(points)

    points1 = np.float32(points)
    points2 = np.float32([[0, 0], [width, 0], [0, height], [width, height]])
    matrix = cv.getPerspectiveTransform(points1, points2)

    warped_image = cv.warpPerspective(img, matrix, (width, height))


    return  warped_image




def pad_image(img, pad=20):
    img = img[pad: img.shape[0] - pad, pad: img.shape[1] - pad]

    return img



def find_diatnce(points1, points2):
    return ((points1[0] - points2[0]) ** 2 + (points1[1] - points2[1]) ** 2) ** 0.5




def main_cv(frame, paper_size, unit, steps, custom_width=0, custom_height=0, window_size=(1500,1000)):

    if paper_size == 'A3':
        paper_width = 297
        paper_height = 420
    elif paper_size == 'A4':
        paper_width = 210
        paper_height = 497
    elif paper_size == 'A5':
        paper_width = 148.5
        paper_height = 210
    elif paper_size == 'Custom':
        paper_width = custom_width
        paper_height = custom_height

    scale = 3
    paper_width = paper_width * scale
    paper_height = paper_height * scale


    if steps == '1':
        frame, x = getContours(frame, steps=steps,min_area=50000, filter=4)
        return frame

    if steps == '2':
        frame, contours1 = getContours(frame,steps=steps, min_area=50000, filter=4, draw=True)
        return frame

    frame, contours1 = getContours(frame, steps=steps, min_area=50000, filter=4)


    if len(contours1) != 0:
        biggest_contour = contours1[0][2]
        warp_image = warpImg(frame, biggest_contour, int(paper_width), int(paper_height))
        warp_image = pad_image(warp_image)

        frame, contours2 = getContours(warp_image, steps=steps, min_area=2000, filter=4, canny_thresh=[50, 50])

        if steps == '3':
            return frame

        if len(contours2) != 0:
            for obj in contours2:
                cv.polylines(frame, [obj[2]], True, (0, 255, 0), 2)
                npoints = reorder(obj[2])
                width = find_diatnce(npoints[0][0], npoints[1][0])
                height = find_diatnce(npoints[0][0], npoints[2][0])

                if steps == '4':
                    return frame

                if unit == 'MM':
                    width = round(width, 1)
                    height = round(height, 1)
                if unit == 'CM':
                    width = round((width / scale / 10), 1)
                    height = round((height / scale / 10), 1)
                if unit == 'INCH':
                    width = round(width / scale / 25.4, 1)
                    height = round(height / scale / 25.4, 1)
                if unit == 'FOOT':
                    width = round(width / scale / 305, 1)
                    height = round(height / scale / 305, 1)

                cv.arrowedLine(frame, (npoints[0][0][0], npoints[0][0][1]), (npoints[1][0][0], npoints[1][0][1]),
                               (0, 0, 255), 3, 8, 0, 0.05)
                cv.arrowedLine(frame, (npoints[0][0][0], npoints[0][0][1]), (npoints[2][0][0], npoints[2][0][1]),
                               (0, 0, 255), 3, 8, 0, 0.05)
                x, y, w, h = obj[3]

                angle1 = atan2((npoints[1][0][1] - npoints[0][0][1]), (npoints[1][0][0] - npoints[0][0][0]))
                angle1 = degrees(angle1)
                angle2 = atan2((npoints[2][0][1] - npoints[0][0][1]), (npoints[2][0][0] - npoints[0][0][0]))
                angle2 = degrees(angle2)

                font = cv.FONT_HERSHEY_COMPLEX_SMALL

                cv.putText(frame, '{} {}'.format(width, unit.casefold()), (x + 30, y - 10), font, 1,
                           (0, 0, 255), 2)
                cv.putText(frame, '{} {}'.format(height, unit.casefold()), (x - 70, y + h // 2), font, 1,
                           (0, 0, 255), 2)

    return frame