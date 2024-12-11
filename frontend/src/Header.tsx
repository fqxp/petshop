import { Navbar } from "flowbite-react";
import { Link } from "preact-router";

import parrotLogo from "./assets/parrot.svg";

export default function Header() {
  return (
    <Navbar rounded className="bg-lime-300">
      <Navbar.Brand as={Link} link="/">
        <img
          src={parrotLogo}
          alt="petshop logo"
          height="30"
          width="75"
          className="mt-0.5 mr-2"
        />
        <span className="whitespace-nowrap text-xl font-semibold text-black">
          petshop
        </span>
      </Navbar.Brand>
      <Navbar.Toggle />
      <Navbar.Collapse>
        <Navbar.Link as={Link} href="#">
          About
        </Navbar.Link>
        <Navbar.Link href="#">FAQ</Navbar.Link>
        <Navbar.Link href="#">Contact</Navbar.Link>
      </Navbar.Collapse>
    </Navbar>
  );
}
