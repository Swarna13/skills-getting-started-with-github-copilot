document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";
      // Reset activity select to the placeholder to avoid duplicate options
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

          const participantsList = details.participants.length > 0
            ? `<ul class="participants-list">${details.participants.map(p => `<li>${p} <button class="remove-participant" data-activity="${name}" data-email="${p}" title="Unregister">✖</button></li>`).join("")}</ul>`
            : `<p class="no-participants"><em>No participants yet</em></p>`;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-section">
            <strong>Participants (${details.participants.length}/${details.max_participants}):</strong>
            ${participantsList}
          </div>
        `;

        activitiesList.appendChild(activityCard);

        // Attach click handlers for remove buttons inside this activity card
        activityCard.querySelectorAll('.remove-participant').forEach(btn => {
          btn.addEventListener('click', async (e) => {
            const activityName = btn.dataset.activity;
            const email = btn.dataset.email;

            if (!confirm(`Unregister ${email} from ${activityName}?`)) return;

            try {
              const res = await fetch(`/activities/${encodeURIComponent(activityName)}/unregister?email=${encodeURIComponent(email)}`, {
                method: 'POST'
              });

              const result = await res.json();
              if (res.ok) {
                messageDiv.textContent = result.message;
                messageDiv.className = 'message success';
                // Refresh activities list
                fetchActivities();
              } else {
                messageDiv.textContent = result.detail || 'Failed to unregister';
                messageDiv.className = 'message error';
              }
            } catch (err) {
              console.error('Error unregistering:', err);
              messageDiv.textContent = 'Failed to unregister. Please try again.';
              messageDiv.className = 'message error';
            }

            messageDiv.classList.remove('hidden');
            setTimeout(() => messageDiv.classList.add('hidden'), 4000);
          });
        });

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "message success";
        signupForm.reset();
        // Refresh activities so the new participant appears immediately
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "message error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
