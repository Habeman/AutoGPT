import AutoGPTServerAPI from "@/lib/autogpt-server-api";
import { useCallback, useEffect, useMemo, useState } from "react";
import { loadStripe } from "@stripe/stripe-js";
import { useRouter } from "next/navigation";

const stripePromise = loadStripe(
  process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!,
);

export default function useCredits(): {
  credits: number | null;
  fetchCredits: () => void;
  requestTopUp: (credit_amount: number) => Promise<void>;
} {
  const [credits, setCredits] = useState<number | null>(null);
  const api = useMemo(() => new AutoGPTServerAPI(), []);
  const router = useRouter();

  const fetchCredits = useCallback(async () => {
    const response = await api.getUserCredit();
    setCredits(response.credits);
  }, [api]);

  useEffect(() => {
    fetchCredits();
  }, [fetchCredits]);

  const requestTopUp = useCallback(
    async (credit_amount: number) => {
      const stripe = await stripePromise;

      if (!stripe) {
        return;
      }

      const response = await api.requestTopUp(credit_amount);
      router.push(response.checkout_url);
    },
    [api, router],
  );

  return {
    credits,
    fetchCredits,
    requestTopUp,
  };
}
