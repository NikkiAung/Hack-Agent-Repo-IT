import { NavLink } from "./nav-link";

interface NavMenuProps {
  className?: string;
}

export const NavMenu = ({ className }: NavMenuProps) => {
  return (
    <nav className={className}>
      <ul className="flex items-center space-x-1 sm:space-x-2 md:space-x-4">
        <li>
          <NavLink href="/">Home</NavLink>
        </li>
        <li className="flex items-center">
          <span className="text-gray-400 dark:text-gray-600">|</span>
        </li>
        <li>
          <NavLink href="/learn">Learn</NavLink>
        </li>
        <li className="flex items-center">
          <span className="text-gray-400 dark:text-gray-600">|</span>
        </li>
        <li>
          <NavLink href="/code">Code</NavLink>
        </li>
        <li className="flex items-center">
          <span className="text-gray-400 dark:text-gray-600">|</span>
        </li>
        <li>
          <NavLink href="/dashboard">Dashboard</NavLink>
        </li>
      </ul>
    </nav>
  );
};
