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
            ad.image = "app/static/concept_0.png"
            const adElement = document.createElement("div");
            adElement.classList.add("ad-box");
            adElement.innerHTML = `
                <img src=${ad.image} alt="${ad.title}" width="500" height="500">
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
  
  let submitButton = this.querySelector('button');
  submitButton.disabled = true;
  submitButton.innerHTML = 'Processing... <span class="loader"></span>'; // Add a spinner

  let formData = new FormData(this);

  let response = await fetch('/new_job', {
      method: 'POST',
      body: formData
  });

  let result = await response.json();

  if (result.error) {
      document.getElementById('ad-results').innerHTML = `<p style="color: red;">${result.error}</p>`;
      submitButton.disabled = false;
      submitButton.innerHTML = 'Submit';
  } else {
      checkStatus(result.job_id, submitButton);
  }
});

async function checkStatus(taskId, submitButton) {
  const interval = setInterval(async () => {
      let response = await fetch(`/check_status?task_id=${taskId}`);  // Update to query Flask, which queries FastAPI
      let result = await response.json();

      if (result.status === 'done') {
          clearInterval(interval);
          displayAds(result);  // Assuming result contains all the ad data
          submitButton.disabled = false;
          submitButton.innerHTML = 'Submit';
      } else if (result.message === 'Job is still in progress') {
          console.log('Job is still processing...');
      } else {
          clearInterval(interval);
          document.getElementById('ad-results').innerHTML = `<p style="color: red;">Error: ${result.error || "Unknown issue"}</p>`;
          submitButton.disabled = false;
          submitButton.innerHTML = 'Submit';
      }
  }, 3000);
}

function displayAds(result) {
  let adResults = document.getElementById('ad-results');
  adResults.innerHTML = `<h3>Generated Ad(s):</h3>`;

  // Iterate through the object keys
  for (let key in result) {
      if (!isNaN(key)) {  // Check if the key is a number (image index)
          let imgPath = result[key];
          adResults.innerHTML += `
              <div style="display: inline-block; margin: 10px;">
                  <img src="${imgPath}" alt="Generated Ad ${key}" style="max-width: 300px; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.2);">
              </div>
          `;
      }
  }
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