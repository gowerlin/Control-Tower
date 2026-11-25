<template>
  <!-- 契約 v2：CT 寫、BAT 讀、你回答（對應 CT Guide diagrams.md § 21；文案對齊 control-tower/references/memory-protocol.md § 契約 v2 欄位） -->
  <figure class="todo-flow" aria-label="契約 v2：CT 寫、BAT 讀、你回答">
    <ol class="tf-steps">
      <li class="tf-step">
        <p class="tf-label">1　塔台寫入</p>
        <ul class="tf-row">
          <li class="tf-box is-tower">
            <p class="tf-who">斷點／提問升級</p>
            <p class="tf-text">停下來等你決定 → 寫一筆 <code>U-n</code>，工單加 <code>waiting_user</code></p>
          </li>
          <li class="tf-box is-tower">
            <p class="tf-who">塔台收單</p>
            <p class="tf-text">回報區的待實機、待你執行項目 → 各寫一筆 <code>A-n</code></p>
          </li>
        </ul>
      </li>
      <li class="tf-step">
        <p class="tf-label">2　寫在檔案裡</p>
        <ul class="tf-row is-single">
          <li class="tf-box is-file">
            <p class="tf-who"><code>_tower-state.md</code> frontmatter</p>
            <p class="tf-text"><code>awaiting_user</code>（<code>U-n</code>）、<code>user_actions</code>（<code>A-n</code>）、<code>reminders</code></p>
          </li>
        </ul>
      </li>
      <li class="tf-step">
        <p class="tf-label">3　兩個地方看得到</p>
        <ul class="tf-row">
          <li class="tf-box is-bat">
            <p class="tf-who">BAT「待辦」分頁</p>
            <p class="tf-text">唯讀顯示；需要 BAT <code>&gt;= 0.8.0-pre.3</code></p>
          </li>
          <li class="tf-box">
            <p class="tf-who">塔台回覆的最後一行</p>
            <p class="tf-text">有項目在等你時每次重列；任何終端都有</p>
          </li>
        </ul>
      </li>
      <li class="tf-step">
        <p class="tf-label">4　你回答</p>
        <ul class="tf-row is-single">
          <li class="tf-box is-you">
            <p class="tf-who">在塔台分頁打一行（或用待辦分頁的回答框）</p>
            <p class="tf-text"><code>U-3：B</code>、<code>A-2：完成</code> → 塔台移除那一筆並記決策日誌</p>
          </li>
        </ul>
      </li>
    </ol>
    <p class="tf-note"><b>BAT 從不改 CT 的檔。</b>清單裡的項目消失，就是已經結了；兩邊各只有一個寫入者。</p>
  </figure>
</template>
