from time import sleep
import cv2, streamlink

from src import IncidentAnalyzer



# url = "https://www.youtube.com/watch?v=bMt47wvK6u0"
# api_key = "AIzaSyBoUsn1c9MBP6DsFE8ZaD66SXV6G64kaNw"
# vido_id = "1EiC9bvVGnk"
video_url = "https://www.youtube.com/watch?v=1EiC9bvVGnk"


streams = streamlink.streams(url=video_url)

# print("streams = ", streams)
# print("url = ", streams["best"].url)

cap = cv2.VideoCapture(streams["best"].url)
incident_analyzer = IncidentAnalyzer()

while True:
    ret, frame = cap.read()
    
    incident_analyzer.analyze_frame(frame)

    # cv2.imshow('frame', frame)

    if cv2.waitKey(1) & 0xff == ord('q'):
        break
    
    sleep(0.01)
    # break

cap.release()
cv2.destroyAllWindows()
