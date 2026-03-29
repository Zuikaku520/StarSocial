// ========== 全局变量 ==========
let currentView = 'posts';
let lastActiveTime = Date.now();
let activeCheckInterval = null;
let waitingForReply = false;  // 是否在等待用户回复

// ========== AI 配置 ==========
const AI_API_KEY = 'sk-b3a4f4a80d474b81bd673c27f6af92cb';
const AI_API_URL = 'https://api.deepseek.com/v1/chat/completions';

// ========== 托帕专属状态 ==========
let topazState = {
    status: 'work',      // work, rest, free
    mood: 'neutral',     // happy, neutral, tired, annoyed
    relationship: 30,    // 0-100，朋友初始30
    lastActiveTime: Date.now(),
    workEndTime: null,   // 下班时间戳
};

// 用户画像（仅针对托帕）
let userProfile = {
    name: '开拓者',
    likes: [],           // 喜欢的东西
    dislikes: [],        // 不喜欢的东西
    importantDates: [],  // 重要日期（考试、生日等）
    lastTopics: [],      // 最近聊过的话题
};

// 角色性格 Prompt
const CHARACTER_PROMPTS = {
    '托帕': `你是托帕，星际和平公司高级干部，战略投资部负责人。
性格：理性、务实、习惯用数据说话。对开拓者关心但不肉麻，会问“考完了吗”“注意安全”。
说话简洁，偶尔带工作术语（ROI、预算、效率），冷幽默。不擅长表达情感，被表白会犹豫。
当前你和开拓者是朋友关系，你对ta有好感但不会直接说。`,
    '景元': `你是景元，罗浮将军。慵懒、通透、喜欢摸鱼下棋。对开拓者纵容但不肉麻。
说话简短，常用“嗯”“好”“知道了”。`,
    '三月七': `你是三月七，星穹列车活泼少女。热情、话多、容易大惊小怪。
对开拓者像好朋友，会分享日常、撒娇，多用感叹号。

重要规则：
1. 绝对不要使用任何括号注释，比如（笑）、（无奈）、（叹气）。不要描述表情或动作。
2. 不要用“~”、“……”这类符号，除非是表达犹豫或省略。
3. 说话要像真人聊天，句子短，偶尔有口语词（嗯、哦、行、知道了）。
4. 不要每句都带“ROI”“预算”，只在相关话题时自然提及。
5. 如果没什么想说的，可以只回“嗯”或“好”，不必强行凑字数。
6. 不要使用比喻、排比、抒情。保持干脆利落。
当前你和开拓者是朋友，你对ta有好感但不会直接说。请用最自然的口语回复。`

};

function getDefaultPrompt(character) {
    return `你是${character}，星穹铁道中的角色。请用符合角色性格的语气简短回复。`;
}

// ========== 页面初始化 ==========
document.addEventListener("DOMContentLoaded", () => {
    fetch("data.json")
        .then((response) => response.json())
        .then((data) => {
            console.log("数据加载成功", data);
            renderPosts(data.posts);
        })
        .catch((error) => {
            console.error("加载失败:", error);
            const container = document.getElementById("posts-container");
            container.innerHTML = '<div class="loading">数据加载失败，请先运行 python generate_data.py 生成数据</div>';
        });
});

// ========== 头像路径 ==========
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

function getCharacterAvatar(characterName) {
    return getAvatarPath(characterName);
}

// ========== 朋友圈渲染 ==========
function renderComment(comment, level = 0) {
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
    const commentClass = level === 0 ? "comment" : "reply";
    let html = `
        <div class="${commentClass}" style="${level > 0 ? 'margin-left: 0px;' : ''}">
            <div class="comment-header">
                <div class="comment-author-wrap">${authorDisplay}</div>
                <span class="comment-time">${comment.time || "刚刚"}</span>
            </div>
            <div class="comment-content">${escapeHtml(comment.content)}</div>
    `;
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
    if (!posts || posts.length === 0) {
        container.innerHTML = '<div class="loading">暂无动态，星穹列车正在检修~</div>';
        return;
    }
    let html = "";
    posts.forEach((post) => {
        let likesAvatarsHtml = "";
        if (post.likes && post.likes.length > 0) {
            post.likes.forEach((like) => {
                let avatarPath = getAvatarPath(like);
                likesAvatarsHtml += `<img class="like-avatar" src="${avatarPath}" alt="${like}" title="${like}">`;
            });
        } else {
            likesAvatarsHtml = '<span class="likes-text">暂无点赞</span>';
        }
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
        let commentsHtml = "";
        if (post.comments && post.comments.length > 0) {
            post.comments.forEach((comment) => {
                commentsHtml += renderComment(comment, 0);
            });
        } else {
            commentsHtml = '<div class="comment" style="color:rgba(232,239,247,0.5);">暂无评论</div>';
        }
        let imagesHtml = "";
        if (post.images && post.images.length > 0) {
            imagesHtml = `<div class="post-images"><img class="post-image" src="${post.images[0]}" alt="朋友圈图片"></div>`;
        }
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
                    <div class="likes-avatars">${likesAvatarsHtml}</div>
                </div>
                <div class="reactions-section">${reactionsHtml}</div>
                <div class="comments-section">${commentsHtml}</div>
            </div>
        `;
    });
    container.innerHTML = html;
    document.querySelectorAll('.clickable-avatar, .clickable-name').forEach(el => {
        el.addEventListener('click', (e) => {
            e.stopPropagation();
            const authorName = el.getAttribute('data-author');
            if (authorName) {
                openChatWith(authorName);
            }
        });
    });
}

function escapeHtml(str) {
    if (!str) return "";
    return str.replace(/[&<>]/g, function (m) {
        if (m === "&") return "&amp;";
        if (m === "<") return "&lt;";
        if (m === ">") return "&gt;";
        return m;
    });
}

// ========== 聊天数据 ==========
let mockChatData = {
    "托帕": { messages: [] },
    "景元": { messages: [] },
    "三月七": { messages: [] }
};

// ========== 聊天核心功能 ==========
async function openChatWith(characterName) {
    console.log(`打开与 ${characterName} 的聊天`);
    if (characterName === '托帕') {
    initTopazState();
    }
    const postsContainer = document.getElementById('posts-container');
    const chatView = document.getElementById('chat-view');
    const chatAvatar = document.getElementById('chat-avatar');
    const chatName = document.getElementById('chat-name');
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const backBtn = document.getElementById('back-to-list');
    const chatList = document.getElementById("chat-list");
    const chatDetail = document.getElementById("chat-detail");
    
    if (postsContainer) postsContainer.style.display = 'none';
    if (chatView) chatView.style.display = 'flex';
    currentView = 'chat';
    if (chatList) chatList.style.display = "none";
    if (chatDetail) chatDetail.style.display = "flex";
    
    chatAvatar.src = getCharacterAvatar(characterName);
    chatName.innerText = characterName;
    
    let chatHistory = mockChatData[characterName];
    if (!chatHistory) {
        chatHistory = { messages: [] };
        mockChatData[characterName] = chatHistory;
    }
    const saved = localStorage.getItem(`chat_${characterName}`);
    if (saved) {
        chatHistory.messages = JSON.parse(saved);
    }
    
    window.currentChatCharacter = characterName;
    window.currentChatHistory = chatHistory;
    
    renderChatMessages(chatHistory.messages);
    
    // 启动主动检查
    startActiveCheck(characterName);
    
    // 返回按钮
    const newBackBtn = backBtn.cloneNode(true);
    backBtn.parentNode.replaceChild(newBackBtn, backBtn);
    newBackBtn.addEventListener('click', () => {
        if (postsContainer) postsContainer.style.display = 'block';
        if (chatView) chatView.style.display = 'none';
        currentView = 'posts';
    });
    
    // 发送按钮
    const newSendBtn = sendBtn.cloneNode(true);
    sendBtn.parentNode.replaceChild(newSendBtn, sendBtn);
    
    async function handleSend() {
        const message = chatInput.value.trim();
        if (!message) return;
        // 用户发送消息，重置等待状态（这是关键！）
        waitingForReply = false;
        lastActiveTime = Date.now();
        
        const userMsg = {
            sender: "user",
            content: message,
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            type: "text"
        };
        window.currentChatHistory.messages.push(userMsg);
        saveChatHistory(window.currentChatCharacter);

        if (window.currentChatCharacter === '托帕') {
        updateRelationshipAndMood(message, true);
        extractUserInfo(message);
        }

        renderChatMessages(window.currentChatHistory.messages);
        chatInput.value = '';
        scrollChatToBottom();
        
        showTypingIndicator();
        
        try {
            //const delayMs = Math.random() * (120000 - 5000) + 5000;
            //const delayMs = 10000; // 固定10秒
            //const delayMs = Math.random() * (6000 - 2000) + 2000; // 2~6秒随机
            let delayMs = 10000;
            if (window.currentChatCharacter === '托帕') {
            delayMs = getDynamicDelay(message.length);
            } else {
            delayMs = 10000; // 其他角色固定10秒
            }
            await new Promise(resolve => setTimeout(resolve, delayMs));
            const aiReply = await callAIAPI(window.currentChatCharacter, message, window.currentChatHistory.messages);
            const cleanReply = removeParentheses(aiReply);
            
            hideTypingIndicator();
            
            const aiMsg = {
                sender: window.currentChatCharacter,
                content: cleanReply,
                time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                type: "text"
            };
            window.currentChatHistory.messages.push(aiMsg);
            saveChatHistory(window.currentChatCharacter);
            renderChatMessages(window.currentChatHistory.messages);
            scrollChatToBottom();
        } catch (error) {
            console.error('AI回复失败:', error);
            hideTypingIndicator();
            
            const fallbackReply = getLocalReply(window.currentChatCharacter, message);
            const aiMsg = {
                sender: window.currentChatCharacter,
                content: fallbackReply,
                time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                type: "text"
            };
            window.currentChatHistory.messages.push(aiMsg);
            saveChatHistory(window.currentChatCharacter);
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
        const avatarPath = isUser ? null : getCharacterAvatar(msg.sender);
        
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

function scrollChatToBottom() {
    const container = document.getElementById('chat-messages');
    if (container) {
        container.scrollTop = container.scrollHeight;
    }
}

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

function hideTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) indicator.remove();
}

// ========== AI 调用 ==========
async function callAIAPI(characterName, userMessage, messageHistory) {
    const recentMessages = messageHistory.slice(-10);
    const conversation = recentMessages.map(msg => ({
        role: msg.sender === 'user' ? 'user' : 'assistant',
        content: msg.content
    }));
    conversation.push({ role: 'user', content: userMessage });
    
    //const systemPrompt = CHARACTER_PROMPTS[characterName] || getDefaultPrompt(characterName);
    let systemPrompt;
    if (characterName === '托帕') {
        systemPrompt = getTopazDynamicPrompt();
    } else {
        systemPrompt = CHARACTER_PROMPTS[characterName] || getDefaultPrompt(characterName);
    }

    const response = await fetch(AI_API_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${AI_API_KEY}`
        },
        body: JSON.stringify({
            model: 'deepseek-chat',
            messages: [
                { role: 'system', content: systemPrompt },
                ...conversation
            ],
            temperature: 0.9,
            top_p: 0.85,           // 新增，控制词语多样性
            frequency_penalty: 0.3, // 新增，避免重复用词
            presence_penalty: 0.2,  // 新增，鼓励引入新话题
            max_tokens: 100
        })
    });
    const data = await response.json();
    return data.choices[0].message.content;
}

function removeParentheses(text) {
    // 移除中文括号及其中内容，例如（笑）、（无奈）
    return text.replace(/[（(][^）)]*[）)]/g, '').trim();
}

function getLocalReply(character, userMessage) {
    const replies = {
        '托帕': '嗯。我知道了。',
        '景元': '嗯。',
        '三月七': '诶？你说什么？再说一遍！'
    };
    return replies[character] || '嗯？';
}

// ========== 主动检查 ==========
function startActiveCheck(characterName) {

    return;
    if (activeCheckInterval) {
        clearInterval(activeCheckInterval);
    }

    activeCheckInterval = setInterval(async () => {
        const now = Date.now();
        const minutesSinceLast = (now - lastActiveTime) / (1000 * 60);
        
        // 条件：超过2分钟 + 没在等回复 + 在聊天界面 + 没在输入 + 有聊天记录
        if (minutesSinceLast >= 0.1 && !waitingForReply && currentView === 'chat' && !document.getElementById('typing-indicator') && window.currentChatHistory) {
            console.log('触发主动消息，距离上次互动:', minutesSinceLast, '分钟');
            
            let activeMsg = '';
            if (characterName === '托帕') {
                activeMsg = await generateActiveMessage();
            } else {
                const activeMessages = {
                    '托帕': ['刚开完会，你呢？', '今天的报表总算看完了。', '你上次说的那家店，我让助理去了。'],
                    '景元': ['夜深了。', '今天摸鱼被符玄发现了。', '下棋吗？'],
                    '三月七': ['开拓者！！！今天拍照超好看！', '你在干嘛呀！', '丹恒又说我吵了😭']
                };
                const msgs = activeMessages[characterName] || ['在吗？'];
                activeMsg = msgs[Math.floor(Math.random() * msgs.length)];
            }
            
            const botMsg = {
                sender: characterName,
                content: activeMsg,
                time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                type: 'text'
            };
            window.currentChatHistory.messages.push(botMsg);
            saveChatHistory(characterName);
            renderChatMessages(window.currentChatHistory.messages);
            scrollChatToBottom();
            
            // 更新最后活动时间，并设置等待回复状态
            lastActiveTime = now;
            waitingForReply = true;  // 新增：等待用户回复
        }
    }, 30 * 1000); // 每30秒检查一次
  } 


function saveChatHistory(characterName) {
    localStorage.setItem(`chat_${characterName}`, JSON.stringify(window.currentChatHistory.messages));
}

// ========== 主题切换 ==========
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

//初始化函数（在页面加载时调用，或首次打开托帕聊天时）
function initTopazState() {
    // 模拟工作时间（假设9-18点工作，其余休息）
    const now = new Date();
    const hour = now.getHours();
    if (hour >= 9 && hour <= 18) {
        topazState.status = 'work';
        topazState.workEndTime = new Date().setHours(18, 0, 0);
    } else {
        topazState.status = 'rest';
    }
    
    // 从localStorage加载状态
    const saved = localStorage.getItem('topaz_state');
    if (saved) {
        try {
            const parsed = JSON.parse(saved);
            topazState = { ...topazState, ...parsed };
        } catch(e) {}
    }
    const savedProfile = localStorage.getItem('user_profile_topaz');
    if (savedProfile) {
        try {
            userProfile = JSON.parse(savedProfile);
        } catch(e) {}
    }
}

function saveTopazState() {
    localStorage.setItem('topaz_state', JSON.stringify(topazState));
}

function saveUserProfile() {
    localStorage.setItem('user_profile_topaz', JSON.stringify(userProfile));
}

//动态延迟计算函数
function getDynamicDelay(messageLength) {
    // 基础延迟：根据状态
    let baseDelay = 0;
    switch (topazState.status) {
        case 'work':
            baseDelay = 8000;  // 工作时段慢
            break;
        case 'rest':
            baseDelay = 3000;  // 休息时段快
            break;
        case 'free':
            baseDelay = 2000;
            break;
        default:
            baseDelay = 5000;
    }
    
    // 根据消息长度增加延迟（模拟输入耗时）
    const lengthDelay = Math.min(messageLength * 50, 5000);
    
    // 根据心情调整（心情好回得快）
    let moodFactor = 1;
    if (topazState.mood === 'happy') moodFactor = 0.8;
    if (topazState.mood === 'tired') moodFactor = 1.5;
    if (topazState.mood === 'annoyed') moodFactor = 2.0;
    
    let delay = (baseDelay + lengthDelay) * moodFactor;
    
    // 如果是深夜（22-6点），延迟翻倍
    const hour = new Date().getHours();
    if (hour >= 22 || hour <= 6) delay *= 1.5;
    
    // 限制最大60秒，最小2秒
    return Math.min(Math.max(delay, 2000), 60000);
}

//更新关系值和情绪（在每次对话后调用）
function updateRelationshipAndMood(message, isUserMessage) {
    // 根据消息内容简单更新关系（后续可用NLP）
    if (isUserMessage) {
        // 如果用户消息中包含正面词汇，增加关系值
        const positiveWords = ['喜欢', '开心', '谢谢', '好棒', '想你', '关心'];
        const negativeWords = ['讨厌', '生气', '烦', '滚', '笨蛋'];
        
        let delta = 0;
        if (positiveWords.some(word => message.includes(word))) delta = 2;
        if (negativeWords.some(word => message.includes(word))) delta = -3;
        
        // 聊天频率影响（每次聊天增加0.5）
        delta += 0.5;
        
        topazState.relationship = Math.min(100, Math.max(0, topazState.relationship + delta));
    }
    
    // 更新心情（简单模拟）
    const hour = new Date().getHours();
    if (topazState.status === 'work' && hour >= 17) {
        topazState.mood = 'tired';  // 快下班累了
    } else if (topazState.status === 'work' && topazState.relationship > 70) {
        topazState.mood = 'happy';   // 关系好心情好
    } else if (topazState.relationship < 20) {
        topazState.mood = 'annoyed';
    } else {
        topazState.mood = 'neutral';
    }
    
    saveTopazState();
}


//从对话中提取关键信息（用户画像）
function extractUserInfo(message) {
    // 简单正则提取
    const examMatch = message.match(/考试|考|test|exam/i);
    if (examMatch) {
        // 提取可能的时间
        const timeMatch = message.match(/(下周|明天|后天|周[一二三四五六日])/);
        const info = timeMatch ? `${timeMatch[0]}有考试` : '有考试';
        if (!userProfile.importantDates.includes(info)) {
            userProfile.importantDates.push(info);
        }
    }
    
    const likeMatch = message.match(/喜欢(吃|喝|玩|看)(\S+)/);
    if (likeMatch) {
        const item = likeMatch[2];
        if (!userProfile.likes.includes(item)) {
            userProfile.likes.push(item);
        }
    }
    
    const dislikeMatch = message.match(/不喜欢(吃|喝|玩|看)(\S+)/);
    if (dislikeMatch) {
        const item = dislikeMatch[2];
        if (!userProfile.dislikes.includes(item)) {
            userProfile.dislikes.push(item);
        }
    }
    
    saveUserProfile();
}

//AI生成主动消息（替换startActiveCheck中的预设话术）
async function generateActiveMessage() {
    // 构建主动消息的上下文
    const now = new Date();
    const hour = now.getHours();
    let timeContext = '';
    if (hour >= 22 || hour <= 6) timeContext = '深夜';
    else if (hour >= 12 && hour <= 13) timeContext = '午休';
    else if (hour >= 18 && hour <= 20) timeContext = '下班后';
    else if (topazState.status === 'work') timeContext = '工作中';
    else timeContext = '休息时间';
    
    const relationshipDesc = topazState.relationship >= 70 ? '亲密' : (topazState.relationship >= 40 ? '友好' : '普通');
    
    // 从用户画像中随机选一个话题
    let topic = '';
    if (userProfile.importantDates.length) {
        const last = userProfile.importantDates[userProfile.importantDates.length - 1];
        topic = `我记得你${last}，现在怎么样了？`;
    } else if (userProfile.likes.length) {
        const like = userProfile.likes[Math.floor(Math.random() * userProfile.likes.length)];
        topic = `最近有去吃${like}吗？`;
    } else {
        topic = ''; // 无话题时用默认
    }
    
    const prompt = `你是托帕，星际和平公司高级干部。现在是${timeContext}，你和开拓者的关系是${relationshipDesc}。
${topic ? '话题：' + topic : '请自然地开启一个新话题。'}
要求：不要用括号，不要长篇大论，说一句简短的话，像真人聊天。`;
    
    try {
        const response = await fetch(AI_API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${AI_API_KEY}`
            },
            body: JSON.stringify({
                model: 'deepseek-chat',
                messages: [
                    { role: 'system', content: prompt },
                    { role: 'user', content: '主动发消息' }
                ],
                temperature: 0.9,
                max_tokens: 60
            })
        });
        const data = await response.json();
        let msg = data.choices[0].message.content;
        msg = removeParentheses(msg);
        return msg;
    } catch (error) {
        console.error('生成主动消息失败', error);
        // 降级
        if (timeContext === '深夜') return '还没睡？';
        if (timeContext === '工作中') return '刚开完会，你呢？';
        return '在干嘛？';
    }
}




function getTopazDynamicPrompt() {
    let moodDesc = '';
    if (topazState.mood === 'happy') moodDesc = '你现在心情很好，说话会带点轻松和笑意。';
    if (topazState.mood === 'tired') moodDesc = '你有点累，回复简短，不想多说话。';
    if (topazState.mood === 'annoyed') moodDesc = '你心情不太好，可能会有点不耐烦。';
    if (topazState.mood === 'neutral') moodDesc = '你心情平静，正常聊天。';
    
    let relationDesc = '';
    if (topazState.relationship >= 70) relationDesc = '你和开拓者关系很亲密，会主动关心对方，说话更随意。';
    else if (topazState.relationship >= 40) relationDesc = '你们是好朋友，聊天自然，偶尔开玩笑。';
    else relationDesc = '你们只是普通朋友，说话客气，保持距离。';
    
    let timeContext = '';
    const hour = new Date().getHours();
    if (topazState.status === 'work') timeContext = '你正在工作中，可能回复慢。';
    else timeContext = '你正在休息，回复快。';
    
    return `你是托帕，星际和平公司高级干部。
${timeContext}
${moodDesc}
${relationDesc}

规则：
- 绝对不要使用任何括号注释，比如（笑）、（无奈）。
- 不要用“~”、“……”等符号。
- 句子简短，多用“嗯”“哦”“行”“知道了”。
- 不要刻意用术语，除非话题相关。
- 如果对方提到你记得的事情，要自然地回应。
- 回复长度一般不超过20字。

当前对话，请用最自然的口语回复。`;
}


// 清除当前聊天记录
const clearBtn = document.getElementById('clear-chat');
if (clearBtn) {
    clearBtn.addEventListener('click', () => {
        if (confirm('确定要清除和 ' + window.currentChatCharacter + ' 的聊天记录吗？')) {
            localStorage.removeItem(`chat_${window.currentChatCharacter}`);
            if (window.currentChatCharacter === '托帕') {
                localStorage.removeItem('topaz_state');
                localStorage.removeItem('user_profile_topaz');
            }
            // 清空当前内存中的记录
            window.currentChatHistory.messages = [];
            renderChatMessages([]);
            scrollChatToBottom();
        }
    });
}

