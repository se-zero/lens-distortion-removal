import numpy as np
import cv2 as cv

video_file = 'data/chessboard.mp4'  

K = np.array([
    [911.06897706, 0, 959.39682216],
    [0, 912.93482348, 536.39064935],
    [0, 0, 1]
])
dist_coeff = np.array([-0.0104789, 0.01314287, -0.00267109, 0.00416095, -0.00936107])

video = cv.VideoCapture(video_file)
assert video.isOpened(), f"Cannot open video: {video_file}"

fps = video.get(cv.CAP_PROP_FPS)
width = int(video.get(cv.CAP_PROP_FRAME_WIDTH))
height = int(video.get(cv.CAP_PROP_FRAME_HEIGHT))
fourcc = cv.VideoWriter_fourcc(*'XVID')
out = cv.VideoWriter('rectified_only.avi', fourcc, fps, (width, height))

show_rectify = True  # 보정 모드 켜짐 여부
map1, map2 = None, None  # 보정 매핑 정보
scale = 0.5  # 화면 축소 비율

while True:
    valid, img = video.read()
    if not valid:
        break

    original = img.copy()

    if show_rectify:
        if map1 is None or map2 is None:
            map1, map2 = cv.initUndistortRectifyMap(
                K, dist_coeff, None, None,
                (img.shape[1], img.shape[0]), cv.CV_32FC1
            )
        img = cv.remap(img, map1, map2, interpolation=cv.INTER_LINEAR)
        info = "Rectified"

        # === 보정된 프레임 저장 ===
        out.write(img)
    else:
        info = "Original"

    # === 화면 표시용 축소 ===
    img_resized = cv.resize(img, None, fx=scale, fy=scale)
    original_resized = cv.resize(original, None, fx=scale, fy=scale)

    cv.putText(img_resized, info, (10, 25), cv.FONT_HERSHEY_DUPLEX, 0.6, (0, 255, 0))
    cv.imshow("Geometric Distortion Correction", img_resized)

    key = cv.waitKey(10)
    if key == 27:  # ESC → 종료
        break
    elif key == ord('\t'):  # Tab → 원본/보정 토글
        show_rectify = not show_rectify
    elif key == ord('s'):  # s → 프레임 저장
        cv.imwrite('original_frame.png', original_resized)
        cv.imwrite('rectified_frame.png', img_resized)
        print("현재 프레임 저장 완료!")

video.release()
out.release()
cv.destroyAllWindows()
