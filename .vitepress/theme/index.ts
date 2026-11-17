// 沿用 BAT 站的結構：extends DefaultTheme、enhanceApp 註冊元件。
// 字體走 Google Fonts（Noto Sans TC、Martian Mono、Chiron Hei HK），所以用不打包 Inter 的 theme-without-fonts；
// Artifact 預覽包因此少 14 個字體檔（Artifact 有檔數限制）。
import { h } from 'vue'
import DefaultTheme from 'vitepress/theme-without-fonts'
import type { Theme } from 'vitepress'
// 版型（vitepress-portal-layout v1.1.2）：主內容加寬、左右功能表收合、圖的放大檢視。
// portal-layout/ 是 skill 原檔，不改內容；升版時整包覆蓋。時間軸元件這一輪不套用，沒有複製。
import LayoutToggles from './portal-layout/components/LayoutToggles.vue'
import FigureZoom from './portal-layout/components/FigureZoom.vue'
import AutonomyDial from './components/AutonomyDial.vue'
import BatLink from './components/BatLink.vue'
import BreakpointMap from './components/BreakpointMap.vue'
import CapabilityLevels from './components/CapabilityLevels.vue'
import CardTable from './components/CardTable.vue'
import CaseCard from './components/CaseCard.vue'
import CtDownload from './components/CtDownload.vue'
import DemoVideo from './components/DemoVideo.vue'
import EcosystemStack from './components/EcosystemStack.vue'
import EraTimeline from './components/EraTimeline.vue'
import FeatureGrid from './components/FeatureGrid.vue'
import GrowthLadder from './components/GrowthLadder.vue'
import HeroTower from './components/HeroTower.vue'
import LandingCheck from './components/LandingCheck.vue'
import LayerStack from './components/LayerStack.vue'
import LearningPath from './components/LearningPath.vue'
import MediaFigure from './components/MediaFigure.vue'
import MergeModes from './components/MergeModes.vue'
import QuestionFlow from './components/QuestionFlow.vue'
import ShellLoop from './components/ShellLoop.vue'
import StatsCounter from './components/StatsCounter.vue'
import TicketLife from './components/TicketLife.vue'
import TicketStates from './components/TicketStates.vue'
import VersionBadge from './components/VersionBadge.vue'
import VersionMatrix from './components/VersionMatrix.vue'
import './portal-layout/layout.css'
import './portal-layout/figure-zoom.css'
// 站點自己的樣式放在 portal-layout 之後
import './custom.css'

export default {
  extends: DefaultTheme,
  Layout: () => h(DefaultTheme.Layout, null, {
    // 寬螢幕的左側選單、右側本頁目錄收合鈕（只在文件頁）
    'doc-top': () => h(LayoutToggles),
    // 文中的圖加「放大檢視」按鈕（SVG、圖片與 HTML 圖）；互動圖在元件的 <figure> 加 data-no-zoom，<figure> 以外的 HTML 圖加 data-pl-zoom
    'layout-bottom': () => h(FigureZoom)
  }),
  enhanceApp({ app }) {
    app.component('AutonomyDial', AutonomyDial)
    app.component('BatLink', BatLink)
    app.component('BreakpointMap', BreakpointMap)
    app.component('CapabilityLevels', CapabilityLevels)
    app.component('CardTable', CardTable)
    app.component('CaseCard', CaseCard)
    app.component('CtDownload', CtDownload)
    app.component('DemoVideo', DemoVideo)
    app.component('EcosystemStack', EcosystemStack)
    app.component('EraTimeline', EraTimeline)
    app.component('FeatureGrid', FeatureGrid)
    app.component('GrowthLadder', GrowthLadder)
    app.component('HeroTower', HeroTower)
    app.component('LandingCheck', LandingCheck)
    app.component('LayerStack', LayerStack)
    app.component('LearningPath', LearningPath)
    app.component('MediaFigure', MediaFigure)
    app.component('MergeModes', MergeModes)
    app.component('QuestionFlow', QuestionFlow)
    app.component('ShellLoop', ShellLoop)
    app.component('StatsCounter', StatsCounter)
    app.component('TicketLife', TicketLife)
    app.component('TicketStates', TicketStates)
    app.component('VersionBadge', VersionBadge)
    app.component('VersionMatrix', VersionMatrix)
  }
} satisfies Theme
