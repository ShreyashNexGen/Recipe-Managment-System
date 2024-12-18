// Mobile Sidebar Toggle Function

function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    sidebar.classList.toggle('closed');
}

// Close the sidebar when clicking outside
window.addEventListener('click', function (event) {
    const sidebar = document.querySelector('.sidebar');
    if (!sidebar.contains(event.target) && !event.target.matches('.menu-toggle')) {
        sidebar.classList.add('closed');
    }
});

// Dropdown Toggle for Tags (for small screen)
document.querySelectorAll('.nav-item.dropdown').forEach(function (dropdown) {
    dropdown.addEventListener('click', function (e) {
        e.stopPropagation(); // Prevent click from closing the dropdown
        this.querySelector('.dropdown-menu').classList.toggle('show');
    });
});

// Close dropdowns when clicking outside
window.addEventListener('click', function (event) {
    document.querySelectorAll('.dropdown-menu').forEach(function (menu) {
        if (!menu.contains(event.target)) {
            menu.classList.remove('show');
        }
    });
});


    function toggleTags() {
        const dropdown = document.getElementById('tagsDropdown');
        dropdown.classList.toggle('show');
    }
    document.querySelectorAll('.dropdown-toggle').forEach(function(toggle) {
        toggle.addEventListener('click', function(e) {
            var menu = this.nextElementSibling;
            menu.classList.toggle('show');
        });
    });
    

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
    console.log("Recipe Data:", recipeData);  // For debugging purposes

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
//   function fetchLiveData() {
//     fetch('http://localhost:5000/getLiveValues')
//         .then(response => response.json())
//         .then(data => {
//             if (data.success) {
//                 const tableBody = document.getElementById('liveDataTable').getElementsByTagName('tbody')[0];
//                 tableBody.innerHTML = ''; // Clear previous rows
                
//                 data.data.forEach(row => {
//                     const tr = document.createElement('tr');
//                     tr.innerHTML = `
//                         <td>${row.tagId}</td>
//                         <td>${row.value}</td>
//                         <td>${row.timestamp}</td>
//                     `;
//                     tableBody.appendChild(tr);
//                 });
//             } else {
//                 console.error('Failed to fetch live data:', data.error);
//             }
//         })
//         .catch(error => console.error('Error fetching live data:', error));
// }

// // Fetch live data every 10 seconds
// setInterval(fetchLiveData, 10000);

// // Fetch live data once on page load
// window.onload = fetchLiveData;

// socket.on('liveData', (data) => {
//     if (data.success) {
//         // Create table rows dynamically
//         const rows = data.results.map(item => `
//             <tr>
//                 <td>${item.nodeId}</td>
//                 <td>${item.value || item.error}</td>
//             </tr>`).join('');

//         // Populate the table
//         document.getElementById('dataContainer').innerHTML = `
//             <table border="1" style="width:100%; border-collapse: collapse;">
//                 <thead>
//                     <tr>
//                         <th>Node</th>
//                         <th>Value</th>
//                     </tr>
//                 </thead>
//                 <tbody>
//                     ${rows}
//                 </tbody>
//             </table>`;
//     } else {
//         document.getElementById('dataContainer').innerHTML = `<p>Error: ${data.error}</p>`;
//     }
// });

// // Trigger live reading from backend
// fetch('http://localhost:5000/startLiveRead', {
//     method: 'POST',
//     headers: { 'Content-Type': 'application/json' },
//     body: JSON.stringify({ nodeIds: ['ns=3;s="DataBlock"."data1"', 'ns=3;s="DataBlock"."data2"'] })
// }).then(response => response.json())
//   .then(data => console.log(data))
//   .catch(error => console.error('Error:', error));



  function searchTable() {
    const input = document.getElementById('searchInput');
    const filter = input.value.toLowerCase();
    const table = document.getElementById('rawMaterialTable');
    const rows = table.getElementsByTagName('tr');

    for (let i = 1; i < rows.length; i++) { // Skip the header row
        const cells = rows[i].getElementsByTagName('td');
        let match = false;

        for (let j = 0; j < cells.length; j++) {
            if (cells[j] && cells[j].innerText.toLowerCase().includes(filter)) {
                match = true;
                break;
            }
        }

        rows[i].style.display = match ? '' : 'none';
    }
}
function searchTable() {
    // Get the input value and convert it to lowercase for case-insensitive comparison
    const input = document.getElementById("searchInput").value.toLowerCase();
    const table = document.getElementById("tagoverviewtable");
    const rows = table.getElementsByTagName("tr");

    // Loop through all table rows (excluding the header row)
    for (let i = 1; i < rows.length; i++) {
        const cells = rows[i].getElementsByTagName("td");
        let match = false;

        // Check each cell in the row
        for (let j = 0; j < cells.length; j++) {
            if (cells[j].innerText.toLowerCase().includes(input)) {
                match = true;
                break;
            }
        }

        // Toggle the visibility of the row based on whether there's a match
        rows[i].style.display = match ? "" : "none";
    }
}





function toggleTagForm() {
    const addTagSection = document.getElementById('add-tag-section');
    if (addTagSection.style.display === 'flex' || addTagSection.style.display === '') {
        addTagSection.style.display = 'none'; // Show the form
    } else {
        addTagSection.style.display = 'flex'; // Hide the form
    }
}



    document.querySelectorAll('.dropdown-toggle').forEach(item => {
        item.addEventListener('click', function (e) {
            e.preventDefault();
            const menu = this.nextElementSibling;
            menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
        });
    });    








    function confirmDelete(tagId) {
        if (confirm("Do you want to delete this tag?")) {
            fetch(`/delete-tag/${tagId}`, {
                method: "DELETE",
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.success) {
                        // Remove the row from the table
                        const row = document.getElementById(`row-${tagId}`);
                        if (row) row.remove();
                        alert("Tag deleted successfully.");
                    } else {
                        alert(`Failed to delete tag: ${data.error || "Unknown error"}`);
                    }
                })
                .catch((error) => {
                    console.error("Error:", error);
                    alert("An error occurred while deleting the tag.");
                });
        }
    }
    

    function confirmDeleteRecipe(recipe_Id) {
        if (confirm("Do you want to delete this Recipe?")) {
            fetch(`/delete-recipe/${recipe_Id}`, {
                method: "DELETE",
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.success) {
                        // Remove the row from the table
                        const row = document.getElementById(`row-${recipe_Id}`);
                        if (row) row.remove();
                        alert('Recipe deleted successfully!');
                    } else {
                        alert(`Failed to delete Recipe: ${data.error || "Unknown error"}`);
                    }
                })
                .catch((error) => {
                    console.error("Error:", error);
                    alert("An error occurred while deleting the recipe.");
                });
        }
    }
    
    
    
    


   function toggleUpdateMaterialForm(materialId = null) {
    const formSection = document.getElementById('update-material-section');
    formSection.style.display = formSection.style.display === 'none' ? 'flex' : 'none';

    // If materialId is provided, prefill the form with existing data
    if (materialId) {
        fetch(`/get_raw_material/${materialId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('update_material_Id').value = data.raw_material.material_Id;
                    document.getElementById('update_typeCode').value = data.raw_material.typeCode;
                    document.getElementById('update_lotNo').value = data.raw_material.lotNo;
                    document.getElementById('update_make').value = data.raw_material.make;
                    document.getElementById('update_user').value = data.raw_material.user;
                    document.getElementById('update_materialType').value = data.raw_material.materialType;
                    document.getElementById('update_barcode').value = data.raw_material.barcode;
                } else {
                    alert('Failed to fetch material data.');
                }
            });
    }
}

function submitUpdate() {
    const materialId = document.getElementById('update_material_Id').value;
    const formData = new FormData(document.getElementById('updateMaterialForm'));

    fetch(`/update_raw_material/${materialId}`, {
        method: 'POST',
        body: formData,
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Material updated successfully!');
                location.reload(); // Reload the page to see changes
            } else {
                alert(`Failed to update material: ${data.error}`);
            }
        })
        .catch(error => console.error('Error:', error));
}


/*js code for show 10 enteries*/

