document.addEventListener("DOMContentLoaded", function() {
    try {
        console.log("Received adData:", adData); // Debugging step

        // Ensure adData is an object with an "ads" array
        if (!adData || !Array.isArray(adData)) {
            console.error("Invalid data format:", adData);
            return;
        }

        const adContainer = document.getElementById("ad-results");
        adContainer.innerHTML = ""; // Clear previous results

        adData.forEach(ad => {  // Directly iterate since adData is already an array
            const adElement = document.createElement("div");
            adElement.classList.add("ad-box");
            adElement.innerHTML = `
                <h3>${ad.title}</h3>
                <p>${ad.description}</p>
                <strong>${ad.key_message}</strong>
            `;
            adContainer.appendChild(adElement);
        });

    } catch (error) {
        console.error("Error parsing ad data:", error);
    }
});

document.getElementById('toggle-font').addEventListener('click', function() {
    document.body.classList.toggle('large-font');
});

document.getElementById('toggle-contrast').addEventListener('click', function() {
    document.body.classList.toggle('high-contrast');
});


document.getElementById('adForm').addEventListener('submit', async function(event) {
    event.preventDefault(); // Prevent default form submission

    let formData = new FormData(this);

    let response = await fetch('/ad_generation', {
        method: 'POST',
        body: formData
    });

    let result = await response.json(); // Parse JSON response

    if (result.error) {
        document.getElementById('ad-results').innerHTML = `<p style="color: red;">${result.error}</p>`;
    } else {
        displayAds(result.generated_ad);
    }
});


function displayAds(adData) {
    let container = document.getElementById('ad-results');
    container.innerHTML = ''; // Clear previous results

    let grid = document.createElement('div');
    grid.classList.add('ad-grid');

    adData.forEach(ad => {
        let adCard = document.createElement('div');
        adCard.classList.add('ad-card');

        adCard.innerHTML = `
            <h3>${ad.title}</h3>
            <p>${ad.description}</p>
            <strong>${ad.key_message}</strong>
        `;

        grid.appendChild(adCard);
    });

    container.appendChild(grid);
}