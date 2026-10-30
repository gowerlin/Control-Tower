# BMad Control Tower Portal

**網站：** <https://gowerlin.github.io/Control-Tower/>

BMad Control Tower（CT）的說明網站原始碼。CT 是檔案驅動的工單編排 skill 組，在 Claude Code 或 Codex 上運作：一個塔台 session 開工單、派工、收單，多個 Worker session 各自執行一張工單，所有決定都留在檔案裡。

網站用 [VitePress](https://vitepress.dev/) 建置，部署到 GitHub Pages（<https://gowerlin.github.io/Control-Tower/>）。

## 本機開發

需要 Node.js 24。

```bash
npm ci
npm run dev        # 開發伺服器（base 是 /）
npm run build      # 建置到 .vitepress/dist/
npm run preview    # 預覽建置結果
```

建置時讀的環境變數：

| 變數 | 用途 | 沒設定時 |
|---|---|---|
| `PORTAL_BASE` | 站點 base 路徑，例如 `/Control-Tower/` | `/` |
| `PORTAL_SITE_URL` | 站點完整網址（結尾有 `/`），用於 sitemap、分享卡片的絕對網址 | 不輸出 sitemap 與絕對網址，建置時印出警告 |
| `BAT_SITE_URL` | Better Agent Terminal 站的網址，Portal 連到 BAT 的連結都用它組 | 設定檔內的預設值 |

用 GitHub Pages 的網址在本機建置一次，可以確認資源路徑都帶 base：

```bash
PORTAL_BASE=/Control-Tower/ PORTAL_SITE_URL=https://<owner>.github.io/Control-Tower/ npm run build
```

## 目錄

| 路徑 | 內容 |
|---|---|
| `*.md`、`guide/`、`deep/`、`versions/`、`reference/` | 頁面 |
| `.vitepress/config.mts` | 站點設定、nav 與 sidebar |
| `.vitepress/theme/` | 主題與 Vue 元件 |
| `.vitepress/ct-release.json` | 內容基準版本：網站內容對應的 CT 版號、CT Guide 版號、發布日與下載檔名 |
| `data/compat.json` | 相容版本對照表的資料 |
| `data/bmad-guide.json` | BMad Guide Skill（`bmad-guide`）的版本資料：版號、對應的 BMad-Method 版號、發布日、發行檔名。版號跟 BMad-Method 走，不跟 CT，所以不放在 `ct-release.json` |
| `public/` | 原樣複製到站點根目錄的靜態檔（圖示、分享卡片圖） |
| `design/og-card.html` | 分享卡片圖 `public/og-card.png` 的原稿，不發布 |
| `scripts/` | 建置與維護用的腳本，見下節 |
| `lychee.toml` | 外部連結檢查（lychee）設定 |
| `.github/workflows/pages.yml` | GitHub Pages 建置與部署 |
| `.claude-plugin/`、`plugins/`（只在公開 repo） | plugin marketplace `control-tower`：CT plugin `ct`（8 個 skill）與 CT Guide plugin `ct-guide`。匯出時從 CT、CT Guide 的版本目錄產生，內容等同發版 zip；不要手改 |

## 內容基準版本與版本頁

網站內容以 `.vitepress/ct-release.json` 記錄的 CT 版本為準，頁尾與版本頁的版號都讀這個檔。

`versions/releases.md`（更版紀錄）與 `ct-release.json` 由維護者在本機用 `scripts/sync-ct-release.mjs <版號>` 從 CT 的原始碼與 CHANGELOG 產生後提交。這支腳本需要 CT 的原始碼目錄，本 repo 沒有，所以在這裡執行會失敗；CI 只建置、不重新產生版本頁。

## 腳本

| 腳本 | 用途 |
|---|---|
| `scripts/sync-ct-release.mjs` | 維護者本機用：CT 發版後同步版本資料與更版紀錄頁，產出後自動掃描；要先設定下面兩個變數 |
| `scripts/deid-scan.mjs` | 去識別掃描：找出不該公開的路徑、權杖、識別碼等，掃描 `.md`、`.yml`、`.gitignore` 等文字檔（二進位檔跳過）。`npm run deid` 掃原始檔與 `.vitepress/dist/`，並加掃內部編號（`--internal-ids`：工單、決策等編號對全站生效，頁面上的範例編號另列允許清單；commit SHA、BAT 契約條目等只對更版紀錄生效）。plugin marketplace 的 repo 名稱只在 CT 發行物（CT 與 Guide 的 skill 檔、CT 的 `CHANGELOG.md`）裡放行，名稱讀 `.vitepress/config.mts` 的設定常數；頁面要寫就用設定常數組出 |
| `scripts/build-plugin-marketplace.mjs` | 維護者本機用：從 CT 與 CT Guide 的版本目錄產生 plugin marketplace（`.claude-plugin/marketplace.json`、`plugins/ct`、`plugins/ct-guide`）。檢查 8 個 CT skill 與 Guide 的版號註解等於指定版號，`plugin.json` 的 `version` 由版號產生；beta 不上架。需要 CT 的原始碼目錄，不在公開 repo；匯出公開 repo 時會用它產生 marketplace |
| `scripts/build-artifact.mjs` | `npm run build:artifact`：建置不需要伺服器路由的靜態預覽包（`dist-artifact/`），自我檢查後對預覽包跑去識別掃描（含 `--internal-ids`），命中就失敗；要先設定下面兩個變數 |

去識別掃描要用的私有詞表與允許清單不在本 repo。以環境變數指定兩個檔案的路徑（也可以改用 `--terms`／`--allow` 參數，參數優先）：

| 變數 | 內容 |
|---|---|
| `PORTAL_DEID_TERMS` | 私有詞表的路徑 |
| `PORTAL_DEID_ALLOW` | 允許清單（可出現的網址常數）的路徑 |

```bash
export PORTAL_DEID_TERMS=<詞表路徑> PORTAL_DEID_ALLOW=<允許清單路徑>
npm run deid
```

沒有設定時 `npm run deid`、`npm run build:artifact` 與 `sync-ct-release.mjs` 會報錯結束，不會略過掃描。

## 註解的寫法

會匯出的檔（頁面、元件、CSS、腳本）會公開，讀者只看得到公開文件。這些檔的註解：

- 不寫規劃文件的章節號、題號、路徑簡寫，也不寫工單或決策編號。
- 要引用出處，就寫公開文件的實際路徑或文件名，例如「BMad Control Tower 安裝(升級)與使用指南 § 4.1」「`control-tower/references/yolo-mode.md` § 斷點判準」。

去識別掃描只擋得住固定格式的編號，擋不住上面這些寫法，要靠寫的人自己避開。

## 部署

`main` 分支有 push，或在 Actions 頁手動執行 **Pages** workflow 時：

1. `npm ci`、`npm run build`（`PORTAL_BASE=/Control-Tower/`，`PORTAL_SITE_URL` 由 repo 擁有者組出）
2. 上傳建置結果，部署到 GitHub Pages
3. 另外跑 lychee 外部連結檢查；只警告，不擋部署

**Pages 尚未啟用時**，workflow 只建置與檢查連結，部署步驟會跳過。到 Settings → Pages → Source 選 **GitHub Actions** 啟用後，回 Actions 頁重新執行 **Pages** workflow 即可部署。

本 repo 的內容由維護者從另一個 repo 匯出後推送；匯出時會對匯出的全部檔案跑去識別掃描（含 `--internal-ids`），沒有通過就不推送。請不要直接在這裡改頁面，改動會在下次匯出時被覆蓋。

匯出時也會產生 plugin marketplace（`.claude-plugin/`、`plugins/`），放在 repo 根目錄，讓 Claude Code 與 Codex 可以直接把這個 repo 加成 marketplace。plugin 內容等同發版 zip，去識別比照發版 zip 的規則另外掃。只改這兩個目錄的 push 不會觸發 Pages 建置（`pages.yml` 的 `paths-ignore`）。

## 授權

網站原始碼，以及 GitHub Releases 中的 Control Tower（CT）、CT Guide、BMad Guide Skill（`bmad-guide`）三組 skill，都以 MIT License 授權發布，見 [`LICENSE`](LICENSE)。

BMad-Method 的授權與商標聲明見 [`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md)。
