"use client";

import { confirmEmailWithToken } from "@/server/actions/token";
import { useRouter, useSearchParams } from "next/navigation";

import { useEffect, useState } from "react";
import { useCallback } from "react";
import AuthForm from "./auth-form";
import { cn } from "@/lib/utils";

const ConfirmEmail = () => {
  const token = useSearchParams().get("token");
  const router = useRouter();
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleConfirmEmail = useCallback(() => {
    if (!token) {
      setError("Invalid token");
      return;
    }
    confirmEmailWithToken(token).then((res) => {
      if (res.success) {
        setSuccess(res.success);
        router.push("/auth/login");
      }
      if (res.error) {
        setError(res.error);
      }
    });
  }, []);

  useEffect(() => {
    handleConfirmEmail();
  }, []);

  return (
    <AuthForm
      formTitle="Confirm Email"
      footerLabel="Login to your accounr"
      footerHref="/auth/login"
      showProvider={false}
    >
      <p
        className={cn(
          "text-center font-bold text-xl text-primary",
          error && "text-red-600"
        )}
      >
        {!success && !error ? "confirming email..." : success ? success : error}
      </p>
    </AuthForm>
  );
};

export default ConfirmEmail;
