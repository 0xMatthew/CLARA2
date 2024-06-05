document.getElementById('upload-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    const fileInput = document.getElementById('file-input');
    const file = fileInput.files[0];

    if (file) {
        const formData = new FormData();
        formData.append('presentation', file);

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData,
            });
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const result = await response.json();
            alert(`presentation audio successfully generated. check the outputs.`);
        } catch (error) {
            console.error('error during upload:', error);
            alert(`error during upload: ${error.message}`);
        }
    } else {
        alert('please select a PowerPoint file to upload.');
    }
});
