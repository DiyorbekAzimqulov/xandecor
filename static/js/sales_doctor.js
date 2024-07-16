document.addEventListener("DOMContentLoaded", (event) => {
  document.getElementById("selectWarehouseButton").addEventListener("click", function () {
    const selectedWarehouse = document.getElementById("warehouseSelect").value;

    // Hide the modal
    $("#warehouseModal").modal("hide");

    // Call a function to update the table with the selected warehouse data
    updateTableWithWarehouseData(selectedWarehouse);
  });
});

function updateTableWithWarehouseData(warehouse) {
  // Fetch the data for the selected warehouse (using Ajax or fetching from a variable)
  $.ajax({
    url: '{% url "fetch_warehouse_data" %}',
    method: "GET",
    data: {
      warehouse: warehouse,
    },
    success: function (response) {
      // Assuming response contains the HTML for the updated table body
      $("table tbody").html(response.html);
    },
    error: function (error) {
      console.log("Error fetching warehouse data:", error);
    },
  });
}
