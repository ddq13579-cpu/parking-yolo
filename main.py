import cv2
import time
import requests
import numpy as np
from ultralytics import YOLO
from shapely.geometry import Polygon, Point
from config import (
    RTSP_URL,
    SNAPSHOT_URL,
    BARK_KEYS,
    FRAME_INTERVAL,
    EMPTY_CONFIRM,
    OCCUPY_CONFIRM,
    PARKING_SLOTS,
    DETECT_CLASSES,
    PUSH_SLOTS,
    DAY_conf,
    NIGHT_conf,
    NIGHT_BRIGHTNESS_THRESHOLD,
)
SNAPSHOT_PATH = "/snapshots/parking_snapshot.jpg"

# =====================
# Bark 推送
# =====================
def bark_push(msg: str, title: str = "停车位提醒", image_url=None):
    for key in BARK_KEYS:
        url = f"https://api.day.app/{key}/{title}"
        params = {"body": msg}

        if image_url:
            params["url"] = image_url

        try:
            response = requests.get(url, params=params, timeout=5)
            if response.status_code != 200:
                print(f"Bark push failed for {key}: {response.text}")
        except Exception as e:
            print(f"Bark push exception for {key}: {e}")


# =====================
# 工具函数：读取最新帧（并裁剪下半部分）
# =====================
def read_latest_frame(cap, max_reads=10):
    frame = None
    for _ in range(max_reads):
        ret, f = cap.read()
        if not ret or f is None:
            break
        frame = f

    if frame is None:
        return None

    h, w = frame.shape[:2]

    # 只取下半部分
    frame = frame[h // 2 : h, :]

    return frame


# =====================
# 工具函数：绘制车位 ROI 测试用
# =====================
#def draw_parking_rois(image):
    """在结果图上标出车位 ROI，便于核对检测框是否命中。"""
    for slot_id, slot in PARKING_SLOTS.items():
        points = np.array(slot["polygon"], dtype=np.int32).reshape((-1, 1, 2))
        cv2.polylines(image, [points], isClosed=True, color=(0, 0, 255), thickness=2)

        # OpenCV 默认字体不支持中文，因此使用车位编号作为图上标识。
        label_x, label_y = slot["polygon"][0]
        cv2.putText(
            image,
            f"ROI {slot_id}",
            (label_x, max(16, label_y - 6)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (0, 0, 255),
            1,
            cv2.LINE_AA,
        )


# =====================
# 初始化
# =====================
model = YOLO("yolo11m.pt")
bark_push("程序启动确认", title="我要开始工作了")

slot_state = {
    slot_id: {"state": "unknown", "empty": 0, "occupy": 0}
    for slot_id in PARKING_SLOTS
}

cap = cv2.VideoCapture(RTSP_URL)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

if not cap.isOpened():
    raise RuntimeError("RTSP stream cannot be opened, please check RTSP_URL")


# =====================
# 主循环
# =====================
last_process_time = 0

while True:
    frame = read_latest_frame(cap, max_reads=10)

    if frame is None:
        print("[WARN] RTSP read failed, reconnecting...", flush=True)
        cap.release()
        time.sleep(2)
        cap = cv2.VideoCapture(RTSP_URL)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        continue

    now = time.time()
    if now - last_process_time < FRAME_INTERVAL:
        continue

    last_process_time = now

    infer_frame = frame.copy()
    draw_frame = frame.copy()
#画roi检测框，测试用！！
    #draw_parking_rois(draw_frame)

    # -------- 昼夜判断 --------
    gray = cv2.cvtColor(infer_frame, cv2.COLOR_BGR2GRAY)
    brightness = gray.mean()

    is_night = brightness < NIGHT_BRIGHTNESS_THRESHOLD
    CONF_SET = NIGHT_conf if is_night else DAY_conf

    print(
        f"[ENV] brightness={brightness:.1f} "
        f"mode={'NIGHT' if is_night else 'DAY'} ",
        flush=True
    )

    # -------- YOLO 推理 --------
    results = model(
        infer_frame,
        conf=CONF_SET,
        iou=0.5,
        verbose=True,
        classes=DETECT_CLASSES
    )

    print(
        "YOLO boxes:",
        sum(len(r.boxes) for r in results if r.boxes is not None),
        flush=True
    )

    # -------- 画检测框 --------
    for r in results:
        if r.boxes is None:
            continue
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(draw_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    changed_msgs = []
    snapshot_needed = False

    # =====================
    # 车位判断（中心点 ∈ ROI）
    # =====================
    for slot_id, slot in PARKING_SLOTS.items():
        roi_poly = Polygon(slot["polygon"])
        slot_hit = False

        for r in results:
            if r.boxes is None:
                continue

            for box in r.boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                cx = float(x1 + x2) / 2
                cy = float(y1 + y2) / 2

                if roi_poly.contains(Point(cx, cy)):
                    slot_hit = True
                    break

            if slot_hit:
                break

        s = slot_state[slot_id]

        print(
            f"[{slot['name']}] "
            f"hit={slot_hit} "
            f"occupy={s['occupy']} "
            f"empty={s['empty']} "
            f"state={s['state']}",
            flush=True
        )

        # -------- 状态机 --------
        if slot_hit:
            s["occupy"] += 1
            s["empty"] = 0

            if s["state"] != "occupied" and s["occupy"] >= OCCUPY_CONFIRM:
                s["state"] = "occupied"
                changed_msgs.append({
                    "slot_id": slot_id,
                    "msg": f"{slot['name']} 车位被占用"
                })
                snapshot_needed = True
        else:
            s["empty"] += 1
            s["occupy"] = 0

            if s["state"] != "empty" and s["empty"] >= EMPTY_CONFIRM:
                s["state"] = "empty"
                changed_msgs.append({
                    "slot_id": slot_id,
                    "msg": f"车位空出来了！！！{slot['name']} "
                })
                snapshot_needed = True

    # =====================
    # 推送 + 截图
    # =====================
    if changed_msgs:
        image_url = None
        if snapshot_needed:
            cv2.imwrite(SNAPSHOT_PATH, draw_frame)
            ts = int(time.time())
            image_url = f"http://parking.dongyulong.cn:25852/parking/parking_snapshot.jpg?t={ts}"

        for item in changed_msgs:
            if item["slot_id"] not in PUSH_SLOTS:
                continue

            bark_push(
                item["msg"],
                title=item["msg"],
                image_url=image_url
            )
