"use client";
import React, { useEffect } from "react";
import { Button } from "../ui/button";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { twoFactorAuthSchema } from "@/types/settings-schema";
import { useAction } from "next-safe-action/hooks";
import { z } from "zod";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "../ui/form";
import { cn } from "@/lib/utils";
import { Switch } from "@/components/ui/switch";
import { twoFactorToogler } from "@/server/actions/settings";
import { toast } from "sonner";

type TwoFactorProps = {
  email: string;
  isTwoFactorEnabled: boolean;
};

const TwoFactor = ({ email, isTwoFactorEnabled }: TwoFactorProps) => {
  const form = useForm({
    resolver: zodResolver(twoFactorAuthSchema),
    defaultValues: {
      email,
      isTwoFactorEnabled,
    },
  });

  const { execute, status, result } = useAction(twoFactorToogler, {
    onSuccess({ data }) {
      form.reset();
      if (data?.error) {
        toast.error(data?.error);
      }
      if (data?.success) {
        toast.success(data?.success);
      }
    },
  });

  const onSubmit = (values: z.infer<typeof twoFactorAuthSchema>) => {
    const { isTwoFactorEnabled, email } = values;
    execute({ isTwoFactorEnabled, email });
  };

  useEffect(() => {
    form.setValue("isTwoFactorEnabled", isTwoFactorEnabled); // Set the initial value of the switch to the isTwoFactorEnabled prop
  }, [isTwoFactorEnabled, form]);

  return (
    <Form {...form}>
      <div className=" items-center w-full">
        <form onSubmit={form.handleSubmit(onSubmit)}>
          <FormField
            name="isTwoFactorEnabled"
            control={form.control}
            render={({ field }) => (
              <FormItem>
                <FormLabel>Two Factor Authentaction</FormLabel>
                <FormDescription>
                  {isTwoFactorEnabled ? "Disable" : "Enable"} two factor
                  authentication for your account
                </FormDescription>
                <FormControl>
                  <Switch
                    disabled={status === "executing"}
                    checked={field.value}
                    onCheckedChange={field.onChange}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <Button
            className={cn(
              "w-full mb-4 mt-2",
              status === "executing" && "animate-pulse",
              isTwoFactorEnabled ? "bg-red-500 hover:bg-red-600" : "bg-primary"
            )}
            disabled={status === "executing"}
          >
            {isTwoFactorEnabled ? "Disable" : "Enable"}
          </Button>
        </form>
      </div>
    </Form>
  );
};

export default TwoFactor;
