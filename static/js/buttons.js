document.addEventListener("DOMContentLoaded", () => {

  const btnImport = document.getElementById("btn-import");
  const btnImportImage = document.getElementById("btn-import-image");
  const btnProcessing = document.getElementById("btn-processing");
  const btnReset = document.getElementById("btn-reset");
  const btnBack = document.getElementById("btn-back");

  const videoInput = document.getElementById("video-input");
  const imageInput = document.getElementById("image-input");

  const videoFeed = document.getElementById("video-feed");
  const placeholder = document.getElementById("video-placeholder");

  const resultPanel = document.getElementById("result-panel");
  const resultTitle = document.getElementById("result-title");
  const resultImage = document.getElementById("result-image");
  const complianceList = document.getElementById("compliance-list");

  // Guarda a última detecção para poder voltar
  let lastDetectionImage = "";
  let lastInference = "";
  let lastCompliance = null;

  // ==========================================================
  // STREAM DE VÍDEO
  // ==========================================================
  function showStream() {
    videoFeed.src = "/video_feed?" + Date.now();
    placeholder.style.display = "none";
    resultPanel.hidden = true;
  }

  btnImport.addEventListener("click", () => videoInput.click());
  btnImportImage.addEventListener("click", () => imageInput.click());

  videoInput.addEventListener("change", async () => {

    if (videoInput.files.length === 0) return;

    const formData = new FormData();
    formData.append("video", videoInput.files[0]);

    try {

      const data = await (
        await fetch("/upload_video", {
          method: "POST",
          body: formData
        })
      ).json();

      if (data.success)
        showStream();
      else
        alert(data.message);

    } catch (e) {

      console.error(e);
      alert("Erro ao enviar vídeo.");

    }

  });

  // ==========================================================
  // IMPORTAÇÃO DE IMAGEM
  // ==========================================================
  imageInput.addEventListener("change", async () => {

    if (imageInput.files.length === 0) return;

    const formData = new FormData();
    formData.append("image", imageInput.files[0]);

    try {

      const data = await (
        await fetch("/upload_image", {
          method: "POST",
          body: formData
        })
      ).json();

      if (!data.success) {
        alert(data.message);
        return;
      }

      // Salva para poder voltar depois
      lastDetectionImage = data.annotated_url;
      lastInference = data.inference_ms;
      lastCompliance = data.compliance;

      videoFeed.src = "";
      placeholder.style.display = "none";

      resultTitle.textContent =
        `Resultado da imagem (inferência ${lastInference} ms)`;

      resultImage.src =
        lastDetectionImage + "?" + Date.now();

      renderCompliance(lastCompliance);

      resultPanel.hidden = false;

    } catch (e) {

      console.error(e);
      alert("Erro ao enviar imagem.");

    }

  });

  // ==========================================================
  // PROCESSAMENTO
  // ==========================================================
  btnProcessing.addEventListener("click", () => {

    resultTitle.textContent = "Etapas de processamento";

    resultImage.src =
      "/processing_demo?" + Date.now();

    complianceList.innerHTML = "";

    resultPanel.hidden = false;

  });

  // ==========================================================
  // VOLTAR PARA A DETECÇÃO
  // ==========================================================
  btnBack.addEventListener("click", () => {

    if (!lastDetectionImage) return;

    resultTitle.textContent =
      `Resultado da imagem (inferência ${lastInference} ms)`;

    resultImage.src =
      lastDetectionImage + "?" + Date.now();

    renderCompliance(lastCompliance);

  });

  // ==========================================================
  // RESET
  // ==========================================================
  btnReset.addEventListener("click", async () => {

    await fetch("/reset", {
      method: "POST"
    });

    videoFeed.src = "";
    resultImage.src = "";

    resultPanel.hidden = true;

    placeholder.style.display = "block";

    complianceList.innerHTML = "";

    imageInput.value = "";
    videoInput.value = "";

    lastDetectionImage = "";
    lastInference = "";
    lastCompliance = null;

    setText("m-fps", 0);
    setText("m-inf", 0);
    setText("m-people", 0);
    setText("m-ok", 0);
    setText("m-alerts", 0);

    chart.data.labels = [];
    chart.data.datasets[0].data = [];
    chart.update();

  });

  // ==========================================================
  // CONFORMIDADE
  // ==========================================================
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

      card.className =
        "comp-card " + (ok ? "ok" : "bad");

      const present =
        p.present.length ? p.present.join(", ") : "—";

      const missing =
        p.missing.length ? p.missing.join(", ") : "—";

      card.innerHTML =
        `<strong>Pessoa ${i + 1}</strong> — ${p.status}` +
        `<div class="comp-detail">✓ Presentes: ${present}</div>` +
        `<div class="comp-detail">✗ Faltando: ${missing}</div>`;

      complianceList.appendChild(card);

    });

  }

  // ==========================================================
  // CHART
  // ==========================================================
  const ctx =
    document.getElementById("chart-classes").getContext("2d");

  const chart = new Chart(ctx, {

    type: "bar",

    data: {

      labels: [],

      datasets: [{
        label: "Detecções por classe",
        data: [],
        backgroundColor: "#38bdf8"
      }]

    },

    options: {

      responsive: true,

      maintainAspectRatio: false,

      plugins: {

        legend: {

          labels: {

            color: "#f8fafc"

          }

        }

      },

      scales: {

        x: {

          ticks: { color: "#94a3b8" },

          grid: { color: "#334155" }

        },

        y: {

          beginAtZero: true,

          ticks: { color: "#94a3b8" },

          grid: { color: "#334155" }

        }

      }

    }

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

    } catch (e) {}

  }

  setInterval(pollMetrics, 1000);

  pollMetrics();

});