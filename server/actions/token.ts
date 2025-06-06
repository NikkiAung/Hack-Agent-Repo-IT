"use server";

import { eq } from "drizzle-orm";
import { db } from "..";
import {
  emailVerificationToken,
  resetPasswordToken,
  twoFactorTokes,
  users,
} from "../schema";
import crypto from "crypto";

const checkEmailVerificationToken = async (
  email: string | null,
  token?: string
) => {
  try {
    let verificationToken:
      | {
          id: string;
          email: string;
          token: string;
          expires: Date;
        }
      | undefined;
    if (email) {
      verificationToken = await db.query.emailVerificationToken.findFirst({
        where: eq(emailVerificationToken.email, email),
      });
    }
    if (token) {
      verificationToken = await db.query.emailVerificationToken.findFirst({
        where: eq(emailVerificationToken.token, token),
      });
    }
    return verificationToken;
  } catch (error) {
    return null;
  }
};

export const generateEmailVericificationToken = async (email: string) => {
  const token = crypto.randomUUID();
  const expires = new Date(new Date().getTime() + 30 * 60 * 1000);
  const existingToken = await checkEmailVerificationToken(email);
  if (existingToken) {
    await db
      .delete(emailVerificationToken)
      .where(eq(emailVerificationToken.id, existingToken.id));
  }
  const verificationToken = await db
    .insert(emailVerificationToken)
    .values({
      email,
      token,
      expires,
    })
    .returning();
  return verificationToken;
};

export const confirmEmailWithToken = async (token: string) => {
  const existingToken = await checkEmailVerificationToken(null, token);
  if (!existingToken) return { error: "Invalid token" };

  const isExpired = new Date() > new Date(existingToken.expires);

  if (isExpired) return { error: "Token expired" };

  const existingUser = await db.query.users.findFirst({
    where: eq(users.email, existingToken.email),
  });
  if (!existingUser) return { error: "User not found" };

  await db
    .update(users)
    .set({
      emailVerified: new Date(),
      email: existingToken.email,
    })
    .where(eq(users.id, existingUser.id));

  await db
    .delete(emailVerificationToken)
    .where(eq(emailVerificationToken.id, existingToken.id));

  return { success: "Email verified" };
};

// ---------------------- reset password --------------------------------

const checkResetPasswordToken = async (email: string) => {
  try {
    const passwordResetToken = await db.query.resetPasswordToken.findFirst({
      where: eq(resetPasswordToken.email, email),
    });

    return passwordResetToken;
  } catch (error) {
    return null;
  }
};

export const generatePasswordResetToken = async (email: string) => {
  const token = crypto.randomUUID();
  const expires = new Date(new Date().getTime() + 30 * 60 * 1000);

  const existingToken = await checkResetPasswordToken(email);

  if (existingToken) {
    await db
      .delete(resetPasswordToken)
      .where(eq(resetPasswordToken.id, existingToken.id));
  }

  const passwordResetToken = await db
    .insert(resetPasswordToken)
    .values({
      email,
      token,
      expires,
    })
    .returning();

  return passwordResetToken;
};

export const checkPasswordResetTokenByToken = async (token: string) => {
  try {
    const passwordResetToken = await db.query.resetPasswordToken.findFirst({
      where: eq(resetPasswordToken.token, token),
    });

    return passwordResetToken;
  } catch (error) {
    return null;
  }
};

export const getTwoFactorCodeByEmail = async (email: string) => {
  try {
    const existingCode = await db.query.twoFactorTokes.findFirst({
      where: eq(twoFactorTokes.email, email),
    });

    return existingCode;
  } catch (error) {
    return null;
  }
};

export const generateTwoFactorCode = async (email: string) => {
  try {
    const code = crypto.randomInt(100_000, 1_000_000).toString();
    const expires = new Date(new Date().getTime() + 30 * 60 * 1000);

    const existingCode = await getTwoFactorCodeByEmail(email);

    if (existingCode) {
      await db
        .delete(twoFactorTokes)
        .where(eq(twoFactorTokes.id, existingCode.id));
    }

    const twoFactorCode = await db
      .insert(twoFactorTokes)
      .values({
        email,
        token: code,
        expires,
      })
      .returning();

    return twoFactorCode;
  } catch (error) {
    return null;
  }
};
