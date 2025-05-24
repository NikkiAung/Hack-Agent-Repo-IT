"use client";

import { updateDisplayName } from "@/server/actions/settings";
import { zodResolver } from "@hookform/resolvers/zod";
import { useAction } from "next-safe-action/hooks";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "../ui/form";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { cn } from "@/lib/utils";
import { settingSchema } from "@/types/settings-schema";

type ProfileFormProps = {
  username: string;
  email: string;
  isDesktop: boolean;
  handleOpen: () => void;
};

const ProfileForm = ({
  username,
  email,
  isDesktop,
  handleOpen,
}: ProfileFormProps) => {
  const form = useForm({
    resolver: zodResolver(settingSchema),
    defaultValues: {
      username,
      email,
    },
  });

  const { execute, status, result } = useAction(updateDisplayName, {
    onSuccess({ data }) {
      form.reset();
      if (data?.error) {
        toast.error(data?.error);
      }
      if (data?.success) {
        handleOpen();
        toast.success(data?.success);
      }
    },
  });

  const onSubmit = (values: z.infer<typeof settingSchema>) => {
    const { username, email } = values;
    execute({ username, email });
  };
  return (
    <main>
      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(onSubmit)}
          className="space-y-4 px-4 lg:px-0"
        >
          <FormField
            name="username"
            control={form.control}
            render={({ field }) => (
              <FormItem>
                <FormLabel>Display Name</FormLabel>
                <FormControl>
                  <Input placeholder="snapshot@admin" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <Button
            className={cn(
              "w-full",
              status === "executing" && "animate-pulse",
              !isDesktop && "mb-4"
            )}
            disabled={status === "executing"}
          >
            Save
          </Button>
        </form>
      </Form>
    </main>
  );
};

export default ProfileForm;
