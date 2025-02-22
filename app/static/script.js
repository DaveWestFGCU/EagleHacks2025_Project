import Chart from 'chart.js/auto'
import marketingData from './marketing_data.json'

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

(async function() {
    const data = marketingData.data;
   
     // Group data by date and channel
     const channels = [...new Set(data.map(d => d.channel))]; // Get all unique channels
     const dates = [...new Set(data.map(d => d.date))]; // Get all unique dates
   
     // Create datasets by channel
     const datasets = channels.map(channel => {
       return {
         label: channel,
         data: dates.map(date => {
           const entry = data.find(d => d.date === date && d.channel === channel);
           return entry ? entry.impressions : 0; // Default to 0 if no data
         }),
         backgroundColor: getColorForChannel(channel), // Optional: Add custom colors for each channel
       };
     });
   
     // Function to get a color based on the channel (can be customized)
     function getColorForChannel(channel) {
       const colors = {
         Facebook: 'rgba(59, 89, 152, 0.6)',
         Instagram: 'rgba(225, 48, 108, 0.6)',
         'Google Ads': 'rgba(34, 153, 84, 0.6)',
         'Email Campaign': 'rgba(255, 165, 0, 0.6)',
         Twitter: 'rgba(29, 161, 242, 0.6)',
       };
       return colors[channel] || 'rgba(0, 0, 0, 0.6)'; // Default color if not found
     }
   
     new Chart(document.getElementById('graph1'), {
       type: 'bar',
       data: {
         labels: dates, // X-axis labels (dates)
         datasets: datasets // Your datasets for each channel
       },
       options: {
         responsive: true,
         scales: {
           x: {
             // Label for x-axis (dates)
             title: {
               display: true,
               text: 'Dates', // X-axis label
               font: {
                 size: 14, // Optional: adjust font size
                 weight: 'bold' // Optional: adjust font weight
               }
             }
           },
           y: {
             // Label for y-axis (impressions)
             title: {
               display: true,
               text: 'Impressions', // Y-axis label
               font: {
                 size: 14, // Optional: adjust font size
                 weight: 'bold' // Optional: adjust font weight
               }
             },
             beginAtZero: true
           }
         },
         plugins: {
           legend: {
             position: 'top',
           },
           tooltip: {
             mode: 'index',
             intersect: false,
           }
         }
       }
     });
})();