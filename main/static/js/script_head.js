document.addEventListener("DOMContentLoaded", () => {
  const menuItems = document.querySelectorAll(".dropdown");

  // Function to close all dropdowns except the one that is passed as a parameter
  const closeOtherDropdowns = (currentDropdown) => {
    menuItems.forEach((menuItem) => {
      const dropdown = menuItem.querySelector(".dropdown-content");
      if (dropdown !== currentDropdown) {
        dropdown.classList.remove("show");
      }
    });
  };

  menuItems.forEach((menuItem) => {
    const dropbtn = menuItem.querySelector(".dropbtn");
    const dropdown = menuItem.querySelector(".dropdown-content");

    dropbtn.addEventListener("click", (event) => {
      event.stopPropagation(); // Prevent event from bubbling up to the document
      dropdown.classList.toggle("show");
      closeOtherDropdowns(dropdown);
    });
  });

  // Close all dropdowns when clicking outside any dropdown
  document.addEventListener("click", () => {
    closeOtherDropdowns(null);
  });
});
