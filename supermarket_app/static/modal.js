function setupDeleteModal(modalId, itemNameId, itemIdField) {
    document.addEventListener("DOMContentLoaded", function () {
        var confirmDeleteModal = document.getElementById(modalId);
        confirmDeleteModal.addEventListener("show.bs.modal", function (event) {
            var button = event.relatedTarget;
            var itemId = button.getAttribute("data-id");
            var itemName = button.getAttribute("data-nombre");

            document.getElementById(itemNameId).textContent = itemName;
            document.getElementById(itemIdField).value = itemId;
        });
    });
}