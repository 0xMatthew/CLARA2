document.getElementById('upload-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    const fileInput = document.getElementById('file-input');
    const file = fileInput.files[0];
    const slidesContainer = document.getElementById('slides-container');

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
            if (result.error) {
                throw new Error(result.error);
            }

            // clear any existing slides
            slidesContainer.innerHTML = '';

            // display the slide images
            const imageFolder = result.image_folder.split('/').pop(); // get the hash folder name
            const numberOfSlides = result.slides.length;  // assuming result contains the number of slides

            for (let i = 0; i < numberOfSlides; i++) {
                const img = document.createElement('img');
                const imgUrl = `/images/${imageFolder}/slide_${i}.png`;
                console.log(`fetching image from: ${imgUrl}`);
                img.src = imgUrl;
                img.alt = `slide ${i + 1}`;
                img.className = 'slide';
                slidesContainer.appendChild(img);
            }
            
        } catch (error) {
            console.error('error during upload:', error);
            alert(`error during upload: ${error.message}`);
        }
    } else {
        alert('please select a PowerPoint file to upload.');
    }
});
