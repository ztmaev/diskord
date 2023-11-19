// RECENTS
const recentsList = document.querySelector('.recents-list');
const mainRecentsLoading = document.querySelector('.recents-loader');

const getRecents = async () => {
    const response = await fetch('/api/recents');
    const data = await response.json();
    return data;
}

const renderRecents = async () => {
    //loading animation
    mainRecentsLoading.innerHTML = `
            <div class="loading">
                <i class='bx bx-loader-alt bx-spin'></i>
            </div>
        `;
    const recents = await getRecents();
    recentsList.innerHTML = '';
    mainRecentsLoading.innerHTML = '';

    if (recents.length === 0) {
        mainRecentsLoading.innerHTML = `
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
        recentItem.setAttribute('name', recent.filename)
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
                <i class="bx bx-dots-vertical" value="${recent.id}" name="${recent.filename}"></i>
                </div>
            `;
        recentsList.appendChild(recentItem);

        // add click and dblclick events
        recentItem.addEventListener('click', () => {
            // remove selected from all files
            clearSelected();

            recentItem.classList.toggle('selected');
            showDetails(recent.id, type = 'file', name = recent.filename);
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
const mainFoldersLoading = document.querySelector('.folders-loader');

const getFolders = async () => {
    const response = await fetch('/api/folders');
    const data = await response.json();
    return data;
}

const renderFolders = async () => {
    //loading animation
    mainFoldersLoading.innerHTML = `
            <div class="loading">
                <i class='bx bx-loader-alt bx-spin'></i>
            </div>
        `;
    const folders = await getFolders();
    mainFoldersLoading.innerHTML = '';
    foldersList.innerHTML = '';

    if (folders.length === 0) {
        mainFoldersLoading.innerHTML = `
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
        folderItem.setAttribute('name', folder.name);
        folderItem.innerHTML = `
                <div class="folder-icon">
                    <i class='bx bxs-folder'></i>
                </div>
                <div class="folder-name">
                    ${folder.name}
                </div>
                <div class="folder-options">
                <i class="bx bx-dots-vertical" value="${folder.dir_id}" name="${folder.name}"></i>
                </div>
            `;
        foldersList.appendChild(folderItem);

        // add click and dblclick events
        folderItem.addEventListener('click', () => {
                // remove selected from all files
                clearSelected();

                folderItem.classList.toggle('selected');
                showDetails(folder.dir_id, type = 'folder', folderName = folder.name);
            }
        );

        folderItem.addEventListener('dblclick', () => {
                const id = folderItem.getAttribute('value');
                const folderName = document.querySelector(`.folder-item[value="${id}"] .folder-name`).innerHTML;

                showfolderView(folderName, id);

            }
        );

        updateFolderDots();
    });

}

//FILES
// sort btns
const filesList = document.querySelector('.files-subgroups .files-list');
const mainFilesLoading = document.querySelector('.files-loader');
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
    mainFilesLoading.innerHTML = `
            <div class="loading">
                <i class='bx bx-loader-alt bx-spin'></i>
            </div>
        `;
    const files = await fetchFiles();
    mainFilesLoading.innerHTML = '';
    filesList.innerHTML = '';

    if (files.length === 0) {
        mainFilesLoading.innerHTML = `
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
        fileItem.setAttribute('name', file.filename)
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
                <i class="bx bx-dots-vertical" value="${file.id}" name="${file.filename}"></i>
                </div>
            `;
        filesList.appendChild(fileItem);

        // add click and dblclick events
        fileItem.addEventListener('click', () => {
            // remove selected from all files
            clearSelected();

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

const showDetails = async (id, type, name = null) => {
    if (type === 'file') {
        updateDetailsOptions(id, name);
    }
    if (type === 'folder') {
        updateDirDetailsOptions(id, name)
    }


    //loading animation
    details.innerHTML = `
            <div class="loading">
                <i class='bx bx-loader-alt bx-spin'></i>
            </div>
        `;

    const response = await fetch(`/api/details/${type}/${id}`);
    const data = await response.json();
    // console.log(data)

    if (type === 'file') {
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
    } else if (type === 'folder') {
        details.innerHTML = `
            <div class="details-item">
                <p class="details-title">Name</p>
                <p class="details-value">${data.name}</p>
            </div>
            <div class="details-item">
                <p class="details-title">Description</p>
                <p class="details-value">${data.description}</p>
            </div>
            <div class="details-item">
            <p class="details-title">Stats</p>
                <p class="details-value">Files: ${data.file_number}</p>
                <p class="details-value">Subfolders: ${data.dir_number}</p>
                <p class="details-value">Size: ${data.size}</p>
            </div>
            
            <div class="details-item">
                <p class="details-title">Date</p>
                <p class="details-value">Date created: ${data.date}</p>
                <p class="details-value">Date updated: ${data.date_updated}</p>
            </div>
        `;
    }
}

const resetDetails = () => {
    details.innerHTML = '';

    // remove options bar
    const options = document.querySelector('.details-body-options-inner');
    const folderOptions = document.querySelector('.details-body-folder-options-inner');
    if (options) {
        options.classList.remove("active");
    }
    if (folderOptions) {
        folderOptions.classList.remove("active");
    }

    const detailsEmpty = document.createElement('div');
    detailsEmpty.classList.add('details-body-empty');
    detailsEmpty.innerHTML = `
            <i class="bx bx-file-find"></i>
            <p>Select a file or folder to view details</p>
        `;
    details.appendChild(detailsEmpty);

}

function updateDetailsOptions(id, name) {
    const folderOptions = document.querySelector('.details-body-folder-options-inner');
    if (folderOptions) {
        folderOptions.classList.remove("active");
    }

    const options = document.querySelector('.details-body-options-inner');
    fileOptionView.setAttribute('value', id);
    fileOptionView.setAttribute('name', name);
    fileOptionCopy.setAttribute('value', id);
    fileOptionCopy.setAttribute('name', name);
    fileOptionMove.setAttribute('value', id);
    fileOptionMove.setAttribute('name', name);
    fileOptionDownload.setAttribute('value', id);
    fileOptionDownload.setAttribute('name', name);
    fileOptionRename.setAttribute('value', id);
    fileOptionRename.setAttribute('name', name);
    fileOptionShare.setAttribute('value', id);
    fileOptionShare.setAttribute('name', name);
    fileOptionDelete.setAttribute('value', id);
    fileOptionDelete.setAttribute('name', name);

    options.classList.add("active");
}

function clearSelected() {
    const selectedFiles = document.querySelectorAll('.file-item.selected');
    const selectedRecents = document.querySelectorAll('.recent-item.selected');
    const selectedFolders = document.querySelectorAll('.folder-item.selected');

    selectedFiles.forEach(file => {
            file.classList.remove('selected');
        }
    );
    selectedRecents.forEach(recent => {
            recent.classList.remove('selected');
        }
    );
    selectedFolders.forEach(folder => {
            folder.classList.remove('selected');
        }
    );
}

function updateDirDetailsOptions(id, folderName = null) {
    const fileOptions = document.querySelector('.details-body-options-inner');
    if (fileOptions) {
        fileOptions.classList.remove("active");
    }

    clearSelected();

    //add selected to folder
    const folder = document.querySelector(`.folder-item[value="${id}"]`);
    folder.classList.add('selected');


    const options = document.querySelector('.details-body-folder-options-inner');

    folderOptionView.setAttribute('value', id);
    folderOptionView.setAttribute('name', folderName);
    folderOptionMove.setAttribute('value', id);
    folderOptionMove.setAttribute('name', folderName);
    folderOptionRename.setAttribute('value', id);
    folderOptionRename.setAttribute('name', folderName);
    folderOptionDelete.setAttribute('value', id);
    folderOptionDelete.setAttribute('name', folderName);

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
const fileOptionRename = document.querySelector('.details-rename');
const fileOptionShare = document.querySelector('.details-share');
const fileOptionDelete = document.querySelector('.details-delete');

const folderOptionsModal = document.querySelector('.details-options-modal');
const folderOptionsModalOverlay = document.querySelector('.details-options-modal-overlay');
const folderOptionModalClose = document.querySelector('.details-options-modal-header .close-btn');

const contextMenu = document.querySelector('.context-menu');
const contextMenuView = document.querySelector('.context-view');
const contextMenuCopy = document.querySelector('.context-copy');
const contextMenuMove = document.querySelector('.context-move');
const contextMenuRename = document.querySelector('.context-rename');
const contextMenuDownload = document.querySelector('.context-download');
const contextMenuShare = document.querySelector('.context-share');
const contextMenuDelete = document.querySelector('.context-delete');

const folderContextMenu = document.querySelector('.folder-context-menu');
const folderContextNewdir = document.querySelector('.folder-context-new-folder');
const folderContextMenuView = document.querySelector('.folder-context-view');
const folderContextMenuMove = document.querySelector('.folder-context-move');
const folderContextMenuRename = document.querySelector('.folder-context-rename');
const folderContextMenuDelete = document.querySelector('.folder-context-delete');

const generalContextMenu = document.querySelector('.general-context-menu');
const generalContextMenuNewdir = document.querySelector('.general-context-new-folder');
const generalContextMenuFileUpload = document.querySelector('.general-context-file-upload');
const generalContextMenuDirUpload = document.querySelector('.general-context-folder-upload');

const folderOptionView = document.querySelector('.folder-details-view');
const folderOptionMove = document.querySelector('.folder-details-move');
const folderOptionRename = document.querySelector('.folder-details-rename');
const folderOptionDelete = document.querySelector('.folder-details-delete');

function updateDots() {
    const recentOptionsDots = document.querySelectorAll('.recent-options');
    const fileOptionsDots = document.querySelectorAll('.file-options');
    const folderOptionsDots = document.querySelectorAll('.folder-options');

    //recent options
    recentOptionsDots.forEach(dot => {
        dot.addEventListener('click', (e) => {
            e.stopPropagation();
            const id = e.target.getAttribute('value');
            const name = e.target.getAttribute('name');

            //select
            clearSelected();
            e.target.closest('.recent-item').classList.add('selected');

            //details
            showDetails(id, type = 'file');

            showContextMenu(e.pageX, e.pageY, id, name);
        });
    });

    //file options
    fileOptionsDots.forEach(dot => {
        dot.addEventListener('click', (e) => {
            e.stopPropagation();
            const id = e.target.getAttribute('value');
            const name = e.target.getAttribute('name');

            //select
            clearSelected();
            e.target.closest('.file-item').classList.add('selected');

            //details
            showDetails(id, type = 'file');

            showContextMenu(e.pageX, e.pageY, id, name);
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
            const folderName = e.target.getAttribute('name');

            //select
            clearSelected();
            e.target.closest('.folder-item').classList.add('selected');

            //details
            showDetails(id, type = 'folder', folderName);

            showFolderContextMenu(e.pageX, e.pageY, id, folderName);
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

function enableScroll() {
    document.querySelector('.body-section-files-inner').style.overflowY = 'scroll';
    // enable pointer events
    document.querySelector('*').style.pointerEvents = 'all';

}

function disableScroll() {
    document.querySelector('.body-section-files-inner').style.overflowY = 'hidden';
    // disable pointer events
    document.querySelector('*').style.pointerEvents = 'none';
    // enable pointer events for context menus
    document.querySelector('.context-menu').style.pointerEvents = 'all';
    document.querySelector('.folder-context-menu').style.pointerEvents = 'all';
    document.querySelector('.general-context-menu').style.pointerEvents = 'all';

}


function showGeneralContextMenu(x, y) {
    // hide context menu if already shown
    hideContextMenu();
    hideFolderContextMenu();
    hideGeneralContextMenu();

    // spawn a context menu off the screen
    generalContextMenu.style.top = `-1000px`;
    generalContextMenu.style.left = `-1000px`;
    generalContextMenu.classList.add('active');


    const width = window.innerWidth;
    const height = window.innerHeight;

    const generalContextMenuWidth = generalContextMenu.offsetWidth;
    const generalContextMenuHeight = generalContextMenu.offsetHeight;

    if (x + generalContextMenuWidth > width) {
        x = width - generalContextMenuWidth - 10;
    }
    if (y + generalContextMenuHeight > height) {
        y = height - generalContextMenuHeight - 10;
    }

    generalContextMenu.style.top = `${y - 45}px`;
    generalContextMenu.style.left = `${x + 5}px`;
}

function hideGeneralContextMenu() {
    generalContextMenu.classList.remove('active');
}

function showContextMenu(x, y, id, name) {
    // hide context menu if already shown
    hideContextMenu();
    hideFolderContextMenu();
    hideGeneralContextMenu();

    // spawn a context menu off the screen
    contextMenu.style.top = `-1000px`;
    contextMenu.style.left = `-1000px`;
    contextMenu.classList.add('active');


    const width = window.innerWidth;
    const height = window.innerHeight;

    const contextMenuWidth = contextMenu.offsetWidth;
    const contextMenuHeight = contextMenu.offsetHeight;

    if (x + contextMenuWidth > width) {
        x = width - contextMenuWidth - 10;
    }
    if (y + contextMenuHeight > height) {
        y = height - contextMenuHeight - 10;
    }

    contextMenu.style.top = `${y - 45}px`;
    contextMenu.style.left = `${x + 5}px`;

    updateContextMenuValues(id, name);
}

function showFolderContextMenu(x, y, id, folderName) {
    // hide context menu if already shown
    hideContextMenu();
    hideFolderContextMenu();
    hideGeneralContextMenu();

    // spawn a context menu off the screen
    folderContextMenu.style.top = `-1000px`;
    folderContextMenu.style.left = `-1000px`;
    folderContextMenu.classList.add('active');


    const width = window.innerWidth;
    const height = window.innerHeight;

    const folderContextMenuWidth = folderContextMenu.offsetWidth;
    const folderContextMenuHeight = folderContextMenu.offsetHeight;

    if (x + folderContextMenuWidth > width) {
        x = width - folderContextMenuWidth - 10;
    }
    if (y + folderContextMenuHeight > height) {
        y = height - folderContextMenuHeight - 10;
    }

    folderContextMenu.style.top = `${y - 45}px`;
    folderContextMenu.style.left = `${x + 5}px`;
    //clear whitespace
    folderName = folderName.replace(/\s/g, '');
    updateFolderContextMenuValues(id, folderName);
}

function hideFolderContextMenu() {
    folderContextMenu.classList.remove('active');
}


function updateContextMenuValues(id, name) {
    contextMenuView.setAttribute('value', id);
    contextMenuView.setAttribute('name', name);
    contextMenuCopy.setAttribute('value', id);
    contextMenuCopy.setAttribute('name', name);
    contextMenuMove.setAttribute('value', id);
    contextMenuMove.setAttribute('name', name);
    contextMenuDownload.setAttribute('value', id);
    contextMenuDownload.setAttribute('name', name);
    contextMenuRename.setAttribute('value', id);
    contextMenuRename.setAttribute('name', name);
    contextMenuShare.setAttribute('value', id);
    contextMenuShare.setAttribute('name', name);
    contextMenuDelete.setAttribute('value', id);
    contextMenuDelete.setAttribute('name', name);
}

function updateFolderContextMenuValues(id, folderName) {
    folderContextNewdir.setAttribute('value', id);
    folderContextNewdir.setAttribute('name', folderName);
    folderContextMenuView.setAttribute('value', id);
    folderContextMenuView.setAttribute('name', folderName);
    folderContextMenuMove.setAttribute('value', id);
    folderContextMenuMove.setAttribute('name', folderName);
    folderContextMenuRename.setAttribute('value', id);
    folderContextMenuRename.setAttribute('name', folderName);
    folderContextMenuDelete.setAttribute('value', id);
    folderContextMenuDelete.setAttribute('name', folderName);
}

function hideContextMenu() {
    contextMenu.classList.remove('active');
}

//EVENTS
//context menu
window.addEventListener('click', (e) => {
    hideContextMenu();
    hideFolderContextMenu();
    hideGeneralContextMenu();
});

//right click
window.addEventListener('contextmenu', (e) => {
    //Files
    if (e.target.matches('.file-item') || e.target.matches('.file-item *')) {
        e.preventDefault();
        // get id
        const id = e.target.closest('.file-item').getAttribute('value');
        const name = e.target.closest('.file-item').getAttribute('name');

        //select
        clearSelected();
        e.target.closest('.file-item').classList.add('selected');

        //details
        showDetails(id, type = 'file');

        //show context menu
        showContextMenu(e.pageX, e.pageY, id, name);
    }

    //Recents
    else if (e.target.matches('.recent-item') || e.target.matches('.recent-item *')) {
        e.preventDefault();
        //get id
        const id = e.target.closest('.recent-item').getAttribute('value');
        const name = e.target.closest('.recent-item').getAttribute('name');

        //select
        clearSelected();
        e.target.closest('.recent-item').classList.add('selected');

        //details
        showDetails(id, type = 'file');

        //show context menu
        showContextMenu(e.pageX, e.pageY, id, name);
    }


    //Folders
    else if (e.target.matches('.folder-item') || e.target.matches('.folder-item *')) {
        e.preventDefault();

        //get id
        const id = e.target.closest('.folder-item').getAttribute('value');
        const folderName = document.querySelector(`.folder-item[value="${id}"] .folder-name`).innerHTML;

        //select
        clearSelected();
        e.target.closest('.folder-item').classList.add('selected');

        //details
        showDetails(id, type = 'folder', folderName);

        //show context menu
        showFolderContextMenu(e.pageX, e.pageY, id, folderName);

    } else if (e.target.matches('.folder-view-body') || e.target.matches('.folder-view-body *')) {
        e.preventDefault();

        const id = folderViewName.getAttribute('value');
        const folderName = folderViewName.getAttribute('name');

        //select
        clearSelected();
        //details
        showDetails(id, type = 'folder', folderName);

        //show context menu
        showFolderContextMenu(e.pageX, e.pageY, id, folderName);
    }

    //General
    else if (e.target.matches('.body-section-files') || e.target.matches('.body-section-files *')) {
        e.preventDefault();
        showGeneralContextMenu(e.pageX, e.pageY);
    } else {
        hideGeneralContextMenu()
        hideContextMenu()
        hideFolderContextMenu()
    }

});

//folder option buttons
const folderViewContainer = document.querySelector('.folder-view');
const folderViewContainerClose = document.querySelector('.folder-view-header-close');
const folderViewName = document.querySelector('.folder-view-name');
const folderViewParentPath = document.querySelector('.folder-view-header-title-inner-path-old');
const folderViewContainerIcon = document.querySelector('.folder-view-header-title-header-snippet i:first-child');
const folderViewContainerTitle = document.querySelector('.folder-view-header-title-header-snippet p');

folderViewContainerIcon.addEventListener('click', () => {
        hidefolderView();
    }
);

folderViewContainerTitle.addEventListener('click', () => {
        hidefolderView();
    }
);
folderViewContainerClose.addEventListener('click', () => {
        hidefolderView();
    }
);

const updateFolderViewName = (name, id) => {
    folderViewName.innerHTML = name;
    folderViewName.setAttribute('value', id);
    folderViewName.setAttribute('name', name);
}

function showfolderView(name, id) {
    //hierarchy
    //check if folderview is open
    if (folderViewContainer.classList.contains('active')) {
        // console.log('active');
        // console.log(folderViewName);
        //get old path
        const oldPathValue = folderViewName.getAttribute('value');
        const oldPathName = folderViewName.innerHTML;

        //create new item and append to old path
        const oldPath = document.createElement('div');
        oldPath.classList.add('folder-view-header-title-inner-path-old-item');
        oldPath.setAttribute('value', oldPathValue);
        oldPath.innerHTML = `
            <p value="${id}">${oldPathName}</p>
            <i class='bx bxs-chevron-right'></i>
        `;
        folderViewParentPath.appendChild(oldPath);
        folderViewParentPath.classList.add('active');


        // console.log(oldPath);


    } else {
        //clear hierarchy
        folderViewParentPath.innerHTML = '';

    }
    // folderOptionsModalOverlay.classList.add('active');
    folderViewContainer.classList.add('active');
    updateFolderViewName(name, id);
    populateFolderView(id);
    updateOldPathsLinks();
}

function updateOldPathsLinks() {
    const oldPaths = document.querySelectorAll('.folder-view-header-title-inner-path-old-item p');
    oldPaths.forEach(path => {
        path.addEventListener('click', () => {
            const id = path.getAttribute('value');
            const name = path.innerHTML;

            showfolderView(name, id);
        });
    });
}

function hidefolderView() {
    // folderOptionsModalOverlay.classList.remove('active');
    folderViewContainer.classList.remove('active');
}


async function getFolderContents(id) {
    const response = await fetch(`/api/folder/${id}`);
    const data = await response.json();
    return data;
}

function populateFolderView(id) {
    const folderList = document.querySelector('.folder-view-section-folders .folder-list');
    const foldersLoading = document.querySelector('.folder-list-loading')
    const filesLoading = document.querySelector('.files-list-loading')
    const fileList = document.querySelector('.folder-view-section-files .files-list');

    folderInfo = getFolderContents(id);
    folderList.innerHTML = ''
    foldersLoading.innerHTML = `
            <div class="loading">
                <i class='bx bx-loader-alt bx-spin'></i>
            </div>
        `;

    //folders
    folderListContent = folderInfo.then(data => {
            foldersLoading.innerHTML = ''
            folderList.innerHTML = '';

            if (data.folders.length === 0) {
                foldersLoading.innerHTML = `
                <div class="loading">
                    <p>No folders found</p>
                </div>
            `;
            }
            data.folders.forEach(folder => {
                const folderItem = document.createElement('div');
                folderItem.classList.add('folder-item');
                folderItem.setAttribute('value', folder.dir_id);
                folderItem.setAttribute('name', folder.name);
                folderItem.innerHTML = `
                <div class="folder-icon">
                    <i class='bx bxs-folder'></i>
                </div>
                <div class="folder-name">
                    ${folder.name}
                </div>
                <div class="folder-options">
                <i class="bx bx-dots-vertical" value="${folder.dir_id}" name="${folder.name}"></i>
                </div>
            `;
                folderList.appendChild(folderItem);

                // add click and dblclick events
                folderItem.addEventListener('click', () => {
                        // remove selected from all files
                        clearSelected();

                        folderItem.classList.toggle('selected');
                        showDetails(folder.dir_id, type = 'folder', folderName = folder.name);
                    }
                );

                folderItem.addEventListener('dblclick', () => {
                        const id = folderItem.getAttribute('value');
                        const folderName = document.querySelector(`.folder-item[value="${id}"] .folder-name`).innerHTML;

                        showfolderView(folderName, id);

                    }
                );

                updateFolderDots();
            });
        }
    );

    //files
    fileList.innerHTML = '';
    filesLoading.innerHTML = `
            <div class="loading">
                <i class='bx bx-loader-alt bx-spin'></i>
            </div>
        `;


    fileListContent = folderInfo.then(data => {
            fileList.innerHTML = '';
            filesLoading.innerHTML = '';


            if (data.files.length === 0) {
                filesLoading.innerHTML = `
                <div class="loading">
                    <p>No files found</p>
                </div>
            `;
            }
            data.files.forEach(file => {
                const fileItem = document.createElement('div');
                fileItem.classList.add('file-item');
                fileItem.setAttribute('value', file.id);
                fileItem.setAttribute('name', file.filename)
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
                fileList.appendChild(fileItem);

                // add click and dblclick events
                fileItem.addEventListener('click', () => {
                    // remove selected from all files
                    clearSelected();

                    fileItem.classList.toggle('selected');
                    showDetails(file.id, type = 'file');
                });

                fileItem.addEventListener('dblclick', () => {
                    window.location.href = `/view/${file.id}`;
                });

                updateDots();

            });
        }
    );

}

const notifActivityClose = document.querySelector('.notifs-container-header-close');
const notifActivityContainer = document.querySelector('.notifs-container');
const downloadsList = document.querySelector('.notifs-processes-downloads');
notifActivityClose.addEventListener('click', () => {
        hideNotifActivity();
    }
);

function showNotifActivity() {
    notifActivityContainer.classList.add('active');
}

function hideNotifActivity() {
    notifActivityContainer.classList.remove('active');
}

//Notifs
const notifsContainer = document.querySelector('.notifs-popup .notifs-list');

function showNotif(state, type, message) {
    // console.log(state, type, message);
    if (state == 'success') {
        //create notif item
        const notifItem = document.createElement('div');
        notifItem.classList.add('notif-item');
        notifItem.classList.add('success');

        //get icon
        let typeIcon = '';
        if (type == 'file') {
            typeIcon = '<i class="bx bxs-file"></i>';
        } else if (type == 'account') {
            typeIcon = '<i class="bx bxs-user"></i>';
        } else if (type == 'system') {
            typeIcon = '<i class="bx bxs-cog"></i>';
        } else if (type == 'security') {
            typeIcon = '<i class="bx bxs-lock"></i>';
        }

        notifItem.innerHTML = `
            <div class="notif-icon">
                ${typeIcon}
            </div>
            <div class="notif-body">
                <p class="notif-message">${message}</p>
            </div>
            <div class="notif-close">
                <i class='bx bx-x'></i>
            </div>
        `;
        notifsContainer.appendChild(notifItem);
        updateNotifClose();

        //remove notif after 5 seconds
        setTimeout(() => {
            notifItem.remove();
        }, 100000);
    } else {
        const notifItem = document.createElement('div');
        notifItem.classList.add('notif-item');
        notifItem.classList.add('error');

        //icon
        let typeIcon = '<i class="bx bxs-error"></i>';

        notifItem.innerHTML = `
            <div class="notif-icon">
                ${typeIcon}
            </div>
            <div class="notif-body">
                <p class="notif-message">${message}</p>
            </div>
            <div class="notif-close">
                <i class='bx bx-x'></i>
            </div>
        `;
        notifsContainer.appendChild(notifItem);
        updateNotifClose();

        //remove notif after 5 seconds
        setTimeout(() => {
            notifItem.remove();
        }, 5000);

    }

}

//notif close
function updateNotifClose() {
    const notifCloseBtns = document.querySelectorAll('.notif-close');
    notifCloseBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                btn.closest('.notif-item').remove();
            });
        }
    );
}


//File submissions
//deletefile
function submitFormFileDelete(event) {
    event.preventDefault();
    const id = document.getElementById('file-delete-id').value;
    const name = document.getElementById('file-delete-name').value;
    //delete file
    console.log(id, name);
    deleteFile(id, name);
}

function deleteFile(id, name) {
    hideOptionsModal();
    fetch('/delete_file', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            deleteFileID: id,
        })
    })
        .then(response => {
            if (response.status === 200) {
                showNotif('success', 'file', `File ${name} deleted`);
                //remove file from list
                const files = document.querySelectorAll(`.file-item[value="${id}"]`);
                files.forEach(file => {
                    file.remove();
                });
                const recents = document.querySelectorAll(`.recent-item[value="${id}"]`);
                recents.forEach(recent => {
                    recent.remove();
                });

            } else {
                response.json().then(data => {
                    showNotif('error', 'file', data.message);
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

// renamefile
function submitFormFileRename(event) {
    event.preventDefault();
    const id = document.getElementById('file-rename-id').value;
    const name = document.getElementById('file-rename-new-name').value;
    renameFile(id, name);
}

function renameFile(id, name) {
    hideOptionsModal();
    fetch('/update_filename', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            fileID: id, fileName: name
        })
    })
        .then(response => {
            if (response.status === 200) {
                showNotif('success', 'file', `Renamed ${name}`);
                //update the name on the file
                const file = document.querySelectorAll(`.file-item[value="${id}"]`);
                file.forEach(file => {
                    file.querySelector('.filename').innerHTML = name;
                });
                const recent = document.querySelectorAll(`.recent-item[value="${id}"]`);
                recent.forEach(recent => {
                    recent.querySelector('.filename').innerHTML = name;
                });

            } else {
                response.json().then(data => {
                    showNotif('error', 'file', data.message);
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

// autofill and fix


//Folder submissions
function submitFormCreation(event) {
    event.preventDefault();
    const name = document.getElementById('new-folder-name').value;
    const isRoot = document.getElementById('new-folder-is-root').value
    const parentdirid = document.getElementById('new-folder-parent-id').value
    let root
    if (isRoot == 'false') {
        root = false
    } else {
        root = true
    }

    //create folder
    console.log(name, root, parentdirid);
    createFolder(name, root, parentdirid);
}

function submitFormDirDelete(event) {
    event.preventDefault();
    const id = document.getElementById('folder-delete-id').value;
    const name = document.getElementById('folder-delete-name').value;
    //delete folder
    console.log(id, name);
    deleteFolder(id, name);
}

function submitFormDirRename(event) {
    event.preventDefault();
    const id = document.getElementById('folder-rename-id').value;
    const name = document.getElementById('folder-rename-name').value;
    const newName = document.getElementById('folder-rename-new-name').value;
    //rename folder
    console.log(id, name, newName);
    renameFolder(id, name, newName);
}

function showOptionsModal(activity, id = null, type = 'file', name = null) {
    //File options
    // fileview
    if (activity == "filecopy") {
        // TODO: inpage file preview

    }

    // filedownload +
    else if (activity == "filedownload") {
        showNotifActivity();
        //create download item
        const downloadItem = document.createElement('div');
        downloadItem.classList.add('download-item');
        downloadItem.setAttribute('value', id);

        downloadItem.innerHTML = `
            <div class="download-progress">
                    <progress max="100" value="0" id="${id}-progress"></progress>
                </div>
                <div class="download-info">
                    <p class="download-info-text" id="${id}-status">Prepairing File</p>
                    <p class="download-info-percent" id="${id}-percent">0%</p>
            </div>`

        downloadsList.appendChild(downloadItem);

        //initiate download
        //make get request to /download/:id, if 200, show notif, else show error
        fetch(`/download/${id}`)
            .then(response => {
                if (response.status === 200) {
                    //get filename(/api/details/file/:id)
                    fetch(`/api/details/file/${id}`)
                        .then(response => response.json())
                        .then(data => {
                                // console.log(data);
                                const fileName = data.filename;
                                // console.log(fileName);
                                fetchProgress(id, fileName);
                            }
                        )
                        .catch(error => {
                                console.error('Error:', error);
                            }
                        );
                } else {
                    showNotifActivity();
                    // show error
                    console.log('error', response.status)
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });

        //monitor and update download progress
        const downloadProgress = document.getElementById(`${id}-progress`);
        const downloadStatus = document.getElementById(`${id}-status`);
        const downloadPercent = document.getElementById(`${id}-percent`);


        function toFullNumber(number) {
            return Math.round(number);

        }

        function updateProgress(stage, stage_percent, stage_activity, filename = null) {
            downloadStatus.innerHTML = stage_activity;
            // calculate overall percentage according to stage, stage 1 is 0-90%, stage 2 is 90-100% and stage 3 is 100%
            let overall_percentdownloadPercent = 0;
            if (stage == 1) {
                // For stage 1, the overall percentage is in the range of 0-90%
                overallPercent = (stage_percent / 100) * 90;
                downloadProgress.value = toFullNumber(overallPercent);
                downloadPercent.innerHTML = toFullNumber(overallPercent) + '%';
            } else if (stage == 2) {
                // For stage 2, the overall percentage is in the range of 90-100%
                overallPercent = 90 + (stage_percent / 100) * 10;
                downloadProgress.value = toFullNumber(overallPercent);
                downloadPercent.innerHTML = toFullNumber(overallPercent) + '%';
            } else if (stage == 3) {
                // For stage 3, the overall percentage is 100%
                overallPercent = 100;
                downloadProgress.value = toFullNumber(overallPercent);
                downloadPercent.innerHTML = toFullNumber(overallPercent) + '%';
                downloadStatus.innerHTML = 'File ready for download';
            } else if (stage == 4) {
                // For stage 4, the overall percentage is in the range of 0-90%
                downloadProgress.value = toFullNumber(stage_percent);
                downloadPercent.innerHTML = toFullNumber(stage_percent) + '%';
                downloadStatus.innerHTML = stage_activity;

                if (stage_percent == 100) {
                    downloadPercent.innerHTML = 'Downloaded';
                    // remove download item after 5 seconds
                    setTimeout(() => {
                        downloadItem.remove();
                        // if no more downloads, hide notif activity
                        if (downloadsList.innerHTML === '') {
                            hideNotifActivity();
                        }
                    }, 100);


                } else if (stage_percent == 400) {
                    downloadPercent.innerHTML = '';
                    // remove download item after 5 seconds
                    setTimeout(() => {
                        downloadItem.remove();
                        // if no more downloads, hide notif activity
                        if (downloadsList.innerHTML === '') {
                            hideNotifActivity();
                        }
                    }, 2000);

                }

            }


        }

        //monitor download progress
        function fetchProgress(id, fileName) {
            fetch('/download_progress', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    fileID: id
                })
            })
                .then(response => {
                    if (response.status === 200) {
                        response.json().then(data => {
                            // console.log(data.message);
                            // console.log(data.message)
                            const stage = data.message.split('_')[0];
                            const stage_percent = data.message.split('_')[1];
                            const stage_activity = data.message.split('_')[2];
                            updateProgress(stage, stage_percent, stage_activity, fileName);

                            if (data.message.startsWith('3_100_')) {
                                // console.log('Download completed!');
                                downloadFile('/download_file/' + id, fileName);
                            } else {
                                // If not completed, fetch progress again
                                fetchProgress(id, fileName);
                            }
                        });
                    } else {
                        response.json().then(data => {
                            // console.log(data.message);
                        });
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        }

        //download file
        function downloadFile(url, fileName) {
            const xhr = new XMLHttpRequest();
            xhr.open("GET", url, true);
            xhr.responseType = "blob";

            xhr.addEventListener("progress", (event) => {
                if (event.lengthComputable) {
                    const percentComplete = (event.loaded / event.total) * 100;
                    updateProgress(4, percentComplete, fileName, fileName);
                }
            });

            xhr.onreadystatechange = () => {
                if (xhr.readyState === 4 && xhr.status === 200) {
                    const blob = xhr.response;
                    const a = document.createElement("a");
                    const url = window.URL.createObjectURL(blob);
                    a.href = url;
                    a.download = fileName;
                    document.body.appendChild(a);
                    a.click();
                    showNotif('success', 'system', (fileName + 'downloaded successfully'));

                    window.URL.revokeObjectURL(url);

                    updateProgress(4, 100, fileName, fileName);

                    // make post request to delete file
                    fetch('/download_file_complete', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            fileID: id
                        })
                    })
                        .then(response => {
                            if (response.status === 200) {
                                response.json().then(data => {
                                    // console.log(data.message);
                                });
                            } else {
                                response.json().then(data => {
                                    // console.log(data.message);
                                });
                            }
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            updateProgress(4, 400, 'Error downloading file, please whitelist this site on your adblocker', fileName);
                        });
                }

                //errors
                xhr.onerror = () => {
                    updateProgress(4, 400, 'Error downloading file, please whitelist this site on your adblocker', fileName);
                }
            };


            xhr.send();

        }

    }

    // filecopy
    else if (activity == "filecopy") {
        // TODO:


    }
    // filemove
    else if (activity == "filemove") {
        // TODO:


    }
    // fileshare
    else if (activity == "fileshare") {
        // TODO:


    }
    // filerename
    else if (activity == "filerename") {
        console.log(activity, id, type, name);
        folderOptionsModalOverlay.classList.add('active');
        folderOptionsModal.classList.add('active');

        const detailsOptionsModalBody = document.querySelector('.details-options-modal-body');
        const fileNameForm = document.createElement('div');
        fileNameForm.classList.add('details-options-modal-body-input');
        fileNameForm.innerHTML = `
        <div>
        <p>Rename <span class="paths">/${name}</span></p>
            <form onsubmit="submitFormFileRename(event)">
                <input type="hidden" name="fileId" value="${id}" id="file-rename-id">
                <input type="hidden" name="fileName" value="${name}" id="file-rename-name">
                <input type="text" name="fileName" placeholder="File name" id="file-rename-new-name" value="${name}" required>
                <p onclick="hideOptionsModal()">Cancel</p>
                <button type="submit" class="btn btn-primary">Rename</button>
            </form>
        </div>
        `;

        detailsOptionsModalBody.innerHTML = '';
        detailsOptionsModalBody.appendChild(fileNameForm);


    }
    // filedelete
    else if (activity == "filedelete") {
        console.log(activity, id, type, name);

        folderOptionsModalOverlay.classList.add('active');
        folderOptionsModal.classList.add('active');

        const deleteForm = document.createElement('div');
        deleteForm.classList.add('details-options-modal-body-input');
        let is_root = false;
        if (name == null) {
            name = '';
            is_root = true;
        }

        deleteForm.innerHTML = `
        <div>
        <p>Are you sure you want to delete <span class="paths">/${name}</span>?</p>
        <i class='bx bxs-error'>This action cannot be undone</i>
            <form onsubmit="submitFormFileDelete(event)">
                <input type="hidden" name="fileId" value="${id}" id="file-delete-id">
                <input type="hidden" name="fileName" value="${name}" id="file-delete-name">
                <p onclick="hideOptionsModal()">Cancel</p>
                <button type="submit" class="btn btn-primary">Delete</button>
            </form>
            
        </div>
        `;
        const detailsOptionsModalBody = document.querySelector('.details-options-modal-body');
        detailsOptionsModalBody.innerHTML = '';
        detailsOptionsModalBody.appendChild(deleteForm);
    }


        // Folder options
    // Folder new folder
    else if (activity == "newdir") {
        folderOptionsModalOverlay.classList.add('active');
        folderOptionsModal.classList.add('active');

        //name form
        const detailsOptionsModalBody = document.querySelector('.details-options-modal-body');
        const folderNameForm = document.createElement('div');
        folderNameForm.classList.add('details-options-modal-body-input');
        let is_root = false;
        if (name == null) {
            name = '';
            is_root = true;
        }
        folderNameForm.innerHTML = `
        <div>
        <p>Create new folder in <span class="paths">/${name}</span></p>
            <form onsubmit="submitFormCreation(event)">
                <input type="hidden" name="parentId" value="${id}" id="new-folder-parent-id">
                <input type="hidden" name="isRoot" value="${is_root}" id="new-folder-is-root">
                <input type="text" name="folderName" placeholder="Folder name" id="new-folder-name" required>
                <p onclick="hideOptionsModal()">Cancel</p>
                <button type="submit" class="btn btn-primary">Create</button>
            </form>
        </div>
        `;

        detailsOptionsModalBody.innerHTML = '';
        detailsOptionsModalBody.appendChild(folderNameForm);


    }

    // Folder delete
    else if (activity == "dirdelete") {
        folderOptionsModalOverlay.classList.add('active');
        folderOptionsModal.classList.add('active');

        //name form
        const detailsOptionsModalBody = document.querySelector('.details-options-modal-body');
        const folderNameForm = document.createElement('div');
        folderNameForm.classList.add('details-options-modal-body-input');
        folderNameForm.innerHTML = `
        <div>
        <p>Are you sure you want to delete <span class="paths">/${name}</span>?</p>
        <p>All files and folders inside will be deleted as well</p>
        <i class='bx bxs-error'>This action cannot be undone</i>
            <form onsubmit="submitFormDirDelete(event)">
                <input type="hidden" name="dirId" value="${id}" id="folder-delete-id">
                <input type="hidden" name="dirName" value="${name}" id="folder-delete-name">
                <p onclick="hideOptionsModal()">Cancel</p>
                <button type="submit" class="btn btn-primary">Delete</button>
            </form>
        </div>
        `;

        detailsOptionsModalBody.innerHTML = '';
        detailsOptionsModalBody.appendChild(folderNameForm);

    }

    //Folder rename
    else if (activity == "dirrename") {
        folderOptionsModalOverlay.classList.add('active');
        folderOptionsModal.classList.add('active');

        const detailsOptionsModalBody = document.querySelector('.details-options-modal-body');
        const folderNameForm = document.createElement('div');
        folderNameForm.classList.add('details-options-modal-body-input');
        folderNameForm.innerHTML = `
        <div>
        <p>Rename <span class="paths">/${name}</span></p>
            <form onsubmit="submitFormDirRename(event)">
                <input type="hidden" name="dirId" value="${id}" id="folder-rename-id">
                <input type="hidden" name="dirName" value="${name}" id="folder-rename-name">
                <input type="text" name="folderName" placeholder="Folder name" id="folder-rename-new-name" required>
                <p onclick="hideOptionsModal()">Cancel</p>
                <button type="submit" class="btn btn-primary">Rename</button>
            </form>
        </div>
        `;

        detailsOptionsModalBody.innerHTML = '';
        detailsOptionsModalBody.appendChild(folderNameForm);


    }

    // Folder move
    else if (activity == "dirmove") {
        folderOptionsModalOverlay.classList.add('active');
        folderOptionsModal.classList.add('active');

        //name form
        const detailsOptionsModalBody = document.querySelector('.details-options-modal-body');
        const folderNameForm = document.createElement('div');
        folderNameForm.classList.add('details-options-modal-body-input');
        folderNameForm.innerHTML = `
        <div class="options-modal-dir-move">
        <p>Choose a folder to move <span class="folder-move-data" name="${name}" value="${id}">/${name}</span></p>
        <div class="folder-list-paths">
            <div class="folder-list-up">
                <i class='bx bx-home'></i>
            </div>
            <p class="paths">/root</p>
            <div class="folder-list-paths-inner"></div>
        </div>
            <div class="folder-list">
                <div class="loading">
                    <i class='bx bx-loader-alt bx-spin'></i>
                    <p>Fetching folders</p>
                </div>
            </div>
        </div>
        `;

        detailsOptionsModalBody.innerHTML = '';
        detailsOptionsModalBody.appendChild(folderNameForm);

        // fetch folders
        const folderStructure = getDirStructure();
        const folderPaths = document.querySelector('.options-modal-dir-move .folder-list-paths-inner');
        const folderList = document.querySelector('.options-modal-dir-move .folder-list');
        const folderListUp = document.querySelector('.options-modal-dir-move .folder-list-up');

        folderListUp.addEventListener('click', () => {
            // Get the current folder path
            const currentPath = folderPaths.textContent;

            // If the current path is not the root, navigate up one level
            if (currentPath !== '/root') {
                const newPath = currentPath.substring(0, currentPath.lastIndexOf('/'));
                folderPaths.textContent = newPath;

                // Reload the folders for the new path
                reloadFolders(newPath);
            }
        });

        function reloadFolders(path) {
            //loading
            folderList.innerHTML = `
            <div class="loading">
                <i class='bx bx-loader-alt bx-spin'></i>
                <p>Fetching folders</p>
            </div>
        `;

            // Fetch folders based on the provided path
            const updatedFolderStructure = getDirStructure(path);

            // Update the folder list with the new data
            updatedFolderStructure.then(data => {
                folderList.innerHTML = '';

                if (data.length === 0) {
                    folderList.innerHTML = `
                <div class="loading">
                    <p>No folders found</p>
                </div>
            `;
                }

                data.forEach(folder => {
                    const folderItem = document.createElement('div');
                    folderItem.classList.add('dirs-folder-item');
                    folderItem.setAttribute('value', folder.dir_id);
                    folderItem.setAttribute('name', folder.name);
                    folderItem.innerHTML = `
                        <div class="folder-icon">
                            <i class='bx bxs-folder'></i>
                        </div>
                        <div class="folder-name">
                            ${folder.name}
                        </div>
                    `;
                    folderList.appendChild(folderItem);

                    // add click event to select folder and double-click to load the folder's subfolders
                    folderItem.addEventListener('click', () => {
                        // remove selected from all files
                        clearSelected();
                        folderItem.classList.toggle('selected');
                    });

                    folderItem.addEventListener('dblclick', () => {
                        loadSubfolders(folderItem, data);
                    });
                });
            });
        }

        // list folders
        folderStructure.then(data => {
            folderList.innerHTML = '';

            if (data.length === 0) {
                folderList.innerHTML = `
            <div class="loading">
                <p>No folders found</p>
            </div>
        `;
            }

            data.forEach(folder => {
                const folderItem = document.createElement('div');
                folderItem.classList.add('dirs-folder-item');
                folderItem.setAttribute('value', folder.dir_id);
                folderItem.setAttribute('name', folder.name);
                folderItem.innerHTML = `
                    <div class="folder-icon">
                        <i class='bx bxs-folder'></i>
                    </div>
                    <div class="folder-name">
                        ${folder.name}
                    </div>
                `;
                folderList.appendChild(folderItem);

                // add click event to select folder and double-click to load the folder's subfolders
                folderItem.addEventListener('click', () => {
                    // remove selected from all files
                    clearSelected();
                    folderItem.classList.toggle('selected');
                });

                folderItem.addEventListener('dblclick', () => {
                    loadSubfolders(folderItem, data);
                });
            });
            // add cancel and move buttons
            const folderMoveBtns = document.createElement('div');
            folderMoveBtns.classList.add('options-modal-dir-move-btns');
            folderMoveBtns.innerHTML = `
            <button onclick="hideOptionsModal()">Cancel</button>
            <button onclick="submitDirMove()" class="btn btn-primary">Move</button>
        `;

            detailsOptionsModalBody.appendChild(folderMoveBtns);

        });

        function loadSubfolders(folderItem, data) {
            data.forEach(folder => {
                if (folder.dir_id == folderItem.getAttribute('value')) {
                    // replace list with the subfolders
                    folderList.innerHTML = '';

                    if (folder.children.length === 0) {
                        folderList.innerHTML = `
                    <div class="loading">
                        <p>No folders found</p>
                    </div>
                `;
                    }

                    folder.children.forEach(subfolder => {
                        const subfolderItem = document.createElement('div');
                        subfolderItem.classList.add('dirs-folder-item');
                        subfolderItem.setAttribute('value', subfolder.dir_id);
                        subfolderItem.setAttribute('name', subfolder.name);
                        subfolderItem.innerHTML = `
                            <div class="folder-icon">
                                <i class='bx bxs-folder'></i>
                            </div>
                            <div class="folder-name">
                                ${subfolder.name}
                            </div>
                        `;

                        folderList.appendChild(subfolderItem);

                        // update event listeners for the new subfolder items
                        subfolderItem.addEventListener('click', () => {
                            clearSelected();
                            subfolderItem.classList.toggle('selected');
                        });

                        subfolderItem.addEventListener('dblclick', () => {
                            loadSubfolders(subfolderItem, folder.children);
                        });
                    });
                }
            });
        }


        function clearSelected() {
            // Remove 'selected' class from all folder items
            const folderItems = document.querySelectorAll('.dirs-folder-item');
            folderItems.forEach(item => {
                item.classList.remove('selected');
            });
        }

    }

    //TODO: remove
    else {
        folderOptionsModalOverlay.classList.add('active');
        folderOptionsModal.classList.add('active');
    }


}

function submitDirMove() {
    // find selected item
    const selectedFolder = document.querySelector('.dirs-folder-item.selected');
    const selectedFolderId = selectedFolder.getAttribute('value');
    const selectedFolderName = selectedFolder.getAttribute('name');
    const folderMoveData = document.querySelector('.folder-move-data');
    const folderMoveDataId = folderMoveData.getAttribute('value');
    const folderMoveDataName = folderMoveData.getAttribute('name');

    console.log(selectedFolderId, selectedFolderName);

    // make post request to move folder
    fetch('/api/move_folder', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            folderId: folderMoveDataId,
            newParentId: selectedFolderId
        })
    })
        .then(response => {
            if (response.status === 200) {
                response.json().then(data => {
                    showNotif('success', 'system', folderMoveDataName + ' moved to ' + selectedFolderName + ' successfully');
                    //refresh notifs
                    // renderFolders()
                    //rename folder from folder view or folders list
                    folderItems = document.querySelectorAll('.folder-item');
                    folderItems.forEach(folder => {
                            if (folder.getAttribute('value') == folderMoveDataId) {
                                folder.remove();
                                resetDetails();
                            }
                        }
                    );

                    //close folder view if folder is deleted
                    if (document.querySelector('.folder-view-name').getAttribute('value') == folderMoveDataId) {
                        hidefolderView();
                        resetDetails();
                    }

                    hideOptionsModal();
                });
            } else {
                response.json().then(data => {
                    showNotif('error', 'system', data);
                    hideOptionsModal();
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotif('error', 'system', 'Error moving folder');
        });
}

// fetch dir_structure
async function getDirStructure(path = null) {
    console.log(path)
    const response = await fetch(`/api/dir_structure`);
    const data = await response.json();
    console.log(data);
    return data;
}

function createFolder(foldername, is_root, parentid = null) {
    fetch('/api/create_folder', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            folderName: foldername,
            isRoot: is_root,
            parentId: parentid,
        })
    })
        .then(response => {
            if (response.status === 200) {
                response.json().then(data => {
                    showNotif('success', 'system', foldername + ' created successfully');
                    //refresh notifs

                    if (is_root) {
                        renderFolders()
                    }

                    if (document.querySelector('.folder-view-name').getAttribute('value') == parentid) {
                        populateFolderView(parentid)
                    }

                    hideOptionsModal();
                });
            } else {
                response.json().then(data => {
                    showNotif('error', 'system', data);
                    hideOptionsModal();
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotif('error', 'system', 'Error creating folder');
        });

}

function deleteFolder(id, name) {
    fetch('/api/delete_folder', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            folderId: id,
        })
    })
        .then(response => {
            if (response.status === 200) {
                response.json().then(data => {
                    showNotif('success', 'system', name + ' deleted successfully');
                    //refresh notifs
                    // renderFolders()
                    //remove folder from folder view or folders list
                    folderItems = document.querySelectorAll('.folder-item');
                    folderItems.forEach(folder => {
                            if (folder.getAttribute('value') == id) {
                                folder.remove();
                                resetDetails();
                            }
                        }
                    );

                    //close folder view if folder is deleted
                    if (document.querySelector('.folder-view-name').getAttribute('value') == id) {
                        hidefolderView();
                        resetDetails();
                    }

                    hideOptionsModal();
                });
            } else {
                response.json().then(data => {
                    showNotif('error', 'system', data);
                    hideOptionsModal();
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotif('error', 'system', 'Error deleting folder');
        });
}

function renameFolder(id, name, newname) {
    fetch('/api/rename_folder', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            folderId: id,
            newName: newname
        })
    })
        .then(response => {
            if (response.status === 200) {
                response.json().then(data => {
                    showNotif('success', 'system', name + ' renamed to ' + newname + ' successfully');
                    //refresh notifs
                    // renderFolders()
                    //rename folder from folder view or folders list
                    folderItems = document.querySelectorAll('.folder-item');
                    folderItems.forEach(folder => {
                            if (folder.getAttribute('value') == id) {
                                folder.querySelector('.folder-name').innerHTML = newname;
                                folder.setAttribute('name', newname);
                            }
                        }
                    );

                    //close folder view if folder is deleted
                    if (document.querySelector('.folder-view-name').getAttribute('value') == id) {
                        document.querySelector('.folder-view-name').innerHTML = newname;
                    }

                    hideOptionsModal();
                });
            } else {
                response.json().then(data => {
                    showNotif('error', 'system', data);
                    hideOptionsModal();
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotif('error', 'system', 'Error renaming folder');
        });

}

//general context menu
{
//new folder
    generalContextMenuNewdir.addEventListener('click', () => {
        showOptionsModal('newdir');
    });

//file upload
    generalContextMenuFileUpload.addEventListener('click', () => {
        showOptionsModal('fileupload');
    });

//folder upload
    generalContextMenuDirUpload.addEventListener('click', () => {
        showOptionsModal('dirupload');
    });
}


//files and recents context menu
{
//view
    fileOptionView.addEventListener('click', () => {
        const id = fileOptionView.getAttribute('value');
        window.location.href = `/view/${id}`;
    });

    contextMenuView.addEventListener('click', () => {
        const id = contextMenuView.getAttribute('value');
        window.location.href = `/view/${id}`;
    });

//copy
    fileOptionCopy.addEventListener('click', () => {
        const id = fileOptionCopy.getAttribute('value');
        const fileName = fileOptionCopy.getAttribute('name');
        showOptionsModal('filecopy', id, type = 'file', name = fileName);
    });

    contextMenuCopy.addEventListener('click', () => {
        const id = contextMenuCopy.getAttribute('value');
        const fileName = contextMenuCopy.getAttribute('name');
        showOptionsModal('filecopy', id, type = 'file', name = fileName);
    });

//move
    fileOptionMove.addEventListener('click', () => {
        const id = fileOptionMove.getAttribute('value');
        const fileName = fileOptionMove.getAttribute('name');
        showOptionsModal('filemove', id, type = 'file', name = fileName);
    });

    contextMenuMove.addEventListener('click', () => {
        const id = contextMenuMove.getAttribute('value');
        const fileName = contextMenuMove.getAttribute('name');
        showOptionsModal('filemove', id, type = 'file', name = fileName);
    });

//download
    fileOptionDownload.addEventListener('click', () => {
        const id = fileOptionDownload.getAttribute('value');
        const fileName = fileOptionDownload.getAttribute('name');
        showOptionsModal('filedownload', id, type = 'file', name = fileName);
    });

    contextMenuDownload.addEventListener('click', () => {
        const id = contextMenuDownload.getAttribute('value');
        const fileName = contextMenuDownload.getAttribute('name');
        showOptionsModal('filedownload', id, type = 'file', name = fileName);
    });

//share
    fileOptionShare.addEventListener('click', () => {
        const id = fileOptionShare.getAttribute('value');
        const fileName = fileOptionShare.getAttribute('name');
        showOptionsModal('fileshare', id, type = 'file', name = fileName);
    });

    contextMenuShare.addEventListener('click', () => {
        const id = contextMenuShare.getAttribute('value');
        const fileName = contextMenuShare.getAttribute('name');
        showOptionsModal('fileshare', id, type = 'file', name = fileName);
    });

//rename
    fileOptionRename.addEventListener('click', () => {
        const id = fileOptionRename.getAttribute('value');
        const fileName = fileOptionRename.getAttribute('name');
        showOptionsModal('filerename', id, type = 'file', name = fileName);
    });

    contextMenuRename.addEventListener('click', () => {
        const id = contextMenuRename.getAttribute('value');
        const fileName = contextMenuRename.getAttribute('name');
        showOptionsModal('filerename', id, type = 'file', name = fileName);
    });

//delete
    fileOptionDelete.addEventListener('click', () => {
        const id = fileOptionDelete.getAttribute('value');
        const fileName = fileOptionDelete.getAttribute('name');
        showOptionsModal('filedelete', id, type = 'file', name = fileName);
    });

    contextMenuDelete.addEventListener('click', () => {
        const id = contextMenuDelete.getAttribute('value');
        const fileName = contextMenuDelete.getAttribute('name');
        showOptionsModal('filedelete', id, type = 'file', name = fileName);
    });

}

//folder context menu
{
//new dir +
    folderContextNewdir.addEventListener('click', () => {
            const id = folderContextNewdir.getAttribute('value');
            const name = folderContextNewdir.getAttribute('name');
            console.log(id, name);
            showOptionsModal('newdir', id, type = 'folder', name);
        }
    );


//view +
    folderOptionView.addEventListener('click', () => {
        const id = folderOptionView.getAttribute('value');
        const folderName = document.querySelector(`.folder-item[value="${id}"] .folder-name`).innerHTML;

        showfolderView(folderName, id);
    });

    folderContextMenuView.addEventListener('click', () => {
        const id = folderContextMenuView.getAttribute('value');
        const folderName = document.querySelector(`.folder-item[value="${id}"] .folder-name`).innerHTML;

        showfolderView(folderName, id);
    });

//move
    folderOptionMove.addEventListener('click', () => {
        const id = folderOptionMove.getAttribute('value');
        const fileName = folderOptionMove.getAttribute('name');

        showOptionsModal('dirmove', id, type = 'folder', name = fileName);
    });

    folderContextMenuMove.addEventListener('click', () => {
        const id = folderContextMenuMove.getAttribute('value');
        const fileName = folderContextMenuMove.getAttribute('name');

        showOptionsModal('dirmove', id, type = 'folder', name = fileName);
    });

//rename +
    folderOptionRename.addEventListener('click', () => {
        const id = folderOptionRename.getAttribute('value');
        const fileName = folderOptionRename.getAttribute('name');

        showOptionsModal('dirrename', id, type = 'folder', name = fileName);
    });

    folderContextMenuRename.addEventListener('click', () => {
        const id = folderContextMenuRename.getAttribute('value');
        const fileName = folderContextMenuRename.getAttribute('name');

        showOptionsModal('dirrename', id, type = 'folder', name = fileName);
    });

//delete +
    folderOptionDelete.addEventListener('click', () => {
        const id = folderOptionDelete.getAttribute('value');
        const fileName = folderOptionDelete.getAttribute('name');

        showOptionsModal('dirdelete', id, type = 'folder', name = fileName);
    });

    folderContextMenuDelete.addEventListener('click', () => {
        const id = folderContextMenuDelete.getAttribute('value');
        const fileName = folderContextMenuDelete.getAttribute('name');

        showOptionsModal('dirdelete', id, type = 'folder', name = fileName);
    });
}

//init
renderFolders();
renderRecents();
sortFiles();
showStats();