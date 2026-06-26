document.addEventListener("DOMContentLoaded", () => {

    const btnWebcam = document.getElementById("btn-webcam");
    const btnImport = document.getElementById("btn-import");

    const videoInput = document.getElementById("video-input");
    const imageInput = document.getElementById("image-input");

    const videoFeed = document.getElementById("video-feed");

    btnWebcam.addEventListener("click", async () => {

        try {

            const response = await fetch("/start_webcam");

            const data = await response.json();

            if (data.success) {

                // força atualizar o stream
                videoFeed.src = "/video_feed?" + new Date().getTime();

            } else {

                alert(data.message);

            }

        } catch (error) {

            console.error(error);

            alert("Erro ao iniciar a webcam.");

        }

    });

    btnImport.addEventListener("click", () => {

        videoInput.click();

    });

    videoInput.addEventListener("change", async () => {

        if (videoInput.files.length === 0)
            return;

        const formData = new FormData();

        formData.append("video", videoInput.files[0]);

        try {

            const response = await fetch("/upload_video", {

                method: "POST",

                body: formData

            });

            const data = await response.json();

            if (data.success) {

                videoFeed.src = "/video_feed?" + new Date().getTime();

            } else {

                alert(data.message);

            }

        } catch (error) {

            console.error(error);

            alert("Erro ao enviar o vídeo.");

        }

    });

    if (imageInput) {

        imageInput.addEventListener("change", async () => {

            if (imageInput.files.length === 0)
                return;

            const formData = new FormData();

            formData.append("image", imageInput.files[0]);

            try {

                const response = await fetch("/upload_image", {

                    method: "POST",

                    body: formData

                });

                const data = await response.json();

                if (data.success) {

                    alert("Imagem enviada com sucesso.");

                } else {

                    alert(data.message);

                }

            } catch (error) {

                console.error(error);

                alert("Erro ao enviar imagem.");

            }

        });

    }

});