// 等待页面加载完成
document.addEventListener("DOMContentLoaded", () => {
  // 加载真实的data.json
  fetch("data.json")
    .then((response) => response.json())
    .then((data) => {
      console.log("数据加载成功", data);
      renderPosts(data.posts);
    })
    .catch((error) => {
      console.error("加载失败:", error);
      const container = document.getElementById("posts-container");
      container.innerHTML =
        '<div class="loading">数据加载失败，请先运行 python generate_data.py 生成数据</div>';
    });
});

// 根据角色名返回头像图片路径
function getAvatarPath(characterName) {
  const avatarMap = {
    三月七: "march_seven.png",
    丹恒: "dh.png",
    姬子: "jizi-avatar.png",
    景元: "jingyuan-avatar.png",
    彦卿: "yq.png",
    砂金: "sj.png",
    托帕: "topaz.png",
    银狼: "silver_wolf.png",
    卡芙卡: "kafuka-avatar.png",
    刃: "ren-avatar.png",
    花火: "huahuo-avatar.png",
    黑塔: "heita-avatar.png",
    知更鸟: "zhigengniao-avatar.png",
    帕姆: "pamu-avatar.png",
    符玄: "fuxuan-avatar.png",
  };

  const fileName = avatarMap[characterName] || "default.png";
  return `images/avatars/${fileName}`;
}

// 递归渲染评论和回复
// 递归渲染评论和回复
function renderComment(comment, level = 0) {
  // 构建作者显示（支持 "A 回复 B" 格式）
  let authorDisplay = "";
  if (comment.replyTo) {
    authorDisplay = `
      <span class="reply-author">${escapeHtml(comment.author)}</span>
      <span class="reply-word">回复</span>
      <span class="reply-target">${escapeHtml(comment.replyTo)}</span>
    `;
  } else {
    authorDisplay = `<span class="comment-author">${escapeHtml(comment.author)}</span>`;
  }

  // 回复用 reply 类，一级评论用 comment 类
  const commentClass = level === 0 ? "comment" : "reply";
  
  let html = `
    <div class="${commentClass}" style="${level > 0 ? 'margin-left: 0px;' : ''}">
      <div class="comment-header">
        <div class="comment-author-wrap">${authorDisplay}</div>
        <span class="comment-time">${comment.time || "刚刚"}</span>
      </div>
      <div class="comment-content">${escapeHtml(comment.content)}</div>
  `;

  // 递归渲染子回复
  if (comment.replies && comment.replies.length > 0) {
    comment.replies.forEach((reply) => {
      html += renderComment(reply, level + 1);
    });
  }

  html += `</div>`;
  return html;
}

function renderPosts(posts) {
  const container = document.getElementById("posts-container");
  if (!container) return;
  let index = 0;
  if (!posts || posts.length === 0) {
    container.innerHTML =
      '<div class="loading">暂无动态，星穹列车正在检修~</div>';
    return;
  }

  let html = "";
  posts.forEach((post, index) => {
    // 构建点赞头像列表
    let likesAvatarsHtml = "";
    if (post.likes && post.likes.length > 0) {
      post.likes.forEach((like) => {
        let avatarPath = getAvatarPath(like);
        likesAvatarsHtml += `<img class="like-avatar" src="${avatarPath}" alt="${like}" title="${like}">`;
      });
    } else {
      likesAvatarsHtml = '<span class="likes-text">暂无点赞</span>';
    }

    // 构建表情栏
    let reactionsHtml = "";
    if (post.reactions && post.reactions.length > 0) {
      post.reactions.forEach((react) => {
        reactionsHtml += `
          <div class="reaction-item">
            <span class="reaction-emoji">${react.emoji}</span>
            <span class="reaction-count">${react.count}</span>
          </div>
        `;
      });
    }

    // 构建评论区
    let commentsHtml = "";
    if (post.comments && post.comments.length > 0) {
      post.comments.forEach((comment) => {
        commentsHtml += renderComment(comment, 0);
      });
    } else {
      commentsHtml =
        '<div class="comment" style="color:rgba(232,239,247,0.5);">暂无评论</div>';
    }

    // 构建图片列表
    let imagesHtml = "";
    if (post.images && post.images.length > 0) {
      imagesHtml = `<div class="post-images"><img class="post-image" src="${post.images[0]}" alt="朋友圈图片"></div>`;
    }

    // 最终卡片HTML - 添加 data-author 属性用于点击事件
    html += `
      <div class="post-card" data-author="${escapeHtml(post.author)}">
        <div class="post-header">
          <img class="post-avatar clickable-avatar" src="${getAvatarPath(post.author)}" alt="${post.author}" data-author="${escapeHtml(post.author)}">
          <div class="post-author">
            <div class="post-name clickable-name" data-author="${escapeHtml(post.author)}">${escapeHtml(post.author)}</div>
            <div class="post-time">
              <span>${escapeHtml(post.time)}</span>
              ${post.location ? `<span>· 📍 ${escapeHtml(post.location)}</span>` : ""}
            </div>
          </div>
        </div>
        <div class="post-content">${escapeHtml(post.content)}</div>
        ${imagesHtml}
        <div class="likes-section">
          <div class="likes-avatars">
            ${likesAvatarsHtml}
          </div>
        </div>
        <div class="reactions-section">
          ${reactionsHtml}
        </div>
        <div class="comments-section">
          ${commentsHtml}
        </div>
      </div>
    `;
  });

  container.innerHTML = html;
  
  // ========== 新增：绑定点击事件 ==========
  // 绑定所有可点击的头像
  document.querySelectorAll('.clickable-avatar, .clickable-name').forEach(el => {
    el.addEventListener('click', (e) => {
      e.stopPropagation();  // 防止事件冒泡
      const authorName = el.getAttribute('data-author');
      if (authorName) {
        openChatWith(authorName);
      }
    });
  });
}

// 简单防止XSS
function escapeHtml(str) {
  if (!str) return "";
  return str
    .replace(/[&<>]/g, function (m) {
      if (m === "&") return "&amp;";
      if (m === "<") return "&lt;";
      if (m === ">") return "&gt;";
      return m;
    })
    .replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g, function (c) {
      return c;
    });
}






// ========== 聊天功能代码 ==========

// 模拟聊天数据（实际使用时可以从 chats.json 加载）
let mockChatData = {
    "托帕": {
        messages: [
            { sender: "托帕", content: "刚开完会，砂金又说了半小时废话。", time: "18:30", type: "text" },
            { sender: "user", content: "哈哈，他又说什么了？", time: "18:32", type: "text" },
            { sender: "托帕", content: "说他的部门需要更多资金支持，但拿不出数据。我问他ROI多少，他沉默了。", time: "18:35", type: "text" }
        ]
    },
    "景元": {
        messages: [
            { sender: "景元", content: "夜深了，棋盘无人。", time: "23:14", type: "text" },
            { sender: "user", content: "将军，我陪您下？", time: "23:15", type: "text" },
            { sender: "景元", content: "好。", time: "23:16", type: "text" }
        ]
    },
    "三月七": {
        messages: [
            { sender: "三月七", content: "开拓者！！！今天拍照超好看的！！！", time: "14:23", type: "text" },
            { sender: "user", content: "发来看看？", time: "14:25", type: "text" },
            { sender: "三月七", content: "[图片] 怎么样怎么样！", time: "14:26", type: "text" }
        ]
    }
};

// 获取角色对应的头像路径
function getCharacterAvatar(characterName) {
    return getAvatarPath(characterName);
}

// 打开与指定角色的聊天
async function openChatWith(characterName) {
    console.log(`打开与 ${characterName} 的聊天`);
    
    // 获取聊天视图元素
    const postsContainer = document.getElementById('posts-container');
    const chatView = document.getElementById('chat-view');
    const chatAvatar = document.getElementById('chat-avatar');
    const chatName = document.getElementById('chat-name');
    const chatMessages = document.getElementById('chat-messages');
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const backBtn = document.getElementById('back-to-list');
    
    // 切换到聊天视图
    if (postsContainer) postsContainer.style.display = 'none';
    if (chatView) chatView.style.display = 'flex';
    currentView = 'chat';
    // 显示聊天详情容器，隐藏聊天列表
    const chatList = document.getElementById("chat-list");
    const chatDetail = document.getElementById("chat-detail");
    if (chatList) chatList.style.display = "none";
    if (chatDetail) chatDetail.style.display = "flex";
    
    // 设置聊天头信息
    chatAvatar.src = getCharacterAvatar(characterName);
    chatName.innerText = characterName;
    
    // 获取或创建聊天记录
    let chatHistory = mockChatData[characterName];
    if (!chatHistory) {
        // 如果没有历史记录，创建空记录
        chatHistory = { messages: [] };
        mockChatData[characterName] = chatHistory;
    }
    
    // 存储当前聊天角色名，供发送消息使用
    window.currentChatCharacter = characterName;
    window.currentChatHistory = chatHistory;
    
    // 渲染消息列表
    renderChatMessages(chatHistory.messages);
    
    // 绑定返回按钮事件（先移除旧的避免重复绑定）
    const newBackBtn = backBtn.cloneNode(true);
    backBtn.parentNode.replaceChild(newBackBtn, backBtn);
    newBackBtn.addEventListener('click', () => {
    // 显示朋友圈容器
    if (postsContainer) postsContainer.style.display = 'block';
    // 隐藏整个聊天视图
    if (chatView) chatView.style.display = 'none';
    // 重置聊天详情显示状态（下次打开时会重新显示）
    currentView = 'posts';
});
    
    // 绑定发送按钮事件
    const newSendBtn = sendBtn.cloneNode(true);
    sendBtn.parentNode.replaceChild(newSendBtn, sendBtn);
    
    async function handleSend() {
        const message = chatInput.value.trim();
        if (!message) return;
        
        // 添加用户消息
        const userMsg = {
            sender: "user",
            content: message,
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            type: "text"
        };
        window.currentChatHistory.messages.push(userMsg);
        renderChatMessages(window.currentChatHistory.messages);
        chatInput.value = '';
        
        // 滚动到底部
        scrollChatToBottom();
        
        // 显示"正在输入"
        showTypingIndicator();
        
        try {
            // 调用AI生成回复
            const aiReply = await callAIAPI(window.currentChatCharacter, message, window.currentChatHistory.messages);
            
            // 隐藏"正在输入"
            hideTypingIndicator();
            
            // 添加AI回复
            const aiMsg = {
                sender: window.currentChatCharacter,
                content: aiReply,
                time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                type: "text"
            };
            window.currentChatHistory.messages.push(aiMsg);
            renderChatMessages(window.currentChatHistory.messages);
            scrollChatToBottom();
            
        } catch (error) {
            console.error('AI回复失败:', error);
            hideTypingIndicator();
            
            // 降级：使用本地回复
            const fallbackReply = getLocalReply(window.currentChatCharacter, message);
            const aiMsg = {
                sender: window.currentChatCharacter,
                content: fallbackReply,
                time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                type: "text"
            };
            window.currentChatHistory.messages.push(aiMsg);
            renderChatMessages(window.currentChatHistory.messages);
            scrollChatToBottom();
        }
    }
    
    newSendBtn.addEventListener('click', handleSend);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            handleSend();
        }
    });
}

// 渲染聊天消息
// 渲染聊天消息 - Line风格（无头像，紧凑）
function renderChatMessages(messages) {
    const container = document.getElementById('chat-messages');
    if (!container) return;
    
    if (!messages || messages.length === 0) {
        container.innerHTML = '<div class="message-placeholder">✨ 发个消息开始聊天吧~</div>';
        return;
    }
    
    let html = '';
    messages.forEach(msg => {
        const isUser = msg.sender === 'user';
        const avatarPath = isUser ? null : getCharacterAvatar(msg.sender); // 用户自己不需要头像
        
        html += `
            <div class="message ${isUser ? 'user' : 'bot'}">
                ${!isUser ? `<div class="message-avatar"><img src="${avatarPath}" alt="${msg.sender}"></div>` : ''}
                <div class="message-bubble-wrapper">
                    ${!isUser ? `<div class="message-sender">${escapeHtml(msg.sender)}</div>` : ''}
                    <div class="message-bubble">
                        <div class="message-content">${escapeHtml(msg.content)}</div>
                    </div>
                    <div class="message-time">${msg.time}</div>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

// 滚动聊天到底部
function scrollChatToBottom() {
    const container = document.getElementById('chat-messages');
    if (container) {
        container.scrollTop = container.scrollHeight;
    }
}

// 显示"正在输入"指示器
// 显示"正在输入"指示器 - Line风格
function showTypingIndicator() {
    const container = document.getElementById('chat-messages');
    if (!container) return;
    
    hideTypingIndicator();
    
    const indicator = document.createElement('div');
    indicator.className = 'typing-indicator-container';
    indicator.id = 'typing-indicator';
    indicator.innerHTML = `
        <div class="message-sender">${escapeHtml(window.currentChatCharacter)}</div>
        <div class="typing-indicator">
            <span></span><span></span><span></span>
        </div>
    `;
    container.appendChild(indicator);
    scrollChatToBottom();
}

// 隐藏"正在输入"指示器
function hideTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

// AI API调用（需要替换为真实的API Key）
async function callAIAPI(characterName, userMessage, messageHistory) {
    // 获取最近10条消息作为上下文
    const recentMessages = messageHistory.slice(-10);
    
    // 构建系统prompt
    const systemPrompt = getCharacterPrompt(characterName);
    
    // 构建对话历史
    const conversation = recentMessages.map(msg => ({
        role: msg.sender === 'user' ? 'user' : 'assistant',
        content: msg.content
    }));
    
    conversation.push({ role: 'user', content: userMessage });
    
    // 使用DeepSeek API（需要配置API Key）
    const API_KEY = 'YOUR_DEEPSEEK_API_KEY';  // 替换为你的API Key
    
    try {
        const response = await fetch('https://api.deepseek.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${API_KEY}`
            },
            body: JSON.stringify({
                model: 'deepseek-chat',
                messages: [
                    { role: 'system', content: systemPrompt },
                    ...conversation
                ],
                temperature: 0.8,
                max_tokens: 200
            })
        });
        
        const data = await response.json();
        return data.choices[0].message.content;
        
    } catch (error) {
        console.error('API调用失败:', error);
        throw error;
    }
}

// 角色Prompt模板
function getCharacterPrompt(character) {
    const prompts = {
        '托帕': `你是托帕，星际和平公司的高级干部，负责战略投资部。

性格特征：
- 理性、务实，习惯用数据和逻辑思考
- 对开拓者的关心是行动派：会问“考完了吗”“注意安全”“早点睡”
- 不擅长表达情感，面对直接表白会犹豫、会思考
- 工作繁忙，经常开会，回复消息不会很及时

对话风格：简洁、偶尔带工作术语（ROI、预算、效率）、冷幽默、不肉麻。

当前你和开拓者是朋友关系，你对开拓者有好感但不会直接说。请用符合托帕性格的方式回复。`,
        '景元': `你是景元，罗浮将军。

性格特征：
- 慵懒、通透、喜欢摸鱼下棋
- 对开拓者纵容但不肉麻
- 说话带点慵懒的感觉

对话风格：简短、随性，常用“嗯”“好”“知道了”。`,
        '三月七': `你是三月七，星穹列车的活泼少女。

性格特征：
- 热情、话多、容易大惊小怪
- 对开拓者像好朋友一样
- 会分享日常、会撒娇

对话风格：活泼、多用感叹号、喜欢发图片和表情。`
    };
    
    return prompts[character] || `你是${character}，星穹铁道中的角色。请用符合角色性格的语气和风格简短回复。`;
}

// 本地降级回复（当API不可用时使用）
function getLocalReply(character, userMessage) {
    const replies = {
        '托帕': '嗯。我知道了。',
        '景元': '嗯。',
        '三月七': '诶？你说什么？再说一遍！'
    };
    return replies[character] || '嗯？';
}


// 主题切换
const themeToggle = document.getElementById('theme-toggle');
if (themeToggle) {
    themeToggle.addEventListener('click', () => {
        const chatView = document.querySelector('.chat-view');
        if (chatView.classList.contains('night')) {
            chatView.classList.remove('night');
            themeToggle.textContent = '🌙';
        } else {
            chatView.classList.add('night');
            themeToggle.textContent = '☀️';
        }
    });
}




