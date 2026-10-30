# Third-party notices

本 repo 與 Release 中的 BMad Guide Skill（`bmad-guide`）說明 BMad-Method 的工作流程，內文含少量引自 BMad-Method v6.12.4 原始檔的短句（都附出處路徑）；Control Tower（CT）與 CT Guide 也以 BMad-Method 的術語與 skill 名稱說明搭配方式。BMad-Method 以 MIT License 授權，全文與商標聲明如下。

本 repo 未內含其他第三方檔案：網站字型（Noto Sans TC、Martian Mono、Chiron Hei HK）在瀏覽時由 Google Fonts 載入，不在本 repo；VitePress 是建置時才安裝的開發依賴，不在本 repo。

## BMad-Method

Source: https://github.com/bmad-code-org/BMAD-METHOD

```
MIT License

Copyright (c) 2025 BMad Code, LLC

This project incorporates contributions from the open source community.
See [CONTRIBUTORS.md](CONTRIBUTORS.md) for contributor attribution.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

TRADEMARK NOTICE:
BMad™, BMad Method™, and BMad Core™ are trademarks of BMad Code, LLC, covering all
casings and variations (including BMAD, bmad, BMadMethod, BMAD-METHOD, etc.). The use of
these trademarks in this software does not grant any rights to use the trademarks
for any other purpose. See [TRADEMARK.md](TRADEMARK.md) for detailed guidelines.
```

BMad Control Tower、BMad Guide Skill 不是 BMad Code, LLC 的產品，也未經其背書；名稱中的 BMad 指所搭配的 BMad-Method。

## ct-adapter-pstack

CT v6.0.0-beta.1 起，Release 另附 `ct-adapter-pstack`（讓 CT 塔台能把部分工作層交給 pstack 的 adapter）。它是 CT 的一部分，以 MIT License 授權，全文見其 zip 內的 `LICENSE`。

本 adapter **只含** pstack 的 skill／playbook／agent 名稱、與 CT 規則的對照、版本與偵測位置、上游連結，以及 CT 自己寫的規則與說明；**不含**上游任何 skill、playbook、hook 或注入文字的原文，也**不附**上游授權全文。上游只在下表引用：

| 元件 | 出處 | 授權 | 著作權人 |
|---|---|---|---|
| pstack-claude（Claude Code／Codex 移植版） | https://github.com/michael-denyer/pstack-claude | MIT | 見上游 repo 的 `LICENSE` |
| pstack（原作） | https://github.com/cursor/plugins/tree/main/pstack | 見原作 repo | 見原作 repo |
| cursor-team-kit、thermos（pstack-claude 內含的第三方元件） | 見上游 `NOTICE.md` | MIT | Cursor |

各元件與上游檔案的對照表在上游 `NOTICE.md`：https://github.com/michael-denyer/pstack-claude/blob/main/NOTICE.md 。以上依 pstack-claude v0.9.103（commit `36885ea6`）整理；上游更版時，授權與著作權人以上游當時的檔案為準。完整的出處與授權說明見 `ct-adapter-pstack` zip 內的 `NOTICE.md`。

「pstack」「poteto-mode」等是上游專案使用的名稱；本 adapter 使用這些名稱只為了指出對應的上游功能，不代表上游作者認可或參與本 adapter。
