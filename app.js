const firebaseConfig = {
    apiKey: "AIzaSyDVrtcjXf83lLCt_VEdQ8NSksUqlbdxMiM",
    authDomain: "ratertara-rfgd.firebaseapp.com",
    databaseURL: "https://ratertara-rfgd-default-rtdb.firebaseio.com",
    projectId: "ratertara-rfgd",
    storageBucket: "ratertara-rfgd.firebasestorage.app",
    messagingSenderId: "624181865811",
    appId: "1:624181865811:web:63bf66817817e3628505a6"
};

firebase.initializeApp(firebaseConfig);
const db = firebase.firestore();

// ১. ভিডিও পাবলিশ করার ফাংশন (লিঙ্ক অটো-ডিটেকশন সহ)
async function publishVideo() {
    const title = document.getElementById('vTitle').value;
    const source = document.getElementById('vSource').value;
    const link = document.getElementById('vLink').value;

    if (!title || !link) return alert("দয়া করে সব তথ্য দিন!");

    let finalEmbedUrl = "";

    try {
        if (source === "youtube") {
            let videoId = "";
            // youtube.com/watch?v=... এবং youtu.be/... উভয় লিঙ্কই কাজ করবে
            if (link.includes("v=")) {
                videoId = link.split('v=')[1].split('&')[0];
            } else if (link.includes("youtu.be/")) {
                videoId = link.split('youtu.be/')[1].split('?')[0];
            } else {
                videoId = link.split('/').pop().split('?')[0];
            }
            finalEmbedUrl = `https://www.youtube.com/embed/${videoId}`;
        } else if (source === "drive") {
            let driveId = link.split('/d/')[1].split('/')[0];
            finalEmbedUrl = `https://drive.google.com/file/d/${driveId}/preview`;
        }

        await db.collection("videos").add({
            title: title,
            source: source,
            url: finalEmbedUrl,
            timestamp: firebase.firestore.FieldValue.serverTimestamp()
        });

        alert("ভিডিও সফলভাবে পাবলিশ হয়েছে!");
        showSection('home-section');
    } catch (e) {
        alert("লিঙ্কটি সঠিক নয়! আবার চেষ্টা করুন।");
    }
}

// ২. ভিডিও লোড করা
function loadVideos() {
    db.collection("videos").orderBy("timestamp", "desc").onSnapshot(snap => {
        const grid = document.getElementById('videoGrid');
        const list = document.getElementById('adminVideoList');
        grid.innerHTML = "";
        list.innerHTML = "";

        snap.forEach(doc => {
            const v = doc.data();
            // হোম গ্রিডের জন্য
            grid.innerHTML += `
                <div class="v-card">
                    <div class="player-container">
                        <iframe src="${v.url}" allowfullscreen></iframe>
                    </div>
                    <div class="v-info">
                        <h4>${v.title}</h4>
                        <div class="v-actions">
                            <span><i class="fas fa-heart"></i> Like</span>
                            <span onclick="shareVideo('${v.url}')"><i class="fas fa-share"></i> Share</span>
                        </div>
                    </div>
                </div>
            `;
            // প্রোফাইল ড্যাশবোর্ডে ডিলিট অপশন
            list.innerHTML += `
                <div style="background: #222; padding: 10px; margin-bottom: 5px; border-radius: 8px; display: flex; justify-content: space-between;">
                    <span>${v.title}</span>
                    <i class="fas fa-trash" style="color: red; cursor: pointer;" onclick="deleteVideo('${doc.id}')"></i>
                </div>
            `;
        });
    });
}

function showSection(id) {
    document.querySelectorAll('.content-section').forEach(s => s.style.display = 'none');
    document.getElementById(id).style.display = 'block';
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
}

async function deleteVideo(id) {
    if(confirm("ভিডিওটি ডিলিট করতে চান?")) {
        await db.collection("videos").doc(id).delete();
    }
}

function shareVideo(url) {
    if (navigator.share) {
        navigator.share({ title: 'Rater Tara Video', url: url });
    } else {
        alert("Link: " + url);
    }
}

window.onload = loadVideos;
