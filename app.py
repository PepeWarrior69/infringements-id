from time import sleep
import cv2, streamlink

from src import IncidentAnalyzer


video_url = "https://www.youtube.com/watch?v=1EiC9bvVGnk"
streams = streamlink.streams(url=video_url)

cap = cv2.VideoCapture(streams["best"].url)
incident_analyzer = IncidentAnalyzer()

while True:
    ret, frame = cap.read()
    
    incident_analyzer.analyze_frame(frame)

    if cv2.waitKey(1) & 0xff == ord('q'):
        break
    
    sleep(0.01)
    # break

cap.release()
cv2.destroyAllWindows()
