let isScanning = false;
let scanningInterval;
let lastSpokenText = "";

window.onload = () => {
  const startButton = document.getElementById('start-button');
  const scannerUI = document.getElementById('scanner-ui');
  const video = document.getElementById('camera-feed');
  const canvas = document.getElementById('camera-canvas');
  const statusText = document.getElementById('status-text');

  // Pre-fetch voices to prevent delay
  speechSynthesis.getVoices();

  startButton.addEventListener('click', async () => {
    // Hide start button and show camera interface
    startButton.style.display = 'none';
    scannerUI.style.display = 'block';

    // Must trigger speech strictly inside the user gesture to unlock AudioContext
    let dummyUtterance = new SpeechSynthesisUtterance("");
    dummyUtterance.volume = 0; // mute
    window.speechSynthesis.speak(dummyUtterance);

    // Give instructions in Voice
    speakOut("Camera activated. Please scan currency.", "en-US");
    speakOut("கேமரா தொடங்கப்பட்டது. தயவுசெய்து பணத்தை காண்பிக்கவும்.", "ta-IN");

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: "environment" // Always try to use the back camera
        }
      });
      video.srcObject = stream;
      
      video.onloadedmetadata = () => {
        video.play();
        isScanning = true;
        // Start capture loop every 5 seconds (to avoid freezing the free server)
        scanningInterval = setInterval(captureAndSend, 5000);
      };
    } catch (err) {
      statusText.innerText = "Camera Access Denied";
      speakOut("Error accessing camera. Please check permissions.", "en-US");
    }
  });

  function captureAndSend() {
    if (!isScanning || !video.videoWidth) return;
    
    // Set canvas dimensions exactly to video dimensions
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Obtain JPEG blob from canvas
    canvas.toBlob((blob) => {
      let formData = new FormData();
      formData.append('image', blob, 'capture.jpg');
      
      statusText.innerText = "Scanning...";

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
          
          if (englishMsg && 
              englishMsg.toLowerCase().indexOf("try with another better image") === -1 && 
              englishMsg.toLowerCase() !== "image contains") {
              
              const cleanMsg = englishMsg.replace(/Image contains/gi, '').trim();

              // Avoid spamming the user by speaking the same result continuously
              if (lastSpokenText !== englishMsg) {
                 statusText.innerText = cleanMsg;
                 
                 // Speak Tamil first, then English
                 speakOut(tamilMsg, "ta-IN");
                 speakOut(cleanMsg, "en-US");
                 
                 lastSpokenText = englishMsg;
                 
                 // Clear internal memory of last spoken after 10 seconds 
                 // just in case they hold the same note for a long time intentionally
                 setTimeout(() => { 
                   if(lastSpokenText === englishMsg) lastSpokenText = ""; 
                 }, 10000);
              }
          } else {
             statusText.innerText = "Scanning...";
          }
        },
        error: function(err) {
          console.error("Transmission error", err);
        }
      });
    }, "image/jpeg", 0.6); // 0.6 quality keeps the upload payload small for snappy response
  }

  function speakOut(text, languageCode) {
    if(!text) return;
    
    let utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = languageCode;
    utterance.rate = 0.9;
    
    const voices = window.speechSynthesis.getVoices();
    // Attempt to pick a high quality matching voice
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