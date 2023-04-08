document.getElementById("image-upload-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    try {
        const response = await fetch("{{ url_for('upload_image') }}", {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const image = await response.json();

        alert("Image uploaded successfully");
    } catch (error) {
        console.error("Error uploading the image:", error);
        // Show an alert to indicate an error during the upload
        alert("Error uploading the image");
    }
});