import { render } from "preact";

import "tailwindcss/tailwind.css";
import "./output.css";
import Header from "./Header";
import Browse from "./Browse";

export function App() {
  return (
    <div>
      <Header />
      <Browse />
    </div>
  );
}

render(<App />, document.getElementById("app"));
