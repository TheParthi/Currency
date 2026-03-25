let video, canvas, ctx, snapshotImg;
let startBtn, captureBtn, detectBtn, retakeBtn, resultText;

window.onload = () => {
  video = document.getElementById('camera-feed');
  canvas = document.getElementById('camera-canvas');
  ctx = canvas.getContext('2d');
  snapshotImg = document.getElementById('snapshot');
  
  startBtn = document.getElementById('start-btn');
  captureBtn = document.getElementById('capture-btn');
  detectBtn = document.getElementById('detect-btn');
  retakeBtn = document.getElementById('retake-btn');
  resultText = document.getElementById('result-text');

  // Pre-load audio engine
  window.speechSynthesis.getVoices();

  startBtn.addEventListener('click', async () => {
    try {
      // Force audio access context unlock
      let dummyUtterance = new SpeechSynthesisUtterance("Starting camera.");
      dummyUtterance.volume = 0;
      window.speechSynthesis.speak(dummyUtterance);
      
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment" }
      });
      video.srcObject = stream;
      video.style.display = 'block';
      snapshotImg.style.display = 'none';
      
      startBtn.style.display = 'none';
      captureBtn.style.display = 'block';
      resultText.innerText = "Camera Active";
      
      speakOut("Camera Active. Point at currency and press Capture.", "en-US");
    } catch (err) {
      resultText.innerText = "Camera Error";
      console.error(err);
      speakOut("Error, please check camera permissions.", "en-US");
    }
  });

  captureBtn.addEventListener('click', () => {
    if (!video.videoWidth) return;
    
    // Set canvas dimensions exactly to video frame
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Convert to Image and place over video
    const dataURL = canvas.toDataURL('image/jpeg', 0.8);
    snapshotImg.src = dataURL;
    
    video.style.display = 'none';
    snapshotImg.style.display = 'block';
    
    captureBtn.style.display = 'none';
    detectBtn.style.display = 'block';
    retakeBtn.style.display = 'block';
    resultText.innerText = "Captured. Press Detect.";
    
    speakOut("Image captured. Please press Detect.", "en-US");
  });

  retakeBtn.addEventListener('click', () => {
    video.style.display = 'block';
    snapshotImg.style.display = 'none';
    
    detectBtn.style.display = 'none';
    retakeBtn.style.display = 'none';
    captureBtn.style.display = 'block';
    resultText.innerText = "Camera Active";
  });

  detectBtn.addEventListener('click', () => {
    detectBtn.style.display = 'none';
    retakeBtn.style.display = 'none';
    resultText.innerText = "Scanning on Server...";
    speakOut("Detecting now...", "en-US");

    canvas.toBlob((blob) => {
      let formData = new FormData();
      formData.append('image', blob, 'capture.jpg');
      
      $.ajax({
        url: "/detectObject",
        type: "POST",
        data: formData,
        cache: false,
        processData: false,
        contentType: false,
        success: function(data) {
          const englishMsg = data['englishmessage'];
          const tamilMsg = data['tamilmessage'];
          const returnedImg = data['status'];
          
          if(returnedImg) {
              snapshotImg.src = 'data:image/jpeg;base64,' + returnedImg;
          }
          
          if (englishMsg && englishMsg.trim() !== "Image contains" && englishMsg.indexOf("another better image") === -1) {
              const cleanMsg = englishMsg.replace(/Image contains/gi, '').trim();
              resultText.innerText = cleanMsg;
              
              speakOut(tamilMsg, "ta-IN");
              speakOut(cleanMsg, "en-US");
          } else {
              resultText.innerText = "Nothing detected. Retake.";
              speakOut("Nothing detected. Please retake the photo.", "en-US");
          }
          retakeBtn.style.display = 'block';
        },
        error: function(err) {
          resultText.innerText = "Server Error";
          speakOut("Server connection error.", "en-US");
          console.error("Upload error", err);
          retakeBtn.style.display = 'block';
        }
      });
    }, "image/jpeg", 0.7);
  });

  function speakOut(text, languageCode) {
    if(!text) return;
    let utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = languageCode;
    utterance.rate = 0.9;
    
    const voices = window.speechSynthesis.getVoices();
    if(languageCode.startsWith('ta')) {
       const tamilVoice = voices.find(v => v.lang.includes('ta'));
       if(tamilVoice) utterance.voice = tamilVoice;
    } else {
       const engVoice = voices.find(v => v.lang === 'en-US' || v.lang === 'en-GB');
       if(engVoice) utterance.voice = engVoice;
    }
    window.speechSynthesis.speak(utterance);
  }
};