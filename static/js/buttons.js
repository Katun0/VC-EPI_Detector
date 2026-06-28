document.addEventListener("DOMContentLoaded", () => {

    const btnWebcam = document.getElementById("btn-webcam");
    const btnImport = document.getElementById("btn-import");
    const btnImportImage = document.getElementById("btn-import-image");
    const btnProcessing = document.getElementById("btn-processing");
    const btnReset = document.getElementById("btn-reset");

    const videoInput = document.getElementById("video-input");
    const imageInput = document.getElementById("image-input");

    const videoFeed = document.getElementById("video-feed");
    const placeholder = document.getElementById("video-placeholder");

    const resultPanel = document.getElementById("result-panel");
    const resultTitle = document.getElementById("result-title");
    const resultImage = document.getElementById("result-image");
    const complianceList = document.getElementById("compliance-list");

    // ------------------------------------------------------------------ //
    // Stream de vídeo
    // ------------------------------------------------------------------ //
    function showStream() {
        videoFeed.src = "/video_feed?" + new Date().getTime();
        placeholder.style.display = "none";
        resultPanel.hidden = true;
    }

    btnWebcam.addEventListener("click", async () => {
        try {
            const data = await (await fetch("/start_webcam")).json();
            if (data.success) showStream();
            else alert(data.message);
        } catch (e) {
            console.error(e);
            alert("Erro ao iniciar a webcam.");
        }
    });

    btnImport.addEventListener("click", () => videoInput.click());
    btnImportImage.addEventListener("click", () => imageInput.click());

    videoInput.addEventListener("change", async () => {
        if (videoInput.files.length === 0) return;

        const formData = new FormData();
        formData.append("video", videoInput.files[0]);

        try {
            const data = await (await fetch("/upload_video", {
                method: "POST", body: formData
            })).json();
            if (data.success) showStream();
            else alert(data.message);
        } catch (e) {
            console.error(e);
            alert("Erro ao enviar o vídeo.");
        }
    });

    // ------------------------------------------------------------------ //
    // Upload de imagem (roda detecção + conformidade)
    // ------------------------------------------------------------------ //
    imageInput.addEventListener("change", async () => {
        if (imageInput.files.length === 0) return;

        const formData = new FormData();
        formData.append("image", imageInput.files[0]);

        try {
            const data = await (await fetch("/upload_image", {
                method: "POST", body: formData
            })).json();

            if (!data.success) {
                alert(data.message);
                return;
            }

            // pausa o stream e mostra o resultado
            videoFeed.src = "";
            placeholder.style.display = "none";

            resultTitle.textContent =
                `Resultado da imagem (inferência ${data.inference_ms} ms)`;
            resultImage.src = data.annotated_url + "?" + new Date().getTime();
            renderCompliance(data.compliance);
            resultPanel.hidden = false;
        } catch (e) {
            console.error(e);
            alert("Erro ao enviar imagem.");
        }
    });

    function renderCompliance(compliance) {
        complianceList.innerHTML = "";
        if (!compliance || compliance.people === 0) {
            complianceList.innerHTML =
                "<p class='muted'>Nenhuma pessoa detectada.</p>";
            return;
        }

        compliance.persons.forEach((p, i) => {
            const ok = p.status === "Conforme";
            const card = document.createElement("div");
            card.className = "comp-card " + (ok ? "ok" : "bad");
            const present = p.present.length ? p.present.join(", ") : "—";
            const missing = p.missing.length ? p.missing.join(", ") : "—";
            card.innerHTML =
                `<strong>Pessoa ${i + 1}</strong> — ${p.status}` +
                `<div class="comp-detail">✓ Presentes: ${present}</div>` +
                `<div class="comp-detail">✗ Faltando: ${missing}</div>`;
            complianceList.appendChild(card);
        });
    }

    // ------------------------------------------------------------------ //
    // Processamento de imagem (mosaico)
    // ------------------------------------------------------------------ //
    btnProcessing.addEventListener("click", () => {
        videoFeed.src = "";
        placeholder.style.display = "none";
        resultTitle.textContent = "Etapas de processamento de imagem";
        resultImage.src = "/processing_demo?" + new Date().getTime();
        complianceList.innerHTML = "";
        resultPanel.hidden = false;
    });

    // ------------------------------------------------------------------ //
    // Reset de métricas
    // ------------------------------------------------------------------ //
    btnReset.addEventListener("click", async () => {
        await fetch("/reset_metrics");
    });

    // ------------------------------------------------------------------ //
    // Gráfico ao vivo + polling de métricas
    // ------------------------------------------------------------------ //
    const ctx = document.getElementById("chart-classes").getContext("2d");
    const chart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: [],
            datasets: [{
                label: "Detecções por classe",
                data: [],
                backgroundColor: "#38bdf8",
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { labels: { color: "#f8fafc" } } },
            scales: {
                x: { ticks: { color: "#94a3b8" }, grid: { color: "#334155" } },
                y: { ticks: { color: "#94a3b8" }, grid: { color: "#334155" },
                     beginAtZero: true },
            },
        },
    });

    function setText(id, value) {
        document.getElementById(id).textContent = value;
    }

    async function pollMetrics() {
        try {
            const m = await (await fetch("/metrics")).json();
            setText("m-fps", m.fps);
            setText("m-inf", m.inference_ms);
            setText("m-people", m.people);
            setText("m-ok", m.compliant);
            setText("m-alerts", m.alerts);

            chart.data.labels = Object.keys(m.class_counts);
            chart.data.datasets[0].data = Object.values(m.class_counts);
            chart.update("none");
        } catch (e) {
            // silencioso: servidor pode estar sem stream ativo
        }
    }

    setInterval(pollMetrics, 1000);
    pollMetrics();
});
