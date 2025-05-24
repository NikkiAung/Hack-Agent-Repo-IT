"use client";

import { useAction } from "next-safe-action/hooks";
import AuthForm from "@/components/auth/auth-form";
import React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { changePasswordSchema } from "@/types/changepassword-schema";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { toast } from "sonner";
import { changePassword } from "@/server/actions/change-password";
import { useSearchParams } from "next/navigation";
import { signOut } from "next-auth/react";

const ChangePassword = () => {
  const form = useForm({
    resolver: zodResolver(changePasswordSchema),
    defaultValues: {
      password: "",
    },
  });

  const { execute, status, result } = useAction(changePassword, {
    onSuccess({ data }) {
      console.log(data);
      form.reset();
      if (data?.error) {
        toast.error(data?.error);
      }
      if (data?.success) {
        signOut({ callbackUrl: "/auth/login" });
        toast.success(data?.success);
      }
    },
  });
  const token = useSearchParams().get("token");
  const onSubmit = (values: z.infer<typeof changePasswordSchema>) => {
    console.log("values", values);
    const { password } = values;
    execute({ password, token });
  };
  return (
    <AuthForm
      formTitle="Change your password"
      footerLabel="Already have an account?"
      footerHref="/auth/login"
      showProvider={false}
    >
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)}>
          <div>
            <FormField
              name="password"
              control={form.control}
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Password</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="****"
                      {...field}
                      type="password"
                      disabled={status === "executing"}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
          <Button
            className={cn(
              "w-full my-4",
              status === "executing" && "animate-pulse"
            )}
            disabled={status === "executing"}
          >
            Change Password
          </Button>
        </form>
      </Form>
    </AuthForm>
  );
};

export default ChangePassword;
