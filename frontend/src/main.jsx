import ReactDOM from "react-dom/client";

import App from "./App.jsx";
import "./styles.css";


const rootElement = document.getElementById("root");

if (!rootElement) {
  throw new Error(
    'VendorGuard could not start because the HTML element with id="root" was not found.',
  );
}

ReactDOM.createRoot(rootElement).render(
  <App />,
);