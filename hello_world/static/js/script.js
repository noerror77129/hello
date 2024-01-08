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
        var defaultEngines = ['google', 'bing', 'baidu'];
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
    //初次加载刷新列表数据
    refreshList();

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
    // 表单验证
    const targetUrl = document.getElementById('target_url').value;
    const enginesearch = selectedEngines;
    const name = document.getElementById('name').value;
    let minutes = parseInt(document.getElementById('minutes').value);
    let pages = parseInt(document.getElementById('pages').value);

    let missingFields = [];
    if (!targetUrl) missingFields.push('目标 URL');
    if (!enginesearch.length) missingFields.push('搜索引擎');
    if (!name) missingFields.push('目标名称');
    // 检查是否超出范围
    if (minutes < 1 || minutes > 43200) {
        missingFields.push('间隔分钟数 (1 - 43200)');
    }
    if (pages < 0 || pages > 50) {
        missingFields.push('搜索页数 (0 - 50)');
    }

    if (missingFields.length > 0) {
        alert('请填写以下必填项或更正错误: ' + missingFields.join(', '));
        return;
    }
    // 收集输入数据
    const inputData = {
        target_url: document.getElementById('target_url').value,
        enginesearch: selectedEngines, // 发送选中的搜索引擎数组
        name: document.getElementById('name').value,
        minutes: parseInt(document.getElementById('minutes').value) || null,
        pages: parseInt(document.getElementById('pages').value) || null,
        keyword: document.getElementById('keyword').value,
        after: document.getElementById('after').value,
        before: document.getElementById('before').value,
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
        refreshList();
    })
    .catch(error => console.error('Error:', error));
}

// 展示JSON数据
function displayJson(strData) {
    try {
        // 如果数据包含转义字符，先解析一次
        const rawData = JSON.parse(strData);

        // 再次解析以确保得到 JSON 对象
        const jsonData = JSON.parse(rawData);

        // 格式化 JSON 对象为字符串
        const formattedJson = JSON.stringify(jsonData, null, 4); // 使用4个空格进行缩进

        // 在页面上展示格式化的 JSON 数据
        const jsonDisplay = document.getElementById('jsonDisplay');
        jsonDisplay.innerHTML = `<pre>${formattedJson}</pre>`;
    } catch (error) {
        console.error('解析 JSON 数据时出错: ', error);
        // 可以选择在页面上显示错误信息
    }
}

function restartAllTasks() {
    const uuidList = document.getElementById('uuidList');
    // 获取所有 li 元素，并从每个元素的 data-uuid 属性中提取 uuid
    const allUuids = Array.from(uuidList.querySelectorAll('li')).map(li => li.dataset.uuid);

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
                refreshBtn.textContent = '重启任务';
                refreshBtn.onclick = function() {
                    refreshSingleItem(item.uuid); // 使用 UUID 刷新单个项目
                };
                listItem.appendChild(refreshBtn);

                // 添加删除按钮
                const deleteBtn = document.createElement('button');
                deleteBtn.textContent = '中止任务';
                deleteBtn.onclick = function() {
                    deleteTask(item.uuid); // 删除任务的逻辑
                };
                listItem.appendChild(deleteBtn);

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

// 删除任务的函数
function deleteTask(uuid) {
    fetch('api/StopSearchApi', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ "uuid": uuid }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('删除成功');
            refreshList(); // 重新加载列表
        } else if (data.status === 'failed') {
            alert('任务已停止');
        } else if (data.status === 'error') {
            alert('无效的请求方法');
        }
    })
    .catch(error => console.error('Error:', error));
}


// 请求详细数据
function requestDetailedData(uuid) {
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

        if (data.status === 'success') {
            try {
                // 解析 JSON 字符串
                const jsonData = JSON.parse(data.data);

                // 格式化 JSON 对象为字符串
                const formattedJson = JSON.stringify(jsonData, null, 4);

                // 展示格式化的 JSON 数据
                jsonDisplay.innerHTML = `<pre>${formattedJson}</pre>`;
            } catch (error) {
                console.error('解析 JSON 数据时出错: ', error);
                jsonDisplay.textContent = 'JSON 解析错误';
            }
        } else {
            const errorMessage = document.createElement('p');
            errorMessage.textContent = '查询数据为空';
            jsonDisplay.appendChild(errorMessage);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        jsonDisplay.textContent = '请求出错';
    });
}