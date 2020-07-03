import cv2
import numpy as np
import dlib


def extract_index_nparray(nparray):
    index = None
    for num in nparray[0]:
        index = num
        break
    return index


def find_landmarks_points(img, shape_predictor_path):
    img_grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(shape_predictor_path)

    faces = detector(img_grey)
    first_face = faces[0]

    landmarks = predictor(img_grey, first_face)
    landmarks_points = []

    for dot in range(0, 68):
        x = landmarks.part(dot).x
        y = landmarks.part(dot).y
        landmarks_points.append((x, y))

        # cv2.circle(img, (x, y), 1, (0, 0, 255), -1)  # draw face dots

    return landmarks_points


def find_indexes_face_triangles(img, landmarks_points, convexhull):
    landmarks_points_numpy = np.array(landmarks_points, np.int32)

    rect = cv2.boundingRect(convexhull)

    subdiv = cv2.Subdiv2D(rect)
    subdiv.insert(landmarks_points)

    triangles = subdiv.getTriangleList()
    triangles = np.array(triangles, dtype=np.int32)

    indexes_triangles = []

    for t in triangles:
        pt1 = (t[0], t[1])
        pt2 = (t[2], t[3])
        pt3 = (t[4], t[5])

        index_pt1 = np.where((landmarks_points_numpy == pt1).all(axis=1))
        index_pt1 = extract_index_nparray(index_pt1)
        index_pt2 = np.where((landmarks_points_numpy == pt2).all(axis=1))
        index_pt2 = extract_index_nparray(index_pt2)
        index_pt3 = np.where((landmarks_points_numpy == pt3).all(axis=1))
        index_pt3 = extract_index_nparray(index_pt3)

        # # draw triangles
        # cv2.line(img, pt1, pt2, (255, 0, 0), 1)
        # cv2.line(img, pt2, pt3, (255, 0, 0), 1)
        # cv2.line(img, pt1, pt3, (255, 0, 0), 1)

        if index_pt1 is not None and index_pt2 is not None and index_pt3 is not None:
            triangle = [index_pt1, index_pt2, index_pt3]
            indexes_triangles.append(triangle)

    return indexes_triangles


def create_mask_img(img, convexhull):
    img_grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mask = np.zeros_like(img_grey)
    cv2.fillConvexPoly(mask, convexhull, 255)
    return mask


def ugly_face_swap(img_1_path, img_2_path, predictor_path):
    img_1 = cv2.imread(img_1_path)
    img_2 = cv2.imread(img_2_path)

    landmarks_points_1 = find_landmarks_points(img_1, predictor_path)
    landmarks_points_numpy_1 = np.array(landmarks_points_1, np.int32)
    convexhull_1 = cv2.convexHull(landmarks_points_numpy_1)
    indexes_triangles_1 = find_indexes_face_triangles(img_1, landmarks_points_1, convexhull_1)

    landmarks_points_2 = find_landmarks_points(img_2, predictor_path)
    landmarks_points_numpy_2 = np.array(landmarks_points_2, np.int32)
    convexhull_2 = cv2.convexHull(landmarks_points_numpy_2)

    img2_new_face = np.zeros_like(img_2)
    img_1_gray = cv2.cvtColor(img_1, cv2.COLOR_BGR2GRAY)

    lines_space_mask = np.zeros_like(img_1_gray)

    for triangle_index in indexes_triangles_1:
        # face 1
        tr1_pt1 = landmarks_points_1[triangle_index[0]]
        tr1_pt2 = landmarks_points_1[triangle_index[1]]
        tr1_pt3 = landmarks_points_1[triangle_index[2]]
        triangle1 = np.array([tr1_pt1, tr1_pt2, tr1_pt3], np.int32)

        rect1 = cv2.boundingRect(triangle1)
        (x, y, w, h) = rect1

        cropped_triangle = img_1[y: y + h, x: x + w]
        cropped_tr1_mask = np.zeros((h, w), np.uint8)
        points_1 = np.array([[tr1_pt1[0] - x, tr1_pt1[1] - y],
                             [tr1_pt2[0] - x, tr1_pt2[1] - y],
                             [tr1_pt3[0] - x, tr1_pt3[1] - y]], np.int32)
        cv2.fillConvexPoly(cropped_tr1_mask, points_1, 255)

        # Lines space
        cv2.line(lines_space_mask, tr1_pt1, tr1_pt2, 255)
        cv2.line(lines_space_mask, tr1_pt2, tr1_pt3, 255)
        cv2.line(lines_space_mask, tr1_pt1, tr1_pt3, 255)

        # face 2
        tr2_pt1 = landmarks_points_2[triangle_index[0]]
        tr2_pt2 = landmarks_points_2[triangle_index[1]]
        tr2_pt3 = landmarks_points_2[triangle_index[2]]
        triangle2 = np.array([tr2_pt1, tr2_pt2, tr2_pt3], np.int32)
        rect2 = cv2.boundingRect(triangle2)
        (x, y, w, h) = rect2
        cropped_triangle2 = img_2[y: y + h, x: x + w]
        cropped_tr2_mask = np.zeros((h, w), np.uint8)
        points_2 = np.array([[tr2_pt1[0] - x, tr2_pt1[1] - y],
                             [tr2_pt2[0] - x, tr2_pt2[1] - y],
                             [tr2_pt3[0] - x, tr2_pt3[1] - y]], np.int32)
        cv2.fillConvexPoly(cropped_tr2_mask, points_2, 255)

        # Warp triangles
        points_float_1 = np.float32(points_1)
        points_float_2 = np.float32(points_2)
        M = cv2.getAffineTransform(points_float_1, points_float_2)
        warped_triangle = cv2.warpAffine(cropped_triangle, M, (w, h))
        warped_triangle = cv2.bitwise_and(warped_triangle, warped_triangle, mask=cropped_tr2_mask)

        # Reconstructing destination face
        img2_new_face_rect_area = img2_new_face[y: y + h, x: x + w]
        img2_new_face_rect_area_gray = cv2.cvtColor(img2_new_face_rect_area, cv2.COLOR_BGR2GRAY)
        _, mask_triangles_designed = cv2.threshold(img2_new_face_rect_area_gray, 1, 255, cv2.THRESH_BINARY_INV)
        warped_triangle = cv2.bitwise_and(warped_triangle, warped_triangle, mask=mask_triangles_designed)

        img2_new_face_rect_area = cv2.add(img2_new_face_rect_area, warped_triangle)
        img2_new_face[y: y + h, x: x + w] = img2_new_face_rect_area

    # Face swapped (putting 1st face into 2nd face)
    img2_gray = cv2.cvtColor(img_2, cv2.COLOR_BGR2GRAY)
    img2_face_mask = np.zeros_like(img2_gray)
    img2_head_mask = cv2.fillConvexPoly(img2_face_mask, convexhull_2, 255)
    img2_face_mask = cv2.bitwise_not(img2_head_mask)

    img2_head_noface = cv2.bitwise_and(img_2, img_2, mask=img2_face_mask)
    result = cv2.add(img2_head_noface, img2_new_face)

    (x, y, w, h) = cv2.boundingRect(convexhull_2)
    center_face2 = (int((x + x + w) / 2), int((y + y + h) / 2))

    result_img = cv2.seamlessClone(result, img_2, img2_head_mask, center_face2, cv2.NORMAL_CLONE)
    return result_img
