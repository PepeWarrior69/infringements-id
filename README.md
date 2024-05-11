https://answers.opencv.org/question/31292/locating-color-in-video-frame-python/

For local development: `python3 -m pip install --force-reinstall https://github.com/yt-dlp/yt-dlp/archive/master.tar.gz`


1) Build: `docker build --no-cache -t infringements-analyzer .`

2) In docker-compose file setup ENV variables:
    - DISPLAY_IMAGES - set to false for production
    - HAAR_CASCADE_PATH - which XML file to use to identify car
    - API_ENDPOINT - endpoint to report incidents
    - STORAGE_PATH - where to save images

