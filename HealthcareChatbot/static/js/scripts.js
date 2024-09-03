// 绑定事件处理程序到DOM加载完毕
document.addEventListener('DOMContentLoaded', function() {
 
    
    // 定义一个变量来记录用户点击"确定咨询"的次数
    let consultCount = 0;   
    // 当用户点击“确定咨询”按钮时的事件处理
    document.getElementById('send-button').addEventListener('click', function() {
        let userMessage = document.getElementById('message-input').value.trim();
        const provideInfo = document.querySelector('input[name="provideInfo"]:checked').value;
        const age = document.getElementById('age').value;
        const gender = document.getElementById('gender').value;
        const occupation = document.getElementById('occupation').value;

        if (!userMessage) {
            // 如果用户没有输入内容，则显示提醒
            alert('请输入咨询内容');
        } else {
            // 用户每次点击且已输入内容时，次数加1
            consultCount++;

            // 如果用户点击次数超过10次，显示提醒
            if (consultCount > 10) {
                alert('咨询次数已达到10次，请结束咨询，进入问卷调查过程');
                // 清空输入框
                document.getElementById('message-input').value = '';
                return; // 不继续执行后面的代码
            }

            // 显示用户的消息在聊天区域
            displayMessage(userMessage, 'user');
            // 清空输入框
            document.getElementById('message-input').value = '';
            // 发送消息到后端
            sendMessageToServer(userMessage, provideInfo, age, gender, occupation);
        }
    });

    // 当用户点击“结束咨询”按钮时的事件处理
    document.getElementById('end-button').addEventListener('click', function() {
        // 可以在这里添加结束咨询的逻辑，例如重置界面或者发送特定请求到服务器
        if(consultCount === 0){
            alert("请先完成至少一次问询过程");
            return;
        }
        // 使用fetch API向后端发送请求，告知当前会话已结束
        fetch(`/LLMHPri/end_session/${sessionId}/`, { // 使用模板字符串构造URL，确保 sessionId 被正确插入
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 'session_id': sessionId })
        })
        .then(response => response.json())
        .then(data => {
            if(data.status === 'success') {
                // alert("咨询结束。专注力测试: 请记住待会需要填入的编号:"+sessionId);
                alert(data.message);
                // window.location.href = "/LLMHPri/survey";
                postToSurvey();
            } else {
                // alert('结束咨询时出错。');
                alert(data.message);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });
});


// dialogue.js
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('input[name="provideInfo"]').forEach(radio => {
        radio.addEventListener('change', function() {
            document.getElementById('additionalInfo').style.display = this.value === 'yes' ? 'block' : 'none';
        });
    });
});


// 用于向服务器发送消息并处理响应的函数
function sendMessageToServer(message, provideInfo, age, gender, occupation) {
    showWaitingMessage(); // 显示等待中提示
    fetch(`/LLMHPri/send_message/${sessionId}/`, {
        method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
        body: JSON.stringify({
            'message':message, 'session_id': sessionId,
            'provideInfo': provideInfo,
            'age': age,
            'gender': gender,
            'occupation': occupation
        })
    })
    .then(response => response.json())
    .then(data => {
        // 移除等待提示
        document.querySelector('.waiting-message').remove();
        // 显示GPT的回复
        displayMessage(data.message, 'gpt');
        // 更新预设提示词
        updateSuggestions(data.suggestions);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// 用于显示消息在聊天区域的函数
function displayMessage(message, sender) {
    
    // 创建消息容器div
    let messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender + '-message'); // 同时添加 sender 的 class

    // 创建头像的img元素
    let avatar = document.createElement('img');
    avatar.classList.add('avatar');
    avatar.src = sender === 'user' ? '/static/img/user1.png' : '/static/img/GPTDoc.png';

    // 创建包含文本内容的div元素，并设置其为 flex 容器
    let textContentDiv = document.createElement('div');
    textContentDiv.classList.add('text-content');
    messageDiv.appendChild(avatar);
    
    // 如果发送者是 GPT，则使用打字效果，否则直接显示消息
    if (sender === 'gpt') {
        // 使用打字效果时，文本内容暂时为空
        let textContentP = document.createElement('p');
        textContentDiv.appendChild(textContentP);
        messageDiv.appendChild(textContentDiv);
        typeMessage(textContentP, message, 50); // 使用打字效果
        // textContentP.innerHTML = message;
    } else {
        // 如果是用户，直接创建并添加 p 元素
        let textContentP = document.createElement('p');
        textContentP.textContent = message;
        textContentDiv.appendChild(textContentP);
        messageDiv.appendChild(textContentDiv);
    }

    // 添加消息到页面上
    document.getElementById('messages').appendChild(messageDiv);
    // 滚动到最新的消息
    messageDiv.scrollIntoView();
}

function postToSurvey() {
    // 创建一个表单
    var form = document.createElement("form");
    form.setAttribute("method", "post");
    form.setAttribute("action", "/LLMHPri/survey/");

    // 如果需要发送数据，可以添加input元素到表单中
    // 例如，发送用户会话的ID
    var hiddenField = document.createElement("input");
    hiddenField.setAttribute("type", "hidden");
    hiddenField.setAttribute("name", "session_id");
    hiddenField.setAttribute("value", sessionId);  // 假设sessionId变量已定义
    form.appendChild(hiddenField);

    // 添加CSRF令牌
    var csrfToken = getCookie('csrftoken');  // 假设getCookie函数可以获取当前的CSRF token
    var csrfInput = document.createElement("input");
    csrfInput.setAttribute("type", "hidden");
    csrfInput.setAttribute("name", "csrfmiddlewaretoken");
    csrfInput.setAttribute("value", csrfToken);
    form.appendChild(csrfInput);

    document.body.appendChild(form);
    form.submit();
}

// 辅助函数，用于获取CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// 添加等待提示的函数
function showWaitingMessage() {
    const waitingMessage = document.createElement('div');
    waitingMessage.classList.add('message', 'waiting-message');
    waitingMessage.textContent = '请耐心等待响应...';
    document.getElementById('messages').appendChild(waitingMessage);
    waitingMessage.scrollIntoView();
  }


// 打字机效果函数
function typeMessage(element, message, interval, sender) {
    let i = 0;
    function typing() {
      if (i < message.length) {
        element.textContent += message.charAt(i);
        i++;
        setTimeout(typing, interval);
      } else {
        // 如果是用户消息，不需要打字效果
        if (sender === 'user') {
          element.textContent = message;
        }
      }
    }
    if (sender === 'gpt') {
      typing();
    } else {
      // 如果是用户消息，直接显示
      element.textContent = message;
    }
  }

// 用于更新预设提示词的函数
function updateSuggestions(suggestions) {
    let suggestionsContainer = document.querySelector('.suggestions');
    suggestionsContainer.innerHTML = ''; // 清空当前的提示词
    suggestions.forEach(suggestion => {
        let button = document.createElement('button');
        button.textContent = suggestion;
        button.classList.add('suggestion-btn-new');
        button.onclick = function() { insertText(suggestion); };
        suggestionsContainer.appendChild(button);
    });
}

// 将预设提示词填入到输入框的函数
function insertText(text) {
    document.getElementById('message-input').value = text;
}


function showConsultation(type) {
    var chatSessionDiv = document.getElementById('chatSession');
    var multipleSessionsDiv = document.getElementById('multipleSessions');


    // 获取所有具有name="provideInfo"的单选按钮
    var radios = document.getElementsByName('provideInfo');
    
    // 检查是否有单选按钮被选中
    var isSelected = false;
    for (var i = 0; i < radios.length; i++) {
        if (radios[i].checked) {
            isSelected = true;
            break;
        }
    }

    // 如果没有选中任何选项，则显示错误消息
    if (!isSelected) {
        alert('请先选择是否提供信息！');
        return; // 阻止进一步操作
    }

    const provideInfo = document.querySelector('input[name="provideInfo"]:checked') ? document.querySelector('input[name="provideInfo"]:checked').value : '';
    const occupation = document.getElementById('occupation').value.trim();
    const age = document.getElementById('age').value;
    const gender = document.getElementById('gender').value;


    //如果用户选择了“是”提供信息，但没有选择“年龄”
    if (provideInfo === 'yes' && !age) {
        alert('请选择您的年龄');
        return; // 阻止进一步操作
    }

    // 如果用户选择了“是”提供信息，但没有选择“性别”
    if (provideInfo === 'yes' && !gender) {
        alert('请选择您的性别');
        return; // 阻止进一步操作
    }


    // 如果用户选择了“是”提供信息，但没有输入“职业”
    if (provideInfo === 'yes' && !occupation) {
        alert('请输入您的职业或身份');
        return; // 阻止进一步操作
    }


    // 隐藏原始选择按钮和文本
    document.querySelector('.content').style.display = 'none';
    document.querySelector('.button-container').style.display = 'none';
    

    // 显示聊天界面
    
    if (type === 'multiple') {
        chatSessionDiv.style.display = 'block';
        // 隐藏原来的h2标题
        document.getElementById('h2title').style.display = 'none';
    }
}



function typeMessage(element, message, interval) {
    let i = 0;
    function typing() {
      if (i < message.length) {
        element.textContent += message.charAt(i);
        i++;
        setTimeout(typing, interval);
      }
    }
    typing();
  }

function loadScriptBasedOnSessionId() {
    // 检查是否在survey.html页面
    var surveyContainer = document.getElementById('survey-container');
    if (!surveyContainer) {
        // 如果不在survey.html页面，直接返回不执行后面的代码
        return;
    }

    var scripts = [
        'https://www.wjx.cn/handler/jqemed.ashx?activity=rc5gVJN&width=750&source=iframe&sm=t&height=2',
        'https://www.wjx.cn/handler/jqemed.ashx?activity=Ohn6yxQ&width=750&source=iframe&sm=t&height=2',
        'https://www.wjx.cn/handler/jqemed.ashx?activity=OQ6gJQn&width=750&source=iframe&sm=t&height=2',
        'https://www.wjx.cn/handler/jqemed.ashx?activity=mxxamXe&width=750&source=iframe&sm=t&height=2',

        'https://www.wjx.cn/handler/jqemed.ashx?activity=YfYWYdS&width=750&source=iframe&sm=t&height=2',
        'https://www.wjx.cn/handler/jqemed.ashx?activity=QBm52M6&width=750&source=iframe&sm=t&height=2',
        'https://www.wjx.cn/handler/jqemed.ashx?activity=YDdSgQY&width=750&source=iframe&sm=t&height=2',
        'https://www.wjx.cn/handler/jqemed.ashx?activity=O0euQnT&width=750&source=iframe&sm=t&height=2',

        'https://www.wjx.cn/handler/jqemed.ashx?activity=rK6gVqS&width=750&source=iframe&sm=t&height=2',
        'https://www.wjx.cn/handler/jqemed.ashx?activity=mSXxaQS&width=750&source=iframe&sm=t&height=2',
        'https://www.wjx.cn/handler/jqemed.ashx?activity=rbVMNkg&width=750&source=iframe&sm=t&height=2',
        'https://www.wjx.cn/handler/jqemed.ashx?activity=tUGqHsp&width=750&source=iframe&sm=t&height=2',

        'https://www.wjx.cn/handler/jqemed.ashx?activity=tOplxHs&width=750&source=iframe&sm=t&height=2',
        'https://www.wjx.cn/handler/jqemed.ashx?activity=Qn2MjaA&width=750&source=iframe&sm=t&height=2',
        'https://www.wjx.cn/handler/jqemed.ashx?activity=YgYd5Gu&width=750&source=iframe&sm=t&height=2',
        'https://www.wjx.cn/handler/jqemed.ashx?activity=rQgVlKX&width=750&source=iframe&sm=t&height=2'
    ];

    // 使用全局变量sessionId来决定加载哪个<script>
    var index = (sessionId - 1) % scripts.length;
    var script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = scripts[index];
    surveyContainer.appendChild(script);
}

