"use client";
import { Session } from "next-auth";
import React, { useState } from "react";
import { UserRoundPen } from "lucide-react";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Drawer,
  DrawerClose,
  DrawerContent,
  DrawerDescription,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from "@/components/ui/drawer";

import { Button } from "../ui/button";
import SettingsCard from "./setting-card";
import { useMediaQuery } from "../hooks/useMediaQuery";
import { DialogClose } from "@radix-ui/react-dialog";
import ProfileForm from "./profile-form";
import AvatarUploadForm from "./avatar-upload-form";

type ProfileCardProps = {
  session: Session;
};
const ProfileCard = ({ session }: ProfileCardProps) => {
  const [open, setOpen] = useState(false);
  const isDesktop = useMediaQuery("(min-width: 768px)");
  const handleOpen = () => {
    setOpen(false);
  };
  return (
    <SettingsCard>
      <div className="flex items-start gap-2 justify-between">
        <div className="flex items-center gap-2 flex-col lg:flex-row">
          <AvatarUploadForm
            username={session.user?.name!}
            image={session.user?.image}
            email={session.user.email!}
          />
          <div>
            <div className="flex flex-col gap-1">
              <p className="text-muted-foreground text-lg">Display Name :</p>
              <h2 className=" font-semibold text-lg">{session?.user?.name}</h2>
            </div>

            <div className="flex flex-col gap-1">
              <p className=" text-muted-foreground text-lg">Email :</p>
              <p className="text-sm font-medium">{session.user?.email}</p>
            </div>
          </div>
        </div>
        {isDesktop ? (
          <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
              <UserRoundPen className="w-5 h-5 text-muted-foreground hover:text-black cursor-pointer" />
            </DialogTrigger>
            <DialogContent className="mx-4 lg:mx-0">
              <DialogHeader>
                <DialogTitle>Edit profile</DialogTitle>
                <DialogDescription>
                  This will be your public display name
                </DialogDescription>
              </DialogHeader>
              <ProfileForm
                username={session?.user?.name!}
                email={session?.user?.email!}
                isDesktop={isDesktop}
                handleOpen={handleOpen}
              />
              <DialogClose asChild>
                <Button variant="outline" className="w-full">
                  Cancel
                </Button>
              </DialogClose>
            </DialogContent>
          </Dialog>
        ) : (
          <Drawer>
            <DrawerTrigger>
              <UserRoundPen className="w-5 h-5 text-muted-foreground hover:text-black cursor-pointer" />
            </DrawerTrigger>
            <DrawerContent>
              <DrawerHeader>
                <DrawerTitle>Edit profile</DrawerTitle>
                <DrawerDescription>
                  This will be your public display name
                </DrawerDescription>
              </DrawerHeader>
              <ProfileForm
                username={session?.user?.name!}
                email={session?.user?.email!}
                isDesktop={isDesktop}
                handleOpen={handleOpen}
              />
              <DrawerClose>
                <Button variant="outline" className="w-full mb-4">
                  Cancel
                </Button>
              </DrawerClose>
            </DrawerContent>
          </Drawer>
        )}
      </div>
    </SettingsCard>
  );
};

export default ProfileCard;
