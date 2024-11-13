function toggleSection(section) {
    const detailsSection = document.getElementById('details-section');
    const submenuSection = document.getElementById('submenu-section');
    
    if (section === 'details') {
        detailsSection.style.display = 'block';
        submenuSection.style.display = 'none';
    } else if (section === 'submenu') {
        submenuSection.style.display = 'block';
        detailsSection.style.display = 'none';
    }
}
function toggleRecipeForm() {
    const recipeSection = document.getElementById('add-recipe-section');
    if (recipeSection.style.display === 'none' || recipeSection.style.display === '') {
        recipeSection.style.display = 'flex';
    } else {
        recipeSection.style.display = 'none';
    }
}
window.onclick = function(event) {
    const recipeSection = document.getElementById('add-recipe-section');
    if (event.target === recipeSection) {
        recipeSection.style.display = 'none';
    }
}

// Show Pop-Up
// function showPopup(recipeId) {
//     document.getElementById("popup-modal").style.display = "block";
//     document.getElementById("recipe-id").textContent = recipeId;
// }d
function showPopup(button) {
    const recipeID = button.getAttribute('data-recipe-id');
    console.log("Recipe ID:", recipeID);
    document.getElementById("popup-modal").style.display = "block";
    document.getElementById("recipe-id").textContent = recipeID;
}

// Close Pop-Up
function closePopup() {
    document.getElementById("popup-modal").style.display = "none";
}

// Handle Form Submission with AJAX
function submitRecipeForm(event) {
    event.preventDefault();  // Prevents the default form submission behavior
    const recipeData = new FormData(document.getElementById("recipe-form"));

    fetch(`/add_recipe_details/${document.getElementById("recipe-id").textContent}`, {
        method: "POST",
        body: recipeData,
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        alert("Recipe details added successfully!");
        closePopup();
        location.reload();  // Reloads the page to see new data
    })
    .catch(error => {
        console.error("Error adding recipe details:", error);
        alert("An error occurred. Please try again.");
    });
}
function toggleNavbar() {
    const navbarLinks = document.getElementById('navbarLinks');
    navbarLinks.style.display = navbarLinks.style.display === 'block' ? 'none' : 'block';
}

function toggleSection(section) {
    const detailsSection = document.getElementById('details-section');
    const submenuSection = document.getElementById('submenu-section');
    
    if (section === 'details') {
        detailsSection.style.display = detailsSection.style.display === 'none' ? 'block' : 'none';
        submenuSection.style.display = 'none';  // Hide submenu when showing details
    } else if (section === 'submenu') {
        submenuSection.style.display = submenuSection.style.display === 'none' ? 'block' : 'none';
        detailsSection.style.display = 'none';  // Hide details when showing submenu
    }
}

  // Password visibility toggle function
  const togglePassword = document.getElementById('togglePassword');
  const passwordField = document.getElementById('password');

  togglePassword.addEventListener('click', function () {
    // Toggle the password field type
    const type = passwordField.type === 'password' ? 'text' : 'password';
    passwordField.type = type;
    // Toggle the eye icon
    this.textContent = this.textContent === '👁️' ? '🙈' : '👁️';
  });

  // Password validation function
  function validatePassword() {
    const password = document.getElementById('password').value;
    const errorMessage = document.getElementById('passwordError');
    
    if (password.length < 8) {
      errorMessage.style.display = 'block';
      return false;
    } else {
      errorMessage.style.display = 'none';
      return true;
    }
  }

