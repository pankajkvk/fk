<!DOCTYPE html>
<html>
<head>
    <title>Liveness Check</title>
    <style>
        #video {
            width: 400px; /* Adjust the width as needed */
            height: 300px; /* Adjust the height as needed */
        }
    </style>
</head>
<body>

    <h2>Record Video for Liveness Check</h2>

    <video id="video" autoplay></video>
    <button id="startButton">Start Recording</button>
    <button id="stopButton" disabled>Stop Recording</button>

    <form action="process_video.php" method="post" enctype="multipart/form-data" id="videoForm">
        <input type="hidden" id="videoBlob" name="video">
        <input type="submit" value="Submit Video" id="submitButton" disabled>
    </form>
    
    <script>
        let mediaRecorder;
        let recordedBlobs;

        const video = document.getElementById('video');
        const startButton = document.getElementById('startButton');
        const stopButton = document.getElementById('stopButton');
        const videoForm = document.getElementById('videoForm');
        const submitButton = document.getElementById('submitButton');

        startButton.addEventListener('click', async () => {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                video.srcObject = stream;

                recordedBlobs = [];
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.ondataavailable = (event) => { recordedBlobs.push(event.data); };
                mediaRecorder.onstop = handleStop;

                mediaRecorder.start();

                startButton.disabled = true;
                stopButton.disabled = false;
            } catch (error) {
                console.error('Error accessing webcam:', error);
            }
        });

        stopButton.addEventListener('click', () => {
            mediaRecorder.stop();
            startButton.disabled = false;
            stopButton.disabled = true;
        });

        function handleStop() {
            const blob = new Blob(recordedBlobs, { type: 'video/webm' });
            const fileOfBlob = new File([blob], 'my-video.webm');
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(fileOfBlob);
            document.getElementById('videoBlob').files = dataTransfer.files;
            submitButton.disabled = false;
        }
    </script>

</body>
</html>
