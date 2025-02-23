

document.addEventListener("DOMContentLoaded", function() {
  try {
      console.log("Received adData:", adData);

      if (!adData || !Array.isArray(adData)) {
          console.error("Invalid data format:", adData);
          return;
      }

      const adContainer = document.getElementById("ad-results");
      adContainer.innerHTML = "";
      adContainer.classList.add("ad-grid"); 

      adData.forEach(ad => { 
          const adElement = document.createElement("div");
          adElement.classList.add("ad-box");
          ad.image = '/home/wcward/Documents/EagleHacks2025_Project/app/static/concept_0'
          adElement.innerHTML = `
              <div class="ad-title">${ad.title}</div>
              <img src="${ad.image}" alt="${ad.title}" class="ad-image">
          `;

          adContainer.appendChild(adElement);
      });

  } catch (error) {
      console.error("Error parsing ad data:", error);
  }
});




document.addEventListener("DOMContentLoaded", function () {
  console.log("DOM fully loaded");

  const toggleFontButton = document.getElementById("toggle-font");
  const toggleContrastButton = document.getElementById("toggle-contrast");

  if (toggleFontButton) {
      toggleFontButton.addEventListener("click", function () {
          document.body.classList.toggle("large-font");

          if (document.body.classList.contains("large-font")) {
              localStorage.setItem("largeFont", "enabled");
          } else {
              localStorage.removeItem("largeFont");
          }
      });

      if (localStorage.getItem("largeFont") === "enabled") {
          document.body.classList.add("large-font");
      }
  }

  if (toggleContrastButton) {
      toggleContrastButton.addEventListener("click", function () {
          document.body.classList.toggle("high-contrast");

          if (document.body.classList.contains("high-contrast")) {
              localStorage.setItem("highContrast", "enabled");
          } else {
              localStorage.removeItem("highContrast");
          }
      });

      if (localStorage.getItem("highContrast") === "enabled") {
          document.body.classList.add("high-contrast");
      }
  }
});




document.getElementById('adForm').addEventListener('submit', async function(event) {
  event.preventDefault();
  
  let submitButton = this.querySelector('button');
  submitButton.disabled = true;
  submitButton.innerHTML = 'Processing... <span class="loader"></span>'; 

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
      let response = await fetch(`/check_status?task_id=${taskId}`);  
      let result = await response.json();

      if (result.status === 'done') {
          clearInterval(interval);
          displayAds(result, taskId);  
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

function displayAds(result, taskId) {
  let adResults = document.getElementById('ad-results');
  adResults.innerHTML = `<h3>Generated Ad(s):</h3>`;
  
  console.log(result)

  for (let key in result) {
      if (!isNaN(key)) {  
          let imgPath = result[key];
          adResults.innerHTML += `
              <div style="display: inline-block; margin: 10px;">
                  <img src="${imgPath}" alt="Generated Ad ${key}" style="max-width: 300px; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.2);">
              </div>
          `;
      }
  }
}
