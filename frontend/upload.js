document.getElementById('upload-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const fileInput = document.getElementById('file-input');
    const file = fileInput.files[0];

    if (file) {
        uploadConnectBackend(file);
    } else {
        alert('please select a PowerPoint file to upload.');
    }
});

function uploadConnectBackend(file) {
    const formData = new FormData();
    formData.append('presentation', file);

    fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => alert('upload successful: ' + data.message))
    .catch(error => alert('error during upload: ' + error));
}
