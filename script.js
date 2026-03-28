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

  if (!posts || posts.length === 0) {
    container.innerHTML =
      '<div class="loading">暂无动态，星穹列车正在检修~</div>';
    return;
  }

  let html = "";
  posts.forEach((post) => {
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
          <img class="post-avatar" src="${getAvatarPath(post.author)}" alt="${post.author}">
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
