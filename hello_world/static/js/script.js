// 事件监听器
document.addEventListener('DOMContentLoaded', function() {

// 上述代码为整个应用添加了必要的事件监听器。当DOM完全加载后，
// `DOMContentLoaded`事件将触发，然后将事件监听器绑定到相应的元素上。
// 这确保了在尝试绑定事件监听器之前，元素已经在DOM中可用。

// 此外，这种方法还避免了将事件处理器直接在HTML元素中定义，
// 从而有助于保持HTML的清洁和易于维护，同时JavaScript代码也更加模块化。

// 确保代码在文档加载完毕后执行
    var selectedEngines = [];
    var input = document.getElementById('enginesearchInput');
    var dropdown = document.getElementById('enginesearchDropdown');
    var options = dropdown.getElementsByClassName('option');
    var selectedEnginesDisplay = document.getElementById('selectedEnginesDisplay');

    input.onclick = function(event) {
        dropdown.style.display = 'block';
        event.stopPropagation();
    };

    Array.from(options).forEach(function(element) {
        element.onclick = function(event) {
            var value = this.getAttribute('data-value');
            var index = selectedEngines.indexOf(value);

            if (index > -1) {
                selectedEngines.splice(index, 1);
                this.classList.remove('selected');
            } else {
                selectedEngines.push(value);
                this.classList.add('selected');
            }

            updateSelectedEnginesDisplay();
            event.stopPropagation();
        };
    });

        // 默认选中前三个选项
        var defaultEngines = ['google', 'bing', 'yahoo'];
        Array.from(options).forEach(function(option) {
            if (defaultEngines.includes(option.getAttribute('data-value'))) {
                option.classList.add('selected');
                selectedEngines.push(option.getAttribute('data-value'));
            }
        });
        updateSelectedEnginesDisplay(); // 更新界面显示

    function updateSelectedEnginesDisplay() {
        selectedEnginesDisplay.innerHTML = ''; // 清空显示区域
        selectedEngines.forEach(function(engine) {
            var div = document.createElement('div');
            div.className = 'selected-engine';
            div.textContent = engine; // 设置显示的引擎名称

            // 添加删除图标
            var removeIcon = document.createElement('span');
            removeIcon.textContent = '×'; // 设置图标文本
            removeIcon.className = 'remove-icon';
            removeIcon.onclick = function() {
                removeEngine(engine); // 移除引擎
            };
            div.appendChild(removeIcon);

            selectedEnginesDisplay.appendChild(div); // 添加到显示区域
        });
    }

    function removeEngine(engine) {
        var index = selectedEngines.indexOf(engine);
        if (index > -1) {
            selectedEngines.splice(index, 1); // 从选中列表中移除
            updateSelectedEnginesDisplay(); // 更新显示

            // 取消下拉列表中相应选项的选中状态
            Array.from(options).forEach(function(option) {
                if (option.getAttribute('data-value') === engine) {
                    option.classList.remove('selected');
                }
            });
        }
    }

    document.addEventListener('click', function() {
        dropdown.style.display = 'none';
    });


    // 添加事件监听器到搜索表单
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', function(event) {
            event.preventDefault();
            sendSearchRequest(selectedEngines);
        });
    }

    // 添加事件监听器到刷新列表按钮
    const refreshButton = document.getElementById('refreshListBtn');
    if (refreshButton) {
        refreshButton.addEventListener('click', refreshList);
    }
    
    // 添加事件监听器到重启所有任务按钮
    const restartAllBtn = document.getElementById('restartAllTasksBtn');
    if (restartAllBtn) {
        restartAllBtn.onclick = restartAllTasks;
    }
});

// 发送搜索请求
function sendSearchRequest(selectedEngines) {
    // 收集输入数据
    const inputData = {
        target_url: document.getElementById('target_url').value,
        keyword: document.getElementById('keyword').value,
        after: document.getElementById('after').value,
        before: document.getElementById('before').value,
        enginesearch: selectedEngines, // 发送选中的搜索引擎数组
        pages: parseInt(document.getElementById('pages').value) || null,
        name: document.getElementById('name').value,
        minutes: parseInt(document.getElementById('minutes').value) || null,
        proxy: document.getElementById('proxy').value,
    };

    // 使用fetch API发送数据到后端
    fetch('api/RunSearchApi', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(inputData),
    })
    .then(response => response.json())
    .then(data => {
        // 在左侧部分显示UUID
        const uuidList = document.getElementById('uuidList');
        const listItem = document.createElement('li');
        listItem.textContent = data.uuid;
        listItem.onclick = function() {
            displayJson(inputData);
        };
        uuidList.prepend(listItem);
    })
    .catch(error => console.error('Error:', error));
}

// 展示JSON数据
function displayJson(data) {
    // 在右侧部分展示JSON数据
    const jsonDisplay = document.getElementById('jsonDisplay');
    jsonDisplay.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
}

function restartAllTasks() {
    const uuidList = document.getElementById('uuidList');
    const allUuids = Array.from(uuidList.querySelectorAll('li span')).map(span => span.textContent);

    fetch('api/GetTaskRestartApi', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ "all_uuid": allUuids }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'Failed') {
            alert('无任务可重启');
        } else if (data.status === 'Succeed') {
            alert(`重启成功 ${data.data.split(' ')[1]} 个任务`);
        }
    })
    .catch(error => console.error('Error:', error));
}


// 刷新UUID列表
function refreshList() {
    // 向后端请求UUID列表
    fetch('api/GetSearchListApi', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        // 可以根据需要发送额外的数据
        body: JSON.stringify({ /* 传递所需的数据 */ }),
    })
    .then(response => response.json())
    .then(data => {
        const uuidList = document.getElementById('uuidList');
        uuidList.innerHTML = ""; // 清空现有列表

        // 处理返回的数据
        if (data.status === 'success') {
            data.data.forEach(item => {
                const listItem = document.createElement('li');

                // 设置显示的名称
                listItem.textContent = item.name;

                // 将 UUID 存储在元素的 data 属性中
                listItem.dataset.uuid = item.uuid;

                // 添加刷新按钮
                const refreshBtn = document.createElement('button');
                refreshBtn.textContent = '刷新';
                refreshBtn.onclick = function() {
                    refreshSingleItem(item.uuid); // 使用 UUID 刷新单个项目
                };
                listItem.appendChild(refreshBtn);

                // 添加详细数据请求的点击事件
                listItem.onclick = function() {
                    requestDetailedData(item.uuid); // 使用 UUID 请求详细数据
                };

                uuidList.appendChild(listItem);
            });
        } else {
            const noDataMessage = document.createElement('li');
            noDataMessage.textContent = '暂无数据';
            uuidList.appendChild(noDataMessage);
        }
    })
    .catch(error => console.error('Error:', error));
}

function refreshSingleItem(uuid) {
    fetch('api/GetTaskRestartApi', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ "all_uuid": [uuid] }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'Failed') {
            alert('无任务可重启');
        } else if (data.status === 'Succeed') {
            alert(`重启成功 ${data.data.split(' ')[1]} 个任务`);
        }
    })
    .catch(error => console.error('Error:', error));
}


// 请求详细数据
function requestDetailedData(uuid) {
    // 向后端发送请求，获取详细数据
    fetch('api/GetSearchqueryApi', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ "uuid": uuid }),
    })
    .then(response => response.json())
    .then(data => {
        const jsonDisplay = document.getElementById('jsonDisplay');
        jsonDisplay.innerHTML = ""; // 清空现有数据

        // 展示查询到的数据
        if (data.status === 'success') {
            const queryValue = data.data.query_value;
            const request_body_value = data.data.request_body_value;

            const displayArea = document.createElement('div');
            displayArea.innerHTML = `<p>Query Value: ${queryValue}</p><p>RequestBody Value: ${request_body_value}</p>`;
            jsonDisplay.appendChild(displayArea);
        } else {
            const errorMessage = document.createElement('p');
            errorMessage.textContent = '查询数据为空';
            jsonDisplay.appendChild(errorMessage);
        }
    })
    .catch(error => console.error('Error:', error));
}

