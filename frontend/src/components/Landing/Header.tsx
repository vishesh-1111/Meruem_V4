import Image from "next/image";
import Logo from "../../../public/assests/logo.png";
import ArrowRight from "../../../public/assests/arrow-right.svg";

import { FaBars } from "react-icons/fa";
import Button from "./Button";
import Link from "next/link";
const Header = () => {
  return (
    <>
      {/* Promotional Banner */}
      <div className="flex justify-center items-center py-3 bg-black text-white text-sm gap-3">
        <p className="text-white/60 hidden md:block">
          Streamline your Data Analysis and boost your productivity
        </p>
        <div className="inline-flex gap-1 items-center">
          <Link href={"/auth"}>
            <p>Get started for free</p>
          </Link>
          <Image
            src={ArrowRight}
            alt="Arrow Right"
            className="h-4 w-4 inline-flex justify-center items-center"
          />
        </div>
      </div>
      
      {/* Main Header */}
      <header className="flex justify-between items-center px-6 py-4 backdrop-blur-md sticky top-0 z-20 bg-gradient-to-r from-[#E0E7FD] to-[#FDFEFF] shadow-md">
        <Image src={Logo} alt="Logo" className="cursor-pointer"/>
        <FaBars className="block md:hidden" />
        <nav className="hidden md:block">
          <ul className="flex gap-6 items-center">
            <li>
              <a href="#">About</a>
            </li>
            <li>
              <a href="#">Features</a>
            </li>
            <li>
              <a href="#">Customers</a>
            </li>
            <li>
              <a href="#">Updates</a>
            </li>
            <li>
              <a href="#">Help</a>
            </li>
            <Link href={"/auth"} prefetch={true}><Button text="Get for free"/></Link>
          </ul>
        </nav>
      </header>
    </>
  );
};export default Header;
