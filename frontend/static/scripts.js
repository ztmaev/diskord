const openModalButtons = document.querySelectorAll('[data-modal-target]')
const closeModalButtons = document.querySelectorAll('[data-close-button]')
const overlay = document.getElementById('overlay')

openModalButtons.forEach(button => {
    button.addEventListener('click', () => {
        const modal = document.querySelector(button.dataset.modalTarget)
        openModal(modal)
    })
})

overlay.addEventListener('click', () => {
    const modals = document.querySelectorAll('.modal.active')
    modals.forEach(modal => {
        closeModal(modal)
    })
})

closeModalButtons.forEach(button => {
    button.addEventListener('click', () => {
        const modal = button.closest('.modal')
        closeModal(modal)
    })
})

function openModal(modal) {
    if (modal == null) return
    modal.classList.add('active')
    overlay.classList.add('active')
}

function closeModal(modal) {
    if (modal == null) return
    modal.classList.remove('active')
    overlay.classList.remove('active')
}

//Password field
const passInput = document.getElementById("password")
const passIcon = document.getElementById("password-toggle")
passInput.addEventListener("input", function (event) {
    if (passInput.value !== "") {
        showPassIcon()
    } else {
        hidePassIcon()
    }
    console.log(passInput.value)
})

function showPassIcon() {
    passIcon.classList.add("active")
}

function hidePassIcon() {
    passIcon.classList.remove("active")
}

function passwordToggle() {
    let passwordStatus = document.getElementById("password");
    let toggleButton = document.getElementById("password-toggle");

    if (passwordStatus.type === "password") {
        passwordStatus.type = "text";
        toggleButton.innerHTML = "<i class='bx bxs-show'></i>";
    } else {
        passwordStatus.type = "password";
        toggleButton.innerHTML = "<i class='bx bxs-hide'></i>";
    }
}


function formSubmission() {
    event.preventDefault()
    const username = document.querySelector('#username').value;
    const password = document.querySelector('#password').value;
    if (!username || !password) {
        alert('please enter your username and password or use discord login.');
        return;
    }
    if (password[7] === undefined) {
        showModalNotif("Password should be at least 8 characters.")
    }
    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({username, password}),
    })
        .then(response => {
            if (response.status === 200) {
                // Redirect to homepage
                window.location.href = '/';
            } else {
                // Handle other status codes or error responses here
                response.json().then(data => {
                    showModalNotif(data.message)
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });


}

const contentOverlay = document.getElementById("overlay-content");
const clearOverlay = document.getElementById("overlay-clear");

contentOverlay.addEventListener("click", () => {
    hideProfileOptions()
    hideNotifs()
    hideSearch()
})
var profilePopup = document.getElementById("profile-options-menu");
clearOverlay.addEventListener("click", () => {
    hideProfileOptions()
    hideNotifs()
    hideSearch()
})

// hover del
const icons = document.querySelectorAll('.bx');

icons.forEach(icon => {
    icon.addEventListener('mouseenter', () => {
        const parentP = icon.closest('.bx-items');
        if (parentP) {
            parentP.classList.add('hovered');
        }
    });

    icon.addEventListener('mouseleave', () => {
        const parentP = icon.closest('.bx-items');
        if (parentP) {
            parentP.classList.remove('hovered');
        }
    });
});


function showProfileOptions() {
    profilePopup.classList.add("active")
    clearOverlay.classList.add("active")
    contentOverlay.classList.add("active")
}

function hideProfileOptions() {
    if (profilePopup !== null && profilePopup) {
        profilePopup.classList.remove("active")
    }
    clearOverlay.classList.remove("active")
    contentOverlay.classList.remove("active")
}

function showModalNotif(message) {
    const notifbox = document.getElementById("modal-notifs")
    const notifboxText = document.getElementById("modal-notif-message")
    notifbox.classList.add("active");
    notifboxText.innerHTML = message;

}

//Search
const searchTrigger = document.getElementById("search-trigger")
if (searchTrigger !== null) {
    searchTrigger.addEventListener("click", () => {
        showSearch()
    })
}

function showSearch() {
    const searchContainer = document.getElementById("search-container")
    searchContainer.classList.add("active")
    clearOverlay.classList.add("active")
    contentOverlay.classList.add("active")
}

function hideSearch() {
    const searchContainer = document.getElementById("search-container")
    searchContainer.classList.remove("active")
    clearOverlay.classList.remove("active")
    contentOverlay.classList.remove("active")
}

// const searchInput = document.getElementById("search-box")
// searchInput.addEventListener("input", function(event){
//     console.log(searchInput.value)
// })

const searchInput = document.getElementById("search-box");
const searchItems = document.querySelectorAll(".search-item");

searchInput.addEventListener("input", function(event) {
    const searchTerm = searchInput.value.toLowerCase();

    searchItems.forEach(item => {
        const fileName = item.querySelector("p").textContent.toLowerCase();
        if (fileName.includes(searchTerm)) {
            item.classList.remove("hidden"); // Remove the "hidden" class
        } else {
            item.classList.add("hidden"); // Add the "hidden" class
        }
    });
});

//TODO: work on this

//Notifs

const notifsBox = document.getElementById("notif-trigger")
notifsBox.addEventListener("click", () => {
    showNotifs()
})

function showNotifs() {
    const notifsBox = document.getElementById("user-notifs-popup")
    notifsBox.classList.add("active")
    clearOverlay.classList.add("active")
    contentOverlay.classList.add("active")

}

function hideNotifs() {
    const notifsBox = document.getElementById("user-notifs-popup")
    notifsBox.classList.remove("active")
    clearOverlay.classList.remove("active")
    contentOverlay.classList.remove("active")

}


// startup
window.onload = hideFlashMessage()

// TODO: fix this
function hideFlashMessage() {
    const flashMessages = document.getElementById("flash-messages")
    if (flashMessages !== null) {
        flashMessages.classList.add("hidden")
    }

}



//Notifs tests
// Function to fetch notifications and display them in the existing container
function fetchNotificationsAndDisplay() {
    fetch('/notifications')
        .then(response => response.json())
        .then(data => {
            // Handle the received notifications data
            displayNotifications(data);
        })
        .catch(error => {
            console.error('Error fetching notifications:', error);
        });
}

// Function to add a single notification to the existing container
function addNotificationToContainer(notification) {
    const notificationsContainer = document.getElementById('user-notifs-popup');

    // Create a new notification element
    const notificationElement = document.createElement('p');
    notificationElement.className = 'bx-items';
    notificationElement.textContent = notification.message;

    // Create a trash icon element
    const trashIcon = document.createElement('i');
    trashIcon.className = 'bx bxs-trash';

    // Add a click event listener to the trash icon (you can implement clearing functionality)
    trashIcon.addEventListener('click', function() {
        // Handle deletion of the notification
        // You can make an API request to your backend to delete the notification if needed
        // Then remove the notificationElement from the container
        // notificationElement.remove();
    });

    // Append the trash icon to the notification element
    notificationElement.appendChild(trashIcon);

    // Append the notification element to the existing container
    notificationsContainer.querySelector('.notifs-list').appendChild(notificationElement);
}

// Function to display notifications in your existing container
function displayNotifications(notifications) {
    notifications.forEach(notification => {
        addNotificationToContainer(notification);
    });
}

// Call the fetchNotificationsAndDisplay function to load notifications initially
fetchNotificationsAndDisplay();

// You can also set up a timer to periodically fetch and display notifications
// setInterval(fetchNotificationsAndDisplay, 5000); // Example: Fetch notifications every 5 seconds
