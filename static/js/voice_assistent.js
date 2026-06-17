document.addEventListener("DOMContentLoaded", function () {
    const voiceBtn = document.getElementById("voice-toggle-btn");
    const voiceBtnText = document.getElementById("voice-btn-text");
    const voiceBubble = document.getElementById("voice-speech-output");
    const voiceGlow = document.getElementById("voice-status-glow");

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const SpeechSynthesis = window.speechSynthesis;

    if (!SpeechRecognition) {
        if (voiceBtn) voiceBtn.style.backgroundColor = "#475569";
        if (voiceBubble) voiceBubble.textContent = "Error: Web Speech API unsupported. Use Google Chrome.";
        return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognition.lang = 'en-US';

    let isListening = false;

    function speakSystemResponse(text) {
        if (!SpeechSynthesis) return;
        SpeechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        SpeechSynthesis.speak(utterance);
    }

    function updateUIListeningState(listening) {
        isListening = listening;
        if (listening) {
            voiceBtnText.textContent = "Listening...";
            voiceGlow.classList.add("listening");
            voiceBubble.textContent = "Listening closely... Speak now.";
        } else {
            voiceBtnText.textContent = "Start Voice Assistant";
            voiceGlow.classList.remove("listening");
        }
    }

    voiceBtn.addEventListener("click", (e) => {
        e.preventDefault();
        if (!isListening) {
            try {
                // Audio Context Wakeup Rule for Modern Browsers
                if (window.AudioContext || window.webkitAudioContext) {
                    const ctx = new (window.AudioContext || window.webkitAudioContext)();
                    if (ctx.state === 'suspended') ctx.resume();
                }
                recognition.start();
            } catch (err) {
                console.error("Recognition execution failure:", err);
                voiceBubble.textContent = `Engine Error: ${err.message}`;
            }
        } else {
            recognition.stop();
        }
    });

    recognition.onstart = () => updateUIListeningState(true);
    recognition.onend = () => updateUIListeningState(false);
    
    // Catch-All Error Diagnostics
    recognition.onerror = function (event) {
        updateUIListeningState(false);
        console.error("Speech Error Logged:", event.error);
        if (event.error === 'not-allowed') {
            voiceBubble.textContent = "Mic Blocked! Change settings to allow access.";
            alert("Microphone permission denied. Please click the mic/lock icon in your address bar and allow access.");
        } else if (event.error === 'no-speech') {
            voiceBubble.textContent = "No speech detected. Try again.";
        } else {
            voiceBubble.textContent = `Error matched: ${event.error}`;
        }
    };

    recognition.onresult = function (event) {
        const command = event.results[0][0].transcript.toLowerCase().trim();
        voiceBubble.textContent = `Processing: "${command}"`;
        
        // --- ROUTING ENGINE ---
        if (command.includes("open jobs") || command.includes("go to jobs") || command.includes("show jobs")) {
            speakSystemResponse("Navigating to Job Postings.");
            setTimeout(() => window.location.href = "/jobs", 600);
            return;
        }
        if (command.includes("open candidates") || command.includes("go to candidates") || command.includes("show candidates")) {
            speakSystemResponse("Opening Candidates Matrix.");
            setTimeout(() => window.location.href = "/candidates", 600);
            return;
        }
        if (command.includes("open dashboard") || command.includes("go to dashboard") || command.includes("show dashboard")) {
            speakSystemResponse("Returning to Dashboard.");
            setTimeout(() => window.location.href = "/dashboard", 600);
            return;
        }
        if (command.includes("open reports") || command.includes("go to reports") || command.includes("show analytics")) {
            speakSystemResponse("Opening Analytics Reports.");
            setTimeout(() => window.location.href = "/reports", 600);
            return;
        }
        if (command.includes("download report") || command.includes("export data")) {
            speakSystemResponse("Downloading spreadsheet export.");
            setTimeout(() => window.location.href = "/reports/export", 600);
            return;
        }

        // --- DATA QUERIES ---
        if (command.includes("statistics") || command.includes("stats")) {
            fetch('/api/voice/stats')
                .then(res => res.json())
                .then(data => {
                    const speech = `System metrics: Total profiles processed is ${data.total}. Total qualified pipelines is ${data.hires}. Peak match index stands at ${data.top_score} percent.`;
                    voiceBubble.textContent = speech;
                    speakSystemResponse(speech);
                });
            return;
        }

        if (command.includes("top candidate") || command.includes("who is leading")) {
            fetch('/api/voice/top-candidate')
                .then(res => res.json())
                .then(data => {
                    let speech = "No applicant data processed inside database yet.";
                    if (data.name !== "None") {
                        speech = `The current leading profile is ${data.name} with an engineering match score of ${data.score} percent.`;
                    }
                    voiceBubble.textContent = speech;
                    speakSystemResponse(speech);
                });
            return;
        }

        if (command.includes("score for") || command.includes("status of")) {
            const match = command.match(/(?:score for|status of)\s+([a-z\s0-9]+)/);
            if (match && match[1]) {
                const targetName = match[1].trim();
                fetch(`/api/voice/candidate/${encodeURIComponent(targetName)}`)
                    .then(res => res.json())
                    .then(data => {
                        let speech = `Could not locate system entries for ${targetName}.`;
                        if (data.found) {
                            speech = `Candidate ${data.name} registers a match score of ${data.score} percent. Dynamic status is marked as ${data.rec}.`;
                        }
                        voiceBubble.textContent = speech;
                        speakSystemResponse(speech);
                    });
            } else {
                speakSystemResponse("Could not parse requested candidate search parameters.");
            }
            return;
        }

        // --- CLIENT SIDE FILTERING (DASHBOARD AND CANDIDATES VIEWS) ---
        if (command.includes("filter") || command.includes("show only")) {
            let keyword = "";
            if (command.includes("filter")) keyword = command.split("filter")[1].trim();
            else if (command.includes("show only")) keyword = command.split("show only")[1].trim();
            
            if (keyword.endsWith("s")) keyword = keyword.slice(0, -1); 

            const rows = document.querySelectorAll(".ats-table tbody tr");
            let visibleCount = 0;

            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                if (text.includes(keyword)) {
                    row.style.display = "";
                    visibleCount++;
                } else {
                    row.style.display = "none";
                }
            });

            const speech = `Isolating matrix rows targeting keyword ${keyword}. Matches display count is ${visibleCount}.`;
            voiceBubble.textContent = speech;
            speakSystemResponse(speech);
            return;
        }

        speakSystemResponse("Command processed but no matching execution vector found.");
    };
});