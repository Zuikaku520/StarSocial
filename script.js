let isLoadingPost = false;
let tempPostId = null;

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
    姬子: "jizi.png",
    景元: "jy.png",
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
    开拓者:"trailblazer-avatar.png",
    花火:"hanabi.png",
    卡芙卡:"kafk.png",
    黑塔:"herta.png",
    知更鸟:"robin.png",
    符玄:"fuxuan.png",
    阮·梅:"rm.gif",
    流萤:"firefly.png",
    黄泉:"momo.png",
    波提欧:"bto.png",
    银枝:"yzh.png",
    青雀:"qque.png"
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

  // 如果有语音文件，添加播放按钮
  if (comment.voice_url && comment.voice_url !== null) {
    // 拼接正确的路径
    const voicePath = `voices/${comment.voice_url}`;
      html += `
          <div class="voice-player">
              <button class="play-voice-btn" data-voice="${escapeHtml(voicePath)}">🔊 语音</button>
          </div>
      `;
  }

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

  if (!posts || posts.length === 0) {
    container.innerHTML =
      '<div class="loading">暂无动态，星穹列车正在检修~</div>';
    return;
  }


   // 按 id 从大到小排序（最新的在前）
  const sortedPosts = [...posts].sort((a, b) => b.id - a.id);
  

  let html = "";
  sortedPosts.forEach((post) => {
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

    // 构建评论区（使用递归函数）
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

    // 最终卡片HTML
    html += `
      <div class="post-card">
        <div class="post-header">
          <img class="post-avatar" src="${post.avatar|| getAvatarPath(post.author)}" alt="${post.author}">
          <div class="post-author">
            <div class="post-name">${escapeHtml(post.author)}</div>
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


document.getElementById('publishBtn').addEventListener('click', async () => {
    if (isLoadingPost) return;
    const content = document.getElementById('postContent').value.trim();
    if (!content) {
        showMessage('请填写内容', 'error');
        return;
    }
    
    isLoadingPost = true;
    const btn = document.getElementById('publishBtn');
    const originalText = btn.innerText;
    btn.innerText = '发布中...';
    btn.disabled = true;
    
    // 显示临时动态（可选）
    // 先添加一个占位卡片
    const tempId = 'temp_' + Date.now();
    addTempPost(tempId, content);
    
    try {
        const response = await fetch('http://localhost:5000/post', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content: content, image: 'images/default.jpg' })
        });
        const result = await response.json();
        if (result.success) {
            // 移除临时卡片
            removeTempPost(tempId);
            // 将新动态插入到列表顶部
            insertPostToTop(result.post);
            showMessage('发布成功！', 'success');
            document.getElementById('postContent').value = '';
            // 清空图片选择（如果有）
            document.getElementById('postImage').value = '';
        } else {
            removeTempPost(tempId);
            showMessage('发布失败：' + (result.error || '未知错误'), 'error');
        }
    } catch (err) {
        removeTempPost(tempId);
        showMessage('网络错误，请稍后重试', 'error');
    } finally {
        isLoadingPost = false;
        btn.innerText = originalText;
        btn.disabled = false;
    }
});

function addTempPost(tempId, content) {
    const container = document.getElementById('posts-container');
    const tempCard = document.createElement('div');
    tempCard.id = tempId;
    tempCard.className = 'post-card temp-post';
    tempCard.innerHTML = `
        <div class="post-header">
            <img class="post-avatar" src="images/avatars/trailblazer-avatar.png" alt="开拓者">
            <div class="post-author">
                <div class="post-name">开拓者</div>
                <div class="post-time">刚刚</div>
            </div>
        </div>
        <div class="post-content">${escapeHtml(content)}</div>
        <div class="loading-comments">AI 正在思考评论中 ✨</div>
    `;
    container.insertBefore(tempCard, container.firstChild);
    
}

function removeTempPost(tempId) {
    const el = document.getElementById(tempId);
    if (el) el.remove();
}

function insertPostToTop(post) {
    fetch("data.json")
        .then((response) => response.json())
        .then((data) => {
            renderPosts(data.posts);
            setTimeout(() => {
                const newCard = document.getElementById(`post-${post.id}`);
                if (newCard) newCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 100);
        })
        .catch(err => console.error("重新加载失败:", err));
}



// 显示提示消息
function showMessage(msg, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast-message ${type}`;
    toast.innerText = msg;
    toast.style.position = 'fixed';
    toast.style.bottom = '20px';
    toast.style.left = '50%';
    toast.style.transform = 'translateX(-50%)';
    toast.style.background = type === 'error' ? '#ff4444' : '#00D4FF';
    toast.style.color = 'white';
    toast.style.padding = '10px 20px';
    toast.style.borderRadius = '40px';
    toast.style.zIndex = '9999';
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}


// 渲染单条朋友圈卡片（用于动态插入）
function renderSinglePost(post) {
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
        commentsHtml = '<div class="comment" style="color:rgba(232,239,247,0.5);">暂无评论</div>';
    }

    // 构建图片列表
    let imagesHtml = "";
    if (post.images && post.images.length > 0) {
        imagesHtml = `<div class="post-images"><img class="post-image" src="${post.images[0]}" alt="朋友圈图片"></div>`;
    }

    // 获取头像路径（开拓者特殊处理）
    let avatarPath = post.avatar;
    if (!avatarPath || avatarPath === "") {
        avatarPath = getAvatarPath(post.author);
    }

    // 最终卡片HTML
    return `
        <div class="post-card">
            <div class="post-header">
                <img class="post-avatar" src="${avatarPath}" alt="${post.author}">
                <div class="post-author">
                    <div class="post-name">${escapeHtml(post.author)}</div>
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
}

// 语音播放事件
document.addEventListener('click', function(e) {
    if (e.target.classList && e.target.classList.contains('play-voice-btn')) {
        const audioUrl = e.target.getAttribute('data-voice');
        if (audioUrl) {
            const audio = new Audio(audioUrl);
            audio.play().catch(err => console.error('播放失败:', err));
        }
    }
});