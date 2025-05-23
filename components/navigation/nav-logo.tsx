import Link from "next/link";

const NavLogo = () => {
  return (
    <Link
      href={"/"}
      className="text-3xl font-bold text-primary font-mono text-bold flex gap-1"
    >
      <svg
        className="h-8 w-8 text-[#add1ea]"
        fill="none"
        viewBox="0 0 48 48"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          clipRule="evenodd"
          d="M24 4H42V17.3333V30.6667H24V44H6V30.6667V17.3333H24V4Z"
          fill="currentColor"
          fillRule="evenodd"
        ></path>
      </svg>
      <span className="text-4xl">Genini</span>
    </Link>
  );
};

export default NavLogo;
