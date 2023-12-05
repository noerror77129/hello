// 发送搜索请求
function sendSearchRequest() {
    // 收集输入数据
    const inputData = {
        target_url: document.getElementById('target_url').value,
        keyword: document.getElementById('keyword').value,
        after: document.getElementById('after').value,
        before: document.getElementById('before').value,
        enginesearch: document.getElementById('enginesearch').value,
        pages: parseInt(document.getElementById('pages').value) || null,
        name: document.getElementById('name').value,
        minutes: parseInt(document.getElementById('minutes').value) || null,
        parent_directory: document.getElementById('parent_directory').value,
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
            // 如果返回数据，则添加到列表中
            data.data.forEach(uuid => {
                const listItem = document.createElement('li');
                listItem.textContent = uuid;
                listItem.onclick = function() {
                    requestDetailedData(uuid);
                };
                uuidList.appendChild(listItem);
            });
        } else {
            // 如果没有数据，显示提示信息
            const noDataMessage = document.createElement('li');
            noDataMessage.textContent = '暂无数据';
            uuidList.appendChild(noDataMessage);
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

// 事件监听器
document.addEventListener('DOMContentLoaded', function() {
    // 添加事件监听器到搜索按钮
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', function(event) {
            event.preventDefault();
            sendSearchRequest();
        });
    }

    // 添加事件监听器到刷新列表按钮
    const refreshButton = document.getElementById('refreshListBtn');
    if (refreshButton) {
        refreshButton.addEventListener('click', refreshList);
    }
});

// 上述代码为整个应用添加了必要的事件监听器。当DOM完全加载后，
// `DOMContentLoaded`事件将触发，然后将事件监听器绑定到相应的元素上。
// 这确保了在尝试绑定事件监听器之前，元素已经在DOM中可用。

// 此外，这种方法还避免了将事件处理器直接在HTML元素中定义，
// 从而有助于保持HTML的清洁和易于维护，同时JavaScript代码也更加模块化。

// 确保代码在文档加载完毕后执行
document.addEventListener('DOMContentLoaded', function() {
    // 可以在这里添加其他需要在页面加载完毕时执行的代码
});