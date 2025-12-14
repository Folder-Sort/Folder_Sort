import "./style.css";
document.addEventListener("DOMContentLoaded", () => {
  const uploadForm = document.getElementById("uploadForm");
  const zipFileInput = document.getElementById("zipFileInput");
  const uploadButton = document.getElementById("uploadButton");
  const statusMessage = document.getElementById("statusMessage");
  const dropArea = document.getElementById("drop-area");
  const selectFileButton = document.getElementById("selectFileButton");

  // 1. Event Listener for Form Submission
  dropArea.addEventListener("click", () => zipFileInput.click());
  zipFileInput.addEventListener("change", () => {
    if (zipFileInput.files.length > 0) {
      // Trigger the form's submit event
      uploadForm.dispatchEvent(new Event("submit"));
    }
  });

  if (selectFileButton) {
    selectFileButton.addEventListener("click", (e) => {
      e.stopPropagation(); // Stop the event from bubbling up to dropArea unnecessarily
      zipFileInput.click();
    });
  }

  uploadForm.addEventListener("submit", handleFileUpload);
  async function handleFileUpload(e) {
    // Prevent the browser from submitting the form normally (which would reload the page)
    e.preventDefault();

    // Basic input validation
    if (zipFileInput.files.length === 0) {
      statusMessage.textContent = "Please select a ZIP file to upload.";
      return;
    }

    const file = zipFileInput.files[0];
    const fileName = file.name;

    // Update UI state
    uploadButton.disabled = true;
    statusMessage.textContent =
      "Uploading and Sorting... Please wait. Do not navigate away.";
    statusMessage.style.color = "orange";

    // 2. Prepare the Data using FormData
    // FormData is essential for sending files via Fetch/XHR
    const formData = new FormData();
    formData.append("file", file); // 'file' MUST match the key Flask expects (request.files['file'])

    try {
      // 3. Send the Request to the Flask Endpoint
      const response = await fetch("/sort", {
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
  }
});
