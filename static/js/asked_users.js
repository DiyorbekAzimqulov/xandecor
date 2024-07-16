function acceptUser(userId) {
  $.ajax({
    url: `/containers/accept-user/${userId}/`,
    type: "GET",
    success: function (response) {
      if (response.status === "show_organizations") {
        $("#modal-user-id").val(response.user_id);
        $("#modal-organization-select").empty();
        response.organizations.forEach(function (organization) {
          $("#modal-organization-select").append(new Option(organization.name, organization.id));
        });
        $("#organization-selection-modal").show();
      }
    },
  });
}

function rejectUser(userId) {
  $.ajax({
    url: `/containers/reject-user/${userId}/`,
    type: "GET",
    success: function (response) {
      if (response.status === "rejected") {
        $(`#user-${userId}`).remove();
      }
    },
  });
}

$("#organization-selection-form").submit(function (event) {
  event.preventDefault();
  const userId = $("#modal-user-id").val();
  const organizationIds = $("#modal-organization-select").val();

  $.ajax({
    url: saveUserWithOrganizationsUrl,
    type: "POST",
    data: {
      user_id: userId,
      "organization_ids[]": organizationIds,
      csrfmiddlewaretoken: csrfToken,
    },
    success: function (response) {
      if (response.status === "success") {
        $(`#user-${userId}`).remove();
        closeModal();
        clearModalContent();
      }
    },
  });
});

function closeModal() {
  $("#organization-selection-modal").hide();
}

function clearModalContent() {
  $("#modal-user-id").val("");
  $("#modal-organization-select").empty();
}
