import Chart from 'chart.js/auto'
import marketingData from './marketing_data.json'


document.addEventListener("DOMContentLoaded", function() {
    try {
        console.log("Received adData:", adData);

        if (!adData || !Array.isArray(adData)) {
            console.error("Invalid data format:", adData);
            return;
        }

        const adContainer = document.getElementById("ad-results");
        adContainer.innerHTML = "";

        adData.forEach(ad => { 
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

//accessibility buttons
document.addEventListener("DOMContentLoaded", function () {
  console.log("DOM fully loaded");

  // Fix: Ensure the buttons exist before attaching event listeners
  const toggleFontButton = document.getElementById("toggle-font");
  const toggleContrastButton = document.getElementById("toggle-contrast");

  if (toggleFontButton) {
      toggleFontButton.addEventListener("click", function () {
          document.body.classList.toggle("large-font");
      });
  }

  if (toggleContrastButton) {
      toggleContrastButton.addEventListener("click", function () {
          document.body.classList.toggle("high-contrast");
      });
  }
});




document.getElementById('adForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    let formData = new FormData(this);

    let response = await fetch('/ad_generation', {
        method: 'POST',
        body: formData
    });

    let result = await response.json(); 

    if (result.error) {
        document.getElementById('ad-results').innerHTML = `<p style="color: red;">${result.error}</p>`;
    } else {
        displayAds(result.generated_ad);
    }
});


function displayAds(adData) {
    let container = document.getElementById('ad-results');
    container.innerHTML = ''; 

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
   
     const channels = [...new Set(data.map(d => d.channel))]; 
     const dates = [...new Set(data.map(d => d.date))]; 
   
     const datasets = channels.map(channel => {
       return {
         label: channel,
         data: dates.map(date => {
           const entry = data.find(d => d.date === date && d.channel === channel);
           return entry ? entry.impressions : 0; 
         }),
         backgroundColor: getColorForChannel(channel), 
       };
     });
   
     function getColorForChannel(channel) {
       const colors = {
         Facebook: 'rgba(59, 89, 152, 0.6)',
         Instagram: 'rgba(225, 48, 108, 0.6)',
         'Google Ads': 'rgba(34, 153, 84, 0.6)',
         'Email Campaign': 'rgba(255, 165, 0, 0.6)',
         Twitter: 'rgba(29, 161, 242, 0.6)',
       };
       return colors[channel] || 'rgba(0, 0, 0, 0.6)'; 
     }
   
     new Chart(document.getElementById('graph1'), {
       type: 'bar',
       data: {
         labels: dates,
         datasets: datasets 
       },
       options: {
         responsive: true,
         scales: {
           x: {
             title: {
               display: true,
               text: 'Dates',
               font: {
                 size: 14, 
                 weight: 'bold'
               }
             }
           },
           y: {
             title: {
               display: true,
               text: 'Impressions', 
               font: {
                 size: 14,
                 weight: 'bold' 
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