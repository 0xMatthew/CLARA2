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
                throw new Error('network response was not ok');
            }

            const result = await response.json();
        } catch (error) {
            console.error('error during upload:', error);
            alert(`error during upload: ${error.message}`);
        }
    } else {
        alert('please select a PowerPoint file to upload.');
    }
});

document.getElementById('stop-button').addEventListener('click', async function() {
    try {
        const response = await fetch('/stop-audio2face', {
            method: 'POST'
        });

        if (!response.ok) {
            throw new Error('network response was not ok');
        }

        const result = await response.json();
        alert(result.message);
    } catch (error) {
        console.error('error stopping Audio2Face:', error);
        alert(`error stopping Audio2Face: ${error.message}`);
    }
});
