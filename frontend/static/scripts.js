// Navbar
const sidebarBtn = document.querySelector('.toggle-btn i')
const sideBarContainer = document.querySelector('.sidebar')
const bodyContainer = document.querySelector('.body-container')
const windowWidth = window.innerWidth


const sidebarItems1 = document.querySelectorAll('.sidebar-items .group-up div a p')
const sidebarItems2 = document.querySelectorAll('.sidebar-items .group-down div a p')

const sidebarItemsDiv1 = document.querySelectorAll('.sidebar-items .group-up a')
const sidebarItemsDiv2 = document.querySelectorAll('.sidebar-items .group-down a')


sidebarBtn.addEventListener("click", () => {

    //check
    if (bodyContainer.matches('.min')) {
        sideBarContainer.classList.remove('min')
        bodyContainer.classList.remove('min')
        sidebarBtn.classList.remove('bx-arrow-from-left')
        sidebarBtn.classList.add('bx-arrow-from-right')
        sidebarItemsDiv1.forEach(item => {
            item.classList.remove('min')
        })
        sidebarItemsDiv2.forEach(item => {
            item.classList.remove('min')
        })

        sidebarItems1.forEach(item => {
            item.classList.remove('hidden')
        })
        sidebarItems2.forEach(item => {
            item.classList.remove('hidden')
        })

    } else {
        sideBarContainer.classList.add('min')
        bodyContainer.classList.add('min')
        sidebarBtn.classList.remove('bx-arrow-from-right')
        sidebarBtn.classList.add('bx-arrow-from-left')
        sidebarItemsDiv1.forEach(item => {
            item.classList.add('min')
        })
        sidebarItemsDiv2.forEach(item => {
            item.classList.add('min')
        })

        sidebarItems1.forEach(item => {
            item.classList.add('hidden')
        })
        sidebarItems2.forEach(item => {
            item.classList.add('hidden')
        })

    }
});

function loginPrompt(page) {
    openModal(modal)
    showModalNotif('Log in to ' + page)
}


const openModalButtons = document.querySelectorAll('[data-modal-target]')
const closeModalButtons = document.querySelectorAll('[data-close-button]')
const overlay = document.getElementById('overlay')
const loginBtn2 = document.getElementById('login-btn-2')

if (loginBtn2 !== null && loginBtn2) {
    loginBtn2.addEventListener('click', () => {
        const modal = document.querySelector(button.dataset.modalTarget)
        openModal(modal)
    })
}


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


function formSubmission(event) {
    event.preventDefault()
    const username = document.querySelector('#username').value;
    const password = document.querySelector('#password').value;
    if (!username || !password) {
        showModalNotif('please enter your username and password or use discord login.');
        return;
    }
    if (password.length < 8) {
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
                response.json().then(data => {
                    showModalNotif(data.message)
                });
                setTimeout(function () {
                    // Redirect to homepage
                    window.location.href = '/login';
                }, 1000);

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
const searchTrigger2 = document.getElementById("search-trigger-2")
if (searchTrigger2 !== null) {
    searchTrigger2.addEventListener("click", () => {
        showSearch()
    })
}

function showSearch() {
    fetchFilesAndDisplay()
    const searchContainer = document.getElementById("search-container")
    searchContainer.classList.add("active")
    clearOverlay.classList.add("active")
    // contentOverlay.classList.add("active")
    overlay.classList.add('active')
}

function hideSearch() {
    const searchContainer = document.getElementById("search-container")
    searchContainer.classList.remove("active")
    clearOverlay.classList.remove("active")
    // contentOverlay.classList.remove("active")
    overlay.classList.remove('active')
}


const searchInput = document.getElementById("search-box");
const searchItems = document.querySelectorAll(".search-item");

searchInput.addEventListener("input", function (event) {
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

//Notifs
function hoverDel() {
    const icons = document.querySelectorAll('.bx');


    icons.forEach(icon => {
        // mouse hover
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
}


const notifsBox = document.getElementById("notif-trigger")
notifsBox.addEventListener("click", () => {
    showNotifs()
})
const notifsBox2 = document.getElementById("notif-trigger-2")
if (notifsBox2 !== null) {
    notifsBox2.addEventListener("click", () => {
        showNotifs()
    })
}


function showNotifs() {
    const notifsBox = document.getElementById("user-notifs-popup")
    notifsBox.classList.add("active")
    clearOverlay.classList.add("active")
    contentOverlay.classList.add("active")

    fetchNotificationsAndDisplay()


}

function hideNotifs() {
    const notifsBox = document.getElementById("user-notifs-popup")
    notifsBox.classList.remove("active")
    clearOverlay.classList.remove("active")
    contentOverlay.classList.remove("active")

}


// startup
window.onload = hideFlashMessage()

function hideFlashMessage() {
    const flashMessages = document.getElementById("flash-messages")
    if (flashMessages !== null) {
        setTimeout(function () {
            flashMessages.classList.add("hidden");
        }, 3000);
    }

}


//Notifs tests
// Function to fetch notifications and display them in the existing container
function fetchNotificationsAndDisplay() {
    // clear the existing container
    const notificationsContainer = document.getElementById('user-notifs-popup');
    notificationsContainer.querySelector('.notifs-list').innerHTML = '';


    fetch('/notifications')
        .then(response => response.json())
        .then(data => {
            // Handle the received notifications data
            displayNotifications(data);
            hoverDel()

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

    if (notification.url) {
        const notifText = document.createElement('a');
        notifText.href = notification.url;
        notifText.target = "_blank"
        notifText.textContent = notification.message;

        notificationElement.appendChild(notifText);
    } else {
        const notifText = document.createElement('p');
        notifText.textContent = notification.message;

        notificationElement.appendChild(notifText);
    }

    // Create a trash icon element
    const trashIcon = document.createElement('i');
    trashIcon.className = 'bx bxs-trash';

    // Append the trash icon to the notification element
    notificationElement.appendChild(trashIcon);

    // remove notif when clicked
    trashIcon.addEventListener('click', () => {
            const messageId = trashIcon.closest('.bx-items').getAttribute('data-notification-id');
            deleteNotif(messageId)
            notificationElement.classList.add('hidden')
        }
    );

    // add a data attribute to the notification element with the notification ID
    notificationElement.setAttribute('data-notification-id', notification.id);

    // Append the notification element to the existing container
    notificationsContainer.querySelector('.notifs-list').appendChild(notificationElement);
}

// Function to display notifications in your existing container
function displayNotifications(notifications) {
    notifications.forEach(notification => {
        addNotificationToContainer(notification);
    });
}


function deleteNotif(id) {
    const url = `/removenotif?id=${id}`;
    fetch(url, {
        method: 'GET',
    })
        .then((response) => {
            if (response.ok) {
                console.log('Notification removed successfully.');
            } else {
                console.error('Failed to remove notification.');
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}

//clear all
const clearAllBtn = document.getElementById("clear-btn")
clearAllBtn.addEventListener("click", () => {
    fetch('/clearnotifs', {
        method: 'GET',
    })
        .then((response) => {
            if (response.ok) {
                console.log('Notifications cleared successfully');
                fetchNotificationsAndDisplay()
            } else {
                console.error('Failed to clear notifications');
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
})


//ALternate notifs
const popNotifs = document.getElementById("popnotifs");
const popNotifItem = document.getElementById("pop-notif");

function addPopNotif(message) {
    popNotifItem.innerHTML = message;
    popNotifs.classList.remove("none")
    popNotifs.classList.remove("hidden")
    setTimeout(function () {
        popNotifs.classList.add("hidden");
    }, 3000);

}

const searchItemsContainer = document.querySelector('.body-contents');

function fetchFilesAndDisplay() {
    // clear the existing container
    searchItemsContainer.innerHTML = '';

    fetch('/files')
        .then(response => response.json())
        .then(data => {
            // Handle the received files data
            displayFiles(data);
        })
        .catch(error => {
            console.error('Error fetching files:', error);
        });
}

// Function to add a single file to the existing container
function addFileToContainer(file) {
    searchUrl = document.createElement('a');
    // searchUrl.href = 'view/' + file.id;
    const currentURL = window.location.href;
    if (currentURL.includes('/view/')) {
        // If the current URL already contains '/view/', simply append the file.id
        searchUrl.href = '/view/' + file.id;
    } else {
        // If the current URL doesn't contain '/view/', add '/view/' and then append the file.id
        searchUrl.href = 'view/' + file.id;
    }
    searchUrl.classList.add('search-urls');

    searchItem = document.createElement('div');
    searchItem.classList.add('search-item');
    left = document.createElement('div');
    left.classList.add('left');
    icon = document.createElement('i');
    icon.classList.add('bx')
    icon.classList.add('bxs-file')

    filename = document.createElement('p');
    filename.classList.add('filename');
    filename.textContent = file.filename;
    filesize = document.createElement('p');
    filesize.classList.add('filesize');
    filesize.textContent = file.size;

    left.appendChild(icon);
    left.appendChild(filename);
    searchItem.appendChild(left);
    searchItem.appendChild(filesize);
    searchUrl.appendChild(searchItem);
    searchItemsContainer.appendChild(searchUrl);

}

// Function to display files in your existing container
function displayFiles(files) {
    files.forEach(file => {
        addFileToContainer(file);
    });
    //update search
    const searchItems = document.querySelectorAll(".search-item");

    searchInput.addEventListener("input", function (event) {
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
}

const body = document.querySelector('*')
body.addEventListener('scroll', () => {
    alert('scrolling')
})

// if ('serviceWorker' in navigator) {
//     navigator.serviceWorker.register('/service-worker.js', {scope: '/'})
//         .then(function (registration) {
//             // console.log('Service Worker registered with scope:', registration.scope);
//         })
//         .catch(function (error) {
//             console.error('Service Worker registration failed:', error);
//         });
// }