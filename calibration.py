import numpy as np
import cv2 as cv

def select_img_from_video(video_file, board_pattern, select_all=False, wait_msec=10, wnd_name='Camera Calibration'):
    video = cv.VideoCapture(video_file)
    assert video.isOpened(), f"Cannot open video: {video_file}"

    img_select = []
    while True:
        valid, img = video.read()
        if not valid:
            break

        if select_all:
            img_select.append(img)
        else:
            display = img.copy()
            cv.putText(display, f'NSelect: {len(img_select)}', (10, 25), cv.FONT_HERSHEY_DUPLEX, 0.6, (0, 255, 0))
            cv.imshow(wnd_name, display)

            key = cv.waitKey(wait_msec)
            if key == ord(' '):  # Space: detect corners and pause
                complete, pts = cv.findChessboardCorners(img, board_pattern)
                if complete:
                    cv.drawChessboardCorners(display, board_pattern, pts, complete)
                cv.imshow(wnd_name, display)
                key = cv.waitKey()
                if key == ord('\r') or key == 13:  # Enter: confirm selection
                    img_select.append(img)
            if key == 27:  # ESC: exit
                break

    cv.destroyAllWindows()
    return img_select

def calib_camera_from_chessboard(images, board_pattern, board_cellsize, K=None, dist_coeff=None, calib_flags=None):
    img_points = []
    for img in images:
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        complete, pts = cv.findChessboardCorners(gray, board_pattern)
        if complete:
            img_points.append(pts)

    assert len(img_points) > 0, "No valid chessboard detections!"

    # Generate object points (3D) for the board
    obj_pts = [[c, r, 0] for r in range(board_pattern[1]) for c in range(board_pattern[0])]
    obj_points = [np.array(obj_pts, dtype=np.float32) * board_cellsize] * len(img_points)

    # Calibrate the camera
    return cv.calibrateCamera(obj_points, img_points, gray.shape[::-1], K, dist_coeff, flags=calib_flags)

if __name__ == '__main__':
    video_file = 'chessboard.mp4'       
    board_pattern = (8, 6)                     
    board_cellsize = 0.029         # 한 칸의 실제 크기 (m 단위)

    # === 프레임 선택 ===
    img_select = select_img_from_video(video_file, board_pattern)
    assert len(img_select) > 0, 'There is no selected image!'

    # === 카메라 보정 수행 ===
    rms, K, dist_coeff, rvecs, tvecs = calib_camera_from_chessboard(img_select, board_pattern, board_cellsize)

    # === 결과 출력 ===
    print('## Camera Calibration Results')
    print(f'* The number of selected images = {len(img_select)}')
    print(f'* RMS reprojection error = {rms:.6f}')
    print(f'* Camera matrix (K) = \n{K}')
    print(f'* Distortion coefficients = {dist_coeff.flatten()}')
