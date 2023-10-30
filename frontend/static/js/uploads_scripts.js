// RECENTS
const recentsList = document.querySelector('.recents-list');

const getRecents = async () => {
    const response = await fetch('/api/recents');
    const data = await response.json();
    return data;
}

const renderRecents = async () => {
    //loading animation
    recentsList.innerHTML = `
            <div class="loading">
                <i class='bx bx-loader-alt bx-spin'></i>
            </div>
        `;
    const recents = await getRecents();
    recentsList.innerHTML = '';

    if (recents.length === 0) {
        recentsList.innerHTML = `
                <div class="loading">
                    <p>No recent files found</p>
                </div>
            `;
        return;
    }

    recents.forEach(recent => {
        const recentItem = document.createElement('div');
        recentItem.classList.add('recent-item');
        recentItem.setAttribute('value', recent.id);
        recentItem.innerHTML = `
                <div class="recent-icon">
                    <i class='bx bxs-file'></i>
                </div>
                <div class="recent-body">
                    <p class="filename">${recent.filename}</p>
                    <p class="filedate">${recent.date}</p>
                    <p class="filesize">${recent.size_simple}</p>
                </div>
                <div class="recent-options">
                <i class="bx bx-dots-vertical" value="${recent.id}"></i>
                </div>
            `;
        recentsList.appendChild(recentItem);

        // add click and dblclick events
        recentItem.addEventListener('click', () => {
            // remove selected from all files
            recents.forEach(recent => {
                const recentItem = document.querySelector(`.recent-item[value="${recent.id}"]`);
                recentItem.classList.remove('selected');
                const fileItem = document.querySelector(`.file-item[value="${recent.id}"]`);
                if (fileItem) {
                    fileItem.classList.remove('selected');
                }
            });
            recentItem.classList.toggle('selected');
            showDetails(recent.id, type = 'file');
        });

        recentItem.addEventListener('dblclick', () => {
                window.location.href = `/view/${recent.id}`;

            }
        );

        updateDots()
    });
}

// FOLDERS

const foldersList = document.querySelector('.folders-list');
const getFolders = async () => {
    const response = await fetch('/api/folders');
    const data = await response.json();
    return data;
}

const renderFolders = async () => {
    //loading animation
    foldersList.innerHTML = `
            <div class="loading">
                <i class='bx bx-loader-alt bx-spin'></i>
            </div>
        `;
    const folders = await getFolders();
    foldersList.innerHTML = '';

    if (folders.length === 0) {
        foldersList.innerHTML = `
                <div class="loading">
                    <p>No folders found</p>
                </div>
            `;
        return;
    }

    folders.forEach(folder => {
        const folderItem = document.createElement('div');
        folderItem.classList.add('folder-item');
        folderItem.setAttribute('value', folder.dir_id);
        folderItem.innerHTML = `
                <div class="folder-icon">
                    <i class='bx bxs-folder'></i>
                </div>
                <div class="folder-name">
                    ${folder.name}
                </div>
                <div class="folder-options">
                <i class="bx bx-dots-vertical" value="${folder.dir_id}"></i>
                </div>
            `;
        foldersList.appendChild(folderItem);

        // add click and dblclick events
        folderItem.addEventListener('click', () => {
            // remove selected from all files
            folders.forEach(folder => {
                const folderItem = document.querySelector(`.folder-item[value="${folder.dir_id}"]`);
                folderItem.classList.remove('selected');
            });
            folderItem.classList.toggle('selected');
            showDetails(folder.dir_id, type = 'folder');
        }
        );

        folderItem.addEventListener('dblclick', () => {
            showfolderView(folder.dir_id);
        }
        );

        updateFolderDots();
    });

}

//FILES
// sort btns
const filesList = document.querySelector('.files-list');
const sortBtn = document.querySelector('.sort-type i');
const sortSelector = document.querySelector('.sort-selector');

sortBtn.addEventListener('click', () => {
    if (sortBtn.matches('.bx-sort-down')) {
        ;
        sortBtn.classList.remove('bx-sort-down');
        sortBtn.classList.add('bx-sort-up');
    } else if (sortBtn.matches('.bx-sort-up')) {
        sortBtn.classList.remove('bx-sort-up');
        sortBtn.classList.add('bx-sort-down');
    }

    sortFiles();
});

// sort selector
sortSelector.addEventListener('change', () => {
    sortFiles();
});

function getSortSelector() {
    return sortSelector.value;
}

function getSortType() {
    if (sortBtn.matches('.bx-sort-down')) {
        return 'desc';
    } else if (sortBtn.matches('.bx-sort-up')) {
        return 'asc';
    }
}

const fetchFiles = async () => {
    const response = await fetch('/files');
    const data = await response.json();
    return data;
}

const sortFiles = async () => {
    const sortMode = getSortSelector();
    const sortType = getSortType();

    // console.log(fetchFiles())
    //loading animation
    filesList.innerHTML = `
            <div class="loading">
                <i class='bx bx-loader-alt bx-spin'></i>
            </div>
        `;
    const files = await fetchFiles();
    filesList.innerHTML = '';

    if (files.length === 0) {
        filesList.innerHTML = `
                <div class="loading">
                    <p>No files found</p>
                </div>
            `;
        return;
    }

    if (sortMode === 'name') {
        files.sort((a, b) => {
            if (sortType === 'asc') {
                return a.filename.localeCompare(b.filename);
            } else if (sortType === 'desc') {
                return b.filename.localeCompare(a.filename);
            }
        });
    } else if (sortMode === 'size') {
        files.sort((a, b) => {
            if (sortType === 'asc') {
                return a.size - b.size;
            } else if (sortType === 'desc') {
                return b.size - a.size;
            }
        });
    } else if (sortMode === 'date') {
        files.sort((a, b) => {
            if (sortType === 'asc') {
                return new Date(a.date) - new Date(b.date);
            } else if (sortType === 'desc') {
                return new Date(b.date) - new Date(a.date);
            }
        });
    }

    files.forEach(file => {
        const fileItem = document.createElement('div');
        fileItem.classList.add('file-item');
        fileItem.setAttribute('value', file.id);
        fileItem.innerHTML = `
                <div class="file-icon">
                    <i class='bx bxs-file'></i>
                </div>
                <div class="file-body">
                    <p class="filename">${file.filename}</p>
                    <p class="filedate">${file.date}</p>
                    <p class="filesize">${file.size_simple}</p>
                </div>
                <div class="file-options">
                <i class="bx bx-dots-vertical" value="${file.id}"></i>
                </div>
            `;
        filesList.appendChild(fileItem);

        // add click and dblclick events
        fileItem.addEventListener('click', () => {
            // remove selected from all files
            files.forEach(file => {
                const fileItem = document.querySelector(`.file-item[value="${file.id}"]`);
                fileItem.classList.remove('selected');
                const recentItem = document.querySelector(`.recent-item[value="${file.id}"]`);
                if (recentItem) {
                    recentItem.classList.remove('selected');
                }
            });
            fileItem.classList.toggle('selected');
            showDetails(file.id, type = 'file');
        });

        fileItem.addEventListener('dblclick', () => {
            window.location.href = `/view/${file.id}`;
        });

        updateDots();

    });

}


//DETAILS
const details = document.querySelector('.details-body-inner');

const showDetails = async (id, type) => {
    updateDetailsOptions(id);
    //loading animation
    details.innerHTML = `
            <div class="loading">
                <i class='bx bx-loader-alt bx-spin'></i>
            </div>
        `;

    const response = await fetch(`/api/details/${type}/${id}`);
    const data = await response.json();
    // console.log(data)

    details.innerHTML = `
            <div class="details-item">
                <p class="details-title">Name</p>
                <p class="details-value">${data.filename}</p>
            </div>
            <div class="details-item">
                <p class="details-title">Description</p>
                <p class="details-value">${data.description}</p>
            </div>
            <div class="details-item">
                <p class="details-title">Type</p>
                <p class="details-value">${data.file_type}</p>
            </div>
            <div class="details-item">
                <p class="details-title">Size</p>
                <p class="details-value">${data.size_simple}</p>
            </div>
            <div class="details-item">
                <p class="details-title">Date</p>
                <p class="details-value">Date uploaded: ${data.date}</p>
                <p class="details-value">Date updated: ${data.date_updated}</p>
            </div>
        `;
}

function updateDetailsOptions(id) {
    const options = document.querySelector('.details-body-options-inner');
    fileOptionView.setAttribute('value', id);
    fileOptionCopy.setAttribute('value', id);
    fileOptionMove.setAttribute('value', id);
    fileOptionDownload.setAttribute('value', id);
    fileOptionShare.setAttribute('value', id);
    fileOptionDelete.setAttribute('value', id);

    options.classList.add("active");
}

//STATS
const stats = document.querySelector('.account-stats-body-inner');

const showStats = async () => {
    //loading animation
    stats.innerHTML = `
            <div class="loading">
                <i class='bx bx-loader-alt bx-spin'></i>
            </div>
        `;

    //fetch stats via post request
    fetch('/stats', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    })
        .then(response => response.json())
        .then(data => {
            stats.innerHTML = `
            <div class="details-item">
                <p class="details-title">Total files</p>
                <p class="details-value">${data.file_number} Files</p>
            </div>
            <div class="details-item">
                <p class="details-title">Total size</p>
                <p class="details-value">${data.file_size}</p>
            </div>
            `
        })
        .catch(error => {
            console.error('Error:', error);
        });

}

//OPTIONS
const fileOptionView = document.querySelector('.details-view');
const fileOptionCopy = document.querySelector('.details-copy');
const fileOptionMove = document.querySelector('.details-move');
const fileOptionDownload = document.querySelector('.details-download');
const fileOptionShare = document.querySelector('.details-share');
const fileOptionDelete = document.querySelector('.details-delete');

const folderOptionsModal = document.querySelector('.details-options-modal');
const folderOptionsModalOverlay = document.querySelector('.details-options-modal-overlay');
const folderOptionModalClose = document.querySelector('.details-options-modal-header .close-btn');

const contextMenu = document.querySelector('.context-menu');
const contextMenuView = document.querySelector('.context-view');
const contextMenuCopy = document.querySelector('.context-copy');
const contextMenuMove = document.querySelector('.context-move');
const contextMenuDownload = document.querySelector('.context-download');
const contextMenuShare = document.querySelector('.context-share');
const contextMenuDelete = document.querySelector('.context-delete');

const folderContextMenu = document.querySelector('.folder-context-menu');
const folderContextMenuView = document.querySelector('.folder-context-view');
const folderContextMenuMove = document.querySelector('.folder-context-move');
const folderContextMenuRename = document.querySelector('.folder-context-rename');
const folderContextMenuDelete = document.querySelector('.folder-context-delete');


function updateDots() {
    const recentOptionsDots = document.querySelectorAll('.recent-options');
    const fileOptionsDots = document.querySelectorAll('.file-options');
    const folderOptionsDots = document.querySelectorAll('.folder-options');

    //recent options
    recentOptionsDots.forEach(dot => {
        dot.addEventListener('click', (e) => {
            e.stopPropagation();
            const id = e.target.getAttribute('value');
            showContextMenu(e.pageX, e.pageY, id);
        });
    });

    //file options
    fileOptionsDots.forEach(dot => {
        dot.addEventListener('click', (e) => {
            e.stopPropagation();
            const id = e.target.getAttribute('value');
            showContextMenu(e.pageX, e.pageY, id);
        });
    });
}

function updateFolderDots() {
    const folderOptionsDots = document.querySelectorAll('.folder-options');


    //folder options
    folderOptionsDots.forEach(dot => {
        dot.addEventListener('click', (e) => {
            e.stopPropagation();
            const id = e.target.getAttribute('value');
            showFolderContextMenu(e.pageX, e.pageY, id);
        });
    });
}


folderOptionsModalOverlay.addEventListener('click', () => {
        hideOptionsModal();
        hidefolderView();
    }
);

folderOptionModalClose.addEventListener('click', () => {
        hideOptionsModal();

    }
);

function hideOptionsModal() {
    folderOptionsModalOverlay.classList.remove('active');
    folderOptionsModal.classList.remove('active');
}

function showContextMenu(x, y, id) {
    // spawn a context menu off the screen
    contextMenu.style.top = `-1000px`;
    contextMenu.style.left = `-1000px`;
    contextMenu.classList.add('active');

    const width = window.innerWidth;
    const height = window.innerHeight;

    const contextMenuWidth = contextMenu.offsetWidth;
    const contextMenuHeight = contextMenu.offsetHeight;

    if (x + contextMenuWidth > width) {
        x = width - contextMenuWidth - 20;
    }
    if (y + contextMenuHeight > height) {
        y = height - contextMenuHeight - 20;
    }

    contextMenu.style.top = `${y - 45}px`;
    contextMenu.style.left = `${x + 5}px`;

    updateContextMenuValues(id);
}

function showFolderContextMenu(x, y, id) {
    // spawn a context menu off the screen
    folderContextMenu.style.top = `-1000px`;
    folderContextMenu.style.left = `-1000px`;
    folderContextMenu.classList.add('active');

    const width = window.innerWidth;
    const height = window.innerHeight;

    const folderContextMenuWidth = folderContextMenu.offsetWidth;
    const folderContextMenuHeight = folderContextMenu.offsetHeight;

    if (x + folderContextMenuWidth > width) {
        x = width - folderContextMenuWidth - 20;
    }
    if (y + folderContextMenuHeight > height) {
        y = height - folderContextMenuHeight - 20;
    }

    folderContextMenu.style.top = `${y - 45}px`;
    folderContextMenu.style.left = `${x + 5}px`;

    updateFolderContextMenuValues(id);
}

function hideFolderContextMenu() {
    folderContextMenu.classList.remove('active');
}


function updateContextMenuValues(id) {
    contextMenuView.setAttribute('value', id);
    contextMenuCopy.setAttribute('value', id);
    contextMenuMove.setAttribute('value', id);
    contextMenuDownload.setAttribute('value', id);
    contextMenuShare.setAttribute('value', id);
    contextMenuDelete.setAttribute('value', id);
}

function updateFolderContextMenuValues(id) {
    folderContextMenuView.setAttribute('value', id);
    folderContextMenuMove.setAttribute('value', id);
    folderContextMenuRename.setAttribute('value', id);
    folderContextMenuDelete.setAttribute('value', id);
}

function hideContextMenu() {
    contextMenu.classList.remove('active');
}

//EVENTS
//context menu
window.addEventListener('click', (e) => {
    hideContextMenu();
    hideFolderContextMenu();
});

//right click
window.addEventListener('contextmenu', (e) => {
    e.preventDefault();
    //Files
    if (e.target.matches('.file-item') || e.target.matches('.file-item *')) {
        // get id
        const id = e.target.closest('.file-item').getAttribute('value');

        //show context menu
        showContextMenu(e.pageX, e.pageY, id);
    }
    ;
    //Recents
    if (e.target.matches('.recent-item') || e.target.matches('.recent-item *')) {
        //get id
        const id = e.target.closest('.recent-item').getAttribute('value');

        //show context menu
        showContextMenu(e.pageX, e.pageY, id);
    }
    ;

    //Folders
    if (e.target.matches('.folder-item') || e.target.matches('.folder-item *')) {
        //get id
        const id = e.target.closest('.folder-item').getAttribute('value');

        //show context menu
        showFolderContextMenu(e.pageX, e.pageY, id);
    }
    ;

});

//folder option buttons
const folderViewContainer = document.querySelector('.folder-view');
const folderViewContainerClose = document.querySelector('.folder-view-header-close');
const folderViewName = document.querySelector('.folder-view-name');

//view
folderContextMenuView.addEventListener('click', () => {
    const id = folderContextMenuView.getAttribute('value');
    const folderName = document.querySelector(`.folder-item[value="${id}"] .folder-name`).innerHTML;
    folderViewName.innerHTML = folderName;
    showfolderView(id);
});

folderViewContainerClose.addEventListener('click', () => {
    hidefolderView();
}
);
function showfolderView(id) {

folderOptionsModalOverlay.classList.add('active');
folderViewContainer.classList.add('active');
}

function hidefolderView() {
    folderOptionsModalOverlay.classList.remove('active');
    folderViewContainer.classList.remove('active');
}


//file option buttons
//view
fileOptionView.addEventListener('click', () => {
    const id = fileOptionView.getAttribute('value');
    window.location.href = `/view/${id}`;
});

contextMenuView.addEventListener('click', () => {
    const id = contextMenuView.getAttribute('value');
    window.location.href = `/view/${id}`;
});


function showOptionsModal(activity) {
    folderOptionsModalOverlay.classList.add('active');
    folderOptionsModal.classList.add('active');
}

//init
renderFolders();
renderRecents();
sortFiles();
showStats();
