import { createApp } from "vue";
import App from "./App.vue";
import "./styles/main.scss";

import { library } from "@fortawesome/fontawesome-svg-core";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import {
  faFilter,
  faCircleQuestion,
  faUser,
  faPaperPlane,
  faChevronDown,
  faChevronUp,
  faBars,
  faThumbtack,
  faBell,
  faTimes,
  faArrowRight,
} from "@fortawesome/free-solid-svg-icons";

library.add(
  faFilter,
  faCircleQuestion,
  faUser,
  faPaperPlane,
  faChevronDown,
  faChevronUp,
  faBars,
  faThumbtack,
  faBell,
  faTimes,
  faArrowRight,
);

import { ModuleRegistry, AllCommunityModule } from "ag-grid-community";
import { AllEnterpriseModule, LicenseManager } from "ag-grid-enterprise";

ModuleRegistry.registerModules([AllEnterpriseModule]);
LicenseManager.setLicenseKey(import.meta.env.VITE_AG_GRID_LICENSE_KEY ?? "");

const app = createApp(App);
app.component("icon", FontAwesomeIcon);
app.mount("#app");
