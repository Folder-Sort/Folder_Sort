import "./style.css";
document.addEventListener("DOMContentLoaded", () => {
  const uploadForm = document.getElementById("uploadForm");
  const zipFileInput = document.getElementById("zipFileInput");
  const uploadButton = document.getElementById("uploadButton");
  const statusMessage = document.getElementById("statusMessage");
  const dropArea = document.getElementById("drop-area");
  const selectFileButton = document.getElementById("selectFileButton");
  const initiateButton = document.getElementById("initiate");
  const originalDropAreaText = dropArea.innerHTML;

  const handleFileUpload = async (e) => {
    // Prevent the browser from submitting the form normally (which would reload the page)
    e.preventDefault();

    // Basic input validation
    if (zipFileInput.files.length === 0) {
      statusMessage.textContent = "Please select a ZIP file to upload.";
      return;
    }

    const file = zipFileInput.files[0];

    // Update UI state
    statusMessage.textContent =
      "Uploading and Sorting... Please wait. Do not navigate away.";
    statusMessage.style.color = "orange";

    // 2. Prepare the Data using FormData
    // FormData is essential for sending files via Fetch/XHR
    const formData = new FormData();
    formData.append("file", file); // 'file' MUST match the key Flask expects (request.files['file'])

    try {
      // 3. Send the Request to the Flask Endpoint
      const response = await fetch("http://127.0.0.1:5000/sort", {
        method: "POST",
        body: formData, // Send the FormData object
        // IMPORTANT: Do NOT set Content-Type header; Fetch does it automatically
        // for FormData, including the boundary required for multipart/form-data.
      });

      // 4. Handle the Response
      if (response.ok) {
        // Successful Response (Expected status 200)
        statusMessage.textContent = "Sorting complete! Initiating download...";
        statusMessage.style.color = "green";

        // Get the intended filename from the response headers (if set by Flask)
        const disposition = response.headers.get("Content-Disposition");
        let downloadFileName = "sorted_files.zip";
        if (disposition && disposition.indexOf("attachment") !== -1) {
          const matches = /filename="(.+?)"/g.exec(disposition);
          if (matches != null && matches[1]) {
            downloadFileName = matches[1];
          }
        }

        // 5. Trigger the Download
        // Fetch returns the file data as a Blob
        const blob = await response.blob();

        // Create a temporary link element to trigger the download
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.style.display = "none";
        a.href = url;
        a.download = downloadFileName; // Use the filename from the Flask response
        document.body.appendChild(a);
        a.click();

        // Clean up the temporary objects
        window.URL.revokeObjectURL(url);
        a.remove();

        statusMessage.textContent = `Success! Download of "${downloadFileName}" started.`;
      } else {
        // Handle Server Errors (e.g., 400, 413, 500)
        const errorText = await response.text();
        statusMessage.textContent = `Error (${response.status}): ${errorText}`;
        statusMessage.style.color = "red";
      }
    } catch (error) {
      // Handle Network Errors (e.g., connection lost)
      console.error("Network or Fetch Error:", error);
      statusMessage.textContent = `A network error occurred. Please try again.`;
      statusMessage.style.color = "red";
    } finally {
      // Reset UI state
      uploadButton.disabled = false;
    }
  };

  uploadForm.addEventListener("submit", async (e) => {
    initiateButton.disabled = true;
    const originalIntiateButtonHTML = initiateButton.innerHTML;
    initiateButton.innerHTML = `
      <span class="text-2xl!">Doing the Magic...</span>
    `;
    dropArea.innerHTML = `
      <div class="loader">
        <svg width="100" height="100" viewBox="0 0 100 100">
          <defs>
            <mask id="clipping">
              <polygon points="0,0 100,0 100,100 0,100" fill="black"></polygon>
              <polygon points="25,25 75,25 50,75" fill="white"></polygon>
              <polygon points="50,25 75,75 25,75" fill="white"></polygon>
              <polygon points="35,35 65,35 50,65" fill="white"></polygon>
              <polygon points="35,35 65,35 50,65" fill="white"></polygon>
              <polygon points="35,35 65,35 50,65" fill="white"></polygon>
              <polygon points="35,35 65,35 50,65" fill="white"></polygon>
            </mask>
          </defs>
        </svg>
        <div class="box"></div>
      </div>
    `;
    await handleFileUpload(e);
    dropArea.innerHTML = originalDropAreaText;
    initiateButton.disabled = false;
    initiateButton.innerHTML = originalIntiateButtonHTML;
  });

  dropArea.addEventListener("click", () => zipFileInput.click());
  zipFileInput.addEventListener("change", () => {
    if (zipFileInput.files.length > 0) {
      dropArea.innerHTML = `
      <div
              class="size-16 rounded-full bg-slate-100 dark:bg-surface-dark flex items-center justify-center shadow-lg group-hover:shadow-neon transition-all duration-300"
            >
              <span class="material-symbols-outlined text-4xl!">
                folder_zip
              </span>
            </div>
            <div class="flex flex-col items-center gap-2 z-10">
              <p
                class="text-slate-900 dark:text-white text-xl font-bold leading-tight tracking-[-0.015em] text-center"
              >
                Your File is ready to be sorted!
              </p>
            </div>
          </div>
      `;
    }
  });

  if (selectFileButton) {
    selectFileButton.addEventListener("click", (e) => {
      e.stopPropagation(); // Stop the event from bubbling up to dropArea unnecessarily
      zipFileInput.click();
    });
  }

  initiateButton.addEventListener("click", (e) => {
    e.preventDefault();

    uploadForm.dispatchEvent(new Event("submit"));
  });
});
