"use client";
import { useForm } from "react-hook-form";
import { Button } from "../ui/button";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
} from "../ui/form";
import { Input } from "../ui/input";
import { deleteAccountSchema } from "@/types/settings-schema";
import { zodResolver } from "@hookform/resolvers/zod";
import { useAction } from "next-safe-action/hooks";
import { z } from "zod";
import { deleteAccount } from "@/server/actions/settings";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import { signOut } from "next-auth/react";

type DeleteAccountProps = {
  email: string;
};

const DeleteAccount = ({ email }: DeleteAccountProps) => {
  const router = useRouter();
  const form = useForm({
    resolver: zodResolver(deleteAccountSchema),
    defaultValues: {
      email,
    },
  });
  const { execute, status, result } = useAction(deleteAccount, {
    onSuccess({ data }) {
      form.reset();
      if (data?.error) {
        toast.error(data?.error);
      }
      if (data?.success) {
        toast.success(data?.success);
        router.push("/");
      }
    },
  });
  const onSubmit = (values: z.infer<typeof deleteAccountSchema>) => {
    const { email } = values;
    execute({ email });
  };
  return (
    <Form {...form}>
      <div className="-mt-4 flex flex-col gap-2">
        <form onSubmit={form.handleSubmit(onSubmit)}>
          <FormField
            name="email"
            control={form.control}
            render={({ field }) => (
              <FormItem>
                <FormLabel>Danger Zone</FormLabel>
                <FormDescription>Delete your account</FormDescription>
                <FormControl>
                  <Input className="hidden"></Input>
                </FormControl>
              </FormItem>
            )}
          />

          <Button
            variant="destructive"
            className="w-full bg-red-500 hover:bg-red-600 mt-2"
            onClick={() => signOut()}
          >
            Delete
          </Button>
        </form>
      </div>
    </Form>
  );
};

export default DeleteAccount;
