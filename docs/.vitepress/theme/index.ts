import { h } from 'vue';
import DefaultTheme from 'vitepress/theme';
import type { Theme } from 'vitepress';
import './tailwind.css';
import './style.css';
import './bento-system.css';
import './custom-layout.css';
//import './assets/custom.css';
import CustomNavBar from './components/CustomNavBar.vue';
import LatestFeatures from './components/LatestFeatures.vue';
import SecurityInfo from './components/SecurityInfo.vue';
import SOFADashboard from './components/SOFADashboard.vue';
import SOFALogo from './components/SOFALogo.vue';
import SOFALogoSVG from './components/SOFALogoSVG.vue';
import BentoGrid from './components/BentoGrid.vue';
import BentoCard from './components/BentoCard.vue';
import BentoButton from './components/BentoButton.vue';
import CveSearch from './components/CveSearch.vue';
import ReleaseDeferralTable from './components/ReleaseDeferralTable.vue';
import ReleaseInstallerTable from './components/ReleaseInstallerTable.vue';
import ModelIdentifierTable from './components/ModelIdentifierTable.vue';
import BetaInfo from './components/BetaInfo.vue';
import FeedInfo from './components/FeedInfo.vue';
import CveDetails from './components/CveDetails.vue';
import BulletinDashboard from './components/BulletinDashboard.vue';

export default {
  extends: DefaultTheme,
  Layout: () => {
    return h(DefaultTheme.Layout, null, {
      // Insert our custom navbar at the top of the layout
      'layout-top': () => h(CustomNavBar),
    });
  },
  enhanceApp({ app, router, siteData }) {
    app.component('LatestFeatures', LatestFeatures);
    app.component('SecurityInfo', SecurityInfo);
    app.component('SOFADashboard', SOFADashboard);
    app.component('SOFALogo', SOFALogo);
    app.component('SOFALogoSVG', SOFALogoSVG);
    app.component('BentoGrid', BentoGrid);
    app.component('BentoCard', BentoCard);
    app.component('BentoButton', BentoButton);
    app.component('CustomNavBar', CustomNavBar);
    app.component('CveSearch', CveSearch);
    app.component('ReleaseDeferralTable', ReleaseDeferralTable);
    app.component('ReleaseInstallerTable', ReleaseInstallerTable);
    app.component('ModelIdentifierTable', ModelIdentifierTable);
    app.component('BetaInfo', BetaInfo);
    app.component('FeedInfo', FeedInfo);
    app.component('CveDetails', CveDetails);
    app.component('BulletinDashboard', BulletinDashboard);
  },
} satisfies Theme;
