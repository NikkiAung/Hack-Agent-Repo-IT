import { z } from "zod";

export const registerSchema = z.object({
  username: z.string().min(4, {
    message: "Please enter a valid name - at least 4 characters long",
  }),
  email: z.string().email({
    message: "Please enter a valid email address",
  }),
  password: z.string().min(4, {
    message: "Password must be at least 4 characters long",
  }),
});
