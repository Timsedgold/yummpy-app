// Select all forms with IDs starting with "fav-form-"
const favoriteForms = document.querySelectorAll("form[id^='fav-form-']");

favoriteForms.forEach(form => {
  form.addEventListener("submit", async function (e) {
    e.preventDefault(); // Prevent the page reload

    // Get the recipe ID from the button's data attribute
    const button = form.querySelector("button");
    const recipeId = button.dataset.recipeId;

    const response = await fetch(`/recipes/${recipeId}/favorites`, {
        method: "POST",
      });

    if (response.ok) {
        // Toggle the button class between primary and secondary
        button.classList.toggle("btn-primary");
        button.classList.toggle("btn-secondary");
    } else {
        console.error("Failed to toggle favorite status.");
      }
   
  });
});
