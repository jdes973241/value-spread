# 價值股與成長股的估值價差 (Value Spread) 互動觀測面板

本部署包內含完整單頁式網頁 (`index.html`) 以及每月自動從達特茅斯學院 **Kenneth R. French Data Library** 拉取最新 `2x3 Size & Book-to-Market` 官方 CSV 並更新網站的 **GitHub Actions 自動化腳本**。

## 方式一：10 秒鐘免費拖曳上架（最快取得公開分享網址）
1. 前往 **Netlify Drop** (`https://app.netlify.com/drop`) 或 **Cloudflare Pages** (`https://pages.cloudflare.com`)。
2. 直接將本 `.zip` 壓縮包（或解壓縮後的資料夾）拖曳進網頁上傳框。
3. 5 秒內即可獲得永久免費的 `https://xxxx.netlify.app` 或 `https://xxxx.pages.dev` 公開分享網址！

## 方式二：GitHub Pages 免費架站 ＋ 每月雲端自動更新數據（零維護）
1. 在 GitHub 建立一個新的公開儲存庫（Repository），上傳本壓縮包解壓縮後的所有檔案（含 `index.html`、`data/`、`scripts/`、`.github/workflows/`）。
2. 進入該儲存庫的 **Settings → Pages**，將 **Build and deployment → Source** 設為 **GitHub Actions**。
3. 完成！你的網站將自動發布於 `https://<你的帳號>.github.io/<專案名>/`，且每月 5 號與 18 號 GitHub Actions 會自動執行 `scripts/update_monthly_data.py` 從 Ken French 資料庫拉取最新月份數據並更新網頁。
