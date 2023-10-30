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

    });

}


//DETAILS
const details = document.querySelector('.details-body-inner');

const showDetails = async (id, type) => {
    const options = document.querySelector('.details-body-options-inner');
    options.classList.add("active")
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
const fileOptionCopy = document.querySelector('.details-copy');
const fileOptionMove = document.querySelector('.details-move');
const fileOptionDownload = document.querySelector('.details-download');
const fileOptionShare = document.querySelector('.details-share');
const fileOptionDelete = document.querySelector('.details-delete');

const folderOptionsModal = document.querySelector('.details-options-modal');
const folderOptionsModalOverlay = document.querySelector('.details-options-modal-overlay');
const folderOptionModalClose = document.querySelector('.details-options-modal-header .close-btn');

folderOptionsModalOverlay.addEventListener('click', () => {
    hideOptionsModal()
}
);

folderOptionModalClose.addEventListener('click', () => {
   hideOptionsModal()
}
);

function hideOptionsModal() {
    folderOptionsModalOverlay.classList.remove('active');
    folderOptionsModal.classList.remove('active');
}








//init
renderFolders();
renderRecents();
sortFiles();
showStats();
