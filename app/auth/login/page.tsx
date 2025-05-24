"use client";
import React, { useState } from "react";
import AuthForm from "@/components/auth/auth-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { loginSchema } from "@/types/login-schema";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import {
  InputOTP,
  InputOTPGroup,
  InputOTPSeparator,
  InputOTPSlot,
} from "@/components/ui/input-otp";

import { Input } from "@/components/ui/input";
import Link from "next/link";
import { useAction } from "next-safe-action/hooks";
import { login } from "@/server/actions/login-action";
import { cn } from "@/lib/utils";
import { toast } from "sonner";

const LoginPage = () => {
  const [isTwoFactorOn, setIsTwoFactorOn] = useState(false);
  const form = useForm<z.infer<typeof loginSchema>>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "",
      password: "",
      code: "",
    },
  });

  const { execute, status } = useAction(login, {
    onSuccess: ({ data }) => {
      if (data?.error) {
        form.reset();
        toast.error(data?.error);
      }
      if (data?.success) {
        form.reset();
        toast.success(data?.success);
      }
      if (data?.twoFactor) {
        toast.success(data?.twoFactor);
        setIsTwoFactorOn(true);
      }
    },
  });

  function onSubmit(values: z.infer<typeof loginSchema>) {
    const { email, password, code } = values;
    console.log("code", code);
    // console.log({ email, password, code });
    execute({ email, password, code });
  }
  return (
    <AuthForm
      formTitle="Login to your account"
      footerLabel="Don't have an account"
      footerHref="/auth/register"
      showProvider
    >
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)}>
          {isTwoFactorOn && (
            <FormField
              control={form.control}
              name="code"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>We sent a code to your email.</FormLabel>
                  <FormControl>
                    <InputOTP
                      maxLength={6}
                      {...field}
                      disabled={status === "executing"}
                      className=" "
                    >
                      <InputOTPGroup>
                        <InputOTPSlot index={0} />
                        <InputOTPSlot index={1} />
                        <InputOTPSlot index={2} />
                      </InputOTPGroup>
                      <InputOTPSeparator />
                      <InputOTPGroup>
                        <InputOTPSlot index={3} />
                        <InputOTPSlot index={4} />
                        <InputOTPSlot index={5} />
                      </InputOTPGroup>
                    </InputOTP>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          )}
          {!isTwoFactorOn && (
            <div className="space-y-4">
              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Email</FormLabel>
                    <FormControl>
                      <Input placeholder="email" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Password</FormLabel>
                    <FormControl>
                      <Input type="password" placeholder="******" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button size={"sm"} variant={"link"} className="pl-0 mb-1">
                <Link href={"/auth/reset"}>Forgot password</Link>
              </Button>
            </div>
          )}

          <Button
            className={cn(
              "w-full mb-4 mt-4",
              status === "executing" && "animate-pulse"
            )}
            disabled={status === "executing"}
          >
            {isTwoFactorOn ? "Verify Code" : "Login"}
          </Button>
        </form>
      </Form>
    </AuthForm>
  );
};

export default LoginPage;
