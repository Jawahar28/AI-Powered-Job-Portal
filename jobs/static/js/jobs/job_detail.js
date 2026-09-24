console.log("JOBCode Cover Letter JS Loaded");

document.addEventListener("DOMContentLoaded", function () {

    const generateButton =
        document.getElementById("generateCoverLetterBtn");

    const modal =
        document.getElementById("coverLetterModal");

    const closeButton =
        document.getElementById("closeCoverLetter");

    const loading =
        document.getElementById("coverLetterLoading");

    const error =
        document.getElementById("coverLetterError");

    const coverLetterText =
        document.getElementById("coverLetterText");

    const copyButton =
        document.getElementById("copyCoverLetter");

    const regenerateButton =
        document.getElementById("regenerateCoverLetter");


    if (!generateButton) {
        return;
    }


    function getCookie(name) {

        const cookies = document.cookie.split(";");

        for (let cookie of cookies) {

            cookie = cookie.trim();

            if (cookie.startsWith(name + "=")) {

                return decodeURIComponent(
                    cookie.substring(name.length + 1)
                );

            }
        }

        return null;
    }


    async function generateCoverLetter() {

        modal.classList.add("active");

        loading.style.display = "flex";
        error.style.display = "none";
        coverLetterText.style.display = "none";

        generateButton.disabled = true;
        regenerateButton.disabled = true;


        try {

            const response = await fetch(
                generateButton.dataset.url,
                {
                    method: "POST",

                    headers: {
                        "X-CSRFToken": getCookie("csrftoken"),
                        "Content-Type": "application/json"
                    }
                }
            );


            const data = await response.json();


            if (!response.ok || !data.success) {

                if (response.status === 429) {

                    error.textContent =
                        data.error ||
                        "You have reached your daily cover letter generation limit.";

                } else {

                    error.textContent =
                        data.error ||
                        "Unable to generate the cover letter right now.";

                }

                throw new Error(
                    data.error || "Generation failed"
                );
            }


            coverLetterText.value =
                data.cover_letter;

            loading.style.display = "none";

            coverLetterText.style.display = "block";


        } catch (err) {

            console.error(err);

            loading.style.display = "none";

            error.style.display = "block";

        } finally {

            generateButton.disabled = false;
            regenerateButton.disabled = false;

        }

    }


    generateButton.addEventListener(
        "click",
        generateCoverLetter
    );


    regenerateButton.addEventListener(
        "click",
        generateCoverLetter
    );


    closeButton.addEventListener(
        "click",
        function () {

            modal.classList.remove("active");

        }
    );


    modal.addEventListener(
        "click",
        function (event) {

            if (event.target === modal) {

                modal.classList.remove("active");

            }

        }
    );


    copyButton.addEventListener(
        "click",
        async function () {

            try {

                await navigator.clipboard.writeText(
                    coverLetterText.value
                );


                copyButton.innerHTML =
                    '<i class="fa-solid fa-check"></i> Copied!';


                setTimeout(
                    function () {

                        copyButton.innerHTML =
                            '<i class="fa-solid fa-copy"></i> Copy';

                    },
                    2000
                );


            } catch (err) {

                console.error(err);

            }

        }
    );

});