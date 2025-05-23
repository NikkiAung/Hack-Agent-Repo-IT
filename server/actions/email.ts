"use server";
import { getBaseUrl } from "@/lib/get-baseUrl";
import { Resend } from "resend";
import EmailComfirimationTemplate from "@/components/email-template";
import ResetPasswordEmail from "@/components/password-reset-email-template";
import MagicCodeEmail from "@/components/two-factor-mail";

const currentBaseUrl = getBaseUrl();
const resend = new Resend(process.env.RESEND_API_KEY);
export const sendEmail = async (
  email: string,
  token: string,
  userFirstname: string
) => {
  const comfirmLink = `${currentBaseUrl}/confirm-email?token=${token}`;

  const { data, error } = await resend.emails.send({
    from: "onboarding@resend.dev",
    to: email,
    subject: "Confirm Your Account - Welcome to Genini",
    react: EmailComfirimationTemplate({
      userFirstname,
      comfirmEmailLink: comfirmLink,
    }),
  });

  if (error) {
    console.log(error);
  }
};

export const sendPasswordResetEmail = async (email: string, token: string) => {
  const resetLink = `${currentBaseUrl}/change-password?token=${token}`;

  const { data, error } = await resend.emails.send({
    from: "onboarding@resend.dev",
    to: email,
    subject: "Reset Your Password - Alert form Genini",
    react: ResetPasswordEmail({
      resetPasswordLink: resetLink,
    }),
  });

  if (error) {
    console.log(error);
  }
};

export const sendTwoFactorEmail = async (email: string, code: string) => {
  const { data, error } = await resend.emails.send({
    from: "onboarding@resend.dev",
    to: email,
    subject: "Two Factor Authentication Code - Genini",
    react: MagicCodeEmail({
      code,
    }),
  });

  if (error) {
    console.log(error);
  }
};
