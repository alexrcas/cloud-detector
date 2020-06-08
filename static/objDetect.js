const s = document.getElementById('objDetect');
const sourceVideo = s.getAttribute("data-source");
const uploadWidth = s.getAttribute("data-uploadWidth") || 640;
const mirror = s.getAttribute("data-mirror") || false;
const scoreThreshold = s.getAttribute("data-scoreThreshold") || 0.5;
const apiServer = s.getAttribute("data-apiServer") || window.location.origin + '/image';

const socket = io('http://localhost:5000');

v = document.getElementById(sourceVideo);

let isPlaying = false,
    gotMetadata = false;

let imageCanvas = document.createElement('canvas');
let imageCtx = imageCanvas.getContext("2d");

let drawCanvas = document.createElement('canvas');
document.body.appendChild(drawCanvas);
let drawCtx = drawCanvas.getContext("2d");

function drawBoxes(objects) {

    drawCtx.clearRect(0, 0, drawCanvas.width, drawCanvas.height);

    objects.filter(object => object.class_name).forEach(object => {

        let x = object.x * drawCanvas.width;
        let y = object.y * drawCanvas.height;
        let width = (object.width * drawCanvas.width) - x;
        let height = (object.height * drawCanvas.height) - y;

        if (mirror) {
            x = drawCanvas.width - (x + width)
        }

        drawCtx.fillText(object.class_name + " - " + Math.round(object.score * 100) + "%", x + 5, y - 20);
        drawCtx.strokeRect(x, y, width, height);

    });
}

function postFile(file) {
    socket.emit('mensaje', file)
    let formdata = new FormData();
    formdata.append("image", file);
    formdata.append("threshold", scoreThreshold);
}

socket.on('response', data => {
    data = JSON.parse(data)
    let objects = data;
    drawBoxes(objects)
    imageCtx.drawImage(v, 0, 0, v.videoWidth, v.videoHeight, 0, 0, uploadWidth, uploadWidth * (v.videoHeight / v.videoWidth));
    imageCanvas.toBlob(postFile, 'image/jpeg');
});

function startObjectDetection() {
    drawCanvas.width = v.videoWidth;
    drawCanvas.height = v.videoHeight;

    imageCanvas.width = uploadWidth;
    imageCanvas.height = uploadWidth * (v.videoHeight / v.videoWidth);
    drawCtx.lineWidth = 2;
    drawCtx.strokeStyle = "cyan";
    drawCtx.font = "36px Verdana";
    drawCtx.fillStyle = "cyan";

    imageCtx.drawImage(v, 0, 0, v.videoWidth, v.videoHeight, 0, 0, uploadWidth, uploadWidth * (v.videoHeight / v.videoWidth));
    imageCanvas.toBlob(postFile, 'image/jpeg');

}


v.onloadedmetadata = () => {
    console.log("video metadata ready");
    gotMetadata = true;
    if (isPlaying)
        startObjectDetection();
};

v.onplaying = () => {
    isPlaying = true;
    if (gotMetadata) {
        startObjectDetection();
    }
};

