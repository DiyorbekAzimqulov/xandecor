document.addEventListener("DOMContentLoaded", function () {
  flatpickr("#date-range", {
    mode: "range",
    dateFormat: "Y-m-d",
  });

  document.getElementById("filter-button").addEventListener("click", function () {
    const dateRange = document.getElementById("date-range").value;
    if (dateRange) {
      const [fromDate, toDate] = dateRange.split(" to ");
      window.location.href = `/containers/pdts-st/${fromDate}_${toDate}`;
    }
  });

  document.getElementById("report-location-button").addEventListener("click", function () {
    $("#reportLocationModal").modal("show");
  });

  document.getElementById("report-location-submit").addEventListener("click", function () {
    const locationName = document.getElementById("location-name").value;
    const selectedContainers = [];
    document.querySelectorAll(".container-checkbox-modal:checked").forEach((checkbox) => {
      selectedContainers.push(checkbox.value);
    });

    // Send data to server (you might want to use AJAX or form submission)
    $.ajax({
      type: "POST",
      url: "report-location/",
      data: {
        location_name: locationName,
        containers: selectedContainers.join(","),
        csrfmiddlewaretoken: "{{ csrf_token }}",
      },
      success: function (response) {
        alert("Location reported successfully");
        $("#reportLocationModal").modal("hide");
      },
      error: function (error) {
        alert("An error occurred");
      },
    });
  });
});
