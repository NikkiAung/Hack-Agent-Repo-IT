import UserButton from "./user-button";
import NavLogo from "./nav-logo";
import { NavMenu } from "./nav-menu";
import { auth } from "@/server/auth";

const AppNav = async () => {
  const session = await auth();

  return (
    <div className="flex items-center justify-between py-4">
      <NavLogo />

      {/* Navigation Menu */}
      <NavMenu className="flex-1 flex justify-center" />

      <UserButton user={session?.user!} expires={session?.expires!} />
    </div>
  );
};

export default AppNav;
