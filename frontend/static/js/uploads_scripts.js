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
            clearSelected();

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
                clearSelected();

                folderItem.classList.toggle('selected');
                showDetails(folder.dir_id, type = 'folder');
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

const showDetails = async (id, type) => {
    if (type === 'file') {
        updateDetailsOptions(id);
    }
    if (type === 'folder') {
        updateDirDetailsOptions(id)
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

function updateDetailsOptions(id) {
    const folderOptions = document.querySelector('.details-body-folder-options-inner');
    if (folderOptions) {
        folderOptions.classList.remove("active");
    }

    const options = document.querySelector('.details-body-options-inner');
    fileOptionView.setAttribute('value', id);
    fileOptionCopy.setAttribute('value', id);
    fileOptionMove.setAttribute('value', id);
    fileOptionDownload.setAttribute('value', id);
    fileOptionShare.setAttribute('value', id);
    fileOptionDelete.setAttribute('value', id);

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

function updateDirDetailsOptions(id) {
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
    folderOptionMove.setAttribute('value', id);
    folderOptionRename.setAttribute('value', id);
    folderOptionDelete.setAttribute('value', id);

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
        x = width - generalContextMenuWidth - 20;
    }
    if (y + generalContextMenuHeight > height) {
        y = height - generalContextMenuHeight - 20;
    }

    generalContextMenu.style.top = `${y - 45}px`;
    generalContextMenu.style.left = `${x + 5}px`;
}

function hideGeneralContextMenu() {
    generalContextMenu.classList.remove('active');
}

function showContextMenu(x, y, id) {
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
    hideGeneralContextMenu();
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

    //Recents
    else if (e.target.matches('.recent-item') || e.target.matches('.recent-item *')) {
        //get id
        const id = e.target.closest('.recent-item').getAttribute('value');

        //show context menu
        showContextMenu(e.pageX, e.pageY, id);
    }


    //Folders
    else if (e.target.matches('.folder-item') || e.target.matches('.folder-item *')) {
        //get id
        const id = e.target.closest('.folder-item').getAttribute('value');

        //show context menu
        showFolderContextMenu(e.pageX, e.pageY, id);
    }


    //General
    else if (e.target.matches('.body-section-files') || e.target.matches('.body-section-files *')) {
        showGeneralContextMenu(e.pageX, e.pageY);
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
}

function showfolderView(name,id) {
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

        folderViewParentPath


    } else {
        //clear hierarchy
        folderViewParentPath.innerHTML = '';

    }
    // folderOptionsModalOverlay.classList.add('active');
    folderViewContainer.classList.add('active');
    updateFolderViewName(name, id);
    populateFolderView(id);
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
    const fileList = document.querySelector('.folder-view-section-files .files-list');

    folderInfo = getFolderContents(id);
    folderList.innerHTML = `
            <div class="loading">
                <i class='bx bx-loader-alt bx-spin'></i>
            </div>
        `;

    //folders
    folderListContent = folderInfo.then(data => {
            folderList.innerHTML = '';

            if (data.folders.length === 0) {
                folderList.innerHTML = `
                <div class="loading">
                    <p>No folders found</p>
                </div>
            `;
            }
            data.folders.forEach(folder => {
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
                folderList.appendChild(folderItem);

                // add click and dblclick events
                folderItem.addEventListener('click', () => {
                        // remove selected from all files
                        clearSelected();

                        folderItem.classList.toggle('selected');
                        showDetails(folder.dir_id, type = 'folder');
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
    fileList.innerHTML = `
            <div class="loading">
                <i class='bx bx-loader-alt bx-spin'></i>
            </div>
        `;


    fileListContent = folderInfo.then(data => {
            fileList.innerHTML = '';

            if (data.files.length === 0) {
                fileList.innerHTML = `
                <div class="loading">
                    <p>No files found</p>
                </div>
            `;
            }
            data.files.forEach(file => {
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


function showOptionsModal(activity, id = null, type = 'file') {
    folderOptionsModalOverlay.classList.add('active');
    folderOptionsModal.classList.add('active');
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
        showOptionsModal('copy', id);
    });

    contextMenuCopy.addEventListener('click', () => {
        const id = contextMenuCopy.getAttribute('value');
        showOptionsModal('copy', id);
    });

//move
    fileOptionMove.addEventListener('click', () => {
        const id = fileOptionMove.getAttribute('value');
        showOptionsModal('move', id);
    });

    contextMenuMove.addEventListener('click', () => {
        const id = contextMenuMove.getAttribute('value');
        showOptionsModal('move', id);
    });

//download
    fileOptionDownload.addEventListener('click', () => {
        const id = fileOptionDownload.getAttribute('value');
        showOptionsModal('download', id);
    });

    contextMenuDownload.addEventListener('click', () => {
        const id = contextMenuDownload.getAttribute('value');
        showOptionsModal('download', id);
    });

//share
    fileOptionShare.addEventListener('click', () => {
        const id = fileOptionShare.getAttribute('value');
        showOptionsModal('share', id);
    });

    contextMenuShare.addEventListener('click', () => {
        const id = contextMenuShare.getAttribute('value');
        showOptionsModal('share', id);
    });

//rename
    fileOptionRename.addEventListener('click', () => {
        const id = fileOptionRename.getAttribute('value');
        showOptionsModal('rename', id);
    });

    contextMenuRename.addEventListener('click', () => {
        const id = contextMenuRename.getAttribute('value');
        showOptionsModal('rename', id);
    });

//delete
    fileOptionDelete.addEventListener('click', () => {
        const id = fileOptionDelete.getAttribute('value');
        showOptionsModal('delete', id);
    });

    contextMenuDelete.addEventListener('click', () => {
        const id = contextMenuDelete.getAttribute('value');
        showOptionsModal('delete', id);
    });

}

//folder context menu
{
//view
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
        showOptionsModal('move', id, type = 'folder');
    });

    folderContextMenuMove.addEventListener('click', () => {
        const id = folderContextMenuMove.getAttribute('value');
        showOptionsModal('move', id, type = 'folder');
    });

//rename
    folderOptionRename.addEventListener('click', () => {
        const id = folderOptionRename.getAttribute('value');
        showOptionsModal('rename', id, type = 'folder');
    });

    folderContextMenuRename.addEventListener('click', () => {
        const id = folderContextMenuRename.getAttribute('value');
        showOptionsModal('rename', id, type = 'folder');
    });

//delete
    folderOptionDelete.addEventListener('click', () => {
        const id = folderOptionDelete.getAttribute('value');
        showOptionsModal('delete', id, type = 'folder');
    });

    folderContextMenuDelete.addEventListener('click', () => {
        const id = folderContextMenuDelete.getAttribute('value');
        showOptionsModal('delete', id, type = 'folder');
    });
}

//init
renderFolders();
renderRecents();
sortFiles();
showStats();
